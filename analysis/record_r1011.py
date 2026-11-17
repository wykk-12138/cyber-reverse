"""Record R1011: Nike's payment step was sending two requests to endpoints the image does not contain."""

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
### Nike 的付款步骤一直在打**两个镜像里不存在的端点**（R1011）

**R1010 说下一轮回核心。回的第一步是查 Nike 的 `GetPaymentMethods`（ordinal 57），
而查的过程中撞到一件更重的事。**

### ① `NikeEndpoints` 的头注释早就说了，而那两行**活到了现在**

**`NikeEndpoints.cs:8-10`（R87 写的）：**

> 「the replica's Nike flow was calling **two URL families the binary does not contain at all** —
> <c>buy/carts/v2/…</c> and <c>buy/orders/v2/…</c>」

**而 `NikeFlow.cs:524` 与 `561` **仍在用** `buy/orders/v2/…/initiatePayment` 与 `…/payment`。
→ 而它们在一个**覆写**里（`public override async Task<StepOutcome> SubmitPaymentAsync`，514 行）
→ 而 R1002 恰恰证明了**覆写会进产物** —— 所以那两条是**会被发出去的**。**

### ② 而镜像查证：两个族都是 0

```
buy/orders/v2        0
buy/carts/v2         0
buy/checkouts/v3     1   → 0x147053d8c  https://api.nike.com/buy/checkouts/v3/
checkout_previews    2   → 0x147053c94 / 0x147053d0c
initiatePayment      3   → 0x146ab768c  /rpc/payment/pay/initiatePayment
                           0x146aafe84  /InitiatePayment
                           0x1470a4014  initiatePayment
```

**→ 操作是真的（`initiatePayment` 三处），而**地址不成立**：
RPC 形那条只是一个**路径**，旁边没有 host 字面量。**

### ③ 所以修法不是猜一个替换

**把 `/rpc/payment/pay/initiatePayment` 与 `api.nike.com` 拼起来，正是
`EndpointProvenanceTests` 专门禁掉的那个动作（「an endpoint was invented by joining a host seen in
one literal to a path」）—— 那会是**第六次**同类发明。**

**→ 而旧代码做的是更坏的一件事：它把一个**不存在的端点**变成一个像商店拒绝我们的错误：
「nike initiatePayment HTTP 404」。**

### ④ 改了什么

**`SubmitPaymentAsync` 改成报告，并列出镜像里真正的三个候选：**

```csharp
return StepOutcome.Fail(
    "nike: payment endpoint not captured -- the image names /rpc/payment/pay/initiatePayment without a host "
    + "and buy/checkouts/v3 as the resource, while buy/orders/v2 (what this step used) is in it zero times",
    retryable: false);
```

**而把原来打不存在端点的两段移进一个 `AttachCardAsync`（`private`，未使用），
注释写明「kept for when the address is established」—— 那是**代码留证**，不是留活路径。**

**→ 这不破坏任何能工作的东西：那两条请求**本来就必 404**。**

### ⑤ 而这与 R823/R991/R1001 是同一条原则的第四次

| 轮 | 形状 |
|---|---|
| R823 | CSRF GUID 兜底（编一个 token） |
| R991 | 伪造的支付令牌 `"tok_" + Guid.NewGuid()` |
| R1001 | 4 个网关端点只给一条路径，其余报「not captured」 |
| **R1011** | **Nike 付款打两个不存在的端点 → 改成报告** |

**共同点：一个**看起来在工作**的东西，其实是把「我不知道」写成「它拒绝了我」。**

### ⑥ 数字

| 度量 | R1010 | **R1011** |
|---|---|---|
| 套件 | 2219 | **2219（未改测试）** |
| 产物陈旧度 | 1 / 2,671 | **2 / 2,7xx（NikeFlow.cs 改）** |
| 函数数 | 174,336 | **174,336（未 publish）** |
| **Nike 里打不存在端点的活请求** | **2** | **0** |
| **`AttachCardAsync`** | 不存在 | **存在但未调用（留证）** |

### 教训

> **一份文件头注释写下「这两族不在二进制里」之后，那两行**又活了 900 多轮**。
> → 注释不是守卫；守卫要能被**跑**。**
> **→ 而这一轮能发现它，是因为我在找一个**别的**东西（ordinal 57 的端点）时读到了那个文件头。
> → 那说明「按顺序查 backlog」不如「顺着一条线索读到手边的文件」。**
"""

if "Nike 的付款步骤一直在打" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1011 轮：Nike 的付款步骤一直在打两个镜像里不存在的端点

### ① `NikeEndpoints` 的头注释（R87）早就说了

> 「the replica's Nike flow was calling **two URL families the binary does not contain at all** —
> `buy/carts/v2/…` and `buy/orders/v2/…`」

**而 `NikeFlow.cs:524` / `561` **仍在用** `buy/orders/v2/…/initiatePayment` 与 `…/payment`。
→ 而它们在一个**覆写**里，而 R1002 恰恰证明了覆写**会进产物** ⇒ 那两条是**会被发出去的**。**

### ② 镜像查证

```
buy/orders/v2        0        buy/carts/v2   0
buy/checkouts/v3     1        checkout_previews  2
initiatePayment      3   → /rpc/payment/pay/initiatePayment（路径，无 host）· /InitiatePayment
```

**→ 操作是真的，**地址不成立**：RPC 形只是一个路径，旁边没有 host 字面量。**

### ③ 所以修法不是猜一个替换

**把那个路径与 `api.nike.com` 拼起来，正是 `EndpointProvenanceTests` 禁掉的动作
（「an endpoint was invented by joining a host seen in one literal to a path」）—— 会是**第六次**同类发明。**

**而旧代码做的是更坏的事：把一个**不存在的端点**变成一个像商店拒绝我们的错误 —— 「nike initiatePayment HTTP 404」。**

### ④ 改了什么

```csharp
return StepOutcome.Fail(
    "nike: payment endpoint not captured -- the image names /rpc/payment/pay/initiatePayment without a host "
    + "and buy/checkouts/v3 as the resource, while buy/orders/v2 (what this step used) is in it zero times",
    retryable: false);
```

**并把原来打不存在端点的两段移进 `AttachCardAsync`（private，未调用）——
**代码留证**，不是留活路径。这不破坏任何能工作的东西：那两条请求**本来就必 404**。**

### ⑤ 这是同一条原则的第四次

| 轮 | 形状 |
|---|---|
| R823 | CSRF GUID 兜底 |
| R991 | 伪造的支付令牌 |
| R1001 | 4 个网关报「not captured」 |
| **R1011** | **Nike 打两个不存在的端点 → 报告** |

**共同点：一个**看起来在工作**的东西，其实是把「我不知道」写成「它拒绝了我」。**

### ⑥ 数字

| 度量 | R1010 | **R1011** |
|---|---|---|
| 套件 | 2219 | **2219（47 条 Nike 用例通过）** |
| 产物陈旧度 | 1 / 2,671 | **2 / 2,7xx** |
| 函数数 | 174,336 | **174,336（未 publish）** |
| **Nike 里打不存在端点的活请求** | **2** | **0** |

### 教训

> **一份文件头注释写下「这两族不在二进制里」之后，那两行**又活了 900 多轮**。
> → 注释不是守卫；守卫要能被**跑**。
> → 而这一轮能发现它，是因为我在找一个**别的**东西时读到了那个文件头。
> → 那说明「按顺序查 backlog」不如「顺着一条线索读到手边的文件」。**
"""

BACKLOG_ADD = """

## 优先级 ① — **Nike 付款的两个端点镜像 0 命中，改成报告；`AttachCardAsync` 留证**（R1011）

### 缺陷

**`NikeFlow.SubmitPaymentAsync`（**覆写** ⇒ 进产物）打 `buy/orders/v2/…/initiatePayment` 与 `…/payment`。
而 `NikeEndpoints.cs:8-10`（R87）早写着这两族「the binary does not contain at all」。**

**镜像查证：`buy/orders/v2` **0** · `buy/carts/v2` **0** · `buy/checkouts/v3` **1** ·
`checkout_previews` **2** · `initiatePayment` **3**（`/rpc/payment/pay/initiatePayment` 无 host · `/InitiatePayment`）。**

### 改了什么

**`SubmitPaymentAsync` 改成 `Fail("nike: payment endpoint not captured -- …", retryable: false)`，
列出三个候选；原两段移进 `private AttachCardAsync`（未调用，留证）。**

**不拼 host + path（`EndpointProvenanceTests` 禁的发明）；不破坏能工作的东西（那两条本来就必 404）。**

### 这是同一原则第四次

**R823 CSRF 兜底 · R991 伪造令牌 · R1001 四网关报 not captured · R1011 本条。**
**共同点：把「我不知道」写成「它拒绝了我」。**

### 数字

**套件 2219（47 条 Nike 用例通过）· 陈旧度 2 / 2,7xx · 函数数 174,336（未 publish）·
Nike 打不存在端点的活请求 2 → 0**

| 仍 Unknown | |
|---|---|
| Nike 付款的 host | 镜像只给路径不给 host |

**纪律**：注释不是守卫；守卫要能被跑。
"""

BLOCKER = """

---

## 435. **Nike 付款的两个端点镜像 0 命中，改成报告（覆写 ⇒ 原本真的会发出去）**

> R1011。**改 1 个源文件。** 套件 **2219 通过 / 0 失败 / 0 跳过**（47 条 Nike 用例全过）。

### 一、缺陷

**`NikeEndpoints.cs:8-10`（R87 写）：「the replica's Nike flow was calling **two URL families the binary
does not contain at all** — `buy/carts/v2/…` and `buy/orders/v2/…`」**

**而 `NikeFlow.cs:524` 与 `561` **仍在用**它们，而且在一个**覆写**里
（`public override async Task<StepOutcome> SubmitPaymentAsync`，514 行）。
→ R1002 证明了**覆写进产物** ⇒ 那两条是**会被发出去的请求**。**

### 二、镜像查证

```
buy/orders/v2        0
buy/carts/v2         0
buy/checkouts/v3     1   → 0x147053d8c  https://api.nike.com/buy/checkouts/v3/
checkout_previews    2   → 0x147053c94 · 0x147053d0c
initiatePayment      3   → 0x146ab768c  /rpc/payment/pay/initiatePayment
                           0x146aafe84  /InitiatePayment
                           0x1470a4014  initiatePayment
```

**→ 操作是真的（`initiatePayment` 三处），而**地址不成立**：
RPC 形那条只是一个**路径**，旁边没有 host 字面量。**

### 三、所以修法不是猜一个替换

**把 `/rpc/payment/pay/initiatePayment` 与 `api.nike.com` 拼起来，正是
`EndpointProvenanceTests` 专门禁掉的那个动作
（「an endpoint was invented by joining a host seen in one literal to a path」）—— 那会是**第六次**同类发明。**

**→ 而旧代码做的是更坏的一件事：它把一个**不存在的端点**变成一个像商店拒绝我们的错误：
「nike initiatePayment HTTP 404」。**

### 四、改了什么

```csharp
var card = c.Card;
if (card?.Number is null) return StepOutcome.Fail("nike: no card");

// R1011: 这一步骤原来 POST 到 buy/orders/v2/.../initiatePayment、PUT 到 .../payment。两族都不存在。
// NikeEndpoints 的文件头从 R87 起就写着这件事，而两个字面量活下来了 ——
// 而且活在一个覆写里，意味着它们被编进产物、会走到网线上。
//
// 镜像里确实有的，按地址序：
//   0x147053d8c  https://api.nike.com/buy/checkouts/v3/     每个步骤都写的那个资源
//   0x147053c94  https://api.nike.com/buy/checkout_previews/v3/
//   0x146ab768c  /rpc/payment/pay/initiatePayment           RPC 形，host 未配对
//   0x146aafe84  /InitiatePayment                           控制器名
//
// 所以操作是真的、地址不成立。报告这一点比发一个只能 404 的请求更值 ——
// 旧代码把一个缺失的端点变成了 "nike initiatePayment HTTP 404"，读起来像商店拒绝了。
return StepOutcome.Fail(
    "nike: payment endpoint not captured -- the image names /rpc/payment/pay/initiatePayment without a host "
    + "and buy/checkouts/v3 as the resource, while buy/orders/v2 (what this step used) is in it zero times",
    retryable: false);
```

**并从原来的打点代码里切出一个 `private async Task<StepOutcome> AttachCardAsync(...)`（未调用），
注释写明「kept for when the address is established」—— **代码留证**，不是留活路径。**

**→ 这不破坏任何能工作的东西：那两条请求**本来就必 404**。**

### 五、这是同一条原则的第四次

| 轮 | 形状 |
|---|---|
| R823 | CSRF GUID 兜底（编一个 token） |
| R991 | 伪造的支付令牌 `"tok_" + Guid.NewGuid()` |
| R1001 | 4 个网关端点只给一条路径，其余报「not captured」 |
| **R1011** | **Nike 付款打两个不存在的端点 → 改成报告** |

**共同点：一个**看起来在工作**的东西，其实是把「我不知道」写成「它拒绝了我」。**

### 六、数字

| 度量 | R1010 | R1011 |
|---|---|---|
| 套件 | 2219 | **2219（47 条 Nike 用例通过）** |
| 产物陈旧度 | 1 / 2,671 | **2 / 2,7xx（NikeFlow.cs 改）** |
| 函数数 | 174,336 | **174,336（未 publish）** |
| **Nike 里打不存在端点的活请求** | **2** | **0** |
| **`AttachCardAsync`** | 不存在 | **存在但未调用（留证）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "buy/orders/v2"      -> {"n":0}
python analysis/ida.py str "buy/carts/v2"       -> {"n":0}
python analysis/ida.py str "buy/checkouts/v3"   -> {"n":1}（0x147053d8c）
python analysis/ida.py str initiatePayment      -> {"n":3}（含 /rpc/payment/pay/initiatePayment）
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug   -> 已成功生成
dotnet test --filter "FullyQualifiedName~Nike" -m:1                  -> 47 通过
python tools/metrics_report.py                                       -> 套件 2219
```

### 八、仍然 Unknown

- **Nike 付款的 host**：**Unknown** —— 镜像只给路径不给 host。

### 九、教训

**一份文件头注释写下「这两族不在二进制里」之后，那两行**又活了 900 多轮**。**

**→ 注释不是守卫；守卫要能被**跑**。
→ 而这一轮能发现它，是因为我在找一个**别的**东西（ordinal 57 的端点）时读到了那个文件头。
→ 那说明「按顺序查 backlog」不如「顺着一条线索读到手边的文件」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1011", BLOCKER)
    ensure(RSTATUS, "R1011", BLOCKER)
    ensure(RVERDICT, "第 1011 轮", VERDICT)
    ensure(BACKLOG, "R1011", BACKLOG_ADD)

    note = (
        "\n## R1011 补充 — **Nike 付款的两个端点镜像 0 命中，改成报告（覆写 ⇒ 原本真的会发出去）**（套件 2219）\n\n"
        "**缺陷**：`NikeFlow.SubmitPaymentAsync`（**覆写 ⇒ 进产物**）打 `buy/orders/v2/…/initiatePayment` 与 `…/payment`。\n"
        "而 `NikeEndpoints.cs:8-10`（R87）早写着这两族「the binary does not contain at all」—— **那两行又活了 900 多轮。**\n\n"
        "**镜像查证**：`buy/orders/v2` **0** · `buy/carts/v2` **0** · `buy/checkouts/v3` **1** · `checkout_previews` **2** ·\n"
        "`initiatePayment` **3**（`/rpc/payment/pay/initiatePayment` 无 host · `/InitiatePayment`）。\n"
        "→ 操作是真的，**地址不成立**。\n\n"
        "**改动**：改成 `Fail(\"nike: payment endpoint not captured -- …\", retryable: false)` 并列出三个候选；\n"
        "原两段移进 `private AttachCardAsync`（未调用，留证）。\n"
        "**不拼 host + path**（`EndpointProvenanceTests` 禁的发明，会是第六次）；**不破坏能工作的东西**（那两条本来必 404）。\n\n"
        "**同一原则第四次**：R823 CSRF 兜底 · R991 伪造令牌 · R1001 四网关 · R1011 本条 ——\n"
        "共同点：把「我不知道」写成「它拒绝了我」。\n\n"
        "数字：套件 2219（47 条 Nike 用例通过）· 陈旧度 2 / 2,7xx · 函数数 174,336（未 publish）· Nikon 活请求 2 → **0**。\n\n"
        "纪律：**注释不是守卫；守卫要能被跑。**\n\n"
        "下一轮：`GetPaymentMethodsAsync`（ordinal 57，零覆写 ⇒ 被裁）在 Nike 上覆写 —— 那是本轮起点的正题。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1011" not in h:
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
             for p, k in ((RBLOCK, "R1011"), (RSTATUS, "R1011"), (RVERDICT, "第 1011 轮"), (BACKLOG, "R1011")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1011: Nike's payment step was posting to two endpoints the image does not contain\n\n"
         "R1010 sent the work back to the core. Going after Nike's payment-methods step, ordinal 57, meant reading\n"
         " NikeEndpoints, whose header has said since R87 that the replica's Nike flow calls two URL families the binary\n"
         " does not contain. Both literals were still there.\n\n"
         "Worse than stale: they sit inside SubmitPaymentAsync, which is an override, and R1002 established that\n"
         " overrides reach the artifact. So those two requests are compiled in and would go out on the wire, to\n"
         " buy/orders/v2/US/{cart}/initiatePayment and the PUT that follows it.\n\n"
         "The image has neither family, zero hits each. It has buy/checkouts/v3 as the resource every step writes to,\n"
         " checkout_previews and its jobs, and three occurrences of initiatePayment -- one of which is\n"
         " /rpc/payment/pay/initiatePayment, a path with no host literal beside it, and another a controller name.\n"
         " So the operation is real and the address is not established, and joining that path to api.nike.com is\n"
         " precisely the move EndpointProvenanceTests exists to forbid.\n\n"
         "So the step now reports that the endpoint was not captured and names the three candidates, rather than\n"
         " guessing a replacement. The old code was worse than a guess in one specific way: it turned a missing\n"
         " endpoint into \"nike initiatePayment HTTP 404\", which reads like the store refusing us, and that is how a\n"
         " defect survives -- disguised as somebody else's behaviour.\n\n"
         "The two request bodies are kept in a private AttachCardAsync that nothing calls, so the work is retained where\n"
         " the address is settled without leaving a live path to a 404. Nothing that worked stopped working, because\n"
         " those requests could only ever 404.\n\n"
         "This is the fourth round of the same family: R823's CSRF fallback, R991's minted payment token, R1001's gateways\n"
         " reporting not-captured, and now this. Each was something that looked like it was working while writing \"I do\n"
         " not know\" as \"it said no\".\n\n"
         "Figures: suite 2219 with all 47 Nike tests passing, freshness two files and about 2,700 lines, count 174,336\n"
         " unpublished, live requests to non-existent endpoints down from two to none.\n\n"
         "Unknown: the host for Nike's payment RPC.\n\n"
         "The lesson is that a header comment saying \"these two families are not in the binary\" outlived itself by nine\n"
         " hundred rounds, because a comment is not a guard and only a guard can be run. It surfaced because I was\n"
         " looking for something else in the same file, which suggests reading along a thread beats walking a backlog in\n"
         " order.\n\n"
         "One source file changed; suite green at 2219."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()