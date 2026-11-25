# Lab: Flawed Enforcement of Business Rules

**Category:** Business Logic Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [Flawed enforcement of business rules](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-flawed-enforcement-of-business-rules)

## Overview

The shop has two discount codes: `NEWCUST5` (shown on the homepage) and `SIGNUP30` (newsletter signup reward). The app prevents applying the same code twice **in a row** but does not track how many times each code has been used overall. By alternating between the two codes, the check is bypassed and both discounts can be stacked repeatedly until the price drops below the $100 store credit.

## Key Concepts

- **Insufficient state tracking:** The app only checks the *last* applied code, not whether the code has been used before.
- **Code alternation bypass:** Switching between two valid codes each time resets the "last used" check, allowing unlimited stacking.

## Exploit Flow

### Step 1 — Obtain both discount codes

- `NEWCUST5` — displayed in the banner on the homepage
- `SIGNUP30` — sign up to the newsletter (link in the page footer)

### Step 2 — Add the jacket to cart

Add the **Lightweight l33t leather jacket** to the cart.

### Step 3 — Alternate codes until price drops below $100

Apply codes in alternating order:
```
NEWCUST5 → SIGNUP30 → NEWCUST5 → SIGNUP30 → ...
```

Each pair reduces the price. Continue until the total is within the $100 store credit budget.

### Step 4 — Checkout

Complete the purchase with the store credit.

## Remediation

- Track discount code usage per order/account, not just the last applied code.
- Enforce a maximum number of uses per code per customer server-side.
- Validate the cumulative discount against a maximum allowed percentage/amount before applying.

## Key Takeaways

- Business rule enforcement must consider the full application state, not just the immediate previous action.
- Two "safe" codes that can each be used once become dangerous when the enforcement only checks adjacency.
- Always test discount/coupon logic by applying the same code or combinations of codes multiple times.
