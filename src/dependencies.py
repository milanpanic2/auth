from fastapi import Depends
from src.database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.services import UserManagementService

def get_user_management_service(db: AsyncSession = Depends(get_db)) -> UserManagementService:
    return UserManagementService(db=db)