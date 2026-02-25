"""Export contact info for ticket buyers of a Stripe product (show).

Usage:
    uv run python scripts/export_stripe_customers.py <STRIPE_PRODUCT_ID>

Reads STRIPE_API_KEY from .env.
Outputs to data/customers_<PRODUCT_ID>_<YYYY-MM-DD>.csv.
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import stripe
from dotenv import load_dotenv

load_dotenv()


def export_customers(product_id: str) -> None:
    # email (lowercase) -> {"name": str|None, "phone": str|None, "tickets": int}
    customers: dict[str, dict] = defaultdict(lambda: {"name": None, "phone": None, "tickets": 0})

    product = stripe.Product.retrieve(product_id)
    show_name = product.name

    print(f"Fetching completed checkout sessions for product {product_id}...")

    sessions = stripe.checkout.Session.list(
        status="complete",
        limit=100,
        expand=["data.line_items", "data.line_items.data.price"],
    )

    session_count = 0
    for session in sessions.auto_paging_iter():
        session_count += 1

        line_items = session.get("line_items")
        if not line_items:
            continue

        matching_quantity = 0
        for item in line_items.get("data", []):
            price = item.get("price") or {}
            # price.product is a string ID when not expanded further
            product = price.get("product") or {}
            product_obj_id = product.get("id") if isinstance(product, dict) else product
            if product_obj_id == product_id:
                matching_quantity += item.get("quantity") or 0

        if matching_quantity == 0:
            continue

        details = session.get("customer_details") or {}
        email = (details.get("email") or "").strip().lower()
        if not email:
            continue

        name = (details.get("name") or "").strip() or None
        phone = (details.get("phone") or "").strip() or None

        customers[email]["tickets"] += matching_quantity
        if name:
            customers[email]["name"] = name
        if phone:
            customers[email]["phone"] = phone

    print(f"Scanned {session_count} completed sessions. Found {len(customers)} unique customer(s).")

    Path("data").mkdir(exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    output_path = Path(f"data/customers_{product_id}_{today}.csv")

    rows = sorted(
        [
            {
                "name": info["name"] or "",
                "email": email,
                "phone": info["phone"] or "",
                "tickets": info["tickets"],
                "show": show_name,
            }
            for email, info in customers.items()
        ],
        key=lambda r: r["name"].lower(),
    )

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "phone", "tickets", "show"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} customer(s) to {output_path}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/export_stripe_customers.py <STRIPE_PRODUCT_ID>")
        sys.exit(1)

    product_id = sys.argv[1]

    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        print("Error: STRIPE_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    stripe.api_key = api_key
    export_customers(product_id)


if __name__ == "__main__":
    main()
