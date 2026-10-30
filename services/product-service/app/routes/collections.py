"""
Collection Routes for Product Service.
Exposes public editorial collections and administrative collection CRUD.
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin_claims
from app.schemas.product import (
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.get(
    "",
    response_model=List[CollectionResponse],
    summary="List active editorial collections",
)
async def list_collections(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve curated editorial collections (e.g. Bridal Edit, Monochrome Luxe)."""
    svc = ProductService(db)
    return await svc.list_collections(active_only=True)


@router.get(
    "/{slug}",
    response_model=CollectionResponse,
    summary="Get collection details by slug",
)
async def get_collection(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve collection details by its slug."""
    svc = ProductService(db)
    return await svc.get_collection_by_slug(slug)


@router.post(
    "",
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Create collection",
)
async def create_collection(
    req: CollectionCreate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Create a new footwear collection."""
    svc = ProductService(db)
    return await svc.create_collection(req)


@router.put(
    "/{collection_id}",
    response_model=CollectionResponse,
    summary="Admin: Update collection",
)
async def update_collection(
    collection_id: uuid.UUID,
    req: CollectionUpdate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Update collection banner, description, or status."""
    svc = ProductService(db)
    return await svc.update_collection(collection_id, req)


@router.delete(
    "/{collection_id}",
    status_code=status.HTTP_200_OK,
    summary="Admin: Delete collection",
)
async def delete_collection(
    collection_id: uuid.UUID,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Delete an editorial collection."""
    svc = ProductService(db)
    await svc.delete_collection(collection_id)
    return {"success": True, "message": "Collection deleted successfully."}
