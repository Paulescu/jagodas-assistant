"""Export ticket buyers using a natural language show description.

Usage:
    uv run python scripts/export_customers_natural.py "show tomorrow in Belgrad"

Reads STRIPE_API_KEY and ANTHROPIC_API_KEY from .env.
Outputs to data/customers_<PRODUCT_ID>_<YYYY-MM-DD>.csv.
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

import anthropic
import stripe
from dotenv import load_dotenv

# Import export logic from sibling script
sys.path.insert(0, str(Path(__file__).parent))
from export_stripe_customers import export_customers

load_dotenv()


def list_active_products() -> list[dict]:
    products = []
    for product in stripe.Product.list(active=True, limit=100).auto_paging_iter():
        products.append({"id": product.id, "name": product.name})
    return products


def identify_product(query: str, products: list[dict], today: str) -> str | None:
    """Ask Claude to match the query to a product. Returns product_id or None."""
    client = anthropic.Anthropic()

    products_json = json.dumps(products, ensure_ascii=False, indent=2)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Today is {today}.\n\n"
                    f"Available Stripe products (shows):\n{products_json}\n\n"
                    f"The user wants to export customers for: \"{query}\"\n\n"
                    "If exactly one product clearly matches, reply with only its product id (e.g. prod_abc123).\n"
                    "If multiple products could match, reply with UNCLEAR and list the matching product ids and names.\n"
                    "If nothing matches, reply with NOMATCH."
                ),
            }
        ],
    )

    return message.content[0].text.strip()


def main() -> None:
    if len(sys.argv) != 2:
        print('Usage: uv run python scripts/export_customers_natural.py "show description"')
        sys.exit(1)

    query = sys.argv[1]

    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        print("Error: STRIPE_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("Error: ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    stripe.api_key = api_key

    print("Fetching your shows from Stripe...")
    products = list_active_products()

    if not products:
        print("No active products found in Stripe.")
        sys.exit(1)

    today = date.today().isoformat()
    print(f'Finding the right show for: "{query}"...')
    result = identify_product(query, products, today)

    if result.startswith("prod_"):
        product_id = result
        matched = next((p for p in products if p["id"] == product_id), None)
        print(f'Matched show: {matched["name"] if matched else product_id}')
        export_customers(product_id)
    elif result.startswith("UNCLEAR"):
        print("Multiple shows could match your description:")
        print(result.replace("UNCLEAR", "").strip())
        print("\nPlease re-run with a more specific description.")
        sys.exit(1)
    else:
        print(f'No show found matching: "{query}"')
        print("Available shows:")
        for p in products:
            print(f"  - {p['name']} ({p['id']})")
        sys.exit(1)


if __name__ == "__main__":
    main()
