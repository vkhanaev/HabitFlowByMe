from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserAlreadyExistsError
from app.modules.users.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        try:
            await self.db.flush()
        except IntegrityError as e:
            # Ловим race condition
            await self.db.rollback()
            raise UserAlreadyExistsError() from e
        return user
