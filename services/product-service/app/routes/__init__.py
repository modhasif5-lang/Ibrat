"""
Product Service Routes Package.
"""

from app.routes.products import router as products_router
from app.routes.categories import router as categories_router
from app.routes.collections import router as collections_router
from app.routes.reviews import router as reviews_router
from app.routes.recommendations import router as recommendations_router

__all__ = [
    "products_router",
    "categories_router",
    "collections_router",
    "reviews_router",
    "recommendations_router",
]
