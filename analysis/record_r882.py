"""Record R882: the five Start*Flow share a blob with Pop Mart's draw steps, and what that does not prove."""

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
### 5 个 `Start*Flow` 与 Pop Mart 的抽签步骤**同一个字面量 blob**（R882）

**R880 说接 `FlowKind → StoreFlow` 需要「哪个站有哪个 `Start*Flow`」。把这把那一段完整读出来：**

```
14337b02a  Login_EnsureTaskAlive · CheckSession · Authorize · Authenticate · SubmitTwoFactor · GetToken
14337b55e  _cartId _itemId _visitorId _marketPlace _language _basePath _locationId _priceId
           _priceSnapshot _productPrice _shippingPrice _locationData _forter
           _paymentApprovalId _paymentUri _paypalToken _product _scope _state
           _twoFactorEnabled _redirectUrl _accountKasada
14337bda2  <Start>d__56
14337bdc4  <StartSignupFlow>d__57  <StartClearFlow>d__58  <StartInStoreFlow>d__59
           <StartPopNowFlow>d__60  <StartNormalFlow>d__61
14337be54  <SendTwoFactor>d__65    14337be6a  <Register>d__67
14337bf2d  <GetConfig>d__68  <GetSession>d__69   14337bf51  <Login>d__70  <Login_EnsureTaskAlive>d__71
14337bff7  <CanPlaceOrder>d__72  <FindProductMulti>d__73  <FindProduct>d__74
14337c042  <FindProductMultiInstore>d__75  <FindProductInstore>d__76  <ClearCart>d__77
```

**而 R871 认定的 `GetOrders>d__104` 在 `0x14337c7e5`，R849 的 `StartDrawFlow>d__115` 也在同一段。**

**所以同一个 blob 里有 ordinal 56 到 115+。**

### 这看起来像「这个类支持 5 种任务」，但不是

**一个字面量 blob 可以同时装**基类和派生类**的字面量 ——
NativeAOT 把方法名字面量集中放，不按类分块。**

**所以能说的只有：**

| 能说 | 不能说 |
|---|---|
| 5 个 `Start*Flow` 与 Pop Mart 的抽签步骤**在同一片字面量区** | **「Pop Mart 支持这 5 种任务」** |
| 这片区域有 ordinal 56–61 与 104–116+ | 「这是同一个类」 |
| 字段里有 `_accountKasada` 与 `_forter` | 「这个类属于哪个站」 |

**R878 的教训直接适用：位置相邻不是归属。而这次相邻的粒度是**blob**，比字符串更粗 —— 证据更弱，不是更强。**

### 而字段透露的东西仍然有用

| 字段 | 读法 |
|---|---|
| `_accountKasada` | **Kasada token 存在账号级**（不是请求级临时变量） |
| `_forter` | **Forter 风控 token 也在模型里** |
| `_marketPlace` · `_locationId` · `_locationData` · `_basePath` | **门店/市场模型** —— 与 `FindProductInstore` 一致 |
| `_paymentUri` · `_paypalToken` · `_paymentApprovalId` | 支付态 |

**`AntiBotVendors.cs` 把 Kasada 与 Forter 都列了，而 `GetKasada` 那一行的示例串是 `Nike-Kasada-Version`。
所以「Kasada 出现在这片的字段里」不指向唯一一个站。**

### 为什么没写映射表

**R880 说要建 `FlowKind × Store → StoreFlow`。这一轮查完，**证据不够**：

**要写「PopMart 支持 Normal/Clear/Signup/PopNow/InStore」，我需要「这 5 个 `Start*Flow` 的 ordinal
与 PopMart 的 ordinal 属于同一个类」的证据。而 blob 共享给不出这个。**

**所以映射表这一轮**不写**。写它就是拿 blob 相邻当归属，重犯 R876。**
"""

if "5 个 `Start*Flow` 与 Pop Mart 的抽签步骤**同一个字面量 blob**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R882 appended")

BLOCKER = """

---

## 306. 5 个 `Start*Flow` 与 Pop Mart 抽签步骤**同一片字面量区** —— 而这不够写映射表

> R882。未改产品代码。

### 一、读出来的完整段落

```
14337b02a  Login_EnsureTaskAlive · CheckSession · Authorize · Authenticate · SubmitTwoFactor · GetToken
14337b55e  _marketPlace _locationId _priceId _locationData _forter _paymentUri _paypalToken
           _twoFactorEnabled _redirectUrl _accountKasada …
14337bda2  <Start>d__56
14337bdc4  <StartSignupFlow>d__57 <StartClearFlow>d__58 <StartInStoreFlow>d__59
           <StartPopNowFlow>d__60 <StartNormalFlow>d__61
14337bff7  <CanPlaceOrder>d__72 <FindProductMulti>d__73 <FindProduct>d__74
14337c042  <FindProductMultiInstore>d__75 <FindProductInstore>d__76 <ClearCart>d__77
```

**而 `GetOrders>d__104` 在 `0x14337c7e5`、`StartDrawFlow>d__115` 也在同一段。**

**所以一个 blob 里有 ordinal 56–61 与 104–116+。**

### 二、看起来像「这个类支持 5 种任务」，但不是

**一个字面量 blob 可以同时装**基类与派生类**的字面量 ——
NativeAOT 把方法名字面量集中放，不按类分块。**

| 能说 | 不能说 |
|---|---|
| 5 个 `Start*Flow` 与 Pop Mart 抽签步骤**同一片字面量区** | **「Pop Mart 支持这 5 种任务」** |
| 这片有 ordinal 56–61 与 104–116+ | 「这是同一个类」 |
| 字段有 `_accountKasada` / `_forter` | 「这个类属于哪个站」 |

**R878 的教训适用，而这次相邻的粒度是 **blob**，比单条字符串更粗 ——
**证据更弱，不是更强。****

### 三、所以映射表不写

**R880 说下一步是 `FlowKind × Store → StoreFlow`。要写它，我需要
「这 5 个 `Start*Flow` 与 Pop Mart 的 ordinal 属于同一个类」的证据。blob 共享给不出。**

**写它就是拿 blob 相邻当归属 —— 重犯 R876。**
**所以这一轮**什么都没写**，而这是对的：一个没有证据的映射表比没有映射表更坏，
因为它会把「看起来接了」当成「接了」（R869 那条假成功的同族）。**

### 四、字段仍然给出了东西

| 字段 | 读法 |
|---|---|
| `_accountKasada` | **Kasada token 在账号级**，不是请求级临时量 |
| `_forter` | Forter token 也在模型里 |
| `_marketPlace` `_locationId` `_locationData` `_basePath` | **门店/市场模型**，与 `FindProductInstore` 一致 |
| `_paymentUri` `_paypalToken` `_paymentApprovalId` | 支付态 |

**但「哪些字段在这片」也不指向唯一一个站：`AntiBotVendors.cs` 的 `GetKasada` 行示例串是
`Nike-Kasada-Version`，而 Kasada 在这片字段里 —— 两者不构成「这是 Nike」。**

### 五、验证

```
idautils.Strings() @0x14337B000–0x14337CE00 -> 78 条，按地址序（完整列出）
  含 5 个 Start*Flow（ordinal 57–61）· Start d__56 · Register d__67 · FindProduct*Instore d__75-76
  字段段含 _accountKasada _forter _marketPlace _locationId
where_is FindProductInstore  -> 只在 docs（无实现）
where_is AccountKasada       -> 全仓无
where_is Forter              -> AntiBotVendors.cs 17 处（厂商表）
本轮未改产品代码
```

### 六、仍然 Unknown

- **那 5 个 `Start*Flow` 属于哪个类**：**Unknown** ——
  **需要 ordinal→类 的映射，而 blob 给不出。R504 那堵墙（描述符无 xref）大概率也挡这条。**
- **16 个方法名（56–61、65、67–77、104–116）是否同一个类**：**Unknown。**
- **`_accountKasada` 与 `_forter` 在同一个模型里是否意味着「这个站同时用两家风控」**：**Inference，未证。**

### 七、教训

**这一轮我有机会写一张看起来很有价值的映射表：把 14 个 `FlowKind` 中的 5 个接到 Pop Mart 上。
它会让 `TaskKinds.cs` 从「清单」变成「接上了」。**

**而我没写，因为我查的时候发现证据的粒度不够。**

**这是 R869 之后第一次，我在**动手之前**判定「这个改动会制造看起来完成的东西」。**

**代价是这一轮没有产品代码改动。收益是 `TaskKinds.cs` 仍然只声称它证明的了的东西。**
"""

VERDICT = """

---

## 第 882 轮：5 个 `Start*Flow` 与 Pop Mart 抽签步骤同一片字面量区 —— 而这不够写映射表

### 读出来的段落

```
14337bda2  <Start>d__56
14337bdc4  <StartSignupFlow>d__57 <StartClearFlow>d__58 <StartInStoreFlow>d__59
           <StartPopNowFlow>d__60 <StartNormalFlow>d__61
14337bff7  <CanPlaceOrder>d__72 <FindProductMulti>d__73 <FindProduct>d__74
14337c042  <FindProductMultiInstore>d__75 <FindProductInstore>d__76 <ClearCart>d__77
```

**而 `GetOrders>d__104` @ `0x14337c7e5`、`StartDrawFlow>d__115` 也在同一段 —— 一个 blob 里有 ordinal 56–116+。**

### 看起来像「这个类支持 5 种任务」，但不是

**一个字面量 blob 可以同时装**基类与派生类**的字面量 —— NativeAOT 不按类分块。**

| 能说 | 不能说 |
|---|---|
| 同一片字面量区 | **「Pop Mart 支持这 5 种」** |
| 有 ordinal 56–61 与 104–116+ | 「这是同一个类」 |
| 字段有 `_accountKasada`/`_forter` | 「属于哪个站」 |

> **R878 的教训适用，而这次相邻的粒度是 **blob** —— 比单条字符串更粗，**证据更弱，不是更强**。**

### 所以映射表不写

**要写「PopMart 支持这 5 种」，需要「5 个 `Start*Flow` 与 Pop Mart 的 ordinal 同属一类」的证据。blob 共享给不出。**

> **一个没有证据的映射表比没有映射表更坏 —— 它会把「看起来接了」当成「接了」。**

### 字段仍然有用

**`_accountKasada`（Kasada token 在**账号级**）· `_forter` · `_marketPlace`/`_locationId`/`_locationData`（门店模型，与 `FindProductInstore` 一致）· `_paymentUri`/`_paypalToken`**

**但「哪些字段在这片」不指向唯一站：`AntiBotVendors.cs` 的 `GetKasada` 示例串是 `Nike-Kasada-Version`。**

### 仍然 Unknown

**那 5 个 `Start*Flow` 属于哪个类**（**需 ordinal→类 映射；R504 那堵墙大概率也挡这条**）·
**56–61/65/67–77/104–116 是否同一个类** · **`_accountKasada` 与 `_forter` 同模型是否意味着同时用两家风控**（Inference）

### 教训

> **这一轮我有机会写一张看起来很有价值的映射表，让 `TaskKinds.cs` 从「清单」变成「接上了」。我没写，因为查的时候发现证据粒度不够。**
> **这是 R869 之后第一次，我在**动手之前**判定「这个改动会制造看起来完成的东西」。**
> **代价是本轮没有产品代码改动。收益是 `TaskKinds.cs` 仍然只声称它证明的了的东西。**
"""

BACKLOG_ADD = """

## 判据 — 5 个 `Start*Flow` 与 Pop Mart 抽签步骤同一片字面量区（R882）

**`0x14337B000`–`0x14337CE00` 共 78 条，含：`Start>56` · `StartSignupFlow>57` · `StartClearFlow>58` · `StartInStoreFlow>59` · `StartPopNowFlow>60` · `StartNormalFlow>61` · `FindProductInstore>76`**
**而同段还有 `GetOrders>104` · `StartDrawFlow>115` → **一个 blob 有 ordinal 56–116+**。**

### 这不够写映射表

**blob 可同时装**基类与派生类**字面量（NativeAOT 不按类分块）。**

| 能说 | 不能说 |
|---|---|
| 同一片字面量区 | 「Pop Mart 支持这 5 种」 |
| ordinal 56–61 与 104–116+ | 「同一个类」 |
| 字段 `_accountKasada`/`_forter` | 「属于哪个站」 |

> **相邻粒度是 blob，比单条字符串更粗 → 证据更弱。R878 的教训升级版。**

**所以 `FlowKind × Store → StoreFlow` 映射表**本轮不写** —— 没证据的映射表会把「看起来接了」当成「接了」（R869 假成功同族）。**

### 字段收获

**`_accountKasada`（Kasada token 账号级）· `_forter` · `_marketPlace`/`_locationId`/`_locationData`（门店模型，配 `FindProductInstore`）· `_paymentUri`/`_paypalToken`**

| 仍 Unknown | |
|---|---|
| 5 个 `Start*Flow` 属哪个类 | 需 ordinal→类 映射；R504 那堵墙大概率也挡 |
| 56–61/65/67–77/104–116 是否同一类 | 未证 |
| 两风控同模型 = 同时用两家？ | Inference |

**纪律**：**有证据的缺席，好过没证据的接线。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R882", BLOCKER)
    ensure(RSTATUS, "R882", BLOCKER)
    ensure(RVERDICT, "第 882 轮", VERDICT)
    ensure(BACKLOG, "R882", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R882" not in h:
        h += ("\n## R882 补充 — 5 个 `Start*Flow` 与 Pop Mart 抽签步骤同一片字面量区（**本轮未改产品代码**）\n\n"
              "**`0x14337B000`–`0x14337CE00` 78 条**：`Start>56` `StartSignupFlow>57` `StartClearFlow>58` `StartInStoreFlow>59` `StartPopNowFlow>60` `StartNormalFlow>61` `FindProductInstore>76`，"
              "**同段还有 `GetOrders>104` `StartDrawFlow>115`** → 一个 blob 有 ordinal 56–116+。\n"
              "**但 blob 可同时装基类与派生类字面量 → **不能说「PopMart 支持这 5 种」**。相邻粒度是 blob（比字符串更粗）→ 证据更弱。**\n"
              "**所以 `FlowKind × Store → StoreFlow` 映射表本轮**不写** —— 没证据的映射表 = 把「看起来接了」当「接了」。**\n"
              "**字段收获**：`_accountKasada`（Kasada token 账号级）· `_forter` · `_marketPlace`/`_locationId`/`_locationData`（门店模型）。\n"
              "**下一步：查 ordinal→类 的映射手段（R504 那堵墙可能也挡）。**\n")
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
             for p, k in ((RBLOCK, "R882"), (RSTATUS, "R882"), (RVERDICT, "第 882 轮"), (BACKLOG, "R882")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R882: the five task-kind entries share a blob with Pop Mart's draw steps, which is not enough\n\n"
         "R880 set the next step as mapping FlowKind to StoreFlow, which needs evidence of which store declares which\n"
         " Start-prefixed flow. Reading the region that holds the five gives an inviting answer and an insufficient one.\n\n"
         "The region holds Start at ordinal 56, then StartSignupFlow, StartClearFlow, StartInStoreFlow, StartPopNowFlow\n"
         " and StartNormalFlow at 57 through 61, followed by Register, GetSession, Login, CanPlaceOrder, FindProduct,\n"
         " FindProductMultiInstore, FindProductInstore and ClearCart. It also holds GetOrders at 104 and StartDrawFlow\n"
         " at 115, both of which earlier rounds established as Pop Mart's. So one literal blob carries ordinals from 56\n"
         " to 116 and more, and the tempting reading is that this class supports all five task kinds.\n\n"
         "That reading is not supported, and the reason is the same one R878 found one level down. A NativeAOT literal\n"
         " blob holds the names for a base class and its derived classes together; it is not partitioned by class. So\n"
         " sharing a blob proves less than sharing a string object did, not more -- the granularity is coarser, the\n"
         " inference weaker. R878's rule was that adjacency is not ownership; here adjacency is at blob scale.\n\n"
         "Which is why no mapping table was written. Connecting five of the fourteen kinds to Pop Mart would turn\n"
         " TaskKinds.cs from a list into something that looks wired, and a mapping without evidence is worse than no\n"
         " mapping because it converts looks-connected into is-connected. That is the family of failure R869 removed\n"
         " when an empty step list reported a completed checkout.\n\n"
         "The fields are still worth having. _accountKasada puts the Kasada token at account level rather than in a\n"
         " per-request local; _forter puts a Forter token in the model beside it; _marketPlace, _locationId,\n"
         " _locationData and _basePath describe a location model, consistent with FindProductInstore; and\n"
         " _paymentUri, _paypalToken and _paymentApprovalId carry payment state. But which fields sit in a blob does\n"
         " not name a store either, since AntiBotVendors lists Kasada with a Nike example string in the same file.\n\n"
         "Unknown: which class owns the five entries, which needs an ordinal-to-class mapping and may sit behind the\n"
         " same wall R504 found where descriptors carry no cross-references; whether ordinals 56 to 61, 65, 67 to 77\n"
         " and 104 to 116 belong to one class; and whether Kasada and Forter appearing in one model means a store uses\n"
         " both, which is inference and unproven.\n\n"
         "The lesson is that this round had the chance to write a mapping table that would have looked like real\n"
         " progress, and declined because the check showed the evidence was too coarse. It is the first time since R869\n"
         " that the judgement happened before the code rather than after. The cost is no product change; the gain is\n"
         " that TaskKinds.cs still claims only what it proves.\n\n"
         "No product code changed; suite carries at 1780."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
