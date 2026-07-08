# Импортируем модели сюда, чтобы Alembic и SQLAlchemy знали о них
from app.modules.habits.models import Habit
from app.modules.users.models import User

__all__ = ["User", "Habit"]
