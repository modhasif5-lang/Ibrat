"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User } from "@/types";

export interface CartItemState {
  id: string;
  productId: string;
  variantId: string;
  name: string;
  slug: string;
  price: number;
  quantity: number;
  heelSize?: string;
  size?: string;
  color?: string;
  imageUrl?: string;
}

interface StoreContextType {
  // User Authentication
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  // Cart
  cart: CartItemState[];
  cartCount: number;
  cartTotal: number;
  isCartOpen: boolean;
  openCart: () => void;
  closeCart: () => void;
  addToCart: (item: CartItemState) => void;
  updateQuantity: (id: string, quantity: number) => void;
  removeFromCart: (id: string) => void;
  clearCart: () => void;
  // Wishlist
  wishlist: string[]; // Product IDs
  toggleWishlist: (productId: string) => void;
  isInWishlist: (productId: string) => boolean;
  // Search Modal
  isSearchOpen: boolean;
  openSearch: () => void;
  closeSearch: () => void;
  // Session
  sessionId: string;
}

const StoreContext = createContext<StoreContextType | undefined>(undefined);

export function StoreProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [cart, setCart] = useState<CartItemState[]>([]);
  const [wishlist, setWishlist] = useState<string[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");

  // Initialize from LocalStorage
  useEffect(() => {
    // Session ID
    let sess = localStorage.getItem("ibrat_session_id");
    if (!sess) {
      sess = "sess_" + Math.random().toString(36).substring(2, 12);
      localStorage.setItem("ibrat_session_id", sess);
    }
    setSessionId(sess);

    // Auth
    const savedToken = localStorage.getItem("access_token");
    const savedUser = localStorage.getItem("ibrat_user");
    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch (e) {
        console.error("Failed to parse stored user", e);
      }
    }

    // Cart
    const savedCart = localStorage.getItem("ibrat_cart");
    if (savedCart) {
      try {
        setCart(JSON.parse(savedCart));
      } catch (e) {
        console.error("Failed to parse cart", e);
      }
    } else {
      // Default sample item for initial luxury preview
      const initialSample: CartItemState[] = [
        {
          id: "cart-item-demo-1",
          productId: "a1000000-0000-0000-0000-000000000001",
          variantId: "v1000000-0000-0000-0000-000000000003",
          name: "Aurelia Crystal Satin Pump",
          slug: "aurelia-crystal-satin-pump",
          price: 380,
          quantity: 1,
          heelSize: "2 inch",
          size: "38",
          color: "Champagne Gold",
          imageUrl: "/media/products/aurelia-champagne-main.webp",
        },
      ];
      setCart(initialSample);
      localStorage.setItem("ibrat_cart", JSON.stringify(initialSample));
    }

    // Wishlist
    const savedWishlist = localStorage.getItem("ibrat_wishlist");
    if (savedWishlist) {
      try {
        setWishlist(JSON.parse(savedWishlist));
      } catch (e) {
        console.error("Failed to parse wishlist", e);
      }
    }
  }, []);

  // Save Cart to LocalStorage
  useEffect(() => {
    if (cart.length > 0 || localStorage.getItem("ibrat_cart")) {
      localStorage.setItem("ibrat_cart", JSON.stringify(cart));
    }
  }, [cart]);

  // Save Wishlist to LocalStorage
  useEffect(() => {
    localStorage.setItem("ibrat_wishlist", JSON.stringify(wishlist));
  }, [wishlist]);

  // User Actions
  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem("access_token", newToken);
    localStorage.setItem("ibrat_user", JSON.stringify(newUser));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("ibrat_user");
  };

  // Cart Actions
  const addToCart = (newItem: CartItemState) => {
    setCart((prev) => {
      const existingIdx = prev.findIndex(
        (i) => i.productId === newItem.productId && i.heelSize === newItem.heelSize && i.size === newItem.size
      );
      if (existingIdx > -1) {
        const updated = [...prev];
        updated[existingIdx].quantity = Math.min(updated[existingIdx].quantity + newItem.quantity, 10);
        return updated;
      }
      return [...prev, newItem];
    });
    setIsCartOpen(true);
  };

  const updateQuantity = (id: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(id);
      return;
    }
    setCart((prev) =>
      prev.map((item) => (item.id === id ? { ...item, quantity: Math.min(quantity, 10) } : item))
    );
  };

  const removeFromCart = (id: string) => {
    setCart((prev) => prev.filter((item) => item.id !== id));
  };

  const clearCart = () => {
    setCart([]);
    localStorage.removeItem("ibrat_cart");
  };

  // Wishlist Actions
  const toggleWishlist = (productId: string) => {
    setWishlist((prev) =>
      prev.includes(productId) ? prev.filter((id) => id !== productId) : [...prev, productId]
    );
  };

  const isInWishlist = (productId: string) => wishlist.includes(productId);

  const cartCount = cart.reduce((acc, item) => acc + item.quantity, 0);
  const cartTotal = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);

  return (
    <StoreContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        cart,
        cartCount,
        cartTotal,
        isCartOpen,
        openCart: () => setIsCartOpen(true),
        closeCart: () => setIsCartOpen(false),
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        wishlist,
        toggleWishlist,
        isInWishlist,
        isSearchOpen,
        openSearch: () => setIsSearchOpen(true),
        closeSearch: () => setIsSearchOpen(false),
        sessionId,
      }}
    >
      {children}
    </StoreContext.Provider>
  );
}

export function useStore() {
  const context = useContext(StoreContext);
  if (!context) {
    throw new Error("useStore must be used within a StoreProvider");
  }
  return context;
}
