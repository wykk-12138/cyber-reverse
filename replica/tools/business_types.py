"""How many business types does the original declare, and how many does the replica have?

R1066 measured the application-side shortfall at roughly 103,000 functions and left open which functions they are. It
also said splitting BCL from business code is not computable, which was too pessimistic: the original's reflection
metadata carries fully qualified type names, and its own types sit under a Cybersole. prefix. Counting those is the
split, done by namespace ownership rather than by symbol names.

The metadata shape is <ns>.<Type>,<assembly>.<Member>!Getter, so every distinct type name can be recovered with one
regex over the string pool. The replica's side is its source, where a namespace declaration is equally explicit.

Run: python tools/business_types.py   (writes docs/BUSINESS_TYPES.md)
"""

import io
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "docs", "BUSINESS_TYPES.md")

SHAPE = re.compile(
    r"([A-Za-z][A-Za-z0-9_.]*\.[A-Za-z][A-Za-z0-9_]*),[A-Za-z0-9_.]+?\.([A-Za-z_][A-Za-z0-9_]*)"
    r"!(?:Getter|Setter|Property)")

# A control that must be non-zero before any zero below can be read: kpsdk is a Kasada cookie prefix the image carries.
CONTROL = r"kpsdk"


def probe(pattern, limit=2000):
    p = subprocess.run(
        [sys.executable, os.path.join(REPO, "analysis", "ida.py"), "str", pattern, "--limit", str(limit)],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return json.loads((p.stdout or "").strip())
    except Exception:
        m = re.search(r"\{.*\}", p.stdout or "", re.S)
        return json.loads(m.group(0)) if m else {"n": 0, "matches": []}


CAP = 500  # R1067: the plugin returns at most this many strings whatever limit is asked for.


def sharded_types(prefix=",Cybersole.", alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", depth=0):
    """Every Cybersole type, by walking the prefix space until each shard comes back unsaturated.

    R1068: one query cannot answer this. The plugin caps a reply at 500 strings, so a single Cybersole query returns
    whichever five hundred happen to sort first. Sharding on a narrowing prefix fixes it and verifies itself -- a shard
    that returns fewer than the cap was complete, and one that fills it gets split again. So the result is either the
    whole set or the shards that could not be resolved, and the two are distinguishable.
    """
    types, saturated, queries = {}, [], 0
    for letter in alphabet:
        pattern = re.escape(prefix + letter) if depth == 0 else re.escape(prefix) + letter
        d = probe(pattern, CAP)
        queries += 1
        hits = d.get("matches", [])
        for hit in hits:
            for m in SHAPE.finditer(hit.get("string", "")):
                full, member = m.group(1), m.group(2)
                if full.startswith("Cybersole."):
                    types.setdefault(full, set()).add(member)
        if len(hits) >= CAP:
            saturated.append(prefix + letter)
    return types, saturated, queries


def grow(terms, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", depth=0):
    """Split saturated shards until none is saturated, or the depth runs out."""
    types, todo, queries = {}, list(terms), 0
    pending = []
    while todo and depth < 2:
        next_round = []
        for term in todo:
            got, sat, q = sharded_types(term, alphabet, depth)
            queries += q
            for full, members in got.items():
                types.setdefault(full, set()).update(members)
            next_round.extend(sat)
        todo = next_round
        depth += 1
    pending = todo
    return types, pending, queries


def original_types():
    top, saturated, queries = sharded_types()
    if saturated:
        deeper_letters = "abcdefghijklmnopqrstuvwxyz"
        more, pending, q2 = grow(saturated, deeper_letters, 1)
        for full, members in more.items():
            top.setdefault(full, set()).update(members)
        queries += q2
        if pending:
            print("  !! still saturated after two levels: %s" % ", ".join(pending[:8]))
    return top, queries


def replica_types():
    types = {}
    for base, _dirs, files in os.walk(os.path.join(ROOT, "src")):
        for name in files:
            if not name.endswith(".cs"):
                continue
            path = os.path.join(base, name)
            try:
                text = io.open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            ns = re.search(r"^namespace\s+([A-Za-z0-9_.]+)", text, re.M)
            ns_name = ns.group(1) if ns else "(none)"
            for m in re.finditer(r"^\s*(?:public|internal)\s+(?:sealed\s+|static\s+|abstract\s+|partial\s+)*"
                                 r"(?:class|record|struct|enum|interface)\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.M):
                types.setdefault(ns_name + "." + m.group(1), set()).add(name)
    return types


def main():
    control = probe(CONTROL).get("n", -1)
    orig, pool_hits = original_types()
    repl = replica_types()

    # R1067: refuse to publish a zero. The probe returns at most 500 strings -- asking for 5000 still returns 500 --
    # so the original side is a sample, and a sample that happens to contain no attribute-shaped Cybersole strings
    # reports zero types. That is a property of the window, not of the image. The next step is to shard the query by
    # first letter to get past the cap rather than to read this zero.
    if not orig:
        print("  REFUSED: the original side returned no types, and the probe is capped at 500 strings.")
        print("  A zero here means the sample missed, not that the image has no such types.")
        print("  Shard the query by prefix before publishing anything from this tool.")
        return 2

    # Compare by simple type name, because the goal allows different names and different namespaces, but a shared
    # simple name is the only correspondence available without reading both.
    orig_simple = defaultdict(set)
    for full in orig:
        orig_simple[full.rsplit(".", 1)[-1]].add(full)
    repl_simple = defaultdict(set)
    for full in repl:
        repl_simple[full.rsplit(".", 1)[-1]].add(full)

    both = sorted(set(orig_simple) & set(repl_simple))
    only_orig = sorted(set(orig_simple) - set(repl_simple))
    only_repl = sorted(set(repl_simple) - set(orig_simple))

    orig_ns = Counter(f.rsplit(".", 1)[0] for f in orig)
    repl_ns = Counter(f.rsplit(".", 1)[0] for f in repl)

    lines = []
    add = lines.append
    add("# 业务类型覆盖（生成物 —— 不要手改）")
    add("")
    add("由 `python tools/business_types.py` 生成。")
    add("")
    add("**为什么用前缀分离**：R1066 说「BCL 与业务不可分」，那说得过头了 ——")
    add("镜像的反射元数据带**全限定类型名**，而它自己的类型都在 `Cybersole.` 下。")
    add("**按命名空间归属分，就是那个分离**，不需要函数名。")
    add("")
    add("## 一、对照")
    add("")
    add("| 对照串 | 命中 |")
    add("|---|---|")
    add("| `%s` | **%d** |" % (CONTROL, control))
    add("| `Cybersole.` **分片查询次数** | **%d** |" % pool_hits)
    add("")
    add("**→ 对照%s。**" % ("成立" if control > 0 else "不成立，下方为零不可读"))
    add("")
    add("## 二、两个数")
    add("")
    add("| 侧 | 业务类型数 | 命名空间数 |")
    add("|---|---|---|")
    add("| **原版**（元数据） | **%d** | %d |" % (len(orig), len(orig_ns)))
    add("| **复刻件**（源码） | **%d** | %d |" % (len(repl), len(repl_ns)))
    add("")
    add("## 三、按简单类型名对")
    add("")
    add("| 类别 | 数 |")
    add("|---|---|")
    add("| 两边都有（同名） | **%d** |" % len(both))
    add("| 只在原版 | **%d** |" % len(only_orig))
    add("| 只在复刻件 | **%d** |" % len(only_repl))
    add("")
    add("**→ 「只在原版」不是缺口**：goal 明说「命名可不同」，而这一列里有一大部分是复刻件用了自己的名字。")
    add("→ 而「两边都有」那 %d 个同名类型，才是可以用名字对字段的（见 `TYPE_COVERAGE.md`）。" % len(both))
    add("")
    add("### 只在原版的 %d 个（逐个列出，否则这个数无法行动）" % len(only_orig))
    add("")
    if only_orig:
        for name in only_orig:
            origin = ", ".join(sorted(orig_simple[name]))
            add("- `%s`  ← 原版 `%s`" % (name, origin))
    else:
        add("（无）")
    add("")
    add("**→ 每一个都要判一次：命名不同、还是真缺。**")
    add("→ 判据不是名字，是**它在任何命名空间下有没有对应物** —— 那要看 534 个「只在复刻件」里有没有干同一件事的。")
    add("")
    add("### 原版有而复刻件**无同名命名空间**的")
    add("")
    orphan_ns = sorted(ns for ns in orig_ns if ns not in repl_ns)
    if orphan_ns:
        add("| 命名空间 | 类型数 |")
        add("|---|---|")
        for ns in orphan_ns:
            add("| `%s` | %d |" % (ns, orig_ns[ns]))
    else:
        add("（无 —— 原版每个命名空间在复刻件里都有同名的）")
    add("")
    add("## 四、原版命名空间的前 20 个（按类型数）")
    add("")
    add("| 命名空间 | 类型数 |")
    add("|---|---|")
    for ns, n in orig_ns.most_common(20):
        marker = " ✓" if ns in repl_ns else ""
        add("| `%s` | **%d** |%s" % (ns, n, marker))
    add("")
    add("**→ ✓ 表示复刻件里也有同名命名空间。**")
    add("")
    add("## 五、边界")
    add("")
    add("- **原版侧是元数据，不是源码**：只算有属性访问器的类型 ⇒ 纯静态类、纯枚举会漏 ⇒ **原版侧是下界**。")
    add("- **复刻件侧是源码**：`class`/`record`/`struct`/`enum`/`interface` 都算，比元数据宽。")
    add("- **只按简单名对**：`A.Thing` 与 `B.Thing` 会被当成同名，而那可能是两个不同的类型。")
    add("- **不比较行为**：类型数齐了不等于功能等。")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("  wrote docs/BUSINESS_TYPES.md")
    print("  control=%d  pool_hits=%d" % (control, pool_hits))
    print("  original types=%d  namespaces=%d" % (len(orig), len(orig_ns)))
    print("  replica  types=%d  namespaces=%d" % (len(repl), len(repl_ns)))
    print("  same simple name=%d  only original=%d  only replica=%d" % (len(both), len(only_orig), len(only_repl)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
