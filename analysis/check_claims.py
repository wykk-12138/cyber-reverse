"""Check criterion (d) mechanically: every claim has authority, and every non-unknown claim has a command. (R811)

docs/PARITY_CLAIMS.md states the rule itself -- "判据 d 满足 = 每条都有 authority，且非 unknown 者都有命令". This applies
that rule to the table rather than reading it, so the answer is a number and not an impression.
"""

import io

PATH = r"D:\projects\cyber-reverse\docs\PARITY_CLAIMS.md"
t = io.open(PATH, encoding="utf-8", errors="replace").read()
lines = t.splitlines()

start = None
for i, l in enumerate(lines):
    if l.strip().startswith("|") and "authority" in l and "gap_reason" in l:
        start = i + 2  # skip header and separator
        break

if start is None:
    print("  header not found")
    raise SystemExit(1)

rows = []
for l in lines[start:]:
    s = l.strip()
    if not s.startswith("|"):
        break
    cells = [c.strip() for c in s.strip("|").split("|")]
    if len(cells) >= 6:
        rows.append(cells)

print("  claim rows: %d" % len(rows))

no_auth = []
no_cmd = []
statuses = {}
for cells in rows:
    rid, claim, status, authority, command, gap = cells[:6]
    statuses[status] = statuses.get(status, 0) + 1
    if authority in ("", "-", "?", "TODO"):
        no_auth.append((rid, claim[:40]))
    unknown = status.lower() in ("unknown", "未定", "?")
    if not unknown and command in ("", "-", "?", "TODO"):
        no_cmd.append((rid, claim[:40], status, authority))

print("  status distribution:")
for k, v in sorted(statuses.items(), key=lambda x: -x[1]):
    print("    %-14s %d" % (k, v))

print()
print("  rows without an authority: %d" % len(no_auth))
for rid, claim in no_auth:
    print("    %-8s %s" % (rid, claim))

print()
print("  non-unknown rows without a command: %d" % len(no_cmd))
for rid, claim, status, authority in no_cmd:
    print("    %-8s %-10s auth=%-12s %s" % (rid, status, authority, claim))

verdict = "PASS" if not no_auth and not no_cmd else "FAIL"
print()
print("  criterion (d) by its own stated rule: %s" % verdict)
