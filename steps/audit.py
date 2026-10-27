"""Audit trail: one line per order with its revenue (audit_2025.csv)."""
# Fix generated with the help of Claude (Anthropic).
# The output file is opened once, before the loop, instead of once per order.
# Python buffers the lines and hands them to the kernel in large writes, so the
# number of openat/write/close system calls no longer grows with the number of orders.
# Note: closing a file never guaranteed the data was on disk; only fsync() does that.

import os

import pandas as pd

DATA = os.environ.get("DATA", os.path.expanduser("~/data/sales_2025.csv"))
OUT = os.environ.get("OUT", os.path.expanduser("~/data/out"))
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, "audit_2025.csv")

orders = pd.read_csv(DATA, usecols=["order_id", "region", "quantity", "unit_price"])
orders["revenue"] = orders["quantity"] * orders["unit_price"]

with open(path, "w") as f:
    for order in orders.itertuples():
        f.write(f"{order.order_id},{order.region},{order.revenue:.2f}\n")
print(f"audit: {len(orders):,} lines written")
