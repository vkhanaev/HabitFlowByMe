from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, TypedDict, cast

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import InvalidCredentialsError

# Инициализируем хешер с безопасными параметрами по умолчанию
# (time_cost=3, memory_cost=65536, parallelism=4)
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием Argon2id."""
    hashed: str = ph.hash(password)
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли пароль хешу. Безопасно обрабатывает битые хеши."""
    try:
        return cast(bool, ph.verify(hashed_password, plain_password))
    except (VerifyMismatchError, InvalidHash):
        # Если хеш поврежден или пароль не подходит, просто возвращаем False
        # Это предотвращает 500 Internal Server Error при логине
        return False


# --- Типизация JWT Payload (твоя отличная идея из пункта 4!) ---
class TokenPayload(TypedDict):
    sub: str
    exp: int
    iat: int
    type: Literal["access"]


def create_access_token(data: Mapping[str, Any]) -> str:
    settings = get_settings()
    to_encode = dict(data)

    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update(
        {
            "exp": int(expire.timestamp()),  # JWT ожидает int для timestamp
            "iat": int(now.timestamp()),
            "type": "access",
        }
    )

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return cast(str, encoded_jwt)


def decode_access_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        if payload.get("type") != "access":
            raise InvalidCredentialsError()
        return cast(TokenPayload, payload)
    except JWTError as exc:
        raise InvalidCredentialsError() from exc
