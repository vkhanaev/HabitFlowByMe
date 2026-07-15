class DomainException(Exception):
    pass


class UserAlreadyExistsError(DomainException):
    pass


class InvalidCredentialsError(DomainException):
    pass


class HabitNotFoundError(DomainException):
    def __init__(self) -> None:
        super().__init__("Habit not found")


class HabitAlreadyLoggedError(DomainException):
    def __init__(self) -> None:
        super().__init__("Habit already logged for this date")


class HabitArchivedError(DomainException):
    def __init__(self) -> None:
        super().__init__("Cannot log an archived habit")


class FutureLogDateError(DomainException):
    def __init__(self) -> None:
        super().__init__("Cannot log habits for future dates")
