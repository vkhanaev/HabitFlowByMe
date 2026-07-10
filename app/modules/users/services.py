from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.users.models import User
from app.modules.users.repositories import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, email: str, password: str) -> User:
        email = email.lower()
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError()

        user = await self.user_repo.create(
            email=email,
            hashed_password=hash_password(password),
        )

        await self.user_repo.db.commit()
        await self.user_repo.db.refresh(user)
        return user

    async def login(self, username: str, password: str) -> str:
        # В нашем случае username — это email
        user = await self.user_repo.get_by_email(username.lower())
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        return create_access_token({"sub": str(user.id)})
