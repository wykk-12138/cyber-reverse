"""Find every bound member whose button already exists under that exact label (R527).

R526 bound `PayPalAccountsView`'s `Edit` / `Toggle` / `Delete` by lifting the button lambdas onto `ICommand`
properties — the labels in `UiKit.Button("<label>", …)` matched the bound names one for one, and the class
already had `rows.SelectedIndex` for them to act on.

That is a general shape, so this looks for it everywhere instead of guessing which page is next. For every
member the shape audit reports as `?`, search the declaring class body for a button whose **label equals the
bound name**:

    UiKit.Button("<Member>", …)      Add("Edit", …) style helpers too

A match means the action exists and is reachable by label — binding it is a move, not an invention.

Read-only: it prints, it does not edit.
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
            return path, text[brace:i]
    return None, None


def main():
    missing = audit_missing()
    by_class = {}
    for cls, member in missing:
        by_class.setdefault(cls, []).append(member)

    found = {}
    for cls, members in by_class.items():
        path, body = class_body(cls)
        if body is None:
            continue
        hits = []
        for member in members:
            # a button whose label is exactly the bound name
            if re.search(r'Button\(\s*"' + re.escape(member) + r'"\s*,', body):
                hits.append((member, "Button(\"%s\")" % member))
                continue
            # or a helper whose label matches, e.g. Add("Edit", …)
            if re.search(r'\w+\(\s*"' + re.escape(member) + r'"\s*,', body):
                hits.append((member, 'helper("%s")' % member))
        if hits:
            found[cls] = (os.path.basename(path), hits)

    print("`?` members: %d across %d classes" % (len(missing), len(by_class)))
    print("classes where a button already carries the bound name: %d" % len(found))
    total = 0
    for cls, (fn, hits) in sorted(found.items(), key=lambda kv: -len(kv[1][1])):
        print("  %-30s %s" % (cls, fn))
        for member, how in hits:
            print("      %-22s <- %s" % (member, how))
            total += 1
    print("\ntotal liftable buttons: %d" % total)


if __name__ == "__main__":
    main()
