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


## Features TODO

This list will change over time, mostly appending new items:

[x] Export of emails and phone numbers of people who bought tickets for a given show from Stripe.

[] Add skill to create a new Stripe product for a new show. Ask the user which previous product they want to use as a refernce to copy, and from there ask the user what adjustments need to be made: including location, date, time, name of the show. With this info generate the product name. Ask also for the price, and force the user to explicitly set the currency too, as she performs both in Serbia and abroad.

