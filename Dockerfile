# --- Этап 1: Сборка зависимостей ---
FROM python:3.13-slim AS builder

# Копируем бинарники uv из официального образа в builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

# Переменная окружения для компиляции байт-кода (ускоряет запуск приложения)
ENV UV_COMPILE_BYTECODE=1

# Копируем только файлы конфигурации зависимостей (для кэширования слоев)
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости проекта.
# --frozen: гарантирует сборку строго по uv.lock без его изменения
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# --- Этап 2: Финальный легковесный образ ---
FROM python:3.13-slim

WORKDIR /code

# Устанавливаем postgresql-client, необходимый для работы команды pg_isready в entrypoint.sh
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем виртуальное окружение из предыдущего этапа
COPY --from=builder /code/.venv /code/.venv

# Копируем исходный код вашего приложения
COPY . .

# Делаем скрипт entrypoint исполняемым
RUN chmod +x docker/entrypoint.sh

# Добавляем виртуальное окружение в PATH.
# Это позволит entrypoint.sh напрямую вызывать alembic и uvicorn
# PYTHONUNBUFFERED=1 - Отключаем буферизацию вывода Python (чтобы логи приложения были видны сразу)
ENV PATH="/code/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["./docker/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]