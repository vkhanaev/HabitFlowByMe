import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import HabitAlreadyLoggedError
from app.modules.habits.models import Habit, HabitLog


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

    # HabitLog
    async def log_completion(self, habit_id: int, log_date: datetime.date) -> HabitLog:
        """
        Создает запись о выполнении привычки.

        Использует begin_nested() для создания savepoint.
        Это позволяет откатить только текущую операцию при дубликате,
        не затрагивая предыдущие изменения в транзакции.

        Пример:
            Если в одном запросе делается:
            1. create_habit() - успешно
            2. log_completion() - дубликат

            То create_habit() НЕ откатится, откатится только log_completion().
        """
        log = HabitLog(habit_id=habit_id, log_date=log_date)
        self.db.add(log)

        try:
            # begin_nested() создает savepoint в транзакции
            async with self.db.begin_nested():
                await self.db.flush()
        except IntegrityError as exc:
            raise HabitAlreadyLoggedError() from exc

        return log

    async def get_log_dates_desc(self, habit_id: int) -> list[datetime.date]:
        """Возвращает все даты логов привычки в обратном порядке."""
        stmt = (
            select(HabitLog.log_date)
            .where(HabitLog.habit_id == habit_id)
            .order_by(HabitLog.log_date.desc())
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_total_logs_count(self, habit_id: int) -> int:
        stmt = select(func.count(HabitLog.id)).where(HabitLog.habit_id == habit_id)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())
