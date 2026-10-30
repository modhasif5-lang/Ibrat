#!/bin/sh
set -e

echo "[search-service] Starting service initialization..."

# Apply seed data to Elasticsearch
if [ -f "app/seed.py" ]; then
    echo "[search-service] Initializing Elasticsearch indices and documents..."
    python -m app.seed || true
fi

echo "[search-service] Initialization complete. Starting application server..."
exec "$@"
