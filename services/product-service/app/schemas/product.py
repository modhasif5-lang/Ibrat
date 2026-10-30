"""
Pydantic validation schemas for Product Service.
Covers Categories, Collections, Footwear Products, Variants, Customizations, Images, and Reviews.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================
# Category Schemas
# ============================================================

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    display_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    created_at: datetime
    updated_at: datetime


class CategoryTreeResponse(CategoryResponse):
    """Hierarchical category with subcategories."""
    subcategories: List[CategoryResponse] = []


# ============================================================
# Collection Schemas
# ============================================================

class CollectionBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    banner_image_url: Optional[str] = None
    is_active: bool = True


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    banner_image_url: Optional[str] = None
    is_active: Optional[bool] = None


class CollectionResponse(CollectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    created_at: datetime
    updated_at: datetime


# ============================================================
# Footwear Customization Schemas (Heel Sizes: 1", 2", 3")
# ============================================================

class CustomizationOptionBase(BaseModel):
    type: str = Field("HEEL_SIZE", max_length=50)
    value: str = Field(..., max_length=50)  # "1 inch", "2 inch", "3 inch"
    additional_price: Decimal = Decimal("0.00")
    is_available: bool = True

    @field_validator("value")
    @classmethod
    def validate_heel_size(cls, v: str) -> str:
        allowed = ["1 inch", "2 inch", "3 inch"]
        if v.lower() not in [a.lower() for a in allowed]:
            raise ValueError(f"Customization value must be one of: {', '.join(allowed)}")
        return v


class CustomizationOptionCreate(CustomizationOptionBase):
    pass


class CustomizationOptionUpdate(BaseModel):
    value: Optional[str] = None
    additional_price: Optional[Decimal] = None
    is_available: Optional[bool] = None

    @field_validator("value")
    @classmethod
    def validate_heel_size(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["1 inch", "2 inch", "3 inch"]
            if v.lower() not in [a.lower() for a in allowed]:
                raise ValueError(f"Customization value must be one of: {', '.join(allowed)}")
        return v


class CustomizationOptionResponse(CustomizationOptionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime


# ============================================================
# Product Variant Schemas (Size + Color + SKU)
# ============================================================

class ProductVariantBase(BaseModel):
    sku: str = Field(..., max_length=100)
    size: str = Field(..., max_length=20)  # "36", "37", "38", "39", "40", "41"
    color_name: str = Field(..., max_length=50)  # "Champagne Gold"
    color_hex: Optional[str] = Field(None, max_length=20)  # "#F7E7CE"
    price_override: Optional[Decimal] = None
    is_active: bool = True


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(BaseModel):
    sku: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=20)
    color_name: Optional[str] = Field(None, max_length=50)
    color_hex: Optional[str] = Field(None, max_length=20)
    price_override: Optional[Decimal] = None
    is_active: Optional[bool] = None


class ProductVariantResponse(ProductVariantBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ============================================================
# Product Image Schemas
# ============================================================

class ProductImageBase(BaseModel):
    url: str = Field(..., max_length=500)
    alt_text: Optional[str] = Field(None, max_length=255)
    display_order: int = 0
    is_primary: bool = False
    variant_id: Optional[uuid.UUID] = None


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageResponse(ProductImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime


# ============================================================
# Review Schemas
# ============================================================

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, max_length=255)
    comment: str = Field(..., min_length=5, description="Review text")
    image_urls: List[str] = []


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = Field(None, min_length=5)


class ReviewApprovalUpdate(BaseModel):
    is_approved: bool



class ReviewImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    url: str
    created_at: datetime


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    rating: int
    title: Optional[str] = None
    comment: str
    is_verified_purchase: bool
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    images: List[ReviewImageResponse] = []


class RatingDistribution(BaseModel):
    five_star: int = 0
    four_star: int = 0
    three_star: int = 0
    two_star: int = 0
    one_star: int = 0


class ProductReviewSummaryResponse(BaseModel):
    product_id: uuid.UUID
    average_rating: float
    total_reviews: int
    distribution: RatingDistribution
    reviews: List[ReviewResponse]


# ============================================================
# Footwear Product Schemas
# ============================================================

class ProductBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    category_id: uuid.UUID
    collection_id: Optional[uuid.UUID] = None
    base_price: Decimal = Field(..., ge=0)
    discount_price: Optional[Decimal] = Field(None, ge=0)
    material: Optional[str] = Field(None, max_length=100)
    sole_material: Optional[str] = Field(None, max_length=100)
    care_instructions: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False
    is_new_arrival: bool = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    collection_id: Optional[uuid.UUID] = None
    base_price: Optional[Decimal] = Field(None, ge=0)
    discount_price: Optional[Decimal] = Field(None, ge=0)
    material: Optional[str] = Field(None, max_length=100)
    sole_material: Optional[str] = Field(None, max_length=100)
    care_instructions: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_new_arrival: Optional[bool] = None


class ProductCardResponse(BaseModel):
    """Concise representation for footwear catalog listings and search."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    base_price: Decimal
    discount_price: Optional[Decimal] = None
    material: Optional[str] = None
    average_rating: float
    review_count: int
    is_featured: bool
    is_new_arrival: bool
    primary_image_url: Optional[str] = None
    category_name: Optional[str] = None
    collection_name: Optional[str] = None


class ProductDetailResponse(ProductBase):
    """Full footwear product view with all relations."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    average_rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime

    category: Optional[CategoryResponse] = None
    collection: Optional[CollectionResponse] = None
    variants: List[ProductVariantResponse] = []
    customizations: List[CustomizationOptionResponse] = []
    images: List[ProductImageResponse] = []


class ProductListPaginatedResponse(BaseModel):
    """Paginated collection of footwear product cards."""
    total: int
    page: int
    size: int
    items: List[ProductCardResponse]
