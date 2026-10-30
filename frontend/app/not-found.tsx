import React from "react";
import Link from "next/link";
import { ArrowRight, Compass, Sparkles } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-[75vh] flex items-center justify-center p-6 sm:p-12">
      <div className="max-w-lg w-full bg-white border border-[#E7E2DA] p-8 sm:p-12 text-center space-y-6 shadow-xs">
        <div className="w-14 h-14 mx-auto rounded-full bg-[#FAF8F5] border border-[#E7E2DA] flex items-center justify-center text-[#8C827A]">
          <Compass className="w-6 h-6 stroke-1 text-[#C5A880]" />
        </div>

        <div className="space-y-2">
          <span className="text-[10px] uppercase tracking-[0.3em] text-[#C5A880] font-semibold block">
            404 Error • Archive Search
          </span>
          <h1 className="font-serif-luxury text-3xl sm:text-4xl text-[#1C1917]">
            Silhouette Not Found
          </h1>
          <p className="text-xs text-[#78716C] leading-relaxed font-light max-w-sm mx-auto">
            The bespoke footwear design or curation you are looking for may have
            concluded its limited studio run or relocated to another collection.
          </p>
        </div>

        {/* Curated Links */}
        <div className="pt-2 border-t border-[#F0EDE8] space-y-2 text-xs">
          <div className="text-[10px] uppercase tracking-widest text-[#8C827A] font-semibold mb-3">
            Explore Active Atelier Edits
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
            <Link
              href="/collections/bridal-couture-edit"
              className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] hover:border-[#1C1917] transition-colors block group"
            >
              <div className="font-semibold text-[#1C1917] group-hover:text-[#C5A880]">
                Bridal Couture Edit
              </div>
              <div className="text-[10px] text-[#8C827A]">Italian silk satin & crystals</div>
            </Link>
            <Link
              href="/categories/stilettos-and-high-heels"
              className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] hover:border-[#1C1917] transition-colors block group"
            >
              <div className="font-semibold text-[#1C1917] group-hover:text-[#C5A880]">
                Stilettos & Heels
              </div>
              <div className="text-[10px] text-[#8C827A]">1", 2", and 3" custom elevations</div>
            </Link>
          </div>
        </div>

        <div className="pt-2">
          <Link
            href="/products"
            className="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors w-full sm:w-auto"
          >
            <span>Browse Full Catalog</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
