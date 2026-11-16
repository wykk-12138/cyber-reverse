"""Record R953: the 800-wiring estimate discounts, because some unreachable code is duplicate."""

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
### 「800 次接线」这个估算，第一次查看就**散了**（R953）

**R952 说缺口约 800 次接线，而依据是「复刻件有很多 async 没接上」。这一轮去数。**

```
src 里 async 方法: 538
  主类型无人引用的文件: 93 （其中含 async 的 26 个）
```

**而第一个被查看的文件就把估算打破了。**

### `Retail2Modules.cs` 的五个 module，**全是已注册 flow 的副本**

| Module | 重复的 flow | 已在 catalog |
|---|---|---|
| `CasioModule` | `CasioFlow` | ✅ |
| `JbHiFiModule` | `JbHiFiFlow` | ✅ |
| `PocketGamesModule` | `PocketGamesFlow` | ✅ |
| `SuperswipeModule` | `SuperswipeFlow` | ✅ |
| `WarhammerModule` | `WarhammerFlow` | ✅ |

> **而 `StoreModuleCatalog.CreateAll()` 返回 `IStoreModule[]`，module 类**正好**符合那个接口 ——
> 所以把它们加进去**能编译、能跑**，而它会让 `Casio` 在 catalog 里出现**两次**（一次 flow、一次 module）。
> **那是行为错误，不是对等收益。****

### 所以不可达的代码分两种，而我只估了第一种

| 种类 | 该做什么 |
|---|---|
| **未接上**（有独立价值） | 接线 |
| **重复品**（和已注册的等价） | **删，不是接** |

> **而「800 次接线」把两者算成了一种。而区分它们的工作，正是这一轮真正的事 ——
> 而它不能靠数名字，只能**逐个看那个类是不是已经有一个等价的已注册项**。**

### 而 538 这个数也不能直接用

**它是 `async` 关键字的出现次数，不是「未接的 async 方法数」。
93 个可疑文件里 26 个含 async —— 而那 26 个里已经有一个是纯重复。**

### 数字

| 度量 | R952 | **R953** |
|---|---|---|
| 套件 | 2093 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,781 | **173,781（未改产品代码）** |
| **纯重复 module** | 未查 | **5** |

### 教训

> **一个估算的第一次具体查看，往往不是把它细化，是把它**否掉**。
> 而 R952 那个「≈800」是从一个 n=1 的增量和一句 Inference 乘出来的 ——
> 它读起来像一个计划，而它从来没有被任何一个具体文件检验过。**
> **而检验它花了不到十分钟，代价是**那个估算不再可用**。
> 而那比继续按它做 800 次接线便宜得多。**
"""

if "「800 次接线」这个估算" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 953 轮：「800 次接线」这个估算，第一次查看就散了

### 数字

```
src async 方法 538 · 主类型无人引用的文件 93（含 async 26）
```

### 而第一个被查看的文件打破了估算

**`Retail2Modules.cs` 的五个 module 全是已注册 flow 的副本：**
`CasioModule`→`CasioFlow` · `JbHiFiModule` · `PocketGamesModule` · `SuperswipeModule` · `WarhammerModule`

> **`StoreModuleCatalog.CreateAll()` 返回 `IStoreModule[]`，module 类正好符合 ——
> 加进去能编译能跑，而它会让 `Casio` 在 catalog 里出现**两次**。
> **那是行为错误，不是对等收益。**

### 不可达的代码分两种

| 种类 | 该做什么 |
|---|---|
| **未接上**（独立价值） | 接线 |
| **重复品** | **删，不是接** |

> **「800 次接线」把两者算成了一种。而区分它们不能靠数名字，
> 只能逐个看那个类是不是已经有一个等价的已注册项。**

### 而 538 也不能直接用

**它是 `async` 关键字的出现次数，不是「未接的 async 方法数」。93 个可疑文件里 26 个含 async，而其中一个已确认是纯重复。**

### 数字

| 度量 | R952 | **R953** |
|---|---|---|
| 套件 | 2093 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,781 | **173,781（未改产品代码）** |
| 纯重复 module | 未查 | **5** |

### 教训

> **一个估算的第一次具体查看，往往不是把它细化，是把它**否掉**。
> R952 的「≈800」是从一个 n=1 的增量和一句 Inference 乘出来的 ——
> 它读起来像一个计划，而它从来没有被任何一个具体文件检验过。
> **检验它花了不到十分钟，代价是那个估算不再可用 —— 而那比按它做 800 次接线便宜得多。**
"""

BACKLOG_ADD = """

## 判据 (c) — 「800 次接线」估算作废；不可达分两种（R953，**+4 用例**）

### 扫描

**538 async · 93 个主类型无人引用的文件（26 含 async）**

### 第一种就是重复品

**`Retail2Modules.cs` 五个 module 全重复已注册 flow：Casio/JbHiFi/PocketGames/Superswipe/Warhammer**

### 两类必须分开

| 种类 | 处理 |
|---|---|
| 未接上 | 接线 |
| 重复品 | 删 |

### `DuplicateModuleAuditTests`（4 例）

**五对 module↔flow 且 flow 确实在 catalog · module 未注册且必须不注册 · 规则「不可达 ≠ 未接」· 扫描数字**

### 数字

**套件 2093 → 2097 · 陈旧度 0/0 · 函数数 173,781（未改产品代码）· 纯重复 module 5**

| 仍 Unknown | |
|---|---|
| 93 个里还剩几个是重复品 | 未逐个查 |
| 真正「未接上」的有多少 | 未知，取决于上一个 |
| 删重复品是否动函数数 | 应该不动（它们本来不在产物） |

**纪律**：一个估算的第一次具体查看，往往不是把它细化，是把它否掉。
"""

BLOCKER = """

---

## 377. 「800 次接线」估算作废；不可达分两种

> R953。**+4 用例，未改产品代码。** 套件 **2097 通过 / 0 失败 / 0 跳过**。

### 一、扫描

```
src async 方法 538
主类型无人引用的文件 93（含 async 26）
```

### 二、第一个被查看的文件打破估算

**`Retail2Modules.cs` 五个 module 全是已注册 flow 的副本：**

| Module | 重复 |
|---|---|
| `CasioModule` | `CasioFlow` |
| `JbHiFiModule` | `JbHiFiFlow` |
| `PocketGamesModule` | `PocketGamesFlow` |
| `SuperswipeModule` | `SuperswipeFlow` |
| `WarhammerModule` | `WarhammerFlow` |

**`CreateAll()` 返回 `IStoreModule[]`，module 类正好符合 → 加进去能编译能跑，
而 `Casio` 会在 catalog 里出现两次 → **行为错误，不是对等收益**。**

### 三、两类必须分开

| 种类 | 处理 |
|---|---|
| 未接上（独立价值） | 接线 |
| 重复品（等价于已注册） | **删** |

**「800 次接线」把两者算成一种。**

### 四、538 也不能直接用

**是 `async` 关键字出现次数，不是「未接 async 方法数」。**

### 五、数字

| 度量 | R952 | R953 |
|---|---|---|
| 套件 | 2093 | **2097** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,781 | **173,781（未改产品代码）** |
| **纯重复 module** | 未查 | **5** |

### 六、验证

```
grep 'class \w*Module' Retail2Modules.cs -> 5 个
grep 'new \w*Flow(' Registry.cs          -> 五个对应 flow 全在
test --filter DuplicateModuleAuditTests  -> 4 通过
metrics_report.py                        -> 2097 通过 / 0 失败
```

### 七、仍然 Unknown

- **93 个里还剩几个重复品**：**Unknown** —— 未逐个查。
- **真正「未接上」的有多少**：**Unknown** —— 取决于上一个。
- **删重复品是否动函数数**：**Inference** —— 应该不动，它们本来不在产物。

### 八、教训

**一个估算的第一次具体查看，往往不是把它细化，是把它否掉。**

**R952 的「≈800」是从一个 n=1 的增量和一句 Inference 乘出来的 —— 它读起来像计划，而从没被任何具体文件检验。**

**检验它花了不到十分钟，而那比按它做 800 次接线便宜得多。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R953", BLOCKER)
    ensure(RSTATUS, "R953", BLOCKER)
    ensure(RVERDICT, "第 953 轮", VERDICT)
    ensure(BACKLOG, "R953", BACKLOG_ADD)

    note = (
        "\n## R953 补充 — 「800 次接线」估算作废；不可达分两种（+4 用例，套件 2097）\n\n"
        "扫描：538 async · 93 个主类型无人引用的文件（26 含 async）。\n\n"
        "第一个被查看的文件就打破了估算：Retail2Modules.cs 五个 module 全是已注册 flow 的副本"
        "（Casio/JbHiFi/PocketGames/Superswipe/Warhammer）。CreateAll() 返回 IStoreModule[]，"
        "module 类正好符合 → 加进去会让 Casio 在 catalog 里出现两次 = 行为错误。\n\n"
        "两类必须分开：未接上（接线）vs 重复品（删）。「800 次接线」把两者算成一种。\n"
        "538 是 async 关键字出现次数，不是未接方法数。\n\n"
        "数字：套件 2093 → 2097 · 陈旧度 0/0 · 函数数 173,781（未改产品代码）· 纯重复 module 5。\n\n"
        "纪律：一个估算的第一次具体查看，往往不是把它细化，是把它否掉。\n\n"
        "下一轮：逐个查 93 个可疑文件里哪些是重复品（先删重复，再谈接线）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R953" not in h:
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h + note)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R953"), (RSTATUS, "R953"), (RVERDICT, "第 953 轮"), (BACKLOG, "R953")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R953: the eight-hundred-wiring estimate dissolved on its first concrete look\n\n"
         "R952 put the gap at roughly eight hundred wirings, multiplying a single sample's gain by a guess that much of the\n"
         " replica is unwired. This round went to count. There are 538 async methods in source and ninety-three files whose\n"
         " main type nothing outside references, twenty-six of which contain async -- and the first file examined ended the\n"
         " estimate.\n\n"
         "Retail2Modules.cs declares five module classes, and all five duplicate stores StoreModuleCatalog already registers\n"
         " as flows: Casio, JbHiFi, PocketGames, Superswipe and Warhammer. CreateAll returns IStoreModule instances and a\n"
         " module fits that interface, so adding them compiles and runs -- and it would put Casio in the catalogue twice,\n"
         " once as a flow and once as a module. That is a behavioural error rather than a parity gain.\n\n"
         "So unreachable code is two kinds, and the estimate treated them as one. Code that is unwired has independent\n"
         " value and should be connected; code that duplicates something already registered should be deleted. Telling\n"
         " them apart cannot be done by counting names, only by checking whether an equivalent registered item already\n"
         " exists for each.\n\n"
         "The 538 figure is also not what it looks like: it counts occurrences of the async keyword rather than unwired async\n"
         " methods, and of the twenty-six suspect files that contain async, one is already confirmed pure duplication.\n\n"
         "Figures: suite 2093 to 2097, freshness zero, function count unchanged at 173,781 since no product code changed,\n"
         " and five duplicate modules now pinned by a test that will fail if a future round wires one.\n\n"
         "Unknown: how many of the ninety-three are duplicates, which was not checked one by one; how many are genuinely\n"
         " unwired, which depends on that; and whether deleting the duplicates moves the count, inferred as no since they\n"
         " were never in the artifact.\n\n"
         "The lesson is that an estimate's first concrete look usually does not refine it, it refutes it. The eight hundred\n"
         " came from multiplying one sample by an inference and reading like a plan, and no single file had ever been\n"
         " checked against it. Checking took ten minutes and cost the estimate its life, which is far cheaper than\n"
         " performing eight hundred wirings on its authority.\n\n"
         "Tests added; no product code changed; suite green at 2097."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()