"""
Inventory Service — FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.database import check_db_connection
from app.core.kafka_producer import event_producer
from app.routes.inventory import router as inventory_router

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(settings.SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    db_ok = await check_db_connection()
    if db_ok:
        logger.info("Database connection established successfully.")
    else:
        logger.warning("Database connection could not be established at startup.")

    # Start Kafka Producer
    await event_producer.start()

    yield

    # Stop Kafka Producer
    await event_producer.stop()
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Ibrat Inventory Service",
    description="Stock tracking, availability, reservations, and inventory movements.",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register inventory routes
app.include_router(inventory_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    db_ok = await check_db_connection()
    checks = {
        "database": "connected" if db_ok else "unreachable",
        "kafka": "connected" if event_producer._connected else "offline",
        "redis": "pending_stage",
    }
    status = "ready" if db_ok else "degraded"
    return {
        "status": status,
        "service": settings.SERVICE_NAME,
        "checks": checks,
    }
