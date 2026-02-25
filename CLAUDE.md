# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jagoda's Assistant is a Claude Code-based automation tool for a Stand Up Comedian. It automates repetitive tasks (emails, Stripe data exports, Facebook marketing) so Jagoda can focus on writing and performing.

## Current Features

- Export emails and phone numbers of ticket buyers for a given show from Stripe.
- Check revenue for a time period from Stripe.
- Create a new Stripe product (show) with price, guided by a short conversation.

## Commands

### Export ticket buyers for a show (skill — preferred)

Use the `/export-stripe-attendees` skill. It accepts a natural language description or a Stripe product ID:

```
/export-stripe-attendees tonight's show
/export-stripe-attendees my show in Belgrade on Friday
/export-stripe-attendees prod_SGdlFX84k2ImuV
```

If the query is ambiguous, the skill will ask a clarifying question. On success it prints:
```
- Show: <show name>
- Customers: <N> unique ticket buyers
- File: data/customers_<product_id>_<date>.csv
```

Output files are never overwritten — a counter suffix (`_1`, `_2`, …) is added if the file already exists.

### Check revenue for a period (skill)

Use the `/get-revenue` skill with a natural language time period:

```
/get-revenue last 30 days
/get-revenue this month
/get-revenue last week
```

It prints a formatted summary:
```
Period: YYYY-MM-DD to YYYY-MM-DD
Gross revenue: €1,250.00
Transactions: 42

By show:
  Belgrade Comedy Night:  €750.00 (30 tickets)
  Zagreb Special:         €500.00 (20 tickets)
```

### Create a new show in Stripe (skill)

Use the `/create-stripe-show` skill. It walks through a short guided conversation:
picks a reference show, asks for name/location/date/time, suggests a product name,
confirms price and currency, then creates the Stripe product and price.

On success it prints:
```
- Show: <name>
- Price: <amount> <CURRENCY>
- Stripe ID: <product_id>
- Dashboard: <url>
```

### Export ticket buyers for a show (scripts — advanced)

Natural language:
```bash
uv run python scripts/export_customers_natural.py "<description>"
```

By Stripe product ID:
```bash
uv run python scripts/export_stripe_customers.py <STRIPE_PRODUCT_ID>
```

### First-time setup

```bash
uv sync
cp .env.example .env  # then add STRIPE_API_KEY and ANTHROPIC_API_KEY
```

## Security

A `gitleaks` pre-commit hook runs on every commit and blocks any staged files containing secrets (API keys, tokens, credentials). Customer CSV files and `.env` are excluded via `.gitignore`.

## Intent Routing

When Jagoda types a message, map it to the right skill automatically — no slash commands needed.

| If the message is about… | Invoke |
|---|---|
| Exporting attendees / customers / ticket buyers for a show | `export-stripe-attendees` skill, passing her description as the argument |
| Revenue, earnings, sales totals, or how much was sold | `get-revenue` skill, passing her time period as the argument |
| Creating a new show, adding a show to Stripe, setting up a new event | `create-stripe-show` skill (no arguments needed) |

Examples that should all trigger `export-stripe-attendees`:
- "Export list of attendees for tomorrow's show"
- "Get me the customer list for Belgrade on Friday"
- "Who bought tickets for tonight?"
- "Export the CSV for my show next week"

Examples that should all trigger `get-revenue`:
- "How much have I sold in the last 30 days?"
- "What's my revenue this month?"
- "How much did I make last week?"

Examples that should all trigger `create-stripe-show`:
- "Create a new show for next Friday in Novi Sad"
- "I need to add a show to Stripe"
- "Set up a new event for March 15th"

## How to Use (for Jagoda)

Just open Claude Code in this folder and type naturally. For example:

- "Export list of attendees for tomorrow's show"
- "Who bought tickets for my Belgrade show on Friday?"

Claude will understand and handle the rest.

## Project Status

Early stage — features will expand. As the project grows, update this file with build/lint/test commands and architecture notes.
