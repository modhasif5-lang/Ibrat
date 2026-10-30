"use client";

import React, { useEffect, useState } from "react";
import { FolderTree, Plus, Sparkles, X } from "lucide-react";
import { Category } from "@/types";
import { adminService } from "@/services/admin.service";

export default function AdminCategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    const data = await adminService.getCategories();
    setCategories([...data]);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    await adminService.createCategory({ name, description });
    setName("");
    setDescription("");
    setModalOpen(false);
    setSubmitting(false);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E7E2DA] pb-6">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block mb-1">
            Taxonomy & Navigation
          </span>
          <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Footwear Categories
          </h1>
        </div>

        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="px-4 py-2 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors flex items-center gap-1.5 self-start sm:self-auto"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Category</span>
        </button>
      </div>

      {/* Categories Grid / Table */}
      <div className="bg-white border border-[#E7E2DA] overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-[#E7E2DA] bg-[#FAF8F5] text-[#8C827A] uppercase tracking-wider text-[11px]">
              <th className="py-3 px-4">Category Name</th>
              <th className="py-3 px-4">URL Slug</th>
              <th className="py-3 px-4">Description</th>
              <th className="py-3 px-4">Silhouettes Count</th>
              <th className="py-3 px-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F0EDE8]">
            {categories.map((c) => (
              <tr key={c.id} className="hover:bg-[#FAF8F5] transition-colors">
                <td className="py-3.5 px-4 font-semibold text-sm text-[#1C1917]">
                  {c.name}
                </td>
                <td className="py-3.5 px-4 font-mono text-[#8C827A]">
                  /categories/{c.slug}
                </td>
                <td className="py-3.5 px-4 text-[#78716C] max-w-xs truncate">
                  {c.description || "Atelier footwear category"}
                </td>
                <td className="py-3.5 px-4 font-medium text-[#1C1917]">
                  {c.product_count ?? 1} pairs
                </td>
                <td className="py-3.5 px-4 text-right">
                  <span className="px-2 py-0.5 bg-[#E8F3EC] text-[#0A4D2E] text-[10px] uppercase tracking-wider font-semibold">
                    Active
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="w-full max-w-md bg-white border border-[#E7E2DA] p-6 space-y-4 shadow-xl relative">
            <button
              onClick={() => setModalOpen(false)}
              className="absolute top-4 right-4 text-[#8C827A] hover:text-[#1C1917]"
            >
              <X className="w-4 h-4" />
            </button>
            <h3 className="font-serif-luxury text-xl text-[#1C1917]">
              Create Footwear Category
            </h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
                  Category Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Sculpted Wedges"
                  className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
                  Description
                </label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Short description for collection banners..."
                  className="w-full px-3 py-2 text-sm bg-[#FAF8F5] border border-[#E7E2DA] text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 border border-[#E7E2DA] text-xs uppercase tracking-widest text-[#1C1917]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
