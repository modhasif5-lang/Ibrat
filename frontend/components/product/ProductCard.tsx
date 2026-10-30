"use client";

import React, { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Heart, ShoppingBag, Sparkles, Star } from "lucide-react";
import { useStore } from "@/context/StoreContext";
import { ProductSummary } from "@/types";

interface ProductCardProps {
  product: ProductSummary & {
    material?: string;
    heel_sizes?: string[];
  };
}

export function ProductCard({ product }: ProductCardProps) {
  const { isInWishlist, toggleWishlist, addToCart, openCart } = useStore();
  const isWishlisted = isInWishlist(product.id);
  const [isHovered, setIsHovered] = useState(false);
  const [selectedHeel, setSelectedHeel] = useState<string>("2 inch");

  // Fallback image url if missing
  const imageUrl =
    product.primary_image_url ||
    "/media/products/aurelia-champagne-main.webp";

  const handleQuickAdd = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    addToCart({
      id: `cart-${product.id}-${Date.now()}`,
      productId: product.id,
      variantId: `var-${product.id}-default`,
      name: product.name,
      slug: product.slug,
      price: product.base_price,
      quantity: 1,
      heelSize: selectedHeel,
      size: "EU 38",
      color: "Classic",
      imageUrl: imageUrl,
    });
    openCart();
  };

  const handleWishlistToggle = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    toggleWishlist(product.id);
  };

  return (
    <div
      className="group relative flex flex-col bg-white border border-[#E7E2DA] hover:border-[#C5A880] transition-all duration-300"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Top Image Stage */}
      <div className="relative aspect-[4/5] bg-[#F5F2EB] overflow-hidden">
        <Link href={`/products/${product.slug}`} className="block w-full h-full">
          <img
            src={imageUrl}
            alt={product.name}
            className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
            onError={(e) => {
              (e.target as HTMLImageElement).src =
                "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=800&q=80";
            }}
          />
        </Link>

        {/* Top Badges */}
        <div className="absolute top-3 left-3 flex flex-col gap-1 pointer-events-none">
          <span className="bg-[#1C1917]/90 text-white text-[9px] uppercase tracking-widest px-2 py-0.5 font-medium backdrop-blur-xs">
            1" • 2" • 3" Heel
          </span>
        </div>

        {/* Wishlist Button */}
        <button
          type="button"
          onClick={handleWishlistToggle}
          className={`absolute top-3 right-3 p-2 rounded-full transition-all duration-200 z-10 ${
            isWishlisted
              ? "bg-[#1C1917] text-[#C5A880] shadow-md"
              : "bg-white/80 text-[#1C1917] hover:bg-white hover:text-[#C5A880] backdrop-blur-xs"
          }`}
          aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
        >
          <Heart className={`w-4 h-4 ${isWishlisted ? "fill-current" : ""}`} />
        </button>

        {/* Quick Add Overlay on Hover */}
        <div
          className={`absolute bottom-0 inset-x-0 p-3 bg-gradient-to-t from-black/80 via-black/40 to-transparent transition-all duration-300 flex flex-col gap-2 ${
            isHovered ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4 pointer-events-none"
          }`}
        >
          {/* Heel Selection Chips */}
          <div className="flex items-center justify-between text-white text-[10px]">
            <span className="font-light tracking-wider">Choose Heel:</span>
            <div className="flex gap-1.5">
              {(["1 inch", "2 inch", "3 inch"] as const).map((h) => (
                <button
                  key={h}
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setSelectedHeel(h);
                  }}
                  className={`px-1.5 py-0.5 border text-[9px] transition-colors ${
                    selectedHeel === h
                      ? "bg-[#C5A880] border-[#C5A880] text-[#1C1917] font-semibold"
                      : "border-white/50 text-white hover:border-white"
                  }`}
                >
                  {h.split(" ")[0]}"
                </button>
              ))}
            </div>
          </div>

          <button
            type="button"
            onClick={handleQuickAdd}
            className="w-full py-2 bg-white text-[#1C1917] hover:bg-[#C5A880] hover:text-white transition-colors text-xs uppercase tracking-widest font-medium flex items-center justify-center gap-1.5"
          >
            <ShoppingBag className="w-3.5 h-3.5" />
            <span>Quick Add • {selectedHeel}</span>
          </button>
        </div>
      </div>

      {/* Information Section */}
      <div className="p-4 flex flex-col flex-1 justify-between bg-white">
        <div className="space-y-1">
          <div className="flex items-center justify-between text-[11px] text-[#8C827A]">
            <span className="uppercase tracking-widest font-light">{product.category_name}</span>
            {product.average_rating > 0 && (
              <span className="flex items-center gap-1 text-[#1C1917] font-medium">
                <Star className="w-3 h-3 fill-[#C5A880] text-[#C5A880]" />
                <span>{product.average_rating.toFixed(1)}</span>
                <span className="text-[#8C827A]">({product.review_count})</span>
              </span>
            )}
          </div>

          <h3 className="font-serif-luxury text-base text-[#1C1917] group-hover:text-[#C5A880] transition-colors leading-snug line-clamp-1">
            <Link href={`/products/${product.slug}`}>{product.name}</Link>
          </h3>
        </div>

        <div className="mt-3 pt-3 border-t border-[#F0EDE8] flex items-center justify-between">
          <span className="text-sm font-semibold text-[#1C1917] tracking-tight">
            ₹{typeof product.base_price === "number" ? product.base_price.toLocaleString("en-IN") : product.base_price}
          </span>
          <span className="text-[10px] uppercase tracking-widest text-[#C5A880] font-medium">
            Bespoke Heel
          </span>
        </div>
      </div>
    </div>
  );
}
