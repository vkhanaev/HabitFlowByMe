from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession]:
    # Используем контекстный менеджер для безопасного открытия и закрытия
    async with AsyncSessionLocal() as db:
        yield db
