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
