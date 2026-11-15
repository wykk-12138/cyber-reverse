"""Audit `docs/PARITY_CLAIMS.md` against the current `docs/METRICS.md`. (R692)

**Why this exists** (project convention §1.2): the IDB cannot be trusted to answer "is this number current" -- the
metrics wrapper already exists and is the single source of truth. This is a consistency check across two local files,
so no reverse-engineering tool applies.

**Why now**: the claim table's §6 self-audit says criterion (d) is satisfied because every row carries `authority`,
`command`, `gap_reason`. That is a **structural** claim and it holds. But several rows also carry **numbers**, and the
project rule is that a number lives only in `docs/METRICS.md`. R433 found eight stale figures in six files by exactly
this route; the same drift is in this table now.

**Criterion, fixed before measuring**: a claim row is INCONSISTENT when it states a value for one of the four metrics
that differs from the generated value. Those get replaced by a pointer. A `gap_reason` that a later round disproved is
listed separately and corrected with the round that disproved it.
"""

import io
import re

METRICS = r"D:\projects\cyber-reverse\docs\METRICS.md"
CLAIMS = r"D:\projects\cyber-reverse\docs\PARITY_CLAIMS.md"

# generated values, read rather than retyped
def metric(name):
    text = io.open(METRICS, encoding="utf-8").read()
    for line in text.splitlines():
        if name in line and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                return cells[1]
    return None



MARKERS = ("见 `METRICS.md`", "当时的", "R633", "R613", "R467", "R468", "一次性", "非当前值")


def annotated(text, needle):
    """True when the line containing `needle` also carries a pointer or a historical marker."""
    for line in text.splitlines():
        if needle in line and any(m in line for m in MARKERS):
            return True
    return False


def main():
    shape = metric("成员形状差异")
    copy_row = metric("文案缺口总表")
    suite = metric("完整套件")
    gap = metric("名字级绑定缺口 — real gap")
    print("current METRICS values:")
    print("  shape mismatches : %s" % shape)
    print("  copy gaps        : %s" % copy_row)
    print("  suite            : %s" % suite)
    print("  name-level gap   : %s" % gap)
    print()

    body = io.open(CLAIMS, encoding="utf-8").read()

    checks = []

    # C7b quotes a composition (175/61/29) and a total (275)
    if "275" in body and not annotated(body, "275"):
        checks.append(("C7b", "says 275 shape mismatches", "current generated value is %s" % shape))
    if "**175** 条" in body:
        checks.append(("C7b", "composition 175/61/29 hard-coded", "composition is not regenerated anywhere"))

    # C14 quotes 5 copy gaps and calls them truncated
    if "5 条缺失，全为\"池中截断\"" in body:
        checks.append(("C14", "says 5 copy gaps, all truncated", "current value is %s" % copy_row))
    if "5 条池中截断（ProfileCsv 2 / Settings 1 / Utilities 2）" in body:
        checks.append(("C14", "gap_reason still calls them truncated",
                       "R668 disproved truncation: both strings are complete in the pool"))

    # C6 / C10 / C11 quote replica function and member counts
    if "187,328" in body and not annotated(body, "187,328"):
        checks.append(("C6", "replica function count 187,328", "R613 measured 186,732 under equal options"))
    if "21/819" in body and not annotated(body, "21/819"):
        checks.append(("C10", "21/819 member coverage", "not regenerated; recompute before quoting"))
    if "111 个绑定类型名" in body and not annotated(body, "111 个绑定类型名"):
        checks.append(("C11", "111 absent type names", "current type-absence metric is a different count"))

    print("inconsistencies found: %d" % len(checks))
    for cid, what, why in checks:
        print("  %-5s %-44s -> %s" % (cid, what, why))


if __name__ == "__main__":
    main()
