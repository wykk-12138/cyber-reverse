"""Loader executed *inside* IDA: run one chunk of the level-2 fingerprint dump.

Kept as its own file for three reasons:

1. The `py_eval` code string stays a single `exec(...)` expression with no backslashes — PowerShell here-strings eat
   backslashes (AGENTS.md §2.5; R569 burned me on exactly that).
2. `py_eval` evaluates one expression, so the multi-statement work lives here.
3. The chunk bounds come from `_chunk.txt` rather than the command line, so the caller can loop without rebuilding
   an escaped code string each time.

Both `open()` calls carry `encoding="utf-8"`: IDA's Python defaults to the system GBK codec and these files contain
Chinese, which killed the first attempt with `UnicodeDecodeError: 'gbk' codec can't decode byte 0x94`.
Paths use forward slashes, which Windows accepts.
"""

exec(open("D:/projects/cyber-reverse/analysis/dump_function_fingerprints.py", encoding="utf-8").read())

_bounds = open("D:/projects/cyber-reverse/analysis/_chunk.txt", encoding="utf-8").read().strip().split(",")
main("orig", int(_bounds[0]), int(_bounds[1]))
