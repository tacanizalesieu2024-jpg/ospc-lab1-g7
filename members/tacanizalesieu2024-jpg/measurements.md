# Measurements – tacanizalesieu2024-jpg

## Warm-up: permissions
- ./run_report.sh → "bad interpreter: Permission denied"
- ls -l: -rw-r--r-- (no x for anyone) → chmod +x → -rwxr-xr-x
- /usr/bin/time on non-executable script → exit status 126

## Task 1 – full pipeline
160.05 s elapsed, 203.38 s user, 27.83 s system, 2087564 KB peak memory
- report.py: loaded 8,400,000 orders (887 MiB) → Killed; revenue_by_region_month.csv missing
- extracts: 6 files, all 0 bytes, yet the script printed "done"
- python3 steps/report.py alone → Killed, echo $? = 137
- memory.events: oom_kill 2, max 3938

## Task 1 – memory growth (report.py)
| Orders | Table | Elapsed | User | System | Peak memory |
|---|---|---|---|---|---|
| 1M | 106 MiB | 2.33 s | 2.41 s | 0.33 s | 504880 KB |
| 2M | 211 MiB | 3.88 s | 3.94 s | 0.55 s | 856796 KB |
| 4M | 423 MiB | 7.45 s | 7.04 s | 1.00 s | 1565004 KB |
- Linear: ~352,000 KB per extra million orders, ~153,000 KB baseline
- Estimate for 8.4M: ~3,118,000 KB (~3.0 GiB) > 2 GiB limit → OOM kill
- report.py | tee: log empty – stdout block-buffered in a pipe, SIGKILL loses the buffer

## Task 2 – extracts
- bash steps/extracts.sh → "extracts: done", echo $? = 0, all 6 files 0 bytes
- Script cd's to ~/data/out/extracts, then reads ../data/sales_2025.csv → ~/data/out/data/sales_2025.csv (doesn't exist)
- Manual run: "grep: No such file or directory", PIPESTATUS = 2 0 0
- 2>/dev/null hides grep's error; exit 0 because last command is echo
- Fix idea: absolute path via DATA=${DATA:-$HOME/data/sales_2025.csv}, set -euo pipefail, remove 2>/dev/null
