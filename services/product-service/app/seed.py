"""
Product Service Seed Script.
Populates realistic, portfolio-grade premium ladies footwear catalog:
- Categories
- Collections
- Products with materials, care instructions, and pricing
- Size (36-41) and Color SKU variants
- Footwear heel customizations (1 inch, 2 inch, 3 inch)
- Sample customer reviews with star ratings
- Recalculates average ratings and review counts

Run via: python -m app.seed
"""

import asyncio
import logging
import uuid
from decimal import Decimal
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.product import (
    Category,
    Collection,
    CustomizationOption,
    Product,
    ProductImage,
    ProductVariant,
    Review,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("seed-product-service")


async def seed_products() -> None:
    """Populate luxury footwear catalog."""
    logger.info("Starting Product Service database seeding...")

    async with AsyncSessionLocal() as session:
        try:
            # 1. Check if products already exist
            existing = await session.execute(select(Product))
            if existing.scalars().first():
                logger.info("Products already seeded. Skipping.")
                return

            # ============================================================
            # 2. Categories
            # ============================================================
            categories_data = [
                {
                    "name": "Stilettos & High Heels",
                    "slug": "stilettos-high-heels",
                    "description": "Exquisite towering silhouettes crafted with architectural balance and soft padded insoles.",
                    "display_order": 1,
                },
                {
                    "name": "Block Heels & Pumps",
                    "slug": "block-heels-pumps",
                    "description": "Timeless day-to-night footwear combining stability, posture, and sophisticated allure.",
                    "display_order": 2,
                },
                {
                    "name": "Luxury Flats & Loafers",
                    "slug": "luxury-flats-loafers",
                    "description": "Ultra-supple leather flats and slip-ons with artisanal stitching and cushioned arches.",
                    "display_order": 3,
                },
                {
                    "name": "Bridal & Evening",
                    "slug": "bridal-evening",
                    "description": "Celebratory luxury footwear adorned with lustrous pearls, crystals, and delicate silk.",
                    "display_order": 4,
                },
                {
                    "name": "Mules & Slides",
                    "slug": "mules-slides",
                    "description": "Effortless slip-on elegance featuring pointed toes, sculpted kitten heels, and rich textures.",
                    "display_order": 5,
                },
            ]

            category_map = {}
            for cat_data in categories_data:
                cat = Category(**cat_data, is_active=True)
                session.add(cat)
                await session.flush()
                category_map[cat.slug] = cat

            logger.info(f"Seeded {len(category_map)} categories.")

            # ============================================================
            # 3. Collections
            # ============================================================
            collections_data = [
                {
                    "name": "Bridal Couture Edit",
                    "slug": "bridal-couture-edit",
                    "description": "Heirloom-quality bridal heels and flats adorned with freshwater pearls and champagne silk.",
                    "banner_image_url": "/api/uploads/collections/bridal-couture.webp",
                },
                {
                    "name": "Riviera Summer Luxe",
                    "slug": "riviera-summer-luxe",
                    "description": "Effortless resort-ready mules and strappy stilettos drenched in Mediterranean tones.",
                    "banner_image_url": "/api/uploads/collections/riviera-summer.webp",
                },
                {
                    "name": "Midnight Atelier",
                    "slug": "midnight-atelier",
                    "description": "Dark romantic evening pumps featuring Italian velvet, gold hardware, and crystal embellishments.",
                    "banner_image_url": "/api/uploads/collections/midnight-atelier.webp",
                },
            ]

            collection_map = {}
            for col_data in collections_data:
                col = Collection(**col_data, is_active=True)
                session.add(col)
                await session.flush()
                collection_map[col.slug] = col

            logger.info(f"Seeded {len(collection_map)} collections.")

            # ============================================================
            # 4. Products & Variants & Customizations
            # ============================================================
            products_data = [
                {
                    "name": "Aurelia Crystal Satin Pump",
                    "slug": "aurelia-crystal-satin-pump",
                    "description": "Hand-constructed in Tuscany from lustrous Italian silk satin, the Aurelia pump features an ankle-framing crystal brooch and our signature shock-absorbing memory foam footbed. Perfectly balanced for all-day celebrations.",
                    "category_slug": "bridal-evening",
                    "collection_slug": "bridal-couture-edit",
                    "base_price": Decimal("380.00"),
                    "discount_price": None,
                    "material": "Italian Silk Satin & Austrian Crystal Brooch",
                    "sole_material": "Genuine Brushed Italian Leather",
                    "care_instructions": "Spot clean silk with a soft damp cloth. Store in provided dust bag.",
                    "is_featured": True,
                    "is_new_arrival": True,
                    "variants": [
                        ("IBR-AUR-GLD-36", "36", "Champagne Gold", "#F7E7CE", None),
                        ("IBR-AUR-GLD-37", "37", "Champagne Gold", "#F7E7CE", None),
                        ("IBR-AUR-GLD-38", "38", "Champagne Gold", "#F7E7CE", None),
                        ("IBR-AUR-GLD-39", "39", "Champagne Gold", "#F7E7CE", None),
                        ("IBR-AUR-GLD-40", "40", "Champagne Gold", "#F7E7CE", None),
                        ("IBR-AUR-EMR-37", "37", "Emerald Velvet", "#097969", Decimal("395.00")),
                        ("IBR-AUR-EMR-38", "38", "Emerald Velvet", "#097969", Decimal("395.00")),
                        ("IBR-AUR-EMR-39", "39", "Emerald Velvet", "#097969", Decimal("395.00")),
                    ],
                    "images": [
                        ("/api/uploads/products/aurelia-champagne-main.webp", "Aurelia Crystal Pump Front", True, 0),
                        ("/api/uploads/products/aurelia-champagne-side.webp", "Aurelia Crystal Pump Side Profile", False, 1),
                        ("/api/uploads/products/aurelia-champagne-detail.webp", "Aurelia Brooch Close-up", False, 2),
                    ],
                    "reviews": [
                        ("Elena Rostova", 5, "Breathtaking comfort and beauty", "Wore these for 10 hours straight on my wedding day. The 2-inch customized heel was the best decision!"),
                        ("Camille Laurent", 5, "Worth every single penny", "The satin quality is sublime and the crystal buckle reflects light effortlessly. Received endless compliments."),
                    ]
                },
                {
                    "name": "Seraphina Nappa Ankle-Strap Heel",
                    "slug": "seraphina-nappa-ankle-strap-heel",
                    "description": "A study in sculptural minimalism. The Seraphina is handcrafted from butter-soft Italian nappa leather with a delicate buckled ankle strap that elongates the leg without friction.",
                    "category_slug": "stilettos-high-heels",
                    "collection_slug": "midnight-atelier",
                    "base_price": Decimal("340.00"),
                    "discount_price": Decimal("295.00"),
                    "material": "100% Full-Grain Italian Nappa Leather",
                    "sole_material": "Non-slip treated leather sole",
                    "care_instructions": "Condition leather twice yearly with neutral wax cream.",
                    "is_featured": True,
                    "is_new_arrival": False,
                    "variants": [
                        ("IBR-SER-BLK-36", "36", "Midnight Black", "#111111", None),
                        ("IBR-SER-BLK-37", "37", "Midnight Black", "#111111", None),
                        ("IBR-SER-BLK-38", "38", "Midnight Black", "#111111", None),
                        ("IBR-SER-BLK-39", "39", "Midnight Black", "#111111", None),
                        ("IBR-SER-NUD-37", "37", "Nude Beige", "#E8D3C3", None),
                        ("IBR-SER-NUD-38", "38", "Nude Beige", "#E8D3C3", None),
                    ],
                    "images": [
                        ("/api/uploads/products/seraphina-black-main.webp", "Seraphina Ankle Strap Front", True, 0),
                        ("/api/uploads/products/seraphina-black-side.webp", "Seraphina Side View", False, 1),
                    ],
                    "reviews": [
                        ("Vivienne Brooks", 5, "The ultimate evening heel", "Stunning silhouette and surprisingly comfortable padding in the toe box."),
                    ]
                },
                {
                    "name": "Valentina Embellished Velvet Mule",
                    "slug": "valentina-embellished-velvet-mule",
                    "description": "Royal evening mules in jewel-toned silk velvet, decorated with intricate tonal micro-beading and a sculpted flared kitten heel.",
                    "category_slug": "mules-slides",
                    "collection_slug": "midnight-atelier",
                    "base_price": Decimal("295.00"),
                    "discount_price": None,
                    "material": "Silk Velvet with Hand-applied Glass Beads",
                    "sole_material": "Genuine Leather",
                    "care_instructions": "Gently brush velvet in direction of grain with a dry bristle brush.",
                    "is_featured": False,
                    "is_new_arrival": True,
                    "variants": [
                        ("IBR-VAL-NAV-37", "37", "Royal Navy", "#000080", None),
                        ("IBR-VAL-NAV-38", "38", "Royal Navy", "#000080", None),
                        ("IBR-VAL-RUB-37", "37", "Ruby Red", "#9B111E", None),
                        ("IBR-VAL-RUB-38", "38", "Ruby Red", "#9B111E", None),
                        ("IBR-VAL-RUB-39", "39", "Ruby Red", "#9B111E", None),
                    ],
                    "images": [
                        ("/api/uploads/products/valentina-navy-main.webp", "Valentina Mule Front", True, 0),
                    ],
                    "reviews": [
                        ("Zoe Kravitz", 4, "Chic & opulent", "The velvet is rich and deep in color. Elegant choice for dinner parties."),
                    ]
                },
                {
                    "name": "Celeste Pointed Toe Flat",
                    "slug": "celeste-pointed-toe-flat",
                    "description": "Refined everyday luxury. Crafted with an elongated almond-pointed toe, hidden arch pillow, and a whisper of polished gold along the low stacked heel.",
                    "category_slug": "luxury-flats-loafers",
                    "collection_slug": "riviera-summer-luxe",
                    "base_price": Decimal("260.00"),
                    "discount_price": None,
                    "material": "Glove Calf Leather & 14k Gold-dipped Heel Accent",
                    "sole_material": "Flexible Rubberized Leather Sole",
                    "care_instructions": "Wipe with damp cotton cloth. Keep dry.",
                    "is_featured": True,
                    "is_new_arrival": True,
                    "variants": [
                        ("IBR-CEL-IVR-36", "36", "Ivory Pearl", "#FFFFF0", None),
                        ("IBR-CEL-IVR-37", "37", "Ivory Pearl", "#FFFFF0", None),
                        ("IBR-CEL-IVR-38", "38", "Ivory Pearl", "#FFFFF0", None),
                        ("IBR-CEL-IVR-39", "39", "Ivory Pearl", "#FFFFF0", None),
                        ("IBR-CEL-ROS-38", "38", "Metallic Rose", "#B76E79", None),
                    ],
                    "images": [
                        ("/api/uploads/products/celeste-ivory-main.webp", "Celeste Flat Main", True, 0),
                    ],
                    "reviews": [
                        ("Sophia Loren", 5, "Flats that feel like heels", "So polished for meetings yet feels like walking on air. The arch pillow makes all the difference."),
                    ]
                },
                {
                    "name": "Camilla Pearl Slingback",
                    "slug": "camilla-pearl-slingback",
                    "description": "Ethereal French moire silk pump with an elasticated slingback strap and graduated natural freshwater pearls encircling the vamp.",
                    "category_slug": "bridal-evening",
                    "collection_slug": "bridal-couture-edit",
                    "base_price": Decimal("350.00"),
                    "discount_price": None,
                    "material": "French Moire Silk with Cultured Freshwater Pearls",
                    "sole_material": "Leather sole with slip-resistant insert",
                    "care_instructions": "Store in dry silk pouch. Avoid perfumes or direct liquids.",
                    "is_featured": True,
                    "is_new_arrival": True,
                    "variants": [
                        ("IBR-CAM-WHT-36", "36", "Bridal White", "#FFFFFF", None),
                        ("IBR-CAM-WHT-37", "37", "Bridal White", "#FFFFFF", None),
                        ("IBR-CAM-WHT-38", "38", "Bridal White", "#FFFFFF", None),
                        ("IBR-CAM-WHT-39", "39", "Bridal White", "#FFFFFF", None),
                        ("IBR-CAM-PNK-37", "37", "Blush Pink", "#FFD1DC", None),
                        ("IBR-CAM-PNK-38", "38", "Blush Pink", "#FFD1DC", None),
                    ],
                    "images": [
                        ("/api/uploads/products/camilla-white-main.webp", "Camilla Slingback Front", True, 0),
                    ],
                    "reviews": [
                        ("Ariana Grande", 5, "Dream shoes", "The pearls are high quality and secure. Best bridal footwear on the market."),
                    ]
                },
                {
                    "name": "Leela Royal Wedge",
                    "slug": "leela-royal-wedge",
                    "description": "A masterpiece of sculpted elevation. Handcrafted in Tuscany with metallic specchio calfskin, braided golden accents, and our signature multi-density orthopedic arch cradle.",
                    "category_slug": "mules-slides",
                    "collection_slug": "riviera-summer-luxe",
                    "base_price": Decimal("365.00"),
                    "discount_price": None,
                    "material": "Italian Specchio Calfskin & Sculpted Metallic Wedge",
                    "sole_material": "Leather sole with cushioned arch contour",
                    "care_instructions": "Buff with soft dry microfibre cloth. Store in bespoke flannel dust bag.",
                    "is_featured": True,
                    "is_new_arrival": True,
                    "variants": [
                        ("IBR-LEE-GLD-36", "36", "Royal Gold", "#D4AF37", None),
                        ("IBR-LEE-GLD-37", "37", "Royal Gold", "#D4AF37", None),
                        ("IBR-LEE-GLD-38", "38", "Royal Gold", "#D4AF37", None),
                        ("IBR-LEE-GLD-39", "39", "Royal Gold", "#D4AF37", None),
                        ("IBR-LEE-GLD-40", "40", "Royal Gold", "#D4AF37", None),
                    ],
                    "images": [
                        ("https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=800&q=80", "Leela Royal Wedge Profile", True, 0),
                    ],
                    "reviews": [
                        ("Alessandra Ambrosio", 5, "Remarkable poise and comfort", "The wedge silhouette gives all the height without any strain. Magnificent craftsmanship."),
                    ]
                },
            ]

            total_variants = 0
            for p_info in products_data:
                category = category_map[p_info["category_slug"]]
                collection = collection_map.get(p_info["collection_slug"])

                prod = Product(
                    name=p_info["name"],
                    slug=p_info["slug"],
                    description=p_info["description"],
                    category_id=category.id,
                    collection_id=collection.id if collection else None,
                    base_price=p_info["base_price"],
                    discount_price=p_info["discount_price"],
                    material=p_info["material"],
                    sole_material=p_info["sole_material"],
                    care_instructions=p_info["care_instructions"],
                    is_active=True,
                    is_featured=p_info["is_featured"],
                    is_new_arrival=p_info["is_new_arrival"],
                )
                session.add(prod)
                await session.flush()

                # 1, 2, and 3-inch heel customization options
                for heel in ["1 inch", "2 inch", "3 inch"]:
                    session.add(
                        CustomizationOption(
                            product_id=prod.id,
                            type="HEEL_SIZE",
                            value=heel,
                            additional_price=Decimal("0.00"),
                            is_available=True,
                        )
                    )

                # Variants
                for sku, size, color_name, color_hex, price_override in p_info["variants"]:
                    session.add(
                        ProductVariant(
                            product_id=prod.id,
                            sku=sku,
                            size=size,
                            color_name=color_name,
                            color_hex=color_hex,
                            price_override=price_override,
                            is_active=True,
                        )
                    )
                    total_variants += 1

                # Images
                for url, alt, is_prim, order in p_info["images"]:
                    session.add(
                        ProductImage(
                            product_id=prod.id,
                            url=url,
                            alt_text=alt,
                            display_order=order,
                            is_primary=is_prim,
                        )
                    )

                # Reviews
                ratings = []
                for user_name, rating, title, comment in p_info["reviews"]:
                    session.add(
                        Review(
                            product_id=prod.id,
                            user_id=uuid.uuid4(),
                            user_name=user_name,
                            rating=rating,
                            title=title,
                            comment=comment,
                            is_verified_purchase=True,
                            is_approved=True,
                        )
                    )
                    ratings.append(rating)

                if ratings:
                    prod.average_rating = round(sum(ratings) / len(ratings), 1)
                    prod.review_count = len(ratings)

                await session.flush()

            await session.commit()
            logger.info(f"Seeded {len(products_data)} footwear products with {total_variants} SKU variants and heel customizations.")
            logger.info("Product Service database seeding completed successfully.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding Product Service: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_products())
