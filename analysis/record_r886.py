"""Record R886: the metric was under-counting by 16 because its source was a sample."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 「形状」从 **78 变 94** —— 数字变差，而那是修正（R886）

**R885 暴露：`METRICS.md` 的「成员形状差异」读的是抽样池。这一轮把三处一起修了。**

| 文件 | 改动 |
|---|---|
| `analysis/dump_accessors_v2.py` | **新建**：每行 `(类型, 属性, 种类)`，**保留 Getter/Setter/Property** |
| `replica/docs/baseline/recovered_accessors_by_type.txt` | **重生成**：1,275 行 (类型,属性) / **508 类型** / Getter 950 · Setter 687 · Property 950 |
| `tools/shape_audit.py` | `--baseline` 读新格式（种类不再丢） |
| `tools/metrics_report.py` | 调 `shape_audit.py` **加 `--baseline`** |

### 数字变化

| 证据源 | 类型数 | mismatches |
|---|---|---|
| 抽样池（原） | 102 | **78** |
| 全量基线（现） | 211 | **94** |

**94 比 78 差 —— 而它更对。**

**多出的 16 条是抽样池里根本没有的类型上的真实差异。
换句话说：这个指标过去一直在**少报**，而「78」在报表上看起来比「94」好。**

### 这是本轮唯一的产品影响

**`docs/METRICS.md` 现在写 `成员形状差异 — total mismatches | 94`（L23 与 L218 两处）。**

**而判据 (a)「类型级缺口 → 0」的距离因此**变远**了 16 条 —— 这是正确方向上的变远。**

### 三层错的顺序

1. **R883**：Dump 时把带字段的数据压成不带字段（引入缺陷，症状是安静返回 0）
2. **R885**：发现证据源是抽样，但只加开关、没改调用方
3. **R886**：重生成基线 + 改调用方 → 指标从 78 修正到 94

**每一层都是上一层没走完的那一步。**
"""

if "「形状」从 **78 变 94**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R886 appended")

BLOCKER = """

---

## 310. 形状指标 **78 → 94**：数字变差，而那是修正

> R886。**改工具链三处**（含 `metrics_report.py` 的调用）。套件 **1780 通过 / 0 失败 / 0 跳过**。

### 一、三层错的完整链

| 轮 | 做错了什么 | 症状 |
|---|---|---|
| **R883** | Dump 时把 `(类型, 属性, 种类)` 压成 `(类型, 属性列表)` | **种类丢了 → 下游读不到 → 安静返回 0** |
| **R885** | 发现证据源是抽样池，但只给工具加开关、**没改调用方** | 指标仍是 78 |
| **R886** | 重生成基线带种类 + 改 `metrics_report.py` 加 `--baseline` | **78 → 94** |

**每一层都是上一层没走完的那一步。**

### 二、重生成的基线

```
1,275 行 (类型, 属性) · 508 个类型 · Getter 950 · Setter 687 · Property 950
```

**格式：`<类型> TAB <属性> TAB <逗号分隔的种类>`。**

### 三、数字变化

| 证据源 | 类型数 | mismatches |
|---|---|---|
| 抽样池（原） | 102 | **78** |
| 全量基线（现） | 211 | **94** |

**94 比 78 差 —— 而它更对。**

**多出的 16 条，是抽样池里根本没有的类型上的真实差异。
也就是说这个指标过去一直在**少报**，而「78」在报表上看起来比「94」好。**

**所以「形状」这个数变差，是判据 (a) 的距离**变远**了 16 条 —— 正确方向上的变远。**

### 四、这次改的是调用方，不只是工具

**R885 我加了 `--baseline` 开关就停了。而「工具支持更好的证据源」和「指标用了更好的证据源」是两件事。**

**这一轮改的是 `metrics_report.py` 那一行：**

```
-    ("成员形状差异", ["tools/shape_audit.py"], ["total mismatches"]),
+    ("成员形状差异", ["tools/shape_audit.py", "--baseline"], ["total mismatches"]),
```

**一行。而它让 `METRICS.md` 的两处数字（L23 与 L218）从 78 变 94。**

### 五、验证

```
dump_accessors_v2.py  -> 2587 raw · 1275 (type,prop) · 508 types · Getter 950 / Setter 687 / Property 950
基线文件行数          -> 1275 + 15 行头
shape_audit.py --baseline -> evidence: baseline (211 types, kinds kept) · total mismatches 94
shape_audit.py            -> evidence: string pool (102 types, sampled)  · total mismatches 78
metrics_report.py         -> 成员形状差异 exit 0  {'total mismatches': '94'}
docs/METRICS.md L23/L218  -> 94
完整套件                  -> 1780 通过 / 0 失败 / 0 跳过
```

### 六、仍然 Unknown

- **那 94 条里有几条是真缺陷**：**Unknown** ——
  **工具只报「镜像有 Setter 证据而复刻件不是可写属性」，而其中一部分可能是 `ICommand` 的有意只读。
  代码里已有 `command` 例外，但例外表是否完整没查。**
- **抽样池该不该退役**：**Unknown** ——
  **它还有别的用途（`shape_audit.py` 的默认路径），而全量基线只覆盖访问器这一种形态。**
- **抽样池与全量的类型差（102 vs 211）里，少掉的那 109 个类型有没有别的证据源**：**Unknown。**

### 七、教训

**这一轮修的是**我自己三轮前引入的缺陷**，而它瞒了两轮，因为症状是「0 个不匹配」。**

**三层错有一个共同点：每一层我都停在了「知道了」。**
**知道种类丢了（R885 写了）、知道证据源是抽样（R885 写了）、知道该改调用方（没做）。**

**「知道了」和「改完了」之间那一步，是这三轮真正反复丢的东西。**
**而它是可以机械检查的：一个开关加了之后，问一句「谁该用它」。**
"""

VERDICT = """

---

## 第 886 轮：形状指标 78 → 94 —— 数字变差，而那是修正

### 三层错的完整链

| 轮 | 做错了什么 | 症状 |
|---|---|---|
| **R883** | Dump 时把 `(类型, 属性, 种类)` 压成 `(类型, 属性列表)` | **种类丢了 → 下游读不到 → 安静返回 0** |
| **R885** | 发现证据源是抽样池，但只加开关、**没改调用方** | 指标仍是 78 |
| **R886** | 重生成基线带种类 + 改 `metrics_report.py` | **78 → 94** |

**每一层都是上一层没走完的那一步。**

### 重生成的基线

```
1,275 行 (类型, 属性) · 508 类型 · Getter 950 · Setter 687 · Property 950
```

### 数字变化

| 证据源 | 类型数 | mismatches |
|---|---|---|
| 抽样池（原） | 102 | **78** |
| 全量基线（现） | 211 | **94** |

> **94 比 78 差 —— 而它更对。多出的 16 条是抽样池里根本没有的类型上的真实差异。
> 这个指标过去一直在**少报**，而「78」在报表上看起来比「94」好。**

**所以判据 (a) 的距离**变远**了 16 条 —— 是正确方向上的变远。**

### 这次改的是调用方，不只是工具

```
-    ("成员形状差异", ["tools/shape_audit.py"], ["total mismatches"]),
+    ("成员形状差异", ["tools/shape_audit.py", "--baseline"], ["total mismatches"]),
```

**一行，让 METRICS 两处数字从 78 变 94。**

### 仍然 Unknown

**那 94 条里有几条是真缺陷**（工具只报「镜像有 Setter 而复刻不是可写属性」，部分可能是 `ICommand` 的有意只读；例外表是否完整没查）·
**抽样池该不该退役** · **少掉的那 109 个类型有无别的证据源**

### 教训

> **这一轮修的是我自己三轮前引入的缺陷，而它瞒了两轮，因为症状是「0 个不匹配」。**
> **三层错有一个共同点：每一层我都停在了「知道了」。知道种类丢了、知道证据源是抽样、知道该改调用方 —— 都写了，都没做完。**
> **「知道了」和「改完了」之间那一步，是这三轮真正反复丢的东西。而它可以机械检查：一个开关加了之后，问一句「谁该用它」。**
"""

BACKLOG_ADD = """

## 判据 — 形状指标 **78 → 94**（R886，**改工具链三处**）

### 三层错的链

| 轮 | 错 | 症状 |
|---|---|---|
| R883 | `(类型,属性,种类)` 压成 `(类型,属性列表)` | 种类丢 → 下游安静返回 0 |
| R885 | 发现证据源是抽样，只加开关、**没改调用方** | 指标仍 78 |
| **R886** | 重生成带种类的基线 + 改 `metrics_report.py` | **78 → 94** |

### 改动

| 文件 | 改动 |
|---|---|
| `analysis/dump_accessors_v2.py` | 新建，每行 `(类型, 属性, 种类)` |
| `replica/docs/baseline/recovered_accessors_by_type.txt` | 重生成：**1,275 行 / 508 类型 / Getter 950 · Setter 687 · Property 950** |
| `tools/shape_audit.py` | `--baseline` 读新格式 |
| `tools/metrics_report.py` | `["tools/shape_audit.py", "--baseline"]` |

### 数字

| 证据源 | 类型 | mismatches |
|---|---|---|
| 抽样池 | 102 | 78 |
| **全量基线** | **211** | **94** |

**94 比 78 差而更对：多 16 条是抽样池没有的类型上的真实差异。判据 (a) 距离变远 16 条 = 正确方向的变远。**
**套件 1780 通过 / 0 失败。**

| 仍 Unknown | |
|---|---|
| 94 条里几条真缺陷 | 部分可能是 `ICommand` 有意只读；例外表完整性未查 |
| 抽样池该不该退役 | 全量基线只覆盖访问器一种形态 |
| 少掉的 109 个类型有无别的证据源 | 未查 |

**纪律**：**「知道了」和「改完了」之间那一步要机械检查 —— 加了开关就问「谁该用它」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R886", BLOCKER)
    ensure(RSTATUS, "R886", BLOCKER)
    ensure(RVERDICT, "第 886 轮", VERDICT)
    ensure(BACKLOG, "R886", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R886" not in h:
        h += ("\n## R886 补充 — 形状指标 **78 → 94**（**改工具链三处**）\n\n"
              "**三层错的链**：R883 压缩丢种类 → R885 只加开关没改调用方 → **R886 重生成带种类的基线 + 改 `metrics_report.py`**。\n"
              "**基线重生成**：1,275 行 (类型,属性) / 508 类型 / Getter 950 · Setter 687 · Property 950。\n"
              "**数字**：抽样池 102 types → 78 mismatches；**全量基线 211 types → 94**。**94 比 78 差而更对 —— 过去一�直在少报。**\n"
              "**套件 1780 通过 / 0 失败。**\n"
              "**纪律：「知道了」和「改完了」之间那一步要机械检查 —— 加了开关就问「谁该用它」。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R886"), (RSTATUS, "R886"), (RVERDICT, "第 886 轮"), (BACKLOG, "R886")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R886: the shape metric goes from seventy-eight to ninety-four, which is a correction and not a regression\n\n"
         "R885 found that the member-shape figure was computed from analysis/pe_strings.txt, a sampled dump holding one\n"
         " hundred and two types where the full inventory holds two hundred and eleven. It also found that my own R883\n"
         " baseline dropped the accessor kind, which made the setter check match nothing and report zero. Both findings\n"
         " were written down and neither was carried through: the tool gained a --baseline switch and the metric kept\n"
         " calling it without one.\n\n"
         "This round finishes the chain. The dump now emits one row per (declaring type, property) with the kinds kept:\n"
         " 1275 rows over 508 types, Getter 950, Setter 687, Property 950. shape_audit reads that format under\n"
         " --baseline, and metrics_report now passes the flag, so the published figure comes from the full inventory.\n\n"
         "The number moves from seventy-eight mismatches to ninety-four. It got worse and it got righter: the extra\n"
         " sixteen are real differences on types the sampled pool does not even contain, so the metric has been\n"
         " under-reporting all along and seventy-eight simply looked better in a table than ninety-four. Against\n"
         " criterion (a), where type-level gaps should reach zero, the distance has grown by sixteen -- in the correct\n"
         " direction.\n\n"
         "The three-round chain has one thing in common. At each step I stopped at knowing: knew the kind was dropped,\n"
         " knew the source was a sample, knew the caller should change. What kept getting lost is the step between\n"
         " knowing and finishing, and that step is mechanically checkable -- when a switch is added, ask who should use\n"
         " it.\n\n"
         "Unknown: how many of the ninety-four are genuine defects, since the check reports any member with Setter\n"
         " evidence that the replica does not expose as settable, and some of those are ICommand properties that are\n"
         " read-only by design -- the code has an exception for command already, and whether that list is complete is\n"
         " unchecked; whether the sampled pool should retire, since the full baseline covers only the accessor shape;\n"
         " and what other evidence might exist for the hundred and nine types the pool omits.\n\n"
         "Tool chain changed; no product code changed; suite green at 1780."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
