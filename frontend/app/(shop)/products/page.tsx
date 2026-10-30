import React from "react";
import { productService } from "@/services/product.service";
import { CatalogClient } from "./CatalogClient";

interface PageProps {
  searchParams: Promise<{
    q?: string;
    category?: string;
    heel_size?: string;
    sort_by?: string;
  }>;
}

export default async function ProductsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const initialCategory = params.category;
  const initialHeel = params.heel_size;
  const initialQuery = params.q;
  const initialSort = params.sort_by;

  const { items: products } = await productService.getProducts();
  const categories = await productService.getCategories();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 sm:py-16 space-y-10">
      {/* Editorial Header */}
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <span className="text-xs uppercase tracking-[0.3em] text-[#C5A880] font-semibold block">
          The Florence Catalog
        </span>
        <h1 className="font-serif-luxury text-3xl sm:text-5xl text-[#1C1917]">
          Atelier Footwear Collection
        </h1>
        <p className="text-sm text-[#78716C] font-light leading-relaxed">
          Every style handcrafted with Italian mastery and available in your
          choice of 1", 2", or 3" heel elevation.
        </p>
      </div>

      {/* Interactive Catalog Client with Facets & Sorting */}
      <CatalogClient
        initialProducts={products}
        categories={categories}
        initialQuery={initialQuery}
        initialCategory={initialCategory}
        initialHeel={initialHeel}
        initialSort={initialSort}
      />
    </div>
  );
}
