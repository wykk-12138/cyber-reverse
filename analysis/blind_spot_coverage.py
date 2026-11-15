"""Bound how much `real gap` understates: coverage for every type `--per-file` cannot locate (R584)

R583 showed `bind_diff --per-file` locates 150 of 174 contract types and silently skips the rest, so its
`real gap: 0` says nothing about 24 types. `Models.Notification.Timestamp` is a real gap that hides exactly there.

This splits the 24:

  * already counted  — `bind_diff --type-presence` lists them as ABSENT, so their members are covered by the
                       类型缺失 metric and are not a new finding.
  * blind spots      — present per type-presence, but `--per-file` cannot locate a body. **These are the ones whose
                       member gaps nobody has counted.**

and then measures member coverage for each blind spot, using the body extraction that includes positional record
parameters (the fix from R582).

Coverage is a name count over the contract's bound members. `SAME` means every bound name appears somewhere in the
declaration; `partial`/`DIFFERENT` are candidates for the gap table. Read-only.
"""

import glob
import io
import json
import os
import re
import subprocess

REPO = r"D:\projects\cyber-reverse\replica"
PY = r"C:\Python312\python.exe"
BIND = os.path.join(REPO, "docs", "xaml_bindings.json")

CLASS_BRACE = re.compile(r"\bclass\s+(\w+)\s*(?::[^{]*)?\{")
ANY_DECL = re.compile(r"\b(?:class|interface|record|struct|enum)\s+(\w+)")
NAMESPACE = re.compile(r"^\s*namespace\s+([\w.]+)", re.M)


def declarations():
    """simple name -> list of (namespace, declaration text incl. positional params)."""
    out = {}
    for path in glob.glob(os.path.join(REPO, "src", "**", "*.cs"), recursive=True):
        text = io.open(path, encoding="utf-8", errors="replace").read()
        m = NAMESPACE.search(text)
        ns = m.group(1) if m else ""
        for d in ANY_DECL.finditer(text):
            start = d.start()
            brace = text.find("{", d.end())
            semi = text.find(";", d.end())
            if brace >= 0 and (semi < 0 or brace < semi):
                depth, i = 0, brace
                while i < len(text):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    i += 1
                body = text[start:i + 1]
            elif semi >= 0:
                body = text[start:semi + 1]
            else:
                body = text[start:start + 400]
            out.setdefault(d.group(1), []).append((ns, body))
    return out


def absent_types():
    res = subprocess.run([PY, "tools/bind_diff.py", "--type-presence"], cwd=REPO,
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {m.group(1) for m in re.finditer(r"\s+ABSENT\s+(\S+)", res.stdout)}


def main():
    binds = json.load(io.open(BIND, encoding="utf-8"))
    decls = declarations()
    absent = absent_types()

    unlocatable = []
    for full in sorted(binds):
        simple = full.split(".")[-1].split("`")[0]
        if not CLASS_BRACE.search(" ".join(b for _ns, b in decls.get(simple, []))):
            if not any(re.search(r"\bclass\s+" + re.escape(simple), b) for _ns, b in decls.get(simple, [])):
                unlocatable.append(full)

    counted = [f for f in unlocatable if f in absent]
    blind = [f for f in unlocatable if f not in absent]

    print("types --per-file cannot locate : %d" % len(unlocatable))
    print("  already counted (ABSENT)     : %d" % len(counted))
    print("  BLIND SPOTS                  : %d" % len(blind))
    print()

    print("%-46s %-8s %-6s %s" % ("blind-spot type", "members", "found", "verdict"))
    print("-" * 108)

    gaps, ok, unclear = [], [], []
    for full in blind:
        members = list(binds.get(full) or [])
        simple = full.split(".")[-1].split("`")[0]
        cands = decls.get(simple) or []
        if not cands:
            print("%-46s %-8d %-6s %s" % (full, len(members), "?", "no declaration at all"))
            unclear.append(full)
            continue
        text = "\n".join(b for _ns, b in cands)
        found = [m for m in members if re.search(r"\b" + re.escape(m) + r"\b", text)]
        missing = [m for m in members if m not in found]
        if not missing:
            verdict = "SAME (all bound names present)"
            ok.append(full)
        elif not found:
            verdict = "GAP? none present: " + ", ".join(members[:5])
            gaps.append(full)
        else:
            verdict = "PARTIAL missing: " + ", ".join(missing[:5])
            gaps.append(full)
        print("%-46s %-8d %-6d %s" % (full, len(members), len(found), verdict[:64]))

    print()
    print("all bound names present : %d" % len(ok))
    print("gap candidates          : %d" % len(gaps))
    print("no declaration          : %d" % len(unclear))
    if gaps:
        print()
        print("=== candidates to add to the gap table ===")
        for g in gaps:
            print("  " + g)


if __name__ == "__main__":
    main()
