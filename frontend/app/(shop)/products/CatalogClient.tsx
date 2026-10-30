"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Filter, RotateCcw, Search, SlidersHorizontal, Sparkles, X } from "lucide-react";
import { Category, ProductSummary } from "@/types";
import { ProductCard } from "@/components/product/ProductCard";
import { getAllProducts } from "@/services/product.service";

interface CatalogClientProps {
  initialProducts: ProductSummary[];
  categories: Category[];
  initialQuery?: string;
  initialCategory?: string;
  initialHeel?: string;
  initialSort?: string;
}

export function CatalogClient({
  initialProducts,
  categories,
  initialQuery = "",
  initialCategory = "all",
  initialHeel = "all",
  initialSort = "featured",
}: CatalogClientProps) {
  const router = useRouter();

  const [query, setQuery] = useState(initialQuery);
  const [selectedCategory, setSelectedCategory] = useState(initialCategory || "all");
  const [selectedHeel, setSelectedHeel] = useState(initialHeel || "all");
  const [sortBy, setSortBy] = useState(initialSort || "featured");
  const [productsList, setProductsList] = useState<ProductSummary[]>(initialProducts);

  useEffect(() => {
    // Directly read from localStorage + fallback catalog (no API call needed).
    const all = getAllProducts();
    if (all.length > 0) {
      setProductsList(
        all.map((p) => ({
          id: p.id,
          name: p.name,
          slug: p.slug,
          base_price: p.base_price,
          category_name: p.category?.name || "Bespoke Footwear",
          average_rating: p.average_rating || 5.0,
          review_count: p.review_count || 0,
          primary_image_url: p.images?.[0]?.url || "/media/products/leela-royal-wedge/LeelaKeyHighlightCard.webp",
          is_active: p.is_active ?? true,
        }))
      );
    }
  }, []);

  // Filtering Logic
  const filteredProducts = useMemo(() => {
    return productsList.filter((product) => {
      // Search Query
      if (query.trim()) {
        const q = query.toLowerCase();
        const matchesName = product.name.toLowerCase().includes(q);
        const matchesCat = product.category_name?.toLowerCase().includes(q);
        if (!matchesName && !matchesCat) return false;
      }

      // Category
      if (selectedCategory && selectedCategory !== "all") {
        if (
          product.category_name.toLowerCase() !== selectedCategory.toLowerCase() &&
          !(categories.find((c) => c.slug === selectedCategory)?.name.toLowerCase() === product.category_name.toLowerCase())
        ) {
          return false;
        }
      }

      // Heel Size filter (all products support 1", 2", 3" unless explicitly filtered)
      if (selectedHeel && selectedHeel !== "all") {
        // all Ibrat footwear models support the 3 bespoke heel heights
      }

      return true;
    }).sort((a, b) => {
      if (sortBy === "price_asc") return a.base_price - b.base_price;
      if (sortBy === "price_desc") return b.base_price - a.base_price;
      if (sortBy === "rating") return b.average_rating - a.average_rating;
      return 0; // featured
    });
  }, [productsList, query, selectedCategory, selectedHeel, sortBy, categories]);

  const handleResetFilters = () => {
    setQuery("");
    setSelectedCategory("all");
    setSelectedHeel("all");
    setSortBy("featured");
  };

  const hasActiveFilters =
    query.trim() !== "" ||
    selectedCategory !== "all" ||
    selectedHeel !== "all" ||
    sortBy !== "featured";

  return (
    <div className="space-y-8">
      {/* Filter and Controls Toolbar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 sm:p-6 bg-white border border-[#E7E2DA]">
        {/* Search Input Bar */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-[#8C827A] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search footwear by silhouette or leather..."
            className="w-full pl-10 pr-4 py-2.5 text-xs bg-[#FAF8F5] border border-[#E7E2DA] focus:outline-none focus:border-[#1C1917] placeholder:text-[#8C827A]"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-[#8C827A] hover:text-[#1C1917]"
            >
              Clear
            </button>
          )}
        </div>

        {/* Heel Height Filter Buttons */}
        <div className="flex items-center gap-2 overflow-x-auto no-scrollbar">
          <span className="text-[11px] uppercase tracking-wider text-[#8C827A] font-semibold shrink-0">
            Heel Height:
          </span>
          {["all", "1 inch", "2 inch", "3 inch"].map((heel) => (
            <button
              key={heel}
              type="button"
              onClick={() => setSelectedHeel(heel)}
              className={`px-3 py-1.5 text-xs whitespace-nowrap border transition-colors ${
                selectedHeel === heel
                  ? "bg-[#1C1917] text-white border-[#1C1917] font-medium"
                  : "bg-white text-[#57534E] border-[#E7E2DA] hover:border-[#1C1917]"
              }`}
            >
              {heel === "all" ? "All Heights" : heel}
            </button>
          ))}
        </div>

        {/* Sort Dropdown */}
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[11px] uppercase tracking-wider text-[#8C827A] font-semibold">
            Sort:
          </span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 text-xs bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
          >
            <option value="featured">Featured Atelier</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="rating">Client Rating</option>
          </select>
        </div>
      </div>

      {/* Category Pills Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 no-scrollbar">
        <button
          type="button"
          onClick={() => setSelectedCategory("all")}
          className={`px-4 py-2 text-xs uppercase tracking-widest whitespace-nowrap transition-colors ${
            selectedCategory === "all"
              ? "bg-[#C5A880] text-[#1C1917] font-semibold"
              : "bg-white text-[#57534E] border border-[#E7E2DA] hover:border-[#1C1917]"
          }`}
        >
          All Categories ({initialProducts.length})
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            type="button"
            onClick={() => setSelectedCategory(cat.name)}
            className={`px-4 py-2 text-xs uppercase tracking-widest whitespace-nowrap transition-colors ${
              selectedCategory.toLowerCase() === cat.name.toLowerCase()
                ? "bg-[#C5A880] text-[#1C1917] font-semibold"
                : "bg-white text-[#57534E] border border-[#E7E2DA] hover:border-[#1C1917]"
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Active Filters Summary & Count */}
      <div className="flex items-center justify-between text-xs text-[#8C827A] border-b border-[#E7E2DA] pb-3">
        <div>
          Showing <span className="font-semibold text-[#1C1917]">{filteredProducts.length}</span>{" "}
          {filteredProducts.length === 1 ? "silhouette" : "silhouettes"}
        </div>

        {hasActiveFilters && (
          <button
            type="button"
            onClick={handleResetFilters}
            className="flex items-center gap-1.5 text-xs text-[#1C1917] hover:text-[#C5A880] font-medium transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset All Filters</span>
          </button>
        )}
      </div>

      {/* Products Grid */}
      {filteredProducts.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 sm:gap-8">
          {filteredProducts.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      ) : (
        /* Empty State */
        <div className="py-20 text-center space-y-4 bg-white border border-[#E7E2DA] p-8 max-w-xl mx-auto">
          <p className="font-serif-luxury text-2xl text-[#1C1917]">
            No footwear matches your criteria
          </p>
          <p className="text-xs text-[#8C827A] leading-relaxed">
            Try adjusting your heel height or category filters, or explore our full
            bridal and evening collection.
          </p>
          <button
            type="button"
            onClick={handleResetFilters}
            className="px-6 py-2.5 bg-[#1C1917] text-white text-xs uppercase tracking-widest hover:bg-[#C5A880] transition-colors"
          >
            Reset Filters
          </button>
        </div>
      )}
    </div>
  );
}
