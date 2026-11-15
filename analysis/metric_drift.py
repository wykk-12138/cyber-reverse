"""Does any live document still hardcode a metric that METRICS.md owns? (R666)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). This reads local
documents and `docs/METRICS.md`, both already on disk.

**Why**: R665 found criterion (e) hardcoding "29 mutations" while the script ran 36. That was the same defect the
project rule forbids -- "any document must not hardcode these numbers" -- but committed by the criterion itself. The
obvious next question is whether there is a second instance. Answering it by eye is how the first one survived; this
answers it by command.

**Definition, fixed before measuring**:

  * a **metric token** is one of the six names in `METRICS.md`'s summary table, e.g. `成员形状差异`;
  * a **hit** is a line in a live document that contains both a metric token and a decimal number;
  * **LIVE** documents are the ones a reader acts on: `PARITY.md`, `SESSION_STATE.md`, `BINDING_BACKLOG.md`,
    `DELIVERY_STATUS.md`, `HANDOFF.md`, `GOAL.md` (both roots, whichever exists);
  * **HISTORICAL** documents are round records -- `VERDICT.md`, `*.archive.md`, `R4*_*.md`, `BLOCKERS.md`. A number
    in those says what was true in that round; changing it would falsify the record, so they are **not** scanned for
    "should be removed" and are reported only for context.

For each hit the script prints whether the number **equals** the current value in `METRICS.md`. Equal means the
document is a snapshot that happens to be right today -- still a latent drift, so it is reported as `MATCH (latent)`.

Read-only. Prints; writes nothing.
"""

import io
import os
import re
import sys

METRICS = r"D:\projects\cyber-reverse\docs\METRICS.md"

LIVE = [
    r"D:\projects\cyber-reverse\docs\PARITY.md",
    r"D:\projects\cyber-reverse\docs\SESSION_STATE.md",
    r"D:\projects\cyber-reverse\docs\BINDING_BACKLOG.md",
    r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md",
    r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md",
    r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md",
    r"D:\projects\cyber-reverse\docs\HANDOFF.md",
    r"D:\projects\cyber-reverse\docs\GOAL.md",
]

# labels as they appear in prose, mapped to the METRICS.md row label
TOKENS = {
    "名字级": "名字级绑定缺口 — real gap",
    "类型级": "类型级绑定缺口 — types with scope misses",
    "类型缺失": "类型缺失（type presence） — types absent from source",
    "成员形状": "成员形状差异 — total mismatches",
    "文案缺口": "文案缺口总表 — copy: zones with a missing key",
}


def current_values():
    values = {}
    for line in io.open(METRICS, encoding="utf-8").read().splitlines():
        m = re.match(r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$", line)
        if not m:
            continue
        label, val = m.group(1), m.group(2)
        num = re.search(r"\d+", val)
        if num and label in TOKENS.values():
            values[label] = int(num.group())
    return values


def main():
    values = current_values()
    if len(values) != len(TOKENS):
        print("could not parse METRICS.md summary (%d of %d)" % (len(values), len(TOKENS)))
        return 1
    print("current values:")
    for k, v in values.items():
        print("  %-52s %d" % (k, v))

    print()
    total = 0
    latent = 0
    drift = 0
    for path in LIVE:
        if not os.path.exists(path):
            continue
        name = path.replace(r"D:\projects\cyber-reverse", "").lstrip("\\")
        hits = []
        for i, line in enumerate(io.open(path, encoding="utf-8", errors="replace").read().splitlines(), 1):
            for token, label in TOKENS.items():
                if token not in line:
                    continue
                for num in re.findall(r"\b(\d+)\b", line):
                    hits.append((i, token, int(num), label, line.strip()))
                    break
        if not hits:
            continue
        print("%s" % name)
        for i, token, num, label, text in hits:
            total += 1
            if num == values[label]:
                latent += 1
                mark = "MATCH (latent)"
            else:
                drift += 1
                mark = "DIFFERS (%d vs %d)" % (num, values[label])
            print("  %4d  %-8s %-22s %s" % (i, token, mark, text[:96]))
        print()

    print("hits: %d   latent (equals today, will drift): %d   already differing: %d" % (total, latent, drift))
    print()
    print("historical documents NOT scanned for removal (their numbers describe a past round):")
    for n in ("VERDICT.md", "SESSION_STATE.archive.md", "R4*_*.md", "BLOCKERS.md"):
        print("  %s" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
