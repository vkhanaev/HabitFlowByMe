import datetime

from httpx import AsyncClient

from tests.conftest import auth_headers


async def test_log_habit_success(client: AsyncClient, user_factory, habit_factory):
    user, token = await user_factory(email="streak@test.com")
    habit = await habit_factory(user_id=user.id, title="Read 10 pages")

    response = await client.post(
        f"/api/habits/{habit.id}/log",
        json={},
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["habit_id"] == habit.id
    assert data["log_date"] == str(datetime.date.today())


async def test_log_habit_twice_same_day_returns_409(
    client: AsyncClient, user_factory, habit_factory
):
    user, token = await user_factory(email="double@test.com")
    habit = await habit_factory(user_id=user.id, title="Drink water")

    response1 = await client.post(
        f"/api/habits/{habit.id}/log",
        json={},
        headers=auth_headers(token),
    )
    assert response1.status_code == 201

    response2 = await client.post(
        f"/api/habits/{habit.id}/log",
        json={},
        headers=auth_headers(token),
    )

    assert response2.status_code == 409
    assert response2.json()["detail"] == "Habit already logged for this date"


async def test_log_archived_habit_returns_400(
    client: AsyncClient, user_factory, habit_factory
):
    user, token = await user_factory(email="archived@test.com")
    habit = await habit_factory(user_id=user.id, title="Old habit")

    await client.patch(f"/api/habits/{habit.id}/archive", headers=auth_headers(token))

    response = await client.post(
        f"/api/habits/{habit.id}/log",
        json={},
        headers=auth_headers(token),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot log an archived habit"


async def test_log_future_date_returns_400(
    client: AsyncClient, user_factory, habit_factory
):
    user, token = await user_factory(email="future@test.com")
    habit = await habit_factory(user_id=user.id, title="Future habit")

    future_date = datetime.date.today() + datetime.timedelta(days=1)

    response = await client.post(
        f"/api/habits/{habit.id}/log",
        json={"log_date": str(future_date)},
        headers=auth_headers(token),
    )

    assert response.status_code == 400


# Тест на ownership
async def test_log_other_users_habit_returns_404(
    client: AsyncClient, user_factory, habit_factory
):
    user_a, token_a = await user_factory(email="user_a@test.com")
    user_b, _ = await user_factory(email="user_b@test.com")

    habit_b = await habit_factory(user_id=user_b.id, title="User B's habit")

    response = await client.post(
        f"/api/habits/{habit_b.id}/log",
        json={},
        headers=auth_headers(token_a),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Habit not found"


async def test_get_other_users_habit_stats_returns_404(
    client: AsyncClient, user_factory, habit_factory
):
    user_a, token_a = await user_factory(email="user_a@test.com")
    user_b, _ = await user_factory(email="user_b@test.com")

    habit_b = await habit_factory(user_id=user_b.id, title="User B's habit")

    response = await client.get(
        f"/api/habits/{habit_b.id}/stats",
        headers=auth_headers(token_a),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Habit not found"


async def test_habit_streak_calculation(
    client: AsyncClient, user_factory, habit_factory, db
):
    from app.modules.habits.models import HabitLog

    user, token = await user_factory(email="streak_calc@test.com")
    habit = await habit_factory(user_id=user.id, title="Meditate")

    today = datetime.date.today()

    for i in range(3):
        log = HabitLog(habit_id=habit.id, log_date=today - datetime.timedelta(days=i))
        db.add(log)
    await db.flush()

    response = await client.get(
        f"/api/habits/{habit.id}/stats", headers=auth_headers(token)
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_streak"] == 3
    assert data["total_logs"] == 3


async def test_log_habit_different_dates_success(
    client: AsyncClient, user_factory, habit_factory
):
    """Лог за разные даты — успешно."""
    user, token = await user_factory(email="multi@test.com")
    habit = await habit_factory(user_id=user.id, title="Exercise")

    # Сегодня
    response1 = await client.post(
        f"/api/habits/{habit.id}/log",
        json={},
        headers=auth_headers(token),
    )
    assert response1.status_code == 201

    # Вчера
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    response2 = await client.post(
        f"/api/habits/{habit.id}/log",
        json={"log_date": str(yesterday)},
        headers=auth_headers(token),
    )
    assert response2.status_code == 201


async def test_log_deleted_habit_returns_404(
    client: AsyncClient, user_factory, habit_factory
):
    """Лог удаленной привычки — 404."""
    user, token = await user_factory(email="deleted@test.com")
    habit = await habit_factory(user_id=user.id, title="To delete")

    # Удаляем привычку
    await client.delete(f"/api/habits/{habit.id}", headers=auth_headers(token))

    # Пытаемся логировать
    response = await client.post(
        f"/api/habits/{habit.id}/log",
        json={},
        headers=auth_headers(token),
    )

    assert response.status_code == 404


async def test_delete_habit_cascades_to_logs(
    client: AsyncClient, user_factory, habit_factory, db
):
    """Удаление Habit каскадно удаляет HabitLogs."""
    from sqlalchemy import select

    from app.modules.habits.models import HabitLog

    user, token = await user_factory(email="cascade@test.com")
    habit = await habit_factory(user_id=user.id, title="Cascade test")

    # Создаем логи
    for i in range(3):
        log = HabitLog(
            habit_id=habit.id,
            log_date=datetime.date.today() - datetime.timedelta(days=i),
        )
        db.add(log)
    await db.flush()

    # Удаляем привычку
    await client.delete(f"/api/habits/{habit.id}", headers=auth_headers(token))

    # Проверяем, что логи удалены
    result = await db.execute(select(HabitLog).where(HabitLog.habit_id == habit.id))
    logs = result.scalars().all()
    assert len(logs) == 0
