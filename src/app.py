import jwt
from contextlib import asynccontextmanager
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from .config import settings
from src.models import RegisterRequest, LoginRequest, BearerTokenResponse, UserResponse
from src.database import get_db, User
from src.database.connection import init_db, sync_engine
from src.config.telemetry import init_telemetry
from src.dependencies import get_user_management_service
from src.services.user_management_service import UserManagementService


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_telemetry(app, sync_engine)
    yield


app = FastAPI(
    title="Auth Service",
    description="Simple auth app kubernetes ingress api auth",
    version="0.1.0",
    lifespan=lifespan)

router = APIRouter(prefix="/api/v1", tags=["auth"])

app.include_router(router)


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


@router.post("/register", response_model=UserResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing_with_displayed_name = await db.execute(
            select(User)
            .where(User.displayed_name == body.displayed_name)
        )

    if existing_with_displayed_name.scalar_one_or_none():
        raise HTTPException(409, "Chosen display name already exists.")
        
    existing_with_email = await db.execute(
        select(User)
        .where(User.email == body.email)
    )

    new_user = User(
        email = body.email,
        password = bcrypt.hash(body.password),
        full_name=body.full_name,
        displayed_name=body.displayed_name,
    )

    if existing_with_email.scalar_one_or_none():
        return new_user

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=BearerTokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .where(User.email == body.email)
    )

    db_user = result.scalar_one_or_none()

    if not db_user or not bcrypt.verify(body.password, db_user.password):
        raise HTTPException(401, "Failed authorizaion.")

    payload = {
        "sub": str(db_user.id),
        "username": db_user.email,
        "email": db_user.email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return BearerTokenResponse(access_token=token)


@router.post("/google-login")
async def google_login(
    body: LoginRequest,
    user_management_service: UserManagementService = Depends(get_user_management_service)):
    return await user_management_service.login_with_google(body)


@router.get("/verify")
async def verify(request: Request, response: Response):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing token")

    try:
        payload = jwt.decode(auth[7:], settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

    response.headers["X-User-Id"] = payload["sub"]
    response.headers["X-Username"] = payload["username"]
    response.headers["X-Email"] = payload["email"]
    return {"status": "ok"}
