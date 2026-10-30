"use client";

import React, { useState } from "react";
import { Check, Heart, ShoppingBag, Sparkles } from "lucide-react";
import { useStore } from "@/context/StoreContext";
import { Product } from "@/types";
import { HeelSelector } from "@/components/product/HeelSelector";
import { SizeSelector } from "@/components/product/SizeSelector";
import { ColorOption, ColorSelector } from "@/components/product/ColorSelector";

interface ProductOrderBoxProps {
  product: Product;
}

export function ProductOrderBox({ product }: ProductOrderBoxProps) {
  const { addToCart, openCart, isInWishlist, toggleWishlist } = useStore();
  const isWishlisted = isInWishlist(product.id);

  const safeVariants =
    product.variants && product.variants.length > 0
      ? product.variants
      : [
          { id: `var-${product.id}-37`, sku: `SKU-37`, size: 37, color: "Royal Gold", color_hex: "#D4AF37", price: product.base_price, is_active: true },
          { id: `var-${product.id}-38`, sku: `SKU-38`, size: 38, color: "Royal Gold", color_hex: "#D4AF37", price: product.base_price, is_active: true },
          { id: `var-${product.id}-39`, sku: `SKU-39`, size: 39, color: "Royal Gold", color_hex: "#D4AF37", price: product.base_price, is_active: true },
        ];

  // Derive unique colors from variants
  const colorOptions: ColorOption[] = Array.from(
    new Set(safeVariants.map((v) => v.color))
  ).map((c) => {
    const v = safeVariants.find((item) => item.color === c);
    return {
      name: c,
      hex: v?.color_hex,
      inStock: true,
    };
  });

  // State
  const [selectedColor, setSelectedColor] = useState<string>(
    colorOptions[0]?.name || "Royal Gold"
  );
  const [selectedHeel, setSelectedHeel] = useState<string>("2 inch");
  const [selectedSize, setSelectedSize] = useState<number | null>(38);
  const [isAdding, setIsAdding] = useState(false);
  const [quantity, setQuantity] = useState(1);

  // Available heel options from product customizations or fallback to 1", 2", 3"
  const availableHeels =
    product.customizations && product.customizations.length > 0
      ? product.customizations.map((c) => c.value)
      : ["1 inch", "2 inch", "3 inch"];

  const handleAddToCart = () => {
    if (!selectedSize) {
      alert("Please select your European shoe size.");
      return;
    }

    setIsAdding(true);

    // Find matching variant if available
    const matchedVariant =
      safeVariants.find(
        (v) => v.color === selectedColor && v.size === selectedSize
      ) || safeVariants[0];

    addToCart({
      id: `cart-${product.id}-${selectedColor}-${selectedSize}-${selectedHeel}-${Date.now()}`,
      productId: product.id,
      variantId: matchedVariant?.id || `var-${product.id}`,
      name: product.name,
      slug: product.slug,
      price: product.base_price,
      quantity: quantity,
      heelSize: selectedHeel,
      size: `EU ${selectedSize}`,
      color: selectedColor,
      imageUrl: product.images?.[0]?.url || "/media/products/aurelia-champagne-main.webp",
    });

    setTimeout(() => {
      setIsAdding(false);
      openCart();
    }, 400);
  };

  return (
    <div className="space-y-6">
      {/* 1. Color Selector */}
      {colorOptions.length > 0 && (
        <ColorSelector
          colors={colorOptions}
          selectedColor={selectedColor}
          onSelectColor={setSelectedColor}
        />
      )}

      {/* 2. Heel Selector (Strictly 1", 2", 3") */}
      <HeelSelector
        selectedHeel={selectedHeel}
        onSelectHeel={setSelectedHeel}
        availableHeels={availableHeels}
      />

      {/* 3. Size Selector */}
      <SizeSelector
        selectedSize={selectedSize}
        onSelectSize={setSelectedSize}
      />

      {/* 4. Action Buttons */}
      <div className="pt-2 space-y-3">
        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleAddToCart}
            disabled={isAdding}
            className="flex-1 py-4 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-[0.2em] font-medium transition-all shadow-md flex items-center justify-center gap-2 group cursor-pointer disabled:opacity-75"
          >
            <ShoppingBag className="w-4 h-4 transition-transform group-hover:scale-110" />
            <span>
              {isAdding ? "Adding to Atelier Bag..." : `Add to Bag • ₹${typeof product.base_price === "number" ? product.base_price.toLocaleString("en-IN") : product.base_price}`}
            </span>
          </button>

          <button
            type="button"
            onClick={() => toggleWishlist(product.id)}
            className={`p-4 border transition-colors flex items-center justify-center ${
              isWishlisted
                ? "border-[#1C1917] bg-[#1C1917] text-[#C5A880]"
                : "border-[#E7E2DA] bg-white text-[#1C1917] hover:border-[#1C1917]"
            }`}
            aria-label={isWishlisted ? "Remove from wishlist" : "Save to wishlist"}
          >
            <Heart className={`w-5 h-5 ${isWishlisted ? "fill-current" : ""}`} />
          </button>
        </div>

        {/* Customization confirmation message */}
        <p className="text-[11px] text-[#78716C] text-center italic">
          Configured with bespoke <strong className="text-[#1C1917] font-medium">{selectedHeel}</strong> elevation in <strong className="text-[#1C1917] font-medium">{selectedColor}</strong>.
        </p>
      </div>
    </div>
  );
}
