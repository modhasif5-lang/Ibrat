"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Minus, Plus, ShoppingBag, Trash2, X } from "lucide-react";
import { useStore } from "@/context/StoreContext";

export function CartDrawer() {
  const { isCartOpen, closeCart, cart, cartCount, cartTotal, updateQuantity, removeFromCart, clearCart } =
    useStore();

  React.useEffect(() => {
    if (isCartOpen) {
      document.body.style.overflow = "hidden";
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === "Escape") closeCart();
      };
      window.addEventListener("keydown", handleKeyDown);
      return () => {
        document.body.style.overflow = "unset";
        window.removeEventListener("keydown", handleKeyDown);
      };
    }
  }, [isCartOpen, closeCart]);

  if (!isCartOpen) return null;

  const freeShippingThreshold = 300;
  const progressPercent = Math.min(100, Math.round((cartTotal / freeShippingThreshold) * 100));
  const amountToFreeShipping = Math.max(0, freeShippingThreshold - cartTotal);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-xs transition-opacity"
        onClick={closeCart}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-[#FAF8F5] shadow-2xl flex flex-col justify-between">
          {/* Header */}
          <div className="p-6 border-b border-[#E7E2DA] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <ShoppingBag className="w-5 h-5 text-[#C5A880]" />
              <h2 className="font-serif-luxury text-lg tracking-wide uppercase text-[#1C1917]">
                Shopping Bag ({cartCount})
              </h2>
            </div>
            <button
              onClick={closeCart}
              className="p-2 -mr-2 text-stone-400 hover:text-stone-900 transition-colors"
              aria-label="Close Shopping Bag"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Free Shipping Progress Meter */}
          <div className="bg-[#F3EFEA] px-6 py-3 border-b border-[#E7E2DA]">
            <div className="flex justify-between text-xs text-stone-700 font-medium">
              <span>Complimentary Express Courier Included on All Orders</span>
              <span className="text-[#C5A880] font-semibold">FREE</span>
            </div>
          </div>

          {/* Items List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {cart.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center py-16">
                <ShoppingBag className="w-12 h-12 text-stone-300 mb-4" />
                <p className="font-serif-luxury text-lg text-stone-700">Your bag is currently empty</p>
                <p className="text-xs text-stone-500 mt-1 max-w-xs">
                  Discover our handmade Tuscan footwear collections and customize your heel height.
                </p>
                <button
                  onClick={closeCart}
                  className="mt-6 px-6 py-2.5 bg-[#1C1917] text-[#FAF8F5] text-xs uppercase tracking-widest hover:bg-[#C5A880] transition-colors"
                >
                  Explore Footwear
                </button>
              </div>
            ) : (
              cart.map((item) => (
                <div key={item.id} className="flex gap-4 pb-6 border-b border-[#E7E2DA] last:border-b-0">
                  {/* Image / Thumbnail placeholder */}
                  <div className="w-20 h-24 bg-stone-200 rounded-sm overflow-hidden flex-shrink-0 relative border border-stone-300">
                    {/* Visual luxury placeholder representation */}
                    <div className="w-full h-full flex items-center justify-center text-[10px] text-stone-500 bg-stone-100 uppercase tracking-widest text-center p-1">
                      {item.color || "Silk"}
                    </div>
                  </div>

                  {/* Details */}
                  <div className="flex-1 flex flex-col justify-between">
                    <div>
                      <div className="flex justify-between items-start">
                        <Link
                          href={`/products/${item.slug}`}
                          onClick={closeCart}
                          className="font-serif-luxury text-sm font-medium text-[#1C1917] hover:text-[#C5A880] transition-colors"
                        >
                          {item.name}
                        </Link>
                        <button
                          onClick={() => removeFromCart(item.id)}
                          className="text-stone-400 hover:text-red-600 transition-colors p-1"
                          title="Remove item"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      {/* Customization Badges */}
                      <div className="flex flex-wrap gap-1.5 mt-1.5">
                        {item.heelSize && (
                          <span className="text-[10px] bg-[#EAE4DC] text-[#1C1917] px-2 py-0.5 rounded-full font-medium">
                            Heel: {item.heelSize}
                          </span>
                        )}
                        {item.size && (
                          <span className="text-[10px] bg-stone-100 text-stone-700 px-2 py-0.5 rounded-full border border-stone-200">
                            EU {item.size}
                          </span>
                        )}
                        {item.color && (
                          <span className="text-[10px] text-stone-500 py-0.5">
                            {item.color}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Price and Quantity Adjusters */}
                    <div className="flex items-center justify-between pt-2">
                      <div className="flex items-center border border-stone-300 rounded-sm bg-white">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="px-2 py-1 text-stone-600 hover:text-stone-900"
                        >
                          <Minus className="w-3 h-3" />
                        </button>
                        <span className="text-xs px-2 font-medium">{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="px-2 py-1 text-stone-600 hover:text-stone-900"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>

                      <span className="text-sm font-medium text-[#1C1917]">
                        ₹{(item.price * item.quantity).toLocaleString("en-IN")}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer Subtotal & Boundary CTA */}
          {cart.length > 0 && (
            <div className="p-6 bg-white border-t border-[#E7E2DA] space-y-4 shadow-lg">
              <div className="space-y-1.5 text-xs text-stone-600">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span className="text-sm font-medium text-stone-900">₹{cartTotal.toLocaleString("en-IN")}</span>
                </div>
                <div className="flex justify-between">
                  <span>Worldwide Courier</span>
                  <span className="text-[#C5A880]">
                    Complimentary (₹0)
                  </span>
                </div>
              </div>

              <div className="pt-2 border-t border-stone-100 flex justify-between items-baseline">
                <span className="text-xs uppercase tracking-wider font-semibold text-stone-900">
                  Estimated Total
                </span>
                <span className="font-serif-luxury text-xl font-medium text-stone-900">
                  ₹{cartTotal.toLocaleString("en-IN")}
                </span>
              </div>

              <div className="text-[11px] text-stone-500 bg-[#FAF8F5] p-2.5 rounded border border-stone-200">
                🔒 Purchasing boundary ends at cart reserve. Order/Payment microservices remain modularly decoupled.
              </div>

              <Link
                href="/cart"
                onClick={closeCart}
                className="w-full py-3.5 bg-[#1C1917] hover:bg-[#C5A880] text-[#FAF8F5] text-xs font-semibold uppercase tracking-widest text-center transition-colors flex items-center justify-center gap-2"
              >
                <span>Proceed to Cart Summary</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
