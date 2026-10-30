# Ibrat — Premium Ladies Footwear E-Commerce Platform

> A production-style, microservice-based e-commerce platform for premium ladies footwear.

---

## Architecture Overview

Ibrat is built on a **5-microservice architecture**:

| Service | Port | Database | Purpose |
|---------|------|----------|---------|
| User Service | 8001 | user_db (PostgreSQL) | Auth, profiles, wishlist, notifications |
| Product Service | 8002 | product_db (PostgreSQL) | Catalog, categories, collections, reviews |
| Search Service | 8003 | Elasticsearch | Full-text search, filtering, autocomplete |
| Cart Service | 8004 | cart_db (PostgreSQL) | Shopping cart management |
| Inventory Service | 8005 | inventory_db (PostgreSQL) | Stock tracking, reservations |

### Infrastructure

| Component | Port | Purpose |
|-----------|------|---------|
| Frontend (Next.js) | 3000 | Customer & admin UI |
| API Gateway (Nginx) | 80 | Reverse proxy, routing |
| PostgreSQL | 5432 | Primary data store |
| Redis | 6379 | Caching, rate limiting |
| Elasticsearch | 9200 | Search engine |
| Kafka | 9092 | Event streaming |
| Zookeeper | 2181 | Kafka coordination |

### Communication Patterns

```
Frontend → API Gateway → Microservices (REST / synchronous)
Microservices → Kafka → Microservices (Events / asynchronous)
```

---

## Prerequisites

- Docker & Docker Compose v2+
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

---

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url>
cd ibrat
cp .env.example .env
```

### 2. Start all services

```bash
docker compose up --build
```

> **Automated Initialization:** Each microservice includes an automated `entrypoint.sh` script that automatically runs Alembic database migrations (`alembic upgrade head`) and seeds initial data (`python -m app.seed`), provisioning the administrator account, demo luxury footwear catalog, variants, and stock ledgers out of the box.

Or use the Makefile:

```bash
make up
```

### 3. Access the application

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Customer frontend (Next.js 16) |
| http://localhost:3000/admin | Atelier Admin Console |
| http://localhost/api | API Gateway (Nginx :80) |
| http://localhost:8001/docs | User Service Swagger UI |
| http://localhost:8002/docs | Product Service Swagger UI |
| http://localhost:8003/docs | Search Service Swagger UI |
| http://localhost:8004/docs | Cart Service Swagger UI |
| http://localhost:8005/docs | Inventory Service Swagger UI |

### 4. Default Admin Login

```
Email: admin@ibrat.com
Password: Admin@12345
```

---

## Footwear Specifications & Architectural Scope

1. **Heel Customization:** Heel elevation options are strictly restricted to `1 inch`, `2 inch`, and `3 inch`.
2. **Purchasing Boundary:** The platform concludes at the luxury shopping cart. Payment gateways and order processing are intentionally out of scope to preserve clean microservice boundaries.
3. **Database Isolation:** PostgreSQL operates with 4 isolated service databases (`user_db`, `product_db`, `cart_db`, `inventory_db`). Direct cross-service database access is strictly prohibited; all inter-service communications occur via REST or Kafka event pub/sub.

---

## Running Tests

### Unified Comprehensive Test Runner (92 Tests)

Run the unified test runner executing unit, schema, API, E2E journey, and frontend contract tests across all 5 microservices and Next.js:

```bash
python scripts/run_all_tests.py
```

### Individual Service Tests via Makefile

```bash
# All backend tests inside Docker
make test

# Individual service tests inside Docker
make test-user
make test-product
make test-search
make test-cart
make test-inventory
```

---

## Project Structure

```
ibrat/
├── frontend/                 # Next.js frontend
│   ├── app/                  # App Router pages
│   ├── components/           # Reusable UI components
│   ├── lib/                  # Utilities and helpers
│   ├── hooks/                # Custom React hooks
│   ├── services/             # API client services
│   └── types/                # TypeScript type definitions
│
├── services/
│   ├── user-service/         # Authentication, profiles, wishlist
│   ├── product-service/      # Catalog, reviews, recommendations
│   ├── search-service/       # Elasticsearch search
│   ├── cart-service/         # Shopping cart
│   └── inventory-service/    # Stock management
│
├── infrastructure/
│   ├── nginx/                # API Gateway config
│   ├── kafka/                # Kafka configuration
│   ├── elasticsearch/        # ES configuration
│   └── postgres/             # Database init scripts
│
├── shared/
│   ├── events/               # Event schema definitions
│   └── docs/                 # Architecture documentation
│
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md
```

---

## Troubleshooting

### Services fail to start
- Ensure Docker has enough memory (at least 4GB recommended)
- Check that ports 3000, 5432, 6379, 9200, 9092 are not in use
- Run `docker compose down -v` to clean up volumes and retry

### Database connection errors
- Wait for PostgreSQL health check to pass before running migrations
- Check `POSTGRES_PASSWORD` matches in `.env`

### Elasticsearch fails
- Ensure `vm.max_map_count=262144` on Linux hosts
- On Windows/Mac, Docker Desktop handles this automatically

### Kafka connection issues
- Wait for Zookeeper to be healthy before Kafka starts
- Check `KAFKA_BOOTSTRAP_SERVERS` configuration

---

## License

This project is for educational and portfolio purposes.
