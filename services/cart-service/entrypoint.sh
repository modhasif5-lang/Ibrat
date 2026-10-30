#!/bin/sh
set -e

echo "[cart-service] Starting service initialization..."

# Apply database migrations
if [ -f "alembic.ini" ]; then
    echo "[cart-service] Applying Alembic database migrations..."
    alembic upgrade head || true
fi

# Apply seed data
if [ -f "app/seed.py" ]; then
    echo "[cart-service] Seeding initial cart tables..."
    python -m app.seed || true
fi

echo "[cart-service] Initialization complete. Starting application server..."
exec "$@"
