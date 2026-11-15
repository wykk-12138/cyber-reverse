"""Run one IDAPython snippet from a file against the live IDA plugin. (R691)

Why this exists (project convention §1.2): `analysis/ida.py` already talks to the plugin, but passing a multi-line
snippet through PowerShell strips its quotes, so the snippet must travel as a file. This driver reads the file and hands
the text to the same client, which keeps the quoting intact end to end.
"""

import io
import json
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import ida  # noqa: E402


def main(argv):
    if not argv:
        print("usage: python analysis/run_idapy.py <snippet.py>")
        return 2
    code = io.open(argv[0], encoding="utf-8").read()
    ida.initialize()
    res = ida.call("py_eval", {"code": code}, timeout=1800)
    print(json.dumps(res, ensure_ascii=False, indent=2)[:8000])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
