"""Record R922: Global-e built from four literals, and the first vendor checkable against a recovered string."""

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
### Global-e 建了 —— 第一个能拿**恢复到的字符串**去核的 vendor（R922）

**R921 说从 4 家缺的服务里挑一家。挑了 Global-e，因为它的四条字面量给出的东西比之前任何一家都多。**

### 四条字面量

```
/Checkout/v2/8x1r
/Checkout/v2/8um2
/Checkout/v2/8x1r/641efc40-744a-443c-ad99-420a092c6644?gaSesID=…&ga4SID=…&chkcuid=…&isNECAllowed=true
                                    &_vwo_store=&vph=1081&vpw=2649&ift=113&utm_source=direct&utm_medium=
/Checkout/v2/{_encodedMerchantId}/641efc40-…?（同一套参数）
```

**两个商户 id、一个**模板占位符**、以及一套**完整的十参数**。**
**而第四条是 `{_encodedMerchantId}` —— 说明原版是**替换**出来的，不是常量拼接。**

### 三个可读的参数

| 参数 | 读作 |
|---|---|
| `chkcuid` | checkout customer id，字面量里是个 GUID |
| `vph` / `vpw` | 视口高 / 宽（1081 / 2649） |
| **`isNECAllowed`** | **「非欧盟国家是否允许」** |

**其余（`gaSesID` · `ga4SID` · `_vwo_store` · `ift` · `utm_*`）是分析与实验标识 —— 它们在这里只因为
**一个缺了这些参数的请求，可能和被当成不一样的请求**。**

### 而 Global-e 属哪一类，现在清楚了

**它在结账时做跨境定价与关税。所以它是**结账关注点**而不是支付网关关注点：
流程必须在订单**定价之前**到达它，而不是在付完款之后。**

**这也回答了 R921 那句 Inference（「Global-e 是否属优先级 ③」）—— 是 ③ 的**定价**职能，
但落在 ① 的结账序列里。两者不冲突。**

### 写了什么

| 成员 | |
|---|---|
| `WebServicesHost` · `DsyHost` | 两台宿主 |
| `RecoveredMerchantIds` = `8x1r` · `8um2` | 两个商户 |
| `MerchantPlaceholder` = `{_encodedMerchantId}` | 模板占位符，记下来因为它说明构造方式 |
| `SampleCheckoutCustomerId` | 字面量里那个 GUID |
| **`ParamOrder`** | **十参数的**顺序**，不只是集合** |
| `UrlFor(merchant, values)` | 按顺序拼，**空值也发** |
| `IsNonEu(code)` | **Inference，明确标注** |

### 两个刻意的决定

**① `ParamOrder` 记的是**顺序**，不是集合。**
**因为按位置比对才能发现「参数名都对但顺序变了」—— 而一个按集合比对的测试会放过它。**

**② 空值也发。**
**因为恢复到的字面量里 `_vwo_store=` 与 `utm_medium=` 本身就是空的。
**所以空参数是**正常请求的证据**，不是错误的证据。****

**③ `IsNonEu` 明确标 Inference。**
**参数名说「非欧盟」、流程需要布尔、而由一个集合得出 —— 那个集合（EEA + GB + CH）是**猜的边界**，
所以标注而非当成恢复。**

### 数字

| 度量 | R921 | **R922** |
|---|---|---|
| 套件 | 1857 | **1868** |
| **vendor 命名** | 5 / 12 | **7 / 12** |
| **vendor 缺失** | 7 | **5** |

**剩 5 个：eShopWorld（2 台）· Disney（2 台）· Viva（1 台）。**

### 教训

> **前面几家 vendor 我只能核「名字在不在」。这一家能核**形状**：路径段、参数名、参数顺序、以及空值的位置。**
> **而这四样都来自同一件事 —— 恢复到的是一条**完整 URL**，不是一条路径。**
> **所以「证据有多少」不取决于服务多复杂，取决于**镜像里存的是路径还是完整请求行**。**
"""

if "Global-e 建了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R922 appended")

VERDICT = """

---

## 第 922 轮：Global-e —— 第一个能拿恢复到的**完整 URL** 去核的 vendor

### 四条字面量给出

**两个商户 id（`8x1r` · `8um2`）· 一个模板占位符 `{_encodedMerchantId}` · **十参数的完整集合与顺序**。**

> **而模板占位符说明原版是**替换**出来的，不是常量拼接。**

### 三个可读的参数

**`chkcuid` = checkout customer id（GUID）· `vph`/`vpw` = 视口高宽（1081/2649）·
**`isNECAllowed` = 「非欧盟国家是否允许」****

**其余五个是分析与实验标识 —— 它们在这里只因为**缺了它们的请求可能被当成不一样的请求**。**

### 分类清楚了

**Global-e 在结账时做跨境定价与关税 → 是**结账关注点**，不是支付网关关注点：
流程必须在订单**定价之前**到达它。**
**这也回答了 R921 那句 Inference：它是 ③ 的**定价**职能，但落在 ① 的结账序列里 —— 两者不冲突。**

### 写了什么

**`WebServicesHost` · `DsyHost` · `RecoveredMerchantIds` · `MerchantPlaceholder` ·
`SampleCheckoutCustomerId` · **`ParamOrder`（顺序而非集合）** · `UrlFor` · `IsNonEu`（Inference）**

### 三个刻意的决定

**① `ParamOrder` 记**顺序**：按位置比对才能发现「名字都对但顺序变了」，按集合比对会放过它。
② 空值也发：恢复到的字面量里 `_vwo_store=` 与 `utm_medium=` 本身就是空的 →
**空参数是正常请求的证据，不是错误的证据**。
③ `IsNonEu` 明确标 Inference：那个集合（EEA+GB+CH）是**猜的边界**。**

### 数字

| 度量 | R921 | **R922** |
|---|---|---|
| 套件 | 1857 | **1868** |
| vendor 命名 | 5 / 12 | **7 / 12** |
| vendor 缺失 | 7 | **5** |

**剩 5 个：eShopWorld（2 台）· Disney（2 台）· Viva（1 台）。**

### 教训

> **前面几家 vendor 只能核「名字在不在」，这一家能核**形状**：路径段、参数名、顺序、空值位置。
> 四样都来自同一件事 —— 恢复到的是一条**完整 URL**，不是一条路径。**
> **所以「证据有多少」不取决于服务多复杂，取决于**镜像里存的是路径还是完整请求行**。**
"""

BACKLOG_ADD = """

## 优先级 ①/③ — Global-e 建了（R922，**改产品代码 +11 用例**）

### 证据：四条字面量，含一条完整 URL + 一个模板

```
/Checkout/v2/8x1r · /Checkout/v2/8um2
/Checkout/v2/8x1r/641efc40-…?gaSesID=…&ga4SID=…&chkcuid=…&isNECAllowed=true&_vwo_store=&vph=1081&vpw=2649&ift=113&utm_source=direct&utm_medium=
/Checkout/v2/{_encodedMerchantId}/641efc40-…?（同套）
```

### `Stores/GlobalECheckout.cs`

**`WebServicesHost`/`DsyHost` · `RecoveredMerchantIds`(8x1r,8um2) · `MerchantPlaceholder` ·
`SampleCheckoutCustomerId` · **`ParamOrder`（十参数顺序）** · `UrlFor(merchant, values)` · `IsNonEu`（Inference）**

### 三个决定

**顺序而非集合（按位置比对）· 空值也发（字面量里两个本就是空的）· `IsNonEu` 标 Inference（EEA+GB+CH 是猜的边界）**

### 分类

**跨境定价 + 关税 → 结账关注点（① 的序列里），职能属 ③ 的定价 —— 不冲突。**

### 数字

**套件 1857 → 1868 · vendor 命名 5/12 → **7/12** · 缺失 7 → **5**（eShopWorld×2 · Disney×2 · Viva×1）**

| 仍 Unknown | |
|---|---|
| 十参数里哪些必需 | 全部发出，空的也发 |
| checkout 返回什么 | 无响应证据 |
| `isNECAllowed` 的真实边界 | Inference |

**纪律**：**证据有多少不取决于服务多复杂，取决于镜像里存的是路径还是完整请求行。**
"""

BLOCKER = """

---

## 346. Global-e：vendor 5/12 → 7/12；第一个可核形状的 vendor

> R922。**改产品代码 +11 用例。** 套件 **1868 通过 / 0 失败 / 0 跳过**。

### 一、四条字面量，比之前任何一家都多

```
/Checkout/v2/8x1r · /Checkout/v2/8um2
/Checkout/v2/8x1r/641efc40-…?gaSesID=…&ga4SID=…&chkcuid=…&isNECAllowed=true
                                &_vwo_store=&vph=1081&vpw=2649&ift=113&utm_source=direct&utm_medium=
/Checkout/v2/{_encodedMerchantId}/641efc40-…?（同套）
```

**两个商户 id · 一个模板占位符（说明是**替换**构造）· 十参数完整集合与顺序。**

### 二、三个可读参数

**`chkcuid`（checkout customer id，GUID）· `vph`/`vpw`（视口 1081/2649）· `isNECAllowed`（非欧盟国家是否允许）**

### 三、分类

**跨境定价与关税 → 结账关注点（① 的序列里），职能属 ③。**
**回答 R921 的 Inference：不冲突 —— 它是 ③ 的定价职能落在 ① 的结账序列里。**

### 四、`Stores/GlobalECheckout.cs`

| 成员 | |
|---|---|
| `WebServicesHost` · `DsyHost` | 两台宿主 |
| `RecoveredMerchantIds` | `8x1r` · `8um2` |
| `MerchantPlaceholder` | `{_encodedMerchantId}` |
| `SampleCheckoutCustomerId` | 字面量里的 GUID |
| **`ParamOrder`** | **十参数的顺序，不只是集合** |
| `UrlFor` · `IsNonEu` | 构造 + Inference |

### 五、三个刻意的决定

1. **`ParamOrder` 记顺序** —— 按位置比对才能发现「名字都对但顺序变了」。
2. **空值也发** —— 恢复到的字面量里 `_vwo_store=` 与 `utm_medium=` 本就是空的，
   **所以空参数是正常请求的证据。**
3. **`IsNonEu` 标 Inference** —— EEA+GB+CH 是猜的边界。

### 六、数字

| 度量 | R921 | R922 |
|---|---|---|
| 套件 | 1857 | **1868** |
| **vendor 命名** | 5 / 12 | **7 / 12** |
| **vendor 缺失** | 7 | **5** |

**剩 5 个：`eShopWorld`（2 台）· `Disney`（2 台）· `Viva`（1 台）。**

### 七、验证

```
vendor_coverage.py                 -> 两台 global-e 宿主均 yes（GlobalECheckout.cs）；7 named / 5 absent
test --filter GlobalECheckoutTests -> 11 通过
metrics_report.py                  -> 1868 通过 / 0 失败
```

### 八、仍然 Unknown

- **十参数里哪些必需**：**Unknown** —— 全部发出，空的也发。
- **checkout 返回什么**：**Unknown** —— 无响应证据。
- **`isNECAllowed` 的真实边界**：**Inference** —— EEA+GB+CH 是猜的。

### 九、教训

**前面几家 vendor 我只能核「名字在不在」，这一家能核形状：路径段、参数名、顺序、空值位置。**

**四样都来自同一件事 —— 恢复到的是一条**完整 URL**，不是一条路径。**

**所以「证据有多少」不取决于服务多复杂，取决于镜像里存的是路径还是完整请求行。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R922", BLOCKER)
    ensure(RSTATUS, "R922", BLOCKER)
    ensure(RVERDICT, "第 922 轮", VERDICT)
    ensure(BACKLOG, "R922", BACKLOG_ADD)

    note = (
        "\n## R922 补充 — Global-e 建了（改产品代码 +11 用例，套件 1857→1868）\n\n"
        "四条字面量：两个商户 id（8x1r/8um2）· 模板占位符 {_encodedMerchantId} · 十参数完整集合与顺序。\n"
        "可读参数：chkcuid（checkout customer id）· vph/vpw（视口 1081/2649）· isNECAllowed（非欧盟国家是否允许）。\n\n"
        "分类：跨境定价与关税 → 结账关注点（① 的序列），职能属 ③。回答 R921 的 Inference：不冲突。\n\n"
        "Stores/GlobalECheckout.cs：ParamOrder 记顺序（按位置比对）· 空值也发（字面量里两个本就是空的）· "
        "IsNonEu 标 Inference。\n\n"
        "数字：套件 1868 · vendor 命名 5/12 → 7/12 · 缺失 7 → 5（eShopWorld×2 · Disney×2 · Viva×1）。\n\n"
        "纪律：证据有多少不取决于服务多复杂，取决于镜像里存的是路径还是完整请求行。\n\n"
        "下一轮：eShopWorld（5 条路径，含 APM session 轮询）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R922" not in h:
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
             for p, k in ((RBLOCK, "R922"), (RSTATUS, "R922"), (RVERDICT, "第 922 轮"), (BACKLOG, "R922")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R922: Global-e built from four literals, the first vendor checkable by shape rather than by name\n\n"
         "R921 left four services unintegrated. This round took Global-e because its four literals give more than any\n"
         " vendor so far: two merchant identifiers, a template placeholder, and a complete ten-parameter query with its\n"
         " order. The fourth literal being /Checkout/v2/{_encodedMerchantId}/ says the original builds this URL by\n"
         " substitution rather than by concatenating constants.\n\n"
         "Three parameters are legible: chkcuid is a checkout customer identifier and appears as a GUID, vph and vpw are\n"
         " a viewport's height and width, and isNECAllowed reads as whether a non-EU country is permitted. The rest are\n"
         " analytics and experimentation identifiers, which matter here only because a request missing them may be\n"
         " treated differently from one carrying them.\n\n"
         "The service classifies itself: Global-e localizes prices and duties across borders at checkout, so it is a\n"
         " checkout concern rather than a gateway, and a flow must reach it before the order is priced and not after it\n"
         " is paid. That also resolves the inference R921 left open -- it is the pricing function of the request layer\n"
         " sitting inside the checkout sequence, and the two do not conflict.\n\n"
         "Three choices are deliberate. ParamOrder records the order and not just the set, because comparing by position\n"
         " catches a reordering that comparing by set would pass. Every parameter is emitted even when empty, because the\n"
         " recovered literal carries empty values itself, so an empty one is evidence of a normal request rather than of\n"
         " a mistake. And IsNonEu is labelled inference, because the set it uses -- the EEA plus the UK and Switzerland --\n"
         " is a guess at where the boundary falls.\n\n"
         "Figures: suite 1857 to 1868, vendors named five of twelve to seven, vendors absent seven to five. What remains\n"
         " is eShopWorld on two hosts, Disney on two and Viva on one.\n\n"
         "Unknown: which of the ten parameters are required; what the checkout returns, since no response is recovered;\n"
         " and where the non-EU boundary really falls.\n\n"
         "The lesson is that how much a vendor can be checked does not depend on how complex the service is but on what\n"
         " the image stored -- a path, or a whole request line. Every earlier vendor could only be checked by name; this\n"
         " one can be checked by shape, and the difference was in the evidence rather than in the work.\n\n"
         "Product code changed; suite green at 1868."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()