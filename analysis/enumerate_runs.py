"""Enumerate every adjacent run of d__N step names in the image, to get the real flow count. (R854)

R853 found a ninth sequence outside the eight that StoreFlowSteps records, which means the denominator behind R844's
16.9 percent was never established. R112's note says each flow's steps sit in one adjacent run, so the runs themselves
are the population: a run is a group of `Name>d__N` occurrences that share one string literal and whose ordinals ascend.

This finds the runs rather than searching for flows by name, which is the point -- the eight were a selection, and a
selection is not a population.

Reading only. No product code is touched.
"""

import io
import json
import re
import subprocess
import sys

IDA = r"analysis\ida.py"
PAT = re.compile(r"<?([A-Za-z_][A-Za-z0-9_]*)>d__(\d+)")

out = subprocess.run([sys.executable, IDA, "str", ">d__", "--limit", "300"],
                     capture_output=True, text=True).stdout
i = out.find("{")
if i < 0:
    print("  no json: " + out[:200])
    sys.exit(1)
d, _ = json.JSONDecoder().raw_decode(out[i:])
matches = d.get("matches", [])
print("  strings containing >d__ (limit 300): %d" % len(matches))

runs = []
for m in matches:
    found = [(n, int(o)) for n, o in PAT.findall(m["string"])]
    if len(found) < 4:
        continue
    # a run is a maximal ascending subsequence
    current = [found[0]]
    for prev, nxt in zip(found, found[1:]):
        if nxt[1] > prev[1] and nxt[1] - prev[1] <= 3:
            current.append(nxt)
        else:
            if len(current) >= 4:
                runs.append((m["addr"], current))
            current = [nxt]
    if len(current) >= 4:
        runs.append((m["addr"], current))

print("  adjacent runs of 4+ ascending steps: %d" % len(runs))
print()
known = {
    "nike": ["StartEcomSession", "Authorize", "GetAccessToken", "FindVariant"],
    "popmart": ["StartDrawFlow", "StartDrawCheckFlow", "FindDraw"],
    "johnlewis": ["WebHandOver", "SessionHandover", "GuestCallback"],
    "demandware-classic": ["InitiateCheckout", "GenerateCSRF", "GetCheckout"],
    "demandware-dual": ["StartAppFast", "StartAppSafe", "GetSessionDw"],
    "collectplus-app": ["GetCollectPlusLocations", "SubmitCollectPlus"],
    "structure-token": ["FindProductMulti", "GetMerchantCode", "GetStructureToken"],
}
for addr, steps in sorted(runs, key=lambda r: -len(r[1])):
    names = [n for n, _ in steps]
    tag = ""
    for flow, marks in known.items():
        if any(mk in names for mk in marks):
            tag = flow
            break
    print("  %-14s %2d steps  %s%s" % (addr, len(steps), ", ".join(names[:6]),
                                       ("   <- " + tag) if tag else "   <- 未命名"))
