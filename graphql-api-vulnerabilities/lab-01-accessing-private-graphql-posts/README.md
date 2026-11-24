# Lab: Accessing Private GraphQL Posts

**Category:** GraphQL API Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [Accessing private GraphQL posts](https://portswigger.net/web-security/graphql/lab-graphql-reading-private-posts)

## Overview

The blog app exposes a GraphQL endpoint. The `getAllBlogPosts` query only returns public posts, but the `getBlogPost(id: X)` query fetches any post by ID — including private ones. Private posts contain a `postPassword` field not shown through the normal UI. By iterating IDs, an attacker can read hidden content.

## Key Concepts

- **Broken object-level authorization:** The API enforces visibility at the listing level but not at the individual object level.
- **Field exposure:** Private fields (`postPassword`, `isPrivate`) are present in the schema and returned by the API — they just aren't requested by the front-end.
- **ID enumeration:** Integer post IDs are sequential and predictable.

## Exploit Flow

### Step 1 — Intercept the GraphQL request

Browse the blog homepage. The app sends:
```graphql
query getBlogSummaries {
    getAllBlogPosts {
        image
        title
        summary
        id
    }
}
```

### Step 2 — Query individual posts with hidden fields

In Burp Repeater, modify the request body:
```json
{
  "query": "query getBlogPost { getBlogPost(id: 1) { id title isPrivate postPassword } }",
  "operationName": "getBlogPost"
}
```

### Step 3 — Enumerate IDs

Increment the `id` value (1, 2, 3...) until you find a post where:
- `isPrivate: true`
- `postPassword` is non-null

### Step 4 — Submit the password

Use the value of `postPassword` to solve the lab.

## Remediation

- Apply object-level authorization checks in the resolver, not just at the listing query.
- Never expose sensitive fields (passwords, tokens, internal flags) in the GraphQL schema unless access is strictly controlled.
- Use schema-level field authorization (e.g. per-field middleware) to restrict sensitive fields to authorized roles.

## Key Takeaways

- GraphQL's flexibility means clients can request any field — restricting what the front-end asks for is not a security control.
- Always test `getAllX` vs `getX(id)` — different resolvers often have different authorization logic.
- Integer IDs are enumerable; prefer UUIDs and enforce authorization in the resolver.
