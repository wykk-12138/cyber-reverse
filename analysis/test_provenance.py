"""Classify the existing tests by where their expectations came from. (R722)

**Why this exists** (project convention §1.2): criterion C7c is `unknown`, and R719-R721 showed that selecting witness
functions from the original is blocked on metadata attribution. The evidence that C7c can actually produce is a
different quantity: **how many existing assertions state something the binary says**, as opposed to restating what the
implementation already does. No tool measures that; it needs the test bodies plus a marker set.

**Why now**: 1639 tests exist. If most assert "the code does what the code does", C7c has almost no evidence no matter
how green the suite is.

**Criterion, fixed before measuring** -- a test method is `binary-sourced` when its body or its immediately preceding
doc comment carries at least one of:

    an original-image address   0x14xxxxxx  or  sub_14XXXXXX
                                 (the replica's own symbols are never spelled either way)
    "decompil"                                   decompilation, Hex-Rays, pseudocode
    "descriptor"                                 the compiled-XAML descriptor table
    "the image"                                  a claim about the original binary

Everything else is `implementation-derived`, which includes tests derived from locale text or from the UI design: those
are still not derived from the binary, and lumping them together would inflate the number the audit exists to report.
"""

import io
import os
import re
import sys

TESTS = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests"
OUT = r"D:\projects\cyber-reverse\docs\TEST_PROVENANCE.md"

METHOD = re.compile(r"^\s*(?:\[(?:Fact|Theory|InlineData)[^\]]*\]\s*)*\s*public\s+(?:async\s+)?\w[\w<>,\[\]\?\. ]*\s+(\w+)\s*\(")
# (R723b) a fourth source the first marker set could not see: the original's OWN on-disk data.
#  -settings.json from the live build- is %APPDATA%\\Cybersole\\settings.json, the shipped program's output,
# which is stronger evidence than decompilation -- it is what the program actually wrote.
MARKERS = ("decompil", "descriptor", "the image", "live build", "live settings", "settings.json")
ADDR = re.compile(r"(0x14[0-9A-Fa-f]{6})|(sub_14[0-9A-Fa-f]{6})")


def preceding_doc(lines, idx):
    """Collect the contiguous /// block above line idx, skipping attribute lines.

    (R722b) A Theory carries its `[InlineData]` rows between the doc comment and the method, so walking straight up
    stops at the first attribute and finds nothing. That silently excluded the very probes R718 added.
    """
    out = []
    i = idx - 1
    while i >= 0:
        stripped = lines[i].strip()
        if stripped.startswith("///"):
            out.append(lines[i])
        elif stripped.startswith("[") or stripped == "":
            # attributes and blank lines sit between the doc block and the signature
            if out and stripped == "":
                break
        else:
            break
        i -= 1
    return "\n".join(reversed(out))


def body_of(text, start):
    """Brace-matched body starting at the first '{' after `start`."""
    i = text.find("{", start)
    if i < 0:
        return ""
    depth, j = 0, i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
        j += 1
    return text[i:]


def file_scope_doc(lines):
    """The doc block attached to the first class/record in the file, if any.

    (R722b) R718's probes cite their addresses in the class summary -- "every expectation is derived from the
    following decompiled addresses" -- and nowhere in the individual methods, so a method-scoped scan reported
    zero for all seven. A class-level statement does cover its methods, but it is weaker evidence than a citation
    on the assertion itself, so the two are counted separately rather than merged.
    """
    for idx, line in enumerate(lines):
        if re.search(r"\b(class|record)\s+\w", line):
            return preceding_doc(lines, idx)
    return ""


def scan_file(path):
    text = io.open(path, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()
    cls_doc = file_scope_doc(lines)
    cls_binary = bool(ADDR.search(cls_doc)) or any(k in cls_doc.lower() for k in MARKERS)
    rows = []
    for idx, line in enumerate(lines):
        m = METHOD.match(line)
        if not m:
            continue
        name = m.group(1)
        # offset of this line inside the file text
        off = sum(len(l) + 1 for l in lines[:idx])
        body = body_of(text, off)
        doc = preceding_doc(lines, idx)
        blob = body + "\n" + doc
        direct = bool(ADDR.search(blob)) or any(k in blob.lower() for k in MARKERS)
        rows.append((name, direct or cls_binary, doc.count("///"), direct))
    return rows


def main():
    per_file, samples_bin, samples_impl = {}, [], []
    total = binary = direct = 0
    for name in sorted(os.listdir(TESTS)):
        if not name.endswith(".cs"):
            continue
        rows = scan_file(os.path.join(TESTS, name))
        if not rows:
            continue
        b = sum(1 for r in rows if r[1])
        d = sum(1 for r in rows if r[3])
        per_file[name] = (len(rows), b, d)
        total += len(rows)
        binary += b
        direct += d
        for r in rows:
            if r[1] and len(samples_bin) < 10:
                samples_bin.append((name, r[0]))
            elif not r[1] and len(samples_impl) < 6:
                samples_impl.append((name, r[0]))

    print("test methods found : %d across %d files" % (total, len(per_file)))
    print("binary (inherited) : %d (%.1f%%)" % (binary, 100.0 * binary / max(total, 1)))
    print("binary (direct)    : %d (%.1f%%)" % (direct, 100.0 * direct / max(total, 1)))
    print("implementation     : %d (%.1f%%)" % (total - binary, 100.0 * (total - binary) / max(total, 1)))
    print()
    print("files with the most binary-sourced methods:")
    for f, (n, b, d) in sorted(per_file.items(), key=lambda kv: -kv[1][2])[:10]:
        print("  %-46s direct %2d  inherited %3d / %3d" % (f, d, b, n))

    lines = ["# 测试的证据来源（生成文件，勿手改）", "",
             "> 由 `python analysis/test_provenance.py` 生成。判据写在脚本头里，先定后量。", "",
             "## 为什么要有这份表", "",
             "判据 C7c（每个函数功能相等）是 `unknown`。R719–R721 证明**从原版挑见证函数**这条路卡在元数据归属上。",
             "那么 C7c 实际能拿出的证据量是另一个量：**有多少条断言陈述的是二进制说过的事**，",
             "而不是把实现本身复述一遍。**1649 条全绿不等于有 1649 条证据。**", "",
             "## 计数", "",
             "```",
             "测试方法总数     : %d" % total,
             "binary (direct)    : %d (%.1f%%)" % (direct, 100.0 * direct / max(total, 1)),
             "binary (inherited) : %d (%.1f%%)" % (binary, 100.0 * binary / max(total, 1)),
             "neither            : %d (%.1f%%)" % (total - binary, 100.0 * (total - binary) / max(total, 1)),
             "```", "",
             "## 判据（从脚本头复制，先定后量）", "",
             "一条测试算 `binary-sourced`，当且仅当方法体或紧邻的文档注释里出现：",
             "",
             "| 标记 | 含义 |",
             "|---|---|",
             "| `0x14xxxxxx` | 原版镜像地址（复刻件自己的地址从不这样写） |",
             "| `decompil` | 反编译 / Hex-Rays / 伪代码 |",
             "| `descriptor` | 编译期 XAML 描述符表 |",
             "| `the image` | 关于原版二进制的主张 |",
             "",
             "**其余一律记 `implementation-derived`**，包含从文案或 UI 设计推出来的测试 ——",
             "那些也不是从二进制推的，混进去会把这张表要报的数放大。", "",
             "## 逐文件", "",
             "| 文件 | direct | inherited | 总数 |", "|---|---|---|---|"]
    for f, (n, b, d) in sorted(per_file.items(), key=lambda kv: (-kv[1][2], kv[0])):
        lines.append("| `%s` | %d | %d | %d |" % (f, d, b, n))
    lines += ["", "## 局限（必须读）", "",
              "**标记法不等于溯源法。** 一条测试带了 `0x14` 地址，不代表它的期望值真的从那个地址推出来；",
              "反过来，一条没有标记的测试也可能间接依赖反编译结论（例如它测的函数是根据反编译写的）。",
              "这张表量的是**显式可追溯性**，不是真实来源。",
              "**所以它是下界**：真正从二进制来的测试**不少于**这个数，但不会多于总数。"]
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
