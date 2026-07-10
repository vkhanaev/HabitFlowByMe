from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import InvalidCredentialsError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # type: ignore[no-any-return]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  # type: ignore[no-any-return]


def create_access_token(data: Mapping[str, Any]) -> str:
    settings = get_settings()
    to_encode = dict(data)

    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": now, "type": "access"})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)  # type: ignore[no-any-return]


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        if payload.get("type") != "access":
            raise InvalidCredentialsError()
        return payload  # type: ignore[no-any-return]
    except JWTError as exc:
        raise InvalidCredentialsError() from exc
