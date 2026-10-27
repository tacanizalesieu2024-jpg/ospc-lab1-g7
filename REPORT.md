## Task 1: Generating the report… again

- Symptom: After making run_report.sh executable, the pipeline ran to the end and printed "Nightly report finished", but revenue_by_region_month.csv was missing from ~/data/out. During the report step the shell printed "Killed", and run_report.sh continued with the next steps as if nothing had happened.
- Commands and recordings you used, why you chose them, and what they showed:
  - `python3 steps/report.py` then `echo $?`: to see how the step ended. It printed "report: loaded 8,400,000 orders (887 MiB)", then "Killed", and the exit status was 137. 137 = 128 + 9, so the process was ended by signal 9 (SIGKILL) and did not stop on its own.
  - `cat /sys/fs/cgroup/memory.events`: to find who sent the signal. `oom_kill 2` (one kill in the full pipeline run, one in the standalone run) shows the kernel's out-of-memory killer ended the process because the container reached its memory limit; `max 3938` shows how often the group hit that limit.
  - `/usr/bin/time` on the first 1M, 2M and 4M orders: to see how peak memory grows with the input. Peak memory was 504,880 KB, 856,796 KB and 1,565,004 KB: linear growth of about 352,000 KB per million orders on top of a ~153,000 KB baseline. Extrapolated to 8.4M orders, the step needs about 3,118,000 KB (~3.0 GiB).
  - `python3 steps/report.py | tee /tmp/report.log`: the log file was empty; even the "loaded" line was missing.
- Cause: report.py loads all 8.4 million orders into memory at once. Although the table itself is 887 MiB, the Python objects needed to hold it take roughly three times as much, so the step needs ~3 GiB while the container's limit (memory.max) is 2 GiB. When the limit is reached, the kernel's OOM killer sends SIGKILL, which cannot be caught, so the program cannot print an error or finish. The log line was lost because, when stdout is a pipe, Python buffers its output in blocks instead of lines; SIGKILL ended the process before the buffer was flushed. run_report.sh did not check exit statuses, so it kept running.
- Fix: (to do)
- Before and after (your measurements): Before: full pipeline 160.05 s elapsed, 203.38 s user, 27.83 s system, 2,087,564 KB peak memory; report.py killed, exit status 137, no output file. After: (to do)

## Task 2: Extracting data

- Symptom: `bash steps/extracts.sh` printed "extracts: done" and exited with status 0, but all six files in ~/data/out/extracts (Benelux, DACH, France, Iberia, Italy, Nordics) were 0 bytes.
- Commands and recordings you used, why you chose them, and what they showed:
  - `cat steps/extracts.sh`: to read what the script does. It changes directory to $OUT/extracts and then reads `../data/sales_2025.csv` with grep, sending grep's errors to /dev/null.
  - The same pipeline run by hand from ~/data/out/extracts, without `2>/dev/null`: grep printed "../data/sales_2025.csv: No such file or directory" and `wc -l` counted 0 lines.
  - `echo ${PIPESTATUS[@]}`: printed `2 0 0`: grep failed with status 2 (error), while cut and wc succeeded with 0.
  - `pwd`: confirmed the working folder was /home/analyst/data/out/extracts.
- Cause: The input path is relative, and it is resolved from the folder the script moved into. From /home/analyst/data/out/extracts, `../data/sales_2025.csv` means /home/analyst/data/out/data/sales_2025.csv, which does not exist; the real file is /home/analyst/data/sales_2025.csv. grep could not open it, so cut received no input and each region file was created empty by the redirection. `2>/dev/null` hid grep's error message. The status of a pipeline is the status of its last command (cut, 0), and the status of the script is that of its last command (`echo "extracts: done"`, 0), so the failure was never reported. The script also ignores the DATA variable that the other steps use.
- Fix: (to do)
- Before and after (your measurements): Before: exit status 0, six files of 0 bytes. After: (to do)

## Task 3: Auditing

- Symptom: audit.py is slow: 82.21 s for 8.4 million orders, and about a quarter of its CPU time is spent in the kernel.
- Commands and recordings you used, why you chose them, and what they showed:
  - `/usr/bin/time` on the sample (100,000 orders) and on the full file, to separate the program's own work (user) from the kernel's (system). Sample: 1.57 s elapsed, 1.61 s user, 0.39 s system. Full: 82.21 s elapsed, 62.78 s user, 20.04 s system, 634,632 KB peak. Kernel share = 20.04 / (62.78 + 20.04) ≈ 24%, about twice that of report.py (≈ 12%).
  - `strace -c -e trace=openat,write,close` on the sample, to count the system calls that write the file: 100,686 openat, 100,001 write and 100,673 close for 100,000 orders, which is about one of each per order. The output file was 1,952,269 bytes.
- Cause: audit.py opens the output file, writes one line and closes it again for every order. Each of these is a system call, a switch into the kernel, so the program makes about 300,000 system calls for 100,000 orders, and about 25 million for the full file. The comment in the code says this ensures "each line is saved on disk", but that is false: close() only hands the data to the kernel's page cache in memory, and the kernel writes it to disk later. Only fsync() forces data to disk. The script pays the cost without gaining the safety it claims.
- Fix: (to do)
- Before and after (your measurements): Before: 82.21 s elapsed, 62.78 s user, 20.04 s system; 100,686 / 100,001 / 100,673 openat / write / close calls on the sample. Expected after: one open and one close of the output file, and about 1,952,269 / 131,072 ≈ 15 write calls with Python's 128 KiB buffer. After: (to do)

