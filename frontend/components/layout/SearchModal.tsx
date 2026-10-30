"use client";

import React, { useEffect, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, Clock, Search, Sparkles, X } from "lucide-react";
import { useStore } from "@/context/StoreContext";
import { AutocompleteSuggestion, searchService } from "@/services/search.service";

export function SearchModal() {
  const router = useRouter();
  const { isSearchOpen, closeSearch } = useStore();
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<AutocompleteSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when opened & lock scroll
  useEffect(() => {
    if (isSearchOpen) {
      document.body.style.overflow = "hidden";
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      document.body.style.overflow = "unset";
      setQuery("");
      setSuggestions([]);
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isSearchOpen]);

  // Handle ESC key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isSearchOpen) {
        closeSearch();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isSearchOpen, closeSearch]);

  // Debounced autocomplete search
  useEffect(() => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const res = await searchService.autocomplete(query.trim());
        setSuggestions(res);
      } catch (err) {
        console.error("Autocomplete error:", err);
      } finally {
        setIsLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    closeSearch();
    router.push(`/products?q=${encodeURIComponent(query.trim())}`);
  };

  const handleQuickSearch = (term: string) => {
    closeSearch();
    router.push(`/products?q=${encodeURIComponent(term)}`);
  };

  const handleHeelSearch = (heel: string) => {
    closeSearch();
    router.push(`/products?heel_size=${encodeURIComponent(heel)}`);
  };

  if (!isSearchOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-24 px-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-200">
      <div
        className="w-full max-w-3xl bg-white shadow-2xl border border-[#E7E2DA] rounded-none overflow-hidden relative"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Header Bar */}
        <form
          onSubmit={handleSearchSubmit}
          className="flex items-center gap-3 px-6 py-5 border-b border-[#E7E2DA] bg-[#FAF8F5]"
        >
          <Search className="w-5 h-5 text-[#8C827A] shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by footwear style, silk, leather, heel height..."
            className="w-full bg-transparent text-[#1C1917] placeholder:text-[#8C827A] placeholder:font-light text-base sm:text-lg focus:outline-none"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="text-[#8C827A] hover:text-[#1C1917] p-1 text-xs"
            >
              Clear
            </button>
          )}
          <button
            type="button"
            onClick={closeSearch}
            className="p-1 text-[#8C827A] hover:text-[#1C1917] transition-colors ml-2"
            aria-label="Close search"
          >
            <X className="w-5 h-5" />
          </button>
        </form>

        {/* Results / Discovery Container */}
        <div className="max-h-[70vh] overflow-y-auto p-6 space-y-6">
          {isLoading && (
            <div className="py-6 text-center text-xs tracking-widest uppercase text-[#8C827A]">
              Searching Atelier Catalog...
            </div>
          )}

          {/* Autocomplete Suggestions */}
          {!isLoading && suggestions.length > 0 && (
            <div>
              <div className="text-[11px] uppercase tracking-widest text-[#8C827A] mb-3 font-semibold">
                Suggested Footwear
              </div>
              <div className="divide-y divide-[#F0EDE8]">
                {suggestions.map((item) => (
                  <Link
                    key={item.id}
                    href={`/products/${item.slug}`}
                    onClick={closeSearch}
                    className="flex items-center justify-between py-3 px-2 hover:bg-[#FAF8F5] transition-colors group"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-14 bg-[#F5F2EB] relative overflow-hidden shrink-0 border border-[#E7E2DA]">
                        <img
                          src={item.primary_image_url || "/media/products/aurelia-champagne-main.webp"}
                          alt={item.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-[#1C1917] group-hover:text-[#C5A880] transition-colors">
                          {item.name}
                        </div>
                        {item.category_name && (
                          <div className="text-xs text-[#8C827A] font-light">
                            {item.category_name}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="text-sm font-medium text-[#1C1917]">
                      ₹{typeof item.effective_price === "number" ? item.effective_price.toLocaleString("en-IN") : item.effective_price}
                    </div>
                  </Link>
                ))}
              </div>
              <button
                type="button"
                onClick={() => handleSearchSubmit()}
                className="w-full mt-4 py-2.5 bg-[#1C1917] text-white text-xs uppercase tracking-widest font-medium hover:bg-[#C5A880] transition-colors flex items-center justify-center gap-2"
              >
                <span>View all results for "{query}"</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Quick Discoveries when query is empty */}
          {!query.trim() && (
            <div className="space-y-6">
              {/* Bespoke Heel Height Quick Filters */}
              <div>
                <div className="text-[11px] uppercase tracking-widest text-[#8C827A] mb-3 font-semibold flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-[#C5A880]" />
                  <span>Shop By Bespoke Heel Height</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {[
                    { label: "1 inch", sub: "Kitten & Low Heel", desc: "Effortless all-day poise" },
                    { label: "2 inch", sub: "Mid Block & Flared", desc: "Balanced architectural lift" },
                    { label: "3 inch", sub: "Classic Stiletto", desc: "Sensational evening drama" },
                  ].map((heel) => (
                    <button
                      key={heel.label}
                      type="button"
                      onClick={() => handleHeelSearch(heel.label)}
                      className="text-left p-3 border border-[#E7E2DA] hover:border-[#C5A880] hover:bg-[#FAF8F5] transition-all group"
                    >
                      <div className="text-sm font-medium text-[#1C1917] group-hover:text-[#C5A880]">
                        {heel.label}
                      </div>
                      <div className="text-xs text-[#8C827A] mt-0.5">{heel.sub}</div>
                      <div className="text-[11px] text-[#A8A29E] mt-1 font-light italic">
                        {heel.desc}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Popular Curated Searches */}
              <div>
                <div className="text-[11px] uppercase tracking-widest text-[#8C827A] mb-3 font-semibold">
                  Trending Atelier Searches
                </div>
                <div className="flex flex-wrap gap-2">
                  {[
                    "Bridal Pump",
                    "Champagne Satin",
                    "Italian Nappa Leather",
                    "Crystal Brooch",
                    "Emerald Velvet",
                    "2 inch heel",
                    "Pointed Toe Stiletto",
                  ].map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => handleQuickSearch(tag)}
                      className="text-xs px-3 py-1.5 bg-[#FAF8F5] text-[#292524] border border-[#E7E2DA] hover:border-[#1C1917] transition-colors"
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              {/* Collections Shortcut */}
              <div className="pt-2 border-t border-[#F0EDE8] flex items-center justify-between text-xs text-[#8C827A]">
                <span>Looking for bridal bespoke?</span>
                <Link
                  href="/collections/bridal-couture-edit"
                  onClick={closeSearch}
                  className="text-[#C5A880] hover:underline flex items-center gap-1 font-medium"
                >
                  Explore Bridal Edit <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          )}

          {/* No results state */}
          {!isLoading && query.trim() && suggestions.length === 0 && (
            <div className="py-8 text-center space-y-2">
              <p className="text-sm text-[#1C1917] font-medium">
                No bespoke footwear found for "{query}"
              </p>
              <p className="text-xs text-[#8C827A]">
                Try searching for "satin", "stiletto", "bridal", or browse by heel height.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
