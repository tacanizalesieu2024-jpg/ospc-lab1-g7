# Lab 1 — Measurements

GitHub user: mvillasanteieu2024-sudo
Machine: MacBook Pro 14-inch, Apple M4, 24 GB RAM
Docker: 10 CPUs, 2 GiB memory limit

## Task 1 — Memory investigation

| Orders | Table size | Elapsed time | User time | System time | Peak memory | Result |
|---|---|---|---|---|---|---|
| 1,000,000 | 106 MiB | 1.15 s | 1.87 s | 0.05 s | 508512 KB | OK |
| 2,000,000 | 211 MiB | 2.16 s | 2.87 s | 0.07 s | 853528 KB | OK |
| 4,000,000 | 423 MiB | 3.99 s | 4.63 s | 0.14 s | 1568428 KB | OK |
| 8,400,000 | 887 MiB | Not recorded | Not recorded | Not recorded | Exceeded 2 GiB limit | OOM killed |

### Observations

Memory usage increases approximately linearly with the number of orders.

The full dataset fails because the Python process requires more memory than the Docker container's 2 GiB limit.

The memory.events file showed oom=1 and oom_kill=1 after the full pipeline run.

### Task 1 — After optimization

The report was optimized to process orders in chunks of 1,000,000 instead of loading the entire dataset into memory.

| Orders | Elapsed | User | System | Peak memory | Result |
|---|---|---|---|---|---|
| 8,400,000 | 3.28 s | 3.88 s | 0.12 s | 396124 KB | OK |

The optimized report completed successfully within the Docker container's 2 GiB memory limit.

## Task 2 — Extracting data

### Problem
The original extracts.sh used an incorrect relative path to the input CSV file. As a result, it generated six empty regional files but still printed "extracts: done".

### Fix
The corrected script uses the DATA variable with an absolute path, removes hidden error messages, and uses set -euo pipefail to detect failures.

### My measurements after the fix

| Elapsed time | User time | System time | Peak memory | Result |
|---|---|---|---|---|
| 2.02 s | 2.80 s | 0.50 s | 8060 KB | OK |

### Output verification

| Region | Rows |
|---|---|
| Benelux | 1,006,912 |
| DACH | 1,846,894 |
| France | 1,345,118 |
| Iberia | 2,183,057 |
| Italy | 1,178,032 |
| Nordics | 839,987 |
| Total | 8,400,000 |

### Conclusion
The corrected extracts.sh completed successfully and generated all six regional files. The files contain a total of 8,400,000 orders, confirming that the extraction works correctly.


## Task 3 — Auditing

### Problem
The original audit.py opened and closed the output file for every order, causing too many system calls and making the program slow.

### Fix
The optimized script opens the output file only once and writes all orders using Python's buffering.

### My measurements after optimization

| Elapsed time | User time | System time | Peak memory | Result |
|---|---|---|---|---|
| 9.71 s | 10.04 s | 0.20 s | 643100 KB | OK |

### Output verification
The generated audit_2025.csv contains 8,400,000 lines.

### Conclusion
The optimized audit.py successfully processed all 8,400,000 orders. Opening the file only once reduces system calls and improves performance.

