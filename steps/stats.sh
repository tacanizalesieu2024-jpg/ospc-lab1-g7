#!/bin/bash
# Bootstrap 95% confidence intervals for the average order value of every
# region and month. The work is split among WORKERS processes that run at
# the same time. More workers than CPUs does not help: they only compete
# for the same CPUs, so the default is the number of CPUs (nproc).
# Fix generated with the help of Claude (Anthropic).
set -euo pipefail

WORKERS=${WORKERS:-$(nproc)}
OUT=${OUT:-$HOME/data/out}

pids=()
# Background processes in a script ignore Ctrl-C (SIGINT), so on Ctrl-C or
# SIGTERM send SIGTERM to every worker explicitly and wait for them to end.
cleanup() {
    trap - INT TERM
    echo "stats: stopping ${#pids[@]} workers" >&2
    kill "${pids[@]}" 2>/dev/null || true
    wait 2>/dev/null || true
    exit 130
}
trap cleanup INT TERM

python3 steps/stats_prepare.py
mkdir -p "$OUT/stats"
rm -f "$OUT"/stats/part_*.csv
for k in $(seq 0 $((WORKERS - 1))); do
    python3 steps/stats_worker.py "$k" "$WORKERS" &
    pids+=($!)
done

# Wait for each worker and fail if any of them failed.
failed=0
for p in "${pids[@]}"; do
    wait "$p" || failed=1
done
if [ "$failed" -ne 0 ]; then
    echo "stats: a worker failed" >&2
    exit 1
fi
cat "$OUT"/stats/part_*.csv | sort > "$OUT/stats.csv"
echo "stats: done with $WORKERS workers"
