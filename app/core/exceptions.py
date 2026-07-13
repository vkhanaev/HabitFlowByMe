class DomainException(Exception):
    """Базовый класс для всех бизнес-исключений. Не знает ничего про HTTP."""

    pass


class UserAlreadyExistsError(DomainException):
    pass


class InvalidCredentialsError(DomainException):
    pass


class HabitNotFoundError(DomainException):
    def __init__(self) -> None:
        super().__init__("Habit not found")
