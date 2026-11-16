"""Split the 73% "implementation-derived" tests: how many assert text that came from the original's pool? (R723)

R722 measured 83 of 1553 test methods (5.3%) carrying an explicit binary citation. That left 1134 with none.

But "no address marker" is not the same as "no binary source". A test asserting that a caption equals "Unknown country"
is derived from the image's string pool: the text exists there verbatim, and it did not come from the implementation.
Grouping those with tests that merely restate a computed value would understate C7c's evidence and, worse, would
misdescribe where the expectations came from.

**Criterion, fixed before measuring** -- among the methods R722 classified as having no direct citation:

    locale-derived     the body mentions `Copy`, `Text(`, or compares against a literal that appears
                       in Cybersole.Locales.en.json
    unaccounted        neither

`locale-derived` is weaker than a cited address (the pool proves the text exists, not that the behaviour around it is
right) and stronger than nothing. The two are reported separately for that reason.
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import test_provenance as T

LOCALES = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Locales\Cybersole.Locales.en.json"
COPY_MARKERS = ("Copy[", "Copy.", "Text(", "// ProfileCsv.", "Locales.")


def locale_values():
    data = json.load(io.open(LOCALES, encoding="utf-8"))
    return {v for v in data.values() if isinstance(v, str) and len(v) >= 8}


def main():
    values = locale_values()
    total = binary = locale_derived = unaccounted = 0
    per_file = {}
    samples = []

    for name in sorted(os.listdir(T.TESTS)):
        if not name.endswith(".cs"):
            continue
        path = os.path.join(T.TESTS, name)
        rows = T.scan_file(path)
        if not rows:
            continue
        text = io.open(path, encoding="utf-8", errors="replace").read()
        lines = text.splitlines()
        n_loc = 0
        for idx, line in enumerate(lines):
            m = T.METHOD.match(line)
            if not m:
                continue
            off = sum(len(l) + 1 for l in lines[:idx])
            body = T.body_of(text, off)
            total += 1
            row = next((r for r in rows if r[0] == m.group(1)), None)
            if row and row[1]:
                binary += 1
                continue
            marked = any(k in body for k in COPY_MARKERS)
            quoted = False
            if not marked and values:
                for lit in re.findall(r'"([^"\\]{8,})"', body):
                    if lit in values:
                        quoted = True
                        break
            if marked or quoted:
                locale_derived += 1
                n_loc += 1
                if len(samples) < 8:
                    samples.append((name, m.group(1), "marker" if marked else "quoted"))
            else:
                unaccounted += 1
        if n_loc:
            per_file[name] = n_loc

    print("test methods          : %d" % total)
    print("  binary (cited)      : %d (%.1f%%)" % (binary, 100.0 * binary / max(total, 1)))
    print("  locale-derived      : %d (%.1f%%)" % (locale_derived, 100.0 * locale_derived / max(total, 1)))
    print("  unaccounted         : %d (%.1f%%)" % (unaccounted, 100.0 * unaccounted / max(total, 1)))
    print()
    print("files with the most locale-derived methods:")
    for f, n in sorted(per_file.items(), key=lambda kv: -kv[1])[:10]:
        print("  %-46s %3d" % (f, n))
    print()
    print("samples:")
    for f, m, how in samples:
        print("  %-42s %-38s %s" % (f, m, how))

    # append to the generated provenance document so there is one authoritative count
    doc = r"D:\projects\cyber-reverse\docs\TEST_PROVENANCE.md"
    if os.path.exists(doc):
        body = io.open(doc, encoding="utf-8").read()
        if "## 第三桶：文案溯源" not in body:
            body += "\n".join([
                "",
                "## 第三桶：文案溯源（R723 追加）",
                "",
                "「没有地址引用」不等于「没有二进制来源」。一条断言「标题等于 'Unknown country'」，",
                "那句话在原版字符串池里逐字存在 —— 它来自镜像，不是来自实现。",
                "",
                "```",
                "测试方法总数        : %d" % total,
                "  binary (cited)    : %d (%.1f%%)   R722 那两档" % (binary, 100.0 * binary / max(total, 1)),
                "  locale-derived    : %d (%.1f%%)   触到池中文案" % (locale_derived, 100.0 * locale_derived / max(total, 1)),
                "  unaccounted       : %d (%.1f%%)   两者都没有" % (unaccounted, 100.0 * unaccounted / max(total, 1)),
                "```",
                "",
                "**检测器是松的**：只要方法体里出现一段 ≥8 字符、且逐字出现在 `Cybersole.Locales.en.json` 的字符串，",
                "就记 locale-derived。所以 `TheHeadersActuallySort` 会被算进来 —— 它确实用到池中的表头文字，",
                "**但它断言的是排序，不是文案**。",
                "",
                "**所以 locale-derived 的含义是「这条测试触到了池中文字」，不是「整条期望来自池」。**",
                "它比 cited 弱，比 unaccounted 强，只能这么用。",
                ""])
            io.open(doc, "w", encoding="utf-8").write(body)
            print()
            print("appended the third bucket to %s" % doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
