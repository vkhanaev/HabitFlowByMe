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

echo "Starting application..."

exec "$@"