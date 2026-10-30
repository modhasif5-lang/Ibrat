"""
Category Routes for Product Service.
Exposes public category listing and administrative category CRUD.
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin_claims
from app.schemas.product import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=List[CategoryResponse],
    summary="List active footwear categories",
)
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve list of all active categories (Heels, Flats, Mules, Boots)."""
    svc = ProductService(db)
    return await svc.list_categories(active_only=True)


@router.get(
    "/{slug}",
    response_model=CategoryResponse,
    summary="Get category details by slug",
)
async def get_category(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve single category by its slug."""
    svc = ProductService(db)
    return await svc.get_category_by_slug(slug)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Create category",
)
async def create_category(
    req: CategoryCreate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Create a new footwear category with automatic slug generation."""
    svc = ProductService(db)
    return await svc.create_category(req)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Admin: Update category",
)
async def update_category(
    category_id: uuid.UUID,
    req: CategoryUpdate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Update category metadata, display ordering, or status."""
    svc = ProductService(db)
    return await svc.update_category(category_id, req)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    summary="Admin: Delete category",
)
async def delete_category(
    category_id: uuid.UUID,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category."""
    svc = ProductService(db)
    await svc.delete_category(category_id)
    return {"success": True, "message": "Category deleted successfully."}
