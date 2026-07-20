#  HabitFlowByMe

**Трекер привычек с фокусом на визуальный прогресс и безопасность**

Современное веб-приложение для отслеживания ежедневных привычек с интерактивным календарём выполнения, статистикой серий (streaks) и профессиональной архитектурой.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Tests](https://img.shields.io/badge/Tests-Integration-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

##  Ключевые возможности

###  Пользовательский интерфейс
- **Интерактивный календарь** выполнения привычек (скользящее окно 31 день)
- **Визуализация прогресса** в стиле GitHub Contributions
- **Мгновенное обновление** без перезагрузки страницы (HTMX)
- **Адаптивный дизайн** с CSS-переменными
- **Inline SVG иконки** (без внешних зависимостей)

### 🔐 Безопасность
- **Argon2id** для хеширования паролей (золотой стандарт 2026)
- **JWT токены** с автоматическим обновлением
- **Защита от IDOR** (Insecure Direct Object Reference)
- **Race condition prevention** через database constraints
- **HttpOnly cookies** для web-аутентификации
- **404 вместо 403** для скрытия существования ресурсов

### 🏗 Архитектура
- **Модульная структура** (Vertical Slice Architecture)
- **Domain-Driven Design** с агрегатами
- **Repository Pattern** для изоляции БД
- **Service Layer** для бизнес-логики
- **Dependency Injection** через FastAPI
- **Transaction Management** на уровне инфраструктуры

### 📊 Аналитика
- **Текущая серия** (current streak) выполнения
- **Общее количество** выполнений
- **Процент выполнения** за период
- **Календарь текущего месяца** и скользящее окно

---

## 🛠 Технологический стек

| Категория | Технологии |
|-----------|-----------|
| **Backend** | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| **База данных** | PostgreSQL 16, asyncpg |
| **Миграции** | Alembic |
| **Аутентификация** | python-jose, argon2-cffi, passlib |
| **Frontend** | Jinja2, HTMX, Vanilla CSS |
| **Тестирование** | pytest, pytest-asyncio, httpx, factory_boy |
| **Инфраструктура** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Код-качество** | Ruff, Mypy (strict), pre-commit |

---

## 📁 Структура проекта

```
HabitFlowByMe/
├── app/
│   ├── api/                    # JSON API (для Swagger/мобильных приложений)
│   │   ├── deps.py            # Зависимости API (get_current_user)
│   │   ├── exception_handlers.py  # Глобальные обработчики исключений
│   │   └── router.py          # Агрегатор API-роутеров
│   │
│   ├── core/                   # Ядро приложения
│   │   ├── config.py          # Настройки (Pydantic Settings)
│   │   ├── exceptions.py      # Domain exceptions
│   │   ├── lifespan.py        # Startup/Shutdown логика
│   │   ├── logging.py         # Настройка логирования
│   │   ├── security.py        # JWT, хеширование паролей
│   │   └── types.py           # Кастомные типы (Password)
│   │
│   ├── db/                     # Работа с базой данных
│   │   ├── base.py            # DeclarativeBase, TimestampMixin
│   │   ├── deps.py            # get_db (управление транзакциями)
│   │   ├── models.py          # Регистрация моделей для Alembic
│   │   └── session.py         # AsyncEngine, AsyncSessionLocal
│   │
│   ├── modules/                # Бизнес-логика (модули)
│   │   ├── users/             # Модуль пользователей
│   │   │   ├── di.py          # Dependency Injection
│   │   │   ├── models.py      # User модель
│   │   │   ├── repositories.py  # UserRepository
│   │   │   ├── router.py      # API endpoints (/api/auth)
│   │   │   ├── schemas.py     # Pydantic схемы
│   │   │   └── services.py    # AuthService
│   │   │
│   │   └── habits/            # Модуль привычек
│   │       ├── di.py
│   │       ├── models.py      # Habit, HabitLog
│   │       ├── repositories.py  # HabitRepository
│   │       ├── router.py      # API endpoints (/api/habits)
│   │       ├── schemas.py
│   │       └── services.py    # HabitService (бизнес-логика)
│   │
│   └── web/                    # HTML Frontend (для браузера)
│       ├── auth.py            # Web-аутентификация
│       ├── dependencies.py    # get_web_user (cookie-based)
│       ├── habits.py          # Web-роуты для привычек
│       ├── router.py          # Агрегатор Web-роутеров
│       └── templates_config.py  # Jinja2 Templates
│
── templates/                  # HTML шаблоны
│   ├── base.html              # Базовый шаблон
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── habits/
│       ├── list.html          # Календарь текущего месяца
│       ├── list_sliding.html  # Скользящее окно 31 день
│       ├── form.html          # Создание/редактирование
│       ├── stats.html         # Детальная статистика
│       ├── _habit_card.html   # Partial для HTMX
│       └── _habit_card_sliding.html
│
├── static/
│   └── css/
│       └── app.css            # Стили приложения
│
├── tests/                      # Интеграционные тесты
│   ├── conftest.py            # Фикстуры, фабрики
│   ├── test_habits.py         # Тесты CRUD привычек
│   └── test_habit_logs.py     # Тесты логирования
│
├── alembic/                    # Миграции БД
│   └── versions/
│
├── docker/
│   ── entrypoint.sh          # Скрипт запуска (миграции + app)
│
├── .github/
│   ── workflows/
│       └── ci.yml             # CI/CD пайплайн
│
├── compose.yml                # Production Docker Compose
├── compose.dev.yml            # Development Docker Compose
├── Dockerfile                 # Multi-stage build
├── pyproject.toml             # Зависимости, настройки Ruff/Mypy/pytest
└── README.md
```

---

## 🚀 Быстрый старт

### Предварительные требования

- **Docker** и **Docker Compose** (v2+)
- **Git**

### Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/yourusername/HabitFlowByMe.git
   cd HabitFlowByMe
   ```

2. **Скопируйте файл окружения:**
   ```bash
   cp .env.example .env
   ```

3. **Отредактируйте `.env`:**
   ```env
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   DATABASE_NAME=habitflowbyme
   DATABASE_USER=habitflowbyme
   DATABASE_PASSWORD=your_secure_password
   SECRET_KEY=your_super_secret_key_change_in_production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   APP_NAME=HabitFlowByMe
   LOG_LEVEL=INFO
   ```

4. **Запустите приложение:**
   ```bash
   docker compose -f compose.yml -f compose.dev.yml up --build
   ```

5. **Откройте браузер:**
   ```
   http://localhost:8000
   ```

6. **Swagger API документация:**
   ```
   http://localhost:8000/docs
   ```

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Поднять тестовую БД
docker compose -f compose.yml -f compose.dev.yml up -d postgres-test

# Запустить тесты
uv run pytest tests/ -v

# Сгенерировать HTML-отчет
uv run pytest --html=report.html --self-contained-html

# Проверить покрытие кода
uv run pytest --cov=app --cov-report=html
```

### Что тестируется

- ✅ **CRUD операции** с привычками
- ✅ **Изоляция данных** (пользователь не видит чужие привычки)
- ✅ **Защита от IDOR** (404 вместо 403)
- ✅ **Race condition** при регистрации
- ✅ **Хеширование паролей** (Argon2)
- ✅ **JWT токены** (создание, валидация, истечение)
- ✅ **Каскадное удаление** (Habit → HabitLog)
- ✅ **Бизнес-логика** (стрики, статистика)

---

##  Архитектурные решения

### 1. Модульная архитектура (Vertical Slice)

Вместо классической слоистой структуры (`models/`, `services/`, `routers/`), проект организован по **доменным модулям**:

```
modules/
├── users/      # Всё, что касается пользователей
└── habits/     # Всё, что касается привычек
```

**Преимущества:**
- Легко найти весь код, связанный с сущностью
- Проще добавлять новые модули (например, `billing/`)
- Уменьшает связанность между доменами

### 2. Domain Exceptions

Исключения **не знают** про HTTP:

```python
#  Неправильно
class UserAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User exists")

# ✅ Правильно
class UserAlreadyExistsError(DomainException):
    pass

# Обработчик в app/api/exception_handlers.py
@app.exception_handler(UserAlreadyExistsError)
async def handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": "User exists"})
```

**Преимущества:**
- Сервисы можно переиспользовать в CLI, Celery, GraphQL
- Легко менять формат ответов (JSON → XML → HTML)

### 3. Transaction Management

Транзакции управляются **инфраструктурой**, а не бизнес-логикой:

```python
# app/db/deps.py
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()  # Автоматический коммит
        except Exception:
            await db.rollback()  # Автоматический откат
            raise
```

**Преимущества:**
- Сервисы не думают о транзакциях
- Нет дублирования `commit()`/`rollback()`
- Гарантированная целостность данных

### 4. Savepoints для Race Condition

```python
# app/modules/users/repositories.py
async def create(self, email, hashed_password):
    user = User(email=email, hashed_password=hashed_password)
    self.db.add(user)
    try:
        async with self.db.begin_nested():  # Savepoint
            await self.db.flush()
    except IntegrityError:
        await self.db.rollback()  # Откат только этой операции
        raise UserAlreadyExistsError()
    return user
```

**Преимущества:**
- Защита от гонки при одновременной регистрации
- Не откатывает другие успешные операции в транзакции

### 5. IDOR Prevention

```python
# app/modules/habits/services.py
async def _get_habit_or_raise(self, habit_id: int, user_id: int):
    habit = await self.repo.get_by_id_and_user(habit_id, user_id)
    if not habit:
        raise HabitNotFoundError()  # 404, не 403!
    return habit
```

**Почему 404 вместо 403?**
- 403 раскрывает существование ресурса ("привычка есть, но у тебя нет доступа")
- 404 скрывает факт существования ("привычки не существует")
- Защита от перебора ID (Insecure Direct Object Reference)

---

## 📊 База данных

### Модели

#### User
```python
class User(Base, TimestampMixin):
    id: Mapped[int]
    email: Mapped[str]  # unique
    hashed_password: Mapped[str]  # Argon2id
    habits: Mapped[list[Habit]]  # cascade delete
```

#### Habit
```python
class Habit(Base, TimestampMixin):
    id: Mapped[int]
    user_id: Mapped[int]  # FK → users.id (CASCADE)
    title: Mapped[str]
    description: Mapped[str | None]
    is_archived: Mapped[bool]
    logs: Mapped[list[HabitLog]]  # cascade delete
```

#### HabitLog
```python
class HabitLog(Base, TimestampMixin):
    id: Mapped[int]
    habit_id: Mapped[int]  # FK → habits.id (CASCADE)
    log_date: Mapped[date]  # unique constraint (habit_id, log_date)
```

### Миграции

Проект использует **Alembic** для управления схемой БД:

```bash
# Создать миграцию
docker compose run --rm app alembic revision --autogenerate -m "add new column"

# Применить миграции
docker compose run --rm app alembic upgrade head

# Откатить миграцию
docker compose run --rm app alembic downgrade -1
```

**Автоматическое применение:** При старте контейнера `entrypoint.sh` автоматически применяет миграции через `pg_advisory_lock` (защита от гонки при множественных контейнерах).

---

## 🔐 Безопасность

### Хеширование паролей

Используется **Argon2id** (победитель Password Hashing Competition):

```python
# app/core/security.py
from argon2 import PasswordHasher

ph = PasswordHasher()  # time_cost=3, memory_cost=65536, parallelism=4

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except (VerifyMismatchError, InvalidHash):
        return False  # Graceful degradation
```

### JWT токены

```python
# Payload
{
    "sub": "123",           # user_id
    "exp": 1721234567,      # expiration (int timestamp)
    "iat": 1721230967,      # issued at
    "type": "access"        # token type
}
```

### Cookie-based аутентификация (Web)

```python
# app/web/dependencies.py
async def get_web_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not access_token:
        raise HTTPException(303, headers={"Location": "/login"})
    # ... decode token, fetch user ...
```

**Преимущества:**
- Автоматический редирект на `/login` при истечении токена
- HttpOnly (недоступен для JavaScript)
- SameSite=Lax (защита от CSRF)

---

## 🌐 API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Регистрация нового пользователя |
| POST | `/api/auth/login` | Вход (возвращает JWT) |
| GET | `/api/auth/me` | Получить текущего пользователя |

### Habits (`/api/habits`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/habits` | Список привычек пользователя |
| POST | `/api/habits` | Создать привычку |
| PATCH | `/api/habits/{id}` | Обновить привычку |
| DELETE | `/api/habits/{id}` | Удалить привычку |
| POST | `/api/habits/{id}/log` | Отметить выполнение (сегодня) |
| POST | `/api/habits/{id}/toggle` | Переключить статус (сегодня) |
| POST | `/api/habits/{id}/toggle-date` | Переключить статус (конкретная дата) |
| GET | `/api/habits/{id}/stats` | Статистика привычки |

---

## 🎨 Frontend

### HTMX для интерактивности

Вместо JavaScript используется **HTMX** для мгновенного обновления UI:

```html
<button 
    hx-post="/habits/{{ habit.id }}/toggle-date-sliding"
    hx-target="#habit-card-{{ habit.id }}"
    hx-swap="outerHTML"
    hx-vals='{"date_str": "{{ day_item.date.isoformat() }}"}'>
</button>
```

**Преимущества:**
- Нет JavaScript кода
- Сервер возвращает HTML-фрагменты
- Мгновенное обновление без перезагрузки
- Graceful degradation (работает без JS)

### CSS Variables

```css
:root {
    --color-primary: #4f46e5;
    --color-success: #10b981;
    --color-danger: #ef4444;
    --color-bg: #f3f4f6;
    --color-card: #ffffff;
    --radius: 8px;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
```

**Преимущества:**
- Легко менять тему (dark mode)
- Консистентность дизайна
- Нет внешних зависимостей (Tailwind, Bootstrap)

---

## 🚢 Деплой

### Production Docker Compose

```yaml
# compose.yml
services:
  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}

  app:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_HOST: postgres
    ports:
      - "8000:8000"
```

### Environment Variables

```env
# Production
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=habitflowbyme
DATABASE_USER=habitflowbyme
DATABASE_PASSWORD=CHANGE_ME_IN_PRODUCTION
SECRET_KEY=CHANGE_ME_IN_PRODUCTION_USE_64_CHARS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_NAME=HabitFlowByMe
LOG_LEVEL=WARNING
```

### Миграции в Production

Миграции применяются **автоматически** при старте контейнера через `entrypoint.sh`:

```bash
#!/bin/sh
# docker/entrypoint.sh

# Ждем готовности БД
until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT"; do
    sleep 2
done

# Применяем миграции с блокировкой (защита от гонки)
export PGPASSWORD="$DATABASE_PASSWORD"
psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -d "$DATABASE_NAME" <<EOF
   SELECT pg_advisory_lock(987654321);
   \! alembic upgrade head
   SELECT pg_advisory_unlock(987654321);
EOF

# Запускаем приложение
exec "$@"
```

---

## 🧰 Разработка

### Локальная разработка с hot-reload

```bash
docker compose -f compose.yml -f compose.dev.yml up --build
```

Изменения в коде автоматически подхватываются благодаря `--reload` в `uvicorn`.

### Pre-commit хуки

```bash
# Установить хуки
uv run pre-commit install

# Запустить вручную
uv run pre-commit run --all-files
```

**Проверки:**
- Ruff (linting + formatting)
- Mypy (type checking)
- Trailing whitespace
- End of file

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/ci.yml
jobs:
  tests:
    steps:
      - Run Ruff (lint + format)
      - Run Mypy (strict mode)
      - Apply migrations
      - Run tests (with HTML report)
      - Check for missing migrations
  
  docker:
    steps:
      - Build Docker image (with cache)
```

---

## 📈 Производительность

### Асинхронность

Весь стек асинхронный:
- **FastAPI** (async/await)
- **SQLAlchemy 2.0** (async engine)
- **asyncpg** (async PostgreSQL driver)
- **HTMX** (async HTTP requests)

### Database Connection Pool

```python
# app/db/session.py
async_engine = create_async_engine(
    settings.database_url,
    pool_size=20,           # Максимум соединений
    max_overflow=10,        # Дополнительные соединения
    pool_pre_ping=True,     # Проверка жизнеспособности
    pool_recycle=3600,      # Пересоздание через час
)
```

### Query Optimization

- **Indexes** на `user_id`, `log_date`, `email`
- **Composite unique constraint** на `(habit_id, log_date)`
- **Lazy loading** для связей (relationship)
- **Eager loading** где нужно (selectinload)

---

## 🐛 Отладка

### Логи приложения

```bash
# Смотреть логи
docker compose logs -f app

# Только ошибки
docker compose logs -f app | grep ERROR
```

### Database debugging

```bash
# Подключиться к БД
docker exec -it habitflowbyme-postgres-1 psql -U habitflowbyme -d habitflowbyme

# Посмотреть таблицы
\dt

# Посмотреть структуру
\d habits

# Посмотреть данные
SELECT * FROM habits LIMIT 10;
```

### HTMX debugging

Откройте DevTools → Network → Filter: `HX-Request`

Вы увидите все AJAX-запросы от HTMX с заголовками:
- `HX-Request: true`
- `HX-Target: #habit-card-123`
- `HX-Trigger: click`

---

## 📚 Дополнительные ресурсы

### Документация

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [HTMX Documentation](https://htmx.org/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)

### Архитектурные паттерны

- [Domain-Driven Design](https://domainlanguage.com/ddd/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Vertical Slice Architecture](https://jimmybogard.com/vertical-slice-architecture/)

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

Используем [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — новая функциональность
- `fix:` — исправление бага
- `docs:` — документация
- `style:` — форматирование
- `refactor:` — рефакторинг
- `test:` — тесты
- `chore:` — инфраструктура

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** — за невероятный фреймворк
- **HTMX** — за возвращение простоты в веб-разработку
- **SQLAlchemy** — за мощный ORM
- **PostgreSQL** — за надежность и производительность

---

##  Contact

Your Name - [@yourusername](https://twitter.com/yourusername) - your.email@example.com

Project Link: [https://github.com/yourusername/HabitFlowByMe](https://github.com/yourusername/HabitFlowByMe)

---

**Made with ❤️ and Python**
