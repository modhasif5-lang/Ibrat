import type { Metadata } from "next";
import { Playfair_Display, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { StoreProvider } from "@/context/StoreContext";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { CartDrawer } from "@/components/layout/CartDrawer";
import { SearchModal } from "@/components/layout/SearchModal";

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
  display: "swap",
});

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Ibrat | Italian Atelier Ladies Footwear & Bespoke Heeling",
  description:
    "Handcrafted in Florence. Discover luxury ladies footwear featuring bespoke 1-inch, 2-inch, and 3-inch heel customization and triple-density memory foam footbeds.",
  keywords: [
    "luxury footwear",
    "ladies shoes",
    "bridal heels",
    "custom heel heights",
    "Italian leather shoes",
    "comfortable stilettos",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${playfair.variable} ${plusJakarta.variable}`}>
      <body className="min-h-screen flex flex-col bg-[#FAF8F5] text-[#1C1917] antialiased selection:bg-[#C5A880] selection:text-white">
        <StoreProvider>
          <Navbar />
          <CartDrawer />
          <SearchModal />
          <main className="flex-1">{children}</main>
          <Footer />
        </StoreProvider>
      </body>
    </html>
  );
}
