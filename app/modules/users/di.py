from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.modules.users.repositories import UserRepository
from app.modules.users.services import AuthService


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)
