from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(status_code=status_code, detail=detail)


class UserAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )


class InvalidCredentialsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
