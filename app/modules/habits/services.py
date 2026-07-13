# app/modules/habits/services.py
from app.core.exceptions import HabitNotFoundError
from app.modules.habits.models import Habit
from app.modules.habits.repositories import HabitRepository
from app.modules.habits.schemas import HabitUpdate


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
