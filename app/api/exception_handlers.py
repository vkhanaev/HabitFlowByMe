import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DomainException,
    FutureLogDateError,
    HabitAlreadyLoggedError,
    HabitArchivedError,
    HabitNotFoundError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует глобальные обработчики исключений для преобразования DomainException в HTTP."""

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(
        request: Request, exc: UserAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "User already exists"},
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(HabitNotFoundError)
    async def habit_not_found_handler(
        request: Request, exc: HabitNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Habit not found"},
        )

    # Fallback для непредвиденных бизнес-ошибок.
    # Возвращаем 400 Bad Request вместо 500, так как это ожидаемая бизнес-ошибка, а не краш сервера.
    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request, exc: DomainException
    ) -> JSONResponse:
        logger.warning(f"Domain exception: {exc.__class__.__name__} - {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc) or "Business logic error occurred"},
        )

    @app.exception_handler(HabitAlreadyLoggedError)
    async def habit_already_logged_handler(
        _request: Request, exc: HabitAlreadyLoggedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Habit already logged for this date"},
        )

    @app.exception_handler(HabitArchivedError)
    async def habit_archived_handler(
        _request: Request, exc: HabitArchivedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Cannot log an archived habit"},
        )

    @app.exception_handler(FutureLogDateError)
    async def future_log_date_handler(
        _request: Request, exc: FutureLogDateError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Cannot log habits for future dates"},
        )
