"""
Product Service Business Logic Layer.
Handles Footwear Catalog, Categories, Collections, Variants, Heel Customizations,
Image Storage, and Review Management.
"""

import re
import uuid
from decimal import Decimal
from typing import List, Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import storage_service
from app.models.product import Category, Collection, Product, Review
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    CategoryCreate,
    CategoryResponse,
    CategoryTreeResponse,
    CategoryUpdate,
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate,
    CustomizationOptionCreate,
    CustomizationOptionResponse,
    CustomizationOptionUpdate,
    ProductCardResponse,
    ProductCreate,
    ProductDetailResponse,
    ProductImageResponse,
    ProductListPaginatedResponse,
    ProductReviewSummaryResponse,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
    RatingDistribution,
    ReviewCreate,
    ReviewImageResponse,
    ReviewResponse,
    ReviewUpdate,
)
from app.core.kafka_producer import event_producer
from app.schemas.events import DomainEvent



def generate_slug(text: str) -> str:
    """Generate a clean URL slug from a name string."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


class ProductService:
    """Core domain service for footwear catalog and reviews."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)

    # ============================================================
    # Categories
    # ============================================================

    async def list_categories(self, active_only: bool = True) -> List[CategoryResponse]:
        categories = await self.repo.list_categories(active_only=active_only)
        return [CategoryResponse.model_validate(c) for c in categories]

    async def get_category_by_slug(self, slug: str) -> CategoryResponse:
        cat = await self.repo.get_category_by_slug(slug)
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
        return CategoryResponse.model_validate(cat)

    async def create_category(self, req: CategoryCreate) -> CategoryResponse:
        slug = generate_slug(req.name)
        existing = await self.repo.get_category_by_slug(slug)
        if existing:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        cat = await self.repo.create_category(
            slug=slug,
            name=req.name,
            description=req.description,
            image_url=req.image_url,
            parent_id=req.parent_id,
            display_order=req.display_order,
            is_active=req.is_active,
        )
        return CategoryResponse.model_validate(cat)

    async def update_category(self, category_id: uuid.UUID, req: CategoryUpdate) -> CategoryResponse:
        cat = await self.repo.get_category_by_id(category_id)
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

        kwargs = req.model_dump(exclude_unset=True)
        if "name" in kwargs and kwargs["name"]:
            kwargs["slug"] = generate_slug(kwargs["name"])

        updated = await self.repo.update_category(cat, **kwargs)
        return CategoryResponse.model_validate(updated)

    async def delete_category(self, category_id: uuid.UUID) -> bool:
        deleted = await self.repo.delete_category(category_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
        return True

    # ============================================================
    # Collections
    # ============================================================

    async def list_collections(self, active_only: bool = True) -> List[CollectionResponse]:
        collections = await self.repo.list_collections(active_only=active_only)
        return [CollectionResponse.model_validate(c) for c in collections]

    async def get_collection_by_slug(self, slug: str) -> CollectionResponse:
        coll = await self.repo.get_collection_by_slug(slug)
        if not coll:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found.")
        return CollectionResponse.model_validate(coll)

    async def create_collection(self, req: CollectionCreate) -> CollectionResponse:
        slug = generate_slug(req.name)
        existing = await self.repo.get_collection_by_slug(slug)
        if existing:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        coll = await self.repo.create_collection(
            slug=slug,
            name=req.name,
            description=req.description,
            banner_image_url=req.banner_image_url,
            is_active=req.is_active,
        )
        return CollectionResponse.model_validate(coll)

    async def update_collection(self, collection_id: uuid.UUID, req: CollectionUpdate) -> CollectionResponse:
        coll = await self.repo.get_collection_by_id(collection_id)
        if not coll:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found.")

        kwargs = req.model_dump(exclude_unset=True)
        if "name" in kwargs and kwargs["name"]:
            kwargs["slug"] = generate_slug(kwargs["name"])

        updated = await self.repo.update_collection(coll, **kwargs)
        return CollectionResponse.model_validate(updated)

    async def delete_collection(self, collection_id: uuid.UUID) -> bool:
        deleted = await self.repo.delete_collection(collection_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found.")
        return True

    # ============================================================
    # Footwear Products
    # ============================================================

    def _to_product_card(self, prod: Product) -> ProductCardResponse:
        """Helper to map a Product entity to a concise ProductCardResponse."""
        primary_img = None
        if prod.images:
            for img in prod.images:
                if img.is_primary:
                    primary_img = img.url
                    break
            if not primary_img and len(prod.images) > 0:
                primary_img = prod.images[0].url

        return ProductCardResponse(
            id=prod.id,
            name=prod.name,
            slug=prod.slug,
            base_price=prod.base_price,
            discount_price=prod.discount_price,
            material=prod.material,
            average_rating=prod.average_rating,
            review_count=prod.review_count,
            is_featured=prod.is_featured,
            is_new_arrival=prod.is_new_arrival,
            primary_image_url=primary_img,
            category_name=prod.category.name if prod.category else None,
            collection_name=prod.collection.name if prod.collection else None,
        )

    def _to_event_payload(self, prod: Product) -> dict:
        heel_sizes = [c.value for c in (prod.customizations or []) if c.type == "HEEL_SIZE" and c.is_available]
        sizes = list(dict.fromkeys([v.size for v in (prod.variants or []) if v.is_active]))
        colors = list(dict.fromkeys([v.color_name for v in (prod.variants or []) if v.is_active]))
        primary_img = next((img.url for img in (prod.images or []) if img.is_primary), None)
        if not primary_img and prod.images:
            primary_img = prod.images[0].url

        effective_price = float(prod.discount_price if prod.discount_price else prod.base_price)
        return {
            "id": str(prod.id),
            "name": prod.name,
            "slug": prod.slug,
            "description": prod.description,
            "category_id": str(prod.category_id) if prod.category_id else None,
            "category_name": prod.category.name if prod.category else None,
            "collection_id": str(prod.collection_id) if prod.collection_id else None,
            "collection_name": prod.collection.name if prod.collection else None,
            "base_price": float(prod.base_price),
            "discount_price": float(prod.discount_price) if prod.discount_price else None,
            "effective_price": effective_price,
            "material": prod.material,
            "sole_material": prod.sole_material,
            "heel_sizes": heel_sizes,
            "sizes": sizes,
            "colors": colors,
            "is_active": prod.is_active,
            "is_featured": prod.is_featured,
            "is_new_arrival": prod.is_new_arrival,
            "is_in_stock": True,
            "average_rating": float(prod.average_rating),
            "review_count": prod.review_count,
            "primary_image_url": primary_img,
            "created_at": prod.created_at.isoformat() if prod.created_at else None,
        }


    async def list_products(
        self,
        page: int = 1,
        size: int = 20,
        category_id: Optional[uuid.UUID] = None,
        collection_id: Optional[uuid.UUID] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        is_featured: Optional[bool] = None,
        is_new_arrival: Optional[bool] = None,
        sort_by: str = "newest",
        active_only: bool = True,
        search: Optional[str] = None,
    ) -> ProductListPaginatedResponse:
        products, total = await self.repo.list_products(
            page=page,
            size=size,
            category_id=category_id,
            collection_id=collection_id,
            min_price=min_price,
            max_price=max_price,
            is_featured=is_featured,
            is_new_arrival=is_new_arrival,
            sort_by=sort_by,
            active_only=active_only,
            search=search,
        )
        cards = [self._to_product_card(p) for p in products]
        return ProductListPaginatedResponse(total=total, page=page, size=size, items=cards)

    async def get_product_detail(self, slug_or_id: str) -> ProductDetailResponse:
        try:
            prod_id = uuid.UUID(slug_or_id)
            prod = await self.repo.get_product_by_id(prod_id)
        except ValueError:
            prod = await self.repo.get_product_by_slug(slug_or_id)

        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        return ProductDetailResponse.model_validate(prod)

    async def create_product(self, req: ProductCreate) -> ProductDetailResponse:
        # Verify category exists
        cat = await self.repo.get_category_by_id(req.category_id)
        if not cat:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category_id.")

        if req.collection_id:
            coll = await self.repo.get_collection_by_id(req.collection_id)
            if not coll:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid collection_id.")

        slug = generate_slug(req.name)
        existing = await self.repo.get_product_by_slug(slug)
        if existing:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        prod = await self.repo.create_product(
            slug=slug,
            name=req.name,
            description=req.description,
            category_id=req.category_id,
            collection_id=req.collection_id,
            base_price=req.base_price,
            discount_price=req.discount_price,
            material=req.material,
            sole_material=req.sole_material,
            care_instructions=req.care_instructions,
            is_active=req.is_active,
            is_featured=req.is_featured,
            is_new_arrival=req.is_new_arrival,
        )

        # Automatically add the 3 standard heel customizations: 1 inch, 2 inch, 3 inch
        for h in ["1 inch", "2 inch", "3 inch"]:
            await self.repo.create_customization(
                product_id=prod.id,
                type="HEEL_SIZE",
                value=h,
                additional_price=Decimal("0.00"),
                is_available=True,
            )

        full_prod = await self.repo.get_product_by_id(prod.id)

        # Publish product.created Kafka event
        await event_producer.publish(
            topic="product.events",
            event=DomainEvent(
                event_type="product.created",
                producer="product-service",
                payload=self._to_event_payload(full_prod),
            ),
            key=str(full_prod.id),
        )

        return ProductDetailResponse.model_validate(full_prod)

    async def update_product(self, product_id: uuid.UUID, req: ProductUpdate) -> ProductDetailResponse:
        prod = await self.repo.get_product_by_id(product_id)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        kwargs = req.model_dump(exclude_unset=True)
        if "name" in kwargs and kwargs["name"]:
            kwargs["slug"] = generate_slug(kwargs["name"])

        updated = await self.repo.update_product(prod, **kwargs)
        full_prod = await self.repo.get_product_by_id(updated.id)

        # Publish product.updated Kafka event
        await event_producer.publish(
            topic="product.events",
            event=DomainEvent(
                event_type="product.updated",
                producer="product-service",
                payload=self._to_event_payload(full_prod),
            ),
            key=str(full_prod.id),
        )

        return ProductDetailResponse.model_validate(full_prod)

    async def delete_product(self, product_id: uuid.UUID) -> bool:
        deleted = await self.repo.delete_product(product_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        # Publish product.deleted Kafka event
        await event_producer.publish(
            topic="product.events",
            event=DomainEvent(
                event_type="product.deleted",
                producer="product-service",
                payload={"product_id": str(product_id)},
            ),
            key=str(product_id),
        )

        return True

    # ============================================================
    # Variants & Customizations
    # ============================================================

    async def add_variant(self, product_id: uuid.UUID, req: ProductVariantCreate) -> ProductVariantResponse:
        prod = await self.repo.get_product_by_id(product_id, load_relations=False)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        existing_sku = await self.repo.get_variant_by_sku(req.sku)
        if existing_sku:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"SKU '{req.sku}' already exists.")

        var = await self.repo.create_variant(
            product_id=product_id,
            sku=req.sku.upper(),
            size=req.size,
            color_name=req.color_name,
            color_hex=req.color_hex,
            price_override=req.price_override,
            is_active=req.is_active,
        )
        return ProductVariantResponse.model_validate(var)

    async def update_variant(self, variant_id: uuid.UUID, req: ProductVariantUpdate) -> ProductVariantResponse:
        var = await self.repo.get_variant_by_id(variant_id)
        if not var:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found.")

        kwargs = req.model_dump(exclude_unset=True)
        if "sku" in kwargs and kwargs["sku"]:
            kwargs["sku"] = kwargs["sku"].upper()
            existing = await self.repo.get_variant_by_sku(kwargs["sku"])
            if existing and existing.id != variant_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already in use.")

        updated = await self.repo.update_variant(var, **kwargs)
        return ProductVariantResponse.model_validate(updated)

    async def delete_variant(self, variant_id: uuid.UUID) -> bool:
        deleted = await self.repo.delete_variant(variant_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found.")
        return True

    async def add_customization(
        self, product_id: uuid.UUID, req: CustomizationOptionCreate
    ) -> CustomizationOptionResponse:
        prod = await self.repo.get_product_by_id(product_id, load_relations=False)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        cust = await self.repo.create_customization(
            product_id=product_id,
            type=req.type,
            value=req.value,
            additional_price=req.additional_price,
            is_available=req.is_available,
        )
        return CustomizationOptionResponse.model_validate(cust)

    async def update_customization(
        self, customization_id: uuid.UUID, req: CustomizationOptionUpdate
    ) -> CustomizationOptionResponse:
        cust = await self.repo.get_customization_by_id(customization_id)
        if not cust:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customization option not found.")

        kwargs = req.model_dump(exclude_unset=True)
        updated = await self.repo.update_customization(cust, **kwargs)
        return CustomizationOptionResponse.model_validate(updated)

    async def delete_customization(self, customization_id: uuid.UUID) -> bool:
        deleted = await self.repo.delete_customization(customization_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customization not found.")
        return True

    # ============================================================
    # Product Images
    # ============================================================

    async def upload_product_image(
        self,
        product_id: uuid.UUID,
        file: UploadFile,
        alt_text: Optional[str] = None,
        display_order: int = 0,
        is_primary: bool = False,
        variant_id: Optional[uuid.UUID] = None,
    ) -> ProductImageResponse:
        prod = await self.repo.get_product_by_id(product_id, load_relations=False)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        if variant_id:
            var = await self.repo.get_variant_by_id(variant_id)
            if not var or var.product_id != product_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid variant_id.")

        rel_url, _ = await storage_service.upload_image(file, subfolder="products")
        img = await self.repo.add_product_image(
            product_id=product_id,
            url=rel_url,
            alt_text=alt_text or prod.name,
            display_order=display_order,
            is_primary=is_primary,
            variant_id=variant_id,
        )
        return ProductImageResponse.model_validate(img)

    async def set_primary_image(self, product_id: uuid.UUID, image_id: uuid.UUID) -> ProductImageResponse:
        img = await self.repo.set_primary_image(product_id, image_id)
        if not img:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
        return ProductImageResponse.model_validate(img)

    async def delete_product_image(self, image_id: uuid.UUID) -> bool:
        img = await self.repo.get_image_by_id(image_id)
        if not img:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")

        await storage_service.delete_image(img.url)
        return await self.repo.delete_image(image_id)

    # ============================================================
    # Reviews
    # ============================================================

    async def get_product_reviews(self, product_id: uuid.UUID) -> ProductReviewSummaryResponse:
        prod = await self.repo.get_product_by_id(product_id, load_relations=False)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        reviews = await self.repo.get_product_reviews(product_id, approved_only=True)
        dist = RatingDistribution()
        for r in reviews:
            if r.rating == 5:
                dist.five_star += 1
            elif r.rating == 4:
                dist.four_star += 1
            elif r.rating == 3:
                dist.three_star += 1
            elif r.rating == 2:
                dist.two_star += 1
            elif r.rating == 1:
                dist.one_star += 1

        review_responses = [ReviewResponse.model_validate(r) for r in reviews]
        return ProductReviewSummaryResponse(
            product_id=product_id,
            average_rating=prod.average_rating,
            total_reviews=prod.review_count,
            distribution=dist,
            reviews=review_responses,
        )

    async def create_review(
        self,
        product_id: uuid.UUID,
        user_id: uuid.UUID,
        user_name: str,
        req: ReviewCreate,
    ) -> ReviewResponse:
        prod = await self.repo.get_product_by_id(product_id, load_relations=False)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        review = await self.repo.create_review(
            product_id=product_id,
            user_id=user_id,
            user_name=user_name,
            rating=req.rating,
            title=req.title,
            comment=req.comment,
            image_urls=req.image_urls,
            is_verified_purchase=True,
        )
        full_rev = await self.repo.get_review_by_id(review.id)
        # Reload product to get updated rating stats
        reloaded_prod = await self.repo.get_product_by_id(product_id, load_relations=False)

        # Publish review.created Kafka event
        await event_producer.publish(
            topic="review.events",
            event=DomainEvent(
                event_type="review.created",
                producer="product-service",
                payload={
                    "review_id": str(full_rev.id),
                    "product_id": str(product_id),
                    "user_id": str(user_id),
                    "rating": full_rev.rating,
                    "new_average_rating": float(reloaded_prod.average_rating) if reloaded_prod else 0.0,
                    "review_count": reloaded_prod.review_count if reloaded_prod else 0,
                },
            ),
            key=str(product_id),
        )

        return ReviewResponse.model_validate(full_rev)

    async def update_review(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        req: ReviewUpdate,
    ) -> ReviewResponse:
        rev = await self.repo.get_review_by_id(review_id)
        if not rev:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

        if rev.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own reviews.",
            )

        kwargs = req.model_dump(exclude_unset=True)
        updated = await self.repo.update_review(rev, **kwargs)
        full_rev = await self.repo.get_review_by_id(updated.id)
        return ReviewResponse.model_validate(full_rev)

    async def delete_review(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> bool:
        rev = await self.repo.get_review_by_id(review_id)
        if not rev:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

        if not is_admin and rev.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews.",
            )

        product_id = rev.product_id
        success = await self.repo.delete_review(review_id)
        if success:
            reloaded_prod = await self.repo.get_product_by_id(product_id, load_relations=False)
            await event_producer.publish(
                topic="review.events",
                event=DomainEvent(
                    event_type="review.created",
                    producer="product-service",
                    payload={
                        "review_id": str(review_id),
                        "product_id": str(product_id),
                        "user_id": str(user_id),
                        "rating": 0,
                        "new_average_rating": float(reloaded_prod.average_rating) if reloaded_prod else 0.0,
                        "review_count": reloaded_prod.review_count if reloaded_prod else 0,
                    },
                ),
                key=str(product_id),
            )
        return success

    async def upload_review_image(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        file: UploadFile,
        is_admin: bool = False,
    ) -> ReviewImageResponse:
        """Attach photo upload to a customer review."""
        rev = await self.repo.get_review_by_id(review_id)
        if not rev:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

        if not is_admin and rev.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload images for your own review.",
            )

        saved_url = await storage_service.save_image(file, subfolder="reviews")
        img = await self.repo.add_review_image(review_id=review_id, url=saved_url)
        return ReviewImageResponse.model_validate(img)

    async def moderate_review(
        self,
        review_id: uuid.UUID,
        is_approved: bool,
    ) -> ReviewResponse:
        """Admin moderation to approve or reject a customer review."""
        rev = await self.repo.set_review_approval(review_id, is_approved=is_approved)
        if not rev:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

        reloaded_prod = await self.repo.get_product_by_id(rev.product_id, load_relations=False)
        await event_producer.publish(
            topic="review.events",
            event=DomainEvent(
                event_type="review.created",
                producer="product-service",
                payload={
                    "review_id": str(rev.id),
                    "product_id": str(rev.product_id),
                    "user_id": str(rev.user_id),
                    "rating": rev.rating,
                    "new_average_rating": float(reloaded_prod.average_rating) if reloaded_prod else 0.0,
                    "review_count": reloaded_prod.review_count if reloaded_prod else 0,
                },
            ),
            key=str(rev.product_id),
        )

        full_rev = await self.repo.get_review_by_id(rev.id)
        return ReviewResponse.model_validate(full_rev)

    async def upload_product_image(
        self,
        product_id: uuid.UUID,
        file: UploadFile,
        alt_text: Optional[str] = None,
        display_order: int = 0,
        is_primary: bool = False,
        variant_id: Optional[uuid.UUID] = None,
    ) -> ProductImageResponse:
        """Upload product image, optimize to WebP, and attach to product gallery."""
        prod = await self.repo.get_product_by_id(product_id, load_relations=False)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        relative_url, _ = await storage_service.upload_image(file, subfolder="products")

        img = await self.repo.add_product_image(
            product_id=product_id,
            url=relative_url,
            alt_text=alt_text or prod.name,
            display_order=display_order,
            is_primary=is_primary,
            variant_id=variant_id,
        )

        if is_primary:
            await self.repo.set_primary_image(product_id, img.id)

        # Broadcast Kafka domain event so Search Service updates primary image
        await event_producer.publish(
            topic="product.events",
            event=DomainEvent(
                event_type="product.updated",
                producer="product-service",
                payload={
                    "product_id": str(product_id),
                    "name": prod.name,
                    "slug": prod.slug,
                    "primary_image_url": relative_url if is_primary else None,
                },
            ),
            key=str(product_id),
        )

        return ProductImageResponse.model_validate(img)

    async def set_primary_image(
        self,
        product_id: uuid.UUID,
        image_id: uuid.UUID,
    ) -> ProductImageResponse:
        """Set designated image as the primary image for a footwear product."""
        img = await self.repo.set_primary_image(product_id, image_id)
        if not img:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")

        prod = await self.repo.get_product_by_id(product_id, load_relations=False)
        if prod:
            await event_producer.publish(
                topic="product.events",
                event=DomainEvent(
                    event_type="product.updated",
                    producer="product-service",
                    payload={
                        "product_id": str(product_id),
                        "name": prod.name,
                        "slug": prod.slug,
                        "primary_image_url": img.url,
                    },
                ),
                key=str(product_id),
            )

        return ProductImageResponse.model_validate(img)

    async def delete_product_image(self, image_id: uuid.UUID) -> bool:
        """Delete an image from disk and product gallery."""
        img = await self.repo.get_image_by_id(image_id)
        if not img:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")

        product_id = img.product_id
        await storage_service.delete_image(img.url)
        deleted = await self.repo.delete_image(image_id)

        if deleted:
            prod = await self.repo.get_product_by_id(product_id, load_relations=True)
            if prod:
                new_primary = next((i.url for i in prod.images if i.is_primary), None) or (prod.images[0].url if prod.images else None)
                await event_producer.publish(
                    topic="product.events",
                    event=DomainEvent(
                        event_type="product.updated",
                        producer="product-service",
                        payload={
                            "product_id": str(product_id),
                            "name": prod.name,
                            "slug": prod.slug,
                            "primary_image_url": new_primary,
                        },
                    ),
                    key=str(product_id),
                )

        return deleted


