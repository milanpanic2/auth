import re
import jwt
from fastapi import Depends, HTTPException
from src.database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
from datetime import datetime, timezone, timedelta

from src.models import RegisterRequest, BearerTokenResponse
from src.models import LoginRequest
from src.database import User
from src.config import settings


class UserManagementService:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def login_with_google(self, request):
        raise HTTPException(501, "Unimplemented")
