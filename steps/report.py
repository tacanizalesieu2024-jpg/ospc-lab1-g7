"""Revenue by region and month (revenue_by_region_month.csv)."""
# Fix generated with Claude (Anthropic). Prompt: "start with the fixes for task 1".
# The file is read in chunks and only the totals per region and month are kept,
# instead of loading all orders (and two more copies of them) into memory at once.

import os

import pandas as pd

DATA = os.environ.get("DATA", os.path.expanduser("~/data/sales_2025.csv"))
OUT = os.environ.get("OUT", os.path.expanduser("~/data/out"))
os.makedirs(OUT, exist_ok=True)

CHUNK = 1_000_000
COLUMNS = ["region", "order_date", "quantity", "unit_price"]

partials = []
n = 0
for chunk in pd.read_csv(DATA, usecols=COLUMNS, chunksize=CHUNK):
    n += len(chunk)
    month = pd.to_datetime(chunk["order_date"]).dt.month
    revenue = chunk["quantity"] * chunk["unit_price"]
    partials.append(revenue.groupby([chunk["region"], month]).sum())
print(f"report: read {n:,} orders in chunks of {CHUNK:,}", flush=True)

table = pd.concat(partials).groupby(level=[0, 1]).sum().unstack()
table.round(2).to_csv(os.path.join(OUT, "revenue_by_region_month.csv"))
print("report: done", flush=True)
