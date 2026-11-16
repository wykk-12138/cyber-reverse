"""Re-check the five zero-evidence modules with IDA, not the pool. (R815)

R813 concluded five modules have no image evidence by searching analysis/pe_strings.txt. That pool turns out to be
incomplete: NIKE-GS is in the image at 0x146e11414 and absent from the pool, so "not in the pool" cannot stand for
"not in the image". IDA searches the actual database, so it is the authority here.

This is the same lesson as R806 and R807 in a new place: a tool that answers a narrower question was read as answering
the wider one.
"""

import json
import subprocess
import sys

IDA = r"D:\projects\cyber-reverse\analysis\ida.py"

CASES = {
    "bodega": ["bodega"],
    "bstn": ["bstn"],
    "nike-gs": ["NIKE-GS", "nike-gs", "NIKEGS"],
    "saintalfred": ["saintalfred", "saint alfred"],
    "shophmvs": ["shophmvs", "hmvs", "HMVS"],
    "trophyroom": ["trophyroom", "trophy room", "Trophy Room"],
}


def count(pattern):
    out = subprocess.run([sys.executable, IDA, "str", pattern], capture_output=True, text=True)
    i = out.stdout.find("{")
    if i < 0:
        return -1, []
    try:
        d, _ = json.JSONDecoder().raw_decode(out.stdout[i:])
    except Exception:
        return -1, []
    ms = d.get("matches", [])
    return len(ms), [m["string"] for m in ms[:3]]


print("  IDA string search per module:")
for mid, forms in CASES.items():
    total = 0
    examples = []
    for f in forms:
        n, ex = count(f)
        if n > 0:
            total += n
            examples.extend(ex)
    verdict = "HAS EVIDENCE" if total else "no match"
    print("    %-14s %-12s %d" % (mid, verdict, total))
    for e in examples[:2]:
        print("        %r" % e[:70])
