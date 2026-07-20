import datetime
from typing import Any

from app.core.exceptions import (
    FutureLogDateError,
    HabitArchivedError,
    HabitNotFoundError,
)
from app.modules.habits.models import Habit, HabitLog
from app.modules.habits.repositories import HabitRepository
from app.modules.habits.schemas import HabitResponse, HabitStatsResponse, HabitUpdate


class HabitService:
    def __init__(self, repo: HabitRepository):
        self.repo = repo

    async def _get_habit_or_raise(self, habit_id: int, user_id: int) -> Habit:
        habit = await self.repo.get_by_id_and_user(habit_id, user_id)
        if not habit:
            raise HabitNotFoundError()
        return habit

    async def create_habit(
        self, user_id: int, title: str, description: str | None
    ) -> Habit:
        return await self.repo.create(
            user_id=user_id, title=title, description=description
        )

    async def list_habits(
        self, user_id: int, include_archived: bool = False
    ) -> list[Habit]:
        return await self.repo.get_all_by_user(
            user_id, include_archived=include_archived
        )

    async def archive_habit(self, habit_id: int, user_id: int) -> Habit:
        habit = await self._get_habit_or_raise(habit_id, user_id)
        if not habit.is_archived:  #
            habit.is_archived = True
            return await self.repo.update(habit)
        return habit

    async def update_habit(
        self, habit_id: int, user_id: int, update_data: HabitUpdate
    ) -> Habit:
        habit = await self._get_habit_or_raise(habit_id, user_id)

        # Даже если в HabitUpdate добавят user_id, он НИКОГДА не обновится здесь.
        update_dict = update_data.model_dump(exclude_unset=True)
        if "title" in update_dict:
            habit.title = update_dict["title"]
        if "description" in update_dict:
            habit.description = update_dict["description"]

        return await self.repo.update(habit)

    async def delete_habit(self, habit_id: int, user_id: int) -> None:
        habit = await self._get_habit_or_raise(habit_id, user_id)
        await self.repo.delete(habit)

    async def log_completion(
        self, habit_id: int, user_id: int, log_date: datetime.date | None = None
    ) -> HabitLog:
        habit = await self._get_habit_or_raise(habit_id, user_id)

        if habit.is_archived:
            raise HabitArchivedError()

        target_date = log_date or datetime.date.today()

        if target_date > datetime.date.today():
            raise FutureLogDateError()

        return await self.repo.log_completion(habit_id, target_date)

    async def get_habit_stats(self, habit_id: int, user_id: int) -> HabitStatsResponse:
        await self._get_habit_or_raise(habit_id, user_id)

        dates = await self.repo.get_log_dates_desc(habit_id)
        streak = self._calculate_current_streak(dates)
        total = await self.repo.get_total_logs_count(habit_id)

        return HabitStatsResponse(
            current_streak=streak,
            total_logs=total,
        )

    def _calculate_current_streak(self, dates: list[datetime.date]) -> int:
        """
        БИЗНЕС-ПРАВИЛО (вариант A из пункта 6):
        Стрик считается от последнего выполненного дня.

        Примеры:
        - Логи: [15, 14, 13] (сегодня=15) → стрик = 3
        - Логи: [14, 13, 12] (сегодня=15) → стрик = 3 (вариант A)
        - Логи: [13, 12, 11] (сегодня=15) → стрик = 0 (пропуск дня)
        """
        if not dates:
            return 0

        today = datetime.date.today()

        if dates[0] < today - datetime.timedelta(days=1):
            return 0

        streak = 1
        for i in range(1, len(dates)):
            if dates[i - 1] - dates[i] == datetime.timedelta(days=1):
                streak += 1
            else:
                break

        return streak

    async def list_habits_dashboard(self, user_id: int) -> list[HabitResponse]:
        raw_data = await self.repo.get_habits_with_stats(user_id)

        return [
            HabitResponse(
                id=data["habit"].id,
                title=data["habit"].title,
                description=data["habit"].description,
                is_archived=data["habit"].is_archived,
                current_streak=data["current_streak"],
                completed_today=data["completed_today"],
            )
            for data in raw_data
        ]

    async def is_completed_today(self, habit_id: int, user_id: int) -> bool:
        """Проверяет, выполнена ли привычка сегодня."""
        await self._get_habit_or_raise(habit_id, user_id)
        today = datetime.date.today()
        return await self.repo.is_logged_on_date(habit_id, today)

    async def get_habit(self, habit_id: int, user_id: int) -> Habit:
        return await self._get_habit_or_raise(habit_id, user_id)

    async def toggle_completion(self, habit_id: int, user_id: int) -> bool:
        """
        Переключает статус выполнения привычки за сегодня.
        Возвращает True, если привычка теперь выполнена, False если отменена.
        """
        habit = await self._get_habit_or_raise(habit_id, user_id)

        if habit.is_archived:
            raise HabitArchivedError()

        today = datetime.date.today()
        is_completed = await self.repo.is_logged_on_date(habit_id, today)

        if is_completed:
            # Отменяем выполнение
            await self.repo.delete_log_by_date(habit_id, today)
            return False
        else:
            # Отмечаем выполнение
            await self.repo.log_completion(habit_id, today)
            return True

    async def get_completion_calendar(
        self, habit_id: int, user_id: int
    ) -> dict[int, bool]:
        """
        Возвращает календарь выполнений за ТЕКУЩИЙ месяц.
        Ключ - день месяца (1-31), значение - выполнена ли привычка.
        """
        await self._get_habit_or_raise(habit_id, user_id)

        today = datetime.date.today()
        #  Берем период строго с 1-го числа текущего месяца
        start_date = today.replace(day=1)

        logs = await self.repo.get_logs_for_period(habit_id, start_date, today)

        calendar = {}
        # Идем по всем дням текущего месяца
        for day_offset in range((today - start_date).days + 1):
            current_date = start_date + datetime.timedelta(days=day_offset)
            day_of_month = current_date.day
            calendar[day_of_month] = current_date in logs

        return calendar

    async def toggle_completion_for_date(
        self, habit_id: int, user_id: int, date: datetime.date
    ) -> bool:
        """
        Переключает статус выполнения привычки за указанную дату.
        Возвращает True, если привычка теперь выполнена, False если отменена.
        """
        habit = await self._get_habit_or_raise(habit_id, user_id)

        if habit.is_archived:
            raise HabitArchivedError()

        is_completed = await self.repo.is_logged_on_date(habit_id, date)

        if is_completed:
            # Отменяем выполнение
            await self.repo.delete_log_by_date(habit_id, date)
            return False
        else:
            # Отмечаем выполнение
            await self.repo.log_completion(habit_id, date)
            return True

    async def get_sliding_window_calendar(
        self, habit_id: int, user_id: int, days: int = 31
    ) -> list[dict[str, Any]]:
        """
        Возвращает данные для скользящего окна (последние N дней).
        Возвращает список словарей: [{"date": ..., "day": 17, "is_completed": True}, ...]
        """
        await self._get_habit_or_raise(habit_id, user_id)

        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days - 1)

        # Получаем все логи за этот период
        logs = await self.repo.get_logs_for_period(habit_id, start_date, today)

        calendar_data = []
        for i in range(days):
            current_date = start_date + datetime.timedelta(days=i)
            calendar_data.append(
                {
                    "date": current_date,
                    "day": current_date.day,  # Просто число для отображения (1-31)
                    "is_completed": current_date in logs,
                    "is_future": current_date > today,
                }
            )

        return calendar_data
