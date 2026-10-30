"""
Customer Reviews and Ratings Routes.
Exposes review submissions, rating distribution, user review editing, and moderation.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin_claims, get_current_user_claims
from app.schemas.product import (
    ProductReviewSummaryResponse,
    ReviewApprovalUpdate,
    ReviewCreate,
    ReviewImageResponse,
    ReviewResponse,
    ReviewUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "/product/{product_id}",
    response_model=ProductReviewSummaryResponse,
    summary="Get customer reviews and star distribution for a product",
)
async def get_product_reviews(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all approved reviews, average rating score, and 1-5 star distribution."""
    svc = ProductService(db)
    return await svc.get_product_reviews(product_id)


@router.post(
    "/product/{product_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a product review with rating (1-5)",
)
async def submit_review(
    product_id: uuid.UUID,
    req: ReviewCreate,
    user: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db),
):
    """Submit a verified review with 1 to 5 star rating, comment, and optional images."""
    svc = ProductService(db)
    user_name = user.get("email", "Verified Customer").split("@")[0].capitalize()
    return await svc.create_review(
        product_id=product_id,
        user_id=user["user_id"],
        user_name=user_name,
        req=req,
    )


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Edit own review",
)
async def update_review(
    review_id: uuid.UUID,
    req: ReviewUpdate,
    user: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db),
):
    """Update review text or rating (author only)."""
    svc = ProductService(db)
    return await svc.update_review(
        review_id=review_id,
        user_id=user["user_id"],
        req=req,
    )


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a review",
)
async def delete_review(
    review_id: uuid.UUID,
    user: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db),
):
    """Delete a review (allowed for the review author or administrator)."""
    svc = ProductService(db)
    is_admin = user.get("role") == "ADMIN"
    await svc.delete_review(
        review_id=review_id,
        user_id=user["user_id"],
        is_admin=is_admin,
    )
    return {"success": True, "message": "Review deleted successfully."}


@router.post(
    "/{review_id}/images",
    response_model=ReviewImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and attach photo to a review",
)
async def upload_review_photo(
    review_id: uuid.UUID,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db),
):
    """Upload a JPEG/PNG/WEBP photo for a customer review."""
    svc = ProductService(db)
    is_admin = user.get("role") == "ADMIN"
    return await svc.upload_review_image(
        review_id=review_id,
        user_id=user["user_id"],
        file=file,
        is_admin=is_admin,
    )


@router.get(
    "/admin/list",
    summary="Admin: Review moderation list",
)
async def admin_list_reviews(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_approved: Optional[bool] = Query(None),
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Review moderation feed."""
    svc = ProductService(db)
    reviews, total = await svc.repo.list_reviews_admin(page=page, size=size, is_approved=is_approved)
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": [ReviewResponse.model_validate(r) for r in reviews],
    }


@router.patch(
    "/admin/{review_id}/moderate",
    response_model=ReviewResponse,
    summary="Admin: Approve or reject a review",
)
async def admin_moderate_review(
    review_id: uuid.UUID,
    req: ReviewApprovalUpdate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Toggle review approval status and update rating aggregation."""
    svc = ProductService(db)
    return await svc.moderate_review(review_id=review_id, is_approved=req.is_approved)


@router.delete(
    "/admin/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Admin: Moderation deletion of a review",
)
async def admin_delete_review(
    review_id: uuid.UUID,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Delete spam or offensive review and recalculate footwear rating."""
    svc = ProductService(db)
    await svc.delete_review(
        review_id=review_id,
        user_id=admin["user_id"],
        is_admin=True,
    )
    return {"success": True, "message": "Review removed by administrator."}
