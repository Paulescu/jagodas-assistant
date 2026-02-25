Create a new Stripe product for a show, guided by a short conversation.

## Workflow

### Step 1: List existing shows

Run from the project root:

```bash
uv run python scripts/list_stripe_products.py
```

- If the script exits with an error or prints "No active products found.", tell the user and stop.
- Otherwise parse the JSON array from stdout. Display a numbered list like:

  ```
  Here are your existing shows (for reference):

  1. Kidaš Irena - 2026-02-14 u 20:00 - Beograd  —  1500 RSD
  2. Kidaš Irena - 2026-02-20 u 19:00 - Novi Sad  —  1200 RSD
  3. Stand-Up Night - 2026-01-10 u 21:00 - Zagreb  —  15 EUR
  ```

  Format the price as `<amount> <CURRENCY>` (uppercase currency, amount in whole units = price_amount / 100).
  If a product has no price, show "no price".

  Then ask: "Which show should I use as a reference? (enter the number)"

  Wait for the user's answer before proceeding.

### Step 2: Ask for show details

Ask for all details in one message:

```
Got it! Now tell me about the new show:
- Show name (e.g. "Kidaš Irena", "Stand-Up Night", …)
- Location (city and venue if known)
- Date (YYYY-MM-DD or natural language)
- Time (HH:MM, 24 h)
```

Wait for the user's answer.

### Step 3: Suggest a product name

Inspect the reference product's `name` to infer the naming convention.

Common pattern: `<Show Title> - <YYYY-MM-DD> u <HH:MM> - <City>`

Generate a suggested name following that pattern, e.g.:
`Kidaš Irena - 2026-03-15 u 20:00 - Novi Sad`

Present it and ask:

```
Suggested name: Kidaš Irena - 2026-03-15 u 20:00 - Novi Sad

Does this look right, or would you like to change it?
```

Wait for confirmation or a corrected name before continuing.

### Step 4: Ask for price and currency

Ask explicitly in one message. Do NOT guess the currency from the location.

```
What is the ticket price?
- Amount (e.g. 1500)
- Currency: RSD for Serbia, EUR or another code for shows abroad
```

If either the amount or the currency is missing from the answer, ask again before continuing.

### Step 5: Confirm before creating

Show a full summary and ask for confirmation:

```
Ready to create the show with these details:

- Name: <name>
- Price: <amount> <CURRENCY>
- Description: <description or "(none)">
- Images: <count or "(none)">
- Metadata: <keys or "(none)">

Shall I create this now? (yes / no / change something)
```

If the user wants to change something, loop back to the relevant step.
Only proceed when the user explicitly says yes (or equivalent).

### Step 6: Create the show

Assemble the `create_stripe_show.py` command. Only include optional flags when
the reference product has non-empty values for them:

- `--description` only if `reference.description` is non-empty
- `--images` only if `reference.images` is non-empty (pass each URL as a separate argument)
- `--metadata` only if `reference.metadata` is non-empty (serialize to JSON string)

Example command:

```bash
uv run python scripts/create_stripe_show.py \
  --name "Kidaš Irena - 2026-03-15 u 20:00 - Novi Sad" \
  --price 1500 \
  --currency rsd \
  --description "Stand-up comedy show" \
  --metadata '{"venue": "Dom omladine"}'
```

Run it from the project root.

Read the output:

- **Success** (exit code 0, output contains "Product created:"): Parse the product ID
  and dashboard URL. Print:
  ```
  - Show: <name>
  - Price: <amount> <CURRENCY>
  - Stripe ID: <product_id>
  - Dashboard: <url>
  ```

- **Any error** (exit code non-zero or output contains "Error:"): Show the error to the
  user and stop.
