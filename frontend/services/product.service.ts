import { api } from "@/lib/api-client";
import { Category, Collection, Product, ProductSummary } from "@/types";
import CATALOG_100 from "@/data/catalog_100_products.json";

// ============================================================
// Luxury Fallback Catalog matching Backend Seed Data & 100 Dataset Products
// ============================================================

export const CATALOG_PRODUCTS: Product[] = (CATALOG_100 as unknown) as Product[];

export const FALLBACK_PRODUCTS: Product[] = [
  {
    id: "a1000000-0000-0000-0000-000000000006",
    name: "Leela Royal Wedges",
    slug: "leela-royal-wedges",
    description:
      "The beauty of the peacock and the relationship of Krishna and Gopis embodied in one footwear.",
    base_price: 169,
    category: {
      id: "c1000000-0000-0000-0000-000000000005",
      name: "Mules & Slides",
      slug: "mules-and-slides",
      is_active: true,
    },
    collection: {
      id: "l1000000-0000-0000-0000-000000000002",
      name: "Riviera Summer Luxe",
      slug: "riviera-summer-luxe",
      is_active: true,
    },
    material: "Italian Specchio Calfskin & Sculpted Metallic Wedge",
    occasion: "Resort Gala & Sunset Soirée",
    style: "Architectural Wedge",
    is_active: true,
    average_rating: 5.0,
    review_count: 8,
    images: [
      {
        id: "img-leela-01",
        url: "/media/products/leela-royal-wedge/LeelaKeyHighlightCard.webp",
        alt_text: "Leela Royal Wedges Highlight Card",
        sort_order: 0,
        is_primary: true,
      },
      {
        id: "img-leela-02",
        url: "/media/products/leela-royal-wedge/LeelaRoyalWedges_1.webp",
        alt_text: "Leela Royal Wedges Angle 1",
        sort_order: 1,
        is_primary: false,
      },
      {
        id: "img-leela-03",
        url: "/media/products/leela-royal-wedge/LeelaRoyalWedges_2.webp",
        alt_text: "Leela Royal Wedges Angle 2",
        sort_order: 2,
        is_primary: false,
      },
    ],
    variants: [
      { id: "v-lee-36", sku: "LEE-ROY-GLD-36", size: 36, color: "Peacock Royal", color_hex: "#0E4D92", price: 169, is_active: true },
      { id: "v-lee-37", sku: "LEE-ROY-GLD-37", size: 37, color: "Peacock Royal", color_hex: "#0E4D92", price: 169, is_active: true },
      { id: "v-lee-38", sku: "LEE-ROY-GLD-38", size: 38, color: "Peacock Royal", color_hex: "#0E4D92", price: 169, is_active: true },
      { id: "v-lee-39", sku: "LEE-ROY-GLD-39", size: 39, color: "Peacock Royal", color_hex: "#0E4D92", price: 169, is_active: true },
      { id: "v-lee-40", sku: "LEE-ROY-GLD-40", size: 40, color: "Peacock Royal", color_hex: "#0E4D92", price: 169, is_active: true },
      { id: "v-lee-40", sku: "LEE-ROY-GLD-40", size: 40, color: "Peacock Royal", color_hex: "#0E4D92", price: 169, is_active: true }
    ],
    customizations: [
      { id: "c1", type: "HEEL_SIZE", value: "1 inch", display_name: "1 inch (Low Wedge Accent)", additional_price: 0, is_available: true },
      { id: "c2", type: "HEEL_SIZE", value: "2 inch", display_name: "2 inch (Mid Wedge)", additional_price: 0, is_available: true },
      { id: "c3", type: "HEEL_SIZE", value: "3 inch", display_name: "3 inch (Sculpted High Wedge)", additional_price: 0, is_available: true },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "a1000000-0000-0000-0000-000000000001",
    name: "Aurelia Crystal Satin Pump",
    slug: "aurelia-crystal-satin-pump",
    description:
      "Hand-constructed in Tuscany from lustrous Italian silk satin, the Aurelia pump features an ankle-framing crystal brooch and our signature shock-absorbing memory foam footbed. Perfectly balanced for all-day celebrations.",
    base_price: 380,
    category: {
      id: "c1000000-0000-0000-0000-000000000004",
      name: "Bridal & Evening",
      slug: "bridal-and-evening",
      is_active: true,
    },
    collection: {
      id: "l1000000-0000-0000-0000-000000000001",
      name: "Bridal Couture Edit",
      slug: "bridal-couture-edit",
      is_active: true,
    },
    material: "Italian Silk Satin & Austrian Crystal Brooch",
    occasion: "Bridal & Gala",
    style: "Pointed Toe Stiletto",
    is_active: true,
    average_rating: 5.0,
    review_count: 14,
    images: [
      {
        id: "img-01",
        url: "/media/products/aurelia-champagne-main.webp",
        alt_text: "Aurelia Crystal Satin Pump in Champagne Gold",
        sort_order: 0,
        is_primary: true,
      },
      {
        id: "img-02",
        url: "/media/products/aurelia-champagne-side.webp",
        alt_text: "Aurelia Satin Pump Side Profile",
        sort_order: 1,
        is_primary: false,
      },
    ],
    variants: [
      { id: "v1", sku: "AUR-SAT-GLD-36", size: 36, color: "Champagne Gold", color_hex: "#F7E7CE", price: 380, is_active: true },
      { id: "v2", sku: "AUR-SAT-GLD-37", size: 37, color: "Champagne Gold", color_hex: "#F7E7CE", price: 380, is_active: true },
      { id: "v3", sku: "AUR-SAT-GLD-38", size: 38, color: "Champagne Gold", color_hex: "#F7E7CE", price: 380, is_active: true },
      { id: "v4", sku: "AUR-SAT-GLD-39", size: 39, color: "Champagne Gold", color_hex: "#F7E7CE", price: 380, is_active: true },
      { id: "v5", sku: "AUR-SAT-GLD-40", size: 40, color: "Champagne Gold", color_hex: "#F7E7CE", price: 380, is_active: true },
      { id: "v6", sku: "AUR-SAT-EMR-38", size: 38, color: "Emerald Velvet", color_hex: "#046307", price: 380, is_active: true },
    ],
    customizations: [
      { id: "c1", type: "HEEL_SIZE", value: "1 inch", display_name: "1 inch (Kitten Low)", additional_price: 0, is_available: true },
      { id: "c2", type: "HEEL_SIZE", value: "2 inch", display_name: "2 inch (Mid Block)", additional_price: 0, is_available: true },
      { id: "c3", type: "HEEL_SIZE", value: "3 inch", display_name: "3 inch (Classic Stiletto)", additional_price: 0, is_available: true },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "a1000000-0000-0000-0000-000000000002",
    name: "Seraphina Nappa Ankle-Strap Heel",
    slug: "seraphina-nappa-ankle-strap-heel",
    description:
      "A study in sculptural minimalism. Handcrafted from butter-soft Italian nappa leather with a delicate buckled ankle strap that elongates the leg without friction.",
    base_price: 340,
    category: {
      id: "c1000000-0000-0000-0000-000000000001",
      name: "Stilettos & High Heels",
      slug: "stilettos-and-high-heels",
      is_active: true,
    },
    collection: {
      id: "l1000000-0000-0000-0000-000000000003",
      name: "Midnight Atelier",
      slug: "midnight-atelier",
      is_active: true,
    },
    material: "100% Full-Grain Italian Nappa Leather",
    occasion: "Evening Cocktail",
    style: "Ankle-Strap Sandal",
    is_active: true,
    average_rating: 4.9,
    review_count: 9,
    images: [
      {
        id: "img-03",
        url: "/media/products/seraphina-black-main.webp",
        alt_text: "Seraphina Nappa Ankle-Strap in Midnight Black",
        sort_order: 0,
        is_primary: true,
      },
    ],
    variants: [
      { id: "v7", sku: "SER-NAP-BLK-36", size: 36, color: "Midnight Black", color_hex: "#111111", price: 340, is_active: true },
      { id: "v8", sku: "SER-NAP-BLK-37", size: 37, color: "Midnight Black", color_hex: "#111111", price: 340, is_active: true },
      { id: "v9", sku: "SER-NAP-BLK-38", size: 38, color: "Midnight Black", color_hex: "#111111", price: 340, is_active: true },
      { id: "v10", sku: "SER-NAP-BLK-39", size: 39, color: "Midnight Black", color_hex: "#111111", price: 340, is_active: true },
    ],
    customizations: [
      { id: "c4", type: "HEEL_SIZE", value: "1 inch", display_name: "1 inch (Kitten Low)", additional_price: 0, is_available: true },
      { id: "c5", type: "HEEL_SIZE", value: "2 inch", display_name: "2 inch (Mid Block)", additional_price: 0, is_available: true },
      { id: "c6", type: "HEEL_SIZE", value: "3 inch", display_name: "3 inch (Classic Stiletto)", additional_price: 0, is_available: true },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "a1000000-0000-0000-0000-000000000003",
    name: "Valentina Embellished Velvet Mule",
    slug: "valentina-embellished-velvet-mule",
    description:
      "Royal evening mules in jewel-toned silk velvet, decorated with intricate tonal micro-beading and a sculpted flared kitten heel.",
    base_price: 295,
    category: {
      id: "c1000000-0000-0000-0000-000000000005",
      name: "Mules & Slides",
      slug: "mules-and-slides",
      is_active: true,
    },
    collection: {
      id: "l1000000-0000-0000-0000-000000000003",
      name: "Midnight Atelier",
      slug: "midnight-atelier",
      is_active: true,
    },
    material: "Silk Velvet with Hand-applied Glass Beads",
    occasion: "Black Tie Dinner",
    style: "Pointed Mule",
    is_active: true,
    average_rating: 4.8,
    review_count: 6,
    images: [
      {
        id: "img-04",
        url: "/media/products/valentina-navy-main.webp",
        alt_text: "Valentina Velvet Mule in Royal Navy",
        sort_order: 0,
        is_primary: true,
      },
    ],
    variants: [
      { id: "v11", sku: "VAL-VEL-NAV-37", size: 37, color: "Royal Navy", color_hex: "#001F3F", price: 295, is_active: true },
      { id: "v12", sku: "VAL-VEL-NAV-38", size: 38, color: "Royal Navy", color_hex: "#001F3F", price: 295, is_active: true },
      { id: "v13", sku: "VAL-VEL-NAV-39", size: 39, color: "Royal Navy", color_hex: "#001F3F", price: 295, is_active: true },
    ],
    customizations: [
      { id: "c7", type: "HEEL_SIZE", value: "1 inch", display_name: "1 inch (Kitten Low)", additional_price: 0, is_available: true },
      { id: "c8", type: "HEEL_SIZE", value: "2 inch", display_name: "2 inch (Mid Block)", additional_price: 0, is_available: true },
      { id: "c9", type: "HEEL_SIZE", value: "3 inch", display_name: "3 inch (Classic Stiletto)", additional_price: 0, is_available: true },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "a1000000-0000-0000-0000-000000000004",
    name: "Celeste Pointed Toe Flat",
    slug: "celeste-pointed-toe-flat",
    description:
      "Refined everyday luxury. Crafted with an elongated almond-pointed toe, hidden arch pillow, and a whisper of polished gold along the low stacked heel.",
    base_price: 260,
    category: {
      id: "c1000000-0000-0000-0000-000000000003",
      name: "Luxury Flats & Loafers",
      slug: "luxury-flats-and-loafers",
      is_active: true,
    },
    collection: {
      id: "l1000000-0000-0000-0000-000000000002",
      name: "Riviera Summer Luxe",
      slug: "riviera-summer-luxe",
      is_active: true,
    },
    material: "Glove Calf Leather & 14k Gold-dipped Heel Accent",
    occasion: "Day-to-Evening",
    style: "Pointed Flat",
    is_active: true,
    average_rating: 5.0,
    review_count: 11,
    images: [
      {
        id: "img-05",
        url: "/media/products/celeste-ivory-main.webp",
        alt_text: "Celeste Pointed Flat in Ivory Pearl",
        sort_order: 0,
        is_primary: true,
      },
    ],
    variants: [
      { id: "v14", sku: "CEL-FLT-IVO-36", size: 36, color: "Ivory Pearl", color_hex: "#FFFFF0", price: 260, is_active: true },
      { id: "v15", sku: "CEL-FLT-IVO-37", size: 37, color: "Ivory Pearl", color_hex: "#FFFFF0", price: 260, is_active: true },
      { id: "v16", sku: "CEL-FLT-IVO-38", size: 38, color: "Ivory Pearl", color_hex: "#FFFFF0", price: 260, is_active: true },
      { id: "v17", sku: "CEL-FLT-IVO-39", size: 39, color: "Ivory Pearl", color_hex: "#FFFFF0", price: 260, is_active: true },
    ],
    customizations: [
      { id: "c10", type: "HEEL_SIZE", value: "1 inch", display_name: "1 inch (Flat Accent)", additional_price: 0, is_available: true },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "a1000000-0000-0000-0000-000000000005",
    name: "Camilla Pearl Slingback",
    slug: "camilla-pearl-slingback",
    description:
      "Ethereal French moire silk pump with an elasticated slingback strap and graduated natural freshwater pearls encircling the vamp.",
    base_price: 350,
    category: {
      id: "c1000000-0000-0000-0000-000000000004",
      name: "Bridal & Evening",
      slug: "bridal-and-evening",
      is_active: true,
    },
    collection: {
      id: "l1000000-0000-0000-0000-000000000001",
      name: "Bridal Couture Edit",
      slug: "bridal-couture-edit",
      is_active: true,
    },
    material: "French Moire Silk with Cultured Freshwater Pearls",
    occasion: "Bridal & Ceremony",
    style: "Pointed Slingback",
    is_active: true,
    average_rating: 4.9,
    review_count: 15,
    images: [
      {
        id: "img-06",
        url: "/media/products/camilla-white-main.webp",
        alt_text: "Camilla Pearl Slingback in Bridal White",
        sort_order: 0,
        is_primary: true,
      },
    ],
    variants: [
      { id: "v18", sku: "CAM-SLG-WHT-36", size: 36, color: "Bridal White", color_hex: "#FFFFFF", price: 350, is_active: true },
      { id: "v19", sku: "CAM-SLG-WHT-37", size: 37, color: "Bridal White", color_hex: "#FFFFFF", price: 350, is_active: true },
      { id: "v20", sku: "CAM-SLG-WHT-38", size: 38, color: "Bridal White", color_hex: "#FFFFFF", price: 350, is_active: true },
      { id: "v21", sku: "CAM-SLG-WHT-39", size: 39, color: "Bridal White", color_hex: "#FFFFFF", price: 350, is_active: true },
    ],
    customizations: [
      { id: "c11", type: "HEEL_SIZE", value: "1 inch", display_name: "1 inch (Kitten Low)", additional_price: 0, is_available: true },
      { id: "c12", type: "HEEL_SIZE", value: "2 inch", display_name: "2 inch (Mid Block)", additional_price: 0, is_available: true },
      { id: "c13", type: "HEEL_SIZE", value: "3 inch", display_name: "3 inch (Classic Stiletto)", additional_price: 0, is_available: true },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

export const FALLBACK_CATEGORIES: Category[] = [
  { id: "c1000000-0000-0000-0000-000000000004", name: "Bridal & Evening", slug: "bridal-and-evening", is_active: true, product_count: 2 },
  { id: "c1000000-0000-0000-0000-000000000001", name: "Stilettos & High Heels", slug: "stilettos-and-high-heels", is_active: true, product_count: 1 },
  { id: "c1000000-0000-0000-0000-000000000005", name: "Mules & Slides", slug: "mules-and-slides", is_active: true, product_count: 1 },
  { id: "c1000000-0000-0000-0000-000000000003", name: "Luxury Flats & Loafers", slug: "luxury-flats-and-loafers", is_active: true, product_count: 1 },
];

export const FALLBACK_COLLECTIONS: Collection[] = [
  { id: "l1000000-0000-0000-0000-000000000001", name: "Bridal Couture Edit", slug: "bridal-couture-edit", is_active: true, product_count: 2 },
  { id: "l1000000-0000-0000-0000-000000000003", name: "Midnight Atelier", slug: "midnight-atelier", is_active: true, product_count: 2 },
  { id: "l1000000-0000-0000-0000-000000000002", name: "Riviera Summer Luxe", slug: "riviera-summer-luxe", is_active: true, product_count: 1 },
];

const STORAGE_KEY = "ibrat_custom_products";

export function getCustomProducts(): Product[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveCustomProduct(product: Product) {
  if (typeof window === "undefined") return;
  try {
    const existing = getCustomProducts().filter((p) => p.id !== product.id && p.slug !== product.slug);
    localStorage.setItem(STORAGE_KEY, JSON.stringify([product, ...existing]));
  } catch (e) {
    console.error("Failed to save product to localStorage:", e);
  }
}

export function removeCustomProduct(id: string) {
  if (typeof window === "undefined") return;
  try {
    const remaining = getCustomProducts().filter((p) => p.id !== id && p.slug !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(remaining));
  } catch (e) {
    console.error("Failed to remove product from localStorage:", e);
  }
}

export function getAllProducts(): Product[] {
  const custom = getCustomProducts();
  return [...custom, ...CATALOG_PRODUCTS, ...FALLBACK_PRODUCTS];
}

// ============================================================
// Product API Service
// ============================================================

export const productService = {
  async getProducts(params?: Record<string, any>): Promise<{ items: ProductSummary[]; total: number }> {
    try {
      const data = await api.get<any>("/products", params);
      return {
        items: data.items || data,
        total: data.total || (data.items ? data.items.length : data.length),
      };
    } catch (e) {
      // Graceful fallback including any custom products created by user
      const all = getAllProducts();
      return {
        items: all.map((p) => ({
          id: p.id,
          name: p.name,
          slug: p.slug,
          base_price: p.base_price,
          category_name: p.category?.name || "Bespoke Footwear",
          average_rating: p.average_rating || 5.0,
          review_count: p.review_count || 0,
          primary_image_url: p.images?.[0]?.url || "/media/products/leela-royal-wedge/LeelaKeyHighlightCard.webp",
          is_active: p.is_active ?? true,
        })),
        total: all.length,
      };
    }
  },

  async getProductBySlug(slug: string): Promise<Product | null> {
    try {
      const data = await api.get<Product>(`/products/${slug}`);
      return data;
    } catch (e) {
      const all = getAllProducts();
      const found = all.find((p) => p.slug === slug || p.id === slug);
      return found || null;
    }
  },

  async getCategories(): Promise<Category[]> {
    try {
      const data = await api.get<Category[]>("/categories");
      return data;
    } catch (e) {
      return FALLBACK_CATEGORIES;
    }
  },

  async getCollections(): Promise<Collection[]> {
    try {
      const data = await api.get<Collection[]>("/collections");
      return data;
    } catch (e) {
      return FALLBACK_COLLECTIONS;
    }
  },
};
