"""Loader executed *inside* IDA: run one chunk of the canonical-hash dump for the REPLICA (R573).

Identical to `_run_hash_orig.py` except for the tag, which decides the output filename
(`_fp_rep_H.tsv`). Kept as a separate file rather than parameterised because `py_eval` takes a code string, and a
tag passed through the shell is one more place a quote or backslash can be eaten (AGENTS.md §2.5).
"""

exec(open("D:/projects/cyber-reverse/analysis/dump_function_hashes.py", encoding="utf-8").read())

_bounds = open("D:/projects/cyber-reverse/analysis/_chunk.txt", encoding="utf-8").read().strip().split(",")
main("rep", int(_bounds[0]), int(_bounds[1]))
