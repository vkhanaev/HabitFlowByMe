from httpx import AsyncClient

from tests.conftest import auth_headers


async def test_create_habit_success(client: AsyncClient, user_factory):
    user, token = await user_factory(email="creator@test.com")

    payload = {"title": "Morning Run", "description": "5km every day"}
    response = await client.post(
        "/api/habits", json=payload, headers=auth_headers(token)
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Morning Run"
    assert data["is_archived"] is False
    assert "id" in data


async def test_create_habit_unauthorized(client: AsyncClient):
    """Попытка создать привычку без токена должна вернуть 401."""
    payload = {"title": "Morning Run"}
    response = await client.post("/api/habits", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_list_habits_isolation(client: AsyncClient, user_factory, habit_factory):
    """Проверяем, что User 1 НЕ видит привычки User 2."""
    user1, token1 = await user_factory(email="user1@test.com")
    user2, _ = await user_factory(email="user2@test.com")

    # Используем фабрику для создания данных напрямую в БД
    await habit_factory(user_id=user1.id, title="Habit of User 1")
    await habit_factory(user_id=user2.id, title="Secret Habit of User 2")

    response = await client.get("/api/habits", headers=auth_headers(token1))

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Habit of User 1"


async def test_update_other_users_habit_returns_404(
    client: AsyncClient, user_factory, habit_factory
):
    """Попытка изменить чужую привычку возвращает 404 (защита от IDOR)."""
    attacker, token_attacker = await user_factory(email="attacker@test.com")
    victim, _ = await user_factory(email="victim@test.com")

    # Жертва создает привычку
    habit = await habit_factory(user_id=victim.id, title="Secret Habit")

    # Атакующий пытается её обновить
    response = await client.patch(
        f"/api/habits/{habit.id}",
        json={"title": "Hacked!"},
        headers=auth_headers(token_attacker),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Habit not found"


async def test_delete_nonexistent_habit_returns_404(client: AsyncClient, user_factory):
    """Попытка удалить привычку, которой не существует (или чужую), возвращает 404."""
    user, token = await user_factory(email="user@test.com")

    response = await client.delete(
        "/api/habits/99999",  # Заведомо несуществующий ID
        headers=auth_headers(token),
    )

    assert response.status_code == 404
