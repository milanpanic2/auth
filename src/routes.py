from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import User, get_db
from src.dependencies import get_user_management_service
from src.models import BearerTokenResponse, LoginRequest, RegisterRequest, UserResponse
from src.services.user_management_service import UserManagementService

router = APIRouter(prefix="/api/v1", tags=["auth"])


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
        password = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode(),
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

    if not db_user or not bcrypt.checkpw(body.password.encode(), db_user.password.encode()):
        raise HTTPException(401, "Failed authorizaion.")

    payload = {
        "sub": str(db_user.id),
        "username": db_user.email,
        "email": db_user.email,
        "exp": datetime.now(UTC) + timedelta(minutes=settings.jwt_expiration_minutes),
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
        raise HTTPException(401, "Token expired") from None
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token") from None

    response.headers["X-User-Id"] = payload["sub"]
    response.headers["X-Username"] = payload["username"]
    response.headers["X-Email"] = payload["email"]
    return {"status": "ok"}


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment
    }
