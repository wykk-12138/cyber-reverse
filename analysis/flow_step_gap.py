"""Compare every flow in StoreFlowSteps against the replica flow that claims it. (R844)

R843 did Nike by hand and found the interesting result: the image's sixteen Nike steps intersect the replica's seventeen
overrides in only two names, because the replica merges ten independently-failing checkout stages into three. This runs
the same comparison for the other eight flows so the table exists once, mechanically, rather than one flow per round.

Reading only. No product code is touched.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"
FLOWS = os.path.join(ROOT, "replica", "src", "Cybersole.Stores", "Flows")
STEPS = os.path.join(FLOWS, "StoreFlowSteps.cs")

# flow id in StoreFlowSteps -> the replica source file whose overrides implement it
OWNER = {
    "nike": ["NikeFlow.cs"],
    "popmart": ["PopMartFlow.cs"],
    "johnlewis": ["JohnLewisFlow.cs", "MagentoFlow.cs"],
    "demandware-classic": ["DemandwareFlow.cs"],
    "demandware-dual": ["DemandwareFlow.cs"],
    "collectplus-app": ["DemandwareFlow.cs", "RetailFlows.cs"],
    "structure-token-multi": ["RetailFlows.cs", "StoreFlow.cs"],
    "structure-token-single": ["RetailFlows.cs", "StoreFlow.cs"],
}

text = io.open(STEPS, encoding="utf-8").read()
# split on the "public static readonly Flow X = new(" declarations
parts = re.split(r"public static readonly Flow (\w+) = new\(\"([^\"]+)\",", text)
flows = []
for i in range(1, len(parts), 3):
    var, fid, body = parts[i], parts[i + 1], parts[i + 2]
    if "new Step(" not in body:
        continue
    steps = [(n, int(o)) for n, o in re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', body)]
    if steps:
        flows.append((var, fid, steps))

print("  flows with step tables: %d" % len(flows))
print()

cache = {}
def overrides(files):
    names = set()
    for f in files:
        p = os.path.join(FLOWS, f)
        if not os.path.exists(p):
            continue
        t = cache.setdefault(f, io.open(p, encoding="utf-8", errors="replace").read())
        names |= set(re.findall(r"public override (?:async )?Task<StepOutcome> (\w+?)Async\(", t))
    return names

total_steps = 0
total_hit = 0
rows = []
for var, fid, steps in flows:
    own = overrides(OWNER.get(fid, []))
    hit = [n for n, _ in steps if n in own]
    miss = [n for n, _ in steps if n not in own]
    total_steps += len(steps)
    total_hit += len(hit)
    rows.append((fid, len(steps), own and len(own) or 0, len(hit), len(miss), miss))
    print("  %-24s steps=%-3d replica_overrides=%-3d same-name=%-3d no-override=%d"
          % (fid, len(steps), len(own), len(hit), len(miss)))
    if miss:
        print("      missing by name: %s" % ", ".join(miss[:14]))
    print()

print("  TOTAL steps %d · same-name %d (%.1f%%) · no same-name %d"
      % (total_steps, total_hit, 100.0 * total_hit / total_steps, total_steps - total_hit))
