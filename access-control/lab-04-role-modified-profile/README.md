# Lab 4: User Role Can Be Modified in User Profile

**Category:** Access Control Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [User role can be modified in user profile](https://portswigger.net/web-security/access-control/lab-user-role-can-be-modified-in-user-profile)

## Overview

The email-update endpoint accepts a JSON body and binds all fields to the user model, including `roleid`. The server response reveals the current role ID, and sending `"roleid": 2` in a subsequent request upgrades the account to admin. Classic mass assignment — the API doesn't filter which fields callers are allowed to set.

## Key Concepts

- **Mass assignment (over-posting):** the server deserializes the full request body into a model object without whitelisting allowed fields. Any field in the model can be set by the client.
- **API response leaks model shape:** the response body reveals internal fields (`roleid`, `email`, etc.) that the client shouldn't necessarily see or control.
- **Vertical privilege escalation via JSON field injection:** adding an unauthorized field to the request body escalates the caller's privileges.

## Solution

### Step 1 — Log in and go to account page

Credentials: `wiener` / `peter`. Navigate to `/my-account`.

### Step 2 — Intercept the email change request

Change your email and capture the request in Burp. The body is JSON:
```json
{"email": "newemail@test.com"}
```

The response includes your user object:
```json
{
  "username": "wiener",
  "email": "newemail@test.com",
  "roleid": 1
}
```

### Step 3 — Resend with roleid: 2

Modify the request body:
```json
{"email": "newemail@test.com", "roleid": 2}
```

Send it. The server updates `roleid` to 2 (admin).

### Step 4 — Access admin panel and delete carlos

Navigate to `/admin`. Delete `carlos`. Lab solved.

## How It Works

The server's update handler does something like:
```python
user.update(request.json)   # binds ALL fields from JSON to the model
db.save(user)
```

No field whitelist — `roleid` gets updated just like `email`.

## Remediation

- **Whitelist updatable fields** at the API layer — only allow the specific fields a user should control (e.g. `email`).
- Never expose internal model fields (`roleid`, `is_admin`) in API responses unless required.
- Use separate DTOs (Data Transfer Objects) for input vs. the full model — the input DTO only contains fields the user may set.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-04-role-modified-profile/solve.py)

Logs in, posts `{"email": "x@x.com", "roleid": 2}` to the update endpoint, then deletes `carlos`.

## Key Takeaways

- **Mass assignment** is an API-layer vulnerability — the server binds all request fields to the model without filtering.
- API responses that expose internal fields (like `roleid`) reveal the attack surface.
- Whitelisting allowed input fields (not blacklisting forbidden ones) is the correct fix.
