import datetime

from app.core.exceptions import (
    FutureLogDateError,
    HabitArchivedError,
    HabitNotFoundError,
)
from app.modules.habits.models import Habit, HabitLog
from app.modules.habits.repositories import HabitRepository
from app.modules.habits.schemas import HabitStatsResponse, HabitUpdate


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
