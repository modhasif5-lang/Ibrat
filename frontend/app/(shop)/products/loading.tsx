import React from "react";
import { ProductCardSkeleton, Skeleton } from "@/components/ui/Skeleton";

export default function CatalogLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 sm:py-16 space-y-10">
      {/* Editorial Header Skeleton */}
      <div className="text-center max-w-xl mx-auto space-y-3">
        <Skeleton className="h-3 w-32 mx-auto" />
        <Skeleton className="h-8 w-64 mx-auto" />
        <Skeleton className="h-4 w-96 mx-auto" />
      </div>

      {/* Filter Bar Skeleton */}
      <div className="p-4 sm:p-6 bg-white border border-[#E7E2DA] flex flex-col lg:flex-row justify-between gap-4">
        <Skeleton className="h-9 w-72" />
        <div className="flex gap-2">
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-20" />
        </div>
        <Skeleton className="h-8 w-36" />
      </div>

      {/* 8 Product Card Skeletons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 sm:gap-8">
        {Array.from({ length: 8 }).map((_, i) => (
          <ProductCardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}
