"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Check, Plus, Sparkles } from "lucide-react";
import { adminService } from "@/services/admin.service";
import { FALLBACK_CATEGORIES, FALLBACK_COLLECTIONS } from "@/services/product.service";

export default function NewProductPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [basePrice, setBasePrice] = useState("360");
  const [categoryName, setCategoryName] = useState(FALLBACK_CATEGORIES[0].name);
  const [collectionName, setCollectionName] = useState(FALLBACK_COLLECTIONS[0].name);
  const [material, setMaterial] = useState("Italian Silk Satin & Austrian Crystals");
  const [occasion, setOccasion] = useState("Bridal & Gala");
  const [style, setStyle] = useState("Pointed Toe Stiletto");
  const [description, setDescription] = useState(
    "Handcrafted in Florence from lustrous Italian silk satin with ergonomic memory foam footbeds."
  );
  const [imageUrl, setImageUrl] = useState("/media/products/aurelia-champagne-main.webp");
  const [submitting, setSubmitting] = useState(false);

  // Heel choices strictly 1", 2", 3"
  const [heel1, setHeel1] = useState(true);
  const [heel2, setHeel2] = useState(true);
  const [heel3, setHeel3] = useState(true);

  const [uploadingImage, setUploadingImage] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;

    setUploadingImage(true);
    try {
      // 1. Upload to permanent Next.js disk storage
      const formData = new FormData();
      formData.append("file", f);
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        if (data.url) {
          setImageUrl(data.url);
          setUploadingImage(false);
          return;
        }
      }
    } catch (err) {
      console.warn("API upload failed, using Base64 data URL fallback", err);
    }

    // 2. Fallback: Permanent Base64 Data URL (stored directly in localStorage)
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") {
        setImageUrl(reader.result);
      }
      setUploadingImage(false);
    };
    reader.onerror = () => {
      setUploadingImage(false);
    };
    reader.readAsDataURL(f);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const selectedCategory = FALLBACK_CATEGORIES.find((c) => c.name === categoryName) || FALLBACK_CATEGORIES[0];
      const selectedCollection = FALLBACK_COLLECTIONS.find((c) => c.name === collectionName);

      const customizations = [];
      if (heel1) customizations.push({ id: "c1", type: "HEEL_SIZE" as const, value: "1 inch", display_name: "1 inch (Kitten Low)", additional_price: 0, is_available: true });
      if (heel2) customizations.push({ id: "c2", type: "HEEL_SIZE" as const, value: "2 inch", display_name: "2 inch (Mid Block)", additional_price: 0, is_available: true });
      if (heel3) customizations.push({ id: "c3", type: "HEEL_SIZE" as const, value: "3 inch", display_name: "3 inch (Classic Stiletto)", additional_price: 0, is_available: true });

      await adminService.createProduct({
        name,
        base_price: Number(basePrice),
        category: selectedCategory,
        collection: selectedCollection,
        material,
        occasion,
        style,
        description,
        images: [
          {
            id: `img-${Date.now()}`,
            url: imageUrl,
            sort_order: 0,
            is_primary: true,
          },
        ],
        customizations,
      });

      router.push("/admin/products");
    } catch (e) {
      console.error("Failed to create product:", e);
      router.push("/admin/products");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back button & Title */}
      <div className="space-y-2 border-b border-[#E7E2DA] pb-6">
        <Link
          href="/admin/products"
          className="inline-flex items-center gap-1.5 text-xs text-[#8C827A] hover:text-[#1C1917] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Products</span>
        </Link>
        <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
          Atelier Creation
        </span>
        <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
          Add New Footwear Silhouette
        </h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 sm:p-8 border border-[#E7E2DA]">
        {/* Core Product Info */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Silhouette Name
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Aurelia Crystal Satin Pump"
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>

          <div>
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Base Price (INR / ₹)
            </label>
            <input
              type="number"
              required
              min={1}
              value={basePrice}
              onChange={(e) => setBasePrice(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>

          <div>
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Category
            </label>
            <select
              value={categoryName}
              onChange={(e) => setCategoryName(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            >
              {FALLBACK_CATEGORIES.map((c) => (
                <option key={c.id} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Collection Capsule
            </label>
            <select
              value={collectionName}
              onChange={(e) => setCollectionName(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            >
              {FALLBACK_COLLECTIONS.map((col) => (
                <option key={col.id} value={col.name}>
                  {col.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Style Silhouette
            </label>
            <input
              type="text"
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              placeholder="e.g. Pointed Toe Stiletto"
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Material & Crafting Description
            </label>
            <input
              type="text"
              value={material}
              onChange={(e) => setMaterial(e.target.value)}
              placeholder="e.g. Italian Silk Satin & Austrian Crystal Brooch"
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Editorial Description
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>

          <div className="sm:col-span-2 space-y-2">
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Primary Product Imagery (Upload File or Asset Path)
            </label>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <label className="cursor-pointer px-4 py-2 bg-[#FAF8F5] border border-[#E7E2DA] hover:border-[#1C1917] text-xs text-[#1C1917] font-medium flex items-center gap-2 transition-colors">
                <span>{uploadingImage ? "Uploading & Saving..." : "Select Image File"}</span>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  disabled={uploadingImage}
                  onChange={handleFileChange}
                />
              </label>
              <span className="text-xs text-[#8C827A]">or enter direct URL / path:</span>
              <input
                type="text"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="/media/products/leela-royal-wedge/LeelaKeyHighlightCard.webp"
                className="flex-1 w-full px-3 py-2 text-xs bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
              />
            </div>
            {imageUrl && (
              <div className="flex items-center gap-3 pt-2">
                <div className="w-16 h-20 bg-[#F5F2EB] border border-[#E7E2DA] overflow-hidden">
                  <img src={imageUrl} alt="Preview" className="w-full h-full object-cover" />
                </div>
                <span className="text-[11px] text-[#0A4D2E] font-medium">
                  {uploadingImage ? "Saving image to disk..." : "Image saved permanently and ready."}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Bespoke Heel Customization Checkboxes (Strictly 1", 2", 3") */}
        <div className="pt-4 border-t border-[#F0EDE8] space-y-3">
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-[#C5A880]" />
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917]">
              Bespoke Heel Customizations (Scope Restricted: 1", 2", 3")
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <label className="p-3 border border-[#E7E2DA] bg-[#FAF8F5] flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={heel1}
                onChange={(e) => setHeel1(e.target.checked)}
                className="w-4 h-4 accent-[#1C1917]"
              />
              <div>
                <strong className="block text-xs font-semibold text-[#1C1917]">1 inch</strong>
                <span className="text-[11px] text-[#8C827A]">Kitten & Low Lift (2.5 cm)</span>
              </div>
            </label>

            <label className="p-3 border border-[#E7E2DA] bg-[#FAF8F5] flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={heel2}
                onChange={(e) => setHeel2(e.target.checked)}
                className="w-4 h-4 accent-[#1C1917]"
              />
              <div>
                <strong className="block text-xs font-semibold text-[#1C1917]">2 inch</strong>
                <span className="text-[11px] text-[#8C827A]">Mid Architectural (5.0 cm)</span>
              </div>
            </label>

            <label className="p-3 border border-[#E7E2DA] bg-[#FAF8F5] flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={heel3}
                onChange={(e) => setHeel3(e.target.checked)}
                className="w-4 h-4 accent-[#1C1917]"
              />
              <div>
                <strong className="block text-xs font-semibold text-[#1C1917]">3 inch</strong>
                <span className="text-[11px] text-[#8C827A]">Classic Stiletto (7.5 cm)</span>
              </div>
            </label>
          </div>
        </div>

        {/* Submit Actions */}
        <div className="pt-6 border-t border-[#F0EDE8] flex items-center justify-end gap-3">
          <Link
            href="/admin/products"
            className="px-4 py-2.5 border border-[#E7E2DA] text-xs uppercase tracking-widest text-[#1C1917] hover:bg-[#FAF8F5]"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2.5 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors"
          >
            {submitting ? "Publishing to Atelier..." : "Publish Silhouette"}
          </button>
        </div>
      </form>
    </div>
  );
}
