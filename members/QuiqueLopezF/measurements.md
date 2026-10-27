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


## Task 4 - Segmenting the Orders
Execution time and memory (current version of segments.py):
29.08 s elapsed, 29.62 s user, 0.06 s system, 750608 KB peak memory

### cProfile results (100,000 orders)
segments: done
         3646598 function calls (3634486 primitive calls) in 1.081 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   100000    0.266    0.000    0.511    0.000 _strptime.py:516(_strptime)
   200012    0.095    0.000    0.095    0.000 array.py:818(__iter__)
        1    0.073    0.073    1.081    1.081 segments.py:1(<module>)
   100000    0.040    0.000    0.552    0.000 _strptime.py:812(_strptime_datetime_datetime)
   408763    0.037    0.000    0.037    0.000 {method 'get' of 'dict' objects}
   100000    0.033    0.000    0.585    0.000 {built-in method strptime}
   100000    0.031    0.000    0.616    0.000 segments.py:15(segment)
   100004    0.027    0.000    0.043    0.000 locale.py:386(normalize)
        1    0.025    0.025    0.027    0.027 c_parser_wrapper.py:203(read)
   100004    0.024    0.000    0.096    0.000 locale.py:587(getlocale)
      442    0.024    0.000    0.024    0.000 {built-in method marshal.loads}
   100461    0.022    0.000    0.022    0.000 {method 'match' of 're.Pattern' objects}
   100138    0.021    0.000    0.036    0.000 __init__.py:453(_make)
339394/338782    0.021    0.000    0.021    0.000 {built-in method builtins.len}
   100000    0.017    0.000    0.017    0.000 {method 'groupdict' of 're.Match' objects}
   200003    0.016    0.000    0.016    0.000 {method 'toordinal' of 'datetime.date' objects}
   100004    0.016    0.000    0.059    0.000 locale.py:469(_parse_localename)
   100004    0.014    0.000    0.110    0.000 _strptime.py:29(_getlang)
    68/37    0.014    0.000    0.047    0.001 {built-in method _imp.exec_dynamic}
