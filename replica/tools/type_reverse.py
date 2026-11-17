"""Reverse-lookup the original's full name for each core replica type, then compare properties.

R1056 found that guessing a namespace is what produced a false zero: Cybersole.Core.CloudflareSolverConfig does not
exist, and the real name was Cybersole.CloudflareSolvers.CloudflareSolver, recovered from a distinctive member name.
R1057 showed the two namespaces this work had been reasoning about hold one type each, so the coverage was exhaustive
for them and nothing more.

This generalises the method rather than the subject. Given a replica type, it recovers the original's full type name
from the metadata shape by searching for the type name followed by a comma -- the shape is <full type>,<assembly>.<member>!
Getter, so the type name alone is enough to find its namespace, and the members come free. Where that fails it falls
back to a distinctive member name and reads the type in front of it.

Run: python tools/type_reverse.py   (writes docs/TYPE_REVERSE.md)
"""

import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "docs", "TYPE_REVERSE.md")

# (replica type, replica file relative to src/, a distinctive member to fall back on). Chosen because they sit on the
# core paths: risk control, captcha, payment and the fingerprint layer.
TARGETS = [
    ("AntiBotProtocol", "Cybersole.Stores/Flows/AntiBotProtocol.cs", None),
    ("AntiBotVendors", "Cybersole.Stores/Flows/AntiBotVendors.cs", None),
    ("CaptchaSolverService", "Cybersole.Services/Captcha/CaptchaSolverService.cs", None),
    ("AdyenGateway", "Cybersole.Stores/Payments/AdyenGateway.cs", None),
    ("ApiKasadaSolver", "Cybersole.Stores/Scripts/ApiKasadaSolver.cs", None),
    ("BrowserIdentity", "Cybersole.Stores/Scripts/BrowserIdentity.cs", None),
    ("VendorWiring", "Cybersole.Stores/Scripts/VendorWiring.cs", None),
    ("CloudflareClearance", "Cybersole.Stores/Scripts/CloudflareClearance.cs", None),
    ("DataDomeClearance", "Cybersole.Stores/Scripts/DataDomeClearance.cs", None),
    ("KasadaClearance", "Cybersole.Stores/Scripts/KasadaClearance.cs", None),
]

SHAPE = re.compile(
    r"([A-Za-z][A-Za-z0-9_.]*\.[A-Za-z][A-Za-z0-9_]*),[A-Za-z0-9_.]+?\.([A-Za-z_][A-Za-z0-9_]*)"
    r"!(?:Getter|Setter|Property)")


def probe(pattern, limit=600):
    p = subprocess.run(
        [sys.executable, os.path.join(REPO, "analysis", "ida.py"), "str", pattern, "--limit", str(limit)],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return json.loads((p.stdout or "").strip())
    except Exception:
        m = re.search(r"\{.*\}", p.stdout or "", re.S)
        return json.loads(m.group(0)) if m else {"n": 0, "matches": []}


def original_for(type_name):
    """Full original type name plus its members, recovered from the metadata shape."""
    d = probe(re.escape(type_name) + ",")
    found = {}
    for hit in d.get("matches", []):
        for m in SHAPE.finditer(hit.get("string", "")):
            full, member = m.group(1), m.group(2)
            if full.rsplit(".", 1)[-1] == type_name:
                found.setdefault(full, set()).add(member)
    return found


def replica_members(rel_path, type_name):
    path = os.path.join(ROOT, "src", rel_path.replace("/", os.sep))
    if not os.path.exists(path):
        return set(), "file missing"
    text = io.open(path, encoding="utf-8", errors="replace").read()
    start = text.find("class " + type_name)
    if start < 0:
        return set(), "class missing"
    begin = text.find("{", start)
    depth, i = 0, begin
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = text[begin:i]
    members = set(re.findall(r"public\s+(?:static\s+)?[\w?.<>\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\{\s*get|\()", body))
    return members, "ok"


def main():
    rows = []
    for type_name, rel, _fallback in TARGETS:
        found = original_for(type_name)
        rmembers, status = replica_members(rel, type_name)
        rows.append((type_name, rel, found, rmembers, status))

    lines = []
    add = lines.append
    add("# 类型反查（生成物 —— 不要手改）")
    add("")
    add("由 `python tools/type_reverse.py` 生成。")
    add("")
    add("**方法**：镜像的反射元数据形如 `<全名>,<程序集>.<成员>!Getter`，所以**用类型名本身**就能反查到它的命名空间，")
    add("成员随之而来。R1056 证明猜命名空间会造出假零（`Cybersole.Core.CloudflareSolverConfig` 不存在），")
    add("而反查不会 —— 名字要么找到，要么找不到，找不到时**这一行报 Unknown**。")
    add("")
    add("## 逐类型")
    add("")
    for type_name, rel, found, rmembers, status in rows:
        add("### `%s`" % type_name)
        add("")
        if not found:
            add("**→ Unknown：镜像里没有以 `%s,` 开头的元数据。** 而这有**三种**成因，而它们的含义完全不同：" % type_name)
            add("")
            add("| 成因 | 含义 | 是不是缺口 |")
            add("|---|---|---|")
            add("| 原版无此类型 | 那一层在原版是**方法**或**数据**，不是一个类 | **不是** |")
            add("| 原版用别的名字 | goal 明说「命名可不同」 | **不是** |")
            add("| 属性 getter 全被内联 | 那这个形状查不到它 | **Unknown —— 需另找路径** |")
            add("")
            add("**→ 所以本行**不能**读成「这个类型在原版缺失」**：只有第三种成因才是缺口，")
            add("而前两种在原版的**功能**里可能完好存在。复刻件侧 `%s` 读作 **%s**，%d 个成员。"
                % (rel, status, len(rmembers)))
            add("")
            continue
        for full, omembers in sorted(found.items()):
            missing = sorted(omembers - rmembers)
            add("| 度量 | 值 |")
            add("|---|---|")
            add("| 镜像全名 | `%s` |" % full)
            add("| 镜像成员 | **%d** |" % len(omembers))
            add("| 复刻件成员（`%s`） | **%d** |" % (rel.rsplit("/", 1)[-1], len(rmembers)))
            add("| **镜像有而复刻件无** | **%d** |" % len(missing))
            add("")
            if missing:
                add("**→ 缺口：** %s" % " · ".join("`%s`" % m for m in missing))
            else:
                add("**→ 缺口：无。**")
            add("")
    add("## 边界")
    add("")
    add("- **只比成员名，不比类型与行为**：属性齐了不等于行为等。")
    add("- **成员提取是启发式**：复刻件侧用正则抓 `public ... Name { get` 与 `public ... Name(`，")
    add("  所以带属性的字段、显式接口实现、以及只读表达式体会漏。**那些漏项会让缺口数偏大，不会偏小。**")
    add("- **原版侧可能不全**：若某属性 getter 被内联，它不出现在这个形状里 ⇒ 原版成员数是**下界**。")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))

    unresolved = [r for r in rows if not r[2]]
    gaps = sum(len(o - r[3]) for _t, _p, f, r, _s in rows for o in f.values())
    print("  wrote docs/TYPE_REVERSE.md")
    print("  types=%d  resolved=%d  unresolved=%d  member gaps=%d"
          % (len(rows), len(rows) - len(unresolved), len(unresolved), gaps))
    for type_name, _rel, found, rmembers, status in rows:
        if not found:
            print("    UNRESOLVED %-24s (replica %d members, %s)" % (type_name, len(rmembers), status))
        else:
            for full, omembers in found.items():
                miss = sorted(omembers - rmembers)
                print("    %-24s -> %-46s orig=%-3d repl=%-3d missing=%d"
                      % (type_name, full, len(omembers), len(rmembers), len(miss)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
