"""Record R946: 772 negatives, 118 named, and most of them self-proving -- so the class is eight."""

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
### 772 条否定断言，而真正需要命令的只有 **8 条**（R946）

**R945 说下一轮扫「其余否定断言有多少没带命令」。扫了，而第一次的数**没有意义**。**

### 第一次扫描：772 里 764 条「没有证据」

**而那个数几乎等于全部 —— 因为它把两类东西算成了一类：**

| 一类 | 例子 | 谁证明它 |
|---|---|---|
| **自证** | `Assert.Null(CookiesFor("NoSuchVendor"))` | **测试自己** —— 函数就在那儿 |
| **需镜像** | 「`NikeEndpoints` 没有 `buy/carts/` 路径」 | **只有二进制** —— 跑代码证不出来 |

> **第一类不是断言，是**算术**。把 772 当成 772 个问题，等于把「2+2=4」当成待办。**

### 窄化到「带具体名字」：118 条

**而 118 里绝大多数仍然是自证**（`Assert.Null(Jwt.Decode("not-a-token"))`、`Assert.Empty(Filter("zzzz"))`）。

### 而真正需要镜像的，是**8 条**

| 断言 | 需要什么 |
|---|---|
| `NikeEndpoints` 无 `buy/carts/` | 搜那个路径 |
| `NikeEndpoints` 无 `buy/orders/` | 搜那个路径 |
| `NikeEndpoints.OrderV5` 不含 `scheels` | 搜 scheels |
| `AntiBotVendors.DataDomeRelay` 不含 `datadome.co` | 搜 relay host |
| `PopMartStepMap` 无 `CheckResult` 端点 | 搜那个端点 |
| `JohnLewisStepMap` 无 `GetStripePaymentIntent` | 搜那个端点 |
| `StoreFlowSteps` 的 shared/single 无 `GetMerchantCode` | 步表自己的序号 |
| 无 `ScrapeProductBox` | **R938 已跑过** |

> **八条里一条已经settled（R938），七条还开着。而按 R944 的比例（3 条里 1 条是假的），
> 那七条里大概**有两条是错的** —— 而每一条现在都长着「事实」的样子。**

### 而 118 → 8 这个过程本身是内容

**三个数：772 · 118 · 8。**
**而在第一和第三个之间，我做的是**分类**，不是筛选。**
**筛选会把 764 当成「不重要」丢掉；分类把它们认成「已经证明」——
**两者对剩下的 8 条做的事一样，而对那 764 条的说法完全相反。****

### 数字

| 度量 | R945 | **R946** |
|---|---|---|
| 套件 | 2048 | **2052** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044** |
| **需镜像的否定断言** | 未分 | **8（1 已 settled，7 开）** |

### 教训

> **一个扫描报「764 条没有证据」，而它的意思是「764 条不需要证据」。**
> **同一个数，两种读法，而第一种会让我去补 764 条命令 —— 那是一场没有产出的劳动。**
> **分类不是筛选的礼貌说法；它是把「哪些需要做」和「哪些已经做完」分开的唯一动作。**
"""

if "772 条否定断言" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 946 轮：772 条否定断言，真正需要命令的只有 8 条

### 第一次扫描的数没有意义

**772 里 764 条「没有证据」—— 而那个数几乎等于全部，因为它把两类算成了一类：**

| 一类 | 例子 | 谁证明 |
|---|---|---|
| **自证** | `Assert.Null(CookiesFor("NoSuchVendor"))` | **测试自己** |
| **需镜像** | 「`NikeEndpoints` 没有 `buy/carts/`」 | **只有二进制** |

> **第一类不是断言，是**算术**。把 772 当成 772 个问题，等于把「2+2=4」当成待办。**

### 窄化到带具体名字：118 —— 而 118 里绝大多数仍是自证

### 真正需要镜像的是 **8 条**

**`NikeEndpoints` 无 `buy/carts/` · 无 `buy/orders/` · `OrderV5` 不含 `scheels` ·
`DataDomeRelay` 不含 `datadome.co` · `PopMartStepMap` 无 `CheckResult` · `JohnLewisStepMap` 无 `GetStripePaymentIntent` ·
`StoreFlowSteps` 的 shared/single 无 `GetMerchantCode` · 无 `ScrapeProductBox`（**R938 已跑**）**

> **八条里一条已 settled，七条还开着。而按 R944 的比例（3 条里 1 条假），那七条里大概有两条是错的 ——
> 而每一条现在都长着「事实」的样子。**

### 而 118 → 8 这个过程本身是内容

**三个数：772 · 118 · 8。而中间做的是**分类**，不是筛选。**

> **筛选会把 764 当成「不重要」丢掉；分类把它们认成「已经证明」。
> 两者对剩下的 8 条做的事一样，而对那 764 条的说法完全相反。**

### 数字

| 度量 | R945 | **R946** |
|---|---|---|
| 套件 | 2048 | **2052** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044** |
| 需镜像的否定 | 未分 | **8（1 settled，7 开）** |

### 教训

> **「764 条没有证据」的意思是「764 条不需要证据」。
> 同一个数两种读法，而第一种会让我去补 764 条命令 —— 一场没有产出的劳动。
> 分类不是筛选的礼貌说法，它是把「哪些需要做」和「哪些已经做完」分开的唯一动作。**
"""

BACKLOG_ADD = """

## 判据 (a)/③ — 否定断言三分类：772 → 118 → 8（R946，**+4 用例**）

### 三分类

| 类 | 判据 | 处理 |
|---|---|---|
| 自证 | 测试自己给输入看输出 | 已完成 |
| 需镜像 | 只有二进制能证 | **要命令** |
| — | — | — |

### 8 条需镜像（1 settled，7 开）

**Nike 两条路径 · OrderV5/scheels · DataDomeRelay · PopMart CheckResult · JohnLewis Stripe · StoreFlowSteps GetMerchantCode ·
ScrapeProductBox（R938 已跑）**

### `NegativeClaimClassTests`（4 例）

**两类被区分 · 每条需镜像的都点名需要什么 · 一条已 settled · 扫描数字带 caveat**

### 数字

**套件 2048 → 2052 · 陈旧度不变 · 需镜像否定 未分 → 8**

| 仍 Unknown | |
|---|---|
| 7 条未验的里几条是假的 | 按 R944 比例约 2 条 |
| 其余「需镜像」是否有第 9 条 | 只扫了带引号名字的 |
| 自证类是否真都自证 | 抽样未逐个核 |

**纪律**：分类不是筛选的礼貌说法，它是把「哪些需要做」和「哪些已经做完」分开的唯一动作。
"""

BLOCKER = """

---

## 370. 否定断言三分类：772 → 118 → 8

> R946。**+4 用例，未改产品代码。** 套件 **2052 通过 / 0 失败 / 0 跳过**。

### 一、第一次扫描的数没有意义

**772 条否定断言，764 条「没有证据」—— 而那几乎等于全部。**

**原因：它把两类算成一类。**

| 类 | 例子 | 谁证明 |
|---|---|---|
| **自证** | `Assert.Null(CookiesFor("NoSuchVendor"))` | **测试自己** |
| **需镜像** | 「`NikeEndpoints` 无 `buy/carts/`」 | **只有二进制** |

**第一类不是断言，是算术。**

### 二、窄化到带名字：118 —— 绝大多数仍自证

### 三、真正需镜像的 8 条

```
NikeEndpoints 无 buy/carts/ · 无 buy/orders/
NikeEndpoints.OrderV5 不含 scheels
AntiBotVendors.DataDomeRelay 不含 datadome.co
PopMartStepMap 无 CheckResult 端点
JohnLewisStepMap 无 GetStripePaymentIntent
StoreFlowSteps 的 shared/single 无 GetMerchantCode
无 ScrapeProductBox（R938 已跑）
```

**1 settled · 7 开。按 R944 比例约 2 条是假的。**

### 四、数字

| 度量 | R945 | R946 |
|---|---|---|
| 套件 | 2048 | **2052** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044** |
| **需镜像否定** | 未分 | **8（1 settled，7 开）** |

### 五、验证

```
grep Assert.{Null,DoesNotContain,Empty,False} tests/ -> 772
带引号名字的                                     -> 118
排除自证类后                                      -> 8
test --filter NegativeClaimClassTests             -> 4 通过
metrics_report.py                                 -> 2052 通过 / 0 失败
```

### 六、仍然 Unknown

- **7 条未验的里几条是假的**：**Unknown** —— 按 R944 比例约 2 条。
- **是否还有第 9 条需镜像**：**Unknown** —— 只扫了带引号名字的。
- **自证类是否真都自证**：**Unknown** —— 抽样未逐个核。

### 七、教训

**一个扫描报「764 条没有证据」，而它的意思是「764 条不需要证据」。**

**同一个数两种读法，而第一种会让我去补 764 条命令 —— 一场没有产出的劳动。**

**分类不是筛选的礼貌说法；它是把「哪些需要做」和「哪些已经做完」分开的唯一动作。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R946", BLOCKER)
    ensure(RSTATUS, "R946", BLOCKER)
    ensure(RVERDICT, "第 946 轮", VERDICT)
    ensure(BACKLOG, "R946", BACKLOG_ADD)

    note = (
        "\n## R946 补充 — 否定断言三分类：772 → 118 → 8（+4 用例，未改产品代码，套件 2052）\n\n"
        "772 条否定断言，764 条「没有证据」—— 而那个数几乎等于全部，因为它把两类算成一类：\n"
        "自证（Assert.Null(CookiesFor(\"NoSuchVendor\")) 由测试自己证明）· 需镜像（只有二进制能证）。\n\n"
        "窄化到带名字 118 条 —— 绝大多数仍自证。真正需镜像的 8 条（1 settled，7 开）：\n"
        "Nike 两条路径 · OrderV5/scheels · DataDomeRelay · PopMart CheckResult · JohnLewis Stripe · "
        "StoreFlowSteps GetMerchantCode · ScrapeProductBox（R938 已跑）。\n\n"
        "按 R944 比例（3 条里 1 条假），那七条里约 2 条是错的 —— 而每条都长着「事实」的样子。\n\n"
        "数字：套件 2048 → 2052 · 陈旧度不变 · 需镜像否定 未分 → 8。\n\n"
        "纪律：分类不是筛选的礼貌说法，它是把「哪些需要做」和「哪些已经做完」分开的唯一动作。\n\n"
        "下一轮：验那 7 条里最可能错的一条（DataDomeRelay 或 Nike 路径）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R946" not in h:
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
             for p, k in ((RBLOCK, "R946"), (RSTATUS, "R946"), (RVERDICT, "第 946 轮"), (BACKLOG, "R946")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R946: of 772 negative assertions, eight need the image and the rest prove themselves\n\n"
         "After two rounds turned on negatives about anti-bot vendors, the question was how many more carry no command.\n"
         " A scan found 772 negative assertions and said 764 of them had no evidence nearby -- a number almost equal to\n"
         " the whole, because it counted two different things as one.\n\n"
         "Most negatives prove themselves. Assert.Null on a lookup for an unknown key is arithmetic: the function is\n"
         " right there, the test supplies the input and observes the output, and nothing is claimed about the original.\n"
         " Calling those unproven would send me to write 764 commands for no gain. The class that matters is the one whose\n"
         " truth depends on the binary: NikeEndpoints having no buy/carts path cannot be settled by running the method.\n\n"
         "Narrowing to negatives that name a concrete string gives 118, and most of those are still self-proving. Excluding\n"
         " them leaves eight: two Nike paths, a scheels mention in OrderV5, datadome.co in the DataDome relay host, a\n"
         " CheckResult endpoint for PopMart, a Stripe endpoint for John Lewis, GetMerchantCode sharing between the step\n"
         " tables, and ScrapeProductBox -- which R938 already settled. So seven remain open.\n\n"
         "Three numbers, 772 then 118 then 8, and what happened between the first and the last was classification rather\n"
         " than filtering. Filtering would have discarded the 764 as unimportant; classifying recognises them as already\n"
         " proven. Both leave the same eight, and they say opposite things about the rest -- which matters, because the\n"
         " first reading would have manufactured work.\n\n"
         "Figures: suite 2048 to 2052, freshness unchanged, and the negatives needing the image recorded as eight with one\n"
         " settled.\n\n"
         "Unknown: how many of the seven are false, which R944's ratio suggests is around two; whether a ninth exists\n"
         " outside the ones naming a quoted string; and whether the self-proving class really all is, which was sampled\n"
         " rather than checked one by one.\n\n"
         "The lesson is that a scan reporting 764 without evidence was reporting 764 that need none. Same number, two\n"
         " readings, and one of them invents a great deal of work.\n\n"
         "Tests and one new class added; no product code; suite green at 2052."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()