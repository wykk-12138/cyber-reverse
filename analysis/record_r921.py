"""Record R921: criterion (f)'s vendor column measured and wired into METRICS.md."""

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
### 判据 (f) 的另一半：vendor **5 / 12**，而缺的 7 个归成 4 家服务（R921）

**R917–R920 把 store 那一侧闭合了。这一轮量 vendor 那一侧 —— (f) 要求的表有**两栏**，我一直只报一栏。**

### 新工具 `tools/vendor_coverage.py`：12 个 vendor 宿主逐个查

| 宿主 | 条 | 服务 | 复刻件 |
|---|---|---|---|
| `challenges.cloudflare.com` | 1 | Cloudflare | **有**（`AntiBotProtocol.cs` · `AntiBotVendors.cs` · `BouncyH2Client.cs`） |
| `checkoutshopper-live.adyen.com` | 2 | Adyen | **有**（`AdyenGateway.cs` · `AdyenPayPalFlow.cs`） |
| `inbox-api.aycd.io` | 3 | AYCD | **有**（`AycdInboxClient.cs` · `AycdInboxAccount.cs`） |
| `www.paypal.com` | 4 | PayPal | **有** |
| `www.purpledotprice.com` | 1 | PurpleDot | **有**（R920 刚建） |
| `payments-panel.production.eshopworld.com` | 3 | **eShopWorld** | **无** |
| `retailer-shopifypayments-api.production.eshopworld.com` | 2 | **eShopWorld** | **无** |
| `paymentsheet-ent.wdprapps.disney.com` | 3 | **Disney** | **无** |
| `registerdisney.go.com` | 1 | **Disney** | **无** |
| `webservices.global-e.com` | 3 | **Global-e** | **无** |
| `web-dsy.global-e.com` | 1 | **Global-e** | **无** |
| `www.vivapayments.com` | 3 | **Viva** | **无** |

**所以：**5 有 7 无**，而无的那 7 条归成**4 家服务、16 条路径**：**
**eShopWorld（5）· Disney（4）· Global-e（4）· Viva（3）。**

### 而这一栏回答了 R905 撤回的那个问题

**R905 我撤回了「反爬在端点层没有具体缺口」，因为当时那两条都不是反爬。
这一轮可以给一个准确的答案：**

> **Cloudflare 是**有**的（`AntiBotProtocol.cs` / `AntiBotVendors.cs`）。
> AYCD 是有的（`AycdInboxClient.cs` —— 那正是 OTP 收件箱）。
> 而**反爬这一侧没有 7 个缺口里的任何一个** —— 缺的 7 个全是**支付/跨境商务**服务。**

**所以「优先级 ② 缺什么」的答案现在是：**在 154 条路径的范围里，它不缺端点。**
**缺的是 ①（支付）与 ③（跨境定价）。****

### 接进了 METRICS.md

**而接进去的过程踩了**两道**机制，而两道都拦对了：**

**① 第一次 `（未解析，见下方原始输出）`** —— 因为 `metrics_report.py` 的 `summary_bits` 有一个**硬编码的 patterns 表**，
而我的键不在里面。**工具不会去读任意 `key: value`，它只读它认识的键。**

**② 补了 patterns 之后仍有三个键没解析** —— 因为 R834 的**归属规则**：
每个条目只能报它自己声明的键。**我原来只声明了三个。**

> **两道都是「工具不知道我要什么」，而不是「工具坏了」。
> 而第二道是 R834 那条规则在起作用：它防止一个宽松的正则把邻近条目的数字填进这一行。**

### 数字

| 度量 | R920 | **R921** |
|---|---|---|
| 套件 | 1857 | **1857** |
| **store 宿主** | 24 / 27 | 24 / 27（已闭合） |
| **vendor 宿主** | 未测 | **5 / 12（7 缺，归 4 家服务）** |
| METRICS.md 里的核心覆盖行 | 0 | **8** |

**这一轮没有改产品代码 —— 它把 (f) 从「一半可复算」变成「两半都在 METRICS.md 里」。**
"""

if "判据 (f) 的另一半：vendor" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R921 appended")

VERDICT = """

---

## 第 921 轮：判据 (f) 的另一半 —— vendor 5/12，缺的归成 4 家服务

### 新工具 `tools/vendor_coverage.py`

| 宿主 | 服务 | 复刻件 |
|---|---|---|
| `challenges.cloudflare.com` | Cloudflare | **有** |
| `checkoutshopper-live.adyen.com` | Adyen | **有** |
| `inbox-api.aycd.io` | AYCD | **有** |
| `www.paypal.com` | PayPal | **有** |
| `www.purpledotprice.com` | PurpleDot | **有** |
| `eshopworld` ×2 | **eShopWorld（5 条）** | **无** |
| `disney` ×2 | **Disney（4 条）** | **无** |
| `global-e` ×2 | **Global-e（4 条）** | **无** |
| `www.vivapayments.com` | **Viva（3 条）** | **无** |

> **5 有 7 无，7 条归成 4 家服务、16 条路径。**

### 而这一栏回答了 R905 撤回的那个问题

**R905 撤回了「反爬在端点层没有具体缺口」。现在能给准确答案：**

> **Cloudflare 有 · AYCD 有（`AycdInboxClient.cs` 就是 OTP 收件箱）。
> 而**反爬这一侧不在 7 个缺口里任何一个** —— 缺的全是**支付/跨境商务**服务。**

**所以「优先级 ② 缺什么」的准确回答是：在 154 条路径范围内它不缺端点；缺的是 ①（支付）与 ③（跨境定价）。**

### 接进 METRICS.md 时踩了两道机制，两道都拦对了

**① 第一次「未解析」—— `summary_bits` 有**硬编码的 patterns 表**，我的键不在里面。
工具不读任意 `key: value`，只读它认识的键。**

**② 补了 patterns 后仍有三个键没解析 —— R834 的**归属规则**：每个条目只能报自己声明的键。
我原来只声明了三个。**

> **两道都是「工具不知道我要什么」，不是「工具坏了」。
> 而第二道正是 R834 那条规则的用途：防止一个宽松正则把邻近条目的数字填进这一行。**

### 数字

| 度量 | R920 | **R921** |
|---|---|---|
| 套件 | 1857 | 1857 |
| store 宿主 | 24 / 27 | 24 / 27（已闭合） |
| **vendor 宿主** | 未测 | **5 / 12** |
| METRICS.md 核心覆盖行 | 0 | **8** |

**这一轮没改产品代码 —— 它把 (f) 从「一半可复算」变成「两半都在 METRICS.md 里」。**

### 教训

> **判据 (f) 写着「站点**与**风控清单」。我连续四轮只报站点那一侧，而没人拦我 ——
> 因为判据不会自己执行。**
> **是这一轮把「与」那个字读了一遍才发现的。**
"""

BACKLOG_ADD = """

## 判据 (f) — vendor 侧：**5 / 12**（R921，**新工具 `tools/vendor_coverage.py` + 接进 METRICS**）

### 5 有

**Cloudflare（`AntiBotProtocol.cs`）· Adyen（`AdyenGateway.cs`）· AYCD（`AycdInboxClient.cs`）· PayPal · PurpleDot**

### 7 无 → 归成 4 家服务 / 16 条路径

| 服务 | 条 | 宿主 |
|---|---|---|
| **eShopWorld** | **5** | `payments-panel.production.…` · `retailer-shopifypayments-api.production.…` |
| **Disney** | **4** | `paymentsheet-ent.wdprapps.…` · `registerdisney.go.com` |
| **Global-e** | **4** | `webservices.…` · `web-dsy.…` |
| **Viva** | **3** | `www.vivapayments.com` |

### 回答 R905 的撤回

**Cloudflare 有、AYCD 有 → **反爬这一侧不在 7 个缺口里**。缺的全是支付/跨境商务。
→ 「优先级 ② 缺什么」的准确回答：在 154 条范围内它不缺端点；缺的是 ①（支付）与 ③（跨境定价）。**

### 接进 METRICS 踩两道机制（都拦对了）

**① `summary_bits` 有硬编码 patterns 表 —— 工具只读它认识的键。**
**② R834 归属规则 —— 每个条目只能报自己声明的键（我原来只声明三个）。**

### 数字

**套件 1857（不变）· vendor 5/12 · METRICS.md 核心覆盖行 0 → **8****

| 仍 Unknown | |
|---|---|
| 4 家服务各自要不要实现 | 16 条路径，无请求体 |
| Global-e 是否属优先级 ③ | 跨境定价，名字支持但未证 |
| vendor 桶之外还有没有 | 本表只覆盖「带路径的宿主」 |

**纪律**：**判据 (f) 写着「站点**与**风控清单」。我连续四轮只报站点那一侧，而没人拦我 —— 因为判据不会自己执行。**
"""

BLOCKER = """

---

## 345. 判据 (f) 的 vendor 侧：5/12，缺 7 条归 4 家服务；核心覆盖接进 METRICS

> R921。**新工具 + 改 metrics 管线，未改产品代码。** 套件 **1857 通过 / 0 失败 / 0 跳过**。

### 一、vendor 表

| 宿主 | 服务 | 复刻件 |
|---|---|---|
| `challenges.cloudflare.com`(1) | Cloudflare | **有** `AntiBotProtocol.cs` |
| `checkoutshopper-live.adyen.com`(2) | Adyen | **有** `AdyenGateway.cs` |
| `inbox-api.aycd.io`(3) | AYCD | **有** `AycdInboxClient.cs` |
| `www.paypal.com`(4) | PayPal | **有** |
| `www.purpledotprice.com`(1) | PurpleDot | **有** R920 |
| `eshopworld` ×2 (5) | **eShopWorld** | **无** |
| `disney` ×2 (4) | **Disney** | **无** |
| `global-e` ×2 (4) | **Global-e** | **无** |
| `www.vivapayments.com`(3) | **Viva** | **无** |

**→ 5 有 7 无；7 条归成 4 家服务、16 条路径。**

### 二、而这一栏回答了 R905 的撤回

**Cloudflare 有、AYCD 有 → **反爬这一侧不在 7 个缺口里任何一个**。缺的全是支付/跨境商务。**

**→ 「优先级 ② 缺什么」的准确回答：在 154 条路径范围内它不缺端点；缺的是 ①（支付）与 ③（跨境定价）。**

### 三、接进 METRICS 踩两道机制，两道都拦对了

1. **`summary_bits` 有**硬编码 patterns 表** → 我的键不在里面 → `（未解析）`。**
   **工具不读任意 `key: value`，只读它认识的键。**
2. **补 patterns 后仍有三个键没解析 → R834 的归属规则：每个条目只能报自己声明的键。**
   **我原来只声明三个。而这条规则正是防止宽松正则把邻近条目的数字填进这一行。**

### 四、数字

| 度量 | R920 | R921 |
|---|---|---|
| 套件 | 1857 | 1857 |
| store 宿主 | 24 / 27 | 24 / 27 |
| **vendor 宿主** | 未测 | **5 / 12** |
| **METRICS.md 核心覆盖行** | 0 | **8** |

### 五、验证

```
vendor_coverage.py            -> vendor 12 宿主，5 named / 7 absent
metrics_report.py             -> 8 行核心覆盖全部解析，套件 1857
docs/METRICS.md               -> 「核心覆盖：store 宿主」5 行 +「vendor 宿主」3 行
```

### 六、仍然 Unknown

- **4 家服务各自要不要实现**：**Unknown** —— 16 条路径，无请求体。
- **Global-e 是否属优先级 ③**：**Inference** —— 跨境定价，名字支持但未证。
- **vendor 桶之外还有没有**：**Unknown** —— 本表只覆盖带路径的宿主。

### 七、教训

**判据 (f) 写着「站点**与**风控清单」。我连续四轮只报站点那一侧，而**没人拦我** ——
因为判据不会自己执行。**

**是这一轮把「与」那个字读了一遍才发现的。而四轮里每一轮的数字都是真的。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R921", BLOCKER)
    ensure(RSTATUS, "R921", BLOCKER)
    ensure(RVERDICT, "第 921 轮", VERDICT)
    ensure(BACKLOG, "R921", BACKLOG_ADD)

    note = (
        "\n## R921 补充 — 判据 (f) 的 vendor 侧：5/12，缺 7 条归 4 家服务（新工具 + 接进 METRICS）\n\n"
        "vendor 12 宿主：5 有（Cloudflare / Adyen / AYCD / PayPal / PurpleDot）· 7 无，归成 4 家服务 16 条路径"
        "（eShopWorld 5 · Disney 4 · Global-e 4 · Viva 3）。\n\n"
        "而这一栏回答 R905 的撤回：Cloudflare 有、AYCD 有 → **反爬这一侧不在 7 个缺口里**，缺的全是支付/跨境商务。"
        "→ 优先级 ② 在 154 条范围内不缺端点；缺的是 ①（支付）与 ③（跨境定价）。\n\n"
        "接进 METRICS 踩两道机制（都拦对了）：summary_bits 的硬编码 patterns 表 · R834 归属规则（每条目只报自己声明的键）。\n\n"
        "数字：套件 1857（不变）· vendor 5/12 · METRICS.md 核心覆盖行 0 → 8。\n\n"
        "纪律：判据 (f) 写着「站点**与**风控清单」，我连续四轮只报站点那一侧 —— 因为判据不会自己执行。\n\n"
        "下一轮：从 4 家缺的服务里挑一家（Global-e 疑似优先级 ③，eShopWorld/Disney 疑似 ①）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R921" not in h:
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
             for p, k in ((RBLOCK, "R921"), (RSTATUS, "R921"), (RVERDICT, "第 921 轮"), (BACKLOG, "R921")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R921: criterion (f)'s vendor column, which four rounds of store work had left unmeasured\n\n"
         "Criterion (f) asks for the original's store and risk-vendor list. R917 built the store column and R918 through\n"
         " R920 closed it. The vendor column had never been measured, and the reason is plain: the criterion's word is\n"
         " \"and\", and nothing in the tooling enforced the second half. Four rounds of true numbers, one column.\n\n"
         "vendor_coverage.py now asks it per host. Five are named somewhere in src: Cloudflare in AntiBotProtocol, Adyen\n"
         " in AdyenGateway, AYCD in AycdInboxClient, PayPal, and Purple Dot which R920 added. Seven are not, and they\n"
         " resolve to four services across sixteen paths -- eShopWorld with five, Disney with four, Global-e with four and\n"
         " Viva with three.\n\n"
         "That column also answers what R905 had to withdraw. R905 retracted the claim that the anti-bot priority had a\n"
         " concrete endpoint gap, because both members of its subset turned out to be payment. Now the answer is precise:\n"
         " Cloudflare and AYCD are both present, so anti-bot is not among the seven gaps at all, and every one of them is\n"
         " payment or cross-border commerce. Within these hundred and fifty-four paths, the anti-bot priority lacks\n"
         " endpoints; what is missing belongs to checkout and to pricing.\n\n"
         "Wiring the two figures into METRICS.md met two mechanisms and both were right to refuse. summary_bits carries a\n"
         " hardcoded pattern table, so it does not read arbitrary key-value output, only keys it knows. And R834's\n"
         " ownership rule means an entry may report only the keys it declares, which is what stops a loose pattern from\n"
         " filling a neighbouring row with a number that is correct somewhere else.\n\n"
         "Figures: suite unchanged at 1857, vendor hosts five of twelve, and METRICS.md goes from no core-coverage rows to\n"
         " eight.\n\n"
         "Unknown: whether each of the four services should be integrated, across sixteen paths with no request bodies;\n"
         " whether Global-e belongs to the request layer, its name suggesting cross-border pricing but proving nothing; and\n"
         " what vendors exist beyond those carrying paths.\n\n"
         "The lesson is that no criterion executes itself. Four rounds reported a true number for the first half of a\n"
         " sentence whose second half was never checked, and only reading the word \"and\" again ended that.\n\n"
         "Tool and pipeline changed; no product code; suite green at 1857."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()