/**
 * Core type definitions for the Ibrat footwear platform.
 */

// ============================================================
// User Types
// ============================================================

export type UserRole = "CUSTOMER" | "ADMIN";

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

// ============================================================
// Product Types
// ============================================================

export interface Product {
  id: string;
  name: string;
  slug: string;
  description: string;
  base_price: number;
  category: Category;
  subcategory?: Category;
  collection?: Collection;
  material?: string;
  occasion?: string;
  style?: string;
  is_active: boolean;
  is_featured?: boolean;
  is_new_arrival?: boolean;
  images: ProductImage[];
  variants: ProductVariant[];
  customizations: CustomizationOption[];
  average_rating: number;
  review_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProductSummary {
  id: string;
  name: string;
  slug: string;
  base_price: number;
  primary_image_url?: string;
  category_name: string;
  average_rating: number;
  review_count: number;
  is_active: boolean;
}

export interface ProductImage {
  id: string;
  url: string;
  alt_text?: string;
  sort_order: number;
  is_primary: boolean;
  variant_id?: string;
}

export interface ProductVariant {
  id: string;
  sku: string;
  size: number;
  color: string;
  color_hex?: string;
  price: number;
  is_active: boolean;
}

export interface CustomizationOption {
  id: string;
  type: "HEEL_SIZE";
  value: string;
  display_name: string;
  additional_price: number;
  is_available: boolean;
}

// ============================================================
// Category & Collection Types
// ============================================================

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  image_url?: string;
  parent_id?: string;
  is_active: boolean;
  product_count?: number;
}

export interface Collection {
  id: string;
  name: string;
  slug: string;
  description?: string;
  image_url?: string;
  is_active: boolean;
  product_count?: number;
}

// ============================================================
// Review Types
// ============================================================

export interface Review {
  id: string;
  product_id: string;
  user_id: string;
  user_name: string;
  rating: number;
  title: string;
  comment: string;
  images: ReviewImage[];
  created_at: string;
  updated_at: string;
}

export interface ReviewImage {
  id: string;
  url: string;
}

export interface ReviewStats {
  average_rating: number;
  total_count: number;
  distribution: Record<number, number>; // { 1: count, 2: count, ... 5: count }
}

export interface CreateReviewRequest {
  rating: number;
  title: string;
  comment: string;
}

// ============================================================
// Cart Types
// ============================================================

export interface Cart {
  id: string;
  user_id: string;
  items: CartItem[];
  total_items: number;
  total_price: number;
  created_at: string;
  updated_at: string;
}

export interface CartItem {
  id: string;
  product_id: string;
  variant_id: string;
  quantity: number;
  selected_customization?: string;
  product_name: string;
  product_image?: string;
  variant_size: number;
  variant_color: string;
  unit_price: number;
  customization_price: number;
  total_price: number;
}

export interface AddToCartRequest {
  product_id: string;
  variant_id: string;
  quantity: number;
  customization_id?: string;
}

// ============================================================
// Inventory Types
// ============================================================

export interface InventoryStatus {
  variant_id: string;
  stock_quantity: number;
  available_quantity: number;
  reserved_quantity: number;
  is_in_stock: boolean;
  is_low_stock: boolean;
}

// ============================================================
// Search Types
// ============================================================

export interface SearchParams {
  q?: string;
  category?: string;
  collection?: string;
  min_price?: number;
  max_price?: number;
  colors?: string[];
  sizes?: number[];
  heel_sizes?: string[];
  min_rating?: number;
  sort_by?: "relevance" | "price_asc" | "price_desc" | "rating" | "newest";
  page?: number;
  page_size?: number;
}

export interface SearchResult {
  products: ProductSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  facets: SearchFacets;
}

export interface SearchFacets {
  categories: FacetBucket[];
  colors: FacetBucket[];
  sizes: FacetBucket[];
  heel_sizes: FacetBucket[];
  price_ranges: FacetBucket[];
  ratings: FacetBucket[];
}

export interface FacetBucket {
  key: string;
  count: number;
}

export interface AutocompleteResult {
  suggestions: string[];
  products: ProductSummary[];
}

// ============================================================
// Wishlist Types
// ============================================================

export interface WishlistItem {
  id: string;
  product_id: string;
  product: ProductSummary;
  added_at: string;
}

// ============================================================
// Notification Types
// ============================================================

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

// ============================================================
// Recommendation Types
// ============================================================

export interface RecommendationSection {
  title: string;
  type: "similar" | "personalized" | "popular" | "category";
  products: ProductSummary[];
}

// ============================================================
// Common Types
// ============================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
  };
}

export interface ApiSuccess<T> {
  success: true;
  data: T;
}

export type ApiResponse<T> = ApiSuccess<T> | ApiError;

// ============================================================
// Admin Types
// ============================================================

export interface DashboardStats {
  total_products: number;
  active_products: number;
  low_stock_products: number;
  total_users: number;
  total_reviews: number;
  average_rating: number;
  wishlist_count: number;
  active_carts: number;
}
