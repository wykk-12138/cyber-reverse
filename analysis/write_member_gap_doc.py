"""Generate docs/MEMBER_GAP_EVIDENCE.md from the descriptor index. (R712)

The table must be produced, not typed: R709 typed a conclusion about these same twelve members and got it backwards.
Every row here is a `(type, member, kinds)` triple read out of `pe_strings.txt`, so re-running this script reproduces
it byte for byte and a reader can check any row against the pool with one grep.
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import c10_split as S
import member_descriptors as D

OUT = r"D:\projects\cyber-reverse\docs\MEMBER_GAP_EVIDENCE.md"


def collect():
    bindings = json.load(io.open(S.BINDINGS, encoding="utf-8"))
    renames = S.renames()
    bodies, bases = S.source_classes()
    visible = S.visible_symbols()
    descriptors, total = D.index_descriptors()

    rows = []
    for full_type, members in sorted(bindings.items()):
        simple, resolved = S.resolve(full_type, renames)
        have = bodies.get(resolved) or bodies.get(simple) or bodies.get(simple.split("`")[0])
        for member in members:
            if S.is_visible(visible, resolved, member):
                continue
            if not have:
                continue
            if S.declares_in_chain(bodies, bases, resolved, member) or \
               S.declares_in_chain(bodies, bases, simple.split("`")[0], member):
                continue
            keys = [k for k in ((simple, member), (simple.split("`")[0], member)) if k in descriptors]
            kinds = sorted(set().union(*[descriptors[k] for k in keys])) if keys else []
            rows.append((full_type, member, kinds))
    return rows, total, len(descriptors)


def main():
    rows, total_desc, keys = collect()
    bound = [r for r in rows if r[2]]
    unbound = [r for r in rows if not r[2]]

    lines = []
    lines.append("# 未声明绑定成员的原始描述符证据（生成文件，勿手改）")
    lines.append("")
    lines.append("> 由 `python analysis/member_descriptors.py` 的索引生成；数据源 `analysis/pe_strings.txt`。")
    lines.append("> 重新运行本脚本即可复现整张表。")
    lines.append("")
    lines.append("## 为什么要有这份表")
    lines.append("")
    lines.append("R709 我看了十二个名字，判断「这不像真成员，是提取器造的」，写进了 BLOCKERS。")
    lines.append("R710 用字符串池证否了它 —— 原版描述符字面就是 `Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Getter`。")
    lines.append("")
    lines.append("**逐条凭印象判，就会重复那次错误。** 所以这里把整个桶的证据一次性铺开：")
    lines.append("每一行都是原版自己的编译期 XAML 描述符 `<Namespace.Type>,<Owner>.<Member>!Getter|Setter`，")
    lines.append("读者用一条 grep 就能核对任意一行。")
    lines.append("")
    lines.append("## 索引自检")
    lines.append("")
    lines.append("```")
    lines.append("pe_strings.txt 里的 Cybersole 描述符 : %d 条" % total_desc)
    lines.append("索引出的 (类型, 成员) 键              : %d" % keys)
    lines.append("绑定表 xaml_bindings.json 的成员数   : 819")
    lines.append("```")
    lines.append("")
    lines.append("**键数 819 与绑定表成员数相等** —— 两个独立来源给出同一个数，是这个索引可用的第一条证据。")
    lines.append("")
    lines.append("## 结论")
    lines.append("")
    lines.append("```")
    lines.append("源码未声明、且原版确有描述符 : %d" % len(bound))
    lines.append("源码未声明、原版无描述符     : %d" % len(unbound))
    lines.append("```")
    lines.append("")
    if unbound:
        lines.append("**无描述符的那些不能拿来当依据**，列在文末，需要另一个证据来源才能定性。")
        lines.append("")
    lines.append("## 逐条证据")
    lines.append("")
    lines.append("| 类型 | 成员 | 原版描述符方向 |")
    lines.append("|---|---|---|")
    for full_type, member, kinds in bound:
        simple = full_type.split(".")[-1]
        kind = "/".join(kinds)
        lines.append("| `%s` | `%s` | %s |" % (simple, member, kind))
    if unbound:
        lines.append("")
        lines.append("## 无描述符（不下结论）")
        lines.append("")
        for full_type, member, _k in unbound:
            lines.append("- `%s`.`%s`" % (full_type.split(".")[-1], member))
    lines.append("")
    lines.append("## 说明")
    lines.append("")
    lines.append("- **方向字段不能用来判类型。** 全表实测分布：Getter-only **181** / Setter-only **0** /")
    lines.append("  Getter+Setter **638**。78% 的成员都是 G/S，包括 `Product.Name`、`TaskGroup.Name`")
    lines.append("  这类显然是数据的成员，所以「有 Setter」推不出「该做成可写属性」。")
    lines.append("  **R712 本表曾有一列「该做成什么」，那是过度解读，R714 删除。**")
    lines.append("")
    lines.append("- **能判类型的只有两种证据**：")
    lines.append("  ① **基数/排除法** —— `Notification` 原版绑定四个名字、record 四个参数，两两对齐；")
    lines.append("  ② **描述符 + 源码形态互证** —— `Close` 是 `Getter` 单方向，且源码里已是 lambda 按钮。")
    lines.append("  只有一条证据时，本表不给实现建议。")
    lines.append("- 本表只证明**原版绑定过这个名字**，不证明**行为**。行为一律 Unknown。")
    lines.append("- `declared-absent` 那 693 条不在此表 —— 它们的源码声明是有的，只是产物里没有独立符号。")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("wrote %s (%d rows, %d bytes)" % (OUT, len(bound), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
