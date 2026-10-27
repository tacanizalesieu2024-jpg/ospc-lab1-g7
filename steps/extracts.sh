#!/bin/bash
# One file per region for the regional managers, with the columns
# order_id, order_date, product_category, quantity, unit_price.
# Fix generated with the help of Claude (Anthropic).
# Reads DATA by absolute path instead of a path relative to the folder the script
# moved into, stops on any error, and no longer hides grep's error messages.
set -euo pipefail

DATA=${DATA:-$HOME/data/sales_2025.csv}
OUT=${OUT:-$HOME/data/out}
mkdir -p "$OUT/extracts"

for region in Iberia DACH France Italy Benelux Nordics; do
    # grep exits with 1 when a region has no orders: that is not an error
    { grep ",$region," "$DATA" || [ $? -eq 1 ]; } | cut -d, -f1,2,4,6,7 > "$OUT/extracts/$region.csv"
done
echo "extracts: done"
