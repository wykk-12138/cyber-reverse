"""Record R925: Viva closes the vendor column, and the tool that measured it had the old comment fault."""

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
### Viva 收尾：vendor **12 / 12**，而测量它的工具还带着旧毛病（R925）

**三条路径，一个版本，一台宿主：**

```
/web2/checkout/v2/chargetokens       卡 → charge token
/web2/checkout/v2/paymentdetails?ref=  按 ref 查这笔的结果
/web2/checkout/v2/transactions         交易列表
```

### 而它是四家里唯一一个**完整周期**

**token 化 → 按 ref 读结果 → 列表。第二条那个 `ref=` 是使它成为周期的原因：
**token 的答案里带着一个引用，而状态读取用这个引用寻址，不用会话标识。****

**这与支付网关的「授权后查询」同形，也是三条能放在一起的原因。**

### 卡只到一个端点

**与 Disney 一样，`chargetokens` 说的是 token 不是 pay。`ChargeTokenAsync` 收卡，另两个只收引用与窗口。
**这是由签名强制的，不是由注释说明的。****

### 而最该做对的那一格

**「token 的答案里找不到可识别的引用」是**失败**，不是半成功。**

> **一个没人能问起的 token 对下一步毫无价值。
> 而从虚无里编一个引用，会产生一个「查询一笔不存在的支付」的状态读取 —— 比失败更坏。**

### 而这一轮抓到工具自己的旧毛病

**第一次跑出来，Disney 的两台宿主报成「在 `DisneyPaymentSheet.cs`, **`VivaPayments.cs`** 里都有」。**

**因为 `VivaPayments.cs` 里有一句注释提到了 Disney。
**这正是 R915 修过的注释假阳性 —— 而那次我只修了两个方法覆盖工具，没修这个。**

**修法一致：`vendor_coverage.py` 也 `import comment_split` 并 `strip_comments(text)`。
修完表诚实了：每家恰好一个文件。**

### 数字，而 (f) 的 vendor 侧闭合

| 度量 | R924 | **R925** |
|---|---|---|
| 套件 | 1888 | **1896** |
| **vendor 命名** | 11 / 12 | **12 / 12** |
| **vendor 缺失** | 1 | **0** |

### 而 (f) 现在的完整状态

| 列 | 结果 |
|---|---|
| **store 宿主** | **24 / 27**，未匹配 3 个全是支付商（判为不需要 flow） |
| **vendor 宿主** | **12 / 12** |

> **两列都在 METRICS.md 里可复算（R921 接进去的 8 行）。**
> **所以判据 (f)「核心覆盖表可复算」这一条，从 R917 的「没有表」走到了「两列都有、都可复算、
> 未匹配的每条都写了为什么」。**

### 而 12/12 不是「都做完了」

**「named somewhere in src」的意思是**某个源文件里有这个服务的名字**，
**不证明集成完整、也不证明它正确 —— 一个常量点名一个宿主，和一条能跑的流程是两件事。**

**而这 12 家里，深做的只有 R920–R925 这六家；Cloudflare / Adyen / AYCD / PayPal 是之前就在的。**
"""

if "Viva 收尾" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R925 appended")

VERDICT = """

---

## 第 925 轮：Viva 收尾，vendor 12/12；而工具还带着旧毛病

### 三条路径，四家里唯一的**完整周期**

```
chargetokens → paymentdetails?ref= → transactions
```

> **第二条的 `ref=` 是周期成立的原因：token 的答案带着引用，状态读取用引用寻址而不是会话标识。
> 与支付网关的「授权后查询」同形。**

### 卡只到一个端点（由**签名**强制，不由注释说明）

**`ChargeTokenAsync` 收卡；另两个只收引用与窗口。**

### 而最该做对的那一格

**「token 答案里找不到可识别引用」是**失败**，不是半成功。**

> **一个没人能问起的 token 对下一步毫无价值。
> 而从虚无里编一个引用会产生「查询一笔不存在的支付」—— 比失败更坏。**

### 这一轮抓到工具自己的旧毛病

**第一次跑：Disney 两台宿主报成「在 `DisneyPaymentSheet.cs`, **`VivaPayments.cs`** 里都有」——
因为 `VivaPayments.cs` 有一句注释提到了 Disney。**

**这正是 R915 修过的注释假阳性，**而那次我只修了两个方法覆盖工具，没修这个。****

**修法一致：也 `strip_comments`。修完表诚实了：每家恰好一个文件。**

### 数字，而 (f) 的 vendor 侧闭合

| 度量 | R924 | **R925** |
|---|---|---|
| 套件 | 1888 | **1896** |
| vendor 命名 | 11 / 12 | **12 / 12** |
| vendor 缺失 | 1 | **0** |

### (f) 的完整状态

| 列 | 结果 |
|---|---|
| store 宿主 | **24 / 27**，未匹配 3 个全是支付商（判为不需要 flow） |
| vendor 宿主 | **12 / 12** |

> **两列都在 METRICS.md 里可复算（R921 接进去的 8 行）。
> 所以判据 (f) 从 R917 的「没有表」走到了「两列都有、都可复算、未匹配的每条都写了为什么」。**

### 而 12/12 不是「都做完了」

**「named somewhere in src」只说明某个文件里有这个服务的名字，不证明集成完整或正确。
深做的是 R920–R925 这六家；Cloudflare / Adyen / AYCD / PayPal 是之前就在的。**

### 教训

> **R915 我发现了注释假阳性，修了两个工具，然后**以为修完了**。
> 而同一类扫描还有第三个 —— 它就在我下一轮要用的那个工具里。**
> **修一处不等于修一类。而判断「修完了吗」的办法是问：还有谁在做同样的事？**
"""

BACKLOG_ADD = """

## 判据 (f) 闭合 — vendor **12 / 12**（R925，**改产品代码 +8 用例 + 修工具**）

### Viva（三家路径，唯一完整周期）

```
chargetokens → paymentdetails?ref= → transactions
```

**`ChargeTokenAsync` 收卡（签名强制）；`PaymentDetailsAsync` 按 ref 寻址；`TransactionsAsync` 记录可调。
**找不到引用 = 失败**，不编引用（编了会产生「查询一笔不存在的支付」）。**

### 工具修正

**`vendor_coverage.py` 也 `strip_comments` —— R915 修了两个方法覆盖工具而漏了它，
于是 `VivaPayments.cs` 里一句提到 Disney 的注释让 Disney 的宿主看起来在两个文件里。**

### (f) 最终状态

| 列 | 结果 | 在 METRICS.md |
|---|---|---|
| store 宿主 | **24 / 27**（未匹配 3 全是支付商） | ✅ |
| vendor 宿主 | **12 / 12** | ✅ |

### 数字

**套件 1888 → 1896 · vendor 命名 11/12 → **12/12** · 缺失 1 → **0****

| 仍 Unknown | |
|---|---|
| 12 个里深做了几家 | 深做 = R920–R925 六家；另四家之前就在 |
| 每家集成的正确性 | named ≠ complete ≠ correct |
| Viva 的响应体 | 无证据 |

**纪律**：**修一处不等于修一类。判断「修完了吗」的办法是问：还有谁在做同样的事？**
"""

BLOCKER = """

---

## 349. Viva 收尾：vendor 12/12，(f) 两列闭合

> R925。**改产品代码 +8 用例 + 修工具。** 套件 **1896 通过 / 0 失败 / 0 跳过**。

### 一、Viva 是四家里唯一的完整周期

```
/web2/checkout/v2/chargetokens → paymentdetails?ref= → transactions
```

**第二条的 `ref=` 是周期成立的原因：token 的答案带引用，状态读取用引用寻址。
与支付网关的「授权后查询」同形。**

**卡只到 `ChargeTokenAsync` —— 由**签名**强制，不由注释说明。**

**「找不到可识别引用」= 失败**：一个没人能问起的 token 对下一步毫无价值；
**而从虚无里编引用会产生「查询一笔不存在的支付」，比失败更坏。**

### 二、而工具还带着 R915 的旧毛病

**第一次跑：Disney 两台宿主报成在 `DisneyPaymentSheet.cs` 与 **`VivaPayments.cs`** 里都有 ——
因为后者有一句注释提到 Disney。**

**R915 我修了两个方法覆盖工具，**没修这个**。修法一致：`strip_comments`。
修完表诚实：每家恰好一个文件。**

### 三、(f) 最终状态

| 列 | 结果 | METRICS.md |
|---|---|---|
| **store 宿主** | **24 / 27**（未匹配 3 全是支付商 braintreegateway/vipps/bigcommerce） | ✅ 5 行 |
| **vendor 宿主** | **12 / 12** | ✅ 3 行 |

**→ 判据 (f)「核心覆盖表可复算」从 R917 的「没有表」走到了「两列都有、都可复算、未匹配每条都写了为什么」。**

### 四、数字

| 度量 | R924 | R925 |
|---|---|---|
| 套件 | 1888 | **1896** |
| **vendor 命名** | 11 / 12 | **12 / 12** |
| **vendor 缺失** | 1 | **0** |

### 五、而 12/12 不是「都做完了」

**`named somewhere in src` 只说明某个文件里有这个服务的名字，不证明集成完整或正确。
深做的是 R920–R925 六家；Cloudflare / Adyen / AYCD / PayPal 是之前就在的。**

### 六、验证

```
vendor_coverage.py               -> 12 named / 0 absent；每家恰好一个文件
test --filter VivaPaymentsTests  -> 8 通过
metrics_report.py                -> 1896 通过 / 0 失败
docs/METRICS.md                  -> 核心覆盖 8 行（store 5 + vendor 3）全部解析
```

### 七、仍然 Unknown

- **12 个里深做了几家**：**已知六家（R920–R925）**，另四家之前就在。
- **每家集成的正确性**：**Unknown** —— named ≠ complete ≠ correct。
- **Viva 的响应体**：**Unknown** —— 六个候选引用字段名是猜的。

### 八、教训

**R915 我发现了注释假阳性，修了两个工具，然后**以为修完了**。
而同一类扫描还有第三个 —— 它就在我下一轮要用的那个工具里。**

**修一处不等于修一类。而判断「修完了吗」的办法是问：还有谁在做同样的事？**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R925", BLOCKER)
    ensure(RSTATUS, "R925", BLOCKER)
    ensure(RVERDICT, "第 925 轮", VERDICT)
    ensure(BACKLOG, "R925", BACKLOG_ADD)

    note = (
        "\n## R925 补充 — Viva 收尾：vendor 12/12，(f) 两列闭合（改产品代码 +8 用例 + 修工具）\n\n"
        "Viva 三条：chargetokens → paymentdetails?ref= → transactions。四家里唯一完整周期（token 的答案带引用、"
        "状态读取用引用寻址）。卡只到 ChargeTokenAsync（签名强制）。找不到引用 = 失败，不编（编了会产生「查询一笔不存在的支付」）。\n\n"
        "而工具还带着 R915 的旧毛病：vendor_coverage.py 没 strip_comments，于是 VivaPayments.cs 里一句提到 Disney 的注释"
        "让 Disney 宿主看起来在两个文件里。修完每家恰好一个文件。\n\n"
        "(f) 最终：store 宿主 24/27（未匹配 3 全是支付商）· vendor 12/12 —— 两列都在 METRICS.md 可复算（8 行）。\n\n"
        "数字：套件 1888 → 1896 · vendor 命名 11/12 → 12/12 · 缺失 1 → 0。\n\n"
        "而 12/12 不是「都做完了」：named ≠ complete ≠ correct；深做的是 R920–R925 六家。\n\n"
        "纪律：修一处不等于修一类。判断「修完了吗」的办法是问 —— 还有谁在做同样的事？\n\n"
        "下一轮：(f) 已闭合，转向其他判据 —— (a) 类型级缺口 / (b) 字符串池截断文案 / (c) 产物级对照。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R925" not in h:
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
             for p, k in ((RBLOCK, "R925"), (RSTATUS, "R925"), (RVERDICT, "第 925 轮"), (BACKLOG, "R925")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R925: Viva closes the vendor column at twelve, and the tool that measured it had R915's fault\n\n"
         "Viva's three paths form the only complete cycle among the four: tokenise a card, read the outcome by the\n"
         " reference the token answer carries, then a listing. That reference is what makes it a cycle rather than one\n"
         " step, and it is why the case that matters is a token answer with no recognisable reference -- the step fails\n"
         " rather than inventing one, since an invented reference produces a status read about a charge that does not\n"
         " exist, which is worse than a failure.\n\n"
         "The card reaches one endpoint and the other two take a reference and a window. That is enforced by the\n"
         " signatures rather than stated in a note.\n\n"
         "The tool that measures this had the fault R915 fixed elsewhere. Its first run reported Disney's hosts as named\n"
         " in DisneyPaymentSheet.cs and VivaPayments.cs, because the latter's prose mentions Disney -- the same\n"
         " comment false positive, in the third scanner, because R915 fixed the two method-coverage tools and I took that\n"
         " for done. With comments stripped the table is honest: each vendor names exactly one file.\n\n"
         "Criterion (f) is now closed on both columns. Store hosts read twenty-four of twenty-seven with all three\n"
         " unmatched hosts being payment subdomains already judged not to need a flow, and vendor hosts read twelve of\n"
         " twelve. Both are computed by METRICS.md in eight rows wired in at R921, so the table is recomputable from the\n"
         " single number source rather than assembled by hand.\n\n"
         "Figures: suite 1888 to 1896, vendors named eleven of twelve to twelve, vendors absent one to zero.\n\n"
         "Twelve of twelve does not mean twelve are finished. Named somewhere in src says a file mentions a service, not\n"
         " that the integration is complete or correct; six were built between R920 and R925 and the other four predate\n"
         " them.\n\n"
         "Unknown: how deeply each of the twelve is actually integrated; whether any of the six built is correct, which\n"
         " named-ness does not say; and Viva's response bodies, of which six candidate reference field names are guesses.\n\n"
         "The lesson is that fixing one instance is not fixing a class. I found the comment false positive at R915, fixed\n"
         " two tools, and assumed the job done, while a third scanner doing the same thing sat in the tool I would need\n"
         " next. The way to judge whether a class is fixed is to ask who else does the same thing.\n\n"
         "Product code and a tool changed; suite green at 1896."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()