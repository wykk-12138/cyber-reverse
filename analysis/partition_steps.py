"""Partition the 108 non-matching image step names by whether StoreFlow declares them. (R845)

R844 produced 108 image step names with no same-named override in the replica flow, and listed three possible causes:
merged into a coarser step, already in the base class, or genuinely missing. The cheap cut is the middle one, and it is
mechanical: StoreFlow declares 165 steps, so a name that appears there is implemented by the base and simply not
overridden. Only names absent from both the flow and the base need a behavioural judgement.

Reading only. No product code is touched.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"
FLOWS = os.path.join(ROOT, "replica", "src", "Cybersole.Stores", "Flows")
STEPS = os.path.join(FLOWS, "StoreFlowSteps.cs")
BASE = os.path.join(FLOWS, "StoreFlow.cs")

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

base_text = io.open(BASE, encoding="utf-8", errors="replace").read()
declared = set(re.findall(r"public virtual (?:async )?Task<StepOutcome> (\w+?)Async\(", base_text))
print("  StoreFlow declares %d virtual steps" % len(declared))

text = io.open(STEPS, encoding="utf-8").read()
parts = re.split(r'public static readonly Flow (\w+) = new\("([^"]+)",', text)
flows = []
for i in range(1, len(parts), 3):
    fid, body = parts[i + 1], parts[i + 2]
    steps = [n for n, _ in re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', body)]
    if steps:
        flows.append((fid, steps))

def overrides(files):
    names = set()
    for f in files:
        p = os.path.join(FLOWS, f)
        if os.path.exists(p):
            names |= set(re.findall(r"public override (?:async )?Task<StepOutcome> (\w+?)Async\(",
                                    io.open(p, encoding="utf-8", errors="replace").read()))
    return names

in_base = []
not_in_base = []
for fid, steps in flows:
    own = overrides(OWNER.get(fid, []))
    for n in steps:
        if n in own:
            continue
        (in_base if n in declared else not_in_base).append((fid, n))

print()
print("  unmatched by name: %d" % (len(in_base) + len(not_in_base)))
print("  ...of which StoreFlow declares the step: %d  -> base implementation, no override" % len(in_base))
print("  ...and StoreFlow does not:                %d  -> needs a behavioural verdict" % len(not_in_base))
print()
print("  --- declared by StoreFlow, merely not overridden ---")
seen = set()
for fid, n in in_base:
    if n in seen:
        continue
    seen.add(n)
    print("    %-26s (%s)" % (n, fid))
print()
print("  --- not in the base either ---")
seen = set()
for fid, n in not_in_base:
    if n in seen:
        continue
    seen.add(n)
    print("    %-26s (%s)" % (n, fid))
print()
print("  distinct base-side: %d · distinct outside the base: %d" % (len({n for _, n in in_base}),
                                                                  len({n for _, n in not_in_base})))
