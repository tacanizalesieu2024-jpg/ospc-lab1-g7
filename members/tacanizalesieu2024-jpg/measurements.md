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
