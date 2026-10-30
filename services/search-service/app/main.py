"""
Search Service — FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.elasticsearch import check_es_connection, es_client, init_search_index
from app.core.kafka_consumer import search_consumer
from app.routes.search import router as search_router

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(settings.SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize ES index and background Kafka event listener."""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    # 1. Verify Elasticsearch
    es_ok = await check_es_connection()
    if es_ok:
        logger.info("Connected to Elasticsearch successfully.")
        await init_search_index()
    else:
        logger.warning("Elasticsearch is not reachable at startup.")

    # 2. Start Kafka Consumer in background
    await search_consumer.start()

    yield

    # Shutdown
    await search_consumer.stop()
    await es_client.close()
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Ibrat Search Service",
    description="Full-text search, filtering, sorting, and autocomplete for products.",
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

# Register search router
app.include_router(search_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    es_ok = await check_es_connection()
    checks = {
        "elasticsearch": "connected" if es_ok else "unreachable",
        "kafka": "pending_stage",
    }
    status = "ready" if es_ok else "degraded"
    return {
        "status": status,
        "service": settings.SERVICE_NAME,
        "checks": checks,
    }
