"""Record R842: the third batch, and the cumulative tally with the shape of what is left."""

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

RENAMED = [
    ("AddToCartNext", "`__NEXT_DATA__` -> `StoreFlow.cs` ×1 —— **换了探针才命中**"),
    ("DetectByteOrderMarkAsync", "`ByteOrderMark` -> `NetClient.cs`"),
    ("StepByteOrderMarkAsync", "`ByteOrderMark` -> `NetClient.cs`"),
    ("GetCartLines", "`CartLines` -> `ShopifyGraphQl.cs`"),
    ("Login_EnsureTaskAlive", "`EnsureTaskAlive` -> `StoreFlow.cs`"),
    ("RaffleOrder", "`Raffle` -> `RetailFlows.cs` 等"),
    ("RpcCreateOrder", "`CreateOrder` -> `StoreApiFamilies.cs` 等"),
    ("StartDailyCheckInTask", "`CheckIn` -> `NikeSteps.cs` · `PopMartEndpoints.cs` · `StoreFlowSteps.cs`"),
    ("StartSignupFlow", "`Signup` -> `DemandwareControllers.cs` 等"),
]

SUMMARY = """

### 累计（R840–R842）

| 批次 | 条数 | 改名实现 | 能力存在 | 探针无辨识力 | 零命中待判 |
|---|---|---|---|---|---|
| R840 | 7 | 3 | 0 | 1 | 3 |
| R841 | 24 | 9 | 5 | 0 | 10 |
| R842 | 39 | 9 | 0 | 3 | 27 |
| **合计** | **70** | **21** | **5** | **4** | **40** |

**70/71 已过一轮探针（剩 `GetSessionData` 一条在 R841 已判「待判」，实际 71 条全覆盖）。**

### 现在这 40 条「零命中」意味着什么，以及不再意味着什么

**它已经不再意味着「缺失」。** 探针在本会话里已经错过很多次：

- **`AddToCartBox`** 零命中一次后，靠 `boxCart` 找到 —— **改名实现**
- **`AddToCartNext`** 用 `Next` 无效，用 `__NEXT_DATA__` 命中 —— **换词才看见**
- **`SubmitAdyenOrder`** 探针命中过多，**而命中的文件里就有 `AdyenGateway.cs`** —— **能力很全**

**所以「零命中」现在的准确含义是：用我试过的这些词，在复刻件源码里找不到它。
它可能是真缺，也可能用的是我没想到的词。**

### 要往下走，探针不是工具了

**这 40 条要判，需要的是调用图证据 —— 镜像里哪个流程调用它。**
**而调用图需要从「函数地址」走，不是从「名字字符串」走。**
**这正是 R828 记的：名字字符串没有 xref，代码地址才有。**

**所以下一阶段的工具不是 `str`，是「按地址找调用者」。**
"""

lessons = """

### 教训（三轮累积）

**探针表的四种结果不是四种「程度」，是四种「不同的东西」：**

| 结果 | 含义 | 能不能当结论 |
|---|---|---|
| 1–5 文件命中 | 找到候选，**文件名字本身就是证据** | 能，但要读那个文件 |
| >5 文件命中 | **词没用**，或**能力很全** —— 须看命中文件是否关于这件事 | 不能，要先分辨 |
| 0 命中 | 用这些词找不到 | **不能**，词可能不对 |
| 换词后仍 0 命中 | 仍未找到 | **仍不能** —— 只能说「我没想到词」 |

**表格里没有一格能单独读成「缺失」。**
**这就是为什么判据 (f) 那句「未覆盖的每条写为什么」难 —— 「为什么」不能是「我搜过没搜到」。**
"""

io.open(DOC, "a", encoding="utf-8").write(SUMMARY + lessons)
print("  ASYNC_OPS.md: cumulative summary + lessons appended")

BLOCKER = """

---

## 266. 71 条全过一轮：21 改名实现 · 5 能力存在 · 4 探针无辨识力 · 40 零命中

> R842。`analysis/adjudicate.py` 成为常驻工具。未改产品代码。

### 一、第三批 39 条

**9 条改名实现，其中两条值得单说：**

- **`AddToCartNext`** —— R840 用 `Next` 探针失败，这一轮换 `__NEXT_DATA__` **命中 `StoreFlow.cs`**。
  **R840 记的「换探针」这条建议真的成立。**
- **`StartDailyCheckInTask`** —— `CheckIn` 命中 `NikeSteps.cs` · `PopMartEndpoints.cs` · `StoreFlowSteps.cs`。
  **每日签到确实有实现，且横跨 Nike / PopMart / 通用步。**

**其余 7 条**：`DetectByteOrderMarkAsync` / `StepByteOrderMarkAsync` → `NetClient.cs` ·
`GetCartLines` → `ShopifyGraphQl.cs` · `Login_EnsureTaskAlive` → `StoreFlow.cs` ·
`RaffleOrder` → `RetailFlows.cs` · `RpcCreateOrder` → `StoreApiFamilies.cs` · `StartSignupFlow` → `Demandware*`

**3 条探针无辨识力**：`GetCartId`（`CartId` 11 文件）· `GetRegisterSession`（`Registration` 9 文件）·
`StartCheckout`（`InitiateCheckout` 7 文件）—— **这三条命中文件需要人工看，不能直接判。**

**27 条零命中。**

### 二、累计

| 批次 | 条数 | 改名实现 | 能力存在 | 探针无辨识力 | 零命中 |
|---|---|---|---|---|---|
| R840 | 7 | 3 | 0 | 1 | 3 |
| R841 | 24 | 9 | 5 | 0 | 10 |
| R842 | 39 | 9 | 0 | 3 | 27 |
| **合计** | **70** | **21** | **5** | **4** | **40** |

### 三、「零命中」现在意味着什么，不再意味着什么

**它不再意味着「缺失」。** 探针在本会话里已经错过多次：

- `AddToCartBox` 零命中后靠 `boxCart` 找到
- `AddToCartNext` 换 `__NEXT_DATA__` 才命中
- `SubmitAdyenOrder` 命中过多，**而命中的文件里就有 `AdyenGateway.cs`**

**准确含义：用我试过的这些词，在复刻件源码里找不到它。可能是真缺，也可能用的是我没想到的词。**

### 四、探针这条路走到头了

**这 40 条要判，需要调用图 —— 镜像里哪个流程调用它。**
**而调用图要从「函数地址」走，不是从「名字字符串」走**（R828 已证：名字字符串无 xref，代码地址才有）。

**所以下一阶段的工具不是 `str`，是「按地址找调用者」。**

### 五、验证

```
python analysis\\adjudicate.py
  39 行；规则 >5⇒探针无辨识力 / 1-5⇒改名实现 / 0⇒待判
  totals: 待判 27 · 改名实现 9 · 探针无辨识力 3
docs\\ASYNC_OPS.md: 第三批表 + 累计表 + 教训
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **那 40 条的真相**：**Unknown** —— 需要调用图。
- **3 条探针无辨识力的命中文件是否关于这件事**：**Unknown** —— 未逐个读。
- **`GetCartId` 的 11 个文件里，哪个是「取车 id」而不是「用 cartId 变量」**：**Unknown。**

### 七、教训

**三轮下来，探针表有了四种结果，而它们不是四种「程度」，是四种「不同的东西」：**

| 结果 | 含义 |
|---|---|
| 1–5 文件 | 找到候选，**文件名字本身就是证据** |
| >5 文件 | **词没用** 或 **能力很全** —— 须看命中文件 |
| 0 命中 | 用这些词找不到 |
| 换词仍 0 | 仍未找到 |

**表格里没有一格能单独读成「缺失」。**
**而判据 (f) 要求「未覆盖的每条写为什么」—— 「为什么」不能是「我搜过没搜到」。**
"""

VERDICT = """

---

## 第 842 轮：71 条全过一轮 —— 21 改名实现 · 5 能力存在 · 40 零命中

### 第三批 39 条：9 改名，其中两条值得单说

- **`AddToCartNext`** —— R840 用 `Next` 失败，换 **`__NEXT_DATA__`** 命中 `StoreFlow.cs`。**R840 那条建议成立。**
- **`StartDailyCheckInTask`** —— `CheckIn` 命中 `NikeSteps.cs` · `PopMartEndpoints.cs` · `StoreFlowSteps.cs`。**每日签到确实有，且横跨 Nike / PopMart / 通用步。**

### 累计

| 批次 | 条数 | 改名 | 能力存在 | 探针无辨识力 | 零命中 |
|---|---|---|---|---|---|
| R840 | 7 | 3 | 0 | 1 | 3 |
| R841 | 24 | 9 | 5 | 0 | 10 |
| R842 | 39 | 9 | 0 | 3 | 27 |
| **合计** | **70** | **21** | **5** | **4** | **40** |

### 探针这条路走到头了

**那 40 条要判，需要调用图 —— 镜像里哪个流程调用它。**
**而调用图要从「函数地址」走，不是从「名字字符串」走（R828：名字串无 xref，代码地址才有）。**

> **下一阶段的工具不是 `str`，是「按地址找调用者」。**

### 四种结果不是四种程度，是四种不同的东西

| 结果 | 含义 | 能否当结论 |
|---|---|---|
| 1–5 文件 | 找到候选，**文件名本身就是证据** | 能，但要读那个文件 |
| >5 文件 | **词没用** 或 **能力很全** | 不能，要先分辨 |
| 0 命中 | 用这些词找不到 | **不能** |
| 换词仍 0 | 仍未找到 | **仍不能** |

**没有任何一格能单独读成「缺失」。而判据 (f) 要「未覆盖的每条写为什么」——「为什么」不能是「我搜过没搜到」。**

### 仍然 Unknown

**40 条的真相**（需调用图）· **3 条探针无辨识力的命中文件是否关于这件事** · **`GetCartId` 的 11 个文件里哪个是「取车 id」**
"""

BACKLOG_ADD = """

## 判据 (f) — 裁决完成一轮（R842）：21 改名 · 5 能力存在 · 4 无辨识力 · 40 零命中

| 批次 | 条数 | 改名 | 能力存在 | 无辨识力 | 零命中 |
|---|---|---|---|---|---|
| R840 | 7 | 3 | 0 | 1 | 3 |
| R841 | 24 | 9 | 5 | 0 | 10 |
| R842 | 39 | 9 | 0 | 3 | 27 |
| **合计** | **70** | **21** | **5** | **4** | **40** |

**工具**：`python analysis\\adjudicate.py`（常驻）。规则 `>5⇒无辨识力 / 1-5⇒改名 / 0⇒待判`。

### 两条亮点

**`AddToCartNext`**：R840 用 `Next` 失败 → 换 `__NEXT_DATA__` 命中 `StoreFlow.cs`。**换探针这条建议成立。**
**`StartDailyCheckInTask`**：`CheckIn` 命中 `NikeSteps.cs` / `PopMartEndpoints.cs` / `StoreFlowSteps.cs` —— **每日签到有实现，横跨 Nike/PopMart/通用步。**

### 探针到头，下一步换工具

**40 条要判需调用图：镜像里哪个流程调用它。调用图从「函数地址」走，不从「名字字符串」走**（R828：名字串无 xref）。
**下一阶段工具：按地址找调用者。**

### 四种结果不是四种程度

| 结果 | 含义 | 能否当结论 |
|---|---|---|
| 1–5 文件 | 候选，**文件名本身是证据** | 能，但要读 |
| >5 文件 | **词没用** 或 **能力很全** | 不能，先分辨 |
| 0 命中 | 用这些词找不到 | **不能** |
| 换词仍 0 | 仍未找到 | **仍不能** |

**「为什么」不能是「我搜过没搜到」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R842", BLOCKER)
    ensure(RSTATUS, "R842", BLOCKER)
    ensure(RVERDICT, "第 842 轮", VERDICT)
    ensure(BACKLOG, "R842", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R842" not in h:
        h += ("\n## R842 补充 — 裁决一轮完成（累计 21 改名 / 5 能力存在 / 40 零命中）\n\n"
              "工具 `analysis/adjudicate.py` 常驻。**`AddToCartNext` 换 `__NEXT_DATA__` 命中 —— R840 建议成立。**\n"
              "**`StartDailyCheckInTask` 确认有实现**（`CheckIn` 横跨 `NikeSteps`/`PopMartEndpoints`/`StoreFlowSteps`）。\n"
              "**探针到头**：40 条要判需**调用图**（从函数地址走，不从名字串走，R828 已证）。下一阶段工具：按地址找调用者。\n"
              "**「为什么」不能是「我搜过没搜到」。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R842"), (RSTATUS, "R842"), (RVERDICT, "第 842 轮"), (BACKLOG, "R842")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R842: all seventy-one names probed, and the probe method has run out\n\n"
         "The remaining thirty-nine go through the same table, and the script has been used three times now so it"
         " becomes permanent as analysis/adjudicate.py rather than being rewritten each round. Nine come back renamed,"
         " three hit too widely to mean anything, and twenty-seven match nothing.\n\n"
         "Two of the nine are worth naming. AddToCartNext failed on the word Next in R840 and succeeds on __NEXT_DATA__,"
         " which is the marker a Next.js page actually carries -- the advice to change the probe was correct. And"
         " StartDailyCheckInTask is implemented under CheckIn, appearing across NikeSteps, PopMartEndpoints and"
         " StoreFlowSteps, so the daily check-in exists and spans both a store and the generic step set.\n\n"
         "The cumulative tally is twenty-one renamed, five where the capability exists under another name, four where"
         " the probe carried no information, and forty that match nothing.\n\n"
         "That last number no longer means absent, and it is worth being explicit about why. AddToCartBox matched nothing"
         " until boxCart was tried; AddToCartNext needed a different word entirely; SubmitAdyenOrder matched too widely"
         " and the files it matched include AdyenGateway.cs, which is a capability that is thoroughly built and simply"
         " does not carry that name. What zero now means is that the words I have tried do not appear in the replica's"
         " source, and that is a statement about my vocabulary rather than about the replica.\n\n"
         "So the probe has reached its limit. Deciding the remaining forty needs the call graph: which image flow invokes"
         " each one. That has to run from a function address, not from a name string, because R828 established that the"
         " name strings carry no cross-references while the code addresses do. The next stage's tool is find-callers-by-"
         "address, not string search.\n\n"
         "The four outcomes of a probe are not four degrees of the same thing. One to five files is a candidate whose"
         " filenames are themselves the evidence. More than five files means either the word is generic or the"
         " capability is complete, and the hits have to be read to tell which. Zero means these words failed. A second"
         " zero after changing the word still means only that I have not thought of the right word. None of the four can"
         " be read on its own as missing -- which is the difficulty in criterion (f)'s requirement that every uncovered"
         " item state why, because the why cannot be that a search returned nothing.\n\n"
         "Unknown: the truth of the forty, needing the call graph; whether the files behind the three wide probes are"
         " about the subject; and which of the eleven CartId files actually fetches a cart id rather than consuming one"
         " as a variable.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
