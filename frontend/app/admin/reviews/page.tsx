"use client";

import React, { useEffect, useState } from "react";
import { Check, CheckCircle2, MessageSquare, RefreshCw, Star, X, XCircle } from "lucide-react";
import { AdminReviewDto, adminService } from "@/services/admin.service";

export default function AdminReviewsPage() {
  const [reviews, setReviews] = useState<AdminReviewDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<"ALL" | "PENDING" | "APPROVED" | "REJECTED">("ALL");

  const loadReviews = async () => {
    setLoading(true);
    try {
      const data = await adminService.getReviews();
      setReviews([...data]);
    } catch (e) {
      console.error("Failed to load reviews:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviews();
  }, []);

  const handleAction = async (id: string, newStatus: "APPROVED" | "REJECTED") => {
    await adminService.updateReviewStatus(id, newStatus);
    loadReviews();
  };

  const filtered = reviews.filter((r) => {
    if (statusFilter !== "ALL" && r.status !== statusFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E7E2DA] pb-6">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block mb-1">
            Trust & Moderation
          </span>
          <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Client Review Moderation
          </h1>
        </div>

        <button
          type="button"
          onClick={loadReviews}
          className="p-2 border border-[#E7E2DA] bg-white hover:bg-[#FAF8F5] text-[#1C1917] self-start sm:self-auto"
          title="Refresh Reviews"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 p-2 bg-white border border-[#E7E2DA] overflow-x-auto">
        {(["ALL", "PENDING", "APPROVED", "REJECTED"] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setStatusFilter(tab)}
            className={`px-3 py-1.5 text-xs uppercase tracking-wider font-medium transition-colors ${
              statusFilter === tab
                ? "bg-[#1C1917] text-white"
                : "bg-transparent text-[#57534E] hover:text-[#1C1917]"
            }`}
          >
            {tab === "ALL" ? "All Reviews" : tab}
          </button>
        ))}
      </div>

      {/* Reviews List */}
      <div className="space-y-4">
        {filtered.map((rev) => (
          <div
            key={rev.id}
            className="p-6 bg-white border border-[#E7E2DA] flex flex-col md:flex-row md:items-center justify-between gap-6"
          >
            <div className="space-y-2 flex-1">
              <div className="flex items-center gap-3">
                {/* Star rating */}
                <div className="flex items-center gap-0.5">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <Star
                      key={s}
                      className={`w-3.5 h-3.5 ${
                        s <= rev.rating ? "fill-[#C5A880] text-[#C5A880]" : "text-stone-300"
                      }`}
                    />
                  ))}
                </div>

                <span className="font-semibold text-sm text-[#1C1917]">
                  {rev.title}
                </span>

                {/* Status Badge */}
                <span
                  className={`px-2 py-0.5 text-[10px] uppercase tracking-wider font-semibold ${
                    rev.status === "APPROVED"
                      ? "bg-emerald-50 text-emerald-700"
                      : rev.status === "REJECTED"
                      ? "bg-red-50 text-red-700"
                      : "bg-amber-50 text-amber-700"
                  }`}
                >
                  {rev.status}
                </span>
              </div>

              <p className="text-xs text-[#57534E] leading-relaxed max-w-2xl font-light">
                "{rev.comment}"
              </p>

              <div className="text-[11px] text-[#8C827A] flex items-center gap-3 pt-1">
                <span>
                  By <strong className="text-[#1C1917]">{rev.user_name}</strong>
                </span>
                <span>•</span>
                <span>{rev.product_name}</span>
                <span>•</span>
                <span>{new Date(rev.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            {/* Moderation Action Buttons */}
            <div className="flex items-center gap-2 self-end md:self-auto shrink-0">
              {rev.status !== "APPROVED" && (
                <button
                  type="button"
                  onClick={() => handleAction(rev.id, "APPROVED")}
                  className="px-3 py-1.5 bg-[#0A4D2E] hover:bg-emerald-800 text-white text-xs uppercase tracking-wider font-medium flex items-center gap-1 transition-colors"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Approve</span>
                </button>
              )}

              {rev.status !== "REJECTED" && (
                <button
                  type="button"
                  onClick={() => handleAction(rev.id, "REJECTED")}
                  className="px-3 py-1.5 bg-red-700 hover:bg-red-800 text-white text-xs uppercase tracking-wider font-medium flex items-center gap-1 transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Reject</span>
                </button>
              )}
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="py-12 text-center text-sm text-[#8C827A] bg-white border border-[#E7E2DA]">
            No reviews matching status "{statusFilter}".
          </div>
        )}
      </div>
    </div>
  );
}
