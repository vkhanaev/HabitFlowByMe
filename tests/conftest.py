import sys

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from alembic import command
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.deps import get_db
from app.main import app
from app.modules.habits.models import Habit
from app.modules.users.models import User

# КРИТИЧНО: SelectorEventLoop для Windows + asyncpg
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# 1. СИНХРОННАЯ фикстура для миграций (выполняется 1 раз за весь прогон)
@pytest.fixture(scope="session", autouse=True)
def setup_database_schema():
    """Применяет миграции Alembic синхронно до запуска любых async тестов."""
    async_url = get_settings().database_url
    sync_url = async_url.replace("+asyncpg", "+psycopg2")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_url)

    command.upgrade(alembic_cfg, "head")
    yield


# 2. FUNCTION-SCOPED Engine (Гарантирует отсутствие конфликтов event loop)
@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """
    Создаем движок для каждого теста. Это предотвращает ошибки
    'attached to a different loop' в asyncpg.
    """
    async_url = get_settings().database_url
    engine = create_async_engine(
        async_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    yield engine
    # Корректно закрываем пул после каждого теста
    await engine.dispose()


# 3. FUNCTION-SCOPED Session с откатом транзакции
@pytest_asyncio.fixture(scope="function")
async def db(test_engine):
    """
    Создает новую сессию и транзакцию для каждого теста.
    После теста транзакция откатывается, оставляя БД чистой.
    """
    async with test_engine.connect() as connection:
        trans = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


# 4. Тестовый клиент
@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# === УТИЛИТЫ И ФАБРИКИ ===


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def user_factory(db: AsyncSession):
    async def _factory(
        email: str = "test@example.com", password: str = "Password123!"
    ) -> tuple[User, str]:
        user = User(email=email, hashed_password=hash_password(password))
        db.add(user)
        await db.flush()
        await db.refresh(user)

        token = create_access_token({"sub": str(user.id)})
        return user, token

    return _factory


@pytest.fixture(scope="function")
def habit_factory(db: AsyncSession):
    async def _factory(
        user_id: int, title: str = "Test Habit", description: str | None = None
    ) -> Habit:
        habit = Habit(user_id=user_id, title=title, description=description)
        db.add(habit)
        await db.flush()
        await db.refresh(habit)
        return habit

    return _factory
