"""Number of orders per region, quarter and order size (segments.csv)."""
# Fix generated with the help of Claude (Anthropic).

import os

import numpy as np
import pandas as pd

DATA = os.environ.get("DATA", os.path.expanduser("~/data/sales_2025.csv"))
OUT = os.environ.get("OUT", os.path.expanduser("~/data/out"))
os.makedirs(OUT, exist_ok=True)

COLUMNS = ["order_date", "region", "quantity", "unit_price"]
NAMES = {0: "large", 1: "medium", 2: "small"}

partials = []
# Chunks of 1M orders; whole columns at once instead of one Python call per order.
for chunk in pd.read_csv(DATA, usecols=COLUMNS, chunksize=1_000_000):
    quarter = pd.to_datetime(chunk["order_date"], format="%Y-%m-%d").dt.quarter
    value = chunk["quantity"] * chunk["unit_price"]
    # Size as a 1-byte code (0 large, 1 medium, 2 small) instead of a string per order.
    size = pd.Series(
        np.select([value >= 500, value >= 100], [0, 1], default=2).astype(np.int8),
        index=chunk.index,
    )
    partials.append(chunk.groupby([chunk["region"], quarter, size]).size())

counts = pd.concat(partials).groupby(level=[0, 1, 2]).sum()
# Build the labels ("Q1 large", ...) once per group, not once per order.
regions = counts.index.get_level_values(0)
labels = [f"Q{q} {NAMES[s]}" for q, s in zip(counts.index.get_level_values(1), counts.index.get_level_values(2))]
counts.index = pd.MultiIndex.from_arrays([regions, labels], names=["region", "segment"])

table = counts.unstack(fill_value=0)
table.to_csv(os.path.join(OUT, "segments.csv"))
print("segments: done")
