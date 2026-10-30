# Measurements: afrancoieu2024-prog

Laptop: Apple MacBook Air 15-inch M3 2024, macOS Sonoma 14.6
Container: 8 CPUs, memory limit 2147483648 bytes (2 GiB), swap limit 0

## 5.1 Warm-up: generating the report
- `ls -l run_report.sh` (original template): `-rw-r--r-- 1 analyst analyst 402 Oct 27 15:55`
- `./run_report.sh`: `bash: ./run_report.sh: Permission denied`, exit status 126
- Missing permission: execute (x), for owner, group and others
- After `chmod +x`: `-rwxr-xr-x`
- `bash run_report.sh` works because bash only needs to read the file; the x bit is needed only when the kernel executes the file directly with `./`

## 5.2 Task 1: generating the report again
- Whole pipeline (original template, `/usr/bin/time`): 90.81 s elapsed, 119.99 s user, 17.57 s system, 2090328 KB peak memory
- Step that failed: `steps/report.py`. It printed `report: loaded 8,400,000 orders (887 MiB)` and then `./run_report.sh: line 10: 359 Killed`. It never printed `report: done`, and the script went on to the next steps
- Missing output: `revenue_by_region_month.csv` was not rewritten (it is dated Oct 27 16:52, from an earlier run). Also, all 6 `extracts/*.csv` files are 0 bytes (Task 2)
- `python3 steps/report.py` alone: `Killed`, exit status 137 (128 + 9 = SIGKILL)
- `/sys/fs/cgroup/memory.max`: 2147483648 (2 GiB)

| memory.events | baseline | after pipeline | after report.py alone |
|---|---|---|---|
| max | 9 | 5788 | 59179 |
| oom | 0 | 1 | 2 |
| oom_kill | 0 | 1 | 2 |

| Orders | Table size | Peak memory (KB) | Elapsed | User | System |
|---|---|---|---|---|---|
| 1,000,000 | 106 MiB | 511640 | 1.53 s | 1.81 s | 0.18 s |
| 2,000,000 | 211 MiB | 858060 | 2.43 s | 2.83 s | 0.20 s |
| 4,000,000 | 423 MiB | 1572024 | 4.76 s | 4.96 s | 0.40 s |
| 8,400,000 | 887 MiB | about 3,100,000 (extrapolated) | killed | | |

Growth is linear: about 105 MiB of table per million orders and about 350 MiB of peak memory per million orders, plus about 140 MB fixed.

### Answers
1. Exit status 137 = 128 + 9: the process was ended by signal 9 (SIGKILL), which cannot be caught. The sender was the kernel's out-of-memory killer. The `oom_kill` line of `memory.events` confirms it: it went from 0 to 1 after the pipeline and to 2 after the standalone run.
2. The 887 MiB printed is only the loaded table. The peak memory of the process is about 3.6 to 4.7 times larger (1.5 GiB at 4M orders), so the whole file needs about 3 GiB. That is more than the 2 GiB limit of the container, so the kernel killed it.
3. The whole file would need about 3 GiB (extrapolated from 1M, 2M and 4M), about 1.5 times the limit.
4. With `| tee`, stdout is a pipe, so Python buffers it. The process was killed by SIGKILL before it could flush, so the `loaded` line never left the buffer. On a terminal the output is line-buffered, so it appeared.

## 5.3 Task 2: extracting data
- Expected (README): `extracts/REGION.csv`, the orders of each of the 6 regions
- `bash steps/extracts.sh` (original template): printed `extracts: done`, exit status 0
- Result: all 6 files (Benelux, DACH, France, Iberia, Italy, Nordics) are 0 bytes
- Manual pipeline from `~/data/out/extracts`: `grep: ../data/sales_2025.csv: No such file or directory`, `wc -l` printed 0, `PIPESTATUS` = `2 0 0`
- `pwd` = `/home/analyst/data/out/extracts`, and `ls ../data` fails (no `~/data/out/data`)
- After the team fix (commit 2540d23): `extracts: done`, exit 0, `check.py` PASS for all 6 extracts (Benelux 1,006,912; DACH 1,846,894; France 1,345,118; Iberia 2,183,057; Italy 1,178,032; Nordics 839,987)

### Answers
1. The script does `cd "$OUT/extracts"`, which is `~/data/out/extracts`, and then reads `../data/sales_2025.csv`. That path resolves to `~/data/out/data/sales_2025.csv`, which does not exist. The real file is `~/data/sales_2025.csv`. The shell creates `"$region.csv"` for the `>` redirection before grep runs, so the files exist but stay empty.
2. There is no `set -e` and no `pipefail`. The status of a pipeline is the status of its last command, `cut`, which returned 0 (`PIPESTATUS` was `2 0 0`: grep failed with 2). The `for` loop ended with status 0, so `echo "extracts: done"` ran and the script exited with 0.
3. `2>/dev/null` after grep hides grep's own error messages: "No such file or directory", "Permission denied", "Is a directory". It does not hide errors from `cut`, from the shell (for example, a failed `> "$region.csv"` redirection) or from `cd` and `mkdir`, because those are not grep's stderr.
4. `-e` exits immediately when a command returns non-zero. `-u` treats an unset variable as an error. `pipefail` makes a pipeline return the status of the last command that failed, not just the last command. `-e` alone would not have helped here, because the pipeline's status was 0 (`cut`); it needs `pipefail`. Fix: put `set -euo pipefail` at the top, remove `2>/dev/null`, and use the correct absolute path. Because grep returns 1 for "no match", the team wrote `|| [ $? -eq 1 ]` so an empty region is not treated as an error.

## 5.4 Task 3: auditing
- Prediction: audit.py writes one line per order, so I expected the time to grow with the number of orders (about 84 times the sample for the whole file) and many system calls on the sample
- Original, sample (100,000 orders): 0.77 s elapsed, 1.16 s user, 0.22 s system, 127932 KB peak memory
- Original, whole file (8,400,000 orders): 46.31 s elapsed, 33.16 s user, 13.76 s system, 634996 KB peak memory
- Output on the sample: 100,000 lines, 1,952,269 bytes

| System calls on the sample | Python startup only (`python3 -c pass`) | Original audit.py | Fixed audit.py |
|---|---|---|---|
| openat | 38 | 100,686 | 686 |
| write | 0 | 100,001 | 17 |
| close | 35 | 100,673 | 673 |
| total | 73 | 301,360 | 1,376 |

- Fixed audit.py (open the output once, commit f4fd705), whole file: 10.13 s elapsed, 10.66 s user, 0.08 s system, 634900 KB peak memory; check.py PASS (8,400,000 lines)

### Answers
1. The original made 100,686 openat, 100,001 write and 100,673 close calls for 100,000 orders. For every order the script runs `with open(path, "a") as f:`, so each order costs one openat, one write (the buffer is flushed when the file is closed) and one close: 3 calls per order, about 300,000 in total. The remaining ~1,360 calls are the same ones the fixed version makes: Python startup and importing pandas (686 openat, 673 close) and reading the CSV. The 100,001 writes are 100,000 orders plus the final `print`.
2. On the whole file, 13.76 s of 46.92 s CPU time went into the kernel: 29% system, 71% user. The cause is about 25 million system calls (3 per order for 8.4 million orders). report.py (original, 4M orders) spent only 0.40 s system out of 5.36 s CPU time, about 7.5%, because it reads the file in a few large calls. After the fix, audit.py spends 0.08 s in the kernel (under 1%) and the whole run is 4.6 times faster (46.31 s to 10.13 s).
3. No. The comment is wrong. `close()` flushes Python's buffer to the kernel with `write`, but the kernel keeps the data in its page cache and writes it to the disk later. Only `fsync()` forces it onto the disk. Data already handed to the kernel survives a crash of the Python process, but not a power loss or kernel crash. Opening and closing for each order therefore costs 3 system calls per order and buys almost no extra safety.
4. The output is 1,952,269 bytes, and 1,952,269 / 131,072 = 14.9, so about 15 writes of 128 KiB (the last one partial). The fixed version made 17 writes in total, which is those ~15 plus the `print` and a couple of others. For the whole file (180,634,390 bytes) it would be about 1,379 writes instead of 8,400,000, which is 6,000 times fewer.
