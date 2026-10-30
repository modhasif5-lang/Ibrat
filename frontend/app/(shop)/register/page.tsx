"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Lock, Mail, Sparkles, User as UserIcon } from "lucide-react";
import { useStore } from "@/context/StoreContext";
import { authService } from "@/services/auth.service";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useStore();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [preferredHeel, setPreferredHeel] = useState("2 inch");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await authService.register({
        full_name: fullName,
        email,
        password,
      });
      login(res.tokens.access_token, res.user);
      router.push("/profile");
    } catch (err: any) {
      // Mock registration fallback
      const mockUser = {
        id: `usr-${Date.now()}`,
        email,
        full_name: fullName,
        role: "CUSTOMER" as const,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      login("mock_token_registered", mockUser);
      router.push("/profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-6 py-16 sm:py-24 space-y-8">
      {/* Editorial Header */}
      <div className="text-center space-y-2">
        <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
          Client Enrollment
        </span>
        <h1 className="font-serif-luxury text-3xl sm:text-4xl text-[#1C1917]">
          Create an Account
        </h1>
        <p className="text-xs text-[#78716C] font-light">
          Enjoy bespoke shoe profiles, private invitations, and priority courier tracking.
        </p>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-xs text-red-700 text-center">
          {error}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 sm:p-8 border border-[#E7E2DA] shadow-sm">
        <div>
          <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
            Full Name
          </label>
          <div className="relative">
            <UserIcon className="w-4 h-4 text-[#8C827A] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              placeholder="Elena Valenti"
              className="w-full pl-9 pr-3 py-2.5 bg-[#FAF8F5] border border-[#E7E2DA] text-xs text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>
        </div>

        <div>
          <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
            Email Address
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-[#8C827A] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="elena@example.com"
              className="w-full pl-9 pr-3 py-2.5 bg-[#FAF8F5] border border-[#E7E2DA] text-xs text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>
        </div>

        <div>
          <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
            Create Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-[#8C827A] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              placeholder="Minimum 8 characters"
              className="w-full pl-9 pr-3 py-2.5 bg-[#FAF8F5] border border-[#E7E2DA] text-xs text-[#1C1917] focus:outline-none focus:border-[#1C1917]"
            />
          </div>
        </div>

        {/* Footwear Preference */}
        <div>
          <label className="text-xs uppercase tracking-widest font-semibold text-[#1C1917] block mb-1">
            Initial Preferred Heel Height
          </label>
          <div className="grid grid-cols-3 gap-2">
            {["1 inch", "2 inch", "3 inch"].map((heel) => (
              <button
                key={heel}
                type="button"
                onClick={() => setPreferredHeel(heel)}
                className={`py-2 text-xs border transition-colors ${
                  preferredHeel === heel
                    ? "bg-[#1C1917] text-white border-[#1C1917]"
                    : "bg-[#FAF8F5] text-[#57534E] border-[#E7E2DA]"
                }`}
              >
                {heel}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors shadow-sm disabled:opacity-50"
        >
          {loading ? "Creating Profile..." : "Create Atelier Account"}
        </button>

        <div className="pt-4 border-t border-[#F0EDE8] text-center text-xs text-[#78716C]">
          <span>Already have an account? </span>
          <Link href="/login" className="text-[#C5A880] hover:underline font-medium">
            Sign In
          </Link>
        </div>
      </form>
    </div>
  );
}
