import contextlib
import datetime

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.core.exceptions import HabitNotFoundError
from app.modules.habits.di import get_habit_service
from app.modules.habits.schemas import HabitUpdate
from app.modules.habits.services import HabitService
from app.modules.users.models import User
from app.web.deps import get_web_user
from app.web.templates_config import templates

router = APIRouter(tags=["Web Habits"])


@router.get("/")
async def home(request: Request) -> RedirectResponse:
    """Главная страница: редирект на /habits или /login в зависимости от авторизации."""
    # Проверяем наличие токена в cookie
    token = request.cookies.get("access_token")

    if token:
        # Пользователь авторизован — отправляем на список привычек
        return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)
    else:
        # Пользователь не авторизован — отправляем на страницу входа
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/habits/create")
async def create_habit_page(
    request: Request,
    user: User = Depends(get_web_user),
) -> HTMLResponse:
    """Страница создания новой привычки."""
    return templates.TemplateResponse(
        request,
        "habits/form.html",
        {"user": user, "habit": None},
    )


@router.get("/habits/{habit_id}/edit")
async def edit_habit_page(
    request: Request,
    habit_id: int,
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> Response:
    """Страница редактирования привычки."""
    try:
        habit = await service.get_habit(habit_id, user.id)
    except HabitNotFoundError:
        return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request,
        "habits/form.html",
        {"user": user, "habit": habit},
    )


@router.post("/habits/{habit_id}")
async def update_habit_submit(
    request: Request,
    habit_id: int,
    title: str = Form(...),
    description: str = Form(None),
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> Response:
    """Обработка формы редактирования привычки."""
    if not title or not title.strip():
        try:
            habit = await service.get_habit(habit_id, user.id)
        except HabitNotFoundError:
            return RedirectResponse(
                url="/habits", status_code=status.HTTP_303_SEE_OTHER
            )

        return templates.TemplateResponse(
            request,
            "habits/form.html",
            {
                "user": user,
                "habit": habit,
                "error": "Название привычки обязательно",
                "title": title,
                "description": description,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    update_data = HabitUpdate(
        title=title.strip(),
        description=description.strip() if description else None,
    )

    try:
        await service.update_habit(habit_id, user.id, update_data)
    except HabitNotFoundError:
        return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/habits/{habit_id}/delete")
async def delete_habit(
    habit_id: int,
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> RedirectResponse:
    """Удаление привычки."""
    with contextlib.suppress(HabitNotFoundError):
        await service.delete_habit(habit_id, user.id)

    return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/habits/{habit_id}/toggle")
async def toggle_habit_completion(
    habit_id: int,
    request: Request,
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> Response:
    """Переключить статус выполнения привычки за сегодня."""
    is_completed = await service.toggle_completion(habit_id=habit_id, user_id=user.id)

    # Проверяем, был ли запрос от HTMX
    if request.headers.get("HX-Request") == "true":
        # Возвращаем только обновленную карточку
        habit = await service.get_habit(habit_id, user.id)
        stats = await service.get_habit_stats(habit_id, user.id)
        calendar = await service.get_completion_calendar(habit_id, user.id)

        item = {
            "habit": habit,
            "stats": stats,
            "completed_today": is_completed,
            "calendar": calendar,
        }

        return templates.TemplateResponse(
            request,
            "habits/_habit_card.html",
            {"item": item},
        )
    else:
        # Fallback для обычных форм (без HTMX)
        return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/habits")
async def habits_list(
    request: Request,
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> HTMLResponse:
    """Список всех привычек пользователя с календарем выполнений."""
    habits = await service.list_habits(user.id, include_archived=False)

    habits_with_data = []
    today = datetime.date.today()  # <-- Обязательно эта строка

    for habit in habits:
        stats = await service.get_habit_stats(habit.id, user.id)
        completed_today = await service.is_completed_today(habit.id, user.id)
        calendar = await service.get_completion_calendar(habit.id, user.id)

        habits_with_data.append(
            {
                "habit": habit,
                "stats": stats,
                "completed_today": completed_today,
                "calendar": calendar,
            }
        )

    return templates.TemplateResponse(
        request,
        "habits/list.html",
        {
            "user": user,
            "habits_with_data": habits_with_data,
            "today": today,
        },
    )


@router.post("/habits", response_model=None)
async def create_habit_submit(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> Response:
    if not title or not title.strip():
        return templates.TemplateResponse(
            request,
            "habits/form.html",
            {
                "user": user,
                "habit": None,
                "error": "Название привычки обязательно",
                "title": title,
                "description": description,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    await service.create_habit(
        user_id=user.id,
        title=title.strip(),
        description=description.strip() if description else None,
    )

    return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/habits/{habit_id}/toggle-date")
async def toggle_habit_date(
    habit_id: int,
    request: Request,
    date_str: str = Form(...),
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> Response:
    """Переключить статус выполнения за дату (для страницы /habits с текущим месяцем)."""
    target_date = datetime.date.fromisoformat(date_str)
    today = datetime.date.today()  # <-- 1. Обязательно определяем today

    if target_date <= today:
        await service.toggle_completion_for_date(
            habit_id=habit_id, user_id=user.id, date=target_date
        )

    if request.headers.get("HX-Request") == "true":
        # Получаем обновленные данные
        habit = await service.get_habit(habit_id, user.id)
        stats = await service.get_habit_stats(habit_id, user.id)
        completed_today = await service.is_completed_today(habit_id, user.id)
        calendar = await service.get_completion_calendar(habit_id, user.id)

        item = {
            "habit": habit,
            "stats": stats,
            "completed_today": completed_today,
            "calendar": calendar,
        }

        # <-- 2. Возвращаем ИМЕННО _habit_card.html (не sliding!)
        # <-- 3. Обязательно передаем today в контекст
        return templates.TemplateResponse(
            request,
            "habits/_habit_card.html",
            {
                "item": item,
                "today": today,
            },
        )

    return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/habits/{habit_id}/calendar")
async def get_habit_calendar(
    habit_id: int,
    request: Request,
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> HTMLResponse:
    """Endpoint для HTMX: возвращает HTML скользящего календаря."""
    calendar_data = await service.get_sliding_window_calendar(habit_id, user.id)

    return templates.TemplateResponse(
        request,
        "habits/_sliding_calendar.html",
        {"calendar_data": calendar_data, "habit_id": habit_id},
    )


@router.get("/habits/{habit_id}/stats")
async def habit_stats_page(
    request: Request,
    habit_id: int,
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> HTMLResponse:
    """Страница со статистикой привычки и скользящим окном за 31 день."""
    habit = await service.get_habit(habit_id, user.id)
    stats = await service.get_habit_stats(habit_id, user.id)
    sliding_calendar = await service.get_sliding_window_calendar(
        habit_id, user.id, days=31
    )

    # Считаем процент выполнения за последние 31 день
    completed_days = sum(
        1 for item in sliding_calendar if item["is_completed"] and not item["is_future"]
    )
    total_days = sum(1 for item in sliding_calendar if not item["is_future"])
    completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0

    return templates.TemplateResponse(
        request,
        "habits/stats.html",
        {
            "habit": habit,
            "stats": stats,
            "sliding_calendar": sliding_calendar,
            "completion_rate": completion_rate,
            "completed_days": completed_days,
            "total_days": total_days,
        },
    )


@router.get("/habits_sliding")
async def habits_list_sliding(
    request: Request,
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> HTMLResponse:
    """Список всех привычек со скользящим окном за 31 день."""
    habits = await service.list_habits(user.id, include_archived=False)

    habits_with_data = []
    today = datetime.date.today()

    for habit in habits:
        stats = await service.get_habit_stats(habit.id, user.id)
        completed_today = await service.is_completed_today(habit.id, user.id)

        #  Получаем данные за последние 31 день (скользящее окно)
        sliding_calendar = await service.get_sliding_window_calendar(
            habit.id, user.id, days=31
        )

        habits_with_data.append(
            {
                "habit": habit,
                "stats": stats,
                "completed_today": completed_today,
                "sliding_calendar": sliding_calendar,  # <-- Передаем список словарей
            }
        )

    return templates.TemplateResponse(
        request,
        "habits/list_sliding.html",
        {
            "user": user,
            "habits_with_data": habits_with_data,
            "today": today,
        },
    )


@router.post("/habits/{habit_id}/toggle-date-sliding")
async def toggle_habit_date_sliding(
    habit_id: int,
    request: Request,
    date_str: str = Form(...),
    user: User = Depends(get_web_user),
    service: HabitService = Depends(get_habit_service),
) -> Response:
    """Переключить статус выполнения привычки за конкретную дату (для скользящего окна)."""
    target_date = datetime.date.fromisoformat(date_str)
    today = datetime.date.today()

    if target_date <= today:
        await service.toggle_completion_for_date(
            habit_id=habit_id, user_id=user.id, date=target_date
        )

    if request.headers.get("HX-Request") == "true":
        # Получаем обновлённые данные
        habit = await service.get_habit(habit_id, user.id)
        stats = await service.get_habit_stats(habit_id, user.id)
        completed_today = await service.is_completed_today(habit_id, user.id)
        sliding_calendar = await service.get_sliding_window_calendar(
            habit_id, user.id, days=31
        )

        item = {
            "habit": habit,
            "stats": stats,
            "completed_today": completed_today,
            "sliding_calendar": sliding_calendar,
        }

        return templates.TemplateResponse(
            request,
            "habits/_habit_card_sliding.html",
            {"item": item},
        )

    return RedirectResponse(
        url="/habits_sliding", status_code=status.HTTP_303_SEE_OTHER
    )
