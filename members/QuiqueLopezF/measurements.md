## Task 1 - 2 million orders (fixed report.py)
1.04 s elapsed, 1.58 s user, 0.07 s system, 358444 KB peak memory
## Task 1 - 1 million orders (fixed report.py)
0.63 s elapsed, 1.19 s user, 0.05 s system, 259820 KB peak memory
## Task 1 - 4 million orders (fixed report.py)
1.93 s elapsed, 2.45 s user, 0.09 s system, 389296 KB peak memory

## Task 2 - Extracting Data

Result: extracts.sh completed successfully.
Exit status: 0
Output: Six regional CSV files were generated.

Original problem:
The script used an incorrect relative path to the input data.
Errors from grep were hidden by redirecting stderr to /dev/null.
The pipeline could finish with exit status 0 even when grep failed.

Fix already applied by the team:
The script uses the DATA variable as its input path.
It includes set -euo pipefail for error handling.
The output files are generated correctly.


## Task 3 - Auditing

### Execution time

| Measurement | 100,000 orders | 8,400,000 orders |
|---|---:|---:|
| Elapsed (s) | 0.74 | 45.54 |
| User (s) | 1.16 | 32.60 |
| System (s) | 0.18 | 13.55 |
| Peak memory (KB) | 129056 | 634980 |

### System calls (100,000 orders)

| System call | Number |
|---|---:|
| openat | 100686 |
| write | 100001 |
| close | 100673 |
| Total | 301360 |

### Observations

The program makes approximately one open, write and close call per order.
Opening and closing the output file repeatedly creates unnecessary system calls.

For the full dataset, system time was 13.55 seconds, approximately 29.4% of total CPU time (user + system).

A more efficient solution is to open the output file once and use buffered writing.

