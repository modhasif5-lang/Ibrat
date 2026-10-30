"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Heart,
  Menu,
  Search,
  ShoppingBag,
  Sparkles,
  User as UserIcon,
  X,
} from "lucide-react";
import { useStore } from "@/context/StoreContext";

export function Navbar() {
  const pathname = usePathname();
  const { cartCount, openCart, wishlist, openSearch, user } = useStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { label: "New In", href: "/products?sort_by=newest" },
    { label: "Bridal Couture", href: "/collections/bridal-couture-edit" },
    { label: "Stilettos", href: "/categories/stilettos-and-high-heels" },
    { label: "Mules & Slides", href: "/categories/mules-and-slides" },
    { label: "Flats & Loafers", href: "/categories/luxury-flats-and-loafers" },
    { label: "Custom Heeling", href: "/products?heel=custom" },
  ];

  return (
    <header className="sticky top-0 z-40 w-full transition-all">
      {/* Main Glass Navbar */}
      <nav className="glass-header border-b border-[#E7E2DA] px-4 sm:px-8 py-4 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Mobile Menu Button */}
          <div className="flex items-center lg:hidden">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="p-2 -ml-2 text-[#1C1917] hover:text-[#C5A880] transition-colors"
              aria-label="Open Navigation Menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <button
              onClick={openSearch}
              className="p-2 text-[#1C1917] hover:text-[#C5A880] transition-colors ml-1"
              aria-label="Search"
            >
              <Search className="w-5 h-5" />
            </button>
          </div>

          {/* Desktop Navigation Links (Left) */}
          <div className="hidden lg:flex items-center gap-6 xl:gap-8 text-xs uppercase tracking-widest font-medium text-[#292524]">
            {navLinks.slice(0, 3).map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`hover:text-[#C5A880] transition-colors py-1 relative ${pathname === link.href
                  ? "text-[#C5A880] after:absolute after:bottom-0 after:left-0 after:w-full after:h-[1px] after:bg-[#C5A880]"
                  : ""
                  }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Center Luxury Brand Wordmark */}
          {/* Center Luxury Brand Wordmark */}
          <div className="text-center flex-1 lg:flex-initial">
            <Link href="/" className="inline-block group">
              <span className="font-serif-luxury text-2xl sm:text-3xl tracking-[0.25em] font-normal text-[#1C1917] uppercase block transition-transform group-hover:scale-[1.02]">
                I B R A T
              </span>
            </Link>
          </div>


          {/* Desktop Navigation Links (Right) + Action Icons */}
          <div className="flex items-center gap-4 sm:gap-6">
            <div className="hidden xl:flex items-center gap-6 text-xs uppercase tracking-widest font-medium text-[#292524]">
              {navLinks.slice(3).map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="hover:text-[#C5A880] transition-colors py-1"
                >
                  {link.label}
                </Link>
              ))}
            </div>

            <div className="flex items-center gap-3 sm:gap-4 pl-2 lg:border-l lg:border-[#E7E2DA]">
              {/* Search Trigger */}
              <button
                onClick={openSearch}
                className="hidden lg:flex p-2 text-[#1C1917] hover:text-[#C5A880] transition-colors"
                title="Search luxury catalog"
              >
                <Search className="w-5 h-5" />
              </button>

              {/* Wishlist Icon */}
              <Link
                href="/wishlist"
                className="p-2 text-[#1C1917] hover:text-[#C5A880] transition-colors relative"
                title="Your Wishlist"
              >
                <Heart className="w-5 h-5" />
                {wishlist.length > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 bg-[#C5A880] text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                    {wishlist.length}
                  </span>
                )}
              </Link>

              {/* Account Profile Icon */}
              <Link
                href={user ? "/profile" : "/login"}
                className="p-2 text-[#1C1917] hover:text-[#C5A880] transition-colors"
                title={user ? `Signed in as ${user.full_name}` : "Sign In or Register"}
              >
                <UserIcon className="w-5 h-5" />
              </Link>

              {/* Shopping Bag Button */}
              <button
                onClick={openCart}
                className="p-2 text-[#1C1917] hover:text-[#C5A880] transition-colors relative"
                title="Shopping Bag"
              >
                <ShoppingBag className="w-5 h-5" />
                {cartCount > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 bg-[#1C1917] text-[#FAF8F5] text-[10px] font-bold rounded-full flex items-center justify-center border border-[#C5A880]">
                    {cartCount}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 w-4/5 max-w-sm bg-[#FAF8F5] p-6 shadow-2xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-6 border-b border-[#E7E2DA]">
                <div>
                  <span className="font-serif-luxury text-xl tracking-[0.2em] font-medium text-[#1C1917]">
                    IBRAT
                  </span>
                </div>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-2 -mr-2 text-stone-500 hover:text-stone-900"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="flex flex-col gap-5 py-8 text-sm uppercase tracking-widest font-medium text-[#1C1917]">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="hover:text-[#C5A880] transition-colors py-1 border-b border-stone-100 flex items-center justify-between"
                  >
                    <span>{link.label}</span>
                    <span className="text-xs text-stone-400">→</span>
                  </Link>
                ))}
              </div>
            </div>

            <div className="pt-6 border-t border-[#E7E2DA] space-y-4 text-xs text-stone-600">
              <Link
                href={user ? "/profile" : "/login"}
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-2 hover:text-stone-900"
              >
                <UserIcon className="w-4 h-4 text-[#C5A880]" />
                <span>{user ? `Account: ${user.full_name}` : "Sign In / Register"}</span>
              </Link>
              <div className="text-[11px] text-stone-400">
                Concierge: concierge@ibrat.com • Firenze, IT
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
