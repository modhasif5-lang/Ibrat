"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { AlertCircle, ArrowLeft, RefreshCw } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Global Error Boundary caught:", error);
  }, [error]);

  return (
    <div className="min-h-[75vh] flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-white border border-[#E7E2DA] p-8 sm:p-10 text-center space-y-6 shadow-sm">
        <div className="w-14 h-14 mx-auto rounded-full bg-red-50 border border-red-100 flex items-center justify-center text-red-700">
          <AlertCircle className="w-6 h-6 stroke-1" />
        </div>

        <div className="space-y-2">
          <span className="text-[10px] uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
            Atelier Service Interruption
          </span>
          <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Something Went Awry
          </h1>
          <p className="text-xs text-[#78716C] leading-relaxed font-light">
            We encountered an unexpected interruption while preparing your footwear
            details. Our master artisans have been notified.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            type="button"
            onClick={() => reset()}
            className="w-full sm:w-auto px-6 py-2.5 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors flex items-center justify-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Again</span>
          </button>

          <Link
            href="/"
            className="w-full sm:w-auto px-6 py-2.5 border border-[#E7E2DA] hover:bg-[#FAF8F5] text-[#1C1917] text-xs uppercase tracking-widest font-medium transition-colors flex items-center justify-center gap-1.5"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return Home</span>
          </Link>
        </div>

        <div className="pt-4 border-t border-[#F0EDE8] text-[11px] text-[#8C827A]">
          Need immediate concierge assistance? Email{" "}
          <a
            href="mailto:concierge@ibrat-footwear.com"
            className="text-[#C5A880] underline font-medium"
          >
            concierge@ibrat-footwear.com
          </a>
        </div>
      </div>
    </div>
  );
}
