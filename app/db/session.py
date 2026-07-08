from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

async_engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=True,
    autocommit=False,
    expire_on_commit=False,  # Важно для асинхронного режима
)
