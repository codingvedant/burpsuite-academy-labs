import argparse
import sys
import requests
from colorama import Fore, Style, init
from urllib.parse import urljoin

init(autoreset=True)


class LabSession:
    def __init__(self, description="Solve a Burp Suite Academy lab"):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
        self.args = parser.parse_args()
        self.base_url = self.args.url.rstrip("/")
        self.session = requests.Session()
        # uncomment to route through Burp proxy
        # self.session.proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
        # self.session.verify = False
        self.info(f"Target: {self.base_url}")

    def url(self, path):
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def get(self, path, **kwargs):
        return self.session.get(self.url(path), **kwargs)

    def post(self, path, **kwargs):
        return self.session.post(self.url(path), **kwargs)

    def login(self, username, password, login_path="/login"):
        # Get CSRF token if the login page has one
        resp = self.get(login_path)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrf"})
        data = {"username": username, "password": password}
        if csrf_input:
            data["csrf"] = csrf_input["value"]
        resp = self.post(login_path, data=data)
        if resp.status_code == 200 and "my-account" in resp.url:
            self.success(f"Logged in as {username}")
        else:
            self.fail(f"Login failed for {username}")
        return resp

    def check_solved(self):
        resp = self.get("/")
        if "Congratulations" in resp.text:
            self.success("Lab solved!")
            return True
        self.fail("Lab not solved yet.")
        return False

    @staticmethod
    def info(msg):
        print(f"{Fore.BLUE}[*]{Style.RESET_ALL} {msg}")

    @staticmethod
    def success(msg):
        print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {msg}")

    @staticmethod
    def fail(msg):
        print(f"{Fore.RED}[-]{Style.RESET_ALL} {msg}")
        sys.exit(1)

    @staticmethod
    def warn(msg):
        print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")
