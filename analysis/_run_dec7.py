"""Loader executed *inside* IDA: decompile the seven pairs' original side (R574).

Single `exec(...)` expression for `py_eval`; `encoding="utf-8"` because IDA's Python defaults to GBK and the script
carries Chinese-free text but reads UTF-8 anyway; forward slashes because the shell eats backslashes
(AGENTS.md §2.5).
"""

exec(open("D:/projects/cyber-reverse/analysis/dump_seven_decompilations.py", encoding="utf-8").read())
main()
