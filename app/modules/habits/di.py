from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.modules.habits.repositories import HabitRepository
from app.modules.habits.services import HabitService


def get_habit_repository(db: AsyncSession = Depends(get_db)) -> HabitRepository:
    return HabitRepository(db)


def get_habit_service(
    repo: HabitRepository = Depends(get_habit_repository),
) -> HabitService:
    return HabitService(repo)
