"""Sixth metric: persisted-data file names, original vs replica (R602).

## Why the existing five metrics do not cover this

`bind_diff` / `bind_scope` / `shape_audit` / `copy_audit_report` / `descriptor_report` all measure the **binding
surface**. None of them looks at what the application writes to disk. Objective sentence 1 asks for a functional 1:1
replica, and the persisted layout is part of that: which files exist and what they are called decides whether data,
backups and exports can be exchanged between the two builds.

## What R600 got wrong, and why the ground truth is the directory

R600 used only UTF-16 literals from the image. That produced "only in replica: `checkoutHistory.json`" — but the real
`%APPDATA%\\Cybersole` **contains** `checkoutHistory.json` (89,554 B). The original builds that filename at runtime, so
the whole string never appears as one literal in the image. A literal scan therefore **misses names that are assembled**
and, in the other direction, **picks up names that are not files at all** (URL paths, MIME type identifiers).

So the original side is now, in order of authority:

  1. **the data directory** — `%APPDATA%\\Cybersole`, listed read-only; this is what the application actually created
  2. **UTF-16 literals in the image** — a secondary signal, useful only to explain a name the directory does not have

The two are reported separately so the difference between "is a file" and "appears as a string" stays visible.

## What it still cannot say

Listing a directory shows the files that exist **now**, on this machine, for this account. A file the application
writes only in a state this install has never reached would not appear. That is recorded as a limitation, not papered
over.

Read-only on `%APPDATA%\\Cybersole`. Prints a table and writes `docs/DATAFILES.md`.
"""

import io
import os
import re

ROOT = str(__import__("pathlib").Path(__file__).resolve().parent.parent.parent)
EXE = os.path.join(ROOT, "target", "Cybersole.exe")
SRC = os.path.join(ROOT, "replica", "src")
OUT = os.path.join(ROOT, "docs", "DATAFILES.md")
DATA_DIR = os.path.join(os.environ.get("APPDATA", ""), "Cybersole")

NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{1,38}\.json")

DENY_PREFIX = ("Chromium", "crash", "Crash", "velopack", "Jint", "manifest", "public.xml", ".7z")
DENY_SUFFIX = (".template.json",)


def keep(name):
    if name.startswith(DENY_PREFIX):
        return False
    if name.endswith(DENY_SUFFIX):
        return False
    return True


def dir_names():
    """Files actually present in the live data directory (read-only)."""
    if not os.path.isdir(DATA_DIR):
        return None, []
    names = sorted(n for n in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, n)))
    return DATA_DIR, names


def literal_names():
    raw = io.open(EXE, "rb").read()
    text = raw.decode("utf-16-le", "ignore")
    return {m.group(0) for m in NAME.finditer(text) if keep(m.group(0))}


def replica_names():
    found = {}
    for dirpath, dirnames, filenames in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".cs"):
                continue
            body = io.open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()
            for m in re.finditer(r'"([A-Za-z0-9_.-]{2,40}\.json)"', body):
                found.setdefault(m.group(1), set()).add(fn)
    return found


def main():
    where, on_disk = dir_names()
    literals = literal_names()
    rep = replica_names()
    rep_data = {k for k in rep if not k.startswith("Cybersole.Locales") and k != "Fingerprint.template.json"}

    on_disk = [n for n in on_disk if n.endswith(".json")]

    print("data directory : %s" % (where or "(not present)"))
    print("  files on disk : %d  %s" % (len(on_disk), ", ".join(on_disk)))
    print("  image literals: %d" % len(literals))
    print("  replica references: %d  %s" % (len(rep_data), ", ".join(sorted(rep_data))))
    print()

    gap = sorted(set(on_disk) - rep_data)
    extra = sorted(rep_data - set(on_disk) - set(literals))
    literal_only = sorted(literals - set(on_disk))

    print("original-on-disk but not written by the replica : %d  %s" % (len(gap), ", ".join(gap) or "-"))
    print("replica-referenced, found in neither source      : %d  %s" % (len(extra), ", ".join(extra) or "-"))
    print("literal-only (a string in the image, not a file) : %d  %s" % (len(literal_only), ", ".join(literal_only) or "-"))

    lines = ["# 数据文件名对照（自动生成：`python tools/datafiles_diff.py`）", "",
             "> **事实源是数据目录本身**（`%APPDATA%\\Cybersole`，只读列举）。",
             "> 镜像里的 UTF-16 字面量只是次要信号：它**漏掉运行时拼接出来的名字**，也**会拣到不是文件的名字**（URL 路径、MIME 类型）。",
             "> R600 曾只用字面量，把 `checkoutHistory.json` 误报为「仅复刻件有」—— 那个文件真实存在（89,554 B）。", "",
             "| 项 | 值 |", "|---|---|",
             "| 数据目录 | `%s` |" % (where or "(不存在)"),
             "| 目录内 .json 文件 | %d |" % len(on_disk),
             "| 镜像 .json 字面量 | %d |" % len(literals),
             "| 复刻件写的 | %d |" % len(rep_data), "",
             "| 集合 | 名字 |", "|---|---|",
             "| 两侧都有（目录 ∩ 复刻件） | %s |" % ", ".join("`%s`" % n for n in sorted(set(on_disk) & rep_data)),
             "| **原版目录有、复刻件没写** | %s |" % (", ".join("`%s`" % n for n in gap) or "—"),
             "| 复刻件引用、两侧都查不到（可能是**读取候选**而非它写的文件） | %s |" % (", ".join("`%s`" % n for n in extra) or "—"),
             "| 只是字面量、不是文件 | %s |" % (", ".join("`%s`" % n for n in literal_only) or "—")]
    io.open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print()
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
