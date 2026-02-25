"""Print a revenue summary for a date range from Stripe completed checkout sessions.

Usage:
    uv run python scripts/get_revenue.py --from YYYY-MM-DD --to YYYY-MM-DD

Reads STRIPE_API_KEY from .env.
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from urllib.request import urlopen

import stripe
from dotenv import load_dotenv

load_dotenv()

CURRENCY_SYMBOLS = {
    "eur": "€",
    "usd": "$",
    "gbp": "£",
    "rsd": "RSD ",
    "huf": "HUF ",
    "czk": "CZK ",
    "pln": "zł",
    "chf": "CHF ",
    "sek": "kr",
    "nok": "kr",
    "dkk": "kr",
}


def format_amount(amount_cents: int, currency: str) -> str:
    symbol = CURRENCY_SYMBOLS.get(currency.lower(), currency.upper() + " ")
    return f"{symbol}{amount_cents / 100:,.2f}"


def fetch_eur_rates() -> dict[str, float]:
    """Return exchange rates relative to EUR (e.g. {"RSD": 117.2, "USD": 1.08, ...})."""
    with urlopen("https://open.er-api.com/v6/latest/EUR", timeout=10) as resp:
        data = json.loads(resp.read())
    if data.get("result") != "success":
        raise RuntimeError(f"Exchange rate API error: {data}")
    return {k.lower(): v for k, v in data["rates"].items()}


def to_eur_cents(amount_cents: int, currency: str, rates: dict[str, float]) -> int:
    """Convert an amount (in smallest currency unit) to EUR cents."""
    cur = currency.lower()
    if cur == "eur":
        return amount_cents
    rate = rates.get(cur)
    if rate is None:
        raise RuntimeError(f"No exchange rate found for {currency.upper()}")
    return round(amount_cents / rate)


def get_revenue(from_date: str, to_date: str) -> None:
    start_ts = int(datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    # end of to_date: 23:59:59 UTC
    end_ts = int(datetime.strptime(to_date, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59, tzinfo=timezone.utc
    ).timestamp())

    eur_rates = fetch_eur_rates()

    # Stripe limits expand depth to 4 levels, so we cannot expand price.product inline.
    # Instead we fetch products on demand and cache them.
    product_cache: dict[str, str] = {}

    def get_product_name(product_id: str) -> str:
        if product_id not in product_cache:
            try:
                product = stripe.Product.retrieve(product_id)
                product_cache[product_id] = product.get("name") or product_id
            except stripe.error.StripeError:
                product_cache[product_id] = product_id
        return product_cache[product_id]

    sessions = stripe.checkout.Session.list(
        status="complete",
        created={"gte": start_ts, "lte": end_ts},
        expand=[
            "data.line_items",
            "data.line_items.data.price",
        ],
        limit=100,
    )

    # product_id -> {"name": str, "revenue_eur": int, "tickets": int}
    by_show: dict[str, dict] = defaultdict(lambda: {"name": "", "revenue_eur": 0, "tickets": 0})
    grand_total_eur = 0
    session_count = 0

    for session in sessions.auto_paging_iter():
        session_count += 1
        session_currency = (session.get("currency") or "").lower()

        amount_total = session.get("amount_total") or 0
        grand_total_eur += to_eur_cents(amount_total, session_currency, eur_rates)

        line_items = session.get("line_items")
        if not line_items:
            continue

        for item in line_items.get("data", []):
            price = item.get("price") or {}
            raw_product = price.get("product")
            if not raw_product:
                continue
            product_id = raw_product if isinstance(raw_product, str) else raw_product.get("id", "")
            if not product_id:
                continue
            product_name = get_product_name(product_id)
            quantity = item.get("quantity") or 0
            unit_amount = price.get("unit_amount") or 0
            item_revenue_eur = to_eur_cents(quantity * unit_amount, session_currency, eur_rates)

            show = by_show[product_id]
            show["name"] = product_name
            show["revenue_eur"] += item_revenue_eur
            show["tickets"] += quantity

    if session_count == 0:
        print("No completed sales found for this period.")
        sys.exit(0)

    print(f"Period: {from_date} to {to_date}")
    print(f"Gross revenue: {format_amount(grand_total_eur, 'eur')}")
    print(f"Transactions: {session_count}")

    if by_show:
        print()
        print("By show:")
        name_width = max(len(s["name"]) for s in by_show.values())
        for show in sorted(by_show.values(), key=lambda s: -s["revenue_eur"]):
            label = show["name"].ljust(name_width)
            amount = format_amount(show["revenue_eur"], "eur")
            tickets = show["tickets"]
            print(f"  {label}  {amount} ({tickets} tickets)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Get revenue summary from Stripe.")
    parser.add_argument("--from", dest="from_date", required=True, metavar="YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", required=True, metavar="YYYY-MM-DD")
    args = parser.parse_args()

    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        print("Error: STRIPE_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    stripe.api_key = api_key
    get_revenue(args.from_date, args.to_date)


if __name__ == "__main__":
    main()
