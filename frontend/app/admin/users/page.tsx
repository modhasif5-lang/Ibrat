"use client";

import React, { useEffect, useState } from "react";
import { RefreshCw, Shield, ShieldCheck, Sparkles, UserCheck, Users } from "lucide-react";
import { adminService } from "@/services/admin.service";
import { User } from "@/types";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<Array<User & { preferred_heel?: string; shoe_size?: number }>>([]);
  const [loading, setLoading] = useState(true);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await adminService.getUsers();
      setUsers([...data]);
    } catch (e) {
      console.error("Failed to load users:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleToggleRole = async (id: string) => {
    await adminService.toggleUserRole(id);
    loadUsers();
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E7E2DA] pb-6">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block mb-1">
            Accounts & Access
          </span>
          <h1 className="font-serif-luxury text-2xl sm:text-3xl text-[#1C1917]">
            Client & Director Accounts
          </h1>
        </div>

        <button
          type="button"
          onClick={loadUsers}
          className="p-2 border border-[#E7E2DA] bg-white hover:bg-[#FAF8F5] text-[#1C1917] self-start sm:self-auto"
          title="Refresh Users"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Users Table */}
      <div className="bg-white border border-[#E7E2DA] overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-[#E7E2DA] bg-[#FAF8F5] text-[#8C827A] uppercase tracking-wider text-[11px]">
              <th className="py-3 px-4">Client Name</th>
              <th className="py-3 px-4">Email Address</th>
              <th className="py-3 px-4">System Role</th>
              <th className="py-3 px-4">Preferred Heel Elevation</th>
              <th className="py-3 px-4">Shoe Size</th>
              <th className="py-3 px-4">Enrolled Since</th>
              <th className="py-3 px-4 text-right">Access Control</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F0EDE8]">
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-[#FAF8F5] transition-colors">
                <td className="py-3.5 px-4 font-semibold text-sm text-[#1C1917]">
                  {u.full_name}
                </td>
                <td className="py-3.5 px-4 text-[#57534E] font-mono">
                  {u.email}
                </td>
                <td className="py-3.5 px-4">
                  <span
                    className={`px-2 py-0.5 text-[10px] uppercase tracking-wider font-semibold ${
                      u.role === "ADMIN"
                        ? "bg-[#1C1917] text-[#C5A880]"
                        : "bg-[#FAF8F5] text-[#57534E] border border-[#E7E2DA]"
                    }`}
                  >
                    {u.role === "ADMIN" ? "Atelier Director" : "VIP Client"}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-[#57534E]">
                  <span className="font-medium text-[#1C1917]">
                    {u.preferred_heel || '2"'}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-[#57534E]">
                  EU {u.shoe_size || 38}
                </td>
                <td className="py-3.5 px-4 text-[#8C827A]">
                  {new Date(u.created_at).toLocaleDateString()}
                </td>
                <td className="py-3.5 px-4 text-right">
                  <button
                    type="button"
                    onClick={() => handleToggleRole(u.id)}
                    className="px-2.5 py-1 border border-[#E7E2DA] hover:bg-[#FAF8F5] text-[#1C1917] text-[10px] uppercase tracking-wider font-medium transition-colors"
                  >
                    Switch to {u.role === "ADMIN" ? "Customer" : "Admin"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
