"""
User Service — FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.database import check_db_connection
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(settings.SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    db_ok = await check_db_connection()
    if db_ok:
        logger.info("Database connection established successfully.")
    else:
        logger.warning("Database connection could not be established at startup.")
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Ibrat User Service",
    description="Authentication, user profiles, wishlist, and notifications for Ibrat footwear platform.",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(users_router)


# ============================================================
# Health Endpoints
# ============================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check (liveness)."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check — verifies service dependencies are available.
    """
    db_ok = await check_db_connection()
    checks = {
        "database": "connected" if db_ok else "unreachable",
        "redis": "pending_stage",
        "kafka": "pending_stage",
    }
    status = "ready" if db_ok else "degraded"
    return {
        "status": status,
        "service": settings.SERVICE_NAME,
        "checks": checks,
    }
