# Jagoda's Assistant

## The problem

[Jagoda](https://jagodajovanovic.com/) is a Stand Up Comedian who wants to spend more time working on her jokes, writing new material and performing, and less time doing boring (but absolutely necessary) things like:

- sending emails to attendees of her shows
- exporting customer information from Stripe payments to share with venue organizers
- managing FB marketing campaigns
- creating new show products on Stripe
- etc. (honestly there are many more, but we will get there step by step)


## The solution

This project is a Claude Code-based solution that automates Jagoda's work.

The main authors are Claude Code itself and her husband, who happens to be me, the one writing this document.

My name is Pau Labarta Bajo, and I am an AI engineer working at Liquid AI. This project is my attempt to help my wife while spending minimum time — because hey, I already have a lot to do at Liquid AI.


## Quickstart

**Prerequisites:** Claude Code installed, and a `.env` file with `STRIPE_API_KEY` and `ANTHROPIC_API_KEY`.

Open Claude Code in this folder, then run:

### Export ticket buyers for a show

```
/export-stripe-attendees tonight's show
/export-stripe-attendees my show in Belgrade on Friday
/export-stripe-attendees prod_SGdlFX84k2ImuV
```

Claude matches your description to the right Stripe product, exports a CSV to `data/`, and prints a summary:

```
- Show: Kidaš Irena - 2026-02-25 u 20:00 - Beograd
- Customers: 34 unique ticket buyers
- File: data/customers_prod_SGdlFX84k2ImuV_2026-02-25.csv
```

If your description matches more than one show, Claude will ask you to pick the right one.


## Features

This list will change over time, mostly appending new items:

[x] Export of emails and phone numbers of people who bought tickets for a given show from Stripe.

[] Add skill to create a new Stripe product for a new show. Ask the user which previous product they want to use as a refernce to copy, and from there ask the user what adjustments need to be made: including location, date, time, name of the show. With this info generate the product name. Ask also for the price, and force the user to explicitly set the currency too, as she performs both in Serbia and abroad.

[x] Add skill /get-revenue to check earnings. I want Jagoda to be able to ask "How much have I sold in the last 30 days" and this slash command is picked up by Claude Code. Implement this slash command the then add a route in the ## Intent Routing in CLAUDE.md so Jagoda does not need to remember the slash command.