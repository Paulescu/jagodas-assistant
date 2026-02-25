# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jagoda's Assistant is a Claude Code-based automation tool for a Stand Up Comedian. It automates repetitive tasks (emails, Stripe data exports, Facebook marketing) so Jagoda can focus on writing and performing.

## Current Features

- Export emails and phone numbers of ticket buyers for a given show from Stripe.

## Commands

### Export ticket buyers for a show (natural language)

When asked to export customers for a show, run:

```bash
uv run python scripts/export_customers_natural.py "<user's description>"
```

Use the user's exact description as the query. Claude will match it to the right Stripe product and export the CSV.

### Export ticket buyers for a show (by product ID)

```bash
uv run python scripts/export_stripe_customers.py <STRIPE_PRODUCT_ID>
```

First-time setup:
```bash
uv sync
cp .env.example .env  # then add STRIPE_API_KEY and ANTHROPIC_API_KEY
```

## How to Use (for Jagoda)

Just open Claude Code in this folder and type naturally, for example:

- "Export customer details for my show tomorrow"
- "Export the list for my show in Belgrad on Friday"

Claude will understand and handle the rest.

## Project Status

Early stage — features will expand. As the project grows, update this file with build/lint/test commands and architecture notes.
