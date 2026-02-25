"""Create a Stripe product and linked price for a show.

Usage:
    uv run python scripts/create_stripe_show.py \\
        --name "Kidaš Irena - 2026-03-15 u 20:00 - Novi Sad" \\
        --price 1500 \\
        --currency rsd \\
        [--description "..."] \\
        [--images "https://..." "https://..."] \\
        [--metadata '{"key": "value"}']

Reads STRIPE_API_KEY from .env.
Price is given in whole units (e.g. 1500 for 1500 RSD); the script converts to
the smallest currency unit by multiplying by 100.
"""

import argparse
import json
import os
import sys

import stripe
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Stripe product and price for a show.")
    parser.add_argument("--name", required=True, help="Product name")
    parser.add_argument("--price", required=True, type=float, help="Price in whole units (e.g. 1500 for 1500 RSD)")
    parser.add_argument("--currency", required=True, help="Lowercase ISO 4217 currency code (e.g. rsd, eur)")
    parser.add_argument("--description", default="", help="Product description (optional)")
    parser.add_argument("--images", nargs="*", default=[], help="Space-separated image URLs (optional)")
    parser.add_argument("--metadata", default="", help="JSON string of metadata key-value pairs (optional)")
    args = parser.parse_args()

    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        print("Error: STRIPE_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    stripe.api_key = api_key

    # Parse optional metadata
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for --metadata: {e}")
            sys.exit(1)

    # Build product kwargs (only include optional fields when non-empty)
    product_kwargs: dict = {"name": args.name}
    if args.description:
        product_kwargs["description"] = args.description
    if args.images:
        product_kwargs["images"] = args.images
    if metadata:
        product_kwargs["metadata"] = metadata

    try:
        product = stripe.Product.create(**product_kwargs)
    except stripe.StripeError as e:
        print(f"Error: Stripe API error: {e.user_message}")
        sys.exit(1)

    # Convert to smallest currency unit (paras for RSD, cents for EUR, etc.)
    unit_amount = round(args.price * 100)

    try:
        stripe.Price.create(
            product=product.id,
            unit_amount=unit_amount,
            currency=args.currency.lower(),
        )
    except stripe.StripeError as e:
        print(f"Error: Stripe API error: {e.user_message}")
        sys.exit(1)

    print(f"Product created: {product.id}")
    print(f"Dashboard: https://dashboard.stripe.com/products/{product.id}")


if __name__ == "__main__":
    main()
