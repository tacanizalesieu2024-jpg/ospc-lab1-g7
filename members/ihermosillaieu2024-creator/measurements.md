# Lab 1 — Individual Measurements

**Student:** Ivan Hermosilla
**GitHub:** ihermosillaieu2024-creator
**Laptop:** Apple MacBook Air M1 (2020)
**Container:** 8 CPUs, 2 GiB memory limit

## Task 1 — Memory Usage of report.py

| Orders | Table Size (MiB) | Elapsed (s) | User (s) | System (s) | Peak Memory (KB) |
|---|---|---|---|---|---|
| 1,000,000 | 106 | 3.15 | 3.23 | 0.31 | 515184 |
| 2,000,000 | 211 | 3.64 | 3.86 | 0.38 | 858736 |
| 4,000,000 | 423 | 7.63 | 7.12 | 0.74 | 1565396 |

### Observations

Memory consumption increases as the number of orders grows. The process uses substantially more memory than the reported table size.

For 4 million orders, the table occupies 423 MiB, but peak process memory is approximately 1.49 GiB.

Extrapolating the observed trend suggests that processing all 8.4 million orders could require approximately 3 GiB of memory, exceeding the container's 2 GiB limit.

These measurements were collected on my own laptop using /usr/bin/time.

## Task 1 — Full Dataset and OOM Investigation

The full pipeline attempted to process 8,400,000 orders (887 MiB reported table size).

During the report step, the Python process was killed.

### Cgroup memory events

| Event | Before | After |
|---|---:|---:|
| max | 114 | 4139 |
| oom | 0 | 1 |
| oom_kill | 0 | 1 |

### Conclusion

The increase in oom_kill from 0 to 1 confirms that the Linux kernel terminated a process due to the container's memory limit.

The container has a 2 GiB memory limit, while the full dataset requires more memory than is available.

The complete pipeline was later interrupted manually with Ctrl+C during segments.py, so its elapsed time of 138.10 seconds is not a successful full-run benchmark.
