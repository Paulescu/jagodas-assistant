# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jagoda's Assistant is a Claude Code-based automation tool for a Stand Up Comedian. It automates repetitive tasks (emails, Stripe data exports, Facebook marketing) so Jagoda can focus on writing and performing.

## Current Features

- Export emails and phone numbers of ticket buyers for a given show from Stripe.

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

## How to Use (for Jagoda)

Open Claude Code in this folder and run:

```
/export-stripe-attendees <your show description>
```

For example:
- `/export-stripe-attendees tonight's show`
- `/export-stripe-attendees my show in Belgrade on Friday`

Claude will match the description to the right Stripe product and export the CSV.

## Project Status

Early stage — features will expand. As the project grows, update this file with build/lint/test commands and architecture notes.
