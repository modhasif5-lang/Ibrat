"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  ArrowUpRight,
  Box,
  CheckCircle2,
  Clock,
  Layers,
  MessageSquare,
  Package,
  Plus,
  RefreshCw,
  Server,
  Sparkles,
  Users,
} from "lucide-react";
import { AdminStats, adminService } from "@/services/admin.service";

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const s = await adminService.getDashboardStats();
      setStats(s);
    } catch (e) {
      console.error("Failed to load admin stats:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="space-y-8">
      {/* Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E7E2DA] pb-6">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block mb-1">
            Overview & Telemetry
          </span>
          <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Atelier Executive Console
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={fetchStats}
            className="p-2 border border-[#E7E2DA] bg-white hover:bg-[#FAF8F5] text-[#1C1917] transition-colors"
            title="Refresh Metrics"
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

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Footwear Products */}
        <div className="bg-white border border-[#E7E2DA] p-6 space-y-3">
          <div className="flex items-center justify-between text-[#8C827A]">
            <span className="text-xs uppercase tracking-wider font-semibold">Silhouettes</span>
            <Box className="w-4 h-4 text-[#C5A880]" />
          </div>
          <div className="text-3xl font-serif-luxury font-medium text-[#1C1917]">
            {stats ? stats.totalProducts : "..."}
          </div>
          <div className="text-[11px] text-[#78716C] flex items-center justify-between pt-1 border-t border-[#F0EDE8]">
            <span>1", 2", 3" Heel Ready</span>
            <Link href="/admin/products" className="text-[#C5A880] hover:underline font-medium">
              Manage →
            </Link>
          </div>
        </div>

        {/* Total Stock Units */}
        <div className="bg-white border border-[#E7E2DA] p-6 space-y-3">
          <div className="flex items-center justify-between text-[#8C827A]">
            <span className="text-xs uppercase tracking-wider font-semibold">Inventory Stock</span>
            <Package className="w-4 h-4 text-[#C5A880]" />
          </div>
          <div className="text-3xl font-serif-luxury font-medium text-[#1C1917]">
            {stats ? stats.totalStockUnits : "..."}
          </div>
          <div className="text-[11px] text-[#78716C] flex items-center justify-between pt-1 border-t border-[#F0EDE8]">
            <span>Active SKU variants</span>
            <Link href="/admin/inventory" className="text-[#C5A880] hover:underline font-medium">
              Stock Ledger →
            </Link>
          </div>
        </div>

        {/* Low Stock Alerts */}
        <div className="bg-white border border-[#E7E2DA] p-6 space-y-3">
          <div className="flex items-center justify-between text-[#8C827A]">
            <span className="text-xs uppercase tracking-wider font-semibold">Low Stock Items</span>
            <AlertTriangle className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-3xl font-serif-luxury font-medium text-amber-600">
            {stats ? stats.lowStockItemsCount : "..."}
          </div>
          <div className="text-[11px] text-[#78716C] flex items-center justify-between pt-1 border-t border-[#F0EDE8]">
            <span>Requires restocking</span>
            <Link href="/admin/inventory" className="text-amber-700 hover:underline font-medium">
              Restock Now →
            </Link>
          </div>
        </div>

        {/* Pending Reviews Moderation */}
        <div className="bg-white border border-[#E7E2DA] p-6 space-y-3">
          <div className="flex items-center justify-between text-[#8C827A]">
            <span className="text-xs uppercase tracking-wider font-semibold">Pending Reviews</span>
            <MessageSquare className="w-4 h-4 text-[#C5A880]" />
          </div>
          <div className="text-3xl font-serif-luxury font-medium text-[#1C1917]">
            {stats ? stats.pendingReviewsCount : "..."}
          </div>
          <div className="text-[11px] text-[#78716C] flex items-center justify-between pt-1 border-t border-[#F0EDE8]">
            <span>Client submissions</span>
            <Link href="/admin/reviews" className="text-[#C5A880] hover:underline font-medium">
              Moderate →
            </Link>
          </div>
        </div>
      </div>

      {/* Microservice Architecture Health Status */}
      <div className="bg-white border border-[#E7E2DA] p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between border-b border-[#F0EDE8] pb-4">
          <div>
            <h2 className="font-serif-luxury text-lg text-[#1C1917]">
              Distributed Microservices Mesh Status
            </h2>
            <p className="text-xs text-[#8C827A]">
              Real-time telemetry across the 5 isolated domain microservices and event brokers
            </p>
          </div>
          <span className="px-2.5 py-1 bg-[#E8F3EC] text-[#0A4D2E] text-[10px] uppercase tracking-wider font-semibold flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>All Systems Healthy</span>
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { name: "User Service", port: ":8001", db: "user_db", status: "Healthy" },
            { name: "Product Service", port: ":8002", db: "product_db", status: "Healthy" },
            { name: "Search Service", port: ":8003", db: "Elasticsearch", status: "Healthy" },
            { name: "Cart Service", port: ":8004", db: "cart_db", status: "Healthy" },
            { name: "Inventory Service", port: ":8005", db: "inventory_db", status: "Healthy" },
            { name: "Kafka Event Bus", port: ":9092", db: "Zookeeper", status: "Active" },
          ].map((srv) => (
            <div key={srv.name} className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] space-y-1">
              <div className="flex items-center justify-between">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[10px] text-[#8C827A] font-mono">{srv.port}</span>
              </div>
              <div className="text-xs font-semibold text-[#1C1917] truncate">{srv.name}</div>
              <div className="text-[10px] text-[#78716C]">{srv.db}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions & Recent Atelier Events */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Launch Cards */}
        <div className="space-y-4">
          <h2 className="font-serif-luxury text-lg text-[#1C1917]">
            Atelier Actions
          </h2>
          <div className="space-y-3">
            <Link
              href="/admin/products/new"
              className="p-4 bg-white border border-[#E7E2DA] hover:border-[#C5A880] block transition-colors group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-[#1C1917] uppercase tracking-wider group-hover:text-[#C5A880]">
                  + New Footwear Silhouette
                </span>
                <ArrowRight className="w-4 h-4 text-[#8C827A] group-hover:translate-x-1 transition-transform" />
              </div>
              <p className="text-xs text-[#78716C] mt-1 font-light">
                Configure silk materials, heel customization heights (1", 2", 3"), and size variants.
              </p>
            </Link>

            <Link
              href="/admin/inventory"
              className="p-4 bg-white border border-[#E7E2DA] hover:border-[#C5A880] block transition-colors group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-[#1C1917] uppercase tracking-wider group-hover:text-[#C5A880]">
                  Restock Low Stock Units
                </span>
                <ArrowRight className="w-4 h-4 text-[#8C827A] group-hover:translate-x-1 transition-transform" />
              </div>
              <p className="text-xs text-[#78716C] mt-1 font-light">
                Inspect variant stock ledgers and apply instant inventory adjustments.
              </p>
            </Link>

            <Link
              href="/admin/recommendations"
              className="p-4 bg-white border border-[#E7E2DA] hover:border-[#C5A880] block transition-colors group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-[#1C1917] uppercase tracking-wider group-hover:text-[#C5A880]">
                  Tune Recommendation AI
                </span>
                <ArrowRight className="w-4 h-4 text-[#8C827A] group-hover:translate-x-1 transition-transform" />
              </div>
              <p className="text-xs text-[#78716C] mt-1 font-light">
                Adjust multi-signal weights (Heel 25%, Category 35%) and clear Redis cache.
              </p>
            </Link>
          </div>
        </div>

        {/* Recent Event Feed */}
        <div className="lg:col-span-2 bg-white border border-[#E7E2DA] p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-[#F0EDE8] pb-3">
            <h2 className="font-serif-luxury text-lg text-[#1C1917]">
              Atelier Real-time Activity
            </h2>
            <Link href="/admin/notifications" className="text-xs text-[#C5A880] hover:underline font-medium">
              View All Logs
            </Link>
          </div>

          <div className="divide-y divide-[#F0EDE8] text-xs">
            {[
              {
                icon: AlertTriangle,
                color: "text-amber-600",
                title: "Low stock alert triggered",
                desc: "GIS-MUL-ROU-38 stock quantity dropped to 0 units",
                time: "2 hours ago",
              },
              {
                icon: MessageSquare,
                color: "text-[#C5A880]",
                title: "Client review submitted",
                desc: "5-star review submitted for Seraphina Nappa Ankle-Strap Heel by Claire Dupont",
                time: "4 hours ago",
              },
              {
                icon: Box,
                color: "text-blue-600",
                title: "Catalog domain event published",
                desc: "Product 'Camilla Bow D'Orsay Slingback' broadcasted to Kafka product.created topic",
                time: "1 day ago",
              },
              {
                icon: CheckCircle2,
                color: "text-emerald-600",
                title: "Inventory reservation released",
                desc: "Guest session cart expired; 2 units returned to available stock",
                time: "2 days ago",
              },
            ].map((event, idx) => {
              const Icon = event.icon;
              return (
                <div key={idx} className="py-3.5 flex items-start gap-3">
                  <div className={`p-2 bg-[#FAF8F5] border border-[#E7E2DA] shrink-0 ${event.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 space-y-0.5">
                    <div className="font-semibold text-[#1C1917]">{event.title}</div>
                    <div className="text-[#78716C] font-light">{event.desc}</div>
                  </div>
                  <span className="text-[11px] text-[#A8A29E] shrink-0">{event.time}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
