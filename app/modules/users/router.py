from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_current_user
from app.modules.users.di import get_auth_service
from app.modules.users.models import User
from app.modules.users.schemas import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.users.services import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    payload: RegisterRequest, service: AuthService = Depends(get_auth_service)
) -> User:
    user = await service.register(payload.email, payload.password)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user and return access token. "
    "**Username is your email address.**",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    token = await service.login(form_data.username, form_data.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
