"""
Search Service Seed Script.
Populates Elasticsearch index with rich footwear documents matching the product catalog.
Run via: python -m app.seed
"""

import asyncio
import logging
from datetime import datetime, timezone

from app.core.elasticsearch import es_client, init_search_index
from app.schemas.search import ProductDocument
from app.services.search_service import SearchService

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("seed-search-service")

INITIAL_FOOTWEAR_DOCUMENTS = [
    ProductDocument(
        id="a1000000-0000-0000-0000-000000000001",
        name="Aurelia Crystal Satin Pump",
        slug="aurelia-crystal-satin-pump",
        description="Hand-constructed in Tuscany from lustrous Italian silk satin, the Aurelia pump features an ankle-framing crystal brooch and our signature shock-absorbing memory foam footbed. Perfectly balanced for all-day celebrations.",
        category_id="c1000000-0000-0000-0000-000000000004",
        category_name="Bridal & Evening",
        collection_id="l1000000-0000-0000-0000-000000000001",
        collection_name="Bridal Couture Edit",
        base_price=380.0,
        discount_price=None,
        effective_price=380.0,
        material="Italian Silk Satin & Austrian Crystal Brooch",
        sole_material="Genuine Brushed Italian Leather",
        heel_sizes=["1 inch", "2 inch", "3 inch"],
        sizes=["36", "37", "38", "39", "40"],
        colors=["Champagne Gold", "Emerald Velvet"],
        is_active=True,
        is_featured=True,
        is_new_arrival=True,
        is_in_stock=True,
        average_rating=5.0,
        review_count=2,
        primary_image_url="/api/uploads/products/aurelia-champagne-main.webp",
        created_at=datetime.now(timezone.utc),
    ),
    ProductDocument(
        id="a1000000-0000-0000-0000-000000000002",
        name="Seraphina Nappa Ankle-Strap Heel",
        slug="seraphina-nappa-ankle-strap-heel",
        description="A study in sculptural minimalism. Handcrafted from butter-soft Italian nappa leather with a delicate buckled ankle strap that elongates the leg without friction.",
        category_id="c1000000-0000-0000-0000-000000000001",
        category_name="Stilettos & High Heels",
        collection_id="l1000000-0000-0000-0000-000000000003",
        collection_name="Midnight Atelier",
        base_price=340.0,
        discount_price=295.0,
        effective_price=295.0,
        material="100% Full-Grain Italian Nappa Leather",
        sole_material="Non-slip treated leather sole",
        heel_sizes=["1 inch", "2 inch", "3 inch"],
        sizes=["36", "37", "38", "39"],
        colors=["Midnight Black", "Nude Beige"],
        is_active=True,
        is_featured=True,
        is_new_arrival=False,
        is_in_stock=True,
        average_rating=5.0,
        review_count=1,
        primary_image_url="/api/uploads/products/seraphina-black-main.webp",
        created_at=datetime.now(timezone.utc),
    ),
    ProductDocument(
        id="a1000000-0000-0000-0000-000000000003",
        name="Valentina Embellished Velvet Mule",
        slug="valentina-embellished-velvet-mule",
        description="Royal evening mules in jewel-toned silk velvet, decorated with intricate tonal micro-beading and a sculpted flared kitten heel.",
        category_id="c1000000-0000-0000-0000-000000000005",
        category_name="Mules & Slides",
        collection_id="l1000000-0000-0000-0000-000000000003",
        collection_name="Midnight Atelier",
        base_price=295.0,
        discount_price=None,
        effective_price=295.0,
        material="Silk Velvet with Hand-applied Glass Beads",
        sole_material="Genuine Leather",
        heel_sizes=["1 inch", "2 inch", "3 inch"],
        sizes=["37", "38", "39"],
        colors=["Royal Navy", "Ruby Red"],
        is_active=True,
        is_featured=False,
        is_new_arrival=True,
        is_in_stock=True,
        average_rating=4.0,
        review_count=1,
        primary_image_url="/api/uploads/products/valentina-navy-main.webp",
        created_at=datetime.now(timezone.utc),
    ),
    ProductDocument(
        id="a1000000-0000-0000-0000-000000000004",
        name="Celeste Pointed Toe Flat",
        slug="celeste-pointed-toe-flat",
        description="Refined everyday luxury. Crafted with an elongated almond-pointed toe, hidden arch pillow, and a whisper of polished gold along the low stacked heel.",
        category_id="c1000000-0000-0000-0000-000000000003",
        category_name="Luxury Flats & Loafers",
        collection_id="l1000000-0000-0000-0000-000000000002",
        collection_name="Riviera Summer Luxe",
        base_price=260.0,
        discount_price=None,
        effective_price=260.0,
        material="Glove Calf Leather & 14k Gold-dipped Heel Accent",
        sole_material="Flexible Rubberized Leather Sole",
        heel_sizes=["1 inch"],
        sizes=["36", "37", "38", "39"],
        colors=["Ivory Pearl", "Metallic Rose"],
        is_active=True,
        is_featured=True,
        is_new_arrival=True,
        is_in_stock=True,
        average_rating=5.0,
        review_count=1,
        primary_image_url="/api/uploads/products/celeste-ivory-main.webp",
        created_at=datetime.now(timezone.utc),
    ),
    ProductDocument(
        id="a1000000-0000-0000-0000-000000000005",
        name="Camilla Pearl Slingback",
        slug="camilla-pearl-slingback",
        description="Ethereal French moire silk pump with an elasticated slingback strap and graduated natural freshwater pearls encircling the vamp.",
        category_id="c1000000-0000-0000-0000-000000000004",
        category_name="Bridal & Evening",
        collection_id="l1000000-0000-0000-0000-000000000001",
        collection_name="Bridal Couture Edit",
        base_price=350.0,
        discount_price=None,
        effective_price=350.0,
        material="French Moire Silk with Cultured Freshwater Pearls",
        sole_material="Leather sole with slip-resistant insert",
        heel_sizes=["1 inch", "2 inch", "3 inch"],
        sizes=["36", "37", "38", "39"],
        colors=["Bridal White", "Blush Pink"],
        is_active=True,
        is_featured=True,
        is_new_arrival=True,
        is_in_stock=True,
        average_rating=5.0,
        review_count=1,
        primary_image_url="/api/uploads/products/camilla-white-main.webp",
        created_at=datetime.now(timezone.utc),
    ),
]


async def seed_search():
    """Seed search index."""
    logger.info("Initializing search index...")
    await init_search_index()

    svc = SearchService()
    logger.info("Bulk indexing footwear documents into Elasticsearch...")
    count = await svc.bulk_index_products(INITIAL_FOOTWEAR_DOCUMENTS)
    logger.info(f"Seeded {count} footwear documents in Elasticsearch.")
    await es_client.close()


if __name__ == "__main__":
    asyncio.run(seed_search())
