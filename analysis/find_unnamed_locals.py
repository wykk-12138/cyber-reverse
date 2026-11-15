"""Find bound members the replica already builds in a constructor but never names (R521).

R520 found that `PayPalAccountCreatorView` was reported as "missing 6 members" while its dialog was actually
complete — the fields were constructor locals (`var password = UiKit.Text(...)`), so no binding could reach them.
That is a repeatable shape, so this looks for it across the whole tree instead of guessing which dialog is next.

For every member the shape audit reports as `?` (replica has no such member), look inside the declaring class's
constructor for a local whose name matches case-insensitively, or a local assigned from a `UiKit.Text` / `UiKit.Check`
/ `UiKit.Combo` call whose name or watermark hints at the member. A hit means "lift, don't invent".

Output is grouped by class so a whole dialog can be fixed in one pass.
"""

import io
import os
import re
import subprocess
import sys

REPLICA = r"D:\projects\cyber-reverse\replica"
SRC = os.path.join(REPLICA, "src")

ROW = re.compile(r"^\s{2,}(\w+)\s+(\w+)\s+evidence=(\S+)\s+replica=(\S+)")


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


def locals_in(body):
    """Local variable names declared in the body (constructor and helpers both count)."""
    return {m.group(1) for m in re.finditer(r"\bvar\s+(\w+)\s*=", body)} | \
           {m.group(2) for m in re.finditer(r"\b(\w[\w<>,\[\]\?\.]*)\s+(\w+)\s*=\s*", body)}


def main():
    missing = audit_missing()
    by_class = {}
    for cls, member in missing:
        by_class.setdefault(cls, []).append(member)

    liftable = {}
    for cls, members in by_class.items():
        body = class_body(cls)
        if body is None:
            continue
        names = locals_in(body)
        lower = {n.lower(): n for n in names}
        hits = []
        for member in members:
            if member.lower() in lower:
                hits.append((member, lower[member.lower()], "same name"))
        if hits:
            liftable[cls] = hits

    print("classes reported with `?` members: %d   (members: %d)" % (len(by_class), len(missing)))
    print("classes where a constructor local already carries the name: %d" % len(liftable))
    total = 0
    for cls, hits in sorted(liftable.items(), key=lambda kv: -len(kv[1])):
        print("  %-30s %d" % (cls, len(hits)))
        for member, local, why in hits:
            print("      %-24s <- local `%s`  (%s)" % (member, local, why))
            total += 1
    print("\ntotal liftable without inventing anything: %d" % total)


if __name__ == "__main__":
    main()
