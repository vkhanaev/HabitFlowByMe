from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.habits.models import Habit


class HabitRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, title: str, description: str | None) -> Habit:
        habit = Habit(user_id=user_id, title=title, description=description)
        self.db.add(habit)
        await self.db.flush()
        await self.db.refresh(habit)
        return habit

    async def get_by_id_and_user(self, habit_id: int, user_id: int) -> Habit | None:
        stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self, user_id: int, include_archived: bool = False
    ) -> list[Habit]:
        stmt = select(Habit).where(Habit.user_id == user_id)
        if not include_archived:
            stmt = stmt.where(Habit.is_archived.is_(False))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, habit: Habit) -> Habit:
        return habit

    async def delete(self, habit: Habit) -> None:
        await self.db.delete(habit)
