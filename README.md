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

**Insecure Deserialization** (4/5) - [labs](insecure-deserialization/)

Tampering with serialized objects in session cookies to escalate privileges, inject arbitrary objects, and trigger gadget chains for remote code execution.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
