"use client";

import React, { useState } from "react";
import { CheckCircle2, Cpu, Database, RefreshCw, Sparkles, Trash2, Wand2 } from "lucide-react";

export default function AdminRecommendationsPage() {
  const [categoryWeight, setCategoryWeight] = useState(35);
  const [heelWeight, setHeelWeight] = useState(25);
  const [materialWeight, setMaterialWeight] = useState(15);
  const [colorWeight, setColorWeight] = useState(15);
  const [priceWeight, setPriceWeight] = useState(10);

  const [cacheStatus, setCacheStatus] = useState("Cached items: 42 keys | Hit Ratio: 94.2%");
  const [purging, setPurging] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const totalWeight =
    categoryWeight + heelWeight + materialWeight + colorWeight + priceWeight;

  const handlePurgeCache = () => {
    setPurging(true);
    setTimeout(() => {
      setCacheStatus("Redis cache purged. Keys: 0 | Memory freed: 1.4 MB");
      setPurging(false);
    }, 600);
  };

  const handleSaveWeights = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E7E2DA] pb-6">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block mb-1">
            Algorithmic Personalization
          </span>
          <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Recommendation Engine Telemetry
          </h1>
        </div>

        <button
          type="button"
          onClick={handlePurgeCache}
          disabled={purging}
          className="px-4 py-2 bg-red-700 hover:bg-red-800 text-white text-xs uppercase tracking-widest font-medium transition-colors flex items-center gap-1.5 self-start sm:self-auto disabled:opacity-50"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>{purging ? "Purging Redis..." : "Purge Redis Cache"}</span>
        </button>
      </div>

      {/* Redis Cache Status Pill */}
      <div className="p-4 bg-white border border-[#E7E2DA] flex items-center justify-between text-xs text-[#57534E]">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-[#C5A880]" />
          <span>
            <strong>Redis L2 Cache:</strong> {cacheStatus}
          </span>
        </div>
        <span className="text-[#0A4D2E] font-semibold uppercase tracking-wider text-[10px]">
          TTL: 3,600s
        </span>
      </div>

      {/* Multi-Signal Algorithm Weight Tuning */}
      <form onSubmit={handleSaveWeights} className="bg-white border border-[#E7E2DA] p-6 sm:p-8 space-y-6">
        <div className="border-b border-[#F0EDE8] pb-4">
          <h2 className="font-serif-luxury text-xl text-[#1C1917]">
            Similarity Scoring Model Weights
          </h2>
          <p className="text-xs text-[#8C827A] mt-0.5">
            The multi-signal algorithm scores candidate footwear against client posture, preferred heel elevation, and material affinity.
          </p>
        </div>

        <div className="space-y-5">
          {/* Category Signal */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-semibold text-[#1C1917]">
              <span>Category Affinity Signal</span>
              <span className="text-[#C5A880]">{categoryWeight}%</span>
            </div>
            <input
              type="range"
              min={0}
              max={60}
              value={categoryWeight}
              onChange={(e) => setCategoryWeight(Number(e.target.value))}
              className="w-full accent-[#1C1917]"
            />
            <span className="text-[10px] text-[#8C827A]">
              Rewards exact or sibling category alignment (e.g. Bridal & Evening).
            </span>
          </div>

          {/* Heel Height Signal */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-semibold text-[#1C1917]">
              <span>Bespoke Heel Height Elevation Match (1", 2", 3")</span>
              <span className="text-[#C5A880]">{heelWeight}%</span>
            </div>
            <input
              type="range"
              min={0}
              max={60}
              value={heelWeight}
              onChange={(e) => setHeelWeight(Number(e.target.value))}
              className="w-full accent-[#1C1917]"
            />
            <span className="text-[10px] text-[#8C827A]">
              Prioritizes pairs supporting the client's preferred elevation choice.
            </span>
          </div>

          {/* Material Signal */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-semibold text-[#1C1917]">
              <span>Tuscan Material & Texture Similarity</span>
              <span className="text-[#C5A880]">{materialWeight}%</span>
            </div>
            <input
              type="range"
              min={0}
              max={50}
              value={materialWeight}
              onChange={(e) => setMaterialWeight(Number(e.target.value))}
              className="w-full accent-[#1C1917]"
            />
            <span className="text-[10px] text-[#8C827A]">
              Rewards matching Italian Silk Satin, Full-grain Nappa, or Velvet.
            </span>
          </div>

          {/* Color Signal */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-semibold text-[#1C1917]">
              <span>Color Harmonic Concordance</span>
              <span className="text-[#C5A880]">{colorWeight}%</span>
            </div>
            <input
              type="range"
              min={0}
              max={50}
              value={colorWeight}
              onChange={(e) => setColorWeight(Number(e.target.value))}
              className="w-full accent-[#1C1917]"
            />
          </div>

          {/* Price Signal */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-semibold text-[#1C1917]">
              <span>Price Proximity Bracket</span>
              <span className="text-[#C5A880]">{priceWeight}%</span>
            </div>
            <input
              type="range"
              min={0}
              max={40}
              value={priceWeight}
              onChange={(e) => setPriceWeight(Number(e.target.value))}
              className="w-full accent-[#1C1917]"
            />
          </div>
        </div>

        <div className="pt-4 border-t border-[#F0EDE8] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="text-xs text-[#57534E]">
            Sum of signals:{" "}
            <strong className={totalWeight === 100 ? "text-emerald-700 font-bold" : "text-amber-700"}>
              {totalWeight}% {totalWeight === 100 ? "(Calibrated)" : "(Normalized dynamically)"}
            </strong>
          </div>

          <div className="flex items-center gap-3">
            {saveSuccess && (
              <span className="text-xs text-emerald-700 flex items-center gap-1 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Engine weights saved</span>
              </span>
            )}
            <button
              type="submit"
              className="px-6 py-2.5 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors"
            >
              Update AI Calibration
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
