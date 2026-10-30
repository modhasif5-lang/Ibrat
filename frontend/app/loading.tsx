import React from "react";
import { Sparkles } from "lucide-react";

export default function GlobalLoading() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center p-8 space-y-6 animate-in fade-in duration-300">
      {/* Animated Luxury Monogram Ring */}
      <div className="relative flex items-center justify-center">
        <div className="w-16 h-16 rounded-full border border-[#E7E2DA] border-t-[#C5A880] animate-spin" />
        <span className="absolute font-serif-luxury text-xl font-normal text-[#1C1917] tracking-widest">
          I
        </span>
      </div>

      <div className="text-center space-y-1.5">
        <span className="font-serif-luxury text-lg tracking-[0.2em] uppercase text-[#1C1917] block">
          IBRAT
        </span>
        <span className="text-[10px] uppercase tracking-[0.3em] text-[#C5A880] block font-sans">
          Atelier di Firenze
        </span>
        <p className="text-xs text-[#8C827A] pt-2 font-light">
          Preparing handcrafted footwear...
        </p>
      </div>
    </div>
  );
}
