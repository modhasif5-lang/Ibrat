"use client";

import React from "react";
import { Check, Info, Sparkles } from "lucide-react";

export type HeelOption = "1 inch" | "2 inch" | "3 inch";

interface HeelSelectorProps {
  selectedHeel: string;
  onSelectHeel: (heel: string) => void;
  availableHeels?: string[]; // Defaults to ["1 inch", "2 inch", "3 inch"]
  disabled?: boolean;
}

const HEEL_DETAILS: Record<
  string,
  {
    label: string;
    metric: string;
    styleName: string;
    description: string;
    idealFor: string;
    silhouetteHeight: string; // for visual graphic
  }
> = {
  "1 inch": {
    label: '1"',
    metric: "2.5 cm",
    styleName: "Kitten & Low Lift",
    description: "Gentle elevation with full-day cushioning and zero pitch fatigue.",
    idealFor: "All-day garden galas, work-to-evening dinners",
    silhouetteHeight: "h-3",
  },
  "2 inch": {
    label: '2"',
    metric: "5.0 cm",
    styleName: "Mid Architectural",
    description: "The golden mean of stability and refined leg-lengthening posture.",
    idealFor: "Ceremonies, dancing, architectural silhouette",
    silhouetteHeight: "h-6",
  },
  "3 inch": {
    label: '3"',
    metric: "7.5 cm",
    styleName: "Classic Couture Stiletto",
    description: "Sculptural drama engineered with our proprietary steel shank & metatarsal foam.",
    idealFor: "Black tie galas, red carpet, statement entrances",
    silhouetteHeight: "h-9",
  },
};

export function HeelSelector({
  selectedHeel,
  onSelectHeel,
  availableHeels = ["1 inch", "2 inch", "3 inch"],
  disabled = false,
}: HeelSelectorProps) {
  const currentDetail = HEEL_DETAILS[selectedHeel] || HEEL_DETAILS["2 inch"];

  return (
    <div className="space-y-3">
      {/* Label and Guide Header */}
      <div className="flex items-center justify-between">
        <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] flex items-center gap-1.5">
          <span>Bespoke Heel Height</span>
          <span className="text-[#C5A880] text-[10px] font-normal tracking-normal lowercase">
            (select elevation)
          </span>
        </label>
        <span className="text-xs text-[#8C827A] font-medium flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-[#C5A880]" />
          <span>Complimentary Atelier Craft</span>
        </span>
      </div>

      {/* 3 Height Buttons Grid */}
      <div className="grid grid-cols-3 gap-2.5">
        {availableHeels.map((heel) => {
          const detail = HEEL_DETAILS[heel] || {
            label: heel,
            metric: "",
            styleName: heel,
            description: "",
            idealFor: "",
            silhouetteHeight: "h-5",
          };
          const isSelected = selectedHeel === heel;

          return (
            <button
              key={heel}
              type="button"
              disabled={disabled}
              onClick={() => onSelectHeel(heel)}
              className={`relative p-3.5 border transition-all text-left flex flex-col justify-between h-[104px] ${
                isSelected
                  ? "border-[#1C1917] bg-[#1C1917] text-white shadow-md ring-1 ring-[#1C1917]"
                  : "border-[#E7E2DA] bg-[#FAF8F5] text-[#1C1917] hover:border-[#8C827A] hover:bg-white"
              } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
            >
              {/* Header with Height & check */}
              <div className="flex items-start justify-between w-full">
                <div>
                  <span className="text-base font-serif-luxury font-medium tracking-tight block">
                    {detail.label}
                  </span>
                  <span
                    className={`text-[10px] uppercase tracking-wider block ${
                      isSelected ? "text-[#C5A880]" : "text-[#8C827A]"
                    }`}
                  >
                    {detail.metric}
                  </span>
                </div>
                {isSelected && (
                  <div className="w-4 h-4 rounded-full bg-[#C5A880] text-[#1C1917] flex items-center justify-center shrink-0">
                    <Check className="w-2.5 h-2.5 stroke-[3]" />
                  </div>
                )}
              </div>

              {/* Subtitle / Style name */}
              <div className="mt-auto">
                <span
                  className={`text-[11px] font-medium block truncate ${
                    isSelected ? "text-white" : "text-[#292524]"
                  }`}
                >
                  {detail.styleName.split("&")[0]}
                </span>
                <span
                  className={`text-[9px] block uppercase tracking-widest ${
                    isSelected ? "text-[#C5A880]" : "text-[#A8A29E]"
                  }`}
                >
                  ₹0 Surcharge
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Ergonomic & Fit Insight for Selected Height */}
      {currentDetail && (
        <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] text-xs text-[#57534E] flex items-start gap-2.5">
          <Info className="w-4 h-4 text-[#C5A880] shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <p className="font-medium text-[#1C1917]">
              {selectedHeel} ({currentDetail.metric}) — {currentDetail.styleName}
            </p>
            <p className="text-[11px] leading-relaxed text-[#78716C]">
              {currentDetail.description} <br />
              <span className="text-[#C5A880] font-medium">Best for:</span> {currentDetail.idealFor}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
