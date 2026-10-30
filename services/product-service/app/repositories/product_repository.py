"""
Product Service Database Repository.
Encapsulates all SQLAlchemy queries for Footwear Products, Categories, Collections,
Variants, Customizations, Images, and Reviews.
"""

import uuid
from typing import List, Optional, Tuple
from decimal import Decimal
from sqlalchemy import desc, asc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import (
    Category,
    Collection,
    CustomizationOption,
    Product,
    ProductImage,
    ProductVariant,
    Review,
    ReviewImage,
)


class ProductRepository:
    """Data access repository for Product Service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # Categories
    # ============================================================

    async def list_categories(self, active_only: bool = True) -> List[Category]:
        """Fetch all categories ordered by display order."""
        stmt = select(Category)
        if active_only:
            stmt = stmt.where(Category.is_active == True)
        stmt = stmt.order_by(Category.display_order, Category.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_category_by_id(self, category_id: uuid.UUID) -> Optional[Category]:
        stmt = select(Category).where(Category.id == category_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_category_by_slug(self, slug: str) -> Optional[Category]:
        stmt = select(Category).where(Category.slug == slug.lower())
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create_category(self, slug: str, **kwargs) -> Category:
        category = Category(slug=slug.lower(), **kwargs)
        self.db.add(category)
        await self.db.flush()
        return category

    async def update_category(self, category: Category, **kwargs) -> Category:
        for k, v in kwargs.items():
            if hasattr(category, k) and v is not None:
                setattr(category, k, v)
        await self.db.flush()
        return category

    async def delete_category(self, category_id: uuid.UUID) -> bool:
        cat = await self.get_category_by_id(category_id)
        if cat:
            await self.db.delete(cat)
            await self.db.flush()
            return True
        return False

    # ============================================================
    # Collections
    # ============================================================

    async def list_collections(self, active_only: bool = True) -> List[Collection]:
        """Fetch all collections."""
        stmt = select(Collection)
        if active_only:
            stmt = stmt.where(Collection.is_active == True)
        stmt = stmt.order_by(Collection.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_collection_by_id(self, collection_id: uuid.UUID) -> Optional[Collection]:
        stmt = select(Collection).where(Collection.id == collection_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_collection_by_slug(self, slug: str) -> Optional[Collection]:
        stmt = select(Collection).where(Collection.slug == slug.lower())
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create_collection(self, slug: str, **kwargs) -> Collection:
        coll = Collection(slug=slug.lower(), **kwargs)
        self.db.add(coll)
        await self.db.flush()
        return coll

    async def update_collection(self, collection: Collection, **kwargs) -> Collection:
        for k, v in kwargs.items():
            if hasattr(collection, k) and v is not None:
                setattr(collection, k, v)
        await self.db.flush()
        return collection

    async def delete_collection(self, collection_id: uuid.UUID) -> bool:
        coll = await self.get_collection_by_id(collection_id)
        if coll:
            await self.db.delete(coll)
            await self.db.flush()
            return True
        return False

    # ============================================================
    # Footwear Products
    # ============================================================

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
    ) -> Tuple[List[Product], int]:
        """Query footwear catalog with flexible filters, sorting, and pagination."""
        offset = (page - 1) * size
        conditions = []

        if active_only:
            conditions.append(Product.is_active == True)
        if category_id:
            conditions.append(Product.category_id == category_id)
        if collection_id:
            conditions.append(Product.collection_id == collection_id)
        if min_price is not None:
            conditions.append(Product.base_price >= min_price)
        if max_price is not None:
            conditions.append(Product.base_price <= max_price)
        if is_featured is not None:
            conditions.append(Product.is_featured == is_featured)
        if is_new_arrival is not None:
            conditions.append(Product.is_new_arrival == is_new_arrival)
        if search:
            pattern = f"%{search.strip()}%"
            conditions.append(or_(Product.name.ilike(pattern), Product.description.ilike(pattern)))

        # Count
        count_stmt = select(func.count(Product.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = (await self.db.execute(count_stmt)).scalar() or 0

        # Query with eager loaded relationships
        stmt = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.collection),
                selectinload(Product.images),
            )
        )
        if conditions:
            stmt = stmt.where(*conditions)

        # Sorting
        if sort_by == "price_asc":
            stmt = stmt.order_by(asc(Product.base_price))
        elif sort_by == "price_desc":
            stmt = stmt.order_by(desc(Product.base_price))
        elif sort_by == "rating":
            stmt = stmt.order_by(desc(Product.average_rating))
        else:
            stmt = stmt.order_by(desc(Product.created_at))

        stmt = stmt.offset(offset).limit(size)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_product_by_id(
        self, product_id: uuid.UUID, load_relations: bool = True
    ) -> Optional[Product]:
        """Fetch product by ID."""
        stmt = select(Product).where(Product.id == product_id)
        if load_relations:
            stmt = stmt.options(
                selectinload(Product.category),
                selectinload(Product.collection),
                selectinload(Product.variants),
                selectinload(Product.customizations),
                selectinload(Product.images),
            )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_product_by_slug(
        self, slug: str, load_relations: bool = True
    ) -> Optional[Product]:
        """Fetch product by unique slug."""
        stmt = select(Product).where(Product.slug == slug.lower())
        if load_relations:
            stmt = stmt.options(
                selectinload(Product.category),
                selectinload(Product.collection),
                selectinload(Product.variants),
                selectinload(Product.customizations),
                selectinload(Product.images),
            )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create_product(self, slug: str, **kwargs) -> Product:
        prod = Product(slug=slug.lower(), **kwargs)
        self.db.add(prod)
        await self.db.flush()
        return prod

    async def update_product(self, product: Product, **kwargs) -> Product:
        for k, v in kwargs.items():
            if hasattr(product, k) and v is not None:
                setattr(product, k, v)
        await self.db.flush()
        return product

    async def delete_product(self, product_id: uuid.UUID) -> bool:
        prod = await self.get_product_by_id(product_id, load_relations=False)
        if prod:
            await self.db.delete(prod)
            await self.db.flush()
            return True
        return False

    async def update_product_rating(self, product_id: uuid.UUID) -> None:
        """Recalculate average rating and count for a product."""
        stmt = select(
            func.coalesce(func.avg(Review.rating), 0.0),
            func.count(Review.id),
        ).where(
            Review.product_id == product_id,
            Review.is_approved == True,
        )
        res = await self.db.execute(stmt)
        avg_rating, total_reviews = res.one()

        prod = await self.get_product_by_id(product_id, load_relations=False)
        if prod:
            prod.average_rating = round(float(avg_rating), 1)
            prod.review_count = int(total_reviews)
            await self.db.flush()

    # ============================================================
    # Product Variants
    # ============================================================

    async def create_variant(self, product_id: uuid.UUID, **kwargs) -> ProductVariant:
        variant = ProductVariant(product_id=product_id, **kwargs)
        self.db.add(variant)
        await self.db.flush()
        return variant

    async def get_variant_by_id(self, variant_id: uuid.UUID) -> Optional[ProductVariant]:
        stmt = select(ProductVariant).where(ProductVariant.id == variant_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_variant_by_sku(self, sku: str) -> Optional[ProductVariant]:
        stmt = select(ProductVariant).where(ProductVariant.sku == sku.upper())
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def update_variant(self, variant: ProductVariant, **kwargs) -> ProductVariant:
        for k, v in kwargs.items():
            if hasattr(variant, k) and v is not None:
                setattr(variant, k, v)
        await self.db.flush()
        return variant

    async def delete_variant(self, variant_id: uuid.UUID) -> bool:
        var = await self.get_variant_by_id(variant_id)
        if var:
            await self.db.delete(var)
            await self.db.flush()
            return True
        return False

    # ============================================================
    # Footwear Customization Options (Heel sizes)
    # ============================================================

    async def create_customization(
        self, product_id: uuid.UUID, **kwargs
    ) -> CustomizationOption:
        cust = CustomizationOption(product_id=product_id, **kwargs)
        self.db.add(cust)
        await self.db.flush()
        return cust

    async def get_customization_by_id(
        self, customization_id: uuid.UUID
    ) -> Optional[CustomizationOption]:
        stmt = select(CustomizationOption).where(CustomizationOption.id == customization_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def update_customization(
        self, customization: CustomizationOption, **kwargs
    ) -> CustomizationOption:
        for k, v in kwargs.items():
            if hasattr(customization, k) and v is not None:
                setattr(customization, k, v)
        await self.db.flush()
        return customization

    async def delete_customization(self, customization_id: uuid.UUID) -> bool:
        cust = await self.get_customization_by_id(customization_id)
        if cust:
            await self.db.delete(cust)
            await self.db.flush()
            return True
        return False

    # ============================================================
    # Product Images
    # ============================================================

    async def add_product_image(
        self,
        product_id: uuid.UUID,
        url: str,
        alt_text: Optional[str] = None,
        display_order: int = 0,
        is_primary: bool = False,
        variant_id: Optional[uuid.UUID] = None,
    ) -> ProductImage:
        if is_primary:
            # Unset existing primary images for this product
            unset_stmt = select(ProductImage).where(
                ProductImage.product_id == product_id,
                ProductImage.is_primary == True,
            )
            existing_primaries = (await self.db.execute(unset_stmt)).scalars().all()
            for img in existing_primaries:
                img.is_primary = False

        image = ProductImage(
            product_id=product_id,
            url=url,
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
            variant_id=variant_id,
        )
        self.db.add(image)
        await self.db.flush()
        return image

    async def get_image_by_id(self, image_id: uuid.UUID) -> Optional[ProductImage]:
        stmt = select(ProductImage).where(ProductImage.id == image_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def set_primary_image(self, product_id: uuid.UUID, image_id: uuid.UUID) -> Optional[ProductImage]:
        # Unset others
        unset_stmt = select(ProductImage).where(ProductImage.product_id == product_id)
        images = (await self.db.execute(unset_stmt)).scalars().all()
        target = None
        for img in images:
            if img.id == image_id:
                img.is_primary = True
                target = img
            else:
                img.is_primary = False
        await self.db.flush()
        return target

    async def delete_image(self, image_id: uuid.UUID) -> bool:
        img = await self.get_image_by_id(image_id)
        if img:
            await self.db.delete(img)
            await self.db.flush()
            return True
        return False

    # ============================================================
    # Reviews
    # ============================================================

    async def get_product_reviews(
        self, product_id: uuid.UUID, approved_only: bool = True
    ) -> List[Review]:
        stmt = (
            select(Review)
            .where(Review.product_id == product_id)
            .options(selectinload(Review.images))
            .order_by(desc(Review.created_at))
        )
        if approved_only:
            stmt = stmt.where(Review.is_approved == True)
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_review_by_id(self, review_id: uuid.UUID) -> Optional[Review]:
        stmt = (
            select(Review)
            .where(Review.id == review_id)
            .options(selectinload(Review.images))
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create_review(
        self,
        product_id: uuid.UUID,
        user_id: uuid.UUID,
        user_name: str,
        rating: int,
        title: Optional[str],
        comment: str,
        image_urls: List[str] = [],
        is_verified_purchase: bool = False,
    ) -> Review:
        review = Review(
            product_id=product_id,
            user_id=user_id,
            user_name=user_name,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=is_verified_purchase,
            is_approved=True,
        )
        self.db.add(review)
        await self.db.flush()

        for url in image_urls:
            r_img = ReviewImage(review_id=review.id, url=url)
            self.db.add(r_img)
        await self.db.flush()

        await self.update_product_rating(product_id)
        return review

    async def update_review(self, review: Review, **kwargs) -> Review:
        for k, v in kwargs.items():
            if hasattr(review, k) and v is not None:
                setattr(review, k, v)
        await self.db.flush()
        await self.update_product_rating(review.product_id)
        return review

    async def delete_review(self, review_id: uuid.UUID) -> bool:
        rev = await self.get_review_by_id(review_id)
        if rev:
            product_id = rev.product_id
            await self.db.delete(rev)
            await self.db.flush()
            await self.update_product_rating(product_id)
            return True
        return False

    async def list_reviews_admin(
        self, page: int = 1, size: int = 20, is_approved: Optional[bool] = None
    ) -> Tuple[List[Review], int]:
        offset = (page - 1) * size
        conditions = []
        if is_approved is not None:
            conditions.append(Review.is_approved == is_approved)

        count_stmt = select(func.count(Review.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Review)
            .options(selectinload(Review.images))
            .order_by(desc(Review.created_at))
            .offset(offset)
            .limit(size)
        )
        if conditions:
            stmt = stmt.where(*conditions)

        return list((await self.db.execute(stmt)).scalars().all()), total

    async def update_product_rating(self, product_id: uuid.UUID):
        """Recalculate and persist average rating and review count for a product."""
        stmt = (
            select(
                func.count(Review.id),
                func.coalesce(func.avg(Review.rating), 0.0),
            )
            .where(Review.product_id == product_id, Review.is_approved == True)
        )
        row = (await self.db.execute(stmt)).first()
        count = row[0] if row else 0
        avg = round(float(row[1]), 1) if row else 0.0

        prod = await self.get_product_by_id(product_id, load_relations=False)
        if prod:
            prod.average_rating = avg
            prod.review_count = count
            await self.db.flush()

    async def add_review_image(self, review_id: uuid.UUID, url: str) -> ReviewImage:
        """Attach customer uploaded photo to a review."""
        img = ReviewImage(review_id=review_id, url=url)
        self.db.add(img)
        await self.db.flush()
        return img

    async def set_review_approval(self, review_id: uuid.UUID, is_approved: bool) -> Optional[Review]:
        """Admin moderation to approve or reject a customer review."""
        rev = await self.get_review_by_id(review_id)
        if rev:
            rev.is_approved = is_approved
            await self.db.flush()
            await self.update_product_rating(rev.product_id)
            return rev
        return None

