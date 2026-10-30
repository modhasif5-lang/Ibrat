"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Heart, ShoppingBag, Sparkles, Trash2 } from "lucide-react";
import { useStore } from "@/context/StoreContext";
import { FALLBACK_PRODUCTS } from "@/services/product.service";
import { ProductSummary } from "@/types";
import { ProductCard } from "@/components/product/ProductCard";

export default function WishlistPage() {
  const { wishlist, toggleWishlist, addToCart, openCart } = useStore();
  const [items, setItems] = useState<ProductSummary[]>([]);

  useEffect(() => {
    // Map wishlist IDs to products
    const saved = FALLBACK_PRODUCTS.filter((p) => wishlist.includes(p.id)).map(
      (p) => ({
        id: p.id,
        name: p.name,
        slug: p.slug,
        base_price: p.base_price,
        category_name: p.category.name,
        average_rating: p.average_rating,
        review_count: p.review_count,
        primary_image_url: p.images[0]?.url,
        is_active: p.is_active,
      })
    );
    setItems(saved);
  }, [wishlist]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 sm:py-16 space-y-12">
      {/* Header */}
      <div className="text-center max-w-xl mx-auto space-y-3">
        <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
          Saved Favorites
        </span>
        <h1 className="font-serif-luxury text-3xl sm:text-5xl text-[#1C1917]">
          Your Atelier Wishlist
        </h1>
        <p className="text-sm text-[#78716C] font-light">
          Your curated selection of Italian footwear, ready for heel customization and sizing.
        </p>
      </div>

      {items.length === 0 ? (
        <div className="max-w-md mx-auto py-16 text-center space-y-6 bg-white border border-[#E7E2DA] p-8">
          <div className="w-14 h-14 mx-auto rounded-full bg-[#FAF8F5] border border-[#E7E2DA] flex items-center justify-center text-[#8C827A]">
            <Heart className="w-6 h-6 stroke-1" />
          </div>
          <h2 className="font-serif-luxury text-2xl text-[#1C1917]">
            No footwear saved yet
          </h2>
          <p className="text-xs text-[#8C827A] leading-relaxed">
            Click the heart icon on any silhouette to curate your dream wardrobe
            before selecting your bespoke heel elevation.
          </p>
          <Link
            href="/products"
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors"
          >
            <span>Explore Collection</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
          {items.map((product) => (
            <div key={product.id} className="space-y-3">
              <ProductCard product={product} />
              <button
                type="button"
                onClick={() => toggleWishlist(product.id)}
                className="w-full py-2 text-xs text-[#8C827A] hover:text-red-700 border border-[#E7E2DA] hover:bg-[#FAF8F5] flex items-center justify-center gap-1.5 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Remove from Wishlist</span>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
