"use client";

import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowUpDown,
  CheckCircle2,
  Package,
  Plus,
  RefreshCw,
  Search,
  Sliders,
  X,
  XCircle,
} from "lucide-react";
import { InventoryItemDto, adminService } from "@/services/admin.service";

export default function AdminInventoryPage() {
  const [items, setItems] = useState<InventoryItemDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<"ALL" | "LOW_STOCK" | "OUT_OF_STOCK">("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  // Restock Modal state
  const [selectedItem, setSelectedItem] = useState<InventoryItemDto | null>(null);
  const [newStock, setNewStock] = useState<number>(10);
  const [saving, setSaving] = useState(false);

  const loadInventory = async () => {
    setLoading(true);
    try {
      const data = await adminService.getInventory();
      setItems([...data]);
    } catch (e) {
      console.error("Failed to load inventory:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInventory();
  }, []);

  const handleRestockSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem) return;
    setSaving(true);
    await adminService.adjustStock(selectedItem.variant_id, Number(newStock));
    setSaving(false);
    setSelectedItem(null);
    loadInventory();
  };

  const filtered = items.filter((item) => {
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      if (!item.sku.toLowerCase().includes(q) && !item.product_name.toLowerCase().includes(q)) {
        return false;
      }
    }
    if (filterType === "LOW_STOCK") return item.is_low_stock && item.available_quantity > 0;
    if (filterType === "OUT_OF_STOCK") return !item.is_in_stock;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E7E2DA] pb-6">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block mb-1">
            Warehouse & Ledger
          </span>
          <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Inventory & Stock Tracking
          </h1>
        </div>

        <button
          type="button"
          onClick={loadInventory}
          className="p-2 border border-[#E7E2DA] bg-white hover:bg-[#FAF8F5] text-[#1C1917] self-start sm:self-auto"
          title="Refresh Ledger"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-4 bg-white border border-[#E7E2DA]">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-[#8C827A] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search SKU or model name..."
            className="w-full pl-9 pr-3 py-2 text-xs bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
          />
        </div>

        <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto">
          {(
            [
              { id: "ALL", label: "All SKUs" },
              { id: "LOW_STOCK", label: "Low Stock Alert" },
              { id: "OUT_OF_STOCK", label: "Depleted (0)" },
            ] as const
          ).map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setFilterType(tab.id)}
              className={`px-3 py-1.5 text-xs uppercase tracking-wider whitespace-nowrap transition-colors ${
                filterType === tab.id
                  ? "bg-[#1C1917] text-white font-medium"
                  : "bg-[#FAF8F5] text-[#57534E] hover:bg-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stock Ledger Table */}
      <div className="bg-white border border-[#E7E2DA] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-[#E7E2DA] bg-[#FAF8F5] text-[#8C827A] uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4">SKU Code</th>
                <th className="py-3 px-4">Footwear Silhouette</th>
                <th className="py-3 px-4">Variant Spec</th>
                <th className="py-3 px-4 text-center">Total Stock</th>
                <th className="py-3 px-4 text-center">Reserved</th>
                <th className="py-3 px-4 text-center">Available</th>
                <th className="py-3 px-4 text-center">Threshold</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Adjustment</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F0EDE8]">
              {filtered.map((item) => (
                <tr key={item.sku} className="hover:bg-[#FAF8F5] transition-colors">
                  <td className="py-3 px-4 font-mono font-semibold text-[#1C1917]">
                    {item.sku}
                  </td>
                  <td className="py-3 px-4 font-medium text-[#1C1917]">
                    {item.product_name}
                  </td>
                  <td className="py-3 px-4 text-[#57534E]">
                    <span className="font-medium text-[#1C1917]">EU {item.size}</span> • {item.color}
                  </td>
                  <td className="py-3 px-4 text-center font-medium text-[#1C1917]">
                    {item.stock_quantity}
                  </td>
                  <td className="py-3 px-4 text-center text-[#8C827A]">
                    {item.reserved_quantity}
                  </td>
                  <td className="py-3 px-4 text-center font-bold text-[#1C1917]">
                    {item.available_quantity}
                  </td>
                  <td className="py-3 px-4 text-center text-[#8C827A]">
                    {item.low_stock_threshold}
                  </td>
                  <td className="py-3 px-4">
                    {!item.is_in_stock ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-red-50 text-red-700 text-[10px] uppercase tracking-wider font-semibold">
                        <XCircle className="w-3 h-3" />
                        <span>Out of Stock</span>
                      </span>
                    ) : item.is_low_stock ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-50 text-amber-700 text-[10px] uppercase tracking-wider font-semibold">
                        <AlertTriangle className="w-3 h-3" />
                        <span>Low Stock</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] uppercase tracking-wider font-semibold">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>In Stock</span>
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedItem(item);
                        setNewStock(item.stock_quantity);
                      }}
                      className="px-2.5 py-1 bg-[#1C1917] hover:bg-[#C5A880] text-white text-[10px] uppercase tracking-wider font-medium transition-colors"
                    >
                      Adjust Stock
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Restock Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="w-full max-w-sm bg-white border border-[#E7E2DA] p-6 space-y-4 shadow-xl relative">
            <button
              onClick={() => setSelectedItem(null)}
              className="absolute top-4 right-4 text-[#8C827A] hover:text-[#1C1917]"
            >
              <X className="w-4 h-4" />
            </button>
            <h3 className="font-serif-luxury text-xl text-[#1C1917]">
              Restock SKU: {selectedItem.sku}
            </h3>
            <p className="text-xs text-[#78716C]">
              {selectedItem.product_name} (EU {selectedItem.size}, {selectedItem.color})
            </p>

            <form onSubmit={handleRestockSubmit} className="space-y-4 pt-2">
              <div>
                <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
                  New Total Stock Units
                </label>
                <input
                  type="number"
                  min={0}
                  required
                  value={newStock}
                  onChange={(e) => setNewStock(Number(e.target.value))}
                  className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
                />
                <span className="text-[10px] text-[#8C827A] mt-1 block">
                  Currently {selectedItem.reserved_quantity} unit(s) reserved by client bags.
                </span>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedItem(null)}
                  className="px-4 py-2 border border-[#E7E2DA] text-xs uppercase tracking-widest text-[#1C1917]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium"
                >
                  {saving ? "Updating..." : "Update Stock"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
