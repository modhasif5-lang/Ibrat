"use client";
import React, { useState } from "react";
import { HelpCircle } from "lucide-react";

interface SizeSelectorProps {
  selectedSize: number | null;
  onSelectSize: (size: number) => void;
  availableSizes?: number[]; // [35, 36, 37, 38, 39, 40, 41]
  outOfStockSizes?: number[];
  disabled?: boolean;
}

const DEFAULT_SIZES = [35, 36, 37, 38, 39, 40, 41];

export function SizeSelector({
  selectedSize,
  onSelectSize,
  availableSizes = DEFAULT_SIZES,
  outOfStockSizes = [],
  disabled = false,
}: SizeSelectorProps) {
  const [showGuide, setShowGuide] = useState(false);

  return (
    <div className="space-y-2.5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] flex items-center gap-1.5">
          <span>European Size</span>
          {selectedSize && (
            <span className="text-[#C5A880] font-normal tracking-normal lowercase">
              (EU {selectedSize})
            </span>
          )}
        </label>
        <button
          type="button"
          onClick={() => setShowGuide(!showGuide)}
          className="text-xs text-[#8C827A] hover:text-[#1C1917] flex items-center gap-1 transition-colors"
        >
          <HelpCircle className="w-3.5 h-3.5" />
          <span className="underline underline-offset-2">Size & Fit Guide</span>
        </button>
      </div>

      {/* Size Grid */}
      <div className="grid grid-cols-7 gap-1.5 sm:gap-2">
        {availableSizes.map((size) => {
          const isSelected = selectedSize === size;
          const isOOS = outOfStockSizes.includes(size);

          return (
            <button
              key={size}
              type="button"
              disabled={disabled || isOOS}
              onClick={() => onSelectSize(size)}
              className={`h-11 sm:h-12 border text-xs sm:text-sm font-medium transition-all relative flex flex-col items-center justify-center ${isSelected
                  ? "border-[#1C1917] bg-[#1C1917] text-white shadow-sm"
                  : isOOS
                    ? "border-[#E7E2DA] bg-[#F5F2EB] text-[#A8A29E] cursor-not-allowed line-through"
                    : "border-[#E7E2DA] bg-white text-[#1C1917] hover:border-[#1C1917] hover:bg-[#FAF8F5]"
                }`}
            >
              <span>{size}</span>
            </button>
          );
        })}
      </div>

      {/* Size Conversion Guide Accordion */}
      {showGuide && (
        <div className="p-3.5 bg-[#FAF8F5] border border-[#E7E2DA] text-xs text-[#57534E] space-y-2 animate-in fade-in duration-150">
          <div className="font-medium text-[#1C1917] flex items-center justify-between">
            <span>Italian Atelier Sizing Chart</span>
            <span className="text-[#C5A880] text-[10px] uppercase tracking-wider">True to Size</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[11px] border-collapse">
              <thead>
                <tr className="border-b border-[#E7E2DA] text-[#8C827A]">
                  <th className="py-1">EU Size</th>
                  <th className="py-1">US</th>
                  <th className="py-1">UK</th>
                  <th className="py-1">Foot Length</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F0EDE8]">
                <tr><td className="py-1 font-medium">35</td><td>5</td><td>2.5</td><td>22.4 cm</td></tr>
                <tr><td className="py-1 font-medium">36</td><td>5.5 - 6</td><td>3.5</td><td>23.0 cm</td></tr>
                <tr><td className="py-1 font-medium">37</td><td>6.5 - 7</td><td>4.5</td><td>23.7 cm</td></tr>
                <tr><td className="py-1 font-medium">38</td><td>7.5 - 8</td><td>5.5</td><td>24.4 cm</td></tr>
                <tr><td className="py-1 font-medium">39</td><td>8.5</td><td>6.5</td><td>25.0 cm</td></tr>
                <tr><td className="py-1 font-medium">40</td><td>9 - 9.5</td><td>7.5</td><td>25.7 cm</td></tr>
                <tr><td className="py-1 font-medium">41</td><td>10</td><td>8.5</td><td>26.4 cm</td></tr>
              </tbody>
            </table>
          </div>
          <p className="text-[10px] text-[#8C827A] italic">
            Note: If you have a wider instep or are in-between sizes, our master cobblers recommend sizing up a half size.
          </p>
        </div>
      )}
    </div>
  );
}
