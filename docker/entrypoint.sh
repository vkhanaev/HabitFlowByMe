#!/bin/sh
set -e

# Проверка обязательных переменных
for var in DATABASE_HOST DATABASE_PORT DATABASE_USER; do
    if [ -z "$(eval echo \$$var)" ]; then
        echo "ERROR: $var is not set. Cannot wait for database."
        exit 1
    fi
done

MAX_RETRIES=30
RETRY_INTERVAL=2
RETRIES=0

echo "Waiting for database at ${DATABASE_HOST}:${DATABASE_PORT}..."

until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -q
do
    RETRIES=$((RETRIES + 1))
    if [ "$RETRIES" -ge "$MAX_RETRIES" ]; then
        echo "ERROR: Database not available after $((MAX_RETRIES * RETRY_INTERVAL))s. Exiting."
        exit 1
    fi
    echo "Database not ready, retrying in ${RETRY_INTERVAL}s... ($RETRIES/$MAX_RETRIES)"
    sleep "$RETRY_INTERVAL"
done

echo "Database is ready."

echo "Acquiring exclusive lock for migrations..."

# Экспортируем пароль, чтобы psql мог аутентифицироваться
export PGPASSWORD="$DATABASE_PASSWORD"

# Держим сессию psql открытой через heredoc
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -v ON_ERROR_STOP=1 <<EOF
   SELECT pg_advisory_lock(987654321);
   \! alembic upgrade head
   SELECT pg_advisory_unlock(987654321);
EOF

echo "Migrations completed."

echo "Starting application..."
exec "$@"