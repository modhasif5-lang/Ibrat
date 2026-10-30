"use client";

import React, { useState } from "react";
import Image from "next/image";
import { ChevronLeft, ChevronRight, Maximize2, ShieldCheck, Sparkles } from "lucide-react";
import { ProductImage } from "@/types";

interface ProductGalleryProps {
  images: ProductImage[];
  productName: string;
}

export function ProductGallery({ images, productName }: ProductGalleryProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isZoomed, setIsZoomed] = useState(false);

  // If no images provided, use a high quality fallback
  const displayImages =
    images && images.length > 0
      ? images
      : [
          {
            id: "fb-1",
            url: "/media/products/aurelia-champagne-main.webp",
            alt_text: productName,
            sort_order: 0,
            is_primary: true,
          },
        ];

  const currentImage = displayImages[activeIndex] || displayImages[0];

  const handleNext = () => {
    setActiveIndex((prev) => (prev + 1) % displayImages.length);
  };

  const handlePrev = () => {
    setActiveIndex((prev) => (prev - 1 + displayImages.length) % displayImages.length);
  };

  return (
    <div className="flex flex-col-reverse md:flex-row gap-4">
      {/* Thumbnails Sidebar */}
      {displayImages.length > 1 && (
        <div className="flex md:flex-col gap-3 overflow-x-auto md:overflow-y-auto max-h-[600px] shrink-0 no-scrollbar">
          {displayImages.map((img, idx) => (
            <button
              key={img.id || idx}
              type="button"
              onClick={() => setActiveIndex(idx)}
              className={`relative w-16 h-20 sm:w-20 sm:h-24 bg-[#F5F2EB] border transition-all overflow-hidden shrink-0 ${
                activeIndex === idx
                  ? "border-[#1C1917] ring-1 ring-[#1C1917]"
                  : "border-[#E7E2DA] opacity-70 hover:opacity-100"
              }`}
            >
              <img
                src={img.url}
                alt={img.alt_text || `${productName} view ${idx + 1}`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).src =
                    "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=800&q=80";
                }}
              />
            </button>
          ))}
        </div>
      )}

      {/* Main Large Visual Stage */}
      <div className="relative flex-1 bg-[#F5F2EB] border border-[#E7E2DA] overflow-hidden group aspect-[4/5] max-h-[640px]">
        {/* Luxury Badge Overlays */}
        <div className="absolute top-4 left-4 z-10 flex flex-col gap-1.5 pointer-events-none">
          <span className="bg-[#1C1917]/90 text-white text-[10px] uppercase tracking-widest px-2.5 py-1 font-medium backdrop-blur-sm flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-[#C5A880]" />
            <span>Artisan Crafted</span>
          </span>
          <span className="bg-white/90 text-[#1C1917] text-[10px] uppercase tracking-widest px-2.5 py-1 font-medium backdrop-blur-sm border border-[#E7E2DA]">
            1" • 2" • 3" Heel Choice
          </span>
        </div>

        {/* Zoom Button */}
        <button
          type="button"
          onClick={() => setIsZoomed(!isZoomed)}
          className="absolute top-4 right-4 z-10 p-2 bg-white/80 hover:bg-white text-[#1C1917] backdrop-blur-sm border border-[#E7E2DA] opacity-0 group-hover:opacity-100 transition-opacity"
          aria-label="Toggle zoom"
        >
          <Maximize2 className="w-4 h-4" />
        </button>

        {/* Image Display */}
        <div
          className={`w-full h-full cursor-zoom-in transition-transform duration-500 ease-out flex items-center justify-center ${
            isZoomed ? "scale-125" : "group-hover:scale-105"
          }`}
          onClick={() => setIsZoomed(!isZoomed)}
        >
          <img
            src={currentImage.url}
            alt={currentImage.alt_text || productName}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src =
                "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=1200&q=85";
            }}
          />
        </div>

        {/* Carousel Prev/Next Buttons */}
        {displayImages.length > 1 && (
          <>
            <button
              type="button"
              onClick={handlePrev}
              className="absolute left-3 top-1/2 -translate-y-1/2 p-2 bg-white/80 hover:bg-white text-[#1C1917] backdrop-blur-sm border border-[#E7E2DA] opacity-0 group-hover:opacity-100 transition-all"
              aria-label="Previous image"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={handleNext}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-white/80 hover:bg-white text-[#1C1917] backdrop-blur-sm border border-[#E7E2DA] opacity-0 group-hover:opacity-100 transition-all"
              aria-label="Next image"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </>
        )}

        {/* Image Counter */}
        <div className="absolute bottom-4 right-4 z-10 bg-black/60 backdrop-blur-sm text-white text-[10px] tracking-widest px-2.5 py-1">
          {activeIndex + 1} / {displayImages.length}
        </div>
      </div>
    </div>
  );
}
