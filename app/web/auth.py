from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.modules.users.di import get_auth_service
from app.modules.users.services import AuthService
from app.web.templates_config import templates

router = APIRouter(tags=["Web Auth"])


@router.get("/login")
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login", response_model=None)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    service: AuthService = Depends(get_auth_service),
) -> Response:
    try:
        # Наш сервис ожидает username, но для нас это email
        token = await service.login(username=email, password=password)

        response = RedirectResponse(
            url="/habits", status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=3600,
        )
        return response
    except InvalidCredentialsError:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Неверный email или пароль"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


@router.get("/register")
async def register_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "auth/register.html")


@router.post("/register", response_model=None)
async def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    service: AuthService = Depends(get_auth_service),
) -> Response:
    try:
        await service.register(email=email, password=password)
        return RedirectResponse(
            url="/login?registered=1", status_code=status.HTTP_303_SEE_OTHER
        )
    except UserAlreadyExistsError:
        return templates.TemplateResponse(
            request,
            "auth/register.html",
            {"error": "Пользователь с таким email уже существует", "email": email},
            status_code=status.HTTP_409_CONFLICT,
        )


@router.post("/logout", response_model=None)
async def logout() -> Response:
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
