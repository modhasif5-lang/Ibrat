"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronRight, ShieldCheck, Truck } from "lucide-react";
import { Product } from "@/types";
import { getAllProducts } from "@/services/product.service";
import { ProductGallery } from "@/components/product/ProductGallery";
import { ProductReviewsSection } from "@/components/product/ProductReviewsSection";
import { RecommendationsCarousel } from "@/components/product/RecommendationsCarousel";
import { ProductOrderBox } from "./ProductOrderBox";

interface ProductDetailClientProps {
  slug: string;
  initialProduct: Product | null;
}

export function ProductDetailClient({ slug, initialProduct }: ProductDetailClientProps) {
  const [product, setProduct] = useState<Product | null>(initialProduct);
  const [loading, setLoading] = useState(!initialProduct);

  useEffect(() => {
    if (!product) {
      // Find product from client-side store (localStorage custom products + fallback catalog)
      const all = getAllProducts();
      const decodedSlug = decodeURIComponent(slug).toLowerCase().trim();
      const found = all.find(
        (p) =>
          p.slug.toLowerCase().trim() === decodedSlug ||
          p.id.toLowerCase().trim() === decodedSlug ||
          p.name.toLowerCase().trim() === decodedSlug
      );

      if (found) {
        setProduct(found);
      }
      setLoading(false);
    }
  }, [slug, product]);

  // Loading Skeleton
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-16 space-y-12 animate-pulse">
        <div className="h-4 w-48 bg-[#E7E2DA]/80 rounded" />
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          <div className="lg:col-span-7 aspect-[4/5] bg-[#E7E2DA]/40 rounded" />
          <div className="lg:col-span-5 space-y-6">
            <div className="h-4 w-32 bg-[#E7E2DA]/80 rounded" />
            <div className="h-8 w-64 bg-[#E7E2DA]/80 rounded" />
            <div className="h-6 w-24 bg-[#E7E2DA]/80 rounded" />
            <div className="h-24 bg-[#E7E2DA]/40 rounded" />
            <div className="h-12 bg-[#E7E2DA]/60 rounded" />
          </div>
        </div>
      </div>
    );
  }

  // Graceful Not Found State (if product truly doesn't exist anywhere)
  if (!product) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-24 text-center space-y-6">
        <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
          Atelier Archive
        </span>
        <h1 className="font-serif-luxury text-3xl sm:text-4xl text-[#1C1917]">
          Silhouette Not Found
        </h1>
        <p className="text-sm text-[#78716C] max-w-md mx-auto font-light leading-relaxed">
          The bespoke footwear model <code className="bg-[#F0EDE8] px-2 py-0.5 text-xs text-[#1C1917]">"{slug}"</code> could not be located in our active Tuscan catalog or your local designs.
        </p>
        <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/products"
            className="w-full sm:w-auto px-6 py-3 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors"
          >
            Explore The Collection
          </Link>
          <Link
            href="/admin/products/new"
            className="w-full sm:w-auto px-6 py-3 border border-[#E7E2DA] hover:border-[#1C1917] text-[#1C1917] text-xs uppercase tracking-widest font-medium transition-colors"
          >
            Create New Silhouette
          </Link>
        </div>
      </div>
    );
  }

  const categoryName = product.category?.name || "Bespoke Footwear";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 sm:py-12 space-y-16">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center gap-2 text-xs text-[#8C827A] uppercase tracking-wider font-light">
        <Link href="/" className="hover:text-[#1C1917] transition-colors">
          Home
        </Link>
        <ChevronRight className="w-3 h-3 text-[#A8A29E]" />
        <Link href="/products" className="hover:text-[#1C1917] transition-colors">
          Footwear
        </Link>
        {product.category && (
          <>
            <ChevronRight className="w-3 h-3 text-[#A8A29E]" />
            <Link
              href={`/categories/${product.category.slug}`}
              className="hover:text-[#1C1917] transition-colors"
            >
              {categoryName}
            </Link>
          </>
        )}
        <ChevronRight className="w-3 h-3 text-[#A8A29E]" />
        <span className="text-[#1C1917] font-medium truncate max-w-[200px]">
          {product.name}
        </span>
      </nav>

      {/* Main PDP Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-start">
        {/* Left Side: Editorial Gallery */}
        <div className="lg:col-span-7 sticky top-28">
          <ProductGallery images={product.images || []} productName={product.name} />
        </div>

        {/* Right Side: Interactive Order Configuration */}
        <div className="lg:col-span-5 space-y-8">
          {/* Header & Title */}
          <div className="space-y-3 border-b border-[#E7E2DA] pb-6">
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-[0.2em] text-[#C5A880] font-semibold">
                {categoryName}
              </span>
              <span className="text-xs text-[#0A4D2E] bg-[#E8F3EC] px-2.5 py-0.5 uppercase tracking-wider font-medium">
                In Stock & Handcrafted
              </span>
            </div>

            <h1 className="font-serif-luxury text-3xl sm:text-4xl text-[#1C1917] font-normal leading-tight">
              {product.name}
            </h1>

            {/* Price & Rating Summary */}
            <div className="flex items-baseline justify-between pt-1">
              <div className="flex items-baseline gap-2">
                <span className="text-2xl sm:text-3xl font-semibold text-[#1C1917]">
                  ₹{typeof product.base_price === "number" ? product.base_price.toLocaleString("en-IN") : product.base_price}
                </span>
                <span className="text-xs text-[#8C827A] font-light">
                  INR (Tax included)
                </span>
              </div>

              {(product.average_rating || 0) > 0 && (
                <a
                  href="#reviews-section"
                  className="text-xs text-[#1C1917] hover:text-[#C5A880] flex items-center gap-1 font-medium transition-colors"
                >
                  <span className="underline">{(product.average_rating || 5).toFixed(1)} Stars</span>
                  <span className="text-[#8C827A]">({product.review_count || 0} reviews)</span>
                </a>
              )}
            </div>

            {product.description && (
              <p className="text-sm text-[#78716C] leading-relaxed font-light pt-2">
                {product.description}
              </p>
            )}
          </div>

          {/* Interactive Client Configuration Box */}
          <ProductOrderBox product={product} />

          {/* Atelier Pillars */}
          <div className="grid grid-cols-2 gap-4 pt-6 border-t border-[#E7E2DA] text-xs text-[#57534E]">
            <div className="flex items-start gap-2.5">
              <Truck className="w-4 h-4 text-[#C5A880] shrink-0 mt-0.5" />
              <div>
                <strong className="block text-[#1C1917] font-medium">Complimentary Global Courier</strong>
                <span className="text-[#8C827A] text-[11px]">2-4 business day tracked delivery</span>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <ShieldCheck className="w-4 h-4 text-[#C5A880] shrink-0 mt-0.5" />
              <div>
                <strong className="block text-[#1C1917] font-medium">Bespoke Fit Guarantee</strong>
                <span className="text-[#8C827A] text-[11px]">Complimentary heel or size adjustments</span>
              </div>
            </div>
          </div>

          {/* Editorial Accordions */}
          <div className="border-t border-[#E7E2DA] divide-y divide-[#E7E2DA] text-xs">
            <details className="py-4 group cursor-pointer" open>
              <summary className="font-medium uppercase tracking-wider text-[#1C1917] flex justify-between items-center list-none">
                <span>Materials & Italian Craftsmanship</span>
                <span className="text-[#8C827A] group-open:rotate-180 transition-transform">↓</span>
              </summary>
              <div className="pt-3 text-[#78716C] space-y-2 leading-relaxed">
                <p>• Upper: {product.material || "100% Full-grain Tuscan leather & Como silk"}</p>
                <p>• Lining: Ultra-soft breathable Italian calfskin</p>
                <p>• Insole: Triple-density memory foam with anatomical metatarsal contouring</p>
                <p>• Outsole: Hand-buffed natural leather sole with non-slip rubberized tip</p>
              </div>
            </details>

            <details className="py-4 group cursor-pointer">
              <summary className="font-medium uppercase tracking-wider text-[#1C1917] flex justify-between items-center list-none">
                <span>The 3 Bespoke Heel Elevations</span>
                <span className="text-[#8C827A] group-open:rotate-180 transition-transform">↓</span>
              </summary>
              <div className="pt-3 text-[#78716C] space-y-2 leading-relaxed">
                <p>• <strong>1 inch (2.5 cm)</strong>: Kitten/Low lift for continuous walking without fatigue.</p>
                <p>• <strong>2 inch (5.0 cm)</strong>: The signature balance for ceremonies and extended dancing.</p>
                <p>• <strong>3 inch (7.5 cm)</strong>: Classic stiletto elevation with reinforced steel arch support.</p>
              </div>
            </details>

            <details className="py-4 group cursor-pointer">
              <summary className="font-medium uppercase tracking-wider text-[#1C1917] flex justify-between items-center list-none">
                <span>Complimentary Delivery & Returns</span>
                <span className="text-[#8C827A] group-open:rotate-180 transition-transform">↓</span>
              </summary>
              <div className="pt-3 text-[#78716C] space-y-1.5 leading-relaxed">
                <p>Orders are dispatched within 24 hours via DHL Express courier in our signature presentation box with dust bags.</p>
                <p>We offer 30-day worldwide complimentary exchanges for sizes or heel adjustments.</p>
              </div>
            </details>
          </div>
        </div>
      </div>

      {/* Customer Reviews Section */}
      <div id="reviews-section">
        <ProductReviewsSection productId={product.id} productName={product.name} />
      </div>

      {/* Coordinated Recommendations */}
      <RecommendationsCarousel
        productId={product.id}
        title="Coordinate Your Wardrobe"
        subtitle="Artisan footwear pairs crafted with matching Tuscan materials and elevations"
      />
    </div>
  );
}
