# Web Security Lab Scripts

Python exploit scripts for [PortSwigger Web Security Academy](https://portswigger.net/web-security) labs. Each script automates the full attack chain from login to shell to flag in a single run.

I'm working through these labs to build a deeper understanding of web application vulnerabilities beyond just knowing the theory. Every script here is something I wrote after solving the lab manually in Burp Suite first, then automating the exploit to make sure I actually understood the mechanics.

## What's here

Each vulnerability category has its own directory with:
- Solve scripts that take a lab URL and exploit the vulnerability end-to-end
- Notes breaking down what the vulnerability is, why the exploit works, and how to defend against it

```bash
# Example: exploiting an unrestricted file upload
python file-upload/lab-01-rce-via-web-shell/solve.py https://0aXX00...web-security-academy.net
```

## Labs

**File Upload Vulnerabilities** (7/7) - [labs](file-upload/)

Exploiting file upload functionality to achieve remote code execution through web shells, bypassing content-type restrictions, path traversal, extension blacklists, and race conditions.

**Path Traversal** (6/6) - [labs](path-traversal/)

Reading arbitrary files from the server by manipulating file paths to escape the intended directory using traversal sequences and encoding tricks.

**Server-Side Request Forgery (SSRF)** (5/5) - [labs](ssrf/)

Making the server send HTTP requests to unintended internal services, localhost admin panels, and cloud metadata endpoints by abusing URL parameters.

**Insecure Deserialization** (6/6) - [labs](insecure-deserialization/)

Tampering with serialized objects in session cookies to escalate privileges, inject arbitrary objects, and trigger gadget chains for remote code execution.

**Race Conditions** (6/6) - [labs](race-conditions/)

Exploiting timing gaps in concurrent request processing to bypass business logic limits, skip authentication steps, and abuse partially constructed objects using the single-packet attack technique.

**API Testing** (4/4) - [labs](api-testing/)

Attacking REST APIs by reading their documentation, calling unused HTTP methods, exploiting mass assignment to inject fields the frontend hides, and abusing server-side parameter pollution to hijack internal requests.

**Prototype Pollution** (9/10) - [labs](prototype-pollution/)

Adding properties to JavaScript's Object.prototype so every object inherits attacker-controlled values, chaining a source, gadget, and sink into DOM XSS on the client and privilege escalation or RCE on the server. Client-side labs are documented as browser payloads since they can't be automated with Python.

**CSRF** (1/12) - [labs](csrf/)

Forging state-changing requests that ride the victim's session cookie, then defeating each CSRF defense in turn: flawed token validation, SameSite cookie restrictions, and Referer checks. Exploits are HTML pages delivered from the exploit server.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
