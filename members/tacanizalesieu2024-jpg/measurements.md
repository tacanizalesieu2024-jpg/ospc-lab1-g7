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

## Task 3 – audit
| Data | Elapsed | User | System | Peak memory | Kernel share |
|---|---|---|---|---|---|
| sample 100k | 1.57 s | 1.61 s | 0.39 s | 130132 KB | ~20% |
| full 8.4M | 82.21 s | 62.78 s | 20.04 s | 634632 KB | ~24% |
- report.py kernel share for comparison: ~12%
- strace -c on sample (100k): openat 100686, write 100001, close 100673 (≈1 of each per order)
- audit_2025.csv (sample) = 1,952,269 bytes → with a 128 KiB buffer ≈ 15 write calls
- close() ≠ saved on disk: data goes to the page cache; only fsync() forces it
- Fix idea: open the file once before the loop, close once after

## Task 1 – after the fix (chunked report.py)
- sample: 0.41 s elapsed, 0.91 s user, 0.10 s system, 137632 KB peak memory
- full 8.4M: 5.69 s elapsed, 5.76 s user, 0.53 s system, 390308 KB peak memory, exit 0
- check.py: PASS revenue_by_region_month.csv

## Task 2 – after the fix
- 4.06 s elapsed, 5.02 s user, 1.06 s system, 6564 KB peak memory, exit 0
- All 6 extracts PASS (Benelux 1,006,912 … Nordics 839,987 rows)
- DATA=/no/such/file.csv → "grep: No such file or directory", exit 1
- Works from another folder (cd ~)
