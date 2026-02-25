Print a revenue summary for a time period from Stripe.

Arguments: $ARGUMENTS

## Workflow

### Step 1: Parse the arguments

- If `$ARGUMENTS` is empty, ask the user: "What time period would you like to check revenue for?"
- Otherwise treat `$ARGUMENTS` as a natural language time period and continue to **Step 2**.

### Step 2: Compute date range

Today's date is available in the `currentDate` context. Compute `from_date` and `to_date` (both as `YYYY-MM-DD`) using these mappings:

| Natural language | from_date | to_date |
|---|---|---|
| "last 30 days" | today minus 30 days | today |
| "last 7 days" / "last week" | today minus 7 days | today |
| "last month" | first day of previous calendar month | last day of previous calendar month |
| "this month" | first day of current month | today |
| "this year" | January 1 of current year | today |
| "last year" | January 1 of previous year | December 31 of previous year |

For any other phrasing, interpret it sensibly using today as the reference point.

### Step 3: Run the script

```bash
uv run python scripts/get_revenue.py --from <from_date> --to <to_date>
```

Print the script output as-is — it is already formatted for the user.
