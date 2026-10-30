import { api } from "@/lib/api-client";
import { FALLBACK_PRODUCTS } from "./product.service";

export interface AutocompleteSuggestion {
  id: string;
  name: string;
  slug: string;
  category_name?: string;
  effective_price: number;
  primary_image_url?: string;
}

export interface SearchResponseDto {
  total: number;
  page: number;
  size: number;
  items: Array<{
    id: string;
    name: string;
    slug: string;
    description: string;
    category_name?: string;
    effective_price: number;
    base_price: number;
    heel_sizes: string[];
    sizes: string[];
    colors: string[];
    average_rating: number;
    review_count: number;
    primary_image_url?: string;
    is_in_stock: boolean;
  }>;
  facets: {
    categories: Array<{ key: string; count: number }>;
    heel_sizes: Array<{ key: string; count: number }>;
    colors: Array<{ key: string; count: number }>;
    sizes: Array<{ key: string; count: number }>;
    price_stats?: { min: number; max: number; avg: number };
  };
}

export const searchService = {
  async search(params: Record<string, any>): Promise<SearchResponseDto> {
    try {
      return await api.get<SearchResponseDto>("/search", params);
    } catch (e) {
      // Local fallback filter over mock catalog
      const q = (params.q || "").toLowerCase();
      const cat = params.category;
      const heel = params.heel_size;

      let filtered = FALLBACK_PRODUCTS.filter((p) => {
        if (q && !p.name.toLowerCase().includes(q) && !p.description.toLowerCase().includes(q)) {
          return false;
        }
        if (cat && p.category.name !== cat) return false;
        if (heel && !p.customizations.some((c) => c.value === heel)) return false;
        return true;
      });

      return {
        total: filtered.length,
        page: 1,
        size: 20,
        items: filtered.map((p) => ({
          id: p.id,
          name: p.name,
          slug: p.slug,
          description: p.description,
          category_name: p.category.name,
          effective_price: p.base_price,
          base_price: p.base_price,
          heel_sizes: p.customizations.map((c) => c.value),
          sizes: p.variants.map((v) => String(v.size)),
          colors: p.variants.map((v) => v.color),
          average_rating: p.average_rating,
          review_count: p.review_count,
          primary_image_url: p.images[0]?.url,
          is_in_stock: true,
        })),
        facets: {
          categories: [
            { key: "Bridal & Evening", count: 2 },
            { key: "Stilettos & High Heels", count: 1 },
            { key: "Mules & Slides", count: 1 },
            { key: "Luxury Flats & Loafers", count: 1 },
          ],
          heel_sizes: [
            { key: "1 inch", count: 4 },
            { key: "2 inch", count: 4 },
            { key: "3 inch", count: 4 },
          ],
          colors: [
            { key: "Champagne Gold", count: 2 },
            { key: "Midnight Black", count: 1 },
            { key: "Royal Navy", count: 1 },
            { key: "Ivory Pearl", count: 1 },
          ],
          sizes: [
            { key: "36", count: 4 },
            { key: "37", count: 5 },
            { key: "38", count: 5 },
            { key: "39", count: 5 },
            { key: "40", count: 2 },
          ],
          price_stats: { min: 260, max: 380, avg: 325 },
        },
      };
    }
  },

  async autocomplete(q: string): Promise<AutocompleteSuggestion[]> {
    if (!q || !q.trim()) return [];
    try {
      const res = await api.get<{ query: string; suggestions: AutocompleteSuggestion[] }>(
        "/search/autocomplete",
        { q, limit: 6 }
      );
      return res.suggestions || [];
    } catch (e) {
      const query = q.toLowerCase();
      return FALLBACK_PRODUCTS.filter((p) => p.name.toLowerCase().includes(query)).map((p) => ({
        id: p.id,
        name: p.name,
        slug: p.slug,
        category_name: p.category.name,
        effective_price: p.base_price,
        primary_image_url: p.images[0]?.url,
      }));
    }
  },
};
