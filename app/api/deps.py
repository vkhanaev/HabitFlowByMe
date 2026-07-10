from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError
from app.core.security import decode_access_token
from app.db.deps import get_db
from app.modules.users.models import User

# OAuth2PasswordBearer автоматически добавит кнопку "Authorize" в Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(token)

    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise InvalidCredentialsError() from None

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise InvalidCredentialsError()

    return user
