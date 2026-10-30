"use client";

import React from "react";
import { Check } from "lucide-react";

export interface ColorOption {
  name: string;
  hex?: string;
  inStock?: boolean;
}

interface ColorSelectorProps {
  selectedColor: string;
  colors: ColorOption[];
  onSelectColor: (colorName: string) => void;
  disabled?: boolean;
}

// Default luxury fallback color swatches if not provided
const LUXURY_COLOR_MAP: Record<string, string> = {
  "Champagne Gold": "#F7E7CE",
  "Midnight Black": "#1A1A1A",
  "Bridal White": "#FAF9F6",
  "Emerald Velvet": "#0A4D2E",
  "Rose Blush": "#E8C5C8",
  "Sapphire Blue": "#0F2537",
  "Tuscan Tan": "#C19A6B",
  "Pearl Ivory": "#FFFFF0",
};

export function ColorSelector({
  selectedColor,
  colors,
  onSelectColor,
  disabled = false,
}: ColorSelectorProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs">
        <label className="uppercase tracking-widest font-semibold text-[#1C1917] flex items-center gap-1.5">
          <span>Shade & Finish</span>
          <span className="text-[#C5A880] font-normal tracking-normal">
            — {selectedColor}
          </span>
        </label>
        <span className="text-[#8C827A] text-[11px] font-light">
          {colors.length} {colors.length === 1 ? "shade" : "shades"}
        </span>
      </div>

      <div className="flex items-center gap-3">
        {colors.map((color) => {
          const isSelected = selectedColor.toLowerCase() === color.name.toLowerCase();
          const hex = color.hex || LUXURY_COLOR_MAP[color.name] || "#C5A880";
          const isLight = hex.toLowerCase() === "#faf9f6" || hex.toLowerCase() === "#fffff0" || hex.toLowerCase() === "#ffffff" || hex.toLowerCase() === "#f7e7ce";

          return (
            <button
              key={color.name}
              type="button"
              disabled={disabled}
              onClick={() => onSelectColor(color.name)}
              title={color.name}
              className={`group relative p-0.5 rounded-full transition-all flex items-center justify-center ${
                isSelected
                  ? "ring-2 ring-offset-2 ring-[#1C1917]"
                  : "hover:scale-110"
              }`}
            >
              <span
                className="w-7 h-7 rounded-full border border-black/10 shadow-inner flex items-center justify-center transition-transform"
                style={{ backgroundColor: hex }}
              >
                {isSelected && (
                  <Check
                    className={`w-3.5 h-3.5 stroke-[2.5] ${
                      isLight ? "text-stone-900" : "text-white"
                    }`}
                  />
                )}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
