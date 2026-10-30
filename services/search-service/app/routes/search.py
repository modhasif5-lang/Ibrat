"""
Search Service API Routes.
Exposes full-text search, multi-faceted filtering, autocomplete, and index sync.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, status

from app.core.elasticsearch import init_search_index
from app.schemas.search import (
    AutocompleteResponse,
    ProductDocument,
    SearchResultResponse,
)
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "",
    response_model=SearchResultResponse,
    summary="Full-text footwear search with multi-attribute facets and filtering",
)
async def search_footwear(
    q: Optional[str] = Query(None, description="Search terms (e.g. 'satin pump', 'ankle strap', 'velvet')"),
    category: Optional[str] = Query(None, description="Category name filter (e.g. 'Bridal & Evening')"),
    collection: Optional[str] = Query(None, description="Collection name filter (e.g. 'Bridal Couture Edit')"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    heel_size: Optional[str] = Query(None, description="Heel customization filter ('1 inch', '2 inch', '3 inch')"),
    size: Optional[str] = Query(None, description="Shoe size filter ('36', '37', '38', etc.)"),
    color: Optional[str] = Query(None, description="Shoe color name (e.g. 'Champagne Gold')"),
    in_stock_only: Optional[bool] = Query(None, description="Show only products currently in stock"),
    sort_by: str = Query("relevance", pattern="^(relevance|price_asc|price_desc|rating|newest)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    Search the footwear catalog.
    Returns matching products along with faceted aggregated counts for categories, heel heights, sizes, and colors.
    """
    svc = SearchService()
    return await svc.search_products(
        q=q,
        category=category,
        collection=collection,
        min_price=min_price,
        max_price=max_price,
        heel_size=heel_size,
        size=size,
        color=color,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/autocomplete",
    response_model=AutocompleteResponse,
    summary="Fast search bar autocomplete suggestions",
)
async def autocomplete(
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(8, ge=1, le=20),
):
    """Instant search suggestions as customer types into the search bar."""
    svc = SearchService()
    return await svc.autocomplete(q=q, limit=limit)


# ============================================================
# Index Management & Webhook Synchronization
# ============================================================

@router.post(
    "/index/init",
    status_code=status.HTTP_200_OK,
    summary="Initialize or update Elasticsearch index mapping",
)
async def initialize_index():
    """Create or verify the Elasticsearch index mapping with edge_ngram analyzers."""
    success = await init_search_index()
    return {"success": success, "message": "Index initialized."}


@router.post(
    "/index/product",
    status_code=status.HTTP_200_OK,
    summary="Index or update a single product document",
)
async def index_product(doc: ProductDocument):
    """Index or update product document in Elasticsearch."""
    svc = SearchService()
    success = await svc.index_product(doc)
    return {"success": success, "id": doc.id}


@router.post(
    "/index/bulk",
    status_code=status.HTTP_200_OK,
    summary="Bulk index a list of footwear product documents",
)
async def bulk_index_products(docs: List[ProductDocument]):
    """Bulk load multiple product documents into Elasticsearch."""
    svc = SearchService()
    count = await svc.bulk_index_products(docs)
    return {"indexed_count": count}


@router.delete(
    "/index/product/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete product document from search index",
)
async def delete_product(product_id: str):
    """Remove product from search index."""
    svc = SearchService()
    success = await svc.delete_product(product_id)
    return {"success": success, "id": product_id}
