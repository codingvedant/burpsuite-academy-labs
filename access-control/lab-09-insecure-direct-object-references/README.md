# Lab 9: Insecure Direct Object References

**Category:** Access Control Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [Insecure direct object references](https://portswigger.net/web-security/access-control/lab-insecure-direct-object-references)

## Overview

The live chat feature saves transcripts as sequentially numbered files (`1.txt`, `2.txt`, …) and serves them directly by filename with no ownership check. Fetching `1.txt` returns another user's transcript which contains their password in plaintext. Use it to log in as `carlos`.

## Key Concepts

- **IDOR on static/file resources:** the direct object reference is a filename. The server serves whatever file is requested from the transcripts directory without checking who owns it.
- **Sequential identifiers are enumerable:** `1.txt`, `2.txt` etc. are trivially guessable. The fix is ownership checks, not randomising filenames.
- **Sensitive data in chat logs:** credentials typed into a chat (or any user-generated content store) leak if the storage is IDOR-vulnerable.

## Solution

### Step 1 — Trigger a transcript download

Open the live chat, send any message, then click **View transcript**. The browser downloads a file — observe the URL in Burp:
```
GET /download-transcript/2.txt
```

### Step 2 — Fetch transcript 1

Change the filename to `1.txt`:
```
GET /download-transcript/1.txt
```

The response is another user's transcript containing:
```
I forgot my password, it's: CARLOS-PASSWORD
```

### Step 3 — Log in as carlos

Use the disclosed password to log in as `carlos`. Lab solved.

## How It Works

The server maps the filename directly to a file on disk:
```python
return send_file(f"/transcripts/{filename}")
```

No session check, no ownership table lookup — any filename is served to any requester.

## Remediation

- Store transcripts with unpredictable names (UUIDs) **and** enforce ownership on retrieval.
- Map resource IDs to owners in the database; verify on every access that the requesting session owns the resource.
- Never store credentials in chat logs or any user-readable store.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-09-insecure-direct-object-references/solve.py)

Fetches transcript `1.txt`, extracts the password, and logs in as `carlos`.

## Key Takeaways

- IDOR applies to any resource type: files, database records, API objects, chat logs.
- Sequential filenames / IDs make enumeration trivial but are not the root cause — a UUID still needs an ownership check.
- Chat/support systems are common sources of credential leakage if users type passwords into them.
