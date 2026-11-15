"""Which of the 34 selection-model rows already have a parameterless action in the same class? (R576)

`docs/SHAPE_GAPS.md` says 34 mismatches are "the member is a parameterised method, the binding says Property".
Moving one to `ICommand` needs a *selection model* to supply the parameter — unless the class already has a
parameterless equivalent, in which case the command can simply delegate to it and nothing is invented.

This finds those cases mechanically:

    for each row dispositioned 需要选择模型
        locate the class body
        list its public methods, with their parameter counts
        report every method whose parameter list is empty

A parameterless method of the **same name** is the jackpot: the command wraps it directly (AGENTS.md §3's
checklist). A parameterless method of a *different* name is weaker — it may be the same action under another
name, and that must be read, not assumed.

Source-text analysis only. No behaviour is claimed.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"
SRC = os.path.join(ROOT, "replica", "src")
GAPS = os.path.join(ROOT, "docs", "SHAPE_GAPS.md")

HEAD = re.compile(r"^### `(\w+)\.(\w+)`")


def load_sources():
    out = {}
    for dirpath, dirnames, filenames in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".cs"):
                p = os.path.join(dirpath, fn)
                out[p] = io.open(p, encoding="utf-8", errors="replace").read()
    return out


def class_bodies(files):
    """class name -> merged body text (a partial class may span files)."""
    bodies = {}
    for path, text in files.items():
        for m in re.finditer(r"\bclass\s+(\w+)", text):
            b = text.find("{", m.end())
            if b < 0:
                continue
            depth, i = 0, b
            while i < len(text):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            bodies.setdefault(m.group(1), []).append(text[b:i + 1])
    return {k: "\n".join(v) for k, v in bodies.items()}


PUBLIC_METHOD = re.compile(
    r"\bpublic\s+(?:static\s+|async\s+|override\s+|virtual\s+)*"
    r"[\w<>,\[\]\.\?\s]+?\s+(\w+)\s*\(([^)]*)\)")


def methods_of(body):
    out = []
    for m in PUBLIC_METHOD.finditer(body):
        name = m.group(1)
        params = m.group(2).strip()
        n = 0 if not params else len([p for p in params.split(",") if p.strip()])
        out.append((name, n))
    return out


def main():
    text = io.open(GAPS, encoding="utf-8").read()
    files = load_sources()
    bodies = class_bodies(files)

    rows = []
    for block in text.split("### ")[1:]:
        lines = block.splitlines()
        h = HEAD.match("### " + lines[0])
        if not h:
            continue
        if not any("需要选择模型" in l for l in lines):
            continue
        rows.append((h.group(1), h.group(2)))

    print("rows dispositioned 需要选择模型: %d" % len(rows))
    print()

    same_name = []
    other_name = []
    nothing = []

    for cls, member in rows:
        body = bodies.get(cls)
        if body is None:
            nothing.append((cls, member, "类体没找到"))
            continue
        ms = methods_of(body)
        zero = [(n, c) for n, c in ms if c == 0]
        exact = [n for n, c in zero if n == member]
        if exact:
            same_name.append((cls, member))
        elif zero:
            other_name.append((cls, member, sorted(set(n for n, _ in zero))[:6]))
        else:
            nothing.append((cls, member, "该类没有无参 public 方法"))

    print("== 同类里有同名无参方法（可直接包 ICommand）: %d ==" % len(same_name))
    for cls, member in same_name:
        print("   %-28s %s" % (cls, member))

    print()
    print("== 同类里有别的无参方法（可能是同一动作，要读）: %d ==" % len(other_name))
    for cls, member, names in other_name:
        print("   %-28s %-20s 现有无参: %s" % (cls, member, "、".join(names)))

    print()
    print("== 没有无参方法（真需要选择模型）: %d ==" % len(nothing))
    for cls, member, why in nothing:
        print("   %-28s %-20s %s" % (cls, member, why))


if __name__ == "__main__":
    main()
