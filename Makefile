.PHONY: up down build restart logs migrate seed test clean

# === Docker Compose ===
up:
	docker compose up -d --build

down:
	docker compose down

down-v:
	docker compose down -v

build:
	docker compose build

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-%:
	docker compose logs -f $*

# === Database ===
migrate:
	docker compose exec user-service alembic upgrade head
	docker compose exec product-service alembic upgrade head
	docker compose exec cart-service alembic upgrade head
	docker compose exec inventory-service alembic upgrade head

migrate-user:
	docker compose exec user-service alembic upgrade head

migrate-product:
	docker compose exec product-service alembic upgrade head

migrate-cart:
	docker compose exec cart-service alembic upgrade head

migrate-inventory:
	docker compose exec inventory-service alembic upgrade head

seed:
	docker compose exec user-service python -m app.seed
	docker compose exec product-service python -m app.seed
	docker compose exec inventory-service python -m app.seed

# === Testing ===
test:
	docker compose exec user-service pytest -v
	docker compose exec product-service pytest -v
	docker compose exec search-service pytest -v
	docker compose exec cart-service pytest -v
	docker compose exec inventory-service pytest -v

test-user:
	docker compose exec user-service pytest -v

test-product:
	docker compose exec product-service pytest -v

test-search:
	docker compose exec search-service pytest -v

test-cart:
	docker compose exec cart-service pytest -v

test-inventory:
	docker compose exec inventory-service pytest -v

# === Utilities ===
clean:
	docker compose down -v --remove-orphans
	docker system prune -f

health:
	@echo "=== User Service ==="
	@curl -s http://localhost:8001/health | python -m json.tool || echo "DOWN"
	@echo "\n=== Product Service ==="
	@curl -s http://localhost:8002/health | python -m json.tool || echo "DOWN"
	@echo "\n=== Search Service ==="
	@curl -s http://localhost:8003/health | python -m json.tool || echo "DOWN"
	@echo "\n=== Cart Service ==="
	@curl -s http://localhost:8004/health | python -m json.tool || echo "DOWN"
	@echo "\n=== Inventory Service ==="
	@curl -s http://localhost:8005/health | python -m json.tool || echo "DOWN"

shell-%:
	docker compose exec $* /bin/bash
