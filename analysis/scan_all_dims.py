"""One table over every `?` member with every dimension that has bitten us (R535).

Each earlier round tightened one dimension and found one more batch:

    R527  label equals the bound name
    R531  label starts with it            (found `Add Size(s)`, `Add Preset`)
    R534  … and the button need not be a local (found six on two Account pages)

Rather than tightening another single rule, this walks all of them at once and prints, for every `?` member:

    how the action appears in the class   Button / SaveButton / DeleteButton / inline new Button / none
    the label it carries                  (and whether it starts with the bound name)
    whether anything names it             `var x =` / assigned to a field / nothing
    where it sits                         statement position or inside an initialiser/argument list

A row whose `appears` is not `none` is mechanically bindable. A row that is `none` needs UI that does not exist.

Read-only.
"""

import io
import os
import re
import subprocess
import sys

REPLICA = r"D:\projects\cyber-reverse\replica"
SRC = os.path.join(REPLICA, "src")

ROW = re.compile(r"^\s{2,}(\w+)\s+(\w+)\s+evidence=(\S+)\s+replica=(\S+)")
HELPERS = ["Button", "SaveButton", "DeleteButton", "Choice", "Check", "Text", "Combo", "Number"]


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


def classify(body, member):
    """Return (appears, label, named, place)."""
    # 1) helper call whose label starts with the member
    for helper in HELPERS:
        for m in re.finditer(r"\b" + helper + r"\(\s*\"([^\"]+)\"", body):
            label = m.group(1)
            if label == member or (label.startswith(member) and not label[len(member):len(member) + 1].isalnum()):
                before = body[max(0, m.start() - 40):m.start()]
                named = re.search(r"var\s+(\w+)\s*=\s*$", before) is not None or "= UiKit." in before
                return (helper, label, named, "statement-or-inline")
    # 2) inline `new Button { … Content = "<member>" … }`
    for m in re.finditer(r"Content\s*=\s*\"([^\"]+)\"", body):
        label = m.group(1)
        if label == member or (label.startswith(member) and not label[len(member):len(member) + 1].isalnum()):
            before = body[max(0, m.start() - 200):m.start()]
            named = "var " in before and "= new Button" in before
            return ("new Button", label, named, "initialiser")
    return ("none", "", False, "")


def main():
    missing = audit_missing()
    by_class = {}
    for cls, member in missing:
        by_class.setdefault(cls, []).append(member)

    bindable, blocked = [], []
    for cls, members in sorted(by_class.items()):
        body = class_body(cls)
        if body is None:
            continue
        for member in members:
            appears, label, named, place = classify(body, member)
            (bindable if appears != "none" else blocked).append((cls, member, appears, label, named, place))

    print("`?` members: %d" % len(missing))
    print("bindable (the action already exists): %d" % len(bindable))
    for cls, member, appears, label, named, place in bindable:
        print("  %-28s %-22s %s(\"%s\")  named=%s  %s" % (cls, member, appears, label, named, place))
    print()
    print("no action found (needs UI that is not there): %d" % len(blocked))
    for cls, member, _a, _l, _n, _p in blocked:
        print("  %-28s %s" % (cls, member))


if __name__ == "__main__":
    main()
