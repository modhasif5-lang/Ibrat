#!/bin/sh
set -e

echo "[user-service] Starting service initialization..."

# Apply database migrations
if [ -f "alembic.ini" ]; then
    echo "[user-service] Applying Alembic database migrations..."
    alembic upgrade head || true
fi

# Apply seed data
if [ -f "app/seed.py" ]; then
    echo "[user-service] Seeding initial users and admin accounts..."
    python -m app.seed || true
fi

echo "[user-service] Initialization complete. Starting application server..."
exec "$@"
