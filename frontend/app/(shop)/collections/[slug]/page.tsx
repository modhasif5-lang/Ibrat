import React from "react";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import { productService } from "@/services/product.service";
import { ProductCard } from "@/components/product/ProductCard";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function CollectionPage({ params }: PageProps) {
  const { slug } = await params;
  const collections = await productService.getCollections();
  const collection = collections.find((c) => c.slug === slug);

  if (!collection) {
    notFound();
  }

  const { items: allProducts } = await productService.getProducts();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 sm:py-16 space-y-12">
      {/* Collection Editorial Hero */}
      <div className="space-y-4 max-w-3xl">
        <Link
          href="/products"
          className="inline-flex items-center gap-1.5 text-xs uppercase tracking-widest text-[#8C827A] hover:text-[#1C1917] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to All Footwear</span>
        </Link>

        <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
          Editorial Line
        </span>

        <h1 className="font-serif-luxury text-3xl sm:text-5xl text-[#1C1917]">
          {collection.name}
        </h1>

        <p className="text-sm text-[#78716C] leading-relaxed font-light">
          {collection.description ||
            `A bespoke seasonal capsule celebrating refined elegance and architectural elevations.`}
        </p>

        <div className="inline-flex items-center gap-2 pt-2 text-xs text-[#1C1917] font-medium">
          <Sparkles className="w-3.5 h-3.5 text-[#C5A880]" />
          <span>Complimentary 1", 2", and 3" Heel Customization Included</span>
        </div>
      </div>

      {/* Footwear Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
        {allProducts.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
