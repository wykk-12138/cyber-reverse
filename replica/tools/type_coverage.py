"""Generate docs/TYPE_COVERAGE.md -- criterion (a)'s type-level gaps, computed rather than asserted.

Criterion (a) asks for type-level gaps and missing types to be zero, with anything unobtainable written as Unknown and
what is missing named. Reflection metadata gives the original's properties in a regular shape: <Namespace>.<Type>,
<Assembly>.<Member>!Getter for a property. So for a chosen type the original's property set is a query, and the
replica's is its source. Comparing the two is arithmetic, not judgement.

Scope is stated rather than implied: the types below are the core ones this work has been reasoning about. The image
carries thousands of types and this does not claim to enumerate them; a type not listed is not thereby absent.

Why a generator: R1030 and R1041, as with the other coverage documents.

Run: python tools/type_coverage.py   (writes docs/TYPE_COVERAGE.md)
"""

import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "docs", "TYPE_COVERAGE.md")

# (original type name, replica file, replica type name). The image's property shape is
# "<ns>.Type,<asm>.<Member>!Getter", so the query is the type name with a comma after it.
TYPES = [
    ("Cybersole.CaptchaProviders.CaptchaProvider", "Cybersole.Core/Settings/GlobalSettings.cs", "CaptchaProvider"),
    # R1056: the real name, found by reverse lookup on IsFetchingBalance and BalanceSupported rather than guessed. The
    # namespace is Cybersole.CloudflareSolvers, the same shape as Cybersole.CaptchaProviders.
    ("Cybersole.CloudflareSolvers.CloudflareSolver", "Cybersole.Core/Settings/GlobalSettings.cs", "CloudflareSolverConfig"),
]

# Members the replica adds deliberately. A key is local bookkeeping; a flag that the list membership already expresses
# is a representation choice. Neither is a gap, and saying so is part of the table rather than a footnote.
REPLICA_EXTRAS = {
    "CaptchaProvider": {"Id": "本地主键（镜像无此字段，镜像用列表位置表示）",
                        "Enabled": "列表成员即启用（镜像用 EnabledProviders 集合表达同一件事）"},
    "CloudflareSolverConfig": {"Id": "本地主键"},
}


def probe(pattern, limit=600):
    p = subprocess.run(
        [sys.executable, os.path.join(REPO, "analysis", "ida.py"), "str", pattern, "--limit", str(limit)],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return json.loads((p.stdout or "").strip())
    except Exception:
        m = re.search(r"\{.*\}", p.stdout or "", re.S)
        return json.loads(m.group(0)) if m else {"n": 0, "matches": []}


def original_members(type_name):
    """Property names the image carries for this type, from the reflection metadata shape."""
    d = probe(re.escape(type_name) + ",")
    members = set()
    for hit in d.get("matches", []):
        for m in re.finditer(re.escape(type_name) + r",[A-Za-z0-9_.]+?\.([A-Za-z_][A-Za-z0-9_]*)!(?:Getter|Setter|Property)",
                             hit.get("string", "")):
            members.add(m.group(1))
    return members, d.get("n", -1)


def replica_members(rel_path, type_name):
    path = os.path.join(ROOT, "src", rel_path.replace("/", os.sep))
    text = io.open(path, encoding="utf-8", errors="replace").read()
    start = text.find("class " + type_name)
    if start < 0:
        return set()
    # to the closing brace of the class: count braces from the declaration
    depth = 0
    begin = text.find("{", start)
    i = begin
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = text[begin:i]
    return set(re.findall(r"public\s+[\w?.<>\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*get", body))


def main():
    rows = []
    for original, rel, replica_type in TYPES:
        omembers, n = original_members(original)
        rmembers = replica_members(rel, replica_type)
        extras = REPLICA_EXTRAS.get(replica_type, {})
        missing = sorted(omembers - rmembers)
        added = sorted(rmembers - omembers - set(extras))
        # R1055: an empty original side makes missing trivially zero, and that zero means nothing -- the query found no
        # metadata for this type name, so either the name is wrong or the members are all inlined away. Reporting zero
        # there would be the empty-set-subtracts-to-empty-set mistake that R1044's control exists to catch.
        resolved = len(omembers) > 0
        rows.append((original, replica_type, omembers, rmembers, missing, added, n, resolved))

    total_missing = sum(len(r[4]) for r in rows if r[7])
    unresolved = [r for r in rows if not r[7]]

    lines = []
    add = lines.append
    add("# 类型级覆盖（生成物 —— 不要手改）")
    add("")
    add("由 `python tools/type_coverage.py` 生成。完成判据 (a)：**类型级缺口、类型缺失 → 0**，")
    add("不可得写 Unknown + 缺什么。")
    add("")
    add("**取证方式**：镜像的反射元数据里，属性形如 `<命名空间>.<类型>,<程序集>.<成员>!Getter`，")
    add("所以「原版某个类型有哪些属性」是一个**查询**而不是判断。复刻件侧读源码里的 `get` 访问器。")
    add("")
    add("**范围**：下表只覆盖本工作一直在推理的核心类型。镜像有数千个类型，")
    add("而**本表不声称枚举了它们** —— 没列出的类型不因此而被判为缺席。")
    add("")
    add("## 一、逐类型对照")
    add("")
    for original, replica_type, omembers, rmembers, missing, added, n, resolved in rows:
        add("### `%s` ↔ `%s`" % (original, replica_type))
        add("")
        if not resolved:
            add("**→ Unknown：原版侧查询为空（元数据命中 %d）。**" % n)
            add("")
            add("**缺什么**：这个类型在镜像里的**真实名字**。`%s` 是本地猜的，而查询返回零 ⇒" % original)
            add("两种可能：名字不对，或该类型的属性 getter 全被内联掉而不出现在这个形状里。")
            add("**→ 所以本行不计入缺口，也不计为已覆盖。**")
            add("")
            continue
        add("| 度量 | 值 |")
        add("|---|---|")
        add("| 镜像元数据命中 | %d |" % n)
        add("| 镜像属性 | **%d** |" % len(omembers))
        add("| 复刻件属性 | **%d** |" % len(rmembers))
        add("| **镜像有而复刻件无** | **%d** |" % len(missing))
        add("| 复刻件自加 | %d |" % len(added))
        add("")
        if omembers:
            add("镜像属性：%s" % " · ".join("`%s`" % m for m in sorted(omembers)))
            add("")
        if missing:
            add("**→ 缺口：** %s" % " · ".join("`%s`" % m for m in missing))
        else:
            add("**→ 缺口：无。** 镜像的每个属性在复刻件里都有。")
        add("")
        if added:
            add("复刻件自加：%s" % " · ".join("`%s`%s" % (m, "（" + REPLICA_EXTRAS.get(replica_type, {}).get(m, "") + "）"
                                                    if REPLICA_EXTRAS.get(replica_type, {}).get(m) else "") for m in added))
            add("")
    add("## 二、结论")
    add("")
    add("**类型级缺口合计：%d**（只计原版侧**查询成功**的类型）。" % total_missing)
    add("")
    if unresolved:
        add("**而 %d 个类型的原版侧查询为空 ⇒ 记为 Unknown，不计入缺口：** %s"
            % (len(unresolved), " · ".join("`%s`" % r[1] for r in unresolved)))
        add("")
    if total_missing == 0:
        add("**→ 在**查询成功**的类型上，(a) 的缺口为 0**：镜像的每个属性在复刻件里都能找到。")
        add("→ 而「复刻件自加」的几个字段各有理由（本地主键、以及用列表成员表达镜像的 `EnabledProviders` 集合），")
        add("那些是**表示选择**，不是缺口 —— 而把理由写在表里，是为了让它们不变成下一轮的假缺口。")
    else:
        add("**→ 上面列出的字段要在复刻件里补上。**")
    add("")
    add("## 三、边界")
    add("")
    add("- **只比属性名，不比类型**：镜像的元数据里没有属性的 CLR 类型，所以 `Balance` 是 `double` 还是 `string` 本表不问。")
    add("- **只比属性，不比行为**：属性齐了不等于行为等 —— 那要到方法级，而 R1045 说产物无符号，方法级要另找路径。")
    add("- **元数据可能不全**：若某属性的 getter 被内联掉，它可能不出现在这个形状里，")
    add("  那样「镜像属性数」就是**下界**而不是全量。")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("  wrote docs/TYPE_COVERAGE.md")
    for original, replica_type, omembers, rmembers, missing, added, n, resolved in rows:
        print("  %-46s meta=%-4d orig=%-3d repl=%-3d missing=%-2d added=%-2d %s"
              % (replica_type, n, len(omembers), len(rmembers), len(missing), len(added),
                 "" if resolved else "UNRESOLVED"))
    print("  type-level gaps total: %d (unresolved types: %d)" % (total_missing, len(unresolved)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
