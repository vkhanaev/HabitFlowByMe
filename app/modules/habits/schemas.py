import datetime

from pydantic import BaseModel, ConfigDict, Field


class HabitCreate(BaseModel):
    title: str
    description: str | None = None


class HabitUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class HabitResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_archived: bool
    current_streak: int = 0
    completed_today: bool = False

    model_config = ConfigDict(from_attributes=True)


# Схемы для HabitLog
class HabitLogCreate(BaseModel):
    log_date: datetime.date | None = Field(
        default=None, description="Defaults to today if not provided"
    )


class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    log_date: datetime.date

    model_config = ConfigDict(from_attributes=True)


class HabitStatsResponse(BaseModel):
    current_streak: int
    total_logs: int
