import { api } from "@/lib/api-client";
import { Category, Collection, Product, User } from "@/types";
import {
  FALLBACK_CATEGORIES,
  FALLBACK_COLLECTIONS,
  getAllProducts,
  removeCustomProduct,
  saveCustomProduct,
} from "./product.service";

export interface AdminStats {
  totalProducts: number;
  totalVariants: number;
  totalCategories: number;
  totalCollections: number;
  totalUsers: number;
  totalStockUnits: number;
  lowStockItemsCount: number;
  pendingReviewsCount: number;
}

export interface InventoryItemDto {
  variant_id: string;
  product_id: string;
  product_name: string;
  sku: string;
  size: number;
  color: string;
  stock_quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  low_stock_threshold: number;
  is_low_stock: boolean;
  is_in_stock: boolean;
}

export interface AdminReviewDto {
  id: string;
  product_id: string;
  product_name: string;
  user_id: string;
  user_name: string;
  rating: number;
  title: string;
  comment: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  created_at: string;
}

export interface AdminNotificationDto {
  id: string;
  type: "LOW_STOCK" | "NEW_REVIEW" | "PRODUCT_CREATED" | "SYSTEM";
  title: string;
  message: string;
  created_at: string;
  read: boolean;
}

// In-memory mock data stores for admin modifications during local session
let mockProducts: Product[] = getAllProducts();
let mockCategories: Category[] = [...FALLBACK_CATEGORIES];
let mockCollections: Collection[] = [...FALLBACK_COLLECTIONS];

function buildInitialInventory(): InventoryItemDto[] {
  const items: InventoryItemDto[] = [];
  getAllProducts().forEach((product) => {
    (product.variants || []).forEach((variant, idx) => {
      // Realistic stocks with a few low stock variants for demo
      const isLow = idx === 3 && product.name.includes("Aurelia");
      const isOut = idx === 1 && product.name.includes("Celeste");
      const stock = isOut ? 0 : isLow ? 3 : 12 + ((idx * 5) % 15);
      const reserved = stock > 2 ? 1 : 0;
      const available = Math.max(0, stock - reserved);

      items.push({
        variant_id: variant.id,
        product_id: product.id,
        product_name: product.name,
        sku: variant.sku,
        size: variant.size,
        color: variant.color,
        stock_quantity: stock,
        reserved_quantity: reserved,
        available_quantity: available,
        low_stock_threshold: 5,
        is_low_stock: available <= 5 && available > 0,
        is_in_stock: available > 0,
      });
    });
  });
  return items;
}

let mockInventory: InventoryItemDto[] = buildInitialInventory();

let mockReviews: AdminReviewDto[] = [
  {
    id: "rev-mod-1",
    product_id: "a1000000-0000-0000-0000-000000000001",
    product_name: "Aurelia Crystal Satin Pump",
    user_id: "user-101",
    user_name: "Isabella Moretti",
    rating: 5,
    title: "Perfect wedding pair with 2 inch heel",
    comment: "The customized 2-inch heel provided the exact elevation I wanted without hurting during dinner.",
    status: "APPROVED",
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
  {
    id: "rev-mod-2",
    product_id: "a1000000-0000-0000-0000-000000000002",
    product_name: "Seraphina Nappa Ankle-Strap Heel",
    user_id: "user-102",
    user_name: "Claire Dupont",
    rating: 5,
    title: "Sublime leather and exquisite packaging",
    comment: "Arrived in Florence dust bags. The butter-soft nappa required zero break-in period.",
    status: "PENDING",
    created_at: new Date(Date.now() - 3600000 * 4).toISOString(),
  },
  {
    id: "rev-mod-3",
    product_id: "a1000000-0000-0000-0000-000000000003",
    product_name: "Gisèle Sculpted Satin Mule",
    user_id: "user-103",
    user_name: "Anonymous Client",
    rating: 2,
    title: "Incorrect shoe size delivered by local courier",
    comment: "Courier mixed up the package with neighbor.",
    status: "PENDING",
    created_at: new Date(Date.now() - 3600000 * 1).toISOString(),
  },
];

let mockUsers: Array<User & { preferred_heel?: string; shoe_size?: number }> = [
  {
    id: "usr-admin-01",
    email: "admin@ibrat.com",
    full_name: "Chiara Rossi (Director)",
    role: "ADMIN",
    preferred_heel: "2 inch",
    shoe_size: 38,
    created_at: "2026-01-15T10:00:00Z",
    updated_at: "2026-10-25T12:00:00Z",
  },
  {
    id: "usr-cust-01",
    email: "customer@ibrat.com",
    full_name: "Elena Valenti",
    role: "CUSTOMER",
    preferred_heel: "2 inch",
    shoe_size: 38,
    created_at: "2026-03-10T14:30:00Z",
    updated_at: "2026-10-27T08:15:00Z",
  },
  {
    id: "usr-cust-02",
    email: "sophia.luxe@fashion.com",
    full_name: "Sophia Laurent",
    role: "CUSTOMER",
    preferred_heel: "3 inch",
    shoe_size: 39,
    created_at: "2026-05-18T18:20:00Z",
    updated_at: "2026-10-20T16:45:00Z",
  },
  {
    id: "usr-cust-03",
    email: "camilla.bridal@events.it",
    full_name: "Camilla Bellini",
    role: "CUSTOMER",
    preferred_heel: "1 inch",
    shoe_size: 37,
    created_at: "2026-08-01T09:10:00Z",
    updated_at: "2026-10-15T11:00:00Z",
  },
];

let mockNotifications: AdminNotificationDto[] = [
  {
    id: "notif-1",
    type: "LOW_STOCK",
    title: "Low Stock Warning: GIS-MUL-ROU-38",
    message: "Gisèle Sculpted Satin Mule (EU 38, Venetian Rouge) has reached 0 units remaining.",
    created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    read: false,
  },
  {
    id: "notif-2",
    type: "NEW_REVIEW",
    title: "New Client Review Awaiting Moderation",
    message: "Claire Dupont submitted a 5-star review for Seraphina Nappa Ankle-Strap Heel.",
    created_at: new Date(Date.now() - 3600000 * 4).toISOString(),
    read: false,
  },
  {
    id: "notif-3",
    type: "PRODUCT_CREATED",
    title: "Catalog Event Synced via Kafka",
    message: "Product 'Camilla Bow D'Orsay Slingback' successfully indexed in Elasticsearch.",
    created_at: new Date(Date.now() - 86400000 * 1).toISOString(),
    read: true,
  },
];

export const adminService = {
  // Stats
  async getDashboardStats(): Promise<AdminStats> {
    const totalStock = mockInventory.reduce((acc, item) => acc + item.stock_quantity, 0);
    const lowStock = mockInventory.filter((item) => item.is_low_stock).length;
    const pendingReviews = mockReviews.filter((r) => r.status === "PENDING").length;

    return {
      totalProducts: mockProducts.length,
      totalVariants: mockInventory.length,
      totalCategories: mockCategories.length,
      totalCollections: mockCollections.length,
      totalUsers: mockUsers.length,
      totalStockUnits: totalStock,
      lowStockItemsCount: lowStock,
      pendingReviewsCount: pendingReviews,
    };
  },

  // Products
  async getProducts(): Promise<Product[]> {
    try {
      const res = await api.get<any>("/products");
      return res.items || res || getAllProducts();
    } catch (e) {
      return getAllProducts();
    }
  },

  async getProductById(id: string): Promise<Product | null> {
    const p = mockProducts.find((item) => item.id === id || item.slug === id);
    return p || null;
  },

  async createProduct(data: Partial<Product>): Promise<Product> {
    const skuPrefix = (data.name || "IBR").replace(/[^a-zA-Z]/g, "").substring(0, 3).toUpperCase();
    const defaultVariants = [
      { id: `v-${Date.now()}-36`, sku: `${skuPrefix}-ROY-36`, size: 36, color: "Royal Gold", color_hex: "#D4AF37", price: Number(data.base_price) || 295, is_active: true },
      { id: `v-${Date.now()}-37`, sku: `${skuPrefix}-ROY-37`, size: 37, color: "Royal Gold", color_hex: "#D4AF37", price: Number(data.base_price) || 295, is_active: true },
      { id: `v-${Date.now()}-38`, sku: `${skuPrefix}-ROY-38`, size: 38, color: "Royal Gold", color_hex: "#D4AF37", price: Number(data.base_price) || 295, is_active: true },
      { id: `v-${Date.now()}-39`, sku: `${skuPrefix}-ROY-39`, size: 39, color: "Royal Gold", color_hex: "#D4AF37", price: Number(data.base_price) || 295, is_active: true },
    ];

    const variants = data.variants && data.variants.length > 0 ? data.variants : defaultVariants;

    const newProduct: Product = {
      id: `prod-${Date.now()}`,
      name: data.name || "Untitled Silhouette",
      slug: (data.name || "untitled").toLowerCase().replace(/[^a-z0-9]+/g, "-"),
      description: data.description || "",
      base_price: Number(data.base_price) || 295,
      category: data.category || mockCategories[0],
      collection: data.collection,
      material: data.material || "Italian Nappa Leather",
      occasion: data.occasion || "Evening Cocktail",
      style: data.style || "Pump",
      is_active: true,
      images: data.images && data.images.length > 0 ? data.images : [
        {
          id: `img-${Date.now()}`,
          url: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=800&q=80",
          sort_order: 0,
          is_primary: true,
        },
      ],
      variants,
      customizations: data.customizations && data.customizations.length > 0 ? data.customizations : [
        { id: "c1", type: "HEEL_SIZE", value: "1 inch", display_name: "1 inch (Kitten Low)", additional_price: 0, is_available: true },
        { id: "c2", type: "HEEL_SIZE", value: "2 inch", display_name: "2 inch (Mid Block)", additional_price: 0, is_available: true },
        { id: "c3", type: "HEEL_SIZE", value: "3 inch", display_name: "3 inch (Classic Stiletto)", additional_price: 0, is_available: true },
      ],
      average_rating: 5.0,
      review_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    mockProducts = [newProduct, ...mockProducts];
    saveCustomProduct(newProduct);

    // Automatically register all variant inventory ledgers
    variants.forEach((v) => {
      const stock = 15;
      const reserved = 0;
      const available = stock - reserved;
      mockInventory.unshift({
        variant_id: v.id,
        product_id: newProduct.id,
        product_name: newProduct.name,
        sku: v.sku,
        size: v.size,
        color: v.color,
        stock_quantity: stock,
        reserved_quantity: reserved,
        available_quantity: available,
        low_stock_threshold: 5,
        is_low_stock: false,
        is_in_stock: true,
      });
    });

    return newProduct;
  },

  async updateProduct(id: string, data: Partial<Product>): Promise<Product | null> {
    const index = mockProducts.findIndex((p) => p.id === id);
    if (index === -1) return null;
    mockProducts[index] = { ...mockProducts[index], ...data, updated_at: new Date().toISOString() };
    return mockProducts[index];
  },

  async deleteProduct(id: string): Promise<boolean> {
    removeCustomProduct(id);
    mockProducts = mockProducts.filter((p) => p.id !== id);
    mockInventory = mockInventory.filter((item) => item.product_id !== id);
    return true;
  },

  // Categories & Collections
  async getCategories(): Promise<Category[]> {
    return mockCategories;
  },

  async createCategory(cat: { name: string; description?: string }): Promise<Category> {
    const newCat: Category = {
      id: `cat-${Date.now()}`,
      name: cat.name,
      slug: cat.name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
      description: cat.description,
      is_active: true,
      product_count: 0,
    };
    mockCategories.push(newCat);
    return newCat;
  },

  async getCollections(): Promise<Collection[]> {
    return mockCollections;
  },

  async createCollection(col: { name: string; description?: string }): Promise<Collection> {
    const newCol: Collection = {
      id: `col-${Date.now()}`,
      name: col.name,
      slug: col.name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
      description: col.description,
      is_active: true,
      product_count: 0,
    };
    mockCollections.push(newCol);
    return newCol;
  },

  // Inventory
  async getInventory(): Promise<InventoryItemDto[]> {
    return mockInventory;
  },

  async adjustStock(variant_id: string, newStock: number): Promise<InventoryItemDto | null> {
    const item = mockInventory.find((i) => i.variant_id === variant_id);
    if (!item) return null;
    item.stock_quantity = newStock;
    item.available_quantity = Math.max(0, newStock - item.reserved_quantity);
    item.is_in_stock = item.available_quantity > 0;
    item.is_low_stock = item.available_quantity <= item.low_stock_threshold;
    return item;
  },

  // Reviews Moderation
  async getReviews(): Promise<AdminReviewDto[]> {
    return mockReviews;
  },

  async updateReviewStatus(id: string, status: "APPROVED" | "REJECTED"): Promise<boolean> {
    const rev = mockReviews.find((r) => r.id === id);
    if (!rev) return false;
    rev.status = status;
    return true;
  },

  // Users
  async getUsers(): Promise<Array<User & { preferred_heel?: string; shoe_size?: number }>> {
    return mockUsers;
  },

  async toggleUserRole(id: string): Promise<User | null> {
    const u = mockUsers.find((user) => user.id === id);
    if (!u) return null;
    u.role = u.role === "ADMIN" ? "CUSTOMER" : "ADMIN";
    return u;
  },

  // Notifications
  async getNotifications(): Promise<AdminNotificationDto[]> {
    return mockNotifications;
  },

  async markNotificationRead(id: string): Promise<void> {
    const n = mockNotifications.find((notif) => notif.id === id);
    if (n) n.read = true;
  },
};
