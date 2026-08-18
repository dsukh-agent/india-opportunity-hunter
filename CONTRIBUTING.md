# Contributing to India Opportunity Hunter

This is an open, living database of unfashionable, cash-flow-positive business opportunities. Anyone may contribute.

## How to contribute
1. **Open an issue** with the opportunity you want to add, OR
2. **Submit a PR** that adds a row to `data.json` and a section to `README.md`.

## What makes a good entry (the filters)
A contribution is strong when it includes **real numbers**, not vibes:
- **Verdict:** STRONG / MEDIUM / WEAK, with reasoning.
- **Entry capital (₹)** and **EBITDA timeline** — must plausibly reach positive EBITDA quickly (this is the primary gate).
- **Sector + model** (consumer / B2B / service — anything, be broad and odd).
- **Country/city focus** (we curate India first; global later).
- **Sources** — live links with dates. Freshness matters: prefer 2026/2027 data and clearly timestamp older info.
- **Watch-outs / failure modes** — honesty is a feature. Documented negative examples are welcome (see the water tanker entry).

## Anti-bias rule
We deliberately do **not** prioritize tech/web3/startup ideas. Evaluate purely on cash-flow fit. Unfashionable B2B/consumer/service opportunities are exactly what this database is for.

## Format for data.json
Each opportunity is an object in the `opportunities` array. Follow the exact field names of existing entries (`id, title, sector, model, country, city_focus, idea, verdict, entry_capital_inr, ebitda_timeline, margins, why, watchouts, sources, updated_at`).
