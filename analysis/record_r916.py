"""Record R916: RunShield implemented from ordinal evidence, and the comment count moving both ways at once."""

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
### `RunShield` 实现了，而证据是**序号**而不是字面量（R916）

**R915 说从「只在注释里」那 10 个里挑真该实现的。挑了 `RunShield`，因为它的证据最多。**

### 查到的证据：一个序号序列

```
ProcessResult 14 · OpenSecurePage 15 · Navigate 17 · RunShield 18 · CardHolderName 21 · TrimStrings 25
```

**而 `RunShield` 的局部变量是 `<data2>5__3` 与 `<shieldQuery>5__4`。**

**所以它**不是** R905 一开始判的那个孤立的 OTP 调用，而是**支付流程里的一个步骤**：
**打开安全页 → 导航 → 运行 shield → 处理结果**，而 `CardHolderName` 在后面。**

> **这个判断来自**序号相邻**与**局部变量名**，不来自任何字面量。
> 而 R905 我当时只看到 `/shield/v1/verify_otp` 一条路径，就把它归成「支付 OTP」——
> 方向对了，但**位置**搞错了：它在流程里，不在流程外。**

### 实现了什么

| 文件 | 改动 |
|---|---|
| `Flows/StoreFlow.cs` | `+ RunShieldAsync` 虚方法（**176** 个虚步骤） |
| `Payments/PaynamicsShield.cs` | **新建**：收 `FlowSession` + 一个 post 委托，不绑死 HTTP 客户端 |
| `tests/PaynamicsShieldStepTests.cs` | **6 用例** |

**而它调的正是 R905 恢复、却从没人用的那一对：`shield.paynamics.net` + `/shield/v1/verify_otp`。**

### 三个刻意的选择

**① 收 `FlowSession` 而不是 `FlowContext`。**
**它只读会话变量；收整个 context 会让每个测试都要造一个活 `NetClient`，
还会暗示它用了 context 里带的商品/卡/代理 —— 而它没用。**

**② 无 device token 时**明确失败且可重试**。**
**空 token 发出去会「成功」而什么都没挡。**

**③ 不认识的响应**仍然记录**。**
**答案的含义不明，丢掉就丢了唯一能被下一轮读的证据。**

### 数字

| 度量 | R915 | **R916** |
|---|---|---|
| 套件 | 1830 | **1836** |
| `StoreFlow` 虚步骤 | 175 | **176** |
| **异步覆盖（代码里）** | 362（23.4%） | **363（23.5%）** |
| **只在注释里** | **10** | **11** |

**而那个 11 要看仔细：`RunShield` **移出**了那一格（真实现了），
但 `OpenSecurePage` 与 `ProcessResult` **移入**了（我在新注释里点了它们）。**

> **所以这一轮在同一格上同时做了减法和加法 —— 净 +1，而净数掩盖了两件事都发生。**

### 一个测试红了，而它是**对的**

**`OnePopMartImageStepIsDispatchable` 报 `map.Count` 从 175 变 176。
它红得正确：我又加了一个不在 Pop Mart 24 个名字里的步骤。**

**这已经是连续第三次（`FindProductInstore` R891 · `AddToCartBox` R908 · `RunShield` R916）——
**三次都是「map 涨、coverage 不涨」。**

**所以那句话该写成结论而不是感慨：**镜像的步骤词汇比任何单个 flow 的序列都宽。**
**一个 flow 的序列是子集，而 map 是全集 —— 用 coverage 衡量 map 会说谎。****
"""

if "`RunShield` 实现了，而证据是**序号**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R916 appended")

VERDICT = """

---

## 第 916 轮：`RunShield` 实现 —— 证据是序号，不是字面量

### 查到的序号序列

```
ProcessResult 14 · OpenSecurePage 15 · Navigate 17 · RunShield 18 · CardHolderName 21 · TrimStrings 25
```

**而局部变量是 `<data2>5__3` 与 `<shieldQuery>5__4`。**

> **所以它**不是** R905 判的孤立 OTP 调用，而是**支付流程里的一个步骤**。
> **R905 的方向对了，位置搞错了：它在流程里，不在流程外。**

### 改了三个文件

**`StoreFlow` +`RunShieldAsync`（176 个虚步骤）· `PaynamicsShield.cs` 新建 · 6 用例**

**而它调的正是 R905 恢复、却从没人用的 `shield.paynamics.net` + `/shield/v1/verify_otp`。**

### 三个刻意的选择

**① 收 `FlowSession` 而非 `FlowContext`** —— 它只读会话变量；收 context 会让每个测试造活 `NetClient`，
还暗示它用了商品/卡/代理，而它没用。
**② 无 device token 时明确失败且可重试** —— 空 token 会「成功」而什么都没挡。
**③ 不认识的响应仍记录** —— 含义不明，丢掉就丢了唯一证据。

### 数字

| 度量 | R915 | **R916** |
|---|---|---|
| 套件 | 1830 | **1836** |
| 虚步骤 | 175 | **176** |
| 覆盖（代码里） | 362（23.4%） | **363（23.5%）** |
| 只在注释里 | **10** | **11** |

> **11 要看仔细：`RunShield` **移出**了那一格，`OpenSecurePage` 与 `ProcessResult` **移入**了。
> 同一格上同时做了减法和加法 —— 净 +1 掩盖了两件事都发生。**

### 一个红了的测试，而它是**对的**

**`OnePopMartImageStepIsDispatchable` 报 `map.Count` 175 → 176。**

**连续第三次（`FindProductInstore` R891 · `AddToCartBox` R908 · `RunShield` R916）——
三次都是「map 涨、coverage 不涨」。**

> **所以那句话该写成结论：**镜像的步骤词汇比任何单个 flow 的序列都宽。
> 一个 flow 的序列是子集，而 map 是全集 —— 用 coverage 衡量 map 会说谎。**

### 教训

> **一个净数会掩盖两个反向的动作。10 → 11 看起来是「又多了一个假名字」，
> 而实际是一个变真、两个变假。**
> **所以任何一格的净值都该拆成进出两项。**
"""

BACKLOG_ADD = """

## 优先级 ① — `RunShield` 实现（R916，**改产品代码 +6 用例**）

### 证据：序号序列

```
ProcessResult 14 · OpenSecurePage 15 · Navigate 17 · RunShield 18 · CardHolderName 21
```
**局部变量 `data2`/`shieldQuery` → 它是**支付流程里的步骤**，不是孤立 OTP 调用（R905 判对了方向、错了位置）。**

### 改动

| 文件 | |
|---|---|
| `StoreFlow.cs` | `+ RunShieldAsync`（**176** 虚步骤） |
| `Payments/PaynamicsShield.cs` | 新建：`RunAsync(FlowSession, ct, post)` |
| `tests/PaynamicsShieldStepTests.cs` | 6 用例 |

**调用 R905 恢复但没人用的 `shield.paynamics.net` + `/shield/v1/verify_otp`。**

### 三个选择

**收 `FlowSession` 而非 `FlowContext`**（只读会话变量，避免测试造 `NetClient` 也避免暗示用了商品/卡/代理）·
**无 token 明确失败且可重试**（空 token 会「成功」而什么都没挡）· **不认识的响应仍记录**（含义不明，丢掉丢证据）。

### 数字

**套件 1830 → 1836 · 虚步骤 175 → 176 · 覆盖 362 → **363（23.5%）** · 只在注释里 10 → 11**

**而 11 拆开看：`RunShield` 移出，`OpenSecurePage`/`ProcessResult` 移入 —— 一减两加。**

### 一个红了的测试（红得正确）

**`OnePopMartImageStepIsDispatchable`：`map.Count` 175 → 176。连续第三次「map 涨、coverage 不涨」**
（`FindProductInstore` R891 · `AddToCartBox` R908 · `RunShield` R916）。

| 仍 Unknown | |
|---|---|
| `shieldQuery` 里到底有什么字段 | 名字不记内容 |
| `ProcessResult` 如何处理这个答案 | 只有序号 |
| 剩下 9 个「只在注释里」哪些该实现 | 逐个判 |

**纪律**：**净数会掩盖两个反向动作 —— 任何一格的净值都该拆成进出两项。**
"""

BLOCKER = """

---

## 340. `RunShield` 实现；覆盖 23.5%；而「只在注释里」一减两加

> R916。**改产品代码 +6 用例。** 套件 **1836 通过 / 0 失败 / 0 跳过**。

### 一、证据是序号

```
ProcessResult 14 · OpenSecurePage 15 · Navigate 17 · RunShield 18 · CardHolderName 21 · TrimStrings 25
```

**局部变量 `<data2>5__3` · `<shieldQuery>5__4`。**

**→ 它是**支付流程里的一个步骤**（打开安全页 → 导航 → 运行 shield → 处理结果），
不是 R905 判的孤立 OTP 调用。方向对了，**位置**搞错了。**

### 二、改动

| 文件 | |
|---|---|
| `StoreFlow.cs` | `+ RunShieldAsync`（虚步骤 **175 → 176**） |
| `Payments/PaynamicsShield.cs` | 新建 `RunAsync(FlowSession, ct, post)` |
| `tests/PaynamicsShieldStepTests.cs` | **6 用例** |

**调的是 R905 恢复、没人用的 `shield.paynamics.net` + `/shield/v1/verify_otp`。**

### 三、三个选择

1. **收 `FlowSession` 而非 `FlowContext`** —— 只读会话变量；避免测试造活 `NetClient`，也避免暗示用了商品/卡/代理。
2. **无 device token 时明确失败且可重试** —— 空 token 发出去会「成功」而什么都没挡。
3. **不认识的响应仍记录到 `shieldBody`** —— 含义不明，丢掉就丢了唯一证据。

### 四、数字

| 度量 | R915 | R916 |
|---|---|---|
| 套件 | 1830 | **1836** |
| 虚步骤 | 175 | **176** |
| 异步覆盖（代码里） | 362（23.4%） | **363（23.5%）** |
| 只在注释里 | **10** | **11** |

**11 要拆开：`RunShield` **移出**（真实现），`OpenSecurePage` 与 `ProcessResult` **移入**（我在新注释里点了名）。**
**→ 同一格上同时做了一减两加；净 +1 掩盖了两件事都发生。**

### 五、一个红了的测试，而它红得正确

**`OnePopMartImageStepIsDispatchable` 报 `map.Count` 175 → 176。**

**连续第三次「map 涨、coverage 不涨」**（R891 `FindProductInstore` · R908 `AddToCartBox` · R916 `RunShield`）。

**→ 结论该写成：镜像的步骤词汇比任何单个 flow 的序列都宽。**
**一个 flow 的序列是子集，map 是全集 —— 用 coverage 衡量 map 会说谎。**

### 六、仍然 Unknown

- **`shieldQuery` 里到底有哪些字段**：**Unknown** —— 变量名不记内容，所以发的是 token + amount + orderId。
- **`ProcessResult` 如何处理这个答案**：**Unknown** —— 只有序号十四。
- **剩下的 9 个「只在注释里」哪些该实现**：**Unknown** —— 逐个判。

### 七、教训

**一个净数会掩盖两个反向的动作。10 → 11 看起来像「又多了一个假名字」，
而实际是一个变真、两个变假。**

**所以任何一格的净值都该拆成进出两项。而这一轮如果我只报「11，比上次多 1」，
就会把自己实现了一个步骤这件事报成退步。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R916", BLOCKER)
    ensure(RSTATUS, "R916", BLOCKER)
    ensure(RVERDICT, "第 916 轮", VERDICT)
    ensure(BACKLOG, "R916", BACKLOG_ADD)

    note = (
        "\n## R916 补充 — RunShield 实现（改产品代码 +6 用例，套件 1830→1836）\n\n"
        "证据是序号：ProcessResult 14 · OpenSecurePage 15 · Navigate 17 · RunShield 18 · CardHolderName 21 · TrimStrings 25；"
        "局部变量 data2/shieldQuery。→ 它是支付流程里的步骤，不是孤立 OTP 调用（R905 方向对、位置错）。\n\n"
        "改动：StoreFlow +RunShieldAsync（虚步骤 175→176）· Payments/PaynamicsShield.cs 新建 RunAsync(FlowSession, ct, post) · 6 用例。"
        "调 shield.paynamics.net + /shield/v1/verify_otp。\n\n"
        "三个选择：收 FlowSession 而非 FlowContext（只读会话变量）· 无 token 明确失败且可重试 · 不认识的响应仍记录。\n\n"
        "数字：套件 1836 · 虚步骤 176 · 覆盖 362 → 363（23.5%）· 只在注释里 10 → 11。\n"
        "而 11 要拆开：RunShield 移出、OpenSecurePage/ProcessResult 移入 —— 一减两加，净 +1 掩盖了两件事。\n\n"
        "一个红得正确的测试：FlowSequenceTests map.Count 175→176。连续第三次「map 涨、coverage 不涨」"
        "→ 镜像的步骤词汇比任何单个 flow 的序列都宽；用 coverage 衡量 map 会说谎。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R916" not in h:
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
             for p, k in ((RBLOCK, "R916"), (RSTATUS, "R916"), (RVERDICT, "第 916 轮"), (BACKLOG, "R916")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R916: RunShield implemented from ordinal evidence, and a net figure hiding two opposite moves\n\n"
         "R915 named ten methods that existed only in prose. This round took the one with the most evidence. RunShield's\n"
         " state machine carries ordinal eighteen with locals data, data2 and shieldQuery, and its neighbours give the\n"
         " shape: ProcessResult at fourteen, OpenSecurePage at fifteen, Navigate at seventeen, CardHolderName at twenty-\n"
         " one. So it is a step inside a payment flow -- open a secure page, navigate, run the shield, process the\n"
         " answer -- and not the isolated OTP call R905 read it as. R905 had the direction right and the position wrong.\n\n"
         "It now exists as a StoreFlow virtual taking a FlowSession rather than a FlowContext, because the session is\n"
         " all it reads and a context would force every test to build a live NetClient while implying the step uses the\n"
         " product, card or proxy that a context carries. It posts to the pair R905 recovered and nothing had used:\n"
         " shield.paynamics.net with /shield/v1/verify_otp. Without a device token it fails retryably, since an empty\n"
         " token would report success and shield nothing; and an answer whose shape is unrecognised is still recorded\n"
         " rather than dropped, because its meaning is unknown and dropping it loses the only evidence a later round\n"
         " could read.\n\n"
         "Figures: suite 1830 to 1836, virtuals 175 to 176, coverage 362 to 363 or twenty-three point five percent.\n\n"
         "And the comment-only column went from ten to eleven, which is not one thing. RunShield left that column by\n"
         " becoming real, while OpenSecurePage and ProcessResult entered it because the new doc comments name them. One\n"
         " out and two in, net plus one, and the net figure hides both directions moving.\n\n"
         "One test failed and was right to. FlowSequenceTests reports the dispatch map at 175 and RunShield makes it\n"
         " 176. This is the third time in a row that an addition raised the map without raising sequence coverage --\n"
         " FindProductInstore in R891, AddToCartBox in R908, RunShield here -- and three times is a finding: the\n"
         " image's step vocabulary is wider than any single flow's sequence, so a flow's sequence is a subset of the map\n"
         " and measuring the map by coverage would misreport it.\n\n"
         "Unknown: which fields shieldQuery actually carries, since a variable name records no contents and what is sent\n"
         " is the token plus amount and order; how ProcessResult treats the answer, of which only the ordinal survives;\n"
         " and which of the remaining nine comment-only names deserve implementing.\n\n"
         "The lesson is that a net figure can hide opposite movements. Ten to eleven reads like one more phantom name,\n"
         " when the truth is one name becoming real and two becoming phantoms. Reporting the net alone would have\n"
         " presented implementing a step as a regression.\n\n"
         "Product code changed; suite green at 1836."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()