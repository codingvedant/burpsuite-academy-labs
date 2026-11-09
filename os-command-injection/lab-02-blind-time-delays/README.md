# Lab 2: Blind OS command injection with time delays

**Category:** OS Command Injection
**Difficulty:** Practitioner
**Lab link:** [Blind OS command injection with time delays](https://portswigger.net/web-security/os-command-injection/lab-blind-time-delays)

## Overview

The feedback-submission endpoint passes the `email` parameter into a shell command. The response contains no command output, so we can't use the Lab 1 technique. Instead: inject `||ping -c 10 127.0.0.1||` so the shell runs `ping` when the real command fails. 10 ICMP packets to loopback = ~10-second response delay → blind execution confirmed.

## Key Concepts

- **Blind injection** means no command output in the response. Detection relies on observable side effects — timing, output redirection to a readable file, or out-of-band DNS/HTTP via OAST.
- **`||` (OR) operator:** `cmd1 || cmd2` runs cmd2 only if cmd1 failed (non-zero exit). Useful when the injected context's first command fails on invalid input, letting us pivot to our command.
- **`ping -c 10 127.0.0.1`:** 10 ICMP packets to loopback, default interval 1s → predictable ~10-second delay. `sleep 10` is the fallback when ping is restricted.
- **Baseline first, then payload.** Compare normal response time against payload response time — jitter is usually <500ms, so a 10s jump is unambiguous.

## Burp Setup

- Proxy → intercept the feedback-submit request.
- Send to Repeater.

## Solution

Change the `email` parameter value to:

```
x||ping+-c+10+127.0.0.1||
```

Full body:
```
csrf=<csrf>&name=x&email=x||ping+-c+10+127.0.0.1||&subject=x&message=x
```

Send. Response pane timer should show ~10,000 ms → lab solved.

## Why `||` Instead of `&&`, `;`, or `|`

| Op | Runs second when | Why used/not here |
|---|---|---|
| `&&` | First succeeds | Email command fails on `x`, so second never runs |
| `;` | Always | Works but may hit input validation that rejects multi-statement |
| `\|` | Always (pipe) | Works but expects stdout from first command |
| `\|\|` | First fails | ✓ email validation fails on `x`, ping runs |

The lab's email processing fails on the literal value `x` (not an email format), so `||` correctly falls through to our command.

## Baseline + Payload

Send once with `email=x@x.com` (valid) → note response time (~150ms).
Send with `email=x||ping+-c+10+127.0.0.1||` → response time ~10,000ms.
Delta = ping execution. Blind injection confirmed.

## Why It Worked

- Feedback endpoint concatenates `email` into a shell command string.
- Email value `x` fails some upstream validation/mail command → `||` triggers fallthrough.
- `ping` to loopback runs in the shell, consumes 10 seconds, returns.
- Response blocks until shell returns → 10-second delay.

## Remediation

- Same as Lab 1: **exec-with-argv, never shell concatenation.**
- Validate email input server-side with an email-format regex before processing.
- Monitor for unusual process spawns from the web user (ping, sleep, curl, bash, etc.) as IOCs.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/os-command-injection/lab-02-blind-time-delays/solve.py)

Measures baseline vs payload response time to confirm the delay.

## Key Takeaways

- **Blind injection detection pattern:** baseline → payload → measure delta. Jitter of 500ms, meaningful delay of seconds.
- **`||` for failing-first-command contexts, `&&` for succeeding-first, `;` for any.** Pick based on what the first command is doing to your input.
- **`ping -c N` and `sleep N`** are the two universal timing payloads. Keep both in your pocket.
- **Timing side-channels generalize:** same technique works for blind SQLi (`WAITFOR DELAY`, `SLEEP()`), blind XXE, blind SSRF against localhost services.
