from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db

router = APIRouter(
    prefix="/api",
    tags=["health"],
)


@router.get("/health")
async def healthcheck():
    return {"status": "ok"}


@router.get("/db/health")
async def healthcheck_db(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
