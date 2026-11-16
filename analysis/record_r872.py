"""Record R872: the guessed step could not be written, and two that could were."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### R871 说 `GetInstoreOrders`「likely 可写」—— 查了，**不可写**（R872）

```
python tools\\where_is.py GetInstoreOrders -> 9 files
    implementation: PopMartFlow.cs (1)   ← 我 R871 自己写的注释，不是实现
    analysis:       StoreFlowSteps.cs
```

**`PopMartEndpoints` 里与订单/门店相关的常量：**

```
BuyNow          /shop/v1/order/pre/v2/buyNow
OrderCounter    /shop/v1/order/pre/counter
CanPlaceOrder   /shop/v1/shop/can/place/order
OrderList       /shop/v1/order/list?currentPage=1&pageSize=20
OrderDetail     /shop/v1/order/v2/detailV2?orderNo=
StoreOfflineDrawInfo /join /joinResult       ← 抽签，不是订单
StoreTicketDates / StoreTicketMainPage
```

**没有一个是「店内订单」。所以写 `GetInstoreOrders` 就等于编一个 URL。**

**R871 那句「likely（同段、`PopMartEndpoints` 里可能有对应常量）」**两半都错了**：
同段是真的，常量没有。而「可能」这个词正是问题 —— 它把一个没查的事写成了倾向。**

### 而同一批查询暴露了更好的目标

**R116 已经配对、常量又都在的两步：**

| 步骤 | 端点 | 查询形状 |
|---|---|---|
| `FindExhibit` | `StoreOfflineDrawInfo` | `?alias=` |
| `EnterExhibit` | `StoreOfflineDrawJoin` | 无查询，POST |

**两步都写了。**

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | 新增 `virtual FindExhibitAsync` / `virtual EnterExhibitAsync`，均**默认显式失败** |
| `PopMartFlow.cs` | `FindExhibit` → `GET info?alias=`（alias 从 session 取，缺则失败）· `EnterExhibit` → `POST join`（体 = 上一步存的 exhibit，缺则失败） |

### 两个「缺就失败」是刻意的

**`FindExhibit` 缺 `alias` → 失败，不是发空 alias。**
**`EnterExhibit` 缺 exhibit 体 → 失败，不是发空 POST。**

**理由一致：返回 200 的空请求会被读成成功。这是本会话第七次遇到同一个形态，而这次是在写的时候就避开的。**

### 覆盖变化

```
map.Count     166 -> 168
implementable   1 ->   3
```
"""

if "R871 说 `GetInstoreOrders`「likely 可写」" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R872 appended")

BLOCKER = """

---

## 296. 猜错一个，写对两个：coverage **1 → 3**

> R872。**改了产品代码。** 套件 **1773 通过 / 0 失败 / 0 跳过**。

### 一、R871 的猜测是错的，而错的形状值得记

**R871 结尾写：`GetInstoreOrders`(105)「likely 可写 —— 同段、`PopMartEndpoints` 里可能有对应常量」。**

**查了：**

```
where_is GetInstoreOrders -> implementation: PopMartFlow.cs (1)   ← 我 R871 自己的注释
PopMartEndpoints 与订单/门店相关的常量：BuyNow · OrderCounter · CanPlaceOrder · OrderList · OrderDetail
                                        StoreOfflineDrawInfo/Join/JoinResult（抽签）· StoreTicketDates · StoreTicketMainPage
```

**没有一个是「店内订单」。写它等于编一个 URL。**

**所以那句「likely」两半都错：同段是真的，常量没有。**

> **而「可能」这个词正是问题 —— 它把一个没查的事写成了倾向。
> 一个带「可能」的待办，下一轮会被当成待办去做；而它其实是一个未验证的猜测。**

**正确写法应该是：「`GetInstoreOrders` 未查端点，下一轮查」。**

### 二、同一批查询暴露了更好的目标

**R116 已配对、常量都在的两步：**

| 步骤 | 端点 | 形状 |
|---|---|---|
| `FindExhibit` | `StoreOfflineDrawInfo` | `?alias=` |
| `EnterExhibit` | `StoreOfflineDrawJoin` | POST |

**两步都写了。**

**`EnterExhibit` 的注释里记了一条值得留的观察：R116 说同一端点也服务 `EnterReservation` ——
一个端点、两个客户端阶段。这与 R847 在 John Lewis 发现的形状相同：步骤是客户端的阶段，端点是服务端的资源。**

### 三、两个「缺就失败」是刻意的

| 步骤 | 缺什么 | 处理 |
|---|---|---|
| `FindExhibit` | session 里的 `alias` | **失败**，不发空 alias |
| `EnterExhibit` | 上一步存的 exhibit 体 | **失败**，不发空 POST |

**理由：返回 200 的空请求会被读成成功。**

**这是本会话第七次遇到同一个形态（编造值 / 空壳方法 / 死字段 / 空循环假成功 / …），
而这次是在**写的时候就避开**，不是事后修。**

### 四、数字

```
map.Count      166 -> 168
implementable    1 ->   3
sequence.Count  24 不变
```

**测试四个数一起钉：`168` / `24` / `3` / 三条 `CanRunStep`。
一个虚方法加了没人用会动第一个；写一步会动第三个 —— 分开断言才分得清。**

### 五、验证

```
where_is GetInstoreOrders  -> implementation 只有我自己的注释，无实现
PopMartEndpoints 常量扫描   -> 无 in-store orders 端点
D:\\tools\\dotnet8\\dotnet.exe build ... -> 0 错误
test --filter FlowSequenceTests          -> 7 通过 / 0 失败
python tools\\metrics_report.py           -> 1773 通过 / 0 失败 / 0 跳过
```

### 六、仍然 Unknown

- **`GetInstoreOrders` 用哪个端点**：**Unknown** —— 常量里没有，可能要查镜像的字符串池里有没有别的
  `order` 类路径。**本轮没查，而这次我写「未查」，不写「likely」。**
- **`alias` 从哪来**：**Unknown** —— 现在是从 session 取，但谁往 session 里放它没建立。
  **这条让 `FindExhibit` 在当前代码里跑不通 —— 它会明确失败，而不是跑错。**
- **`StoreOfflineDrawJoin` 的请求体结构**：**Unknown** —— 现在发的是上一步的响应体，那是**我的选择**，不是镜像的行为。

### 七、教训

**一个「likely」在待办清单里能活很久，而它其实只是「我没查」。**

**这一轮把它查了，代价是一条 `where_is` 加一次常量扫描 —— 两分钟。
而如果不查，我会花一轮去写一个没有端点的步骤，写到一半发现没地方发请求。**

**所以待办里不该有「可能可写」；只该有「已确认可写，因为 X」和「未查，下一步查 Y」。**
"""

VERDICT = """

---

## 第 872 轮：猜错一个，写对两个 —— coverage 1 → 3

### R871 那个「likely」是错的

```
where_is GetInstoreOrders -> implementation: PopMartFlow.cs (1)   ← 我 R871 自己的注释
PopMartEndpoints: BuyNow · OrderCounter · CanPlaceOrder · OrderList · OrderDetail
                  StoreOfflineDrawInfo/Join/JoinResult（抽签）· StoreTicketDates · StoreTicketMainPage
```

**没有「店内订单」端点。写它等于编 URL。那句「likely」两半都错：同段是真的，常量没有。**

> **「可能」这个词正是问题 —— 它把一个没查的事写成了倾向。而一个带「可能」的待办，下一轮会被当成待办去做。**
> **正确写法：「`GetInstoreOrders` 未查端点，下一轮查」。**

### 而同一批查询暴露了更好的目标

| 步骤 | 端点 | 形状 |
|---|---|---|
| `FindExhibit` | `StoreOfflineDrawInfo` | `?alias=` |
| `EnterExhibit` | `StoreOfflineDrawJoin` | POST |

**两步都写了（R116 已配对、常量都在）。**

**`EnterExhibit` 注释里留了 R116 的一条观察：同一端点也服务 `EnterReservation` ——
一个端点、两个客户端阶段，与 R847 在 John Lewis 发现的形状相同。**

### 两个「缺就失败」是刻意的

| 步骤 | 缺什么 | 处理 |
|---|---|---|
| `FindExhibit` | session 的 `alias` | **失败**，不发空 alias |
| `EnterExhibit` | 上一步的 exhibit 体 | **失败**，不发空 POST |

**理由：返回 200 的空请求会被读成成功 —— 本会话第七次遇到这个形态，而这次是**写的时候就避开**。**

### 数字

```
map.Count 166 -> 168 · implementable 1 -> 3 · sequence 24 不变
测试四数一起钉：168 / 24 / 3 / 三条 CanRunStep
```

### 仍然 Unknown

**`GetInstoreOrders` 用哪个端点**（常量里没有；**这次我写「未查」，不写「likely」**）·
**`alias` 从哪来**（现在从 session 取，**谁放它进去没建立 —— 所以 `FindExhibit` 会明确失败而不是跑错**）·
**`StoreOfflineDrawJoin` 的请求体结构**（现在发上一步响应体，**那是我的选择，不是镜像的行为**）

### 教训

> **一个「likely」在待办里能活很久，而它其实只是「我没查」。**
> **查它两分钟；不查，我会花一轮去写一个没有端点的步骤，写到一半发现没地方发请求。**
> **所以待办里不该有「可能可写」；只该有「已确认可写，因为 X」和「未查，下一步查 Y」。**
"""

BACKLOG_ADD = """

## 优先级 ① — 猜错一个，写对两个（R872，**已改产品代码**）：coverage 1 → 3

### R871 的「likely」被证伪

**`where_is GetInstoreOrders` → implementation 只有我 R871 的注释；`PopMartEndpoints` 无 in-store orders 端点。**
**→ 写它等于编 URL。**「同段」是真的，「常量可能有」是假的。**

> **待办里不该有「可能可写」——只该有「已确认可写，因为 X」和「未查，下一步查 Y」。**

### 写了一对

| 步骤 | 端点 | 形状 |
|---|---|---|
| `FindExhibit` | `StoreOfflineDrawInfo` | `?alias=`（缺 alias → **失败**） |
| `EnterExhibit` | `StoreOfflineDrawJoin` | POST（缺 exhibit 体 → **失败**） |

**`StoreFlow` 加两个默认失败的虚方法；`PopMartFlow` override。**

**R116 观察：`StoreOfflineDrawJoin` 也服务 `EnterReservation` —— 一端点两阶段，同 R847 的 John Lewis。**

### 数字

`map 166→168` · `implementable 1→3` · `sequence 24` —— **四数一起钉（168/24/3 + 三条 CanRunStep）。**
**套件 1773 通过 / 0 失败。**

| 仍 Unknown | |
|---|---|
| `GetInstoreOrders` 用哪个端点 | **未查（不写 likely）** |
| `alias` 从哪来 | **无人放入 → `FindExhibit` 会明确失败** |
| `StoreOfflineDrawJoin` 请求体结构 | **现在发上一步响应体 = 我的选择，不是镜像行为** |

**纪律**：**「缺就失败」优于「发空的、返回 200 算成功」—— 第七次同一形态，这次写时就避开。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R872", BLOCKER)
    ensure(RSTATUS, "R872", BLOCKER)
    ensure(RVERDICT, "第 872 轮", VERDICT)
    ensure(BACKLOG, "R872", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R872" not in h:
        h += ("\n## R872 补充 — 猜错一个，写对两个（**已改产品代码**）：coverage 1 → 3\n\n"
              "**R871 的「`GetInstoreOrders` likely 可写」被证伪**：`PopMartEndpoints` 无 in-store orders 端点（只有 `BuyNow`/`OrderCounter`/`CanPlaceOrder`/`OrderList`/`OrderDetail` + 抽签/票务）。"
              "**写它等于编 URL。**\n"
              "**改写了一对**：`FindExhibit` → `StoreOfflineDrawInfo?alias=`（缺 alias 失败）· `EnterExhibit` → `POST StoreOfflineDrawJoin`（缺 exhibit 体失败）。"
              "**`StoreFlow` 各加默认失败的虚方法。**\n"
              "**数字：`map 166→168` · `implementable 1→3` · 四数一起钉（168/24/3 + 三条 CanRunStep）。套件 1773 通过 / 0 失败。**\n"
              "**待办里不写「likely」——只写「已确认，因为 X」或「未查，下一步查 Y」。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R872"), (RSTATUS, "R872"), (RVERDICT, "第 872 轮"), (BACKLOG, "R872")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R872: the step I guessed was writable is not, and two that are got written\n\n"
         "R871 closed by calling GetInstoreOrders likely writable because it sits in the same run and PopMartEndpoints"
         " may hold a matching constant. The check says otherwise on both halves: the run is shared, but no constant"
         " matches. BuyNow, OrderCounter, CanPlaceOrder, OrderList and OrderDetail are order endpoints and none is"
         " in-store; StoreOfflineDrawInfo, Join and JoinResult are draw endpoints, not orders. Writing it would mean\n"
         " inventing a URL, and where_is found only my own R871 comment under implementation.\n\n"
         "The word 'likely' is the real fault there. It turned an unchecked question into a leaning, and a leaning in a\n"
         " backlog gets picked up next round as though it were a task. The honest line would have been that the endpoint\n"
         " is unlooked-up and next round should look.\n\n"
         "The same scan offered better targets. FindExhibit and EnterExhibit were paired by R116 and their constants\n"
         " carry their query shapes, so both could be written without inventing anything. Both are now written, with a\n"
         " note from R116 worth keeping: the join endpoint also serves EnterReservation, which is one endpoint for two\n"
         " client phases -- the same shape R847 found at John Lewis, where steps are the client's stages and endpoints\n"
         " are the server's resources.\n\n"
         "Both new steps fail when their input is missing rather than sending an empty request. FindExhibit needs an\n"
         " alias and says so; EnterExhibit needs the body the previous step stored and says so. A 200 from an empty POST\n"
         " reads as success, and this is the seventh time this project has met that shape -- except this time it was\n"
         " avoided while writing rather than removed afterwards.\n\n"
         "Coverage moved from one of twenty-four to three, the map from 166 to 168, and the test pins all four numbers\n"
         " together so a virtual added without a user moves one and a step written moves another.\n\n"
         "Unknown: which endpoint GetInstoreOrders uses, which this time is written as unchecked rather than as likely;\n"
         " where the alias comes from, since the step reads it from the session and nothing puts it there, which is why\n"
         " FindExhibit will fail clearly rather than run wrongly; and the structure of the join request body, where\n"
         " sending the previous step's response is my choice and not the image's behaviour.\n\n"
         "The lesson is about backlog vocabulary. A task list should not contain maybes. It should contain what is\n"
         " confirmed and why, and what is unchecked and what would check it -- because a maybe is indistinguishable from\n"
         " a task once the round that wrote it is over.\n\n"
         "Product code changed; suite green at 1773."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
