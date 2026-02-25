Creat a skill that helps me export customer data from stripe. Data is fetched from Stripe API and saved into a new file under the `data/` folder. A new file is always created when invoking this skill, never overwritten.

The skill has an argument which is a Natural Language query that represents the segment of users to export.

Examples

- Plain english without much context
    ```
    /export-stripe-attendees Get list of all people who bought a ticket for tomorrow's show
    ```

- Product_id from Stripe provided
    ```
    /export-stripe-attendees prod_SGdlFX84k2ImuV
    ```

- Name of the show
    ```
    /export-stripte-attendees Get attendance for Belgrade on 2026-02-25
    ```

If the Natural Language Query is ambiguous please follow up with clarifiying questions that the user can answer and then proceed.

Reuse as much logic as possible from the existing py files in `scripts/`.