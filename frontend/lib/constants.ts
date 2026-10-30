/**
 * Application-wide constants.
 */

export const SITE_NAME = process.env.NEXT_PUBLIC_SITE_NAME || "Ibrat";
export const SITE_DESCRIPTION = "Premium ladies footwear — curated with care, crafted for comfort.";
export const CURRENCY = "₹";

// Sizes available for footwear
export const AVAILABLE_SIZES = [35, 36, 37, 38, 39, 40, 41];

// Heel size options
export const HEEL_SIZES = [
  { value: "1_INCH", label: "1 inch", display: "1\"" },
  { value: "2_INCH", label: "2 inch", display: "2\"" },
  { value: "3_INCH", label: "3 inch", display: "3\"" },
] as const;

// Sort options
export const SORT_OPTIONS = [
  { value: "relevance", label: "Relevance" },
  { value: "price_asc", label: "Price: Low to High" },
  { value: "price_desc", label: "Price: High to Low" },
  { value: "rating", label: "Highest Rated" },
  { value: "newest", label: "Newest First" },
] as const;

// Product categories
export const PRODUCT_CATEGORIES = [
  "Sandals",
  "Heels",
  "Flats",
  "Slippers",
  "Mojaris",
  "Juttis",
  "Loafers",
  "Wedges",
  "Casual",
  "Party Wear",
] as const;

// Pagination
export const DEFAULT_PAGE_SIZE = 12;
export const ADMIN_PAGE_SIZE = 20;

// Image constraints
export const MAX_IMAGE_SIZE_MB = 5;
export const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

// Rating
export const MIN_RATING = 1;
export const MAX_RATING = 5;
