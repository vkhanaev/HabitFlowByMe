from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.modules.habits.di import get_habit_service
from app.modules.habits.schemas import HabitCreate, HabitResponse, HabitUpdate
from app.modules.habits.services import HabitService
from app.modules.users.models import User

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    payload: HabitCreate,
    service: HabitService = Depends(get_habit_service),
    user: User = Depends(get_current_user),
) -> HabitResponse:
    habit = await service.create_habit(user.id, payload.title, payload.description)
    return HabitResponse.model_validate(habit)


@router.get("", response_model=list[HabitResponse])
async def list_habits(
    include_archived: bool = False,
    service: HabitService = Depends(get_habit_service),
    user: User = Depends(get_current_user),
) -> list[HabitResponse]:
    habits = await service.list_habits(user.id, include_archived=include_archived)
    return [HabitResponse.model_validate(h) for h in habits]


@router.patch("/{habit_id}/archive", response_model=HabitResponse)
async def archive_habit(
    habit_id: int,
    service: HabitService = Depends(get_habit_service),
    user: User = Depends(get_current_user),
) -> HabitResponse:
    habit = await service.archive_habit(habit_id, user.id)
    return HabitResponse.model_validate(habit)


@router.patch("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: int,
    payload: HabitUpdate,
    service: HabitService = Depends(get_habit_service),
    user: User = Depends(get_current_user),
) -> HabitResponse:
    habit = await service.update_habit(habit_id, user.id, payload)
    return HabitResponse.model_validate(habit)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: int,
    service: HabitService = Depends(get_habit_service),
    user: User = Depends(get_current_user),
) -> None:
    await service.delete_habit(habit_id, user.id)
