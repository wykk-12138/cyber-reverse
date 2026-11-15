"""Find bound members the replica implements under a slightly different name (R523).

After R521/R522 took the "lift a local" batch to zero, what is left in the `?` bucket splits in two:
not implemented at all, and implemented under a neighbouring name (`Save` vs `SaveCore`, `Cancel` vs
`CancelCore`, `_proxy` vs `Proxy`). The second kind is a rename away, and a rename is safe; inventing is not.

For every member the shape audit reports as `?`, search the declaring class body for identifiers that contain
the bound name with a known affix:

    <Member>Core    Core<Member>     <Member>Value   <Member>Command
    On<Member>      _<member>        m_<member>      <Member>Async

A hit means "the code is there, only the name is not". Prefix/suffix matching is deliberate: it cannot invent
anything, because the base identifier must already exist in the class.
"""

import io
import os
import re
import subprocess
import sys

REPLICA = r"D:\projects\cyber-reverse\replica"
SRC = os.path.join(REPLICA, "src")

ROW = re.compile(r"^\s{2,}(\w+)\s+(\w+)\s+evidence=(\S+)\s+replica=(\S+)")

AFFIX_PATTERNS = [
    "%sCore", "Core%s", "%sValue", "%sCommand", "On%s", "%sAsync", "%sImpl", "%sInternal",
]
FIELD_PATTERNS = ["_%s", "m_%s", "_%sValue", "_%sCore"]


def audit_missing():
    out = subprocess.run([sys.executable, os.path.join(REPLICA, "tools", "shape_audit.py")],
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         cwd=REPLICA).stdout
    return [(m.group(1), m.group(2)) for m in (ROW.match(l) for l in out.splitlines())
            if m and m.group(4) == "?"]


def class_body(name):
    for dirpath, _, files in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in files:
            if not fn.endswith(".cs"):
                continue
            path = os.path.join(dirpath, fn)
            text = io.open(path, encoding="utf-8", errors="replace").read()
            m = re.search(r"\bclass\s+" + re.escape(name) + r"\b", text)
            if not m:
                continue
            brace = text.find("{", m.end())
            if brace < 0:
                continue
            depth, i = 0, brace
            while i < len(text):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            return text[brace:i]
    return None


def main():
    missing = audit_missing()
    by_class = {}
    for cls, member in missing:
        by_class.setdefault(cls, []).append(member)

    hits = {}
    for cls, members in by_class.items():
        body = class_body(cls)
        if body is None:
            continue
        declared = set(re.findall(r"\b(\w+)\s*(?:\(|\{|=|;)", body))
        found = []
        for member in members:
            cands = []
            for pat in AFFIX_PATTERNS:
                cand = pat % member
                if cand in declared and cand != member:
                    cands.append(cand)
            for pat in FIELD_PATTERNS:
                cand = pat % (member[0].lower() + member[1:])
                if cand in declared:
                    cands.append(cand)
            if cands:
                found.append((member, cands))
        if found:
            hits[cls] = found

    print("`?` members: %d across %d classes" % (len(missing), len(by_class)))
    print("classes where a neighbouring identifier already carries the meaning: %d" % len(hits))
    total = 0
    for cls, found in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        print("  %-32s %d" % (cls, len(found)))
        for member, cands in found:
            print("      %-22s <- %s" % (member, ", ".join(cands)))
            total += 1
    print("\ntotal rename candidates (no invention needed): %d" % total)


if __name__ == "__main__":
    main()
