from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)
