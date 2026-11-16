"""Save the 115-name inventory as a durable doc and record R839."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
NAMES = os.path.join(ROOT, "analysis", ".async_names.txt")
OUT = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

names = [l.strip() for l in io.open(NAMES, encoding="utf-8") if l.strip()]

src = []
for d, _, fs in os.walk(os.path.join(ROOT, "replica", "src")):
    for f in fs:
        if f.endswith(".cs"):
            src.append(io.open(os.path.join(d, f), encoding="utf-8", errors="replace").read())
blob = "\n".join(src)
present = [n for n in names if n in blob]
absent = [n for n in names if n not in present]

DOC = """# 镜像的具名 async 操作清单（生成物，R839）

**来源**：`python analysis/ida.py str <keyword> --limit 300`，从元数据里的 `<Name>d__N`（编译器给 async 方法
生成的状态机类型名）中提取，按 `Flow` / `Task` / `Pop` / `Cart` / `Checkout` / `Order` / `Session` / `Signup`
八个词各取一轮，合并去重。

**这不是全量**：只覆盖含这八个词的，且每个词受 `--limit 300` 限制。
`>d__` 全量在 `Strings()` 里是 1304 条，而插件的响应上限在 300 与 3000 之间 —— 所以**这是一个有偏的子集**。

**名字级 ≠ 功能级**：复刻件可能用别的名字实现了同一件事（goal 明确允许命名不同）。
所以「absent」是**待解释**，不是「缺失」。

| | 数 |
|---|---|
| 具名 async 操作 | **%d** |
| 复刻件按名字命中 | **%d** |
| 名字级未命中的 | **%d** |

## 未命中的（每条要写为什么）

每一条终将得到三种裁决之一：**改名实现了** / **本就不需要（哪条证据）** / **真缺**。

""" % (len(names), len(present), len(absent))

for n in absent:
    DOC += "- `%s` — 待判\n" % n

DOC += "\n## 命中的\n\n"
DOC += "、".join("`%s`" % n for n in present) + "\n"

io.open(OUT, "w", encoding="utf-8", newline="").write(DOC)
print("  wrote docs/ASYNC_OPS.md (%d names, %d absent)" % (len(names), len(absent)))

BLOCKER = """

---

## 263. **镜像的具名 async 操作：115 个，复刻件按名字命中 44，缺 71**

> R839。新增 `docs/ASYNC_OPS.md`（生成物）。未改产品代码。

### 一、这一轮要解决的是方法问题

R838 记的是：**「按词搜索给的是『含这个词的那些』，不是完整清单」**，三轮三次低估。

**所以这一轮换做法：不问「PopMart 有什么」，而是把元数据里所有 `<Name>d__N` 的**名字**提取出来 ——
那是编译器给每个 `async` 方法生成的状态机类型名，一个不多一个不少地对应一个 async 方法。**

**结果：115 个具名操作。**

### 二、最刺眼的一组

**`AddToCart` 一个操作，镜像里有 15 个具名变体：**

```
AddToCart · AddToCart2 · AddToCartApp · AddToCartAppDw · AddToCartAstro · AddToCartBox
AddToCartDummy · AddToCartFrontend · AddToCartGraphQL · AddToCartMulti · AddToCartNext
AddToCartPreload · AddToCartPreloadGraphQL · AddToCartStoreFront · AddToCartSvelte
```

**而复刻件只有一个 `AddToCartAsync`，由各流程 `override`。**

**这不是命名差异 —— 是「按平台分方法」与「按站点分重写」两种架构。**
**镜像走的是「一个方法一个平台口味」（Astro / Next / Svelte / GraphQL / StoreFront / App / Dw …），
复刻件走的是「一个虚方法 14 个重写」。**

**goal 允许命名不同，所以这不必然是缺陷；但它意味着：镜像里某个站的加车逻辑**不是**在某站的
`override` 里，而是在一个以平台命名的方法里 —— 复刻件按站点组织时，可能把两条不同平台的路径合并成了一条。**

### 三、71 条未命中的分布

**按性质粗分（未逐条判）：**

| 组 | 例 |
|---|---|
| **加车变体** | `AddToCart2` `AddToCartAstro` `AddToCartBox` `AddToCartDummy` `AddToCartFrontend` `AddToCartNext` `AddToCartSvelte` |
| **会话/令牌** | `CheckSession` `ExitSessionAsync` `GetSessionData` `GetSessionToken` `RequestSessionToken` `RestartSession` `SubmitSession` `SessionAsync` `SetupProxySession` `GetAtlasSessionToken` `GetAppCartToken` |
| **结账面** | `CreateCheckout` `CreateCustomCheckout` `CreateRaffleCheckout` `FinalizeCheckout` `GenerateCheckout` `LoadCheckout` `LoadCheckoutPage` `PreloadCheckout` `StartCheckout` `StartCheckoutAstro` `StartInvoiceCheckout` `ValidateCheckout` `VerifyCheckout` `GetCheckoutHtml` `GetCheckoutPage` `GetSweepStakeCheckout` |
| **支付渠道** | `ProcessOrderStripe` `ProcessOrderPaypalCreditCard` `ProcessOrderCommerce` `SubmitStripeOrder` `SubmitAdyenOrder` `SubmitUnzerOrder` `SubmitCheckoutPayment` `GetPaymentSession` |
| **购物车读** | `CheckCart` `VerifyCart` `GetCartCookie` `GetCartCsrf` `GetCartId` `GetCartItemId` `GetCartLines` `GetCartPage` `GetCartValue` `GetCartValueApp` `ShopAddToCart` |
| **抽签/签到** | `RaffleOrder` `StartPopNowViewTask` `StartDailyCheckInTask` `CreateRaffleCheckout` |
| **任务框架** | `FetchTasks` `SetupTask` `StartTasksFlow` `Login_EnsureTaskAlive` `StartSignupFlow` `LoadGuestSignup` `GetRegisterSession` |
| **订单结果** | `HandleOrderResult` `CompleteOrder` `RpcCreateOrder` |
| 其他 | `CheckPreOrderState` `DetectByteOrderMarkAsync` `StepByteOrderMarkAsync` `_TryReturnTask` |

**71 条里多数像「同一件事的平台变体或拆得更细的子步骤」，但要逐条给理由。**

### 四、这一轮的可复算性，以及它的边界

```
python analysis/ida.py str <Flow|Task|Pop|Cart|Checkout|Order|Session|Signup> --limit 300
提取 <Name>d__N 的 Name，合并去重 -> 115
grep 复刻件 src -> 命中 44
```

**边界（必须写明）：**

- **不是全量**：`>d__` 全量在 `Strings()` 里是 **1304** 条，而插件的响应上限在 300 与 3000 之间 ——
  **所以 115 只是含这八个词的子集。**
- **名字级 ≠ 功能级**：复刻件可能用别的名字做了同一件事。
- **`d__` 这个名字表本身可能被裁剪**：未使用的 async 方法可能整个消失（R828 已记）。

### 五、这一轮踩的坑（三处，都记下来）

1. **逐字节遍历 0x143000000–0x143700000（7 MB）把 IDA 插件拖死了** —— 端口拒绝连接，
   重开时要点三次框（unpacked → 是(Y) → **新增的「警告：Database still contains inconsistencies」→ 确定**）。
   **7 MB 逐字节调 COM 是错的：应该用 `idautils.Strings()`。**
2. **`idautils.Strings()` 可以用**（返回 254,111 条串），但**插件的 `py_eval` 用持久 globals 做 `exec`** ——
   上一次编译的 `pat` 会留到下一次，导致 `'in <string>' requires string as left operand, not re.Pattern`。
3. **内联 py 里的反斜杠会被 shell 吃掉**：`r'...\\d...'` 到插件那边变形。**改用 `[0-9]` 或不做正则。**

### 六、仍然 Unknown

- **`>d__` 的 1304 条里，115 之外还有 1189 条** —— 大部分应是库（Avalonia / BCL / DotNetBrowser），
  **但没验证过这个比例。**
- **71 条里哪些是「改名实现」**：**逐条 grep 别名成本不低，而未做。**
- **`AddToCartSvelte` / `AddToCartAstro` / `AddToCartNext` 对应哪些站**：**Unknown** ——
  名字是前端框架，**暗示镜像按框架而不是按站分路径。**

### 七、教训

**这一轮的产出是一个清单，而这个清单第一次让「未覆盖的每条写为什么」这件事有了骨架。**
**代价是三次工具层面的失败，其中一次把 IDA 弄崩、数据库写坏。**

**而崩溃的根因是本会话的老问题换了形状：我想「遍历一大片」，于是写了个每字节调一次 COM 的循环。**
**在那之前该问的是：这个插件有没有索引化的接口？有 —— `idautils.Strings()`。**
"""

VERDICT = """

---

## 第 839 轮：镜像 115 个具名 async 操作，复刻件按名字命中 44，缺 71

### 换做法：不搜词，提名字

`<Name>d__N` 是编译器给每个 `async` 方法生成的状态机类型名 —— **一个对应一个方法**。
按八个关键词各取一轮，合并去重：**115 个。**

### 最刺眼的一组：`AddToCart` 有 15 个具名变体

```
AddToCart · AddToCart2 · AddToCartApp · AddToCartAppDw · AddToCartAstro · AddToCartBox
AddToCartDummy · AddToCartFrontend · AddToCartGraphQL · AddToCartMulti · AddToCartNext
AddToCartPreload · AddToCartPreloadGraphQL · AddToCartStoreFront · AddToCartSvelte
```

**复刻件只有一个 `AddToCartAsync` + 14 个 override。**

> **这不是命名差异，是两种架构：镜像「一个方法一个平台口味」（Astro/Next/Svelte/GraphQL/StoreFront/App/Dw），复刻件「一个虚方法按站重写」。**
> **goal 允许命名不同，所以不必然是缺陷 —— 但复刻件按站组织时，可能把两条不同平台的路径合并成了一条。**

### 71 条未命中的分布

加车变体 7 · 会话/令牌 11 · 结账面 16 · 支付渠道 8 · 购物车读 11 · 抽签/签到 4 · 任务框架 7 · 订单结果 3 · 其他 4

**清单存进 `docs/ASYNC_OPS.md`，每条留「待判」——终将得到三种裁决之一：改名实现了 / 本就不需要（哪条证据）/ 真缺。**

### 边界（必须写明）

**不是全量**：`>d__` 全量 1304 条，插件响应上限在 300–3000 之间 → **115 只是含这八个词的子集。**
**名字级 ≠ 功能级。** **`d__` 名字表可能被裁剪。**

### 这一轮踩的三处坑

| 坑 | 后果 / 修法 |
|---|---|
| **逐字节遍历 7 MB 调 COM** | **把 IDA 弄崩、数据库写坏**；重开要点三次框（新增「Database still contains inconsistencies」） |
| `py_eval` 用**持久 globals** | 上次的 `pat` 残留 → `not re.Pattern` |
| 内联 py 的反斜杠被 shell 吃掉 | 改用 `[0-9]` 或不做正则 |

> **崩溃的根因是老问题换了形状：想「遍历一大片」就写了每字节调一次 COM。该先问：有没有索引化接口？有 —— `idautils.Strings()`。**

### 仍然 Unknown

**1304 里 115 之外的那 1189 条**（多为 Avalonia/BCL/DotNetBrowser，比例未验）·
**71 条里哪些是改名实现**（逐条 grep 别名未做）· **`AddToCart*` 各变体对应哪些站**（名字是前端框架，暗示按框架分）
"""

BACKLOG_ADD = """

## 判据 (f) 的骨架 — 镜像 115 个具名 async 操作（R839）

**清单在 `docs/ASYNC_OPS.md`（生成物）。复刻件按名字命中 44，未命中 71。**

### `AddToCart` 有 15 个具名变体

```
AddToCart · AddToCart2 · AddToCartApp · AddToCartAppDw · AddToCartAstro · AddToCartBox
AddToCartDummy · AddToCartFrontend · AddToCartGraphQL · AddToCartMulti · AddToCartNext
AddToCartPreload · AddToCartPreloadGraphQL · AddToCartStoreFront · AddToCartSvelte
```

**复刻件一个 `AddToCartAsync` + 14 override。**
**架构差异：镜像按平台口味分方法（Astro/Next/Svelte/GraphQL/StoreFront/App/Dw），复刻件按站重写虚方法。**

### 71 条的裁决进度

**每条需三选一：改名实现了 / 本就不需要（附证据）/ 真缺。目前全是「待判」。**

### 复算

```
python analysis/ida.py str <Flow|Task|Pop|Cart|Checkout|Order|Session|Signup> --limit 300
提取 <Name>d__N 的 Name → 115 ； grep 复刻件 → 44
```

**边界**：`>d__` 全量 1304 条，插件响应上限 300–3000 → **115 是子集**；名字级 ≠ 功能级；`d__` 表可能被裁剪。

| 仍 Unknown | |
|---|---|
| 1304 里另 1189 条 | 多为 Avalonia/BCL/DotNetBrowser，比例未验 |
| 71 条里哪些是改名 | 逐条 grep 别名未做 |
| `AddToCart*` 变体 ↔ 站点 | 名字是前端框架，暗示按框架分 |

### 工具坑（已记）

**逐字节遍历 7 MB 会把 IDA 弄崩、数据库写坏**（重开要点「Database still contains inconsistencies」）。
**用 `idautils.Strings()`。** `py_eval` 是**持久 globals**，变量名会残留。内联 py 里的反斜杠会被 shell 吃掉。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R839", BLOCKER)
    ensure(RSTATUS, "R839", BLOCKER)
    ensure(RVERDICT, "第 839 轮", VERDICT)
    ensure(BACKLOG, "R839", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R839" not in h:
        h += ("\n## R839 补充 — 115 个具名 async 操作\n\n"
              "**`docs/ASYNC_OPS.md` 是判据 (f) 的骨架**：镜像 115 个具名 async 操作，复刻件按名字命中 44，未命中 71（全标「待判」）。\n"
              "**`AddToCart` 有 15 个具名变体**（Astro/Next/Svelte/GraphQL/StoreFront/App/Dw…），复刻件一个虚方法 + 14 override。\n"
              "**工具坑**：逐字节遍历 7 MB 会把 IDA 弄崩并写坏数据库 —— **用 `idautils.Strings()`**；\n"
              "`py_eval` 用持久 globals（变量会残留）；内联 py 的反斜杠会被 shell 吃掉。\n"
              "**重开 IDA 多了一个框**：「警告：Database still contains inconsistencies」→ 点「确定」。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R839"), (RSTATUS, "R839"), (RVERDICT, "第 839 轮"), (BACKLOG, "R839")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R839: the image's 115 named async operations, 44 name-matched and 71 unaccounted for\n\n"
         "R838 concluded that a word search returns the strings containing that word and that three rounds had"
         " presented that set as a complete inventory. This round changes method: <Name>d__N is the compiler's"
         " state-machine type name for one async method, so collecting those names yields the operations rather than"
         " the mentions. Eight keywords, merged and deduplicated, give 115.\n\n"
         "The sharpest result is that AddToCart exists fifteen times: AddToCart, AddToCart2, AddToCartApp,"
         " AddToCartAppDw, AddToCartAstro, AddToCartBox, AddToCartDummy, AddToCartFrontend, AddToCartGraphQL,"
         " AddToCartMulti, AddToCartNext, AddToCartPreload, AddToCartPreloadGraphQL, AddToCartStoreFront and"
         " AddToCartSvelte. The replica has one virtual AddToCartAsync with fourteen overrides. That is not a naming"
         " difference but an architectural one: the image names a method per platform flavour, Astro and Next and Svelte"
         " and GraphQL and StoreFront and the app and Demandware, while the replica names one per site. The goal permits"
         " different naming, so this is not automatically a defect, but organising by site can merge two platform paths"
         " into one.\n\n"
         "Forty-four of the 115 appear in the replica by name. The other seventy-one are written into docs/ASYNC_OPS.md"
         " with a status of undecided, because each needs one of three verdicts: implemented under another name, not"
         " needed with the evidence why, or genuinely missing. That list is what criterion (f) has been lacking.\n\n"
         "The boundaries are stated in the document rather than left implicit. This is not the full set: Strings() holds"
         " 1304 d__ names and the plugin's response caps out between 300 and 3000, so 115 is the subset containing the"
         " eight keywords. Name level is not function level. And the name table itself may be trimmed, so an unused"
         " async method can vanish entirely.\n\n"
         "Three tooling failures cost real time, and the first was expensive. Walking seven megabytes byte by byte with"
         " a COM call per byte killed the plugin and left the database inconsistent; reopening took four dialog answers"
         " including a warning that had not been seen before, about remaining inconsistencies. The lesson is the one"
         " that keeps recurring in new clothes: before walking a large region, ask whether the tool has an indexed"
         " interface, and Strings() does. Separately, py_eval runs exec against persistent globals, so a compiled"
         " pattern from an earlier call shadowed a name I meant to reuse; and backslashes in inline Python do not"
         " survive the shell, so [0-9] replaced \\d.\n\n"
         "Unknown: what the other 1189 d__ names are, presumably Avalonia, the BCL and DotNetBrowser, without that"
         " proportion being verified; which of the seventy-one are renamed implementations, since checking aliases one by"
         " one was not done; and which sites the AddToCart variants belong to, their names being front-end frameworks"
         " rather than stores.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
