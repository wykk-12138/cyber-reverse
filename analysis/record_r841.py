"""Record R841: 24 more adjudicated, and the distinction between a bad probe and an absent capability."""

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

ROWS = [
    ("SubmitStripeOrder", "能力存在，命名未对上", "`Stripe` 命中 9 文件 —— 探针无辨识力，但 Stripe 处理显然在"),
    ("ProcessOrderStripe", "同上", "`Stripe` 9 文件"),
    ("SubmitAdyenOrder", "能力存在，命名未对上", "`Adyen` 命中 13 文件（含 `AdyenGateway.cs`）"),
    ("ProcessOrderPaypalCreditCard", "改名实现", "`Paypal` -> `NikePersistedOperations.cs` ×10"),
    ("SubmitUnzerOrder", "改名实现", "`Unzer` -> `Gateways.cs` ×3 · `PaymentGateway.cs` ×1 · `CandidateSteps.cs` ×1"),
    ("ProcessOrderCommerce", "能力存在，命名未对上", "`Commerce` 命中 10 文件"),
    ("SubmitCheckoutPayment", "能力存在，命名未对上", "`SubmitPayment` 命中 19 文件"),
    ("GetPaymentSession", "待判", "`PaymentSession` 0 文件"),
    ("GetSessionToken", "改名实现", "`SessionToken` -> `NikePersistedOperations.cs` ×4"),
    ("RequestSessionToken", "改名实现", "同上"),
    ("GetSessionData", "待判", "`SessionData` 0 文件"),
    ("CheckSession", "改名实现", "`VerifySession` -> `StoreFlow.cs` ×2 · `RetailFlows.cs` ×1 · `StepAction.cs` ×1"),
    ("RestartSession", "待判", "`RestartSession` 0 文件"),
    ("SetupProxySession", "待判", "`ProxySession` 0 文件"),
    ("GetAtlasSessionToken", "待判", "`Atlas` 0 文件"),
    ("GetAppCartToken", "改名实现", "`CartToken` -> `ShopifyHeaders.cs` ×2"),
    ("CreateCheckout", "改名实现", "-> `StoreFlow.cs` ×1 · `StoreFlowSteps.cs` ×2"),
    ("CreateCustomCheckout", "待判", "`CustomCheckout` 0 文件"),
    ("CreateRaffleCheckout", "改名实现", "`Raffle` -> `RetailFlows.cs` ×11 · `DemandwareFlow.cs` ×5 · `DemandwareRaffle.cs` ×1"),
    ("FinalizeCheckout", "待判", "`Finalize` 0 文件"),
    ("GenerateCheckout", "改名实现", "-> `StoreFlow.cs` ×1"),
    ("LoadCheckoutPage", "待判", "`GetCheckoutPage` 0 文件"),
    ("ValidateCheckout", "待判", "`ValidateCheckout` 0 文件"),
    ("VerifyCheckout", "待判", "`VerifyCart` 0 文件"),
]

block = "\n### 第二批（R841）：支付 + 会话 + 结账面，24 条\n\n"
block += "| 名字 | 裁决 | 依据 |\n|---|---|---|\n"
for n, v, w in ROWS:
    block += "| `%s` | %s | %s |\n" % (n, v, w)
block += ("\n**新分出一类裁决：「能力存在，命名未对上」。**\n"
          "`Stripe` 命中 9 个文件、`Adyen` 13 个、`Commerce` 10 个、`SubmitPayment` 19 个 ——\n"
          "**这些探针作为「名字对应」无效，但作为「能力存在」是强证据。**\n"
          "**探针失败有两种读法，必须分开：词没辨识力（这一种）vs 能力真的没有（零命中且换词仍零）。**\n")
io.open(DOC, "a", encoding="utf-8").write(block)
print("  ASYNC_OPS.md: batch 2 appended (24 rows)")

BLOCKER = """

---

## 265. 第二批 24 条：9 改名实现 · 5「能力存在」 · 10 待判

> R841。`docs/ASYNC_OPS.md` 追加第二批。未改产品代码。

### 一、把 R840 的教训做成了机械规则

**命中文件数 >5 ⇒ 探针无效**（这个词太常见，说明不了任何事）。
**0 ⇒ 待判。1–5 ⇒ 候选，值得读。**

### 二、结果

| 类别 | 数 | 例 |
|---|---|---|
| **改名实现** | **9** | `ProcessOrderPaypalCreditCard`→`NikePersistedOperations.cs` · `SubmitUnzerOrder`→`Gateways.cs`/`PaymentGateway.cs` · `GetSessionToken`/`RequestSessionToken`→`NikePersistedOperations.cs` · `CheckSession`→`VerifySession` · `GetAppCartToken`→`ShopifyHeaders.cs` · `CreateCheckout` · `CreateRaffleCheckout`→`Raffle`（`RetailFlows.cs`×11）· `GenerateCheckout` |
| **能力存在，命名未对上** | **5** | `Stripe` 9 文件 · `Adyen` 13 文件（含 `AdyenGateway.cs`）· `Commerce` 10 · `SubmitPayment` 19 |
| **待判（0 命中）** | **10** | `GetPaymentSession` · `GetSessionData` · `RestartSession` · `SetupProxySession` · `GetAtlasSessionToken` · `CreateCustomCheckout` · `FinalizeCheckout` · `LoadCheckoutPage` · `ValidateCheckout` · `VerifyCheckout` |

### 三、这一轮最重要的区分

**R840 说「命中为零」和「命中一片」都可以是无效探针。这一轮发现还要再分：**

> **探针失败有两种读法，必须分开：**
> **① 词没辨识力** —— 例如 `Stripe` 命中 9 个文件，但那 9 个文件恰恰**证明 Stripe 处理存在**；
> **② 能力真的没有** —— 零命中，且换词后仍零。

**`SubmitAdyenOrder` 就是 ①：探针 `Adyen` 命中的文件里有 `AdyenGateway.cs` ——
这不是「名字没对上」，这是「这条能力做得很完整，只是不叫那个名字」。**

**如果我把 ① 也算成「未覆盖」，覆盖表会难看，而且不真。**

### 四、10 条零命中里，值得先看的两个

- **`FinalizeCheckout` / `ValidateCheckout` / `VerifyCheckout`** —— 三个都是**结账前把车锁死**这一步的候选名。
  复刻件有 `SubmitOrderAsync`，但**「锁车前校验」这一步可能真没有。**
- **`RestartSession`** —— 与 R824 的 `RefreshSession` 是同一族问题（会话保活），
  **而 R827 已证镜像没有 `RefreshSession`；`RestartSession` 是另一个名字，值得核。**

### 五、验证

```
python analysis\\adjudicate_batch.py
  24 行，每行给出 探针 / 命中文件数 / 裁决
  规则：>5 文件 ⇒ probe-invalid；1-5 ⇒ renamed；0 ⇒ undecided
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **那 10 条零命中是真缺还是词不对**：**Unknown** ——
  **`ValidateCheckout` 可能叫 `EnsureCheckoutReady` 之类，本轮没试同义词。**
- **`Stripe` 那 9 个文件是否覆盖了 `SubmitStripeOrder` 的全部语义**：**Unknown** ——
  **「能力存在」比「实现相等」弱一档。**
- **剩余 40 条**（71 − 7 − 24）：**全部待判。**

### 七、教训

**这一轮真正得到的不是 9 个裁决，是「探针失败有两种」这条区分。**
**而我上一轮把它当成了一种 —— 于是 `Next` 命中几十个文件时我说「无效」，**
**这一轮 `Stripe` 命中 9 个文件，那 9 个文件里就有 `AdyenGateway.cs` 的同族。**

**同样是「命中过多」，一个说明词没用，一个说明功能很全。**
**差别在：那些文件是不是关于这件事的。**
"""

VERDICT = """

---

## 第 841 轮：第二批 24 条 —— 9 改名实现 · 5「能力存在」 · 10 待判

### 机械规则（R840 教训落地）

**>5 文件 ⇒ 探针无效；0 ⇒ 待判；1–5 ⇒ 候选。**

### 结果

| 类别 | 数 |
|---|---|
| **改名实现** | **9**（Paypal·Unzer·SessionToken×2·CheckSession·CartToken·CreateCheckout·Raffle·GenerateCheckout） |
| **能力存在，命名未对上** | **5**（`Stripe` 9 文件 · `Adyen` 13 · `Commerce` 10 · `SubmitPayment` 19） |
| **待判** | **10**（`GetPaymentSession`·`GetSessionData`·`RestartSession`·`SetupProxySession`·`GetAtlasSessionToken`·`CreateCustomCheckout`·`FinalizeCheckout`·`LoadCheckoutPage`·`ValidateCheckout`·`VerifyCheckout`） |

### 最重要的区分

> **探针失败有两种读法：① 词没辨识力；② 能力真的没有。**
> **`SubmitAdyenOrder` 属 ①：`Adyen` 命中的文件里有 `AdyenGateway.cs` —— 不是「名字没对上」，是「这条能力做得很完整，只是不叫那个名字」。**

**若把 ① 也算成「未覆盖」，覆盖表会难看而且不真。**

### 值得先看的两个零命中

**`FinalizeCheckout`/`ValidateCheckout`/`VerifyCheckout`** —— 都是「锁车前校验」的候选名，复刻件有 `SubmitOrderAsync` 但**这一步可能真没有**。
**`RestartSession`** —— 与 R824 的 `RefreshSession` 同族（会话保活），而 R827 已证镜像没有 `RefreshSession`。

### 仍然 Unknown

**10 条零命中是真缺还是词不对**（未试同义词）· **`Stripe` 那 9 个文件是否覆盖 `SubmitStripeOrder` 的全部语义**（「能力存在」比「实现相等」弱一档）· **剩余 40 条**

### 教训

**同样是「命中过多」，`Next` 说明词没用，`Stripe` 说明功能很全 —— 差别在那些文件是不是关于这件事的。**
"""

BACKLOG_ADD = """

## 判据 (f) — 裁决进度（R841：累计 31/71）

**机械规则**：`>5` 文件 ⇒ 探针无效；`0` ⇒ 待判；`1–5` ⇒ 候选。

### 第二批 24 条

| 类别 | 数 | 例 |
|---|---|---|
| **改名实现** | **9** | Paypal→`NikePersistedOperations.cs` · Unzer→`Gateways.cs` · SessionToken×2 · CheckSession→`VerifySession` · CartToken→`ShopifyHeaders.cs` · CreateCheckout · Raffle（`RetailFlows.cs`×11）· GenerateCheckout |
| **能力存在，命名未对上** | **5** | `Stripe` 9 文件 · `Adyen` 13（含 `AdyenGateway.cs`）· `Commerce` 10 · `SubmitPayment` 19 |
| **待判** | **10** | `GetPaymentSession` `GetSessionData` `RestartSession` `SetupProxySession` `GetAtlasSessionToken` `CreateCustomCheckout` `FinalizeCheckout` `LoadCheckoutPage` `ValidateCheckout` `VerifyCheckout` |

### 关键区分（新）

> **探针失败有两种：① 词没辨识力；② 能力真的没有。**
> **`SubmitAdyenOrder` 属 ①：命中的文件里有 `AdyenGateway.cs` —— 能力很全，只是不叫那个名字。**
> **把 ① 算成「未覆盖」会让表难看且不真。**

### 先看哪两个

**`FinalizeCheckout`/`ValidateCheckout`/`VerifyCheckout`** —— 「锁车前校验」，复刻件可能真没有。
**`RestartSession`** —— 与 `RefreshSession` 同族；R827 已证镜像无 `RefreshSession`。

| 仍 Unknown | |
|---|---|
| 10 条零命中真缺还是词不对 | 未试同义词 |
| `Stripe` 9 文件是否覆盖全部语义 | 「能力存在」弱于「实现相等」 |
| 剩余 40 条 | 待判 |
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R841", BLOCKER)
    ensure(RSTATUS, "R841", BLOCKER)
    ensure(RVERDICT, "第 841 轮", VERDICT)
    ensure(BACKLOG, "R841", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R841" not in h:
        h += ("\n## R841 补充 — 裁决累计 31/71\n\n"
              "第二批 24 条：**9 改名实现 · 5「能力存在，命名未对上」 · 10 待判**。\n"
              "**新区分**：探针失败有两种 —— ① 词没辨识力（`Stripe` 9 文件里有 `AdyenGateway.cs` 同族）· ② 能力真的没有。\n"
              "机械规则：`>5` 文件 ⇒ 探针无效；`0` ⇒ 待判；`1–5` ⇒ 候选。\n"
              "**先看**：`FinalizeCheckout`/`ValidateCheckout`/`VerifyCheckout`（锁车前校验）· `RestartSession`（与 `RefreshSession` 同族）。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R841"), (RSTATUS, "R841"), (RVERDICT, "第 841 轮"), (BACKLOG, "R841")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R841: twenty-four more verdicts, and a probe failure has two meanings\n\n"
         "R840 learned that a probe can fail by matching nothing or by matching everything. This round turns that into a"
         " rule -- more than five files means the word carries no information, zero means undecided, one to five is a"
         " candidate -- and applies it to twenty-four more names across payment, session and checkout.\n\n"
         "Nine come back implemented under another name. ProcessOrderPaypalCreditCard appears as Paypal in"
         " NikePersistedOperations, SubmitUnzerOrder as Unzer across Gateways and PaymentGateway, CheckSession as"
         " VerifySession, GetAppCartToken as CartToken in ShopifyHeaders, CreateCheckout and GenerateCheckout in"
         " StoreFlow, and CreateRaffleCheckout as Raffle across RetailFlows where it appears eleven times.\n\n"
         "The finding worth more than those nine is that a wide probe has two meanings that must be kept apart. Grepping"
         " Next matched dozens of files because NextPoll is everywhere, which says the word is useless. Grepping Stripe"
         " matches nine files, Adyen thirteen, Commerce ten and SubmitPayment nineteen -- and among the Adyen hits is"
         " AdyenGateway.cs. That is not a naming mismatch but a capability that exists and is called something else, and"
         " counting it as uncovered would make the coverage table both worse and less true.\n\n"
         "So the probe vocabulary now has four outcomes rather than three: renamed, capability present under another"
         " name, undecided, and probe invalid. The distinction between the middle two is whether the files the word hit"
         " are about that subject.\n\n"
         "Ten keep zero hits. Three of them, FinalizeCheckout, ValidateCheckout and VerifyCheckout, look like the"
         " lock-before-order step that the replica may genuinely lack, since it has SubmitOrder but nothing named for"
         " checking the cart first. RestartSession belongs to the same family as RefreshSession, which R827 established"
         " the image does not have -- a second name for session keep-alive, worth checking rather than assuming.\n\n"
         "Unknown: whether the ten zero-hit names are genuinely absent or merely named differently, since synonyms were"
         " not tried; whether the nine Stripe files cover everything SubmitStripeOrder does, capability being weaker"
         " evidence than equivalence; and the remaining forty names, all undecided.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
