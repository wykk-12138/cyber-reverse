"""Per flow, how many step overrides do real work and how many are placeholders.

WHY THIS EXISTS (AGENTS.md §1.2 requires the reason be stated):

Priority one of the objective is that each store actually check out. `hollow_audit.py` answers a different question -- how
many overrides each *step* has across all stores -- and its own output has been read as if it answered this one. A step
having one override somewhere says nothing about whether a given store's override does anything.

So this counts per file: each override body is classified by whether anything remains after removing the
`StepOutcome.Fail/Stop/Success(...)` returns. A body that is only such a return is a placeholder -- the shape R850 recorded
as "method with shape but no content".

What it can and cannot say:
    CAN   : count overrides whose bodies contain no work beyond returning an outcome.
    CANNOT: decide whether the work that remains is correct, nor whether a placeholder is deliberate. Some steps are
            legitimately not applicable to a store, which is why the counts are a map and not a score.

Reproduce:
    cd replica
    python tools/flow_work_audit.py
"""

import io
import os
import re
import sys

FLOWS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "Cybersole.Stores", "Flows"))

# an override's signature, then everything up to the closing brace of the method at this indent level
OVERRIDE = re.compile(
    r"public\s+override\s+(?:async\s+)?Task<StepOutcome>\s+(\w+)\s*Async\s*\([^)]*\)\s*"
    r"(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\s*=>[^;]*;)",
    re.S)

OUTCOME = re.compile(r"StepOutcome\.(?:Fail|Stop|Success)\s*\([^;]*?\)", re.S)

# R986: the first version of this classifier counted only await/Http/session use as work, and so called
# `=> OpenCheckoutAsync(c, "goat-checkout", "/checkout", ct)` a placeholder. It is not: the work is in the helper. That is
# the same mistake R824 recorded about delegation -- a call to a method of this class has no receiver, so a pattern that
# looks for one sees nothing. A body that calls any other method of the flow, or of the base class's protected helpers,
# does work.
DELEGATION = re.compile(r"\b\w*Async\s*\(|\b\w+Core\s*\(|\bOpen\w*\s*\(")


def classify(body):
    """True when the body does something other than return an outcome."""
    rest = OUTCOME.sub("", body)
    if re.search(r"\bawait\b|\bHttp\b|\bc\.Session\b|\bc\.Vars\b|\bthrow\b", rest):
        return True
    # a delegation to another step or helper counts: the work is somewhere this body does not show
    return bool(DELEGATION.search(rest))


def main():
    rows = []
    for name in sorted(os.listdir(FLOWS)):
        if not name.endswith("Flow.cs"):
            continue
        text = io.open(os.path.join(FLOWS, name), encoding="utf-8", errors="replace").read()
        pairs = OVERRIDE.findall(text)
        real = sum(1 for _n, body in pairs if classify(body))
        rows.append((name[:-len("Flow.cs")], len(pairs), real, len(pairs) - real))

    rows.sort(key=lambda r: (-r[1], r[0]))

    print("  %-16s %6s %8s %8s" % ("flow", "overrides", "real", "placeholder"))
    print("  " + "-" * 44)
    tot = [0, 0, 0]
    for name, overrides, real, placeholder in rows:
        print("  %-16s %6d %8d %8d" % (name, overrides, real, placeholder))
        for i, v in enumerate((overrides, real, placeholder)):
            tot[i] += v
    print("  " + "-" * 44)
    print("  %-16s %6d %8d %8d" % ("total", tot[0], tot[1], tot[2]))

    if tot[0]:
        print()
        print("  %.1f%% of overrides do work beyond returning an outcome." % (100.0 * tot[1] / tot[0]))
    print()
    print("  A placeholder is not automatically a gap: some steps genuinely do not apply to a store, which is why")
    print("  these are counts to read and not a score. What they do settle is that \"every step has an override\" and")
    print("  \"every store can check out\" are different claims, and only the first one had been measured.")
    return 0


if __name__ == "__main__":
    sys.exit(main())