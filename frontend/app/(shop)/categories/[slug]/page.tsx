import React from "react";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import { productService } from "@/services/product.service";
import { ProductCard } from "@/components/product/ProductCard";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function CategoryPage({ params }: PageProps) {
  const { slug } = await params;
  const categories = await productService.getCategories();
  const category = categories.find((c) => c.slug === slug);

  if (!category) {
    notFound();
  }

  const { items: allProducts } = await productService.getProducts();
  const categoryProducts = allProducts.filter(
    (p) => p.category_name.toLowerCase() === category.name.toLowerCase()
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 sm:py-16 space-y-12">
      {/* Category Editorial Hero */}
      <div className="space-y-4 max-w-3xl">
        <Link
          href="/products"
          className="inline-flex items-center gap-1.5 text-xs uppercase tracking-widest text-[#8C827A] hover:text-[#1C1917] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to All Footwear</span>
        </Link>

        <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
          Curated Category
        </span>

        <h1 className="font-serif-luxury text-3xl sm:text-5xl text-[#1C1917]">
          {category.name}
        </h1>

        <p className="text-sm text-[#78716C] leading-relaxed font-light">
          {category.description ||
            `Exquisite Italian handcrafted designs in ${category.name.toLowerCase()}. Customizable with your choice of 1", 2", or 3" heel elevation.`}
        </p>

        <div className="inline-flex items-center gap-2 pt-2 text-xs text-[#1C1917] font-medium">
          <Sparkles className="w-3.5 h-3.5 text-[#C5A880]" />
          <span>{categoryProducts.length} Silhouettes Available</span>
        </div>
      </div>

      {/* Footwear Grid */}
      {categoryProducts.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
          {categoryProducts.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      ) : (
        <div className="py-16 text-center text-sm text-[#8C827A] bg-white border border-[#E7E2DA]">
          Currently crafting new additions for {category.name}. Check back shortly.
        </div>
      )}
    </div>
  );
}
