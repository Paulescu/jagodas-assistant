"""List all active Stripe products with their first active price.

Usage:
    uv run python scripts/list_stripe_products.py

Reads STRIPE_API_KEY from .env.
Outputs a JSON array to stdout, one object per product.
"""

import json
import os
import sys

import stripe
from dotenv import load_dotenv

load_dotenv()


def list_products() -> list[dict]:
    products = []
    for product in stripe.Product.list(active=True).auto_paging_iter():
        prices = stripe.Price.list(product=product.id, active=True, limit=1)
        price_data = prices.data[0] if prices.data else None

        entry = {
            "id": product.id,
            "name": product.name,
            "description": product.description or "",
            "images": list(product.images or []),
            "metadata": dict(product.metadata or {}),
            "price_amount": price_data.unit_amount if price_data else None,
            "price_currency": price_data.currency if price_data else None,
        }
        products.append(entry)

    return products


def main() -> None:
    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        print("Error: STRIPE_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    stripe.api_key = api_key

    products = list_products()

    if not products:
        print("No active products found.")
        sys.exit(1)

    print(json.dumps(products, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
