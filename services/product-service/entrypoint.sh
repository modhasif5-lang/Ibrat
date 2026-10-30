#!/bin/sh
set -e

echo "[product-service] Starting service initialization..."

# Apply database migrations
if [ -f "alembic.ini" ]; then
    echo "[product-service] Applying Alembic database migrations..."
    alembic upgrade head || true
fi

# Apply seed data
if [ -f "app/seed.py" ]; then
    echo "[product-service] Seeding initial footwear catalog, categories, collections, and variants..."
    python -m app.seed || true
fi

echo "[product-service] Initialization complete. Starting application server..."
exec "$@"
