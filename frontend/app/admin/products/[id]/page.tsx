"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Check, Sparkles } from "lucide-react";
import { adminService } from "@/services/admin.service";
import { FALLBACK_CATEGORIES, FALLBACK_COLLECTIONS } from "@/services/product.service";
import { Product } from "@/types";

export default function EditProductPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  const [loading, setLoading] = useState(true);
  const [product, setProduct] = useState<Product | null>(null);
  const [name, setName] = useState("");
  const [basePrice, setBasePrice] = useState("360");
  const [categoryName, setCategoryName] = useState("");
  const [material, setMaterial] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function load() {
      if (!id) return;
      const p = await adminService.getProductById(id);
      if (p) {
        setProduct(p);
        setName(p.name);
        setBasePrice(String(p.base_price));
        setCategoryName(p.category?.name || FALLBACK_CATEGORIES[0].name);
        setMaterial(p.material || "");
        setDescription(p.description || "");
      }
      setLoading(false);
    }
    load();
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const selectedCat = FALLBACK_CATEGORIES.find((c) => c.name === categoryName) || FALLBACK_CATEGORIES[0];
      await adminService.updateProduct(id, {
        name,
        base_price: Number(basePrice),
        category: selectedCat,
        material,
        description,
      });
      router.push("/admin/products");
    } catch (e) {
      console.error("Update failed:", e);
      router.push("/admin/products");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-xs text-[#8C827A]">Loading product details...</div>;
  }

  if (!product) {
    return (
      <div className="py-12 text-center space-y-4">
        <p className="text-sm text-[#1C1917]">Product not found.</p>
        <Link href="/admin/products" className="text-xs text-[#C5A880] underline">
          Return to products
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="space-y-2 border-b border-[#E7E2DA] pb-6">
        <Link
          href="/admin/products"
          className="inline-flex items-center gap-1.5 text-xs text-[#8C827A] hover:text-[#1C1917] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Products</span>
        </Link>
        <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
          Modify Footwear
        </span>
        <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
          Edit: {product.name}
        </h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 sm:p-8 border border-[#E7E2DA]">
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
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>

          <div>
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Base Price (USD)
            </label>
            <input
              type="number"
              required
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

          <div className="sm:col-span-2">
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Material
            </label>
            <input
              type="text"
              value={material}
              onChange={(e) => setMaterial(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
              Description
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>
        </div>

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
            {submitting ? "Saving Updates..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
