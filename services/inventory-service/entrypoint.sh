#!/bin/sh
set -e

echo "[inventory-service] Starting service initialization..."

# Apply database migrations
if [ -f "alembic.ini" ]; then
    echo "[inventory-service] Applying Alembic database migrations..."
    alembic upgrade head || true
fi

# Apply seed data
if [ -f "app/seed.py" ]; then
    echo "[inventory-service] Seeding initial inventory balances and movements..."
    python -m app.seed || true
fi

echo "[inventory-service] Initialization complete. Starting application server..."
exec "$@"
