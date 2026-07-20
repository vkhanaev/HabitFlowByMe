import datetime
from collections import defaultdict
from typing import Any

from sqlalchemy import delete, func, select
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

    async def get_habits_with_stats(self, user_id: int) -> list[dict[str, Any]]:
        """Эффективно получает привычки и их статистику за 2 запроса (решение N+1)."""
        # 1. Получаем привычки
        stmt = select(Habit).where(
            Habit.user_id == user_id, Habit.is_archived.is_(False)
        )
        result = await self.db.execute(stmt)
        habits = list(result.scalars().all())

        if not habits:
            return []

        habit_ids = [h.id for h in habits]
        today = datetime.date.today()

        # 2. Получаем все логи для этих привычек одним запросом
        logs_stmt = (
            select(HabitLog.habit_id, HabitLog.log_date)
            .where(HabitLog.habit_id.in_(habit_ids))
            .order_by(HabitLog.log_date.desc())
        )
        logs_result = await self.db.execute(logs_stmt)
        logs = logs_result.all()

        # 3. Группируем логи по habit_id в памяти (это очень быстро)
        habit_logs_map = defaultdict(list)
        for log in logs:
            habit_logs_map[log.habit_id].append(log.log_date)

        # 4. Собираем итоговый результат
        result_data = []
        for habit in habits:
            dates = habit_logs_map.get(habit.id, [])

            # Используем ту же логику расчета стрика, что и в сервисе (можно вынести в утилиту)
            streak = 0
            if dates and dates[0] >= today - datetime.timedelta(days=1):
                streak = 1
                for i in range(1, len(dates)):
                    if dates[i - 1] - dates[i] == datetime.timedelta(days=1):
                        streak += 1
                    else:
                        break

            result_data.append(
                {
                    "habit": habit,
                    "current_streak": streak,
                    "completed_today": today in dates,
                }
            )

        return result_data

    async def is_logged_on_date(self, habit_id: int, date: datetime.date) -> bool:
        """Проверяет, есть ли лог за указанную дату."""
        stmt = select(HabitLog.id).where(
            HabitLog.habit_id == habit_id, HabitLog.log_date == date
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_log_by_date(self, habit_id: int, date: datetime.date) -> bool:
        """Удаляет лог за указанную дату. Возвращает True, если лог был удален."""
        stmt = delete(HabitLog).where(
            HabitLog.habit_id == habit_id, HabitLog.log_date == date
        )
        result = await self.db.execute(stmt)
        rowcount = getattr(result, "rowcount", 0)
        return bool(rowcount and rowcount > 0)

    async def get_logs_for_period(
        self, habit_id: int, start_date: datetime.date, end_date: datetime.date
    ) -> list[datetime.date]:
        """Получает все даты логов за указанный период."""
        stmt = (
            select(HabitLog.log_date)
            .where(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date >= start_date,
                HabitLog.log_date <= end_date,
            )
            .order_by(HabitLog.log_date)
        )

        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]
