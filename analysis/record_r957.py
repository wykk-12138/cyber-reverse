"""Record R957: the gateway list was an invention one layer down; selection is a filter."""

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
### 上一轮我改对了键名，**却把发明留在了下一层**（R957）

**R956 把 `paymentGateway` 换成 `paymentGatewayName`，然后写了一个常量数组
`PaymentGateways = {viva, disney, purpledot, eshopworld}` —— **那四个名字也是编的**。**

### 而查出来的是另一套机制

```
PreferredGateways     设置（有序偏好）
blockedGateways       设置（排除）
RpcGetPaymentMethods  取这家店提供哪些
ParsePaymentMethods   解析那个答案
IsWalletOnly          分类钱包类（不需要卡）
```

> **所以网关**不是一个常量** —— 它是**这家店返回的东西，被两个设置过滤**。
> 而我上一轮写的那四个名字，既不来自镜像、也不来自任何一家店的返回。**

### 改成了选择函数

```
ChooseGateway(available, preferred, blocked)
  → 偏好顺序命中且未封禁的胜出
  → 没偏好 → 取第一个未封禁的（而不是一个都不选）
  → 全被禁 / 空的 available → null
```

> **「没偏好 → 取第一个未封禁的」这一条是刻意的：
> 一家店提供支付，不能因为用户没表达偏好就失败。而这是**行为决定**，不是从列表里挑一个。****

### 而 `apple_pay` 与 `applepay` 两种拼法

**我的第一版只匹配 `applepay`，而测试里 `apple_pay` 失败了。
而两种拼法**都存在**（镜像和各家店不一致），所以两个都查。**

### 而函数数**不动**

**`ChooseGateway` 与 `IsWalletOnly` 是小的同步方法 → 被内联 → `.pdata` 不增。**
**与 R951 一致。**

> **所以这一轮的价值不在数上：它把**四轮前那 43 个函数**所依附的选择逻辑，
> 从一个编出来的常量换成了一个有证据的过滤函数。**

### 数字

| 度量 | R956 | **R957** |
|---|---|---|
| 套件 | 2101 | **2115** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,824 | **173,824（未变，内联）** |
| 产物大小 | 54,692 KB | **54,692 KB** |

### 教训

> **两轮，同一个错两次：R956 修了**键名**，却留着**取值集合**是编的；
> R957 修了取值集合，而它的形状（一个常量）仍然是编的。**
> **而两次我都以为改对了 —— 因为两次我都只改了**被上一个错误直接指出的那一样东西**。
> 而那个错误的下层还有一层，它长得不像错误，因为它是**一个数组**。**
"""

if "上一轮我改对了键名" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 957 轮：上一轮改对了键名，却把发明留在了下一层

### R956 的残留

**`PaymentGateways = {viva, disney, purpledot, eshopworld}` —— **那四个名字也是编的**。**

### 查出来的是另一套机制

```
PreferredGateways（有序偏好）· blockedGateways（排除）
RpcGetPaymentMethods（取这家店提供哪些）· ParsePaymentMethods（解析）· IsWalletOnly（钱包分类）
```

> **网关**不是常量** —— 是**这家店返回的东西被两个设置过滤**。**

### 改成选择函数

```
ChooseGateway(available, preferred, blocked)
  偏好顺序命中且未封禁 → 胜出
  没偏好 → 第一个未封禁（而不是一个都不选）
  全禁 / 空 → null
```

**「没偏好 → 第一个未封禁」是行为决定：一家店提供支付，不能因为用户没表达偏好就失败。**

### 而 `apple_pay` 与 `applepay` 两种拼法都存在

**第一版只匹配 `applepay`，测试里 `apple_pay` 失败 → 两个都查。**

### 函数数不动

**`ChooseGateway` / `IsWalletOnly` 是小的同步方法 → 内联 → `.pdata` 不增（与 R951 一致）。**

> **价值不在数上：它把四轮前那 43 个函数依附的选择逻辑，从编出来的常量换成了有证据的过滤函数。**

### 数字

| 度量 | R956 | **R957** |
|---|---|---|
| 套件 | 2101 | **2115** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,824 | **173,824（未变，内联）** |
| 产物大小 | 54,692 KB | **54,692 KB** |

### 教训

> **两轮，同一个错两次：R956 修了**键名**留着**取值集合**是编的；
> R957 修了取值集合，而它的**形状**（一个常量）仍然是编的。**
> **两次我都以为改对了 —— 因为两次我都只改了**被上一个错误直接指出的那一样东西**。
> 而错误的下层还有一层，它长得不像错误，因为它是**一个数组**。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — 网关选择改成过滤函数（R957，**改产品代码 +14 用例**）

### 镜像证据

**`PreferredGateways` · `blockedGateways` · `RpcGetPaymentMethods` · `ParsePaymentMethods` · `IsWalletOnly`**

### 改动

**`ChooseGateway(available, preferred, blocked)` · `IsWalletOnly`（两种拼法） ·
`PreferredGatewaysSetting`/`BlockedGatewaysSetting` · 派发先取 session 名、否则调 chooser**

### 删掉了

**`PaymentGateways` 常量数组（四个编出来的名字）**

### 数字

**套件 2101 → 2115 · 陈旧度 0/0 · 函数数 173,824（未变，内联）· 产物 54,692 KB**

| 仍 Unknown | |
|---|---|
| `RpcGetPaymentMethods` 的返回形状 | 未反编译 |
| `ParsePaymentMethods` 解析什么 | 只有名字 |
| 偏好/封禁设置的真实类型 | 只有名字 |

**纪律**：错误的下层还有一层，它长得不像错误，因为它是一个数组。
"""

BLOCKER = """

---

## 381. 网关选择改成过滤函数；四个编出来的名字删掉

> R957。**改产品代码 +14 用例。** 套件 **2115 通过 / 0 失败 / 0 跳过**。

### 一、R956 的残留

**`PaymentGateways = {viva, disney, purpledot, eshopworld}` —— 四个名字也是编的。**

### 二、镜像的机制

```
PreferredGateways · blockedGateways · RpcGetPaymentMethods · ParsePaymentMethods · IsWalletOnly
```

**→ 网关不是常量，是这家店返回的东西被两个设置过滤。**

### 三、改成

**`ChooseGateway(available, preferred, blocked)`：偏好顺序胜出 · 没偏好取第一个未封禁 · 全禁/空 → null**

**`IsWalletOnly`：`applepay` 与 `apple_pay` 两种拼法都查。**

### 四、函数数不动

**小的同步方法 → 内联 → `.pdata` 不增（R951 一致）。**

### 五、数字

| 度量 | R956 | R957 |
|---|---|---|
| 套件 | 2101 | **2115** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,824 | **173,824** |
| 产物大小 | 54,692 KB | **54,692 KB** |

### 六、验证

```
analysis/ida.py str gateways       -> Gateways / blockedGateways / PaymentGateways / PreferredGateways
analysis/ida.py str paymentMethods -> RpcGetPaymentMethods / ParsePaymentMethods
test --filter GatewaySelectionTests -> 12 通过
metrics_report.py                 -> 2115 通过 / 0 失败
```

### 七、仍然 Unknown

- **`RpcGetPaymentMethods` 的返回形状**：**Unknown** —— 未反编译。
- **`ParsePaymentMethods` 解析什么**：**Unknown** —— 只有名字。
- **偏好/封禁设置的真实类型**：**Unknown** —— 只有名字。

### 八、教训

**两轮，同一个错两次：修了键名留着取值集合；修了取值集合留着它的形状（一个常量）。**

**两次我都以为改对了 —— 因为两次我都只改了被上一个错误直接指出的那一样东西。**

**而错误的下层还有一层，它长得不像错误，因为它是一个数组。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R957", BLOCKER)
    ensure(RSTATUS, "R957", BLOCKER)
    ensure(RVERDICT, "第 957 轮", VERDICT)
    ensure(BACKLOG, "R957", BACKLOG_ADD)

    note = (
        "\n## R957 补充 — 网关选择改成过滤函数；四个编出来的名字删掉（+14 用例，套件 2115）\n\n"
        "R956 修了键名却把 `PaymentGateways = {viva, disney, purpledot, eshopworld}` 留着 —— 那四个名字也是编的。\n"
        "镜像的机制是：PreferredGateways / blockedGateways 两个设置 + RpcGetPaymentMethods 取 + ParsePaymentMethods 解析 "
        "+ IsWalletOnly 分类 → 网关不是常量，是这家店返回的东西被两个设置过滤。\n\n"
        "改成 ChooseGateway(available, preferred, blocked)：偏好顺序胜出 · 没偏好取第一个未封禁 · 全禁/空 → null。\n"
        "IsWalletOnly 同时查 applepay 与 apple_pay。\n\n"
        "函数数不动（小的同步方法被内联，与 R951 一致）—— 价值在把四轮前那 43 个函数依附的选择逻辑换成了有证据的。\n\n"
        "数字：套件 2101 → 2115 · 陈旧度 0/0 · 函数数 173,824 · 产物 54,692 KB。\n\n"
        "纪律：错误的下层还有一层，它长得不像错误，因为它是一个数组。\n\n"
        "下一轮：反编译 RpcGetPaymentMethods 看返回形状（唯一能定 ParsePaymentMethods 的途径）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R957" not in h:
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
             for p, k in ((RBLOCK, "R957"), (RSTATUS, "R957"), (RVERDICT, "第 957 轮"), (BACKLOG, "R957")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R957: last round fixed the key and left the invention one layer down\n\n"
         "R956 replaced an invented session key with the image's paymentGatewayName and then wrote a constant array of four\n"
         " gateways, which was the same mistake one layer deeper: viva, disney, purpledot and eshopworld came from my head,\n"
         " not from the image.\n\n"
         "Searching for how selection works found a different mechanism altogether. PreferredGateways and blockedGateways\n"
         " are settings, RpcGetPaymentMethods fetches what a shop offers, ParsePaymentMethods reads the answer, and\n"
         " IsWalletOnly classifies one kind. So the gateways are not a constant at all; they are whatever the shop returns,\n"
         " filtered by two settings.\n\n"
         "ChooseGateway replaces the array: preference order wins when the preferred method is offered and not blocked, an\n"
         " empty preference takes the first unblocked offer rather than none, and nothing offered or everything blocked\n"
         " returns null. The middle rule is a behavioural decision rather than a default -- a shop that offers payment must\n"
         " not fail because nobody expressed a preference.\n\n"
         "IsWalletOnly needed both spellings, applepay and apple_pay, because the image and the shops disagree; my first\n"
         " version matched one and the test caught the other.\n\n"
         "The count did not move, which is consistent with R951: ChooseGateway and IsWalletOnly are small synchronous methods\n"
         " and were inlined. The value here is not in the number but in replacing the logic that last round's forty-three\n"
         " functions hung from with something evidence-based.\n\n"
         "Figures: suite 2101 to 2115, freshness zero, count and artifact unchanged at 173,824 and 54,692 kilobytes.\n\n"
         "Unknown: the shape RpcGetPaymentMethods returns, which was not decompiled; what ParsePaymentMethods actually\n"
         " parses; and the real types of the two settings.\n\n"
         "The lesson is that I made the same error twice in two rounds, and both times believed it fixed: R956 corrected the\n"
         " key and left the value set invented, R957 corrected the value set and left its shape -- a constant -- invented.\n"
         " Each time I changed only the thing the previous error pointed at, and the layer beneath looked like nothing at\n"
         " all, because it was an array.\n\n"
         "Product code changed; suite green at 2115."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()