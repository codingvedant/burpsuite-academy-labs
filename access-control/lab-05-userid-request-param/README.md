# Lab 5: User ID Controlled by Request Parameter

**Category:** Access Control Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [User ID controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter)

## Overview

The account page renders data for whoever the `id` URL parameter names, with no check that the logged-in user matches. Changing `id=wiener` to `id=carlos` returns carlos's account including his API key — a textbook horizontal privilege escalation via IDOR.

## Key Concepts

- **IDOR (Insecure Direct Object Reference):** a user-supplied identifier (here a username in the URL) directly selects a database record with no ownership check.
- **Horizontal privilege escalation:** accessing another user's data at the same privilege level (not escalating to admin — just crossing the boundary between users).
- **Predictable identifiers:** usernames are guessable. Even numeric IDs are enumerable. The fix is a server-side ownership check, not making IDs hard to guess.

## Solution

### Step 1 — Log in

Credentials: `wiener` / `peter`. After login, the URL is:
```
/my-account?id=wiener
```

### Step 2 — Change the id parameter

Navigate to:
```
/my-account?id=carlos
```

### Step 3 — Grab the API key

Carlos's account page renders, showing his API key.

### Step 4 — Submit the solution

Click **Submit solution** and paste the API key. Lab solved.

## How It Works

The server fetches account data with something like:
```python
user = db.get_user(request.args['id'])
render_account(user)
```

No comparison between `request.args['id']` and `session['logged_in_user']` — the logged-in user is irrelevant to what gets returned.

## Remediation

- Always verify that the resource referenced by the ID belongs to the authenticated user:
  ```python
  if request.args['id'] != session['username']:
      return 403
  ```
- For numeric IDs, use unpredictable values (UUIDs) **and** enforce ownership — obscurity alone is not a fix.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-05-userid-request-param/solve.py)

Logs in as `wiener`, fetches `/my-account?id=carlos`, extracts the API key, and submits the solution.

## Key Takeaways

- **IDOR** is a horizontal access control failure — same privilege level, wrong user's data.
- Predictable identifiers (usernames, sequential IDs) make enumeration trivial, but even random IDs need ownership checks.
- The session tells the server who you are; every resource access must be validated against that, not against what the client claims.
