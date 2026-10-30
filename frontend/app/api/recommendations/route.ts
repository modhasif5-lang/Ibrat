import { NextRequest, NextResponse } from "next/server";
import path from "path";
import fs from "fs";

// Cache in memory across requests
let embeddingsCache: Record<string, number[]> | null = null;
let normalizedCache: { key: string; vector: number[] }[] | null = null;

function loadEmbeddings() {
  if (normalizedCache) return normalizedCache;

  try {
    const filePath = path.join(process.cwd(), "data", "product_embeddings.json");
    if (!fs.existsSync(filePath)) {
      return null;
    }

    const raw = fs.readFileSync(filePath, "utf-8");
    embeddingsCache = JSON.parse(raw);

    normalizedCache = Object.entries(embeddingsCache!).map(([key, vector]) => {
      // Compute L2 norm
      let sumSq = 0;
      for (let i = 0; i < vector.length; i++) {
        sumSq += vector[i] * vector[i];
      }
      const norm = Math.sqrt(sumSq) || 1;
      const normalizedVec = vector.map((v) => v / norm);

      return {
        key,
        vector: normalizedVec,
      };
    });

    return normalizedCache;
  } catch (err) {
    console.error("Failed to load embeddings:", err);
    return null;
  }
}

function cosineSimilarity(vecA: number[], vecB: number[]): number {
  let dotProduct = 0;
  const len = vecA.length;
  for (let i = 0; i < len; i++) {
    dotProduct += vecA[i] * vecB[i];
  }
  return dotProduct;
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const productId = searchParams.get("productId") || "";
  const name = searchParams.get("name") || "";
  const slug = searchParams.get("slug") || "";
  const limit = parseInt(searchParams.get("limit") || "4", 10);

  const dataset = loadEmbeddings();
  if (!dataset || dataset.length === 0) {
    return NextResponse.json({ success: false, items: [] });
  }

  // Find the matching embedding key for this product
  const queryTerms = [
    productId.toLowerCase().trim(),
    slug.toLowerCase().trim().replace(/-/g, " "),
    name.toLowerCase().trim(),
  ].filter(Boolean);

  let targetIndex = -1;

  // 1. First exact match or prefix match on numeric ID (e.g. "391" -> "391_Leela Wedges")
  for (let i = 0; i < dataset.length; i++) {
    const keyLower = dataset[i].key.toLowerCase();
    const idPrefix = keyLower.split("_")[0];

    for (const term of queryTerms) {
      if (idPrefix === term || keyLower === term) {
        targetIndex = i;
        break;
      }
    }
    if (targetIndex !== -1) break;
  }

  // 2. Keyword/substring match (e.g. "leela" in "391_Leela Wedges  Royal Wedding Heels")
  if (targetIndex === -1) {
    for (const term of queryTerms) {
      const words = term.split(" ").filter((w) => w.length > 3);
      for (const word of words) {
        const found = dataset.findIndex((d) => d.key.toLowerCase().includes(word));
        if (found !== -1) {
          targetIndex = found;
          break;
        }
      }
      if (targetIndex !== -1) break;
    }
  }

  // If still not found, fallback to the first item or popular reference item
  const targetItem = targetIndex !== -1 ? dataset[targetIndex] : dataset[0];
  const queryVector = targetItem.vector;

  // Compute similarities against all products in catalog
  const scored = dataset
    .filter((_, idx) => idx !== targetIndex)
    .map((item) => ({
      key: item.key,
      score: cosineSimilarity(queryVector, item.vector),
    }));

  // Sort descending by similarity
  scored.sort((a, b) => b.score - a.score);

  const topMatches = scored.slice(0, limit);

  return NextResponse.json({
    success: true,
    targetKey: targetItem.key,
    recommendations: topMatches.map((m) => {
      // Parse clean title from folder name: "391_Leela Wedges  Royal Wedding Heels"
      const parts = m.key.split("_");
      const id = parts[0];
      const remainder = parts.slice(1).join("_").trim();
      const nameParts = remainder.split(/\s{2,}/);
      const cleanName = nameParts[0] || remainder;
      const subtitle = nameParts[1] || "Bespoke Footwear";

      return {
        id,
        folderName: m.key,
        name: cleanName,
        subtitle,
        similarityScore: parseFloat(m.score.toFixed(4)),
      };
    }),
  });
}
