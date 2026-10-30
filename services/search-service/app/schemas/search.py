"""
Pydantic validation schemas for Search Service.
Covers search documents, multi-attribute filter parameters, facets, and autocomplete.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Search Index Product Document Schema
# ============================================================

class ProductDocument(BaseModel):
    """Product representation indexed in Elasticsearch."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: str
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    collection_id: Optional[str] = None
    collection_name: Optional[str] = None
    base_price: float
    discount_price: Optional[float] = None
    effective_price: float
    material: Optional[str] = None
    sole_material: Optional[str] = None
    heel_sizes: List[str] = []   # ["1 inch", "2 inch", "3 inch"]
    sizes: List[str] = []        # ["36", "37", "38", "39", "40", "41"]
    colors: List[str] = []       # ["Champagne Gold", "Emerald Velvet"]
    is_active: bool = True
    is_featured: bool = False
    is_new_arrival: bool = False
    is_in_stock: bool = True
    average_rating: float = 0.0
    review_count: int = 0
    primary_image_url: Optional[str] = None
    created_at: Optional[datetime] = None


# ============================================================
# Search Facets & Aggregations
# ============================================================

class FacetBucket(BaseModel):
    key: str
    count: int


class PriceStatsFacet(BaseModel):
    min: float
    max: float
    avg: float


class SearchFacets(BaseModel):
    categories: List[FacetBucket] = []
    collections: List[FacetBucket] = []
    heel_sizes: List[FacetBucket] = []
    colors: List[FacetBucket] = []
    sizes: List[FacetBucket] = []
    price_stats: Optional[PriceStatsFacet] = None


class SearchResultResponse(BaseModel):
    """Full search response including paginated matches and calculated facets."""
    total: int
    page: int
    size: int
    items: List[ProductDocument]
    facets: SearchFacets


# ============================================================
# Autocomplete Schemas
# ============================================================

class AutocompleteSuggestion(BaseModel):
    id: str
    name: str
    slug: str
    category_name: Optional[str] = None
    effective_price: float
    primary_image_url: Optional[str] = None


class AutocompleteResponse(BaseModel):
    query: str
    suggestions: List[AutocompleteSuggestion]
