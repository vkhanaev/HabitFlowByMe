import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.models import User


class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_archived: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="habits")
    logs: Mapped[list["HabitLog"]] = relationship(
        back_populates="habit", cascade="all, delete-orphan"
    )


class HabitLog(Base, TimestampMixin):
    __tablename__ = "habit_logs"

    __table_args__ = (
        UniqueConstraint("habit_id", "log_date", name="uq_habit_logs_habit_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"),
    )
    log_date: Mapped[datetime.date] = mapped_column(Date)

    habit: Mapped["Habit"] = relationship(back_populates="logs")
