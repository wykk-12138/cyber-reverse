"""Record R924: Disney's payment sheet, and vendor coverage at eleven of twelve."""

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
### Disney 的支付面板：卡先进一个端点，结账拿 token（R924）

**四条路径、两台宿主，而其中一条决定了整个类的形状：**

```
paymentsheet-ent.wdprapps.disney.com/api/v1/card/token   一张卡，token 化
paymentsheet-ent.wdprapps.disney.com/api/v1/checkout     这张 token 付的结账
paymentsheet-ent.wdprapps.disney.com/api/v3/process      处理步骤，晚一个版本
registerdisney.go.com/jgc/v8/client                      Disney Guest Connect（身份）
```

### 为什么先 token 化是一个**该实现的属性**，而不是一句注释

**卡端点与结账分开，且它的名字说的是 token 而不是 pay —— 所以**流程里的卡永远不到结账那一步**。**

> **一个在两个请求体里出现的卡号被暴露两次。原版看起来只让它出现一次。
> 所以 `TokeniseCardAsync` 收卡并返回 token，而这个类里**没有第二个方法收卡**。**

**而结账方法**没有 token 就拒绝** —— 因为一个没有 token 的结账只能带卡，而那正是这个拆分要避免的。**

### 两个版本并存是对的

**v1 结账、v3 处理。**服务里「处理比启动它的结账活得更久」是常态。
**所以分开记，不统一 —— 统一会**静默改掉两次调用中的一次**。**

### 而 `jgc/v8/client` **只记录、不调用**

**没有任何东西说它返回什么、或一次购买是否需要它。
**按猜发一个请求，就是发一个原版可能从不发的请求。****

### 数字

| 度量 | R923 | **R924** |
|---|---|---|
| 套件 | 1881 | **1888** |
| **vendor 命名** | 9 / 12 | **11 / 12** |
| **vendor 缺失** | 3 | **1** |

**只剩 Viva 一家（3 条：`chargetokens` → `paymentdetails?ref=` → `transactions`）。**

### 而 11/12 这个数到这里可以总结了

**R921 量出 5/12，R922 Global-e、R923 eShopWorld、R924 Disney —— 四轮把 7 个未匹配降到 1。**

**而四轮里每一轮的产品**形状都不同**：**
- **Global-e**：一条完整 URL → 可核参数顺序与空值
- **eShopWorld**：两条轮询端点 → **一个带第三结果的等待**
- **Disney**：卡与结账分开 → **一个安全性属性**

> **所以「补 vendor」不是同一件事做四遍。每家给的证据形状不同，实现的东西也就不同。**
> **如果我把四家都做成「一组常量」，7 会降到 1，而三家真正值钱的东西都不会出现。**
"""

if "Disney 的支付面板" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R924 appended")

VERDICT = """

---

## 第 924 轮：Disney 的支付面板 —— 卡先进一个端点，结账拿 token

### 四条路径，一条决定类的形状

```
/api/v1/card/token   一张卡，token 化
/api/v1/checkout     这张 token 付的结账
/api/v3/process      处理步骤，晚一个版本
jgc/v8/client        Disney Guest Connect
```

### 先 token 化是**该实现的属性**，不是注释

**卡端点与结账分开，且名字说 token 不说 pay → **流程里的卡永远不到结账那一步**。**

> **一个在两个请求体里出现的卡号被暴露两次。原版看起来只让它出现一次。
> 所以 `TokeniseCardAsync` 收卡并返回 token，而这个类里**没有第二个方法收卡**。
> 结账方法**没有 token 就拒绝** —— 没有 token 的结账只能带卡，而那正是拆分要避免的。**

**而测试断言的是**实际发出的 body** 里没有卡号 —— 只查会话的测试即使卡被追加进去也会过。**

### 两个版本并存是对的

**v1 结账、v3 处理。「处理比启动它的结账活得更久」是常态。统一会**静默改掉两次调用中的一次**。**

### `jgc/v8/client` 只记录、不调用

**没有东西说它返回什么、或购买是否需要它。按猜发请求，就是发一个原版可能从不发的请求。**

### 数字

| 度量 | R923 | **R924** |
|---|---|---|
| 套件 | 1881 | **1888** |
| vendor 命名 | 9 / 12 | **11 / 12** |
| vendor 缺失 | 3 | **1** |

**只剩 Viva（`chargetokens` → `paymentdetails?ref=` → `transactions`）。**

### 而这四轮可以总结了

**R921 量出 5/12，R922 Global-e、R923 eShopWorld、R924 Disney —— 把 7 个未匹配降到 1。**

**而每轮的产品**形状都不同**：**
- **Global-e**：一条完整 URL → 可核**参数顺序与空值**
- **eShopWorld**：两条轮询 → **一个带第三结果的等待**
- **Disney**：卡与结账分开 → **一个安全性属性**

### 教训

> **「补 vendor」不是同一件事做四遍。每家给的证据形状不同，实现的东西也就不同。**
> **如果我把四家都做成「一组常量」，7 会降到 1，而三家真正值钱的东西都不会出现。**
"""

BACKLOG_ADD = """

## 优先级 ① — Disney 支付面板（R924，**改产品代码 +7 用例**）

### 四条路径两台宿主

```
/api/v1/card/token · /api/v1/checkout · /api/v3/process · jgc/v8/client
```

### `Payments/DisneyPaymentSheet.cs`

**`SheetHost`/`GuestHost` · 四条路径 · `TokeniseCardAsync` · `CheckoutAsync` · `ProcessAsync` · `StepOrder` · `GuestClientNote`**

### 三个刻意的决定

**① 只有 `TokeniseCardAsync` 收卡** —— 类里没有第二个收卡的方法；`CheckoutAsync` 无 token 就拒绝。
**② v1 与 v3 分开记** —— 统一会静默改掉两次调用中的一次。
**③ `jgc/v8/client` 只记录不调用** —— 按猜发请求就是发一个原版可能从不发的请求。

### 测试断言的是实际 body

**`TheCheckoutCarriesTheTokenAndNotTheCard` 断言发出的 body 里没有卡号 —— 只查会话的测试会被追加的卡骗过。**

### 数字

**套件 1881 → 1888 · vendor 命名 9/12 → **11/12** · 缺失 3 → **1**（只剩 Viva）**

| 仍 Unknown | |
|---|---|
| 所有请求体与响应 | 只有端点名的顺序 |
| `jgc/v8/client` 的用途 | 未证 |
| Viva 三条的顺序 | 名字暗示 token→details→transactions |

**纪律**：「补 vendor」不是同一件事做四遍 —— 每家给的证据形状不同，实现的东西也就不同。
"""

BLOCKER = """

---

## 348. Disney 支付面板：vendor 11/12；只剩 Viva

> R924。**改产品代码 +7 用例。** 套件 **1888 通过 / 0 失败 / 0 跳过**。

### 一、四条路径

```
paymentsheet-ent.wdprapps.disney.com/api/v1/card/token   卡 token 化
paymentsheet-ent.wdprapps.disney.com/api/v1/checkout     结账
paymentsheet-ent.wdprapps.disney.com/api/v3/process      处理（v3）
registerdisney.go.com/jgc/v8/client                      Guest Connect
```

### 二、先 token 化是实现出来的属性

**卡端点与结账分开、名字说 token 不说 pay → 流程里的卡永远不到结账那一步。**

**实现：只有 `TokeniseCardAsync` 收卡，类里没有第二个收卡方法；`CheckoutAsync` 无 token 就拒绝。**

**测试断言**实际发出的 body** 里没有卡号 —— 只查会话的测试即使卡被追加也会过。**

### 三、两个版本分开记

**v1 结账、v3 处理。「处理比启动它的结账活得更久」是常态。统一会静默改掉两次调用中的一次。**

### 四、`jgc/v8/client` 只记录不调用

**没有东西说它返回什么、或购买是否需要它。按猜发请求就是发一个原版可能从不发的请求。**

### 五、数字

| 度量 | R923 | R924 |
|---|---|---|
| 套件 | 1881 | **1888** |
| **vendor 命名** | 9 / 12 | **11 / 12** |
| **vendor 缺失** | 3 | **1** |

**只剩 Viva（`chargetokens` · `paymentdetails?ref=` · `transactions`）。**

### 六、验证

```
vendor_coverage.py                  -> 两台 disney 宿主均 yes；11 named / 1 absent
test --filter DisneyPaymentSheetTests -> 7 通过
metrics_report.py                   -> 1888 通过 / 0 失败
```

### 七、仍然 Unknown

- **所有请求体与响应**：**Unknown** —— 只有端点名的顺序。
- **`jgc/v8/client` 的用途**：**Unknown** —— 只记录不调用。
- **Viva 三条的顺序**：**Inference** —— 名字暗示 token → details → transactions。

### 八、教训

**R921 量出 5/12。四轮之后 11/12。**

**而四轮的产品形状都不同：Global-e 核**参数顺序与空值** · eShopWorld 给**一个带第三结果的等待** ·
Disney 给**一个安全性属性**。**

**如果我把四家都做成「一组常量」，7 会降到 1，而三家真正值钱的东西都不会出现。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R924", BLOCKER)
    ensure(RSTATUS, "R924", BLOCKER)
    ensure(RVERDICT, "第 924 轮", VERDICT)
    ensure(BACKLOG, "R924", BACKLOG_ADD)

    note = (
        "\n## R924 补充 — Disney 支付面板（改产品代码 +7 用例，套件 1881→1888）\n\n"
        "四条路径两台宿主：api/v1/card/token · api/v1/checkout · api/v3/process · jgc/v8/client。\n\n"
        "先 token 化是实现出来的属性：卡端点与结账分开、名字说 token 不说 pay → 只有 TokeniseCardAsync 收卡，"
        "类里没有第二个收卡方法；CheckoutAsync 无 token 就拒绝。测试断言实际发出的 body 里没有卡号。\n\n"
        "v1 与 v3 分开记（统一会静默改掉两次调用中的一次）；jgc/v8/client 只记录不调用。\n\n"
        "数字：套件 1888 · vendor 命名 9/12 → 11/12 · 缺失 3 → 1（只剩 Viva）。\n\n"
        "而四轮 vendor 的形状都不同：Global-e 核参数顺序与空值 · eShopWorld 给带第三结果的等待 · Disney 给安全性属性。"
        "如果都做成「一组常量」，7 会降到 1，而三家值钱的东西都不会出现。\n\n"
        "下一轮：Viva（最后一家，3 条）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R924" not in h:
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
             for p, k in ((RBLOCK, "R924"), (RSTATUS, "R924"), (RVERDICT, "第 924 轮"), (BACKLOG, "R924")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R924: Disney's payment sheet, where the card reaches one endpoint and the checkout gets a token\n\n"
         "Four paths across two hosts, and one of them decides the class's shape. The card endpoint is separate from\n"
         " checkout and its name says token rather than pay, so a flow's card never reaches the checkout call. That is\n"
         " implemented as a property and not described as one: TokeniseCardAsync takes a card and returns a token, no\n"
         " other method in the class accepts a card, and the checkout refuses without a token because a checkout\n"
         " without one would have to carry the card the split exists to avoid. The test asserts on the body actually\n"
         " sent, since one that only inspected the session would pass even if the card had been appended.\n\n"
         "Two API versions sit side by side -- v1 for checkout and v3 for process -- and they stay separate, because a\n"
         " service whose processing outlives the checkout that started it is ordinary and unifying them would silently\n"
         " change one of the two calls.\n\n"
         "The guest client at jgc/v8/client is recorded and never called. Nothing says what it returns or whether a\n"
         " purchase needs it, and a request made on a guess would be one the original might never send.\n\n"
         "Figures: suite 1881 to 1888, vendors named nine of twelve to eleven, vendors absent three to one. Viva is all\n"
         " that remains.\n\n"
         "Unknown: every request body and response, since the order of the endpoint names is the whole of the evidence;\n"
         " what the guest client is for; and the order of Viva's three calls, which the names only suggest.\n\n"
         "The lesson is the one these four rounds keep producing in different forms. Global-e could be checked by\n"
         " parameter order and empty values, eShopWorld needed a third outcome for a wait that settles late, and Disney\n"
         " gave a security property. Building all four as one set of constants would have taken the count from seven to\n"
         " one and lost what each of the last three was actually worth.\n\n"
         "Product code changed; suite green at 1888."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()