"""Sort every absent copy key into three piles and write docs/COPY_TRIAGE.md (R544).

`analysis/copy_coverage.py` showed the pool has 1142 keys and 222 of them have no literal match in `src/`. A
count that large is not a work list — before anything can be written, the 222 have to be separated into:

    wording   the source already says it, differently   (difflib ratio >= 0.55 against some literal)
    missing   the owning class exists but this string does not
    no-home   no class by that prefix exists in the tree at all (the page is not implemented)

The third pile matters because `Solver.*`, `Update.*`, `TimeAgo.*` are whole-feature prefixes; writing their copy
without the page would be inventing a surface. The second pile is the actual to-do list.

Ownership is decided from the prefix: `Settings.Payment.*` is looked for under `Settings*`, `Creator.*` under
`*Creator*`, and so on — a heuristic, and it is labelled as one in the output.

Generated file; do not hand-edit. Read-only with respect to `src/`.
"""

import io
import os
import re
import difflib

POOL = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
SRC = r"D:\projects\cyber-reverse\replica\src"
OUT = r"D:\projects\cyber-reverse\replica\docs\COPY_TRIAGE.md"

PAT = re.compile(r'"([A-Z][\w.]*\.[\w.]+)":\s*"((?:[^"\\\n]|\\.){1,400})"')
RATIO = 0.55


def main():
    raw = io.open(POOL, encoding="utf-8", errors="replace").read()
    pairs = sorted(set(
        (m.group(1), m.group(2).replace('\\"', '"').replace('\\\\', '\\'))
        for m in PAT.finditer(raw)))

    literals = []
    class_names = set()
    for dirpath, _d, files in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in files:
            if not fn.endswith(".cs"):
                continue
            body = io.open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()
            # R544: the first literal pattern was r'"([^"\\\n]{6,400})"'. Excluding the backslash meant every
            # source string containing `\n` was never collected — including
            #     $"Are you sure you want to delete {count} accounts?\nYou cannot undo this action."
            # which is exactly the string the pool has as `Accounts.DeleteConfirm.MessageFormat`. Allow escapes,
            # then unescape so the two sides can be compared.
            for m in re.finditer(r'"((?:[^"\\\n]|\\.){6,400})"', body):
                literals.append((m.group(1).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\'), fn))
            class_names.update(re.findall(r"\b(?:class|record)\s+(\w+)", body))
    haystack = "\n".join(lit for lit, _fn in literals)

    # R544: the pool writes format templates as `{0}`, `{1}`; the source writes interpolations as `{count}`,
    # `{name}`. Comparing them literally put real copy into the "missing" pile — e.g. AccountGrid.cs already
    # contains "Are you sure you want to delete {count} accounts?\nYou cannot undo this action." and the pool
    # has the same sentence with `{0}`. Normalising every placeholder to `{0}` before comparing removes that
    # whole class of false positives.
    PLACEHOLDER = re.compile(r"\{[A-Za-z0-9_:.]*\}")

    def norm(s):
        return PLACEHOLDER.sub("{0}", s)

    normed_literals = [(norm(lit), fn) for lit, fn in literals]
    normed_haystack = "\n".join(lit for lit, _fn in normed_literals)

    def has_home(area):
        """True when some class name in the tree carries the area's name (heuristic)."""
        a = area.lower()
        return any(a in c.lower() for c in class_names)

    wording, missing, no_home = [], [], []
    for key, value in pairs:
        if value in haystack or norm(value) in normed_haystack:
            continue
        area = key.split(".")[0]
        nv = norm(value)
        best, ratio, where = None, 0.0, None
        for lit, fn in normed_literals:
            r = difflib.SequenceMatcher(None, nv.lower(), lit.lower()).ratio()
            if r > ratio:
                best, ratio, where = lit, r, fn
        if ratio >= RATIO:
            wording.append((key, value, best, ratio, where))
        elif has_home(area):
            missing.append((key, value, area))
        else:
            no_home.append((key, value, area))

    lines = ['# 文案缺口三分类（自动生成：`python analysis/copy_triage.py`）', '',
             '> 生成物，勿手改。汇总口径见 `docs/METRICS.md`（R433 裁决 1）。', '',
             '| 堆 | 条数 | 含义 |', '|---|---|---|',
             '| 措辞不同 | %d | 源码已有这句意思，字面不同（近似度 ≥ %.2f） |' % (len(wording), RATIO),
             '| 真缺失 | %d | 宿主类存在，但这句文案没写 |' % len(missing),
             '| 无宿主 | %d | 树里没有对应前缀的类 —— 整块功能未实现 |' % len(no_home),
             '| **合计** | **%d** | 全池 1142 键中无字面匹配者 |' % (len(wording) + len(missing) + len(no_home)),
             '',
             '> **归属判定是启发式的**：`area` 前缀以子串形式在某个类名里出现即算"有宿主"。'
             '它会把 `Creator` 认到 `TaskCreatorView` 头上，也可能认错。**"真缺失"这一堆在动手前要逐条确认。**',
             '',
             '## 措辞不同（%d）' % len(wording), '',
             '| 键 | 原文 | 源码里最接近的 | 近似度 | 文件 |', '|---|---|---|---|---|']
    for key, value, best, ratio, where in sorted(wording, key=lambda x: -x[3])[:80]:
        lines.append('| `%s` | %s | %s | %.2f | `%s` |'
                     % (key, value[:80].replace('|', '\\|'), best[:80].replace('|', '\\|'), ratio, where))

    lines += ['', '## 真缺失（%d）' % len(missing), '',
              '| 键 | 原文 | 归属（启发式） |', '|---|---|---|']
    for key, value, area in missing:
        lines.append('| `%s` | %s | `%s` |' % (key, value[:110].replace('|', '\\|'), area))

    lines += ['', '## 无宿主（%d）' % len(no_home), '',
              '| 键 | 原文 | 前缀 |', '|---|---|---|']
    for key, value, area in no_home:
        lines.append('| `%s` | %s | `%s` |' % (key, value[:110].replace('|', '\\|'), area))

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    print("wrote COPY_TRIAGE.md")
    print("  wording  %3d" % len(wording))
    print("  missing  %3d" % len(missing))
    print("  no-home  %3d" % len(no_home))
    print("  total    %3d" % (len(wording) + len(missing) + len(no_home)))


if __name__ == "__main__":
    main()
