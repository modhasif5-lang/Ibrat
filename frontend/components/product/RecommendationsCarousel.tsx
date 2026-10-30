"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { ProductCard } from "./ProductCard";
import {
  RecommendationCardDto,
  recommendationService,
} from "@/services/recommendation.service";

interface RecommendationsCarouselProps {
  productId?: string;
  title?: string;
  subtitle?: string;
  type?: "similar" | "popular" | "personalized";
  limit?: number;
}

export function RecommendationsCarousel({
  productId,
  title = "You May Also Admire",
  subtitle = "Curated pairs styled to coordinate seamlessly with your bespoke footwear",
  type = "similar",
  limit = 4,
}: RecommendationsCarouselProps) {
  const [items, setItems] = useState<RecommendationCardDto[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRecommendations() {
      setLoading(true);
      try {
        let results: RecommendationCardDto[] = [];
        if (type === "similar" && productId) {
          results = await recommendationService.getSimilar(productId, limit);
        } else if (type === "personalized") {
          results = await recommendationService.getPersonalized(undefined, limit);
        } else {
          results = await recommendationService.getPopular(limit);
        }
        setItems(results);
      } catch (err) {
        console.error("Failed to load recommendations:", err);
      } finally {
        setLoading(false);
      }
    }
    loadRecommendations();
  }, [productId, type, limit]);

  if (!loading && items.length === 0) return null;

  return (
    <section className="py-16 border-t border-[#E7E2DA] space-y-8">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <span className="text-xs uppercase tracking-widest text-[#C5A880] font-semibold flex items-center gap-1.5 mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Atelier Recommendations</span>
          </span>
          <h2 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            {title}
          </h2>
          {subtitle && (
            <p className="text-sm text-[#8C827A] font-light mt-1 max-w-xl">
              {subtitle}
            </p>
          )}
        </div>

        <Link
          href="/products"
          className="text-xs uppercase tracking-widest text-[#1C1917] hover:text-[#C5A880] font-medium flex items-center gap-1 group self-start sm:self-auto transition-colors"
        >
          <span>View All Footwear</span>
          <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      {/* Grid of Product Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading
          ? Array.from({ length: limit }).map((_, i) => (
              <div
                key={i}
                className="aspect-[4/5] bg-[#F5F2EB] animate-pulse border border-[#E7E2DA]"
              />
            ))
          : items.map((rec) => (
              <div key={rec.id} className="flex flex-col">
                <ProductCard
                  product={{
                    id: rec.id,
                    name: rec.name,
                    slug: rec.slug,
                    base_price: rec.base_price,
                    category_name: rec.category_name || "Footwear",
                    average_rating: rec.average_rating,
                    review_count: rec.review_count,
                    primary_image_url: rec.primary_image_url,
                    is_active: true,
                    material: rec.material,
                    heel_sizes: rec.heel_sizes,
                  }}
                />
                {rec.recommendation_reason && (
                  <div className="mt-2 px-1 text-[11px] text-[#C5A880] flex items-center gap-1 font-medium">
                    <Sparkles className="w-3 h-3 shrink-0" />
                    <span className="truncate">{rec.recommendation_reason}</span>
                  </div>
                )}
              </div>
            ))}
      </div>
    </section>
  );
}
