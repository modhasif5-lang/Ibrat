# Ibrat — Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│                     Customer UI + Admin Dashboard               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     API Gateway (Nginx)                          │
│              Routing · CORS · Rate Limiting · Headers            │
└────┬──────────┬──────────┬──────────┬──────────┬────────────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────────┐
│  User   ││ Product ││ Search  ││  Cart   ││  Inventory  │
│ Service ││ Service ││ Service ││ Service ││   Service   │
│  :8001  ││  :8002  ││  :8003  ││  :8004  ││    :8005    │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘└──────┬──────┘
     │          │          │          │             │
     ▼          ▼          │          ▼             ▼
┌─────────┐┌─────────┐    │    ┌─────────┐  ┌───────────┐
│ user_db ││product_db│    │    │ cart_db  │  │inventory_db│
└─────────┘└─────────┘    │    └─────────┘  └───────────┘
                           │
                    ┌──────┴──────┐
                    │Elasticsearch│
                    └─────────────┘

     ╔═══════════════════════════════════╗
     ║    Kafka (Async Event Bus)        ║
     ║  product.events · inventory.events║
     ║  review.events · cart.events      ║
     ╚═══════════════════════════════════╝

     ┌─────────────────────────────────┐
     │      Redis (Cache / Locks)      │
     └─────────────────────────────────┘
```

## Data Ownership

| Data Domain | Owner Service | Storage |
|---|---|---|
| Users, Auth, Wishlist, Notifications | User Service | user_db (PostgreSQL) |
| Products, Categories, Collections, Reviews, Recommendations | Product Service | product_db (PostgreSQL) |
| Search Index | Search Service | Elasticsearch |
| Shopping Cart | Cart Service | cart_db (PostgreSQL) |
| Stock, Reservations, Inventory Movements | Inventory Service | inventory_db (PostgreSQL) |

## Communication Patterns

### Synchronous (REST)
- Frontend → API Gateway → Service
- Service → Service (e.g., Cart validates against Product/Inventory)

### Asynchronous (Kafka)
- Product Service → `product.events` → Search Service (index sync)
- Inventory Service → `inventory.events` → Search Service (availability updates)
- Review events, Cart events, Wishlist events for cross-service awareness

## Service Boundary Rules

1. No direct database access across services
2. PostgreSQL is the source of truth for business data
3. Redis is for caching and coordination only
4. Elasticsearch is eventually consistent
5. Recommendation engine lives within Product Service (not a separate microservice)
