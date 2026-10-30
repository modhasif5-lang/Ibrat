import { api } from "@/lib/api-client";

export interface CartResponseDto {
  id: string;
  user_id?: string;
  session_id?: string;
  items: Array<{
    id: string;
    product_id: string;
    variant_id: string;
    quantity: number;
    selected_customization?: string;
    unit_price: number;
    subtotal: number;
  }>;
  total_items: number;
  total_price: number;
}

export const cartService = {
  async getCart(sessionId?: string): Promise<CartResponseDto | null> {
    try {
      const headers = sessionId ? { "X-Session-ID": sessionId } : undefined;
      return await api.get<CartResponseDto>("/cart", undefined);
    } catch (e) {
      return null;
    }
  },

  async addItem(
    sessionId: string,
    payload: {
      product_id: string;
      variant_id: string;
      quantity: number;
      selected_customization?: string;
      unit_price: number;
    }
  ): Promise<CartResponseDto | null> {
    try {
      return await api.post<CartResponseDto>("/cart/items", payload);
    } catch (e) {
      console.warn("Cart API add item fallback", e);
      return null;
    }
  },

  async updateQuantity(
    sessionId: string,
    itemId: string,
    quantity: number
  ): Promise<CartResponseDto | null> {
    try {
      return await api.patch<CartResponseDto>(`/cart/items/${itemId}`, { quantity });
    } catch (e) {
      return null;
    }
  },

  async removeItem(sessionId: string, itemId: string): Promise<CartResponseDto | null> {
    try {
      return await api.delete<CartResponseDto>(`/cart/items/${itemId}`);
    } catch (e) {
      return null;
    }
  },

  async clearCart(sessionId: string): Promise<boolean> {
    try {
      await api.delete("/cart/clear");
      return true;
    } catch (e) {
      return false;
    }
  },

  async validateCart(): Promise<{ is_valid: boolean; issues: any[] }> {
    try {
      return await api.post<any>("/cart/validate");
    } catch (e) {
      return { is_valid: true, issues: [] };
    }
  },
};
