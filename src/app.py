from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.config import settings
from src.database.connection import init_db, sync_engine
from src.config.telemetry import init_telemetry
from src.routes import router


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

app.include_router(router)
