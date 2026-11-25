# Lab: Excessive Trust in Client-Side Controls

**Category:** Business Logic Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [Excessive trust in client-side controls](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-excessive-trust-in-client-side-controls)

## Overview

The application sends the product price as a parameter in the add-to-cart POST request and trusts it without server-side validation. By intercepting and modifying the price, an attacker can purchase any item for an arbitrary amount — including 1 cent.

## Key Concepts

- **Client-side trust:** Any data sent by the browser can be modified by the user. Price, quantity, discounts, and other business-critical values must be validated server-side.
- **Parameter tampering:** Changing hidden form fields or POST parameters to manipulate application logic.

## Exploit Flow

### Step 1 — Add the jacket to cart and intercept

Add the **Lightweight l33t leather jacket** to the cart. The intercepted `POST /cart` request contains:
```
productId=1&redir=PRODUCT&quantity=1&price=133700
```

### Step 2 — Modify the price

Change `price=133700` to `price=1` (1 cent) and forward the request.

### Step 3 — Checkout

Complete the purchase with the $100 store credit. The server accepts the tampered price and completes the order.

## Remediation

- Never trust price, discount, or quantity values from the client — always look them up server-side from the product catalog.
- Treat all client-submitted data as untrusted input.
- Use server-side cart/session storage for pricing rather than relying on request parameters.

## Key Takeaways

- If it comes from the browser, it can be changed — business logic must be enforced server-side.
- Always intercept and inspect add-to-cart, checkout, and payment requests for client-controlled pricing parameters.
