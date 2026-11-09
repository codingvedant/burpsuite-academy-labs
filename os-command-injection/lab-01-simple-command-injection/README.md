# Lab 1: OS command injection, simple case

**Category:** OS Command Injection
**Difficulty:** Apprentice
**Lab link:** [OS command injection, simple case](https://portswigger.net/web-security/os-command-injection/lab-simple)

## Overview

The product-page "Check stock" feature passes `productId` and `storeId` directly into a shell command (`stockreport.pl <productId> <storeId>`) with no escaping. Injecting `|whoami` into `storeId` chains a second command whose output replaces the stock count in the response.

## Key Concepts

- **Shell metacharacters** (`&`, `;`, `|`, `&&`, `||`, backticks, `$()`) break out of the intended command when user input is concatenated into a shell string.
- **Non-blind (in-band) injection:** command output is returned directly in the HTTP response — the easiest class to detect and exploit.
- **Pipe (`|`)** is the lightest metacharacter — doesn't require spaces or special escaping, and its output replaces the original command's output cleanly.

## Burp Setup

- Proxy → intercept on, browse to any product's "Check stock" button.
- Send the captured `POST /product/stock` to Repeater.

## Solution

Change the body from:
```
productId=1&storeId=1
```

to:
```
productId=1&storeId=1|whoami
```

Send. Response body contains the username (e.g. `peter-xxxxxx`) → lab solved.

URL-encode the pipe (`%7c`) if Burp's auto-encoding complains, though usually works raw.

## How It Works

The back-end builds and executes:
```bash
stockreport.pl 1 1|whoami
```

The pipe makes the shell run `whoami` and that command's stdout becomes the final output the app reads. The app returns that output as the stock-check response body, verbatim.

## Why It Worked

- Application passes `storeId` into a shell command string without escaping.
- Shell interprets `|` as a pipe to chain commands.
- Output of the injected command (`whoami`) becomes the response.

## Remediation

- **Never pass user input to a shell.** Use the language's exec-with-argv API (`subprocess.run([...], shell=False)` in Python, `execFile` in Node) so the shell never sees the input as code.
- If a shell is unavoidable, **allow-list** the input to a tight character set (digits only for a numeric store ID) and reject anything else. Blacklists always have a bypass.
- Drop privileges — the web process shouldn't be root.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/os-command-injection/lab-01-simple-command-injection/solve.py)

## Key Takeaways

- **Any parameter passed into a shell command string is a candidate** for `|cmd`, `&&cmd`, `;cmd` injection.
- **Test with `whoami`, `id`, or `uname -a`** — small, universally available, output is unmistakable.
- **Pipe is the gentlest primitive** when you just want to replace the command's output with your own.
- **The fix is an API change** (exec-with-argv), not escaping. Escaping is a lost cause.
