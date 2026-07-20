from fastapi import Cookie, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError
from app.core.security import decode_access_token
from app.db.deps import get_db
from app.modules.users.models import User


async def get_web_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if access_token is None:
        raise InvalidCredentialsError()

    try:
        payload = decode_access_token(access_token)
        user_id = int(payload["sub"])
    except Exception as exc:
        raise InvalidCredentialsError() from exc

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise InvalidCredentialsError()

    return user
