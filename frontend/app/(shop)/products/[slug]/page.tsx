import React from "react";
import { productService } from "@/services/product.service";
import { ProductDetailClient } from "./ProductDetailClient";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function ProductDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const initialProduct = await productService.getProductBySlug(slug);

  return <ProductDetailClient slug={slug} initialProduct={initialProduct} />;
}

