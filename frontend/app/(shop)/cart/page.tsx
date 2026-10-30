"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, CheckCircle2, Lock, Minus, Plus, ShieldCheck, ShoppingBag, Sparkles, Trash2, Truck } from "lucide-react";
import { useStore } from "@/context/StoreContext";

export default function CartPage() {
  const { cart, cartTotal, updateQuantity, removeFromCart, clearCart } = useStore();
  const [reserved, setReserved] = useState(false);

  const handleCheckoutSimulate = () => {
    setReserved(true);
  };

  if (cart.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-24 text-center space-y-6">
        <div className="w-16 h-16 mx-auto rounded-full bg-[#FAF8F5] border border-[#E7E2DA] flex items-center justify-center text-[#8C827A]">
          <ShoppingBag className="w-8 h-8 stroke-1" />
        </div>
        <h1 className="font-serif-luxury text-3xl text-[#1C1917]">
          Your Atelier Bag is Empty
        </h1>
        <p className="text-sm text-[#78716C] max-w-md mx-auto font-light">
          Experience Italian craftsmanship and bespoke 1", 2", or 3" heel
          elevations crafted for enduring comfort.
        </p>
        <Link
          href="/products"
          className="inline-flex items-center gap-2 px-8 py-3.5 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors"
        >
          <span>Explore The Footwear Collection</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 sm:py-16 space-y-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between border-b border-[#E7E2DA] pb-6 gap-4">
        <div>
          <span className="text-xs uppercase tracking-[0.2em] text-[#C5A880] font-semibold block mb-1">
            Florence Atelier
          </span>
          <h1 className="font-serif-luxury text-3xl sm:text-4xl text-[#1C1917]">
            Your Shopping Bag
          </h1>
        </div>
        <Link
          href="/products"
          className="text-xs uppercase tracking-widest text-[#8C827A] hover:text-[#1C1917] flex items-center gap-1.5 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Continue Selecting Footwear</span>
        </Link>
      </div>

      {reserved ? (
        /* Reservation Confirmation Banner (Purchasing boundary ends at cart) */
        <div className="p-8 sm:p-12 bg-white border border-[#C5A880] text-center space-y-4 max-w-2xl mx-auto shadow-lg animate-in fade-in">
          <div className="w-14 h-14 mx-auto rounded-full bg-[#E8F3EC] text-[#0A4D2E] flex items-center justify-center">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
            Atelier Reservation Confirmed
          </span>
          <h2 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Your Bespoke Footwear is Held
          </h2>
          <p className="text-sm text-[#78716C] leading-relaxed font-light">
            As per Ibrat platform specifications, the purchasing journey concludes
            at the bag. Your custom heel selections and sizes have been reserved in
            inventory.
          </p>
          <div className="pt-4 flex justify-center gap-4">
            <button
              onClick={() => setReserved(false)}
              className="px-6 py-2.5 border border-[#1C1917] text-xs uppercase tracking-widest hover:bg-[#FAF8F5]"
            >
              Modify Bag
            </button>
            <Link
              href="/"
              className="px-6 py-2.5 bg-[#1C1917] text-white text-xs uppercase tracking-widest hover:bg-[#C5A880]"
            >
              Return Home
            </Link>
          </div>
        </div>
      ) : (
        /* Main Cart Split */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          {/* Cart Items List */}
          <div className="lg:col-span-8 divide-y divide-[#E7E2DA] border-y border-[#E7E2DA]">
            {cart.map((item) => (
              <div key={item.id} className="py-6 flex flex-col sm:flex-row gap-6 items-start justify-between">
                <div className="flex gap-4 sm:gap-6">
                  {/* Item Image */}
                  <div className="w-24 h-30 sm:w-28 sm:h-36 bg-[#F5F2EB] border border-[#E7E2DA] overflow-hidden shrink-0">
                    <img
                      src={item.imageUrl || "/media/products/aurelia-champagne-main.webp"}
                      alt={item.name}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  {/* Details */}
                  <div className="space-y-2">
                    <h3 className="font-serif-luxury text-lg text-[#1C1917]">
                      <Link href={`/products/${item.slug}`} className="hover:text-[#C5A880] transition-colors">
                        {item.name}
                      </Link>
                    </h3>

                    <div className="text-xs text-[#78716C] space-y-1">
                      {item.color && (
                        <div>
                          <span className="text-[#8C827A]">Shade:</span> {item.color}
                        </div>
                      )}
                      {item.size && (
                        <div>
                          <span className="text-[#8C827A]">Size:</span> {item.size}
                        </div>
                      )}
                    </div>

                    {/* Bespoke Heel Height Badge */}
                    <div className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-[#1C1917] text-white text-[10px] uppercase tracking-wider font-medium">
                      <Sparkles className="w-3 h-3 text-[#C5A880]" />
                      <span>Bespoke Heel: {item.heelSize || "2 inch"}</span>
                    </div>

                    {/* Quantity Selector on Mobile */}
                    <div className="flex sm:hidden items-center gap-3 pt-2">
                      <div className="flex items-center border border-[#E7E2DA] bg-[#FAF8F5]">
                        <button
                          type="button"
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="p-1.5 text-[#1C1917] hover:text-[#C5A880]"
                        >
                          <Minus className="w-3.5 h-3.5" />
                        </button>
                        <span className="px-3 text-xs font-medium">{item.quantity}</span>
                        <button
                          type="button"
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="p-1.5 text-[#1C1917] hover:text-[#C5A880]"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <button
                        type="button"
                        onClick={() => removeFromCart(item.id)}
                        className="text-xs text-[#8C827A] hover:text-red-700 underline"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>

                {/* Right Quantity & Subtotal on Desktop */}
                <div className="hidden sm:flex flex-col items-end justify-between h-36">
                  <div className="text-base font-semibold text-[#1C1917]">
                    ₹{(item.price * item.quantity).toLocaleString("en-IN")}
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="flex items-center border border-[#E7E2DA] bg-[#FAF8F5]">
                      <button
                        type="button"
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        className="p-1.5 text-[#1C1917] hover:text-[#C5A880] transition-colors"
                      >
                        <Minus className="w-3.5 h-3.5" />
                      </button>
                      <span className="px-3 text-xs font-medium">{item.quantity}</span>
                      <button
                        type="button"
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        className="p-1.5 text-[#1C1917] hover:text-[#C5A880] transition-colors"
                      >
                        <Plus className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <button
                      type="button"
                      onClick={() => removeFromCart(item.id)}
                      className="text-[#8C827A] hover:text-red-700 p-1.5 transition-colors"
                      aria-label="Remove item"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}

            <div className="pt-4 flex justify-end">
              <button
                type="button"
                onClick={clearCart}
                className="text-xs text-[#8C827A] hover:text-red-700 underline"
              >
                Clear entire bag
              </button>
            </div>
          </div>

          {/* Order Summary Box */}
          <div className="lg:col-span-4 bg-white border border-[#E7E2DA] p-6 sm:p-8 space-y-6 sticky top-28">
            <h2 className="font-serif-luxury text-xl text-[#1C1917] border-b border-[#E7E2DA] pb-4">
              Atelier Summary
            </h2>

            <div className="space-y-3 text-xs text-[#78716C]">
              <div className="flex justify-between">
                <span>Footwear Subtotal</span>
                <span className="text-[#1C1917] font-semibold">₹{cartTotal.toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between">
                <span>Bespoke Heel Customization (1"-3")</span>
                <span className="text-[#0A4D2E] font-medium">Complimentary (₹0)</span>
              </div>
              <div className="flex justify-between">
                <span>Worldwide Tracked Courier</span>
                <span className="text-[#0A4D2E] font-medium">Complimentary (₹0)</span>
              </div>
              <div className="flex justify-between">
                <span>Silk Dust Bags & Hardcase Box</span>
                <span className="text-[#0A4D2E] font-medium">Included</span>
              </div>
              <div className="pt-4 border-t border-[#E7E2DA] flex justify-between text-base font-semibold text-[#1C1917]">
                <span>Total</span>
                <span>₹{cartTotal.toLocaleString("en-IN")} INR</span>
              </div>
            </div>

            <button
              type="button"
              onClick={handleCheckoutSimulate}
              className="w-full py-4 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-[0.2em] font-medium transition-colors shadow-md flex items-center justify-center gap-2 cursor-pointer"
            >
              <Lock className="w-3.5 h-3.5" />
              <span>Reserve & Complete Bag</span>
            </button>

            <div className="text-[11px] text-[#8C827A] space-y-2 pt-2 border-t border-[#F0EDE8]">
              <p className="flex items-center gap-1.5 text-[#57534E]">
                <Truck className="w-3.5 h-3.5 text-[#C5A880]" />
                <span>Dispatches from Florence within 24 hours</span>
              </p>
              <p className="flex items-center gap-1.5 text-[#57534E]">
                <ShieldCheck className="w-3.5 h-3.5 text-[#C5A880]" />
                <span>30-day complimentary exchanges & heel adjustments</span>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
