"""Record R1013: the flaky failure does not reproduce, and Nike has no cart endpoint at all."""

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
### 间歇失败**不复现**；而 Nike **根本没有购物车端点**（R1013）

**R1012 留了三个未解释。这一轮关掉两个，第三个变成一条更清的结论。**

### ① 间歇失败：三次独立验证为 0

| 跑法 | 结果 |
|---|---|
| `metrics_report.py`（R1012 那次） | 2218 通过 / **1 失败** |
| 全套 `Speed!=Slow`（R1012） | 2236 / 0 / 2 |
| 全套 `Speed!=Slow`（本轮） | **2236 / 0 / 2** |
| **metrics 的精确 filter**（本轮，逐字照抄） | **2219 / 0 / 0** |
| `metrics_report.py`（本轮） | **2219 / 0 / 0** |

**→ 同一份代码、同一 filter，**四次跑出三次 0**，而失败那次正是我**同时在做 publish**。**
**→ 所以最可能是构建服务器 / 文件锁竞争，而不是用例本身。**
**→ 但它**不可复现**就不算已解决 —— 记为「四次中一次失败，之后三次为 0，保留观察」。**

### ② 而这一轮的取证给出一个比「4 处拼错」更准的结论

**R1012 查出 4 处活代码打 `buy/orders/v2` 或 `buy/carts/v2`。这一轮把 Nike 的**整个** `api.nike.com/buy`
清单取出来：**

```
0x147053c94  https://api.nike.com/buy/checkout_previews/v3/
0x147053d0c  https://api.nike.com/buy/checkout_previews_jobs/v3/
0x147053d8c  https://api.nike.com/buy/checkouts/v3/
0x147053df4  https://api.nike.com/buy/checkouts_jobs/v3/
（另 3 条在同族）

buy/carts    0
carts/v2     0
```

> **→ Nike **没有购物车端点**，也**没有订单端点**。它只有**一个 checkout 资源**加它的 preview 与两个 jobs。
> → 所以那 3 处「购物车」代码**不是端点拼错，是模型错**：它们假设有一个购物车资源，而原版没有。**

**那是 R87 那条注释真正说的事（「the real checkout surface is a single `buy/checkouts/v3/` resource
that each step writes to」）—— 而它被读成了「换一下 URL 前缀」。**

### ③ 所以这一轮只修了有据的那一处

**`NikeFlow.cs:493` 的 `/delivery`（运单地址）→ `NikeEndpoints.Checkouts + CartId`。**

**理由：镜像里那个资源是「每个 step 都写它」，而运单是一个 step。**请求体保持复刻件原来构造的** ——
镜像没有说运单写入长什么样，发明一个形状会在**新位置**犯同一个错。**

**→ 而另 3 处**没修**，因为它们需要**行为改动**（从「往购物车加」改成「建/写 checkout」），
而那要先确证 Nike 的 checkout 创建语义。**留作下一轮，写清理由。**

### ④ 而第三个未解释（函数数未变）仍未解

| 度量 | R1012 | **R1013** |
|---|---|---|
| 函数数 | 174,336 | **174,336（仍未变）** |

**→ 这一轮又改了 `NikeFlow.cs`（加注释 + 换 URL），函数数仍未动。
→ 而 R1012 加了一个 `public override` 也未动。
→ **所以「改 `NikeFlow` 不动函数数」已经是两次一致的观测** —— 那是一条**规律**，而不是矛盾：
`NikeFlow` 的方法大多**已被覆写并已在产物里**，改它们的身体不改变函数数。
→ **而 R1002 的 `+342` 是因为**从零拉进**了一整族新类，不是改一个已有方法。**
**→ 两个观测不再矛盾：一个是「改已可达的代码」，一个是「让不可达的代码变可达」。**

### 数字

| 度量 | R1012 | **R1013** |
|---|---|---|
| 套件（metrics filter） | 2218 / 1 失败 | **2219 / 0 / 0** |
| 全套 | 2236 / 0 / 2 | **2236 / 0 / 2** |
| 产物陈旧度 | 0 / 0 | **1 / 711（只改 NikeFlow）** |
| 函数数 | 174,336 | **174,336（两次一致，已解释）** |
| **Nike 的 buy 端点** | 已知 3 条 | **7 条，全 checkouts 家族** |
| **打不存在族的活代码** | 4 | **3（修了 `/delivery`）** |
| **间歇失败** | 未定位 | **四次中一次，之后三次为 0** |

### 教训

> **「4 处拼错了 URL」和「这 3 处假设了一个原版没有的资源」是两个不同大小的结论，
> 而它们的第一步取证动作是同一个：把那个 host 的**全部**字面量取出来。**
> **→ 我上一轮取的是「这几个族有没有」，得到「没有」；这一轮取的是「那这个 host 有什么」，
> 得到「只有一个 checkout 资源」。后者才说明了该怎么办。**
"""

if "间歇失败**不复现**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1013 轮：间歇失败不复现；而 Nike 根本没有购物车端点

### ① 间歇失败：三次独立验证为 0

| 跑法 | 结果 |
|---|---|
| `metrics_report.py`（R1012） | 2218 / **1 失败** |
| 全套（R1012） | 2236 / 0 / 2 |
| 全套（本轮） | **2236 / 0 / 2** |
| **metrics 精确 filter**（本轮） | **2219 / 0 / 0** |
| `metrics_report.py`（本轮） | **2219 / 0 / 0** |

**→ 同一份代码、同一 filter，四次三次为 0，而失败那次我**同时在做 publish**。
→ 最可能是构建服务器 / 文件锁竞争。**不可复现就不算已解决** —— 记「四次中一次，之后三次为 0」。**

### ② 而取证给出一个比「4 处拼错」更准的结论

```
0x147053c94  https://api.nike.com/buy/checkout_previews/v3/
0x147053d0c  https://api.nike.com/buy/checkout_previews_jobs/v3/
0x147053d8c  https://api.nike.com/buy/checkouts/v3/
0x147053df4  https://api.nike.com/buy/checkouts_jobs/v3/
buy/carts  0        carts/v2  0
```

> **→ Nike **没有购物车端点**，也**没有订单端点**。只有一个 checkout 资源 + preview + 两个 jobs。
> → 所以那 3 处「购物车」代码**不是端点拼错，是模型错** —— 它们假设了一个原版没有的资源。
> → 而 R87 那句「the real checkout surface is a single `buy/checkouts/v3/` resource that each step writes to」
> 被读成了「换一下 URL 前缀」，而它说的是**模型**。**

### ③ 所以这一轮只修有据的那一处

**`NikeFlow.cs:493` 的 `/delivery` → `NikeEndpoints.Checkouts + CartId`。
理由：那个资源是「每个 step 都写它」，运单是一个 step。请求体保持原样 —— 镜像没说运单写入长什么样，
发明形状会在**新位置**犯同一个错。**

**另 3 处**没修**：需要**行为改动**（从「往购物车加」变成「建/写 checkout」），要先确证 checkout 创建语义。**

### ④ 第三个未解释现在**解释了**

**「改 `NikeFlow` 不动函数数」已经**两次一致** ⇒ 那是规律，不是矛盾：
`NikeFlow` 的方法大多**已被覆写且已在产物里**，改它们的身体不改变函数数。
而 R1002 的 `+342` 是**从零拉进一整族新类**。**

> **两个观测不再矛盾：一个是「改已可达的代码」，一个是「让不可达的代码变可达」。**

### 数字

| 度量 | R1012 | **R1013** |
|---|---|---|
| metrics filter | 2218 / 1 | **2219 / 0 / 0** |
| 全套 | 2236 / 0 / 2 | **2236 / 0 / 2** |
| 产物陈旧度 | 0 / 0 | **1 / 711** |
| 函数数 | 174,336 | **174,336（已解释）** |
| **Nike buy 端点** | 已知 3 | **7，全 checkouts 家族** |
| **打不存在族的活代码** | 4 | **3** |
| **间歇失败** | 未定位 | **四次中一次，之后三次为 0** |

### 教训

> **「4 处拼错了 URL」和「这 3 处假设了一个原版没有的资源」是两个不同大小的结论，
> 而第一步取证动作相同：把那个 host 的**全部**字面量取出来。**
> **→ 上一轮我问「这几个族有没有」，得到「没有」；这一轮问「那这个 host 有什么」，
> 得到「只有一个 checkout 资源」。后者才说明了该怎么办。**
"""

BACKLOG_ADD = """

## 优先级 ① — **间歇失败不复现；Nike 无购物车端点（模型错非拼错）；修 `/delivery`；函数数未变已解释**（R1013）

### 间歇失败

**五次跑中一次失败，之后三次全 0（含 metrics 精确 filter 2219/0/0）。
失败那次我同时在做 publish ⇒ 最可能构建服务器竞争。**不可复现 ≠ 已解决**，保留观察。**

### Nike 的完整 buy 面（7 条，全 checkouts 家族）

```
checkout_previews/v3/  ·  checkout_previews_jobs/v3/  ·  checkouts/v3/  ·  checkouts_jobs/v3/  （另 3 条同族）
buy/carts 0  ·  carts/v2 0
```

**→ Nike **没有购物车端点、没有订单端点**。只有**一个 checkout 资源**（每个 step 写它）+ preview + jobs。
→ 那 3 处「购物车」代码**是模型错，不是端点拼错**。**
**→ R87 那句「the real checkout surface is a single `buy/checkouts/v3/` resource that each step writes to」
被读成了「换 URL 前缀」，而它说的是**模型**。**

### 修了什么

**`NikeFlow.cs:493` 的 `/delivery` → `NikeEndpoints.Checkouts + CartId`（有据：每个 step 写它）。
请求体保持原样 —— 镜像没说运单写入长什么样，发明形状会在新位置犯同一个错。**

**另 3 处未修：需行为改动（购物车 → checkout），需先确证 checkout 创建语义。**

### 「函数数未变」现在解释了

**两次一致 ⇒ 规律而非矛盾：`NikeFlow` 的方法多已覆写且已在产物里，改身体不改函数数。
R1002 的 `+342` 是**从零拉进一整族新类**。**

### 数字

**metrics 2219/0/0 · 全套 2236/0/2 · 陈旧度 1 / 711 · 函数数 174,336 · Nike buy 端点 7 · 活代码 4 → 3**

| 仍 Unknown | |
|---|---|
| Nike checkout 的创建语义 | 未取证（另 3 处要它） |
| 间歇失败的真实原因 | 不可复现 |

**纪律**：问「这个 host 有什么」比问「这几个族有没有」更能说明该怎么办。
"""

BLOCKER = """

---

## 437. **间歇失败不复现；Nike 无购物车端点（模型错）；修 `/delivery`；函数数未变已解释**

> R1013。**改 1 个源文件。** 套件 **2219 通过 / 0 失败**（metrics filter）· 全套 **2236 / 0 / 2**。

### 一、间歇失败：五次跑中一次，之后三次为 0

| 跑法 | 结果 |
|---|---|
| `metrics_report.py`（R1012 那次） | 2218 通过 / **1 失败** |
| 全套 `Speed!=Slow`（R1012） | 2236 / 0 / 2 |
| 全套 `Speed!=Slow`（本轮） | **2236 / 0 / 2** |
| **metrics 的精确 filter**（本轮，逐字照抄） | **2219 / 0 / 0** |
| `metrics_report.py`（本轮） | **2219 / 0 / 0** |

**→ 同一份代码、同一 filter，四次跑出三次 0，而失败那次正是我**同时在做 publish**。
→ 最可能是构建服务器 / 文件锁竞争，而不是用例本身。
→ 但**不可复现就不算已解决** —— 记为「五次中一次失败，之后三次为 0，保留观察」。**

### 二、而这一轮的取证给出一个比「4 处拼错」更准的结论

**把 Nike 的**整个** `api.nike.com/buy` 清单取出来：**

```
0x147053c94  https://api.nike.com/buy/checkout_previews/v3/
0x147053d0c  https://api.nike.com/buy/checkout_previews_jobs/v3/
0x147053d8c  https://api.nike.com/buy/checkouts/v3/
0x147053df4  https://api.nike.com/buy/checkouts_jobs/v3/
（另 3 条在同族）

buy/carts    0
carts/v2     0
```

**→ Nike **没有购物车端点**，也**没有订单端点**。它只有**一个 checkout 资源**加它的 preview 与两个 jobs。
→ 所以那 3 处「购物车」代码**不是端点拼错，是模型错**：它们假设有一个购物车资源，而原版没有。**

**→ 那是 R87 那条注释真正说的事（「the real checkout surface is a single `buy/checkouts/v3/` resource
  that each step writes to」）—— 而它被读成了「换一下 URL 前缀」。**

### 三、这一轮只修了有据的那一处

**`NikeFlow.cs:493` 的 `/delivery`（运单地址）→ `NikeEndpoints.Checkouts + CartId`。**

**理由：镜像里那个资源是「每个 step 都写它」，而运单是一个 step。
**请求体保持复刻件原来构造的** —— 镜像没有说运单写入长什么样，发明一个形状会在**新位置**犯同一个错。**

**→ 另 3 处**没修**，因为它们需要**行为改动**（从「往购物车加」改成「建/写 checkout」），
  而那要先确证 Nike 的 checkout 创建语义。留作下一轮，写清理由。**

### 四、而第三个未解释（函数数未变）现在解释了

| 度量 | R1012 | R1013 |
|---|---|---|
| 函数数 | 174,336 | **174,336（仍未变）** |

**→ 这一轮又改了 `NikeFlow.cs`，函数数仍未动；R1012 加了一个 `public override` 也未动。
→ **所以「改 `NikeFlow` 不动函数数」已经是两次一致的观测** —— 那是一条**规律**，不是矛盾：
  `NikeFlow` 的方法大多**已被覆写并已在产物里**，改它们的身体不改变函数数。
→ **而 R1002 的 `+342` 是因为**从零拉进**了一整族新类，不是改一个已有方法。**

**→ 两个观测不再矛盾：一个是「改已可达的代码」，一个是「让不可达的代码变可达」。**

### 五、数字

| 度量 | R1012 | R1013 |
|---|---|---|
| 套件（metrics filter） | 2218 / 1 失败 | **2219 / 0 / 0** |
| 全套 | 2236 / 0 / 2 | **2236 / 0 / 2** |
| 产物陈旧度 | 0 / 0 | **1 / 711（只改 NikeFlow）** |
| 函数数 | 174,336 | **174,336（两次一致，已解释）** |
| **Nike 的 buy 端点** | 已知 3 条 | **7 条，全 checkouts 家族** |
| **打不存在族的活代码** | 4 | **3（修了 `/delivery`）** |
| **间歇失败** | 未定位 | **五次中一次，之后三次为 0** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "api.nike.com/buy"  -> {"n":7}
python analysis/ida.py str "buy/carts"         -> {"n":0}
python analysis/ida.py str "carts/v2"          -> {"n":0}
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~Nike" -m:1                 -> 47 通过
dotnet test --filter "<metrics 的精确 filter>" -m:1                 -> 2219 / 0 / 0
python tools/metrics_report.py                                      -> 完整套件 exit 0  2219 / 0 / 0
```

### 七、仍然 Unknown

- **Nike checkout 的创建语义**：**未取证** —— 另 3 处要它才能改。
- **间歇失败的真实原因**：**不可复现** —— 五次中一次。

### 八、教训

**「4 处拼错了 URL」和「这 3 处假设了一个原版没有的资源」是两个不同大小的结论，
而它们的第一步取证动作是同一个：把那个 host 的**全部**字面量取出来。**

**→ 上一轮取的是「这几个族有没有」，得到「没有」；这一轮取的是「那这个 host 有什么」，
得到「只有一个 checkout 资源」。后者才说明了该怎么办。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1013", BLOCKER)
    ensure(RSTATUS, "R1013", BLOCKER)
    ensure(RVERDICT, "第 1013 轮", VERDICT)
    ensure(BACKLOG, "R1013", BACKLOG_ADD)

    note = (
        "\n## R1013 补充 — **间歇失败不复现；Nike 无购物车端点（模型错）；修 `/delivery`；函数数未变已解释**\n\n"
        "**间歇失败**：五次跑中一次，之后三次全 0（含 metrics 精确 filter **2219/0/0**）。失败那次我在同时 publish\n"
        "⇒ 最可能构建服务器竞争。**不可复现 ≠ 已解决**，保留观察。\n\n"
        "**Nike 的完整 buy 面 7 条，全 checkouts 家族**：`checkout_previews/v3/` · `..._jobs/v3/` · `checkouts/v3/` ·\n"
        "`checkouts_jobs/v3/`（另 3 条同族）。而 **`buy/carts` 0 · `carts/v2` 0**。\n"
        "→ **Nike 没有购物车端点、没有订单端点**，只有一个 checkout 资源 + preview + jobs。\n"
        "→ 那 3 处「购物车」代码**是模型错不是拼错**。而 R87 那句「single `buy/checkouts/v3/` resource that each step\n"
        "writes to」被读成了「换 URL 前缀」，它说的是**模型**。\n\n"
        "**修了有据的一处**：`NikeFlow.cs:493` `/delivery` → `NikeEndpoints.Checkouts + CartId`。请求体保持原样。\n"
        "**另 3 处未修**：需行为改动（购物车 → checkout），要先确证 checkout 创建语义。\n\n"
        "**「函数数未变」现在解释了**：两次一致 ⇒ 规律 —— `NikeFlow` 的方法多已覆写且已在产物里，改身体不改函数数。\n"
        "而 R1002 的 `+342` 是**从零拉进一整族新类**。**两者不矛盾：改已可达的代码 vs 让不可达的代码变可达。**\n\n"
        "数字：metrics 2219/0/0 · 全套 2236/0/2 · 陈旧度 1 / 711 · 函数数 174,336 · Nike buy 端点 7 · 活代码 4 → 3。\n\n"
        "纪律：**问「这个 host 有什么」比问「这几个族有没有」更能说明该怎么办。**\n\n"
        "下一轮：取证 Nike checkout 的创建语义，改那 3 处（购物车 → checkout）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1013" not in h:
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
             for p, k in ((RBLOCK, "R1013"), (RSTATUS, "R1013"), (RVERDICT, "第 1013 轮"), (BACKLOG, "R1013")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1013: the flaky failure does not reproduce, and Nike has no cart endpoint at all\n\n"
         "Three things were left unexplained last round. Two are now closed and the third turned out to be a rule rather\n"
         " than a contradiction.\n\n"
         "The intermittent failure does not reproduce. With the metrics filter copied verbatim the subset passes 2219\n"
         " with none failing, and a second metrics run agrees; the full suite passes twice as well. The only run that\n"
         " failed was the one where I was publishing at the same time, so the likeliest cause is contention over the\n"
         " build server rather than a test. Not reproducing is not the same as solved, so it stays on the record as one\n"
         " failure in five runs followed by three clean ones.\n\n"
         "The four live sites got sharper. Last round asked whether the two families exist and got zero. This round asked\n"
         " what that host has, and the answer reframes the problem: seven literals, all of them checkout_previews or\n"
         " checkouts with their jobs, and neither buy/carts nor carts/v2 anywhere. Nike has no cart endpoint and no order\n"
         " endpoint. Its model is one checkout resource that every step writes to, which is what NikeEndpoints' header has\n"
         " said since R87 -- and that sentence had been read as \"change the URL prefix\" when it is describing a model.\n\n"
         "So three of those sites are not misspelled addresses, they are code built on a resource that does not exist,\n"
         " and fixing them means changing behaviour rather than substituting a string. One of the four did have a\n"
         " defensible substitution: the delivery step now writes to the checkout resource, because a delivery step is a\n"
         " step and the image says every step writes there. The body stays as it was, since the image does not say what a\n"
         " delivery write contains and inventing a shape would repeat the same mistake somewhere new.\n\n"
         "The third puzzle resolves by repetition. The function count did not move again after editing NikeFlow, making it\n"
         " two observations that agree: an override was added and a URL changed, and the count stayed at 174,336 both\n"
         " times. That is a rule, not a contradiction -- NikeFlow's methods are largely already overridden and already in\n"
         " the artifact, so editing their bodies does not add functions. R1002's 342 came from pulling a whole family of\n"
         " classes in from nothing.\n\n"
         "Figures: metrics filter 2219 with no failures, full suite 2236 with two skipped, freshness one file and 711\n"
         " lines, count 174,336, seven Nike buy endpoints, live sites down from four to three, one flaky failure in five\n"
         " runs.\n\n"
         "Unknown: the checkout creation semantics the remaining three sites need, and the flaky failure's real cause.\n\n"
         "The lesson is that \"are these families present\" and \"what does this host have\" are different questions, and\n"
         " the second one tells you what to do about it.\n\n"
         "One source file changed; suite green at 2219 on the metrics filter and 2236 in full."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()