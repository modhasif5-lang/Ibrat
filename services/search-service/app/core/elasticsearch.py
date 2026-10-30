"""
Elasticsearch client and index mapping configuration for Search Service.
Defines edge_ngram analyzers for autocomplete and structured footwear attributes.
"""

import logging
from typing import Any, Dict, Optional
from elasticsearch import AsyncElasticsearch
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Async Elasticsearch client
es_client = AsyncElasticsearch(
    hosts=[settings.ELASTICSEARCH_URL],
    request_timeout=10,
    max_retries=3,
    retry_on_timeout=True,
)

# Elasticsearch index configuration with custom analyzers for luxury footwear
PRODUCT_INDEX_CONFIG: Dict[str, Any] = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "filter": {
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 20,
                }
            },
            "analyzer": {
                "autocomplete_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "autocomplete_filter"],
                },
                "autocomplete_search_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase"],
                },
            },
        },
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "standard",
                "fields": {
                    "autocomplete": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "autocomplete_search_analyzer",
                    },
                    "keyword": {"type": "keyword"},
                },
            },
            "slug": {"type": "keyword"},
            "description": {"type": "text", "analyzer": "english"},
            "category_id": {"type": "keyword"},
            "category_name": {"type": "keyword"},
            "collection_id": {"type": "keyword"},
            "collection_name": {"type": "keyword"},
            "base_price": {"type": "float"},
            "discount_price": {"type": "float"},
            "effective_price": {"type": "float"},
            "material": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "sole_material": {"type": "keyword"},
            "heel_sizes": {"type": "keyword"},  # ["1 inch", "2 inch", "3 inch"]
            "sizes": {"type": "keyword"},       # ["36", "37", "38", "39", "40", "41"]
            "colors": {"type": "keyword"},      # ["Champagne Gold", "Emerald Velvet"]
            "is_active": {"type": "boolean"},
            "is_featured": {"type": "boolean"},
            "is_new_arrival": {"type": "boolean"},
            "is_in_stock": {"type": "boolean"},
            "average_rating": {"type": "float"},
            "review_count": {"type": "integer"},
            "primary_image_url": {"type": "keyword"},
            "created_at": {"type": "date"},
        }
    },
}


async def init_search_index() -> bool:
    """Initialize or update the products Elasticsearch index."""
    try:
        exists = await es_client.indices.exists(index=settings.ELASTICSEARCH_INDEX)
        if not exists:
            await es_client.indices.create(
                index=settings.ELASTICSEARCH_INDEX,
                body=PRODUCT_INDEX_CONFIG,
            )
            logger.info(f"Created Elasticsearch index: '{settings.ELASTICSEARCH_INDEX}'")
        else:
            logger.info(f"Elasticsearch index '{settings.ELASTICSEARCH_INDEX}' already exists.")
        return True
    except Exception as e:
        logger.warning(f"Could not initialize Elasticsearch index: {e}")
        return False


async def check_es_connection() -> bool:
    """Test Elasticsearch health with cluster ping."""
    try:
        return await es_client.ping()
    except Exception as e:
        logger.warning(f"Elasticsearch health check failed: {e}")
        return False
