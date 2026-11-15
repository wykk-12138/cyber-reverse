"""Reclassify the last seven "fixable" types — they are not data models (R566).

`TYPE_GAPS.md`'s `disposal()` only knew two structural cases (markup extension, collection wrapper) and called
everything else 「可补」. That left seven entries looking like a to-do list when they are not:

    AccountsCreatorView    binds `Add` and `Close` — Close is the Window constraint
    AuthWindow             a Window subclass: Exit / Minimise / Logout
    LicenseControl         Authenticate / Refresh / Dashboard
    SettingsView           ~30 members, each a settings-page reference
    TaskCreatorCartView    Add / Delete / SizeItems
    TaskCreatorMainView    ProfileGroupItems / ProfileItems / ShowCartView
    Services.ImapProvider  already RENAMED to ImapMailProvider (R512)

The rule added here is mechanical and stated in the output, so it can be argued with:

  * the short name ends in `View`, `Window` or `Control`  -> a page/shell, not a container
  * any member is a verb-shaped command
    (Add, Close, Delete, Exit, Logout, Minimise, Authenticate, Refresh, Dashboard, Show*)
                                                          -> the type carries behaviour
  * otherwise                                             -> 「可补」

`ImapProvider` still appears as UNIMPLEMENTED because the triage only drops a type when a *same-named* class
exists; the rename map knows better, so it is called out by name.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"
DESCRIPTORS = os.path.join(ROOT, "analysis", "binding_descriptors.tsv")
TRIAGE = os.path.join(ROOT, "analysis", "type_presence_triage.tsv")
OUT = os.path.join(ROOT, "docs", "TYPE_GAPS.md")

VERBS = ("Add", "Close", "Delete", "Exit", "Logout", "Minimise", "Authenticate", "Refresh",
         "Dashboard")
RENAMED_BY_HAND = {"Cybersole.Services.ImapProvider": "ImapMailProvider"}


def load_descriptors():
    table = {}
    for line in io.open(DESCRIPTORS, encoding="utf-8").read().splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        table.setdefault(parts[0], {}).setdefault(parts[2], set()).add(parts[3])
    return table


def load_triage():
    rows = []
    for line in io.open(TRIAGE, encoding="utf-8").read().splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 6 and parts[5].strip() == "UNIMPLEMENTED":
            rows.append((parts[0], parts[1], parts[2], parts[3], parts[4]))
    return rows


def why(decl, members):
    short = decl.split(".")[-1]
    names = set(members)
    accessors = set()
    for kinds in members.values():
        accessors |= kinds
    if short.endswith("Extension") or "$" in short:
        return "markup extension / XAML helper"
    if names <= {"Count", "IsReadOnly", "Item", "Keys", "Values", "Add", "Remove", "Contains"}:
        return "collection wrapper"
    if "Property" in accessors and len(names) <= 3:
        return "single bindable property holder"
    if accessors <= {"Getter", "Setter"} and len(names) <= 4:
        return "small data model"
    if accessors <= {"Getter", "Setter"}:
        return "data model"
    return "view / control surface"


def disposal(decl, guess, members):
    short = decl.split(".")[-1]

    if guess == "markup extension / XAML helper":
        return ("**结构差异，不补**：这是 XAML 的 `MarkupExtension`。复刻件没有 XAML"
                "（0 个 `.axaml`、0 个 `MarkupExtension` 子类），全部控件用 C# 构建，没有可插的地方。")
    if guess == "collection wrapper":
        return "**结构差异，不补**：Avalonia 的基础集合类型已经覆盖，复刻件不需要自己的包装。"

    if decl in RENAMED_BY_HAND:
        return ("**结构差异，不补**：R512 已把它判为改名 → `%s`，那个类已经存在。再补一个同名类型"
                "只是为把数字减一。" % RENAMED_BY_HAND[decl])

    if short.endswith("View") or short.endswith("Window") or short.endswith("Control"):
        return ("**结构差异，不补**：类型名以 `View`/`Window`/`Control` 结尾 —— 这是一个页面或外壳，"
                "不是装数据的类。复刻件对应页面已经存在（见 `OriginalViewClassParityTests`）。")

    hits = sorted(n for n in members if n in VERBS or n.startswith("Show"))
    if hits:
        return ("**结构差异，不补**：成员里有命令形状的 `%s` —— 这个类型承载行为，不是数据。"
                "补一个只有属性的壳子会把「有行为」写成「有属性」。" % "`/`".join(hits))

    return "**可补**：先定职责，再按描述符表里的成员名补齐。"


def main():
    desc = load_descriptors()
    rows = load_triage()

    detail = []
    for decl, count, best, hit, jac in rows:
        members = desc.get(decl, {})
        guess = why(decl, members)
        detail.append((decl, count, best, hit, jac, guess, members, disposal(decl, guess, members)))

    structural = sum(1 for d in detail if "结构差异" in d[7])
    fixable = len(detail) - structural

    lines = [
        "# 类型缺失：未实现类型，逐条列出缺什么",
        "",
        "> 生成物：`python analysis/type_gaps_report.py`。数据来自 `analysis/binding_descriptors.tsv`"
        "（原版绑定描述符表）与 `analysis/type_presence_triage.tsv`（R512 三分类）。",
        "> 判据 a 要求「每条若不可得则写 Unknown + 缺什么」—— 这份文件就是那句「缺什么」。",
        "",
        "## 怎么读",
        "",
        "- **成员**：原版在那个类型上绑定的成员名，后跟访问器种类（`G` = Getter、`S` = Setter、`P` = Property）。",
        "- **判断（启发式）**：从成员形状和类型名推的，**不是反编译证据**。",
        "- **处置**：`结构差异` 表示复刻件换了实现方式或这本来就不是数据类；`可补` 表示应该补。",
        "",
        "## 汇总",
        "",
        "| 项 | 条数 |",
        "|---|---|",
        "| 总计 | %d |" % len(detail),
        "| **结构差异（不补）** | **%d** |" % structural,
        "| **可补** | **%d** |" % fixable,
        "",
        "> **标成结构差异的条目，`bind_diff --type-presence` 的数字不会因此变化** —— 那个度量问的是"
        "「有没有同名类型」，不是「该不该有」。所以 `docs/METRICS.md` 仍是它自己的数。",
        "",
        "## 逐条",
        "",
    ]

    for decl, count, best, hit, jac, guess, members, disp in sorted(
            detail, key=lambda x: (x[7].startswith("**可补"), x[0])):
        lines.append("### `%s`" % decl)
        lines.append("")
        lines.append("- 成员数（描述符表记的）：%s；分类脚本命中：%s / Jaccard %s" % (count, hit, jac))
        lines.append("- 与复刻件最接近的类：`%s`（**这是启发式匹配，不要当成同一类型**）" % best)
        lines.append("- 判断（启发式）：%s" % guess)
        lines.append("- 处置：%s" % disp)
        if members:
            rendered = []
            for name in sorted(members):
                kinds = members[name]
                tag = ("G" if "Getter" in kinds else "") + ("S" if "Setter" in kinds else "") + \
                      ("P" if "Property" in kinds else "")
                rendered.append("`%s`(%s)" % (name, tag or "?"))
            lines.append("- 成员：%s" % "、".join(rendered))
        else:
            lines.append("- 成员：（描述符表里没有这个类型的成员行）")
        lines.append("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    print("wrote TYPE_GAPS.md")
    print("  total      %d" % len(detail))
    print("  structural %d" % structural)
    print("  fixable    %d" % fixable)


if __name__ == "__main__":
    main()
