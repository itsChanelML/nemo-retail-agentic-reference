"""
ShopMind — Best Buy API Connector
Fetches live product data from Best Buy's public Products API v1
and normalizes it into ShopMind's RAG-ready product schema.

Auth: Simple API key in query string. Free. Instant approval.
Get your key at: https://developer.bestbuy.com

Rate limits: 5 req/sec, 50,000 req/day on free tier.

Best Buy Products API returns:
  - Real pricing (salePrice, regularPrice)
  - Real-time availability (inStoreAvailability, onlineAvailability)
  - Customer reviews (customerReviewAverage, customerReviewCount)
  - Full specs (shortDescription, longDescription)
  - Categories, brand, manufacturer, model number
  - Thumbnail images
"""

import os
import asyncio
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

BBY_BASE = "https://api.bestbuy.com/v1"
BBY_API_KEY = os.environ.get("BESTBUY_API_KEY", "")

# Best Buy category IDs — used to scope product searches
# Full taxonomy: https://developer.bestbuy.com/documentation/categories-api
BBY_CATEGORIES = {
    "headphones":       "cat02015",
    "laptops":          "abcat0502000",
    "monitors":         "abcat0515000",
    "tablets":          "pcmcat209400050001",
    "smartwatches":     "cat02047",
    "earbuds":          "cat02016",
    "speakers":         "abcat0204000",
    "keyboards":        "abcat0901001",
    "mice":             "abcat0901002",
    "cameras":          "abcat0400000",
    "phones":           "cat02076",
    "smart_home":       "pcmcat295700050011",
    "gaming":           "abcat0700000",
    "networking":       "abcat0503000",
}


def _bby_params(extra: dict = None) -> dict:
    """Base query params — API key + JSON format."""
    if not BBY_API_KEY:
        raise ValueError(
            "BESTBUY_API_KEY not set. "
            "Get a free key at https://developer.bestbuy.com"
        )
    params = {
        "apiKey": BBY_API_KEY,
        "format": "json",
        "show": (
            "sku,name,salePrice,regularPrice,customerReviewAverage,"
            "customerReviewCount,shortDescription,longDescription,"
            "manufacturer,modelNumber,categoryPath,thumbnailImage,"
            "inStoreAvailability,onlineAvailability,onlineAvailabilityText,"
            "color,weight,depth,height,width,features.feature"
        ),
    }
    if extra:
        params.update(extra)
    return params


def _normalize_product(p: dict) -> dict:
    """
    Map a raw Best Buy API product dict to ShopMind's product schema.
    Handles missing/null fields gracefully.
    """
    # Price: prefer salePrice, fall back to regularPrice
    price = p.get("salePrice") or p.get("regularPrice") or 0.0

    # Rating: Best Buy provides real customer review averages (0–5)
    rating = p.get("customerReviewAverage")
    if rating is None:
        rating = 3.5  # neutral default for unreviewed products
    else:
        try:
            rating = round(float(rating), 1)
        except (TypeError, ValueError):
            rating = 3.5

    # Category: use last item in categoryPath hierarchy
    cat_path = p.get("categoryPath", [])
    category = cat_path[-1].get("name", "Electronics") if cat_path else "Electronics"

    # Stock: Best Buy gives both online and in-store availability
    in_stock = bool(
        p.get("onlineAvailability") or p.get("inStoreAvailability")
    )

    # Brand
    brand = p.get("manufacturer") or "Best Buy"

    # Build rich description for embedding quality
    # Pull from multiple fields and feature bullets
    short = (p.get("shortDescription") or "").strip()
    long = (p.get("longDescription") or "").strip()[:300]
    features = p.get("features", []) or []
    feature_text = ". ".join(
        f.get("feature", "") for f in features[:5] if f.get("feature")
    )

    description = " ".join(filter(None, [
        p.get("name", ""),
        short,
        long,
        feature_text,
        f"Brand: {brand}.",
        f"Model: {p.get('modelNumber', '')}.",
        f"Category: {category}.",
    ])).strip()

    review_count = p.get("customerReviewCount", 0) or 0

    return {
        "sku":          f"BBY-{p.get('sku', 'UNKNOWN')}",
        "name":         (p.get("name") or "")[:100],
        "brand":        brand,
        "category":     category.lower(),
        "price":        round(float(price), 2),
        "rating":       rating,
        "in_stock":     in_stock,
        "description":  description[:800],  # cap for embedding quality
        # Best Buy extras — shown in UI, not used by RAG
        "image_url":    p.get("thumbnailImage", ""),
        "review_count": review_count,
        "model_number": p.get("modelNumber", ""),
        "bby_sku":      p.get("sku"),
        "availability_text": p.get("onlineAvailabilityText", ""),
        "regular_price": p.get("regularPrice"),
        "sale_price":   p.get("salePrice"),
    }


class BestBuyConnector:
    """
    Fetches and normalizes Best Buy product listings for ShopMind's RAG pipeline.

    Supports:
      - Keyword search across entire catalog
      - Category-scoped search
      - Multi-category catalog building
      - Price-range and availability filtering
    """

    def __init__(self, rate_limit: int = 5):
        self._sem = asyncio.Semaphore(rate_limit)

    async def _get(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        params: dict
    ) -> dict:
        async with self._sem:
            resp = await client.get(
                f"{BBY_BASE}/{endpoint}",
                params=params,
                timeout=15.0,
            )
            resp.raise_for_status()
            return resp.json()

    async def search_products(
        self,
        client: httpx.AsyncClient,
        query: str = "",
        category_id: Optional[str] = None,
        page_size: int = 10,
        page: int = 1,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: bool = True,
        sort: str = "customerReviewAverage.dsc",
    ) -> dict:
        """
        Search Best Buy products with optional filters.
        Returns raw API response dict with 'products' list and 'total'.

        Filter syntax: https://developer.bestbuy.com/documentation/products-api
        """
        # Build filter string
        filters = []

        if query:
            # Full-text search across name, description, features
            filters.append(f"(search={query})")

        if category_id:
            filters.append(f"(categoryPath.id={category_id})")

        if min_price is not None:
            filters.append(f"(salePrice>={min_price})")

        if max_price is not None:
            filters.append(f"(salePrice<={max_price})")

        if min_rating is not None:
            filters.append(f"(customerReviewAverage>={min_rating})")

        if in_stock_only:
            filters.append("(onlineAvailability=true)")

        # Best Buy filter syntax: all conditions joined with & INSIDE one parens block
        # Correct:   /products(categoryPath.id=cat02015&onlineAvailability=true)
        # Wrong:     /products(categoryPath.id=cat02015)&(onlineAvailability=true)
        if filters:
            # Strip outer parens from each filter, join with &, re-wrap in one parens
            inner = "&".join(f.strip("()") for f in filters)
            filter_str = f"({inner})"
        else:
            filter_str = "(onlineAvailability=true)"

        params = _bby_params({
            "pageSize": min(page_size, 100),
            "page": page,
            "sort": sort,
        })

        return await self._get(client, f"products{filter_str}", params)

    async def fetch_by_keyword(
        self,
        client: httpx.AsyncClient,
        keyword: str,
        limit: int = 20,
        **kwargs,
    ) -> list[dict]:
        """Fetch products matching a keyword, return normalized list."""
        raw = await self.search_products(
            client, query=keyword, page_size=limit, **kwargs
        )
        products = raw.get("products", [])
        return [_normalize_product(p) for p in products]

    async def fetch_by_category(
        self,
        client: httpx.AsyncClient,
        category_name: str,
        limit: int = 20,
        min_rating: float = 3.5,
    ) -> list[dict]:
        """Fetch top-rated products in a named Best Buy category."""
        cat_id = BBY_CATEGORIES.get(category_name)
        if not cat_id:
            print(f"  Unknown category '{category_name}' — skipping")
            return []

        raw = await self.search_products(
            client,
            category_id=cat_id,
            page_size=limit,
            min_rating=min_rating,
            sort="customerReviewAverage.dsc",
        )
        products = raw.get("products", [])
        return [_normalize_product(p) for p in products]

    async def fetch_catalog(
        self,
        keyword: str = "electronics",
        limit: int = 100,
    ) -> list[dict]:
        """
        Simple single-keyword catalog fetch.
        For richer catalogs use fetch_multi_category_catalog().
        """
        if not BBY_API_KEY:
            raise ValueError("BESTBUY_API_KEY not set.")

        all_products = []
        page = 1
        page_size = min(100, limit)

        async with httpx.AsyncClient() as client:
            while len(all_products) < limit:
                raw = await self.search_products(
                    client,
                    query=keyword,
                    page_size=page_size,
                    page=page,
                )
                batch = raw.get("products", [])
                if not batch:
                    break

                all_products.extend([_normalize_product(p) for p in batch])
                page += 1

                total = raw.get("total", 0)
                if len(all_products) >= total:
                    break

        return all_products[:limit]

    async def fetch_multi_category_catalog(
        self,
        categories: list[dict],
    ) -> list[dict]:
        """
        Fetch products across multiple categories/keywords for a diverse catalog.
        Deduplicates by BBY SKU.

        categories format:
            [
                {"type": "category", "name": "headphones", "limit": 20},
                {"type": "keyword", "query": "gaming mouse wireless", "limit": 15},
            ]
        """
        all_products = []
        seen_skus = set()

        async with httpx.AsyncClient() as client:
            for cat in categories:
                fetch_type = cat.get("type", "category")
                limit = cat.get("limit", 20)

                if fetch_type == "category":
                    name = cat.get("name", "")
                    print(f"  Fetching category: {name} (up to {limit})...")
                    batch = await self.fetch_by_category(
                        client, name, limit=limit,
                        min_rating=cat.get("min_rating", 3.5)
                    )
                else:
                    query = cat.get("query", "")
                    print(f"  Fetching keyword: '{query}' (up to {limit})...")
                    batch = await self.fetch_by_keyword(
                        client, query, limit=limit
                    )

                for p in batch:
                    if p["sku"] not in seen_skus:
                        seen_skus.add(p["sku"])
                        all_products.append(p)

                # Gentle rate-limiting between batches
                await asyncio.sleep(0.3)

        print(f"Best Buy catalog ready: {len(all_products)} unique products")
        return all_products


# ── Default catalog spec for ShopMind ───────────────────────────────────────
# Covers the same categories as the seed data but with live Best Buy prices,
# real customer ratings, and real-time stock status.

BBY_DEFAULT_CATALOG = [
    {"type": "category", "name": "headphones",   "limit": 20, "min_rating": 4.0},
    {"type": "category", "name": "earbuds",       "limit": 15, "min_rating": 4.0},
    {"type": "category", "name": "laptops",       "limit": 20, "min_rating": 4.0},
    {"type": "category", "name": "monitors",      "limit": 15, "min_rating": 4.0},
    {"type": "category", "name": "tablets",       "limit": 10, "min_rating": 4.0},
    {"type": "category", "name": "smartwatches",  "limit": 10, "min_rating": 4.0},
    {"type": "category", "name": "cameras",       "limit": 10, "min_rating": 4.0},
    {"type": "category", "name": "keyboards",     "limit": 10, "min_rating": 4.0},
    {"type": "category", "name": "mice",          "limit": 10, "min_rating": 4.0},
    {"type": "category", "name": "phones",        "limit": 15, "min_rating": 4.0},
    {"type": "category", "name": "smart_home",    "limit": 10, "min_rating": 4.0},
    {"type": "category", "name": "speakers",      "limit": 10, "min_rating": 4.0},
    # Keyword searches for specific high-value segments
    {"type": "keyword",  "query": "noise canceling headphones", "limit": 10},
    {"type": "keyword",  "query": "mechanical keyboard",        "limit": 8},
    {"type": "keyword",  "query": "4K gaming monitor",          "limit": 8},
]


async def load_bestbuy_catalog(
    categories: list[dict] = None,
    fallback_to_seed: bool = True,
) -> list[dict]:
    """
    Top-level loader called by agent.py at startup.
    Tries Best Buy API first; falls back to seed data if no key is set.

    Usage in agent.py:
        from bestbuy_connector import load_bestbuy_catalog
        catalog = await load_bestbuy_catalog()
    """
    if not BBY_API_KEY:
        if fallback_to_seed:
            print("No BESTBUY_API_KEY — falling back to seed product catalog.")
            from products import PRODUCT_CATALOG
            return PRODUCT_CATALOG
        raise ValueError("BESTBUY_API_KEY not set and fallback disabled.")

    connector = BestBuyConnector()
    cats = categories or BBY_DEFAULT_CATALOG
    return await connector.fetch_multi_category_catalog(cats)


if __name__ == "__main__":
    """Quick smoke test — run directly to verify your Best Buy key works."""
    async def test():
        print("Testing Best Buy API connection...")
        connector = BestBuyConnector()

        async with httpx.AsyncClient() as client:
            products = await connector.fetch_by_keyword(
                client,
                keyword="Sony noise canceling headphones",
                limit=3,
            )

        for p in products:
            print(
                f"  [{p['sku']}] {p['name'][:60]} "
                f"— ${p['price']} | "
                f"Rating: {p['rating']} | "
                f"In stock: {p['in_stock']}"
            )
        print(f"\nFetched {len(products)} products. API key is working.")

    asyncio.run(test())