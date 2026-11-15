"""Which of the ProfileCsv copy strings does any code actually produce? (R630)

R629 found the `Copy` table in `ProfileViews.cs` has 41 entries and zero consumers. The next question is not "who reads
the table" but "does the code say these sentences at all, by any route" — the table may be dead while the text still
appears as a literal at the place that produces it.

So this compares two sets, both taken mechanically from the same file:

  * **the table** — every `["Name"] = "value",` entry;
  * **produced text** — every string literal assigned to something that reaches the UI (`status.Text`, `RowStatus`,
    `RowError`), plus every literal used as a `UiKit` caption/button/message argument.

A table entry whose value (or its first sentence) never appears among the produced text is a sentence the replica
**never says** — which is a different and stronger statement than "the table is unused".

Limits, stated so the numbers are not over-read: this is a **text** comparison inside one file. A sentence produced by
`string.Format` from a template, or assembled by concatenation, may not match verbatim and will be reported as absent.
The list is therefore a **lower bound** on coverage and an **upper bound** on dead text.

Read-only. Writes `docs/DEAD_COPY.md`.
"""

import io
import os
import re

SRC = r"D:\projects\cyber-reverse\replica\src"
OUT = r"D:\projects\cyber-reverse\docs\DEAD_COPY.md"
TARGET = os.path.join(SRC, "Cybersole.Ui", "Views", "Profiles", "ProfileViews.cs")


def main():
    text = io.open(TARGET, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()

    # the table: ["Name"] = "value",   // Key
    table = []
    for i, l in enumerate(lines, 1):
        m = re.match(r'\s*\["([A-Za-z0-9_]+)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', l)
        if m:
            table.append((i, m.group(1), m.group(2)))

    # produced text: right-hand literals of UI assignments, and UiKit message arguments
    produced = []
    for i, l in enumerate(lines, 1):
        if re.search(r"(status\.Text|_status\.Text|RowStatus|RowError)\s*=", l) or "UiKit." in l:
            produced.append(l)
    produced_blob = "\n".join(produced)

    # R631: an entry is also produced when the code looks it up by name -- `Text("ErrorMonth")` is the whole point of
    # the table. Checking only for the value was the narrow-probe mistake this session keeps repeating: the sentence
    # reaches the user through the lookup, and its text never appears in the producing line.
    used_names = set(re.findall(r'\bText\(\s*"([A-Za-z0-9_]+)"\s*\)', text))

    print("table entries        : %d" % len(table))
    print("lines with UI text   : %d" % len(produced))
    print("entries looked up by name: %d" % len(used_names))
    print()

    dead = []
    for lineno, name, value in table:
        if name in used_names:
            continue
        # compare on the first sentence, unescaped, so a long entry with a trailing clause still matches
        probe = value.replace('\\"', '"').split(".")[0].strip()
        if len(probe) < 8:
            probe = value.replace('\\"', '"').strip()
        if probe and probe not in produced_blob:
            dead.append((lineno, name, value))

    print("table entries whose sentence no code produces: %d / %d" % (len(dead), len(table)))
    for lineno, name, value in dead:
        print("   L%-5d %-24s %s" % (lineno, name, value[:80]))

    rows = ["# `ProfileCsv` 文案：字典里有、代码不产出的（自动生成：`python analysis/dead_copy_check.py`）", "",
            "> 判据见脚本文件头。**这是文本比较，只覆盖一个文件**：由 `string.Format` 模板或拼接生成的句子",
            "> 可能匹配不上而被报为缺席，所以本表是**覆盖下界 / 死文案上界**。", "",
            "| 行 | 名称 | 文案 |", "|---|---|---|"]
    for lineno, name, value in dead:
        rows.append("| %d | `%s` | %s |" % (lineno, name, value.replace("|", "\\|")))
    rows.append("")
    rows.append("合计：**%d / %d** 条字典文案没有代码产出。" % (len(dead), len(table)))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(rows) + "\n")
    print()
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
