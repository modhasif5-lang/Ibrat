"""
Product Service — FastAPI Application Entry Point
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.core.database import check_db_connection
from app.core.kafka_producer import event_producer
from app.core.redis import cache_service
from app.routes.products import router as products_router
from app.routes.categories import router as categories_router
from app.routes.collections import router as collections_router
from app.routes.reviews import router as reviews_router
from app.routes.recommendations import router as recommendations_router

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

    # Connect to Redis
    await cache_service.connect()

    yield

    # Disconnect Redis & Kafka
    await cache_service.disconnect()
    await event_producer.stop()
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Ibrat Product Service",
    description="Product catalog, categories, collections, reviews, and footwear recommendation engine.",
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

# Static files for product images
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(collections_router)
app.include_router(reviews_router)
app.include_router(recommendations_router)


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
    redis_ok = await cache_service.is_healthy()
    checks = {
        "database": "connected" if db_ok else "unreachable",
        "kafka": "connected" if event_producer._connected else "offline",
        "redis": "connected" if redis_ok else "offline",
    }
    status = "ready" if db_ok else "degraded"
    return {
        "status": status,
        "service": settings.SERVICE_NAME,
        "checks": checks,
    }
