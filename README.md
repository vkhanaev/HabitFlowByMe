# HabitFlowByMe

Backend приложения HabitFlow, реализованный на FastAPI.

## Технологии

* Python 3.13+
* FastAPI
* Uvicorn
* uv

## Требования

* Python 3.13 или выше
* uv

## Установка

Клонируйте репозиторий:

```bash
git clone <repository-url>
cd HabitFlowByMe
```

Установите зависимости:

```bash
uv sync
```

## Запуск

Запустите сервер разработки:

```bash
uv run uvicorn app.main:app --reload
```

После запуска приложение будет доступно по адресу:

* http://127.0.0.1:8000

Документация API:

* Swagger UI — `/docs`
* ReDoc — `/redoc`

Проверка работоспособности:

* `GET /health`

## Структура проекта

```text
HabitFlowByMe/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Переменные окружения

На текущем этапе проект не использует переменные окружения.

## Статус проекта

🚧 Проект находится в активной разработке.
