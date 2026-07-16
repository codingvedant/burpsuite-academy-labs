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

**File Upload Vulnerabilities** (3/7) - [labs](file-upload/)

Exploiting file upload functionality to achieve remote code execution through web shells, bypassing content-type restrictions, path traversal, extension blacklists, and race conditions.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
