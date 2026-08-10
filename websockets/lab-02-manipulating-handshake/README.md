# Lab 2: Manipulating the WebSocket handshake to exploit vulnerabilities

**Difficulty:** Practitioner

## Goal

Get an XSS payload to execute in the support agent's browser. The chat has an XSS filter that, when triggered, drops the connection and bans your IP - and the handshake trusts `X-Forwarded-For` for that IP decision.

## Exploit

Two moves combined:

1. Spoof the source IP in the handshake to dodge the ban:
   ```
   X-Forwarded-For: 1.1.1.1
   ```
2. Send an obfuscated XSS payload that bypasses the filter:
   ```
   <img src=1 oNeRror=alert`1`>
   ```

## Steps

1. Send a basic payload (`<img src=1 onerror='alert(1)'>`) - it is blocked, the connection drops, and your IP is banned
2. In WebSockets Repeater, click Reconnect and edit the handshake request, adding `X-Forwarded-For: 1.1.1.1` - the handshake now succeeds despite the ban
3. Send the obfuscated payload (`oNeRror` mixed case, backticks instead of parentheses) - it slips past the filter and fires in the agent's browser

## Why it works

The vulnerability is a design flaw: the app makes a security decision (IP ban) based on an attacker-controllable header, `X-Forwarded-For`. Spoofing it resets the ban. The filter is also weak - it matches specific patterns that mixed-case handlers and backtick calls avoid.

## Takeaway

Never trust HTTP headers like `X-Forwarded-For` for security decisions - they are attacker-controlled, including in the WebSocket handshake. And blocklist-style XSS filters are routinely bypassed with case variation and alternative call syntax.

## Note on automation

Browser/Burp driven - the payload must render in the agent's browser. No Python solve; the payload and handshake header above are the exploit.
