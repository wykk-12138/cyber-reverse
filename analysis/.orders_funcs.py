"""R1140: from the orders URL literal to the functions that issue it.

Runs with the local client (analysis/ida.py) for xrefs, then maps each site with site_to_func-style
.pdata lookup through the plug-in, so the result is recomputable from the IDB alone.
"""
import json
import subprocess
import sys

CHARS = 0x14705D7CC
OBJ = CHARS - 12
print("chars=%#x obj=%#x" % (CHARS, OBJ))

IDA = r"python"
SCRIPT = r"D:\projects\cyber-reverse\analysis\ida.py"


def run(args):
    p = subprocess.run([IDA, SCRIPT] + args, capture_output=True, text=True, timeout=600)
    return p.stdout


out = run(["xrefs", hex(OBJ)])
sys.stdout.write(out[:2000])
print()
try:
    data = json.JSONDecoder().raw_decode(out)[0]
except Exception as exc:  # noqa: BLE001
    print("parse failed:", exc)
    raise SystemExit(0)

sites = []
def walk(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("addr", "from", "site") and isinstance(v, str) and v.startswith("0x"):
                sites.append(v)
            walk(v)
    elif isinstance(node, list):
        for v in node:
            walk(v)

walk(data)
uniq = sorted(set(sites))
print("sites:", uniq)
for s in uniq:
    print("---- site", s)
    sys.stdout.write(run(["py", "import ida_funcs; print(hex(ida_funcs.get_func(0x%s).start_ea))" % s[2:]])[:300])
