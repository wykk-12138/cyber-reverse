"""Loader executed *inside* IDA: run one chunk of the canonical-hash dump (R573).

Same three reasons as its R572 sibling:

1. The `py_eval` code string stays a single `exec(...)` expression with no backslashes — PowerShell here-strings
   eat backslashes (AGENTS.md §2.5; R569 burned me).
2. `py_eval` evaluates one expression, so multi-statement work lives here.
3. Chunk bounds come from `_chunk.txt`, so the caller loops without rebuilding an escaped code string.

`encoding="utf-8"` on every `open()`: IDA's Python defaults to the system GBK codec and these files contain
Chinese. Forward slashes because Windows accepts them and they survive the shell.
"""

exec(open("D:/projects/cyber-reverse/analysis/dump_function_hashes.py", encoding="utf-8").read())

_bounds = open("D:/projects/cyber-reverse/analysis/_chunk.txt", encoding="utf-8").read().strip().split(",")
main("orig", int(_bounds[0]), int(_bounds[1]))
