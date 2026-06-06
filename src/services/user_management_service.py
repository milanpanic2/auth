import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import User
from src.database.connection import get_db
from src.models import BearerTokenResponse, LoginRequest, RegisterRequest


class UserManagementService:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def login_with_google(self, request):
        raise HTTPException(501, "Unimplemented")
