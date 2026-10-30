"use client";

import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  Bell,
  Box,
  Check,
  CheckCheck,
  CheckCircle2,
  MessageSquare,
  RefreshCw,
} from "lucide-react";
import { AdminNotificationDto, adminService } from "@/services/admin.service";

export default function AdminNotificationsPage() {
  const [notifications, setNotifications] = useState<AdminNotificationDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [onlyUnread, setOnlyUnread] = useState(false);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const data = await adminService.getNotifications();
      setNotifications([...data]);
    } catch (e) {
      console.error("Failed to load notifications:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleMarkRead = async (id: string) => {
    await adminService.markNotificationRead(id);
    loadNotifications();
  };

  const filtered = notifications.filter((n) => {
    if (onlyUnread && n.read) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E7E2DA] pb-6">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block mb-1">
            System Events & Alerts
          </span>
          <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Atelier Notifications
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setOnlyUnread(!onlyUnread)}
            className={`px-3 py-1.5 text-xs uppercase tracking-wider font-medium border transition-colors ${
              onlyUnread
                ? "bg-[#1C1917] text-white border-[#1C1917]"
                : "bg-white text-[#57534E] border-[#E7E2DA]"
            }`}
          >
            {onlyUnread ? "Showing Unread Only" : "Show All"}
          </button>
          <button
            type="button"
            onClick={loadNotifications}
            className="p-2 border border-[#E7E2DA] bg-white hover:bg-[#FAF8F5] text-[#1C1917]"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {filtered.map((notif) => {
          let Icon = Bell;
          let color = "text-[#C5A880]";
          if (notif.type === "LOW_STOCK") {
            Icon = AlertTriangle;
            color = "text-amber-600";
          } else if (notif.type === "NEW_REVIEW") {
            Icon = MessageSquare;
            color = "text-[#C5A880]";
          } else if (notif.type === "PRODUCT_CREATED") {
            Icon = Box;
            color = "text-blue-600";
          }

          return (
            <div
              key={notif.id}
              className={`p-5 bg-white border transition-colors flex items-start justify-between gap-4 ${
                notif.read ? "border-[#E7E2DA] opacity-80" : "border-[#1C1917] shadow-xs"
              }`}
            >
              <div className="flex items-start gap-4">
                <div className={`p-2.5 bg-[#FAF8F5] border border-[#E7E2DA] shrink-0 ${color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-sm text-[#1C1917]">
                      {notif.title}
                    </h3>
                    {!notif.read && (
                      <span className="w-2 h-2 rounded-full bg-[#C5A880]" />
                    )}
                  </div>
                  <p className="text-xs text-[#57534E] leading-relaxed font-light">
                    {notif.message}
                  </p>
                  <div className="text-[10px] text-[#A8A29E] pt-1">
                    {new Date(notif.created_at).toLocaleString()}
                  </div>
                </div>
              </div>

              {!notif.read && (
                <button
                  type="button"
                  onClick={() => handleMarkRead(notif.id)}
                  className="px-2.5 py-1 text-xs text-[#8C827A] hover:text-[#1C1917] hover:bg-[#FAF8F5] border border-[#E7E2DA] shrink-0 flex items-center gap-1 transition-colors"
                >
                  <Check className="w-3 h-3" />
                  <span>Mark Read</span>
                </button>
              )}
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="py-12 text-center text-sm text-[#8C827A] bg-white border border-[#E7E2DA]">
            No notifications to display.
          </div>
        )}
      </div>
    </div>
  );
}
