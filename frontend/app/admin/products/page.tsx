"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowUpDown,
  Box,
  Edit2,
  ExternalLink,
  Plus,
  RefreshCw,
  Search,
  Sparkles,
  Trash2,
} from "lucide-react";
import { Product } from "@/types";
import { adminService } from "@/services/admin.service";

export default function AdminProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await adminService.getProducts();
      setProducts(data);
    } catch (e) {
      console.error("Failed to load products:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleDelete = async (id: string, name: string) => {
    if (confirm(`Are you sure you want to remove "${name}" from the atelier catalog?`)) {
      await adminService.deleteProduct(id);
      loadProducts();
    }
  };

  const filtered = products.filter((p) => {
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      if (!p.name.toLowerCase().includes(q) && !p.description.toLowerCase().includes(q)) {
        return false;
      }
    }
    if (selectedCategory !== "all" && p.category?.name !== selectedCategory) {
      return false;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E7E2DA] pb-6">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block mb-1">
            Catalog Management
          </span>
          <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Footwear Silhouettes
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={loadProducts}
            className="p-2 border border-[#E7E2DA] bg-white hover:bg-[#FAF8F5] text-[#1C1917]"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <Link
            href="/admin/products/new"
            className="px-4 py-2 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add New Silhouette</span>
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-4 bg-white border border-[#E7E2DA]">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-[#8C827A] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter by name, silk, or leather..."
            className="w-full pl-9 pr-3 py-2 text-xs bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs text-[#8C827A] font-medium">Category:</span>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 text-xs bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
          >
            <option value="all">All Categories</option>
            <option value="Bridal & Evening">Bridal & Evening</option>
            <option value="Stilettos & High Heels">Stilettos & High Heels</option>
            <option value="Mules & Slides">Mules & Slides</option>
            <option value="Luxury Flats & Loafers">Luxury Flats & Loafers</option>
          </select>
        </div>
      </div>

      {/* Products Table */}
      <div className="bg-white border border-[#E7E2DA] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-[#E7E2DA] bg-[#FAF8F5] text-[#8C827A] uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4">Silhouette</th>
                <th className="py-3 px-4">Category & Collection</th>
                <th className="py-3 px-4">Base Price</th>
                <th className="py-3 px-4">Bespoke Heel Heights</th>
                <th className="py-3 px-4">Variants</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F0EDE8]">
              {filtered.map((product) => (
                <tr key={product.id} className="hover:bg-[#FAF8F5] transition-colors">
                  {/* Image & Name */}
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-14 bg-[#F5F2EB] border border-[#E7E2DA] overflow-hidden shrink-0">
                        <img
                          src={product.images[0]?.url || "/media/products/aurelia-champagne-main.webp"}
                          alt={product.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div>
                        <div className="font-semibold text-sm text-[#1C1917]">
                          {product.name}
                        </div>
                        <div className="text-[11px] text-[#8C827A] font-mono">
                          /{product.slug}
                        </div>
                      </div>
                    </div>
                  </td>

                  {/* Category & Collection */}
                  <td className="py-3 px-4 text-[#57534E]">
                    <div className="font-medium text-[#1C1917]">{product.category?.name}</div>
                    <div className="text-[10px] text-[#C5A880] uppercase tracking-wider">
                      {product.collection?.name || "Permanent Collection"}
                    </div>
                  </td>

                  {/* Base Price */}
                  <td className="py-3 px-4 font-semibold text-sm text-[#1C1917]">
                    ₹{typeof product.base_price === "number" ? product.base_price.toLocaleString("en-IN") : product.base_price}
                  </td>

                  {/* Heel Customizations */}
                  <td className="py-3 px-4">
                    <div className="flex gap-1.5">
                      {product.customizations?.map((c) => (
                        <span
                          key={c.id || c.value}
                          className="px-2 py-0.5 bg-[#FAF8F5] border border-[#E7E2DA] text-[10px] text-[#1C1917] font-medium"
                        >
                          {c.value}
                        </span>
                      )) || (
                        <span className="text-[10px] text-[#8C827A]">1", 2", 3"</span>
                      )}
                    </div>
                  </td>

                  {/* Variants */}
                  <td className="py-3 px-4 text-[#57534E]">
                    <span className="font-medium text-[#1C1917]">
                      {product.variants?.length || 4}
                    </span>{" "}
                    sizes/shades
                  </td>

                  {/* Actions */}
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        href={`/products/${product.slug}`}
                        target="_blank"
                        className="p-1.5 text-[#8C827A] hover:text-[#1C1917] transition-colors"
                        title="View Public PDP"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </Link>
                      <Link
                        href={`/admin/products/${product.id}`}
                        className="p-1.5 text-[#8C827A] hover:text-[#C5A880] transition-colors"
                        title="Edit Silhouette"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </Link>
                      <button
                        type="button"
                        onClick={() => handleDelete(product.id, product.name)}
                        className="p-1.5 text-[#8C827A] hover:text-red-700 transition-colors"
                        title="Delete Silhouette"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
