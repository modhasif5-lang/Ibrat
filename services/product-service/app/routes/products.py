"""
Footwear Product Catalog Routes.
Exposes public browsing and administrative product management.
"""

import uuid
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin_claims
from app.schemas.product import (
    CustomizationOptionCreate,
    CustomizationOptionResponse,
    CustomizationOptionUpdate,
    ProductCreate,
    ProductDetailResponse,
    ProductImageResponse,
    ProductListPaginatedResponse,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


# ============================================================
# Public Catalog Routes
# ============================================================

@router.get(
    "",
    response_model=ProductListPaginatedResponse,
    summary="List and filter footwear products",
)
async def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category_id: Optional[uuid.UUID] = Query(None),
    collection_id: Optional[uuid.UUID] = Query(None),
    min_price: Optional[Decimal] = Query(None, ge=0),
    max_price: Optional[Decimal] = Query(None, ge=0),
    is_featured: Optional[bool] = Query(None),
    is_new_arrival: Optional[bool] = Query(None),
    sort_by: str = Query("newest", pattern="^(newest|price_asc|price_desc|rating)$"),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve catalog listing with filtering by collection, category, price, or editorial tag."""
    svc = ProductService(db)
    return await svc.list_products(
        page=page,
        size=size,
        category_id=category_id,
        collection_id=collection_id,
        min_price=min_price,
        max_price=max_price,
        is_featured=is_featured,
        is_new_arrival=is_new_arrival,
        sort_by=sort_by,
        active_only=True,
        search=search,
    )


@router.get(
    "/{slug_or_id}",
    response_model=ProductDetailResponse,
    summary="Get full product details by slug or UUID",
)
async def get_product(
    slug_or_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full product detail with variants, heel customizations, images, and reviews."""
    svc = ProductService(db)
    return await svc.get_product_detail(slug_or_id)


# ============================================================
# Admin Product Management Routes
# ============================================================

@router.post(
    "",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Create a new footwear product",
)
async def create_product(
    req: ProductCreate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Create a new footwear product. Automatically provisions 1, 2, and 3-inch heel customization options."""
    svc = ProductService(db)
    return await svc.create_product(req)


@router.put(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Admin: Update a footwear product",
)
async def update_product(
    product_id: uuid.UUID,
    req: ProductUpdate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Update details, materials, pricing, or status of a product."""
    svc = ProductService(db)
    return await svc.update_product(product_id, req)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Admin: Delete a product",
)
async def delete_product(
    product_id: uuid.UUID,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Delete a footwear product and all associated variants/images."""
    svc = ProductService(db)
    await svc.delete_product(product_id)
    return {"success": True, "message": "Product deleted successfully."}


# ============================================================
# Admin Variant Management
# ============================================================

@router.post(
    "/{product_id}/variants",
    response_model=ProductVariantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Add a size/color variant SKU to a product",
)
async def add_variant(
    product_id: uuid.UUID,
    req: ProductVariantCreate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Add a new size and color variant with unique SKU."""
    svc = ProductService(db)
    return await svc.add_variant(product_id, req)


@router.put(
    "/variants/{variant_id}",
    response_model=ProductVariantResponse,
    summary="Admin: Update variant SKU details",
)
async def update_variant(
    variant_id: uuid.UUID,
    req: ProductVariantUpdate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Update variant SKU, price override, or availability."""
    svc = ProductService(db)
    return await svc.update_variant(variant_id, req)


@router.delete(
    "/variants/{variant_id}",
    status_code=status.HTTP_200_OK,
    summary="Admin: Delete a variant SKU",
)
async def delete_variant(
    variant_id: uuid.UUID,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Delete a product variant SKU."""
    svc = ProductService(db)
    await svc.delete_variant(variant_id)
    return {"success": True, "message": "Variant deleted successfully."}


# ============================================================
# Admin Customization Management
# ============================================================

@router.post(
    "/{product_id}/customizations",
    response_model=CustomizationOptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Add footwear heel customization option",
)
async def add_customization(
    product_id: uuid.UUID,
    req: CustomizationOptionCreate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Add a customization option (restricted to 1 inch, 2 inch, or 3 inch heel)."""
    svc = ProductService(db)
    return await svc.add_customization(product_id, req)


@router.put(
    "/customizations/{customization_id}",
    response_model=CustomizationOptionResponse,
    summary="Admin: Update heel customization option",
)
async def update_customization(
    customization_id: uuid.UUID,
    req: CustomizationOptionUpdate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Update customization availability or differential price."""
    svc = ProductService(db)
    return await svc.update_customization(customization_id, req)


@router.delete(
    "/customizations/{customization_id}",
    status_code=status.HTTP_200_OK,
    summary="Admin: Delete heel customization option",
)
async def delete_customization(
    customization_id: uuid.UUID,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Delete a heel customization option."""
    svc = ProductService(db)
    await svc.delete_customization(customization_id)
    return {"success": True, "message": "Customization deleted successfully."}


# ============================================================
# Image Uploads & Management
# ============================================================

@router.post(
    "/{product_id}/images",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Upload image for product gallery",
)
async def upload_product_image(
    product_id: uuid.UUID,
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    display_order: int = Form(0),
    is_primary: bool = Form(False),
    variant_id: Optional[uuid.UUID] = Form(None),
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Upload product image file (JPEG, PNG, WebP up to 5MB) and attach to gallery."""
    svc = ProductService(db)
    return await svc.upload_product_image(
        product_id=product_id,
        file=file,
        alt_text=alt_text,
        display_order=display_order,
        is_primary=is_primary,
        variant_id=variant_id,
    )


@router.patch(
    "/{product_id}/images/{image_id}/primary",
    response_model=ProductImageResponse,
    summary="Admin: Designate primary image for footwear product card",
)
async def set_primary_image(
    product_id: uuid.UUID,
    image_id: uuid.UUID,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Set the primary display image for the footwear catalog card."""
    svc = ProductService(db)
    return await svc.set_primary_image(product_id, image_id)


@router.delete(
    "/images/{image_id}",
    status_code=status.HTTP_200_OK,
    summary="Admin: Delete product image",
)
async def delete_product_image(
    image_id: uuid.UUID,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Delete an image from disk and product gallery."""
    svc = ProductService(db)
    await svc.delete_product_image(image_id)
    return {"success": True, "message": "Image deleted successfully."}
