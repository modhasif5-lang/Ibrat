import React from "react";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Check, Compass, Feather, HeartHandshake, ShieldCheck, Sparkles, Star } from "lucide-react";
import { FeaturedProductsSection } from "@/components/home/FeaturedProductsSection";
import { productService } from "@/services/product.service";

export default async function HomePage() {
  const { items: products } = await productService.getProducts({ page_size: 4 });
  const collections = await productService.getCollections();

  return (
    <div className="space-y-24 sm:space-y-32">
      {/* 1. Hero Section */}
      <section className="relative min-h-[85vh] flex items-center justify-center bg-[#1C1917] text-[#FAF8F5] overflow-hidden px-6 sm:px-12 py-20">
        {/* Background Editorial Ambiance */}
        <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-[#C5A880]/30 via-transparent to-black pointer-events-none" />

        <div className="relative max-w-4xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 border border-[#C5A880]/40 text-[#C5A880] text-xs uppercase tracking-[0.3em] font-light">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Florence Atelier • Bespoke Heights</span>
          </div>

          <h1 className="font-serif-luxury text-4xl sm:text-6xl md:text-7xl font-normal tracking-tight leading-[1.1] text-white">
            Sculptural Grace. <br />
            <span className="italic font-light text-[#E8DFD3]">
              Bespoke Elevation.
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-[#D6D0C7] font-light leading-relaxed">
            Every silhouette handcrafted by master cobblers in India. Personalized with your ideal choice.
          </p>


          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              href="/products"
              className="w-full sm:w-auto px-8 py-4 bg-[#C5A880] text-[#1C1917] hover:bg-white text-xs uppercase tracking-[0.2em] font-medium transition-all shadow-lg flex items-center justify-center gap-2"
            >
              <span>Explore The Collection</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/collections/bridal-couture-edit"
              className="w-full sm:w-auto px-8 py-4 border border-[#FAF8F5]/30 hover:border-white text-white text-xs uppercase tracking-[0.2em] font-medium transition-all flex items-center justify-center gap-2"
            >
              <span>Bridal Couture Edit</span>
            </Link>
          </div>

          {/* Value Badges */}
          <div className="pt-12 border-t border-white/10 grid grid-cols-2 md:grid-cols-4 gap-6 text-center text-xs tracking-wider uppercase text-[#A8A29E] font-light">
            <div>• Handcrafted in India</div>
            <div>• Customization available</div>
            <div>• Triple-Density Memory Insoles</div>
            <div>• Complimentary Global Courier</div>
          </div>
        </div>
      </section>

      {/* 3. Featured Atelier Footwear */}
      <section className="max-w-7xl mx-auto px-6 sm:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-12">
          <div>
            <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block mb-1">
              Curated Masterpieces
            </span>
            <h2 className="font-serif-luxury text-3xl sm:text-4xl text-[#1C1917]">
              The Current Edit
            </h2>
          </div>
          <Link
            href="/products"
            className="text-xs uppercase tracking-widest text-[#1C1917] hover:text-[#C5A880] font-semibold flex items-center gap-1.5 transition-colors group"
          >
            <span>View Full Catalog</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        <FeaturedProductsSection initialProducts={products} />
      </section>

      {/* 4. Curated Collections Visual Banner */}
      <section className="max-w-7xl mx-auto px-6 sm:px-8">
        <div className="text-center max-w-xl mx-auto space-y-3 mb-12">
          <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
            Curated Lines
          </span>
          <h2 className="font-serif-luxury text-3xl sm:text-4xl text-[#1C1917]">
            Distinct Footwear Collections
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {collections.map((col) => (
            <Link
              key={col.id}
              href={`/collections/${col.slug}`}
              className="group relative aspect-[4/5] overflow-hidden bg-[#1C1917] flex flex-col justify-end p-8 text-white border border-[#E7E2DA]"
            >
              {/* Background Tint / Gradient */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/30 to-black/10 group-hover:scale-105 transition-transform duration-700" />

              <div className="relative space-y-2">
                <span className="text-[10px] uppercase tracking-[0.25em] text-[#C5A880] font-medium block">
                  Atelier Collection
                </span>
                <h3 className="font-serif-luxury text-2xl text-white group-hover:text-[#C5A880] transition-colors">
                  {col.name}
                </h3>
                {col.description && (
                  <p className="text-xs text-[#D6D0C7] line-clamp-2 font-light">
                    {col.description}
                  </p>
                )}
                <div className="pt-2 text-xs uppercase tracking-widest text-[#FAF8F5] flex items-center gap-1.5 group-hover:gap-3 transition-all font-medium">
                  <span>Explore Edit</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 5. The Atelier Craftsmanship Manifesto */}
      <section className="bg-[#FAF8F5] border-y border-[#E7E2DA] py-20 px-6 sm:px-12">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <div className="space-y-6">
            <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
              The Florence Standard
            </span>
            <h2 className="font-serif-luxury text-3xl sm:text-5xl text-[#1C1917] leading-tight">
              Anatomically Engineered for Absolute Poise
            </h2>
            <p className="text-sm sm:text-base text-[#78716C] leading-relaxed font-light">
              High fashion should never require enduring discomfort. Each Ibrat pair
              is engineered around proprietary orthopedic geometry that distributes
              body weight uniformly across the heel, arch, and metatarsals.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-semibold text-[#1C1917]">
                  <Feather className="w-4 h-4 text-[#C5A880]" />
                  <span>Triple-Density Cushioning</span>
                </div>
                <p className="text-xs text-[#78716C] leading-relaxed">
                  Dual layers of aerospace memory foam bonded to breathable calfskin lining.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-semibold text-[#1C1917]">
                  <Compass className="w-4 h-4 text-[#C5A880]" />
                  <span>Tempered Spring Steel</span>
                </div>
                <p className="text-xs text-[#78716C] leading-relaxed">
                  High-tolerance internal shanks prevent heel wobble and preserve balance.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-semibold text-[#1C1917]">
                  <ShieldCheck className="w-4 h-4 text-[#C5A880]" />
                  <span>100% Certified Materials</span>
                </div>
                <p className="text-xs text-[#78716C] leading-relaxed">
                  Only LWG-certified Italian tanneries and Como heritage silks are utilized.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-semibold text-[#1C1917]">
                  <HeartHandshake className="w-4 h-4 text-[#C5A880]" />
                  <span>Complimentary Alterations</span>
                </div>
                <p className="text-xs text-[#78716C] leading-relaxed">
                  Enjoy seamless heel swaps or size adjustments within 30 days of delivery.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#1C1917] text-white p-8 sm:p-12 space-y-6 border border-[#E7E2DA]">
            <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
              Atelier Note
            </span>
            <blockquote className="font-serif-luxury text-xl sm:text-2xl leading-relaxed italic font-light text-[#FAF8F5]">
              "A woman is empowered when her footwear commands presence without
              demanding her endurance. That is the sole promise of Ibrat."
            </blockquote>
            <div className="pt-4 border-t border-white/10 flex items-center justify-between">
              <div>
                <div className="text-sm font-medium tracking-wide">
                  Chiara & Matteo Rossi
                </div>
                <div className="text-xs text-[#A8A29E] font-light">
                  Master Cobblers & Founders, Florence
                </div>
              </div>
              <span className="text-xs uppercase tracking-widest text-[#C5A880] font-serif">
                Est. 2024
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 6. VIP Atelier Invitation */}
      <section className="max-w-4xl mx-auto px-6 text-center space-y-6 pb-12">
        <span className="text-xs uppercase tracking-[0.25em] text-[#C5A880] font-semibold block">
          Private Access
        </span>
        <h2 className="font-serif-luxury text-3xl sm:text-4xl text-[#1C1917]">
          Join The Ibrat Atelier Circle
        </h2>
        <p className="text-sm text-[#78716C] max-w-xl mx-auto font-light">
          Receive priority invitations to made-to-order bespoke bridal runs,
          exclusive seasonal leathers, and private shoe consultations.
        </p>

        <form className="flex flex-col sm:flex-row items-center justify-center gap-3 max-w-md mx-auto pt-2">
          <input
            type="email"
            placeholder="Enter your email address"
            className="w-full sm:flex-1 px-4 py-3 bg-white border border-[#E7E2DA] text-xs text-[#1C1917] placeholder:text-[#8C827A] focus:outline-none focus:border-[#1C1917]"
          />
          <button
            type="button"
            className="w-full sm:w-auto px-6 py-3 bg-[#1C1917] text-white hover:bg-[#C5A880] text-xs uppercase tracking-widest font-medium transition-colors"
          >
            Request Access
          </button>
        </form>
      </section>
    </div>
  );
}
