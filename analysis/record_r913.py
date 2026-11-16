"""Record R913: the Submit family split four ways, which relocates the gap."""

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
### `Submit` 族拆成四桶，而缺口位置被搬了家（R913）

**R912 之后回到优先级 ①。先按次数排结账相关缺失名，得到 244 个 —— 而**次数几乎都是 1**。**

**再看最高的三个：`SubmitShipping` 28 · `SubmitOrder` 24 · `SubmitPayment` 22 ——
**它们都在 `StoreFlow` 上。** 所以「244 个缺失」不说明结账有问题。**

### 所以拆成四桶

| 桶 | 名字 | 出现次数 | 复刻件有 |
|---|---|---|---|
| **base** | **50** | **183** | **26** |
| provider | 14 | 20 | 3 |
| platform | 9 | 11 | 2 |
| **challenge** | **20** | **26** | **3** |

**而缺口在最后两桶：**

**provider 缺：** `AdyenOrder` · `AdyenPayment` · `StripeOrder` · `UnzerOrder` · `KakaoPay` · `HpsPayment` ·
`ExternalPayment` · `WebComponent` · `SDK` · `Paypal` · `ThreeDSAuthentication`

**challenge 缺：** `RecaptchaChallenge` · `PowChallenge` · `POW` · `Challenges` · **`Fingerprint`** ·
**`ClientData`** · **`WebRtc`** · **`BrowserData`** · `Collect` · `CollectRedirect` · `CollectRedirectV2` ·
`Pat` · `Wpt` · `Render`

### 而 challenge 那桶里混了两件事

**`RecaptchaChallenge` / `PowChallenge` / `Challenges` 是**反爬挑战应答**（优先级 ②）。**

**而 `Fingerprint` / `ClientData` / `WebRtc` / `BrowserData` 是**指纹采集**（优先级 ③）——
**它们被放进同一桶只是因为名字里都带 challenge 类的词。**

**所以这一轮也把「优先级 ② 在端点层没有具体缺口」（R905 的撤回）修成了一句更准的话：
**反爬挑战应答有 3 个名字在、还有几个不在；而指纹采集那一组是优先级 ③ 的缺口，不是 ② 的。**

### 一处方法说明

**分桶按名字，而 AGENTS.md §1 的 R730 裁决说「不要用名字替代读代码」。**

**这里用名字**只为把候选分组给人挑**，不声称某个名字属于某一层。
**分错桶的代价是看一眼，不是错结论。**
"""

if "`Submit` 族拆成四桶" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R913 appended")

VERDICT = """

---

## 第 913 轮：`Submit` 族拆四桶 —— 缺口位置被搬了家

### 先否掉一个假印象

**按次数排结账相关缺失名得到 244 个，而次数几乎都是 1。
再看最高的三个 `SubmitShipping` 28 · `SubmitOrder` 24 · `SubmitPayment` 22 —— **都在 `StoreFlow` 上**。**

> **所以「244 个缺失」不说明结账有问题。它在数变体，不在数功能。**

### 四桶

| 桶 | 名字 | 出现次数 | 复刻件有 |
|---|---|---|---|
| **base** | **50** | **183** | **26** |
| provider | 14 | 20 | 3 |
| platform | 9 | 11 | 2 |
| **challenge** | **20** | **26** | **3** |

**provider 缺：** `AdyenOrder` · `AdyenPayment` · `StripeOrder` · `UnzerOrder` · `KakaoPay` · `HpsPayment` ·
`ExternalPayment` · `WebComponent` · `SDK` · `Paypal` · `ThreeDSAuthentication`

**challenge 缺：** `RecaptchaChallenge` · `PowChallenge` · `POW` · `Challenges` · **`Fingerprint`** ·
**`ClientData`** · **`WebRtc`** · **`BrowserData`** · `Collect` · `CollectRedirect` · `CollectRedirectV2` ·
`Pat` · `Wpt` · `Render`

### 而 challenge 那桶里混了两件事

> **`RecaptchaChallenge` / `PowChallenge` / `Challenges` 是反爬挑战应答（优先级 ②）。
> `Fingerprint` / `ClientData` / `WebRtc` / `BrowserData` 是**指纹采集**（优先级 ③）——
> 它们在同一桶只是因为名字里都带那类词。**

**所以 R905 那句「反爬在端点层没有具体缺口」要修成更准的：
**挑战应答有几个在、几个不在；而指纹采集那一组是 ③ 的缺口，不是 ② 的。****

### 方法说明

**分桶按名字，而 R730 裁决说「不要用名字替代读代码」。这里用名字**只为把候选分组**，
不声称某名字属于某层。分错桶的代价是看一眼，不是错结论。**

### 教训

> **一个「244 个缺失」的数让我以为结账有问题。而最高的三个名字都在。
> 所以缺口的形状不是「少 244 个」，是「基础集有一半、变体几乎没有」。**
> **这两个说法对下一步的指示完全不同。**
"""

BACKLOG_ADD = """

## 优先级 ① / ② / ③ — `Submit` 族四桶（R913，**新工具 `tools/submit_family.py`**）

### 先否掉假印象

**244 个结账相关缺失名，次数几乎都是 1；而最高的三个 `SubmitShipping` 28 · `SubmitOrder` 24 · `SubmitPayment` 22 **都在 StoreFlow 上**。
→ 「244 个缺失」在数**变体**，不在数功能。**

### 四桶

| 桶 | 名字 | 出现次数 | 有 |
|---|---|---|---|
| **base** | **50** | **183** | **26** |
| provider | 14 | 20 | 3 |
| platform | 9 | 11 | 2 |
| **challenge** | **20** | **26** | **3** |

**provider 缺 11**：`Adyen*` `StripeOrder` `UnzerOrder` `KakaoPay` `HpsPayment` `ExternalPayment` `WebComponent` `SDK` `Paypal` `ThreeDSAuthentication`
**challenge 缺 14**：`RecaptchaChallenge` `PowChallenge` `POW` `Challenges` · **`Fingerprint` `ClientData` `WebRtc` `BrowserData`** · `Collect*` `Pat` `Wpt` `Render`

### 而 challenge 桶混了两层

**挑战应答 = ②；`Fingerprint`/`ClientData`/`WebRtc`/`BrowserData` = ③（指纹采集）。**
**→ R905 的撤回要修正：挑战应答缺几个、指纹采集缺四个。**

| 仍 Unknown | |
|---|---|
| provider 缺的 11 个各自要不要 | 需读实现 |
| 指纹那四个的名字对应什么 | `ClientData` 像 Kasada |
| 分桶按名字是否可靠 | **只为分组，非结论** |

**纪律**：**缺口形状是「基础集一半、变体几乎没有」，而不是「少 244 个」—— 两句话对下一步的指示完全不同。**
"""

BLOCKER = """

---

## 337. `Submit` 族四桶：基础 26/50，challenge 3/20，provider 3/14

> R913。**新增工具，未改产品代码。**

### 一、先否掉一个假印象

**244 个结账相关缺失名，次数几乎都是 1。而最高的三个 `SubmitShipping` 28 · `SubmitOrder` 24 ·
`SubmitPayment` 22 **都在 `StoreFlow` 上**。**

**所以「244 个缺失」在数**变体**，不在数功能。**

### 二、四桶（93 个名字 / 240 次出现）

| 桶 | 名字 | 出现次数 | 复刻件有 |
|---|---|---|---|
| **base** | **50** | **183** | **26** |
| provider | 14 | 20 | 3 |
| platform | 9 | 11 | 2 |
| **challenge** | **20** | **26** | **3** |

**provider 缺 11**：`AdyenOrder` `AdyenPayment` `StripeOrder` `UnzerOrder` `KakaoPay` `HpsPayment`
`ExternalPayment` `WebComponent` `SDK` `Paypal` `ThreeDSAuthentication`

**challenge 缺 14**：`RecaptchaChallenge` `PowChallenge` `POW` `Challenges` · **`Fingerprint` `ClientData`
`WebRtc` `BrowserData`** · `Collect` `CollectRedirect` `CollectRedirectV2` `Pat` `Wpt` `Render`

### 三、而 challenge 桶混了两层

**挑战应答 = 优先级 ②。`Fingerprint` / `ClientData` / `WebRtc` / `BrowserData` = 优先级 ③（指纹采集）。**

**→ R905 那句「反爬在端点层没有具体缺口」要修成：挑战应答缺几个、**指纹采集缺四个**。**

### 四、方法说明

**分桶按名字，而 R730 裁决说「不要用名字替代读代码」。**
**这里用名字只为把候选分组；分错桶的代价是看一眼，不是错结论。**

### 五、验证

```
absent_checkout.py     -> 244 个结账相关缺失，次数几乎都是 1
submit_family.py       -> 93 个 Submit 名字 / 240 次；base 50/183/26 有 · provider 14/20/3 · platform 9/11/2 · challenge 20/26/3
StoreFlow 的 Submit 步骤 -> 26 个（含 SubmitOrder/SubmitPayment/SubmitShipping）
本轮未改产品代码；套件沿用 1815
```

### 六、仍然 Unknown

- **provider 缺的 11 个各自要不要**：**Unknown** —— 需逐个读实现。
- **指纹那四个（`ClientData` 等）对应什么**：**Unknown** —— `ClientData` 像 Kasada 的客户端数据。
- **分桶按名字是否可靠**：**Unknown，且这一轮的工具自己声明了不可靠** —— 只为分组。

### 七、教训

**一个「244 个缺失」的数让我以为结账有问题。而最高的三个名字都在。**

**所以缺口的形状不是「少 244 个」，是「**基础集有一半、变体几乎没有**」。**

**这两句话对下一步的指示完全不同：前者指向大规模重写，后者指向补变体 ——
而补变体之前要先知道每个变体差什么，那需要读实现而不是数名字。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R913", BLOCKER)
    ensure(RSTATUS, "R913", BLOCKER)
    ensure(RVERDICT, "第 913 轮", VERDICT)
    ensure(BACKLOG, "R913", BACKLOG_ADD)

    note = (
        "\n## R913 补充 — Submit 族四桶（新工具 tools/submit_family.py）\n\n"
        "先否掉假印象：244 个结账相关缺失名次数几乎都是 1；而最高的三个 SubmitShipping 28 / SubmitOrder 24 / SubmitPayment 22 都在 StoreFlow 上。\n"
        "→「244 个缺失」在数变体，不在数功能。\n\n"
        "四桶（93 名 / 240 次）：base 50/183/**26 有** · provider 14/20/3 · platform 9/11/2 · **challenge 20/26/3**。\n\n"
        "provider 缺 11：Adyen* StripeOrder UnzerOrder KakaoPay HpsPayment ExternalPayment WebComponent SDK Paypal ThreeDSAuthentication\n"
        "challenge 缺 14：RecaptchaChallenge PowChallenge POW Challenges · **Fingerprint ClientData WebRtc BrowserData** · Collect* Pat Wpt Render\n\n"
        "而 challenge 桶混了两层：挑战应答=②；Fingerprint/ClientData/WebRtc/BrowserData=③（指纹采集）。\n"
        "→ R905 的撤回要修正：挑战应答缺几个、**指纹采集缺四个**。\n\n"
        "纪律：缺口形状是「基础集一半、变体几乎没有」，不是「少 244 个」。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R913" not in h:
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
             for p, k in ((RBLOCK, "R913"), (RSTATUS, "R913"), (RVERDICT, "第 913 轮"), (BACKLOG, "R913")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R913: the Submit family splits four ways, and the gap is not where the count said\n\n"
         "Returning to the checkout priority after several rounds of tooling, the first measurement was two hundred and\n"
         " forty-four checkout-related names absent, almost all with a count of one. The three highest counts --\n"
         " SubmitShipping at twenty-eight, SubmitOrder at twenty-four, SubmitPayment at twenty-two -- are all present on\n"
         " StoreFlow. So the count was counting variants, not missing functionality.\n\n"
         "Splitting the ninety-three Submit names four ways shows where the gap is. The base set has fifty names and a\n"
         " hundred and eighty-three occurrences, twenty-six of them present. Providers are fourteen names and twenty\n"
         " occurrences with three present, platforms nine and eleven with two, and challenges twenty names and twenty-six\n"
         " occurrences with three present.\n\n"
         "So the shape is half the base and almost none of the variants, which points at adding variants rather than at\n"
         " a rewrite, and those two readings imply very different next steps.\n\n"
         "The challenge bucket turned out to hold two different concerns. Challenge response -- recaptcha, proof of work,\n"
         " and the generic challenge name -- belongs to the anti-bot priority. But fingerprint collection -- Fingerprint,\n"
         " ClientData, WebRtc, BrowserData -- belongs to the request layer. They sat together only because their names\n"
         " carry the same kind of word, so R905's withdrawal of the anti-bot claim needs amending: challenge response is\n"
         " partly present, while fingerprint collection is absent on four names and is priority three, not two.\n\n"
         "The classification is by name, which R730 rules out as a substitute for reading code. It is used here to group\n"
         " candidates for selection and never to claim a layer; a name in the wrong bucket costs a look, not a wrong\n"
         " conclusion.\n\n"
         "Unknown: whether each of the eleven absent provider variants is worth having, which needs reading each\n"
         " implementation; what the four fingerprint names correspond to, ClientData suggesting Kasada's client data; and\n"
         " whether name-based bucketing is reliable at all, which this round's own tool declines to assert.\n\n"
         "The lesson is that a large absent count can mean the opposite of what it looks like. Two hundred and\n"
         " forty-four sounds like a broken checkout, and the three names with the most occurrences were already there.\n\n"
         "New tool; no product code changed; suite carries at 1815."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()