"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Check, Heart, LogOut, Package, Settings, ShieldCheck, Sparkles, User as UserIcon } from "lucide-react";
import { useStore } from "@/context/StoreContext";

export default function ProfilePage() {
  const router = useRouter();
  const { user, logout } = useStore();

  const [preferredHeel, setPreferredHeel] = useState("2 inch");
  const [shoeSize, setShoeSize] = useState(38);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    // If not logged in, redirect to login
    if (!user) {
      router.push("/login");
    }
  }, [user, router]);

  const handleSavePreferences = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2000);
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!user) return null;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-8 py-10 sm:py-16 space-y-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#E7E2DA] pb-8 gap-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-[#1C1917] text-[#C5A880] flex items-center justify-center font-serif-luxury text-2xl">
            {user.full_name?.charAt(0) || "I"}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
                {user.full_name}
              </h1>
              <span className="px-2 py-0.5 bg-[#C5A880]/20 text-[#1C1917] text-[10px] uppercase tracking-wider font-semibold">
                {user.role === "ADMIN" ? "Director" : "VIP Client"}
              </span>
            </div>
            <p className="text-xs text-[#8C827A] mt-0.5">{user.email}</p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          className="self-start sm:self-auto px-4 py-2 border border-[#E7E2DA] text-xs uppercase tracking-widest text-[#8C827A] hover:text-[#1C1917] hover:border-[#1C1917] flex items-center gap-1.5 transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Footwear Fit Profile */}
        <div className="md:col-span-2 bg-white border border-[#E7E2DA] p-6 sm:p-8 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs uppercase tracking-[0.2em] text-[#C5A880] font-semibold block">
                Personal Atelier Profile
              </span>
              <h2 className="font-serif-luxury text-xl sm:text-2xl text-[#1C1917]">
                Footwear & Heel Preferences
              </h2>
            </div>
            <Sparkles className="w-5 h-5 text-[#C5A880]" />
          </div>

          <p className="text-xs text-[#78716C] leading-relaxed">
            Your preferences inform our master artisans and automatically configure
            default elevations when you view new collections.
          </p>

          <div className="space-y-4 pt-2">
            {/* Preferred Heel */}
            <div>
              <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-2">
                Preferred Bespoke Heel Height
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { h: "1 inch", sub: "Kitten / Low" },
                  { h: "2 inch", sub: "Mid Architectural" },
                  { h: "3 inch", sub: "Classic Stiletto" },
                ].map((item) => (
                  <button
                    key={item.h}
                    type="button"
                    onClick={() => setPreferredHeel(item.h)}
                    className={`p-3 border text-left transition-all ${
                      preferredHeel === item.h
                        ? "border-[#1C1917] bg-[#1C1917] text-white"
                        : "border-[#E7E2DA] bg-[#FAF8F5] text-[#1C1917] hover:border-[#8C827A]"
                    }`}
                  >
                    <div className="font-semibold text-sm">{item.h}</div>
                    <div className="text-[10px] text-[#C5A880] mt-0.5">{item.sub}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Preferred Shoe Size */}
            <div>
              <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-2">
                Italian Shoe Size (EU)
              </label>
              <div className="flex gap-2 overflow-x-auto">
                {[35, 36, 37, 38, 39, 40, 41].map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setShoeSize(s)}
                    className={`w-10 h-10 border text-xs font-medium transition-colors ${
                      shoeSize === s
                        ? "border-[#1C1917] bg-[#1C1917] text-white"
                        : "border-[#E7E2DA] bg-[#FAF8F5] text-[#1C1917] hover:border-[#1C1917]"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {savedSuccess && (
              <div className="p-3 bg-[#E8F3EC] text-[#0A4D2E] text-xs font-medium text-center">
                Atelier preferences saved successfully.
              </div>
            )}

            <button
              type="button"
              onClick={handleSavePreferences}
              className="px-6 py-2.5 bg-[#1C1917] text-white text-xs uppercase tracking-widest hover:bg-[#C5A880] transition-colors"
            >
              Update Preferences
            </button>
          </div>
        </div>

        {/* Quick Links & Concierge */}
        <div className="space-y-6">
          <div className="bg-white border border-[#E7E2DA] p-6 space-y-4">
            <h3 className="font-serif-luxury text-lg text-[#1C1917]">
              Client Quick Links
            </h3>
            <div className="divide-y divide-[#F0EDE8] text-xs">
              <Link
                href="/wishlist"
                className="py-2.5 flex items-center justify-between text-[#57534E] hover:text-[#1C1917]"
              >
                <span className="flex items-center gap-2">
                  <Heart className="w-3.5 h-3.5 text-[#C5A880]" />
                  <span>Curated Wishlist</span>
                </span>
                <span>→</span>
              </Link>
              <Link
                href="/cart"
                className="py-2.5 flex items-center justify-between text-[#57534E] hover:text-[#1C1917]"
              >
                <span className="flex items-center gap-2">
                  <Package className="w-3.5 h-3.5 text-[#C5A880]" />
                  <span>Shopping Bag</span>
                </span>
                <span>→</span>
              </Link>
              {user.role === "ADMIN" && (
                <Link
                  href="/admin"
                  className="py-2.5 flex items-center justify-between text-[#1C1917] font-semibold hover:text-[#C5A880]"
                >
                  <span className="flex items-center gap-2">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#C5A880]" />
                    <span>Atelier Admin Portal</span>
                  </span>
                  <span>→</span>
                </Link>
              )}
            </div>
          </div>

          <div className="p-6 bg-[#FAF8F5] border border-[#E7E2DA] space-y-2 text-xs text-[#78716C]">
            <strong className="block text-[#1C1917] font-medium uppercase tracking-wider">
              Private Concierge
            </strong>
            <p className="font-light">
              Need custom bridal sizing or emergency 48-hour event dispatch?
            </p>
            <p className="text-[#C5A880] font-medium pt-1">
              concierge@ibrat-footwear.com
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
