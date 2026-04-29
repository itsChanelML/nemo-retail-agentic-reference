"""
ProductRetriever
Wraps EnsembleRetriever (FAISS dense + BM25 sparse) and provides:
  - semantic retrieve()
  - structured filter_products()
  - cross-score rerank()
"""

from typing import Any
from langchain.schema import Document
from sentence_transformers import CrossEncoder


class ProductRetriever:
    def __init__(self, hybrid_retriever, all_products: list[dict]):
        self.hybrid = hybrid_retriever
        self.catalog = all_products
        # Lightweight cross-encoder for re-ranking
        self._cross_encoder = None

    def _get_cross_encoder(self) -> CrossEncoder:
        if self._cross_encoder is None:
            self._cross_encoder = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2"
            )
        return self._cross_encoder

    def retrieve(self, query: str) -> list[Document]:
        """Hybrid dense+sparse retrieval."""
        return self.hybrid.invoke(query)

    def filter_products(self, filters: dict) -> list[dict]:
        """
        Attribute-based filter over product catalog.
        Supported filters: category, max_price, min_price, min_rating,
                           brand, in_stock, on_sale, store, keyword
        """
        results = self.catalog.copy()

        if cat := filters.get("category"):
            results = [p for p in results
                       if cat.lower() in p.get("category", "").lower()]

        if max_p := filters.get("max_price"):
            try:
                results = [p for p in results
                           if (p.get("sale_price") or p["price"]) <= float(max_p)]
            except ValueError:
                pass

        if min_p := filters.get("min_price"):
            try:
                results = [p for p in results if p["price"] >= float(min_p)]
            except ValueError:
                pass

        if min_r := filters.get("min_rating"):
            try:
                results = [p for p in results if p.get("rating", 0) >= float(min_r)]
            except ValueError:
                pass

        if brand := filters.get("brand"):
            results = [p for p in results
                       if brand.lower() in p.get("brand", "").lower()]

        if filters.get("in_stock") == "true":
            results = [p for p in results if p.get("in_stock", False)]

        if filters.get("on_sale") == "true":
            results = [p for p in results if p.get("sale_price")]

        if store := filters.get("store"):
            results = [p for p in results
                       if store.lower() in
                       " ".join(p.get("store_availability", [])).lower()]

        if kw := filters.get("keyword"):
            kw = kw.lower()
            results = [p for p in results
                       if kw in p.get("name", "").lower()
                       or kw in p.get("description", "").lower()]

        # Sort by rating desc
        return sorted(results, key=lambda x: x.get("rating", 0), reverse=True)

    def rerank(self, query: str, skus: list[str]) -> list[dict]:
        """
        Cross-encoder re-ranking: scores each (query, product_description) pair
        and returns sorted list with rank_score attached.
        """
        candidates = [p for p in self.catalog if p["sku"] in skus]
        if not candidates:
            return []

        model = self._get_cross_encoder()
        pairs = [(query, p["description"]) for p in candidates]
        scores = model.predict(pairs)

        for p, score in zip(candidates, scores):
            p["rank_score"] = round(float(score), 4)

        return sorted(candidates, key=lambda x: x["rank_score"], reverse=True)
