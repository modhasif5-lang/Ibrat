"""
Search Service Business Logic Layer.
Orchestrates full-text queries, multi-attribute filtering, faceted aggregations,
autocomplete suggestions, and document indexing in Elasticsearch.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.config import get_settings
from app.core.elasticsearch import es_client, init_search_index
from app.schemas.search import (
    AutocompleteResponse,
    AutocompleteSuggestion,
    FacetBucket,
    PriceStatsFacet,
    ProductDocument,
    SearchFacets,
    SearchResultResponse,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchService:
    """Core domain service for footwear search and autocomplete."""

    def __init__(self):
        self.index_name = settings.ELASTICSEARCH_INDEX

    # ============================================================
    # Full-Text Search with Facets and Filtering
    # ============================================================

    async def search_products(
        self,
        q: Optional[str] = None,
        category: Optional[str] = None,
        collection: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        heel_size: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        in_stock_only: Optional[bool] = None,
        sort_by: str = "relevance",
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResultResponse:
        """Execute full-text fuzzy query with multi-attribute faceted filters."""
        from_offset = (page - 1) * page_size

        must_clauses: List[Dict[str, Any]] = []
        filter_clauses: List[Dict[str, Any]] = [
            {"term": {"is_active": True}}
        ]

        # 1. Full-text search or match_all
        if q and q.strip():
            query_str = q.strip()
            must_clauses.append({
                "multi_match": {
                    "query": query_str,
                    "fields": [
                        "name^3",
                        "name.autocomplete^2",
                        "description",
                        "material^1.5",
                        "category_name^2",
                        "collection_name^1.5",
                    ],
                    "fuzziness": "AUTO",
                }
            })
        else:
            must_clauses.append({"match_all": {}})

        # 2. Attribute Filters
        if category:
            filter_clauses.append({"term": {"category_name": category}})
        if collection:
            filter_clauses.append({"term": {"collection_name": collection}})
        if heel_size:
            filter_clauses.append({"term": {"heel_sizes": heel_size}})
        if size:
            filter_clauses.append({"term": {"sizes": size}})
        if color:
            filter_clauses.append({"term": {"colors": color}})
        if in_stock_only is True:
            filter_clauses.append({"term": {"is_in_stock": True}})

        # Price range filter
        price_range: Dict[str, Any] = {}
        if min_price is not None:
            price_range["gte"] = min_price
        if max_price is not None:
            price_range["lte"] = max_price
        if price_range:
            filter_clauses.append({"range": {"effective_price": price_range}})

        # 3. Sorting
        sort_config: List[Any] = []
        if sort_by == "price_asc":
            sort_config.append({"effective_price": {"order": "asc"}})
        elif sort_by == "price_desc":
            sort_config.append({"effective_price": {"order": "desc"}})
        elif sort_by == "rating":
            sort_config.append({"average_rating": {"order": "desc"}})
        elif sort_by == "newest":
            sort_config.append({"created_at": {"order": "desc", "unmapped_type": "date"}})
        else:  # relevance
            if q and q.strip():
                sort_config.append("_score")
            sort_config.append({"average_rating": {"order": "desc"}})

        # 4. Faceted Aggregations
        aggregations: Dict[str, Any] = {
            "categories": {"terms": {"field": "category_name", "size": 20}},
            "collections": {"terms": {"field": "collection_name", "size": 20}},
            "heel_sizes": {"terms": {"field": "heel_sizes", "size": 10}},
            "colors": {"terms": {"field": "colors", "size": 20}},
            "sizes": {"terms": {"field": "sizes", "size": 20}},
            "price_stats": {"stats": {"field": "effective_price"}},
        }

        body = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses,
                }
            },
            "aggs": aggregations,
            "sort": sort_config,
            "from": from_offset,
            "size": page_size,
        }

        try:
            response = await es_client.search(index=self.index_name, body=body)
        except Exception as e:
            logger.warning(f"Elasticsearch search failed or unreachable: {e}")
            # Graceful fallback returning empty result instead of crashing
            return SearchResultResponse(
                total=0,
                page=page,
                size=page_size,
                items=[],
                facets=SearchFacets(),
            )

        # Parse documents
        hits = response.get("hits", {})
        total_count = hits.get("total", {}).get("value", 0)
        items: List[ProductDocument] = []
        for hit in hits.get("hits", []):
            source = hit.get("_source", {})
            source["id"] = hit.get("_id", source.get("id"))
            items.append(ProductDocument.model_validate(source))

        # Parse Aggregations into Facets
        aggs = response.get("aggregations", {})
        facets = SearchFacets(
            categories=[FacetBucket(key=b["key"], count=b["doc_count"]) for b in aggs.get("categories", {}).get("buckets", [])],
            collections=[FacetBucket(key=b["key"], count=b["doc_count"]) for b in aggs.get("collections", {}).get("buckets", [])],
            heel_sizes=[FacetBucket(key=b["key"], count=b["doc_count"]) for b in aggs.get("heel_sizes", {}).get("buckets", [])],
            colors=[FacetBucket(key=b["key"], count=b["doc_count"]) for b in aggs.get("colors", {}).get("buckets", [])],
            sizes=[FacetBucket(key=b["key"], count=b["doc_count"]) for b in aggs.get("sizes", {}).get("buckets", [])],
        )

        p_stats = aggs.get("price_stats", {})
        if p_stats and p_stats.get("count", 0) > 0:
            facets.price_stats = PriceStatsFacet(
                min=round(p_stats.get("min", 0.0), 2),
                max=round(p_stats.get("max", 0.0), 2),
                avg=round(p_stats.get("avg", 0.0), 2),
            )

        return SearchResultResponse(
            total=total_count,
            page=page,
            size=page_size,
            items=items,
            facets=facets,
        )

    # ============================================================
    # Autocomplete Suggestions
    # ============================================================

    async def autocomplete(self, q: str, limit: int = 8) -> AutocompleteResponse:
        """Fast prefix edge_ngram query for immediate search bar suggestions."""
        if not q or not q.strip():
            return AutocompleteResponse(query=q, suggestions=[])

        query_str = q.strip()
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "name.autocomplete": {
                                    "query": query_str,
                                    "operator": "and",
                                }
                            }
                        }
                    ],
                    "filter": [{"term": {"is_active": True}}],
                }
            },
            "_source": ["id", "name", "slug", "category_name", "effective_price", "primary_image_url"],
            "size": limit,
        }

        try:
            response = await es_client.search(index=self.index_name, body=body)
            suggestions: List[AutocompleteSuggestion] = []
            for hit in response.get("hits", {}).get("hits", []):
                src = hit.get("_source", {})
                suggestions.append(
                    AutocompleteSuggestion(
                        id=str(hit.get("_id", src.get("id"))),
                        name=src.get("name", ""),
                        slug=src.get("slug", ""),
                        category_name=src.get("category_name"),
                        effective_price=src.get("effective_price", 0.0),
                        primary_image_url=src.get("primary_image_url"),
                    )
                )
            return AutocompleteResponse(query=query_str, suggestions=suggestions)
        except Exception as e:
            logger.warning(f"Autocomplete query failed: {e}")
            return AutocompleteResponse(query=query_str, suggestions=[])

    # ============================================================
    # Document Indexing Operations
    # ============================================================

    async def index_product(self, doc: ProductDocument) -> bool:
        """Index or update a single product document."""
        try:
            body = doc.model_dump(mode="json")
            product_id = body.pop("id")
            await es_client.index(
                index=self.index_name,
                id=product_id,
                body=body,
                refresh="wait_for",
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index product document {doc.id}: {e}")
            return False

    async def bulk_index_products(self, docs: List[ProductDocument]) -> int:
        """Bulk index a collection of footwear products."""
        if not docs:
            return 0
        operations = []
        for doc in docs:
            body = doc.model_dump(mode="json")
            doc_id = body.pop("id")
            operations.append({"index": {"_index": self.index_name, "_id": doc_id}})
            operations.append(body)

        try:
            res = await es_client.bulk(operations=operations, refresh="wait_for")
            if res.get("errors"):
                logger.warning("Bulk indexing reported some document errors.")
            return len(docs)
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return 0

    async def delete_product(self, product_id: str) -> bool:
        """Delete document from search index."""
        try:
            await es_client.delete(index=self.index_name, id=product_id, refresh="wait_for")
            return True
        except Exception as e:
            logger.warning(f"Could not delete product {product_id} from Elasticsearch: {e}")
            return False

    async def update_product_partial(self, product_id: str, fields: Dict[str, Any]) -> bool:
        """Update specific fields of an existing product document in Elasticsearch."""
        try:
            await es_client.update(
                index=self.index_name,
                id=product_id,
                body={"doc": fields},
                refresh="wait_for",
            )
            return True
        except Exception as e:
            logger.warning(f"Could not partially update product {product_id} in Elasticsearch: {e}")
            return False

