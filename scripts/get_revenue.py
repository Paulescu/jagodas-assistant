"""Print a revenue summary for a date range from Stripe completed checkout sessions.

Usage:
    uv run python scripts/get_revenue.py --from YYYY-MM-DD --to YYYY-MM-DD

Reads STRIPE_API_KEY from .env.
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

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


def get_revenue(from_date: str, to_date: str) -> None:
    start_ts = int(datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    # end of to_date: 23:59:59 UTC
    end_ts = int(datetime.strptime(to_date, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59, tzinfo=timezone.utc
    ).timestamp())

    sessions = stripe.checkout.Session.list(
        status="complete",
        created={"gte": start_ts, "lte": end_ts},
        expand=[
            "data.line_items",
            "data.line_items.data.price",
            "data.line_items.data.price.product",
        ],
        limit=100,
    )

    # product_id -> {"name": str, "revenue": int, "tickets": int, "currency": str}
    by_show: dict[str, dict] = defaultdict(lambda: {"name": "", "revenue": 0, "tickets": 0, "currency": ""})
    grand_total = 0
    currency = ""
    session_count = 0

    for session in sessions.auto_paging_iter():
        session_count += 1
        session_currency = (session.get("currency") or "").lower()
        if session_currency and not currency:
            currency = session_currency

        grand_total += session.get("amount_total") or 0

        line_items = session.get("line_items")
        if not line_items:
            continue

        for item in line_items.get("data", []):
            price = item.get("price") or {}
            product = price.get("product") or {}
            if not isinstance(product, dict):
                continue

            product_id = product.get("id") or ""
            product_name = product.get("name") or product_id
            quantity = item.get("quantity") or 0
            unit_amount = price.get("unit_amount") or 0
            item_revenue = quantity * unit_amount

            show = by_show[product_id]
            show["name"] = product_name
            show["revenue"] += item_revenue
            show["tickets"] += quantity
            show["currency"] = session_currency

    if session_count == 0:
        print("No completed sales found for this period.")
        sys.exit(0)

    print(f"Period: {from_date} to {to_date}")
    print(f"Gross revenue: {format_amount(grand_total, currency)}")
    print(f"Transactions: {session_count}")

    if by_show:
        print()
        print("By show:")
        name_width = max(len(s["name"]) for s in by_show.values())
        for show in sorted(by_show.values(), key=lambda s: -s["revenue"]):
            label = show["name"].ljust(name_width)
            amount = format_amount(show["revenue"], show["currency"] or currency)
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
