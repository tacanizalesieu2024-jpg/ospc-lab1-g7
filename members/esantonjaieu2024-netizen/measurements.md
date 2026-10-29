
# Elena Santonja - Lab 1 Measurements

## Task 1 - Original report.py (8.4 million orders)

Command:
`/usr/bin/time -v python3 steps/report.py`

Results:
- Orders loaded: 8,400,000
- DataFrame memory: 887 MiB
- Elapsed time: 8.26 seconds
- User time: 8.34 seconds
- System time: 0.62 seconds
- Maximum resident set size: 2,146,860 KB
- Result: Command terminated by signal 9

## Memory investigation

Commands:
`cat /sys/fs/cgroup/memory.max`
`cat /sys/fs/cgroup/memory.events`

Results:
- Container memory limit: 2,147,483,648 bytes (2 GiB)
- OOM events: 1
- OOM kills: 1

Conclusion:
The original report.py exceeded the container's 2 GiB memory limit. The operating system killed the process before it could finish.

## Fix

The team optimized report.py to reduce memory usage and avoid unnecessary copies of the dataset.


