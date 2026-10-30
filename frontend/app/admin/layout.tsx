"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bell,
  Box,
  ChevronRight,
  ExternalLink,
  FolderTree,
  Layers,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  Package,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Users,
  Wand2,
} from "lucide-react";
import { useStore } from "@/context/StoreContext";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, login, logout } = useStore();

  const navItems = [
    { label: "Dashboard", href: "/admin", icon: LayoutDashboard },
    { label: "Products Catalog", href: "/admin/products", icon: Box },
    { label: "Categories", href: "/admin/categories", icon: FolderTree },
    { label: "Collections", href: "/admin/collections", icon: Layers },
    { label: "Inventory & Stock", href: "/admin/inventory", icon: Package },
    { label: "Review Moderation", href: "/admin/reviews", icon: MessageSquare },
    { label: "Clients & Users", href: "/admin/users", icon: Users },
    { label: "Recommendation AI", href: "/admin/recommendations", icon: Wand2 },
    { label: "Notifications", href: "/admin/notifications", icon: Bell },
  ];

  const handleSwitchToAdmin = () => {
    login("mock_admin_jwt", {
      id: "usr-admin-01",
      email: "admin@ibrat.com",
      full_name: "Chiara Rossi (Director)",
      role: "ADMIN",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  };

  const isAdmin = user?.role === "ADMIN";

  return (
    <div className="min-h-screen bg-[#F5F2EB] flex flex-col">
      {/* Top Admin Bar */}
      <header className="bg-[#1C1917] text-white border-b border-[#292524] px-4 sm:px-8 py-3 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-4">
          <Link href="/admin" className="flex items-center gap-2">
            <span className="font-serif-luxury text-xl tracking-[0.2em] font-medium text-white uppercase">
              IBRAT
            </span>
            <span className="text-[9px] uppercase tracking-widest text-[#C5A880] px-2 py-0.5 bg-black/40 border border-[#C5A880]/30 font-sans font-semibold">
              Atelier Management
            </span>
          </Link>

          <span className="hidden md:inline text-xs text-stone-500">|</span>

          <span className="hidden md:flex items-center gap-1.5 text-xs text-stone-400">
            <Sparkles className="w-3.5 h-3.5 text-[#C5A880]" />
            <span>Florence Master Console</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          {/* Link back to public storefront */}
          <Link
            href="/"
            target="_blank"
            className="flex items-center gap-1.5 text-xs text-stone-300 hover:text-white transition-colors px-3 py-1.5 border border-stone-700 bg-stone-900 rounded-none"
          >
            <span>View Live Store</span>
            <ExternalLink className="w-3 h-3 text-[#C5A880]" />
          </Link>

          {/* User role & status */}
          {user ? (
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <div className="text-xs font-medium text-white">{user.full_name}</div>
                <div className="text-[10px] uppercase tracking-wider text-[#C5A880]">
                  {user.role}
                </div>
              </div>
              <button
                type="button"
                onClick={logout}
                className="p-1.5 text-stone-400 hover:text-white transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={handleSwitchToAdmin}
              className="px-3 py-1.5 bg-[#C5A880] hover:bg-white text-[#1C1917] text-xs uppercase tracking-wider font-semibold transition-colors"
            >
              Enable Admin Mode
            </button>
          )}
        </div>
      </header>

      {/* Main Container: Sidebar + Content */}
      <div className="flex-1 flex max-w-[1600px] w-full mx-auto">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-[#E7E2DA] p-4 hidden lg:flex flex-col justify-between shrink-0">
          <nav className="space-y-1">
            <div className="px-3 py-2 text-[10px] uppercase tracking-widest text-[#8C827A] font-semibold">
              Management Modules
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3.5 py-2.5 text-xs uppercase tracking-wider font-medium transition-all ${
                    isActive
                      ? "bg-[#1C1917] text-white shadow-xs"
                      : "text-[#57534E] hover:bg-[#FAF8F5] hover:text-[#1C1917]"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? "text-[#C5A880]" : "text-[#8C827A]"}`} />
                    <span>{item.label}</span>
                  </div>
                  {isActive && <ChevronRight className="w-3.5 h-3.5 text-[#C5A880]" />}
                </Link>
              );
            })}
          </nav>

          <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] text-[11px] text-[#78716C] space-y-1">
            <strong className="block text-[#1C1917] font-semibold">Atelier Policy Note</strong>
            <p className="font-light">
              Heel custom heights are strictly restricted to 1", 2", and 3". Purchasing boundaries conclude at cart.
            </p>
          </div>
        </aside>

        {/* Content Area */}
        <main className="flex-1 p-4 sm:p-8 overflow-y-auto">
          {!isAdmin && (
            <div className="mb-6 p-4 bg-amber-50 border border-amber-200 text-amber-900 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0" />
                <span>
                  You are previewing the Admin Console. Click to activate full Atelier Director rights.
                </span>
              </div>
              <button
                type="button"
                onClick={handleSwitchToAdmin}
                className="px-3 py-1.5 bg-[#1C1917] text-white hover:bg-[#C5A880] transition-colors uppercase tracking-wider font-medium"
              >
                Activate Admin Role
              </button>
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
