# Lab 6: User ID Controlled by Request Parameter with Unpredictable User IDs

**Category:** Access Control Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [User ID controlled by request parameter, with unpredictable user IDs](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-unpredictable-user-ids)

## Overview

Same IDOR as Lab 5, but user IDs are GUIDs — not guessable by enumeration. However, the app leaks carlos's GUID on a blog post authored by him. Finding it and using it in the account URL still works because the missing ownership check on `/my-account` is unchanged.

## Key Concepts

- **Unpredictable IDs reduce enumeration, not access control.** A GUID stops brute-forcing but doesn't fix a missing server-side ownership check.
- **ID leakage through application features:** any place the app renders a user's profile link, author attribution, comment history, etc. exposes their ID to any other user who can view that page.
- **IDOR with indirect discovery:** attacker finds the target's ID through normal application browsing, then exploits the missing check.

## Solution

### Step 1 — Log in

Credentials: `wiener` / `peter`.

### Step 2 — Find carlos's GUID via blog posts

Browse the blog and find a post authored by `carlos`. Click his username or inspect the author link — the URL will contain his GUID:
```
/blogs?userId=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Copy the GUID.

### Step 3 — Access carlos's account page

```
/my-account?id=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Step 4 — Grab the API key and submit

Copy the API key from carlos's account page and submit it. Lab solved.

## How It Works

The server uses GUIDs as the identifier, which prevents sequential guessing. But:
1. The blog feature links author names to their profiles, exposing GUIDs to anyone who views a post.
2. The `/my-account` handler still doesn't verify the requesting user owns the account.

Both conditions together make the exploit work.

## Why GUIDs Don't Fix IDOR

A GUID is a secret in name only if it's never revealed. As soon as any app feature exposes it (author links, shared resources, activity feeds, error messages), it's public. The correct fix is an ownership check — the identifier's entropy is irrelevant.

## Remediation

- Same as Lab 5: enforce ownership server-side.
- Avoid exposing internal user identifiers in publicly visible features (author links, profile URLs). Use a separate public-facing username instead of the internal GUID.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-06-userid-unpredictable-ids/solve.py)

Fetches the blog post list, finds a post by `carlos`, extracts his GUID from the author link, then fetches his account page and submits the API key.

## Key Takeaways

- Unpredictable IDs are not a substitute for access control checks.
- Applications routinely expose IDs in author attributions, profile links, and activity feeds.
- The fix is always a server-side ownership check, regardless of ID format.
