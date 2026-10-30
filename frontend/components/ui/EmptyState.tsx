import React from "react";
import Link from "next/link";
import { LucideIcon, Sparkles } from "lucide-react";

interface EmptyStateProps {
  icon?: LucideIcon;
  eyebrow?: string;
  title: string;
  description: string;
  actionText?: string;
  actionHref?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon: Icon = Sparkles,
  eyebrow = "Atelier Collection",
  title,
  description,
  actionText,
  actionHref,
  onAction,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`p-8 sm:p-12 bg-white border border-[#E7E2DA] text-center max-w-xl mx-auto space-y-4 shadow-xs ${className}`}
    >
      <div className="w-14 h-14 mx-auto rounded-full bg-[#FAF8F5] border border-[#E7E2DA] flex items-center justify-center text-[#8C827A]">
        <Icon className="w-6 h-6 stroke-1 text-[#C5A880]" />
      </div>

      <div className="space-y-1">
        <span className="text-[10px] uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
          {eyebrow}
        </span>
        <h3 className="font-serif-luxury text-2xl text-[#1C1917]">
          {title}
        </h3>
      </div>

      <p className="text-xs text-[#78716C] leading-relaxed font-light max-w-md mx-auto">
        {description}
      </p>

      {(actionText && (actionHref || onAction)) && (
        <div className="pt-2">
          {actionHref ? (
            <Link
              href={actionHref}
              className="inline-flex items-center justify-center px-6 py-2.5 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors"
            >
              {actionText}
            </Link>
          ) : (
            <button
              type="button"
              onClick={onAction}
              className="inline-flex items-center justify-center px-6 py-2.5 bg-[#1C1917] hover:bg-[#C5A880] text-white text-xs uppercase tracking-widest font-medium transition-colors"
            >
              {actionText}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
