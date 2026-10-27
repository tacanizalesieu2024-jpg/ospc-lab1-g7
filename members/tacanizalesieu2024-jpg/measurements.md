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

## Task 3 – after the fix
- sample: 0.53 s elapsed, 1.02 s user, 0.11 s system, 128404 KB peak memory
- strace -c on sample: openat 686, write 17, close 673
- full 8.4M: 16.95 s elapsed, 17.05 s user, 0.51 s system, 634692 KB peak memory
- check.py: PASS audit_2025.csv (8,400,000 lines)

## Task 4 – segments (before)
- sample: 1.04 s elapsed, 1.51 s user, 0.14 s system, 132420 KB peak memory
- full 8.4M: 46.07 s elapsed, 45.19 s user, 1.53 s system, 744464 KB peak memory
- cProfile (sample, 1.917 s): segment() called 100,000 times, cumtime 1.048 s (~55%);
  strptime 100,000 calls (0.995 s cum); locale.getlocale 100,004 calls

## Task 4 – after the fix
- vectorized, no chunks: 9.33 s elapsed, 6.91 s user, 3.00 s system, 1650792 KB peak memory
- vectorized, size as int8: 6.15 s elapsed, 5.82 s user, 0.93 s system, 1259216 KB peak memory
- final (chunked): 6.03 s elapsed, 6.02 s user, 0.61 s system, 374368 KB peak memory
- cProfile on sample after: 454,991 calls in 0.432 s
- check.py: PASS segments.csv

## Task 5 – stats
- old (16 workers): 11.18 s elapsed, 78.79 s user, 4.43 s system, 112804 KB peak memory
- new (8 workers = nproc): 10.52 s elapsed, 74.01 s user, 3.82 s system, 111736 KB peak memory
- simulated Ctrl-C (kill -INT -- -PID) on old: 16 workers left running, parent PID 1
- simulated Ctrl-C on new: "stats: stopping 8 workers", exit 130, 0 workers left
- check.py: PASS stats.csv
