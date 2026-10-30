import React from "react";
import { Skeleton } from "@/components/ui/Skeleton";

export default function ProductDetailLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 sm:py-12 space-y-12">
      {/* Breadcrumb Skeleton */}
      <div className="flex gap-2 items-center">
        <Skeleton className="h-3 w-12" />
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-3 w-28" />
      </div>

      {/* Split view */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
        {/* Left Gallery Skeleton */}
        <div className="lg:col-span-7">
          <Skeleton className="aspect-[4/5] w-full" />
        </div>

        {/* Right Info Skeleton */}
        <div className="lg:col-span-5 space-y-6">
          <div className="space-y-2 border-b border-[#E7E2DA] pb-6">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-16 w-full mt-2" />
          </div>

          {/* Heel Selector Skeleton */}
          <div className="space-y-3">
            <Skeleton className="h-3 w-36" />
            <div className="grid grid-cols-3 gap-2">
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
            </div>
          </div>

          {/* Size Selector Skeleton */}
          <div className="space-y-3">
            <Skeleton className="h-3 w-28" />
            <div className="grid grid-cols-7 gap-2">
              {Array.from({ length: 7 }).map((_, i) => (
                <Skeleton key={i} className="h-11 w-full" />
              ))}
            </div>
          </div>

          {/* Button Skeleton */}
          <Skeleton className="h-14 w-full" />
        </div>
      </div>
    </div>
  );
}
