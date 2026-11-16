"""Record R897: where_is was case-sensitive, which nearly produced a wrong correction."""

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

MARK = "where_is` 原来分大小写"

TABLE = """
### `where_is` 原来分大小写 —— 它差点让我推翻一个正确的结论（R897）

**目标：补 Vans 那 3 个端点（R896 报 `www.vans.com` 0/3）。第一步就差点走错。**

### 差点走错的那一步

**按 §2.7c 跑 `where_is Vans` —— 返回**2 个文件，全是 docs，实现组 0 个**。**

**于是下一步的判断是：R894 说「Vans 模块在」是错的，Vans 根本没有模块。**

**而真相是**大小写** —— 实现里写 `"vans"`（小写 site id）。**

### 改了默认

```
before:  区分大小写
after :  默认不分，--case 才严格
```

| 调用 | 文件数 | 内容 |
|---|---|---|
| 默认（改后） | **5** | `DemandwareControllers.cs` 2 · `DemandwareControllerTests.cs` 2 · docs 1 |
| `--case` | 2 | 回到旧的「只有 docs」 |

**理由写进 `--case` 的 help：一个概念会以类型名、变量名、字符串字面量、常量四种形式出现，四种都是命中。**

### 所以 R894 那半句是对的

| 主张 | 判断 | 证据 |
|---|---|---|
| 「Vans 的模块在」 | **对** | `DemandwareControllers.cs` 的 site id 表含 `"vans"`；`DemandwareControllerTests.cs` 2 条 |
| 「端点不在」 | **对** | `cart/v1` · `cart/v2` · `products/v2` 三个族一条常量都没有 |

**0/3 是真缺口，不是「Vans 整个不存在」—— 两者对下一步的答案完全不同。**

### 同一串里的第三次

| 轮 | 默认值错 | 怎么发现的 |
|---|---|---|
| R884 | `where_is` 默认子串 | 编译报 CS0101 |
| R885 | `shape_audit` 默认读抽样池 | 换证据源 |
| **R897** | **`where_is` 默认分大小写** | **顺手多查了一次全库字面量** |

**三次共同点：我都准备把工具输出当结论了。而三次发现都不是「按计划查的」—— 都是某个动作的副作用。**
"""

VERDICT = """

---

## 第 897 轮：`where_is` 分大小写 —— 它差点让我推翻一个正确的结论

**目标：补 Vans 那 3 个端点。第一步 `where_is Vans` 只返回 2 个 docs 文件，实现组 0 个。**

**我的下一步判断是：R894 说「Vans 模块在」是错的。而真相是大小写 —— 实现里写 `"vans"`。**

### 改了默认

```
before:  区分大小写
after :  默认不分，--case 才严格
```

| 调用 | 文件数 |
|---|---|
| 默认（改后） | **5**：`DemandwareControllers.cs` 2 · `DemandwareControllerTests.cs` 2 · docs 1 |
| `--case` | 2：只有 docs |

### R894 那半句是对的

| 主张 | 判断 | 证据 |
|---|---|---|
| 「Vans 的模块在」 | **对** | site id 表含 `"vans"`；`DemandwareControllerTests.cs` 2 条测试 |
| 「端点不在」 | **对** | `cart/v1` `cart/v2` `products/v2` 一条常量都没 |

> **所以 0/3 是真缺口，不是「Vans 整个不存在」—— 两者对下一步的答案完全不同。**

### 同一串里的第三次

| 轮 | 默认值错 | 怎么发现的 |
|---|---|---|
| R884 | `where_is` 默认子串 | 编译报 CS0101 |
| R885 | `shape_audit` 默认读抽样池 | 换证据源 |
| **R897** | **`where_is` 默认分大小写** | **顺手多查了一次全库字面量** |

**三次共同点：我都准备把工具输出当结论了。而三次发现都不是「按计划查的」—— 都是某个动作的副作用。**

### 仍然 Unknown

**Vans 那 3 个端点该不该补**（还差每条的具体路径，R895 的路径级判据不能只看族名）·
**还有多少标识符因大小写被判成「不存在」**（回溯审计，非本轮）· **`where_is` 还有别的默认值错吗**

### 教训

> **这一轮我准备写下「R894 那句是错的」。而它是**对的**。**
> **那不是判断失误 —— 推理链在工具输出上是自洽的。错的是**我把一个区分大小写的搜索当成了穷举**。**
> **R884 之后我给 `where_is` 加了整词默认，理由是「工具默认值本身可能是陷阱」。
> 这一轮证明那句话还成立：**修了一个默认值，不等于修完了所有默认值**。**
"""

BACKLOG_ADD = """

## 方法 — `where_is` 默认改为不分大小写（R897）

### 它差点让我推翻一个正确的结论

**`where_is Vans` → 2 个文件全是 docs → 我准备判「Vans 无模块、R894 错」。实际实现写 `"vans"` 小写。**

```
before: 区分大小写
after : 默认不分, --case 才严格
```

**改后 5 文件（`DemandwareControllers.cs` 2 · `DemandwareControllerTests.cs` 2 · docs 1）；`--case` 回到 2。**

### R894 对：0/3 是真缺口

**「模块在」= site id `"vans"` + 2 条测试；「端点不在」= 3 个族一条常量都没。**
**「Vans 整个不存在」与「模块在端点缺」对下一步的答案完全不同。**

### 同一串第三次默认值错误

| 轮 | 默认值错 | 怎么发现的 |
|---|---|---|
| R884 | 子串 | 编译报 CS0101 |
| R885 | 抽样池 | 换证据源 |
| **R897** | **大小写** | **顺手全库搜字面量** |

**→ 三次都不是按计划查出来的，都是副作用动作；三次我都准备把工具输出当结论。**

| 仍 Unknown | |
|---|---|
| Vans 3 个端点该不该补 | 还差每条具体路径 |
| 多少标识符因大小写被误判 | 回溯审计 |
| `where_is` 还有别的错默认吗 | 同批工具第三次 |

**纪律**：**修了一个默认值，不等于修完了所有默认值。**
"""


BLOCKER = """

---

## 321. `where_is` 分大小写 —— 它差点让我推翻一个正确的结论

> R897。**改工具默认值，未改产品代码。** 套件沿用 **1783 通过 / 0 失败**。

### 一、差点走错的那一步

**目标：补 Vans 那 3 个端点（R896 报 0/3）。第一步按 §2.7c 跑 `where_is Vans` ——
返回 2 个文件全是 docs，实现组 0 个。**

**我的下一步判断是：R894 的「Vans 模块在、端点不在」错了，Vans 根本没有模块。**

**而真相是大小写：实现里写 `"vans"`（小写 site id）。**

### 二、修了默认

```
before:  区分大小写
after :  默认不分，--case 才严格
```

| 调用 | 文件数 |
|---|---|
| 默认（改后） | **5**：`DemandwareControllers.cs` 2 · `DemandwareControllerTests.cs` 2 · docs 1 |
| `--case` | 2：只有 docs |

### 三、R894 那半句是对的

| 主张 | 判断 | 证据 |
|---|---|---|
| 「Vans 的模块在」 | **对** | site id 表含 `"vans"`；`DemandwareControllerTests.cs` 2 条测试 |
| 「端点不在」 | **对** | `cart/v1` `cart/v2` `products/v2` 一条常量都没 |

**所以 0/3 是真缺口，不是「Vans 整个不存在」。**

### 四、同一串里的第三次

| 轮 | 默认值错 | 症状 | 怎么发现的 |
|---|---|---|---|
| R884 | `where_is` 子串 | 55 个假命中 | 编译报 CS0101 |
| R885 | `shape_audit` 抽样池 | 102 vs 211 类型 | 换证据源 |
| **R897** | **`where_is` 大小写** | **实现存在却报「只在 docs」** | **顺手全库搜字面量** |

**三次共同点：我都准备把工具输出当结论了。三次发现都不是按计划查的 —— 都是某个动作的副作用。**

### 五、验证

```
where_is Vans          -> 5 files（含 DemandwareControllers.cs 2 / DemandwareControllerTests.cs 2）
where_is Vans --case   -> 2 files（只有 docs）
全库搜 "vans" 字面量    -> DemandwareControllers.cs:123 的 site id 表
本轮未改产品代码；套件 1783
```

### 六、仍然 Unknown

- **Vans 那 3 个端点该不该补**：**Unknown，而这是本轮本来要做的事。**
  **现在知道族名与宿主，但每条的具体路径还没取 —— R895 的路径级判据不能只看族名。**
- **还有多少标识符因大小写被判成「不存在」**：**Unknown** —— 前者几十轮 `where_is` 全是区分大小写，可重扫，但那是回溯审计。
- **`where_is` 还有别的默认值错吗**：**Unknown** —— 同一批工具里的第三次。

### 七、教训

**这一轮我准备写下「R894 那句是错的」。而它是**对的**。**

**那不是判断失误 —— 推理链在工具输出上是自洽的。错的是**我把一个区分大小写的搜索当成了穷举**。**

**R884 之后我给 `where_is` 加了整词默认，理由是「工具默认值本身可能是陷阱」。
这一轮证明那句话还成立：**修了一个默认值，不等于修完了所有默认值**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R897", BLOCKER)
    ensure(RSTATUS, "R897", BLOCKER)
    ensure(RVERDICT, "第 897 轮", VERDICT)
    ensure(BACKLOG, "R897", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R897" not in h:
        h += ("\n## R897 补充 — `where_is` 分大小写（**改工具默认，未改产品代码**）\n\n"
              "**`where_is Vans` 只返回 docs（实现组 0）→ 我差点判「Vans 无模块、R894 错了」。实际实现写 `\"vans\"` 小写。**\n"
              "**改默认**：`默认不分大小写 / --case 才严格`。改后 5 文件（`DemandwareControllers.cs` 2 · `DemandwareControllerTests.cs` 2）。\n"
              "**R894 那半句对**：「模块在」（site id + 2 条测试）·「端点不在」（3 个族一条常量都没）→ **0/3 是真缺口。**\n"
              "**同一串第三次默认值错误**（R884 子串 / R885 抽样池 / R897 大小写），**三次发现都靠副作用动作，没有一次是按计划查的。**\n"
              "**下一轮**：取 Vans 那 3 个族的具体路径（R895 的路径级判据要具体路径），然后补常量。\n")
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
             for p, k in ((RBLOCK, "R897"), (RSTATUS, "R897"), (RVERDICT, "第 897 轮"), (BACKLOG, "R897")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R897: where_is was case-sensitive, and it nearly made me overturn a conclusion that was right\n\n"
         "The round's goal was to add Vans's three endpoints, since R896 measured www.vans.com at zero of three. The\n"
         " first step, as section 2.7c requires, was to run where_is Vans, which returned two files, both documents,\n"
         " and nothing under implementation.\n\n"
         "From that I was about to conclude that R894's claim -- Vans has a module but no endpoints -- was wrong, and\n"
         " that Vans does not exist in the replica. It does. The implementation spells the site id vans in lowercase,\n"
         " so a case-sensitive search could not see it.\n\n"
         "The fix makes matching case-insensitive by default, with --case restoring strictness, and states the reason\n"
         " in the help text: one concept shows up as a PascalCase type, a camelCase variable, a lowercase string\n"
         " literal and a SCREAMING constant, and all four are hits. After the change the search finds five files,\n"
         " including DemandwareControllers.cs and DemandwareControllerTests.cs; under --case it finds the original\n"
         " two.\n\n"
         "So R894's half-sentence stands. Vans has a site id in DemandwareControllers.cs and two test assertions in\n"
         " DemandwareControllerTests.cs, and it has no constants for cart/v1, cart/v2 or products/v2. Zero of three is\n"
         " a real gap and not a store that is absent wholesale -- two readings that lead to completely different next\n"
         " steps, which is why the misreading mattered.\n\n"
         "This is the third time in this cluster that a tool default led me toward a wrong conclusion. R884's where_is\n"
         " matched substrings and produced fifty-five decoys that hid the type. R885's shape audit read a sampled pool\n"
         " and saw half the types. R897's where_is was case-sensitive and reported an existing module as existing only\n"
         " in documents. What is common to all three is that I was one step from treating tool output as a finding,\n"
         " and what is common to how each was caught is that none was caught by the planned check: they surfaced as\n"
         " side effects of some other action.\n\n"
         "Unknown: whether Vans's three endpoints should be added now, which is what the round set out to do and which\n"
         " still needs each path's exact tail rather than just the family name, since R895's path-level criterion\n"
         " cannot work from family names; how many identifiers have been written off as absent over previous rounds\n"
         " because of case, which is a retrospective audit rather than this round's work; and what other defaults in\n"
         " this tool set are wrong, this being the third such defect in the same small set.\n\n"
         "The lesson is that fixing one default does not finish the job. R884 added whole-word matching to this same\n"
         " script and wrote that a tool's default can be the trap; that sentence still held, because I had fixed one\n"
         " of its defaults and not the others.\n\n"
         "Tool default changed; no product code changed; suite carries at 1783."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
