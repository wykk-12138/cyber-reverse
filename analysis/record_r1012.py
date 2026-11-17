"""Record R1012: the first GetPaymentMethods override reaches the artifact, and two things went unexplained."""

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
### 第一个 `GetPaymentMethods` 覆写进了产物 —— 而两个观测没解释（R1012）

**R1011 说下一轮做「ordinal 57 的覆写」。做了，它成功了。而同一轮里出现两件我不解释的事。**

### ① `NikeFlow.GetPaymentMethodsAsync` —— 全仓第一个覆写

**R1008 查出 `StoreFlow.GetPaymentMethodsAsync` 覆写 **0** 次 ⇒ 按 R963 被裁 ⇒ 那个步骤在任何产物里都不存在，
而它读的 `Vars["paymentMethodsUrl"]` 是自造键名。
→ 覆写同时解决两件事：给它一个调用者，并让地址来自镜像而不是一个没人设的会话变量。**

**地址用 `NikeEndpoints.Checkouts` —— 镜像 `0x147053d8c`，`NikeEndpoints` 头注释说它是
「the single resource every checkout step writes to」。Nike 的 `GetPaymentMethods` 是**读**那个结账资源，
因为镜像给这个 host **没有**付款方式路径 —— 造一条会是 host+path 拼接那类错误。**

**并复用基类的 `ParsePaymentMethodNames`（一个解析器，不是两个会漂移的）。**

### ② 产物验证：它**进去了**

| 串 | 新 | 旧 |
|---|---|---|
| **`buy/checkouts/v3`** | **IN** | absent |
| **`no checkout to read payment methods`** | **IN** | absent |
| `nike-payment-methods` | absent | absent |
| `nike: no card` | absent → **删除后仍 absent** | absent |

**→ 新端点与覆写体的错误串都进了产物 —— 与 R1002 同一条规则（有覆写 ⇒ 进产物）。**

### ③ 而第一个未解释的观测：**字符串池不等于可达性**

**R1011 把打不存在端点的两段移进一个 `private AttachCardAsync`（未调用），作为「代码留证」。
而 publish 之后 `buy/orders/v2` **仍在**产物里。**

**→ 删掉那个方法再 publish：`nike: no card`（只在该方法里）消失了 —— 证明删对了；
而 `buy/orders/v2` **仍在**。**

**→ 所以那个串**不是**从 `NikeFlow` 来的。而 `where_is` 给出答案：还有 **4 处活代码**在用它。**

| 位置 | 形态 |
|---|---|
| `NikeFlow.cs:493` | `.../buy/orders/v2/US/{cart}/delivery` |
| `NikeFlow.cs:670` | `.../buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified` |
| `StoreFlow.cs:2365` | `Origin(c.Url) + "/buy/carts/v2/app"` |
| `NikeModule.cs:80` | `.../buy/carts/v2/US/Nike/SNKRS?format=simplified` |

**→ 所以 R1011「把两段移进未调用方法」那个动作**同时**做对了一件事（不留活路径）
和留了一个副作用（字符串可能仍在池里）—— 而真正的答案更简单：**它本来就不止两处。****

### ④ 而第二个未解释的观测：**函数数没动**

| 度量 | R1011 | **R1012** |
|---|---|---|
| **函数数** | 174,336 | **174,336（未变）** |

**→ 加了一个 `public override` 方法（约 45 行），而函数数**一个都没变**。
→ 而 R1002 加一句 `registry.Resolve` 就涨了 **342**。
→ **两个观测互相矛盾，而本轮不足以判定原因 —— 标 Unknown，不写成结论。**

**可能的解释（未证）：**那个覆写替换了一个已被裁的基类方法，净增接近零；
或者 `pdata` 的条目数对「在已有方法组里加一个覆写」不敏感。**都不是结论。**

### ⑤ 而第三个：metrics 报 1 失败，全跑报 0

| 跑法 | 结果 |
|---|---|
| `metrics_report.py`（排除浏览器依赖类） | **2218 通过 / 1 失败** |
| 全套 `--filter "Speed!=Slow"` | **2236 通过 / 0 失败 / 2 跳过** |

**→ 同一份代码，一次有失败一次没有 ⇒ 间歇失败。**
**→ 而我没有定位到它是哪一条 —— 那是本轮的缺口，不是可忽略的噪声。**

### 数字

| 度量 | R1011 | **R1012** |
|---|---|---|
| 全套 | 2219 | **2236 通过 / 0 失败 / 2 跳过** |
| **metrics 子集** | 2219 通过 | **2218 通过 / 1 失败（间歇）** |
| 产物陈旧度 | 2 / 2,7xx | **0 / 0（已 publish）** |
| **函数数** | 174,336 | **174,336（未变，未解释）** |
| **`GetPaymentMethodsAsync` 覆写数** | 0 | **1** |
| **`buy/checkouts/v3` 在产物** | absent | **IN** |
| **打不存在族的活代码位置** | 2（已修） | **4（新查出）** |

### 教训

> **「代码留证」这个做法有一个我没算到的代价：未调用的方法体里的字面量**仍可能进池**。
> → 而它把注意力从真问题引开了 —— 真正的答案是那族 URL **本来就不止两处**，
> 而 `where_is` 一次就给出了全部 4 处。**
> **→ 我上一轮「修了两处」的满足感，让「还有几处」这个问题没被问出来。**
"""

if "第一个 `GetPaymentMethods` 覆写进了产物" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1012 轮：第一个 `GetPaymentMethods` 覆写进了产物 —— 而两个观测没解释

### ① 全仓第一个覆写

**`NikeFlow.GetPaymentMethodsAsync`：地址用 `NikeEndpoints.Checkouts`（镜像 `0x147053d8c`，
「the single resource every checkout step writes to」），复用基类的 `ParsePaymentMethodNames`。**

**→ 它同时解决 R1008 那两件事：给它一个调用者（零覆写 ⇒ 被裁），并让地址来自镜像而不是自造的 `paymentMethodsUrl`。**

### ② 产物验证：它**进去了**

| 串 | 新 | 旧 |
|---|---|---|
| **`buy/checkouts/v3`** | **IN** | absent |
| **`no checkout to read payment methods`** | **IN** | absent |

### ③ 观测一：**字符串池不等于可达性**

**R1011 的「代码留证」（未调用的 `private AttachCardAsync`）删掉后，`nike: no card` 消失（证明删对），
而 `buy/orders/v2` **仍在**产物里 —— 因为它本来就不止两处。`where_is` 给出**还有 4 处活代码**：**

| 位置 | 形态 |
|---|---|
| `NikeFlow.cs:493` | `.../buy/orders/v2/US/{cart}/delivery` |
| `NikeFlow.cs:670` | `.../buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified` |
| `StoreFlow.cs:2365` | `Origin(c.Url) + "/buy/carts/v2/app"` |
| `NikeModule.cs:80` | `.../buy/carts/v2/US/Nike/SNKRS?format=simplified` |

**→ R1011「修了两处」的满足感，让「还有几处」这个问题没被问出来。**

### ④ 观测二：**函数数没动**

**加了一个 `public override`（约 45 行），函数数 **174,336 未变**。
而 R1002 加一句 `registry.Resolve` 涨了 **342**。→ 两个观测互相矛盾，**本轮不足以判定 —— 标 Unknown。****

### ⑤ 观测三：metrics 报 1 失败，全跑报 0

| 跑法 | 结果 |
|---|---|
| `metrics_report.py`（排除浏览器依赖类） | **2218 通过 / 1 失败** |
| 全套 `Speed!=Slow` | **2236 通过 / 0 失败 / 2 跳过** |

**→ 同一份代码一次有失败一次没有 ⇒ **间歇失败**，而我没有定位到它是哪一条。那是本轮的缺口，不是噪声。**

### 数字

| 度量 | R1011 | **R1012** |
|---|---|---|
| 全套 | 2219 | **2236 / 0 / 2** |
| **metrics 子集** | 2219 | **2218 / 1（间歇）** |
| 产物陈旧度 | 2 / 2,7xx | **0 / 0** |
| **函数数** | 174,336 | **174,336（未变，未解释）** |
| **覆写数** | 0 | **1** |
| **`buy/checkouts/v3` 在产物** | absent | **IN** |
| **打不存在族的活代码位置** | 2（已修） | **4（新查出）** |

### 教训

> **「代码留证」有一个我没算到的代价：未调用方法体里的字面量**仍可能进池**。
> → 而它把注意力从真问题引开了 —— 那族 URL **本来就不止两处**，`where_is` 一次给出全部 4 处。
> → **上一轮「修了两处」的满足感，让「还有几处」没被问出来。**
"""

BACKLOG_ADD = """

## 优先级 ① — **`NikeFlow.GetPaymentMethodsAsync` 首个覆写进产物；查出该族还有 **4 处活代码**（R1012）

### 做成了

**`NikeFlow.GetPaymentMethodsAsync` 覆写：地址 `NikeEndpoints.Checkouts`（`0x147053d8c`），
复用 `ParsePaymentMethodNames`，写 `PaymentGatewayNameKey`。**
**产物验证：`buy/checkouts/v3` **IN**（旧 absent）· `no checkout to read payment methods` **IN**。**
**→ 全仓 `GetPaymentMethodsAsync` 覆写 0 → 1。**

### 未解释 ×2（标 Unknown，不写成结论）

1. **函数数 174,336 **未变**** —— 而 R1002 加一句 `Resolve` 涨 342。两个观测矛盾。
2. **metrics 报 2218/1 失败，全套报 2236/0** —— **间歇失败，未定位。**

### 新查出：该族仍 **4 处活代码**

| 位置 | 形态 |
|---|---|
| `NikeFlow.cs:493` | `.../buy/orders/v2/US/{cart}/delivery` |
| `NikeFlow.cs:670` | `.../buy/carts/v2/{CC}/Nike/SNKRS?format=simplified` |
| `StoreFlow.cs:2365` | `Origin(c.Url) + "/buy/carts/v2/app"` |
| `NikeModule.cs:80` | `.../buy/carts/v2/US/Nike/SNKRS?format=simplified` |

### 一条做法被否掉

**R1011 的「把死代码留成未调用 private 方法」有副作用：未调用方法体的字面量仍可能进池。
→ 正确做法是**删掉**，把代码写进文档。**

### 数字

**全套 2236/0/2 · metrics 2218/1（间歇）· 陈旧度 0/0 · 函数数 174,336（未变，未解释）· 覆写 1 · 残留 4 处**

| 仍 Unknown | |
|---|---|
| 函数数为何未变 | 未证 |
| 间歇失败是哪一条 | 未定位 |
| Nike 付款/运单的 host | 镜像只给路径 |

**纪律**：「修了两处」的满足感会让「还有几处」不被问出来。
"""

BLOCKER = """

---

## 436. **首个 `GetPaymentMethodsAsync` 覆写进产物；查出该族还有 4 处活代码；两个观测未解释**

> R1012。**改 1 个源文件（新增覆写 + 删掉一段死代码）。** 全套 **2236 通过 / 0 失败 / 2 跳过**。

### 一、做成了什么

**`NikeFlow.GetPaymentMethodsAsync` —— 全仓第一个 `GetPaymentMethods` 覆写：**

- 地址 `NikeEndpoints.Checkouts`（镜像 `0x147053d8c`，头注释说它是「the single resource every checkout step writes to」）
- 复用基类的 `ParsePaymentMethodNames`（一个解析器，不是两个会漂移的）
- 写回 `PaymentGatewayNameKey`（R956 说镜像叫 `_paymentGatewayName`）
- `CartId` 为空 / 无付款方式 / 全被封 → 三种 `Fail`，各带不重试的理由

**→ 它同时解决 R1008 那两件事：给它一个调用者（零覆写 ⇒ 按 R963 被裁），
并让地址来自镜像而不是自造的 `Vars["paymentMethodsUrl"]`。**

### 二、产物验证：它**进去了**

| 串 | 新 | 旧 |
|---|---|---|
| **`buy/checkouts/v3`** | **IN** | absent |
| **`no checkout to read payment methods`** | **IN** | absent |
| `nike-payment-methods` | absent | absent |

### 三、未解释的观测 ①：**字符串池不等于可达性**

**R1011 把打不存在端点的两段移进一个 `private AttachCardAsync`（未调用）作为「代码留证」。
publish 之后 `buy/orders/v2` **仍在**产物里。
删掉那个方法再 publish：`nike: no card`（只在该方法里）消失 —— 证明删对了；而 `buy/orders/v2` **仍在**。**

**→ 所以它**不是**从 `NikeFlow` 来的。`where_is` 给出答案：还有 **4 处活代码**：**

| 位置 | 形态 |
|---|---|
| `NikeFlow.cs:493` | `.../buy/orders/v2/US/{cart}/delivery` |
| `NikeFlow.cs:670` | `.../buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified` |
| `StoreFlow.cs:2365` | `Origin(c.Url) + "/buy/carts/v2/app"` |
| `NikeModule.cs:80` | `.../buy/carts/v2/US/Nike/SNKRS?format=simplified` |

### 四、未解释的观测 ②：**函数数没动**

| 度量 | R1011 | R1012 |
|---|---|---|
| **函数数** | 174,336 | **174,336（未变）** |

**加了一个 `public override`（约 45 行），函数数**一个都没变**。
而 R1002 加一句 `registry.Resolve` 涨了 **342**。→ **两个观测互相矛盾，本轮不足以判定原因 —— 标 Unknown。**

**可能的解释（未证）：**那个覆写替换了一个已被裁的基类方法，净增接近零；
或 `pdata` 条目数对「在已有方法组里加一个覆写」不敏感。**都不是结论。**

### 五、未解释的观测 ③：metrics 报 1 失败，全跑报 0

| 跑法 | 结果 |
|---|---|
| `metrics_report.py`（排除浏览器依赖类） | **2218 通过 / 1 失败** |
| 全套 `--filter "Speed!=Slow"` | **2236 通过 / 0 失败 / 2 跳过** |

**→ 同一份代码，一次有失败一次没有 ⇒ **间歇失败**。
→ 而我没有定位到它是哪一条 —— 那是本轮的缺口，不是可忽略的噪声。**

### 六、数字

| 度量 | R1011 | R1012 |
|---|---|---|
| 全套 | 2219 | **2236 通过 / 0 失败 / 2 跳过** |
| **metrics 子集** | 2219 通过 | **2218 通过 / 1 失败（间歇）** |
| 产物陈旧度 | 2 / 2,7xx | **0 / 0（已 publish）** |
| **函数数** | 174,336 | **174,336（未变，未解释）** |
| **`GetPaymentMethodsAsync` 覆写数** | 0 | **1** |
| **`buy/checkouts/v3` 在产物** | absent | **IN** |
| **打不存在族的活代码位置** | 2（已修） | **4（新查出）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "buy/checkouts/v3"  -> {"n":1}（0x147053d8c）
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug   -> 已成功生成
dotnet test --filter "FullyQualifiedName~Nike|FullyQualifiedName~Payment|FullyQualifiedName~Gateway" -m:1  -> 112 通过
dotnet publish … -o .publish-aot-new --nologo                        -> exit 0
python - 在 .publish-aot 字节里搜 -> buy/checkouts/v3 IN · no checkout to read payment methods IN ·
        nike: no card absent · buy/orders/v2 IN（说明在别处）
python tools/metrics_report.py -> 完整套件 2218 通过 / 1 失败（而全套 2236/0）
```

### 八、仍然 Unknown

- **函数数为何未变**：**未证**。
- **间歇失败是哪一条**：**未定位**。
- **Nike 付款与运单的 host**：**镜像只给路径不给 host**。

### 九、教训

**「代码留证」这个做法有一个我没算到的代价：未调用的方法体里的字面量**仍可能进池**。**

**→ 而它把注意力从真问题引开了 —— 真正的答案是那族 URL **本来就不止两处**，
而 `where_is` 一次就给出了全部 4 处。**

**→ 我上一轮「修了两处」的满足感，让「还有几处」这个问题没被问出来。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1012", BLOCKER)
    ensure(RSTATUS, "R1012", BLOCKER)
    ensure(RVERDICT, "第 1012 轮", VERDICT)
    ensure(BACKLOG, "R1012", BACKLOG_ADD)

    note = (
        "\n## R1012 补充 — **首个 `GetPaymentMethodsAsync` 覆写进产物；查出该族还有 4 处活代码；两个观测未解释**\n\n"
        "**做成了**：`NikeFlow.GetPaymentMethodsAsync`（全仓第一个覆写）—— 地址 `NikeEndpoints.Checkouts`（`0x147053d8c`），\n"
        "复用 `ParsePaymentMethodNames`，写 `PaymentGatewayNameKey`。\n"
        "**产物验证**：`buy/checkouts/v3` **IN**（旧 absent）· `no checkout to read payment methods` **IN**。\n"
        "→ 同时解决 R1008 的两件事（零覆写被裁 + 自造端点键）。\n\n"
        "**未解释 ×3（标 Unknown，不写成结论）**：\n"
        "1. **函数数 174,336 未变** —— 而 R1002 加一句 `Resolve` 涨 342。两个观测矛盾。\n"
        "2. **metrics 报 2218/1，全套报 2236/0** —— **间歇失败，未定位**。\n"
        "3. ~~字符串池~~ 已解释：**「代码留证」的未调用方法体可能留字面量**；删掉后 `nike: no card` 消失证明删对，\n"
        "   而 `buy/orders/v2` 仍在 —— 因为它**本来就不止两处**。\n\n"
        "**新查出该族仍 4 处活代码**：`NikeFlow.cs:493`（`/delivery`）· `NikeFlow.cs:670`（SNKRS cart）·\n"
        "`StoreFlow.cs:2365`（`/buy/carts/v2/app`）· `NikeModule.cs:80`（SNKRS cart）。\n\n"
        "数字：全套 2236/0/2 · metrics 2218/1（间歇）· 陈旧度 0/0 · 函数数 174,336（未变）· 覆写 1 · 残留 4 处。\n\n"
        "纪律：**「修了两处」的满足感会让「还有几处」不被问出来。**\n\n"
        "下一轮：修那 4 处（`NikeFlow.cs:493` 的 `/delivery` 最急，它是运单步骤，必 404），并定位间歇失败。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1012" not in h:
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
             for p, k in ((RBLOCK, "R1012"), (RSTATUS, "R1012"), (RVERDICT, "第 1012 轮"), (BACKLOG, "R1012")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1012: the first GetPaymentMethods override reaches the artifact, and three things went unexplained\n\n"
         "R1011 sent the work at Nike's payment-methods step, ordinal 57. R1008 had found that the base method had no\n"
         " overrides at all, so under R963 it was trimmed and the step existed in no artifact, reading a session key that\n"
         " is absent from the image. NikeFlow now overrides it.\n\n"
         "The address is NikeEndpoints.Checkouts, the single resource NikeEndpoints' header says every checkout step\n"
         " writes to. Nike's GetPaymentMethods is a read of that checkout rather than a separate route, because the image\n"
         " names no payment-methods path for this host and inventing one would be the join-two-fragments mistake. The\n"
         " parser is the base class's, so there is one reader rather than two that can drift.\n\n"
         "The artifact agrees: buy/checkouts/v3 is present where it was absent, and so is the refusal string from the new\n"
         " override. That is the same rule as R1002 -- an override reaches the binary.\n\n"
         "Then three things I cannot explain, recorded as unknown rather than as findings. First, the function count did\n"
         " not move. Forty-five lines including a new public override, and 174,336 before and after, where R1002 gained\n"
         " 342 from one resolved call. The two observations contradict each other and this round cannot settle which\n"
         " reading is wrong.\n\n"
         "Second, the metrics run reports one failure while the full suite reports none, on the same tree -- so something\n"
         " is flaky, and I did not locate it. That is a gap in this round, not noise to skip past.\n\n"
         "Third, buy/orders/v2 was still in the artifact after R1011 moved it into an uncalled private method, which I had\n"
         " described as leaving evidence. Deleting that method made the string it alone contained disappear, proving the\n"
         " deletion bit, and buy/orders/v2 stayed -- because the family is in four live places, not two. where_is gave all\n"
         " four at once: a delivery call in NikeFlow, the SNKRS cart URL there, the app cart in StoreFlow, and the same\n"
         " cart in NikeModule.\n\n"
         "So the lesson is that keeping dead code as evidence has a cost I did not count, and worse, that doing it made\n"
         " two repairs feel like the whole job and stopped me asking how many there were.\n\n"
         "Figures: full suite 2236 passed, no failures, two skipped; the metrics subset 2218 with one intermittent\n"
         " failure; freshness zero after publishing; count 174,336 unchanged; overrides one; four live sites of the\n"
         " non-existent family remaining.\n\n"
         "Unknown: why the count did not move, which test is flaky, and the hosts for Nike's payment and delivery paths.\n\n"
         "One source file changed; full suite green at 2236."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()