import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.logging import setup_logging
from app.db.session import async_engine

logger = logging.getLogger(__name__)


async def _check_database_connection() -> None:
    """Проверяем, что БД доступна на старте."""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful.")
    except Exception:
        logger.exception("Database connection failed.")
        raise  # Если БД недоступна, приложение не должно стартовать


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # --- startup ---
    setup_logging()

    logger.info("Application startup initiated...")

    # Проверяем БД
    await _check_database_connection()

    # Здесь позже подключим Redis, Kafka и т.д.

    yield

    # --- shutdown ---
    logger.info("Application shutdown initiated...")
    try:
        await async_engine.dispose()
        logger.info("Database connections closed.")
    except Exception:
        # Логируем ошибку, но не прерываем процесс остановки
        logger.exception("Error during DB engine disposal.")
