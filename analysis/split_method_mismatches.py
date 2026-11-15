"""Find the `method -> property` mismatches whose replica method already takes no arguments (R517).

Why a script and not a hand list: 78 of the 140 shape mismatches are "the original binds a property, the replica
has a method". An `ICommand` is a no-argument property, so a replica method WITH parameters cannot simply be
renamed — it needs a selected-item concept first, which is a design change, not a rename. A replica method with
NO parameters can be wrapped in one line (`X = new RelayCommand(XCore)`), which is the cheap batch.

So this splits the 78 into:
  * WRAP     — replica method takes no arguments; wrapping is mechanical
  * REPARAM  — replica method takes arguments; needs a selection concept, out of scope for a batch
  * MISSING  — the method named in the audit is not found in the file at all (audit may name a nested type)

Input: the shape audit's own output, plus a scan of src/ for the class bodies.
"""

import io
import os
import re
import subprocess
import sys

REPLICA = r"D:\projects\cyber-reverse\replica"
SRC = os.path.join(REPLICA, "src")

ROW = re.compile(r"^\s{2,}(\w+)\s+(\w+)\s+evidence=(\S+)\s+replica=(\S+)")


def audit_rows():
    out = subprocess.run([sys.executable, os.path.join(REPLICA, "tools", "shape_audit.py")],
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         cwd=REPLICA).stdout
    return [m.groups() for m in (ROW.match(l) for l in out.splitlines()) if m]


def class_bodies():
    """class name -> (path, body text)."""
    bodies = {}
    for dirpath, _, files in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in files:
            if not fn.endswith(".cs"):
                continue
            path = os.path.join(dirpath, fn)
            text = io.open(path, encoding="utf-8", errors="replace").read()
            for m in re.finditer(r"\bclass\s+(\w+)\b", text):
                name = m.group(1)
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
                bodies.setdefault(name, (path, text[m.end():i]))
    return bodies


def main():
    rows = audit_rows()
    bodies = class_bodies()

    wrap, reparam, missing = [], [], []
    for cls, member, ev, rep in rows:
        if rep != "method":
            continue
        if cls not in bodies:
            missing.append((cls, member, "class not found"))
            continue
        _, body = bodies[cls]
        m = re.search(r"\bpublic\s+(?:async\s+)?(?:void|bool|Task)\s+" + re.escape(member) + r"\s*\(([^)]*)\)", body)
        if not m:
            missing.append((cls, member, "no public method of that name"))
            continue
        params = m.group(1).strip()
        if params:
            reparam.append((cls, member, params))
        else:
            wrap.append((cls, member))

    print("method-replica mismatches: %d" % (len(wrap) + len(reparam) + len(missing)))
    print("  WRAP     (no args, one-line wrap): %d" % len(wrap))
    for c, m_ in wrap:
        print("      %-26s %s" % (c, m_))
    print("  REPARAM  (needs a selection concept): %d" % len(reparam))
    for c, m_, p in reparam[:12]:
        print("      %-26s %-22s (%s)" % (c, m_, p[:40]))
    print("  MISSING  (audit names something not in the class): %d" % len(missing))
    for c, m_, why in missing[:12]:
        print("      %-26s %-22s %s" % (c, m_, why))


if __name__ == "__main__":
    main()
