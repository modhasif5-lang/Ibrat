"use client";

import React, { useEffect, useState } from "react";
import { ProductSummary } from "@/types";
import { ProductCard } from "@/components/product/ProductCard";
import { getAllProducts } from "@/services/product.service";

interface FeaturedProductsSectionProps {
  initialProducts: ProductSummary[];
}

export function FeaturedProductsSection({ initialProducts }: FeaturedProductsSectionProps) {
  const [products, setProducts] = useState<ProductSummary[]>(initialProducts);

  useEffect(() => {
    // Directly read from localStorage + fallback products (no API call needed).
    // This picks up any products created via the Admin console instantly.
    const all = getAllProducts();
    if (all.length > 0) {
      setProducts(
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

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
