r"""Function inventory broken down by namespace prefix, for both images.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
`func_compare.py` gives two totals (321,244 vs 187,328) and nothing else. A bare total cannot be
interpreted: most of a NativeAOT image is BCL, framework and CRT, so "the replica has 42% fewer
functions" says nothing about the application code. This splits each inventory by symbol prefix so the
*application* share becomes visible and the rest can be attributed to a named framework.

The asymmetry is the point, and it must stay visible:
    replica : 175,104 functions carry real names (PDB), so `Cybersole_*` vs `System_*` vs `Avalonia_*`
              is an observation.
    original: 311,203 of 321,244 are `sub_*` with no owning namespace, so the same split is
              **not available**. Its named remainder (10,041) is CRT/compiler symbols, not application
              code — do not read it as "the original has 10k app functions".

Reproduce:
    cd D:\projects\cyber-reverse
    python analysis/function_breakdown.py
Output: analysis/function_breakdown.md
"""

import argparse
import io
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANALYSIS = os.path.join(ROOT, "analysis")
OUT = os.path.join(ANALYSIS, "function_breakdown.md")

# Ordered: first match wins.
GROUPS = [
    ("Cybersole_（复刻件自己的代码）", re.compile(r"^Cybersole_")),
    ("Avalonia_（UI 框架）", re.compile(r"^Avalonia")),
    ("S_P_CoreLib_ / System_（BCL）", re.compile(r"^(S_P_CoreLib|System_|Microsoft_)")),
    ("Interop_ / 平台互操作", re.compile(r"^(Interop|ABI|PInvoke)")),
    ("<other named>", re.compile(r"^(?!sub_)")),
]


def load(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for line in io.open(path, encoding="utf-8", errors="replace"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3 and parts[0]:
            rows.append((int(parts[0], 16), int(parts[1]), parts[2]))
    return rows


def classify(name):
    if name.startswith("sub_"):
        return "sub_（未命名）"
    for label, pattern in GROUPS:
        if pattern.search(name):
            return label
    return "<other named>"


def breakdown(rows):
    table = {}
    for _addr, size, name in rows:
        label = classify(name)
        entry = table.setdefault(label, [0, 0])
        entry[0] += 1
        entry[1] += size
    return table


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=OUT)
    args = parser.parse_args(argv)

    original = load(os.path.join(ANALYSIS, "original_funcs.txt"))
    replica = load(os.path.join(ANALYSIS, "replica_funcs.txt"))
    if not original or not replica:
        raise SystemExit("missing inventories - run: python analysis/func_compare.py")

    ob, rb = breakdown(original), breakdown(replica)
    order = [label for label, _ in GROUPS] + ["sub_（未命名）"]
    labels = [l for l in order if l in ob or l in rb]

    lines = ["# 函数清单按前缀分解（生成文件，请勿手改）", "",
             "> 由 `python analysis/function_breakdown.py` 生成。输入是 `analysis/func_compare.py` 导出的两侧清单。",
             "> 目的：两个总数（321,244 / 187,328）不能直接解释，大部分是 BCL/框架/CRT。",
             "> **注意不对称**：复刻件侧有 175,104 个真实名字，能按命名空间分；原版侧 311,203 个是 `sub_*`，**分不了**。", ""]
    lines += ["| 分组 | 原版 函数数 | 原版 字节 | 复刻件 函数数 | 复刻件 字节 |", "|---|---|---|---|---|"]
    for label in labels:
        o = ob.get(label, [0, 0])
        r = rb.get(label, [0, 0])
        lines.append("| %s | %d | %d | %d | %d |" % (label, o[0], o[1], r[0], r[1]))
    lines += ["| **合计** | **%d** | **%d** | **%d** | **%d** |"
              % (len(original), sum(x[1] for x in original), len(replica), sum(x[1] for x in replica)), ""]

    app = rb.get("Cybersole_（复刻件自己的代码）", [0, 0])
    if app[0]:
        lines += ["## 可读的结论", "",
                  "- 复刻件镜像里，**`Cybersole_*` 命名空间下有自己的独立函数 %d 个，占 %d 字节** —— "
                  "这是“我们写的业务代码”在产物里的可见规模。" % (app[0], app[1]),
                  "- 其余 %d 个函数属于 BCL / Avalonia / CRT / 未命名，**不能算作业务代码的多少**。"
                  % (len(replica) - app[0]),
                  "- 原版侧**没有对应的数字**：它的 311,203 个函数是 `sub_*`，10,041 个有名字的是 CRT/编译器符号。"
                  "所以“函数数量对等”这一句**目前只能报差值，不能报比值**。", ""]

    io.open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("original: %d functions" % len(original))
    print("replica : %d functions" % len(replica))
    for label in labels:
        o = ob.get(label, [0, 0])
        r = rb.get(label, [0, 0])
        print("  %-34s original %7d  replica %7d" % (label, o[0], r[0]))
    print()
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
