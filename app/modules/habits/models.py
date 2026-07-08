from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.models import User  # Импортируем модель User здесь


class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255))

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    is_archived: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="habits")
