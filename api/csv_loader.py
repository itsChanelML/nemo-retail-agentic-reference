"""
ShopMind — CSV Product Loader
Loads products from data/products.csv and normalizes them
into ShopMind's RAG-ready schema.

In production this CSV would be replaced by a live inventory
feed from a retail partner's ERP or PIM system — same schema,
different data source.
"""

import os
import csv
from pathlib import Path

# Resolve path relative to this file so it works from any directory
DATA_DIR = Path(__file__).parent.parent / "data"
PRODUCTS_CSV = DATA_DIR / "products.csv"


def _parse_bool(val: str) -> bool:
    return str(val).strip().lower() in ("true", "1", "yes")


def _parse_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val.strip()) if val.strip() else default
    except (ValueError, AttributeError):
        return default


def _parse_int(val: str, default: int = 0) -> int:
    try:
        return int(val.strip()) if val.strip() else default
    except (ValueError, AttributeError):
        return default


def _build_description(row: dict) -> str:
    """
    Build a rich embedding-ready description from CSV fields.
    Combines the base description with key specs so the RAG
    retriever can match on spec-level queries like
    'laptop with 32GB RAM under $1500'.
    """
    parts = [row.get("description", "").strip()]

    specs = []
    if row.get("display_size"):
        specs.append(f"{row['display_size']}-inch display")
    if row.get("resolution"):
        specs.append(row["resolution"])
    if row.get("processor"):
        specs.append(row["processor"])
    if row.get("ram"):
        specs.append(f"{row['ram']} RAM")
    if row.get("storage"):
        specs.append(row["storage"])
    if row.get("battery_life"):
        specs.append(f"{row['battery_life']} battery")
    if row.get("weight"):
        specs.append(f"Weighs {row['weight']}")
    if row.get("color"):
        specs.append(f"Color: {row['color']}")

    if specs:
        parts.append("Specs: " + ". ".join(specs) + ".")

    stores = row.get("store_availability", "")
    if stores:
        parts.append(f"Available at: {stores.replace('|', ', ')}.")

    sale = row.get("sale_price", "").strip()
    price = row.get("price", "").strip()
    if sale and sale != price:
        parts.append(f"On sale: ${sale} (was ${price}).")

    return " ".join(filter(None, parts))


def load_csv_catalog(csv_path: Path = PRODUCTS_CSV) -> list[dict]:
    """
    Load and normalize all products from the CSV file.
    Returns a list of product dicts ready for FAISS ingestion.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Products CSV not found at {csv_path}. "
            "Make sure data/products.csv exists in the project root."
        )

    products = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                price = _parse_float(row.get("price", "0"))
                sale_price_raw = row.get("sale_price", "").strip()
                sale_price = _parse_float(sale_price_raw) if sale_price_raw else None

                product = {
                    "sku":              row.get("sku", "").strip(),
                    "name":             row.get("name", "").strip()[:100],
                    "brand":            row.get("brand", "").strip(),
                    "category":         row.get("category", "").strip().lower(),
                    "price":            price,
                    "sale_price":       sale_price,
                    "rating":           _parse_float(row.get("rating", "3.5"), 3.5),
                    "review_count":     _parse_int(row.get("review_count", "0")),
                    "in_stock":         _parse_bool(row.get("in_stock", "true")),
                    "stock_quantity":   _parse_int(row.get("stock_quantity", "0")),
                    "store_availability": [
                        s.strip()
                        for s in row.get("store_availability", "").split("|")
                        if s.strip()
                    ],
                    "color":            row.get("color", "").strip(),
                    "model_number":     row.get("model_number", "").strip(),
                    "warranty_years":   _parse_int(row.get("warranty_years", "1"), 1),
                    # Spec fields (empty string if not applicable)
                    "display_size":     row.get("display_size", "").strip(),
                    "resolution":       row.get("resolution", "").strip(),
                    "processor":        row.get("processor", "").strip(),
                    "ram":              row.get("ram", "").strip(),
                    "storage":          row.get("storage", "").strip(),
                    "battery_life":     row.get("battery_life", "").strip(),
                    "weight":           row.get("weight", "").strip(),
                    # Competitor pricing for price match tool
                    "competitor_prices": __import__("json").loads(
                        row.get("competitor_prices", "{}") or "{}"
                    ),
                    # Rich description built from all fields — used for embedding
                    "description":      _build_description(row),
                }
                products.append(product)
            except Exception as e:
                print(f"  Skipping row {row.get('sku', '?')}: {e}")

    print(f"CSV catalog loaded: {len(products)} products from {csv_path.name}")
    return products


async def load_bestbuy_catalog(
    categories: list = None,
    fallback_to_seed: bool = True,
) -> list[dict]:
    """
    Drop-in replacement for the old bestbuy_connector.load_bestbuy_catalog.
    Loads from CSV — no API calls, no rate limits, fully offline.

    In production: swap this implementation to call your retail partner's
    inventory API and return the same schema.
    """
    return load_csv_catalog()


if __name__ == "__main__":
    products = load_csv_catalog()
    print(f"\nSample product:")
    import json
    print(json.dumps(products[0], indent=2))
    print(f"\nCategories: {sorted(set(p['category'] for p in products))}")
    print(f"Brands: {sorted(set(p['brand'] for p in products))}")
    in_stock = sum(1 for p in products if p["in_stock"])
    print(f"In stock: {in_stock}/{len(products)}")
    on_sale = sum(1 for p in products if p["sale_price"])
    print(f"On sale: {on_sale}/{len(products)}")
