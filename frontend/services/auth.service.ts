import { api } from "@/lib/api-client";
import { AuthTokens, LoginRequest, RegisterRequest, User } from "@/types";

export const authService = {
  async login(data: LoginRequest): Promise<{ tokens: AuthTokens; user: User }> {
    try {
      const res = await api.post<{ access_token: string; refresh_token: string; token_type: string; user: User }>(
        "/auth/login",
        data
      );
      return {
        tokens: {
          access_token: res.access_token,
          refresh_token: res.refresh_token,
          token_type: res.token_type,
        },
        user: res.user,
      };
    } catch (e: any) {
      // Mock demo customer login fallback if backend user-service is starting up
      if (data.email === "customer@ibrat.com" && data.password === "Customer@12345") {
        const demoUser: User = {
          id: "u1000000-0000-0000-0000-000000000002",
          email: "customer@ibrat.com",
          full_name: "Elena Rostova",
          role: "CUSTOMER",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        return {
          tokens: {
            access_token: "mock-customer-access-token",
            refresh_token: "mock-customer-refresh-token",
            token_type: "Bearer",
          },
          user: demoUser,
        };
      }
      throw e;
    }
  },

  async register(data: RegisterRequest): Promise<{ tokens: AuthTokens; user: User }> {
    const res = await api.post<any>("/auth/register", data);
    return {
      tokens: {
        access_token: res.access_token,
        refresh_token: res.refresh_token,
        token_type: res.token_type,
      },
      user: res.user,
    };
  },

  async getProfile(): Promise<User | null> {
    try {
      return await api.get<User>("/users/me");
    } catch (e) {
      return null;
    }
  },

  async getPreferences(): Promise<any> {
    try {
      return await api.get<any>("/users/preferences");
    } catch (e) {
      return { preferred_heel_sizes: ["2 inch"], preferred_shoe_size: "38" };
    }
  },

  async updatePreferences(data: { preferred_heel_sizes?: string[]; preferred_shoe_size?: string }): Promise<any> {
    return await api.put("/users/preferences", data);
  },

  async getWishlist(): Promise<string[]> {
    try {
      const res = await api.get<any>("/users/wishlist");
      return (res.items || []).map((item: any) => item.product_id);
    } catch (e) {
      return [];
    }
  },

  async addToWishlist(productId: string): Promise<boolean> {
    try {
      await api.post(`/users/wishlist/${productId}`);
      return true;
    } catch (e) {
      return false;
    }
  },

  async removeFromWishlist(productId: string): Promise<boolean> {
    try {
      await api.delete(`/users/wishlist/${productId}`);
      return true;
    } catch (e) {
      return false;
    }
  },
};
