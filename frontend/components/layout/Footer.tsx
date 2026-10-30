"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Headphones, HeartHandshake, Truck } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-[#1C1917] text-[#FAF8F5] pt-16 pb-12 border-t border-stone-800">
      {/* Brand Value Pillars */}
      <div className="max-w-7xl mx-auto px-6 sm:px-8 pb-14 border-b border-stone-800 grid grid-cols-1 sm:grid-cols-3 gap-8 text-center sm:text-left">
        <div className="flex items-center gap-4 justify-center sm:justify-start">
          <div className="w-12 h-12 rounded-full bg-stone-900 border border-stone-700 flex items-center justify-center text-[#C5A880] shrink-0">
            <Truck className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs uppercase tracking-widest font-medium">Free Shipping</h4>
            <p className="text-xs text-stone-400 mt-1">Free shipping on all orders in India</p>
          </div>
        </div>

        <div className="flex items-center gap-4 justify-center sm:justify-start">
          <div className="w-12 h-12 rounded-full bg-stone-900 border border-stone-700 flex items-center justify-center text-[#C5A880] shrink-0">
            <HeartHandshake className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs uppercase tracking-widest font-medium">100% Vegan</h4>
            <p className="text-xs text-stone-400 mt-1">
              All our products are cruelty free. We use textile-based raw materials for most of our shoes.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 justify-center sm:justify-start">
          <div className="w-12 h-12 rounded-full bg-stone-900 border border-stone-700 flex items-center justify-center text-[#C5A880] shrink-0">
            <Headphones className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs uppercase tracking-widest font-medium">Support Online</h4>
            <p className="text-xs text-stone-400 mt-1">
              We are around always for you. Reach out to us on Whatsapp or email. You can expect a response within 48 business hours.
            </p>
          </div>
        </div>
      </div>

      {/* Main Footer Links & Newsletter */}
      <div className="max-w-7xl mx-auto px-6 sm:px-8 py-16 grid grid-cols-1 md:grid-cols-4 gap-12">
        {/* Brand Column */}
        <div className="space-y-4">
          <span className="font-serif-luxury text-2xl tracking-[0.25em] font-normal uppercase block">
            IBRAT
          </span>
          <span className="text-[9px] uppercase tracking-[0.4em] text-[#C5A880] block -mt-2">
            Atelier di Firenze
          </span>
          <p className="text-xs text-stone-400 leading-relaxed max-w-xs pt-2">
            Crafting modern bridal and evening footwear in limited studio runs. Designed for
            uncompromising grace, all-day celebration, and effortless comfort.
          </p>
        </div>

        {/* Collections */}
        <div>
          <h4 className="text-xs uppercase tracking-widest text-[#C5A880] font-semibold mb-4">
            Atelier Collections
          </h4>
          <ul className="space-y-2.5 text-xs text-stone-300">
            <li>
              <Link href="/products?category=wedges" className="hover:text-white transition-colors">
                Wedges & Platforms
              </Link>
            </li>
            <li>
              <Link href="/products?category=mules-and-slides" className="hover:text-white transition-colors">
                Mules & Slides
              </Link>
            </li>
            <li>
              <Link href="/products?category=sandals" className="hover:text-white transition-colors">
                Sandals & Block Heels
              </Link>
            </li>
            <li>
              <Link href="/products?category=flats" className="hover:text-white transition-colors">
                Flats & Slip-Ons
              </Link>
            </li>
            <li>
              <Link href="/products?category=sneakers" className="hover:text-white transition-colors">
                Sneakers & High Tops
              </Link>
            </li>
          </ul>
        </div>

        {/* Client Care */}
        <div>
          <h4 className="text-xs uppercase tracking-widest text-[#C5A880] font-semibold mb-4">
            Bespoke Services
          </h4>
          <ul className="space-y-2.5 text-xs text-stone-300">
            <li>
              <Link href="/faq" className="hover:text-white transition-colors">
                Heel Customization Guide
              </Link>
            </li>
            <li>
              <Link href="/faq" className="hover:text-white transition-colors">
                Bridal Consultations
              </Link>
            </li>
            <li>
              <Link href="/shipping" className="hover:text-white transition-colors">
                Courier Tracking & Delivery
              </Link>
            </li>
            <li>
              <Link href="/faq" className="hover:text-white transition-colors">
                Exchanges & Care
              </Link>
            </li>
            <li>
              <Link href="/contact" className="hover:text-white transition-colors">
                Concierge Contact
              </Link>
            </li>
          </ul>
        </div>

        {/* Private Atelier Register */}
        <div className="space-y-4">
          <h4 className="text-xs uppercase tracking-widest text-[#C5A880] font-semibold">
            Private Atelier Access
          </h4>
          <p className="text-xs text-stone-400 leading-relaxed">
            Receive exclusive previews of seasonal limited runs and priority invitations to custom sizing appointments.
          </p>
          <form onSubmit={(e) => e.preventDefault()} className="space-y-2">
            <div className="flex border border-stone-700 focus-within:border-[#C5A880] transition-colors">
              <input
                type="email"
                placeholder="Enter your email address"
                className="w-full bg-stone-900 px-3 py-2 text-xs text-white placeholder-stone-500 focus:outline-none"
              />
              <button
                type="submit"
                className="bg-[#C5A880] text-[#1C1917] px-3.5 hover:bg-[#d6ba94] transition-colors flex items-center justify-center"
                aria-label="Subscribe"
              >
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-[10px] text-stone-500">
              By subscribing, you accept our Privacy Policy.
            </p>
          </form>
        </div>
      </div>

      {/* Bottom Legal / Copyright */}
      <div className="max-w-7xl mx-auto px-6 sm:px-8 pt-8 border-t border-stone-800 flex flex-col sm:flex-row justify-between items-center gap-4 text-[11px] text-stone-500">
        <div>
          © {new Date().getFullYear()} IBRAT Atelier. All rights reserved. Handcrafted Footwear.
        </div>
        <div className="flex gap-6">
          <Link href="/privacy" className="hover:text-stone-300 transition-colors">
            Privacy Policy
          </Link>
          <Link href="/terms" className="hover:text-stone-300 transition-colors">
            Terms of Service
          </Link>
          <Link href="/accessibility" className="hover:text-stone-300 transition-colors">
            Accessibility
          </Link>
        </div>
      </div>
    </footer>
  );
}
