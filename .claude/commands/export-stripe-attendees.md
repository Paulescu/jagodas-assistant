Export Stripe customer data for a show and save it to a new CSV file in `data/`.

Arguments: $ARGUMENTS

## Workflow

### Step 1: Parse the arguments

- If `$ARGUMENTS` starts with `prod_`, treat it as a Stripe product ID and jump to **Step 3**.
- Otherwise treat it as a natural language show query and continue to **Step 2**.
- If `$ARGUMENTS` is empty, ask the user: "Which show would you like to export attendees for?"

### Step 2: Natural language matching

Run from the project root:

```bash
uv run python scripts/export_customers_natural.py "$ARGUMENTS"
```

Read the output carefully:

- **Success** (exit code 0, output contains "Exported N customer(s) to"): The file was created. Print a summary in this exact format:
  ```
  - Show: <show name from "Matched show: ..." line>
  - Customers: <N> unique ticket buyers
  - File: <path from "Exported N customer(s) to ..." line>
  ```
  Done.

- **UNCLEAR** (output contains "Multiple shows could match"): The script found several matching shows. Parse the product IDs and names from the output. Present them to the user with AskUserQuestion so they can pick the right one, then proceed to **Step 3** with the selected product ID.

- **NOMATCH** (output contains "No show found matching"): Report back to the user that no show matched their description and list the available shows from the script output. Ask them to try again with a different description.

- **Any other error**: Show the error output to the user and stop.

### Step 3: Export by product ID

Run from the project root:

```bash
uv run python scripts/export_stripe_customers.py <PRODUCT_ID>
```

When complete, print a summary in this exact format:
```
- Markdown table with customer information printed on console
- Show: <show name from "Matched show: ..." line>
- Customers: <N> unique ticket buyers
- File: <path from "Exported N customer(s) to ..." line>
```
