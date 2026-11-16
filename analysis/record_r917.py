"""Record R917: criterion (f) gets a table, and the table needed two corrections before it was worth reading."""

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
### 判据 (f) 终于有了表，而表在能读之前要修两次（R917）

**判据 (f)：核心覆盖表可复算 —— 原版站点与风控清单从二进制取证 ↔ `Registry.cs` 与 `Flows/Scripts`，
未覆盖的每条写为什么。**

**核了一遍：METRICS.md 里**没有这一栏**。判据 (f) 一直未满足。**

### 左右两边各自是什么

| 边 | 来源 | 数 |
|---|---|---|
| **左** | `Registry.cs` | **64 个注册**（33 个 flow 类型，含 `HybrisFlow("offspring", …)` 这种带参数） |
| **右** | 镜像 154 条路径的宿主 | **39 个宿主**（store 28 · vendor 11） |

**新工具 `tools/core_coverage.py`：逐宿主比对。**

### 而它修了两次才可信

**① 第一次：只查 `Registry.cs` → `www.vans.com` 判成 unmatched。**
**而 R899 已经证明 Vans 是处理的 —— 在 `DemandwareControllers.cs` 的 site-id 表里，不在 Registry。**
**→ 来源太窄，与 R911 的 `Async` 后缀同一类错。改成扫全 `src`：**7/28 → 16/28**。**

**② 第二次：`api-search.dickssportinggoods.com` 取成标签 `api-search`，
`prod-hk-actapi.popmart.com` 取成 `prod-hk-actapi` —— **而 Pop Mart 明明是一个 flow。****
**→ 假设「子域要么整体泛用、要么整体有意义」，而连字符前缀两者都不是。
改成**每一段都当候选**（`search`/`dickssportinggoods`、`actapi`/`popmart`）：**16/28 → 22/28**。**

### 最终

| 桶 | 匹配 | 未匹配 |
|---|---|---|
| **store** | **22 / 28** | **6** |
| vendor | **2 / 11** | **9** |

**store 那 6 个：**

```
api.braintreegateway.com        (2)   —— 支付商，不是店
api.vipps.no                    (1)   —— 挪威支付商
checkout.sportsshoes.com        (1)   —— 真店
payments.bigcommerce.com        (1)   —— 支付商
payments.dickssportinggoods.com (2)   —— 真店（但走的是支付子域）
www.purpledotprice.com          (1)   —— 未知
```

**vendor 那 9 个：** `aycd` · `eshopworld` ×2 · `disney` ×2 · `global-e` ×2 · `vivapayments` ·
`checkoutshopper-live.adyen`（脚本层都还没有）。

### 而 22/28 这个数要怎么读

**「matched」的意思是**某个候选标签出现在 `src` 的某个文件里** ——
不证明那个店能用，也不证明它的结账流程对。**

**而「unmatched」现在是一个**更强**的说法（因为搜索面已经扩到全 `src`）：
**这个标签在整个复刻件里一次都没出现。****

**所以那 6 个里，`checkout.sportsshoes.com` 与 `payments.dickssportinggoods.com` 是真缺口；
另 4 个是支付商的子域，可能根本不需要 flow。**

### 数字

| 度量 | R916 | **R917** |
|---|---|---|
| 套件 | 1836 | **1836** |
| **store 宿主覆盖** | 无此栏 | **22 / 28** |
| vendor 宿主覆盖 | 无此栏 | **2 / 11** |

**这一轮没有改产品代码 —— 它把判据 (f) 从「没有表」变成「有一张带注脚的表」。**

### 教训

> **一张表修两次才可信，而两次都是**来源或形状假设太窄**：
> 第一次只查一个文件，第二次只取一个段。**
> **而两次修之前，数都看起来正常：7/28 和 16/28 都是「有零有整」的数，读起来不像坏了。**
"""

if "判据 (f) 终于有了表" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R917 appended")

VERDICT = """

---

## 第 917 轮：判据 (f) 终于有了表，而表在能读之前要修两次

### 核了一遍：METRICS.md 里没有这一栏

**判据 (f)：核心覆盖表可复算。** 一直未满足。**

### 两边

| 边 | 来源 | 数 |
|---|---|---|
| **左** | `Registry.cs` | **64 个注册**（33 个 flow 类型，含带参数的 `HybrisFlow("offspring", …)`） |
| **右** | 镜像 154 条路径的宿主 | **39 个宿主**（store 28 · vendor 11） |

**新工具 `tools/core_coverage.py`。**

### 修了两次

**① 只查 `Registry.cs` → `www.vans.com` 判 unmatched。而 R899 已证明 Vans 在
`DemandwareControllers.cs` 的 site-id 表里。→ 来源太窄，与 R911 同一类错。扫全 `src`：7/28 → 16/28。**

**② `api-search.dickssportinggoods.com` 取成 `api-search`、`prod-hk-actapi.popmart.com` 取成 `prod-hk-actapi`
—— 而 Pop Mart 是个 flow。→ 假设「子域整体泛用或整体有意义」，而连字符前缀两者都不是。
每段都当候选：16/28 → 22/28。**

### 最终

| 桶 | 匹配 | 未匹配 |
|---|---|---|
| **store** | **22 / 28** | **6** |
| vendor | **2 / 11** | **9** |

**store 那 6 个：** `api.braintreegateway.com`（支付商）· `api.vipps.no`（支付商）·
**`checkout.sportsshoes.com`（真店）** · `payments.bigcommerce.com`（支付商）·
**`payments.dickssportinggoods.com`（真店）** · `www.purpleprice.com`（未知）

### 22/28 怎么读

> **「matched」= 某候选标签出现在 `src` 某文件里 —— 不证明那个店能用，也不证明结账流程对。
> 「unmatched」现在是更强的说法（搜索面已扩到全 `src`）：**这个标签在整个复刻件里一次都没出现。****

**所以 6 个里 `sportsshoes` 与 `dickssportinggoods` 是真缺口，另 4 个是支付商子域，可能不需要 flow。**

### 教训

> **两次修之前，数都看起来正常：7/28 和 16/28 都是「有零有整」的数，读起来不像坏了。**
> **所以「有零有整」不说明判据对 —— 只有拿一个已知答案去试（Vans）才说明。**
"""

BACKLOG_ADD = """

## 判据 (f) — 核心覆盖表（R917，**新工具 `tools/core_coverage.py`，未改产品代码**）

### 之前：METRICS.md 无此栏 → 判据 (f) 未满足

### 两边

| 边 | 来源 | 数 |
|---|---|---|
| 左 | `Registry.cs` | **64 注册 / 33 flow 类型** |
| 右 | 镜像 154 条路径宿主 | **39 宿主**（store 28 · vendor 11） |

### 两次修正（都是来源/形状假设太窄）

**① 只查 Registry.cs → `www.vans.com` unmatched（R899 已证它在 DemandwareControllers 的 site-id 表里）
→ 扫全 src：7/28 → 16/28。**
**② `api-search.dickssportinggoods.com` 取成 `api-search`、`prod-hk-actapi.popmart.com` 取成 `prod-hk-actapi`
→ 每段都当候选：16/28 → 22/28。**

### 结果

| 桶 | 匹配 | 未匹配 |
|---|---|---|
| **store** | **22 / 28** | **6** |
| vendor | **2 / 11** | **9** |

**store 未匹配 6：** `braintreegateway`(支付商) `vipps`(支付商) **`sportsshoes`(真店)** `bigcommerce`(支付商)
**`dickssportinggoods`(真店)** `purpledotprice`(未知)
**vendor 未匹配 9：** `aycd` `eshopworld`×2 `disney`×2 `global-e`×2 `vivapayments` `adyen`（脚本层都没有）

### 判据 (f) 现在的状态

**有表、可复算、每条带注脚。** 未覆盖项的原因已写出，但**「为什么」需要逐条判定** —— 6 个 store 里 2 个是真缺口，
4 个是支付商子域（可能不需要 flow），vendor 9 个是脚本层的缺口。

| 仍 Unknown | |
|---|---|
| `purpledotprice` 是什么 | 只有一条路径 |
| vendor 9 个各属哪个优先级 | 需逐个判 |
| 32 个 store 宿主里那 6 个之外还有没有 | 本表只覆盖「有路径的宿主」 |

**纪律**：**「有零有整」不说明判据对 —— 只有拿一个已知答案去试才说明。**
"""

BLOCKER = """

---

## 341. 判据 (f) 有了表：store 22/28 · vendor 2/11

> R917。**新工具，未改产品代码。** 套件沿用 **1836 通过 / 0 失败**。

### 一、先确认了一件坏事

**判据 (f) 要求「核心覆盖表可复算」，而 METRICS.md 里**没有这一栏**。一直未满足。**

### 二、两边

| 边 | 来源 | 数 |
|---|---|---|
| 左 | `Registry.cs` | **64 个注册 / 33 个 flow 类型** |
| 右 | 镜像 154 条路径的宿主 | **39 个宿主**（store 28 · vendor 11） |

### 三、工具修了两次才可信

**① 只查 `Registry.cs` → `www.vans.com` 判 unmatched。
而 R899 已证明 Vans 在 `DemandwareControllers.cs` 的 site-id 表里。
→ **来源太窄**，与 R911 的 `Async` 后缀同一类错。扫全 `src`：**7/28 → 16/28**。**

**② `api-search.dickssportinggoods.com` 取成 `api-search`、`prod-hk-actapi.popmart.com` 取成 `prod-hk-actapi`
—— 而 Pop Mart 是个 flow。
→ **形状假设太窄**（以为子域整体泛用或整体有意义，而连字符前缀两者都不是）。每段都当候选：**16/28 → 22/28**。**

### 四、结果

| 桶 | 匹配 | 未匹配 |
|---|---|---|
| **store** | **22 / 28** | **6** |
| vendor | **2 / 11** | **9** |

**store 未匹配：** `api.braintreegateway.com`(2) · `api.vipps.no`(1) · **`checkout.sportsshoes.com`(1)** ·
`payments.bigcommerce.com`(1) · **`payments.dickssportinggoods.com`(2)** · `www.purpledotprice.com`(1)

**vendor 未匹配：** `inbox-api.aycd.io`(3) · `payments-panel.production.eshopworld.com`(3) ·
`paymentsheet-ent.wdprapps.disney.com`(3) · `retailer-shopifypayments-api.production.eshopworld.com`(2) ·
`webservices.global-e.com`(3) · `web-dsy.global-e.com`(1) · `www.vivapayments.com`(3) ·
`checkoutshopper-live.adyen.com`(2) · `registerdisney.go.com`(1)

### 五、22/28 的正确读法

**matched = 某候选标签出现在 `src` 某文件里。不证明那个店能用，也不证明结账流程对。**

**unmatched 现在是更强的说法（搜索面已扩到全 `src`）：这个标签在整个复刻件里一次都没出现。**

**→ 6 个里 `sportsshoes` 与 `dickssportinggoods` 是真缺口；另 4 个是支付商子域，可能不需要 flow。**

### 六、验证

```
python tools/core_coverage.py     -> 39 宿主（store 28 · vendor 11）；store 22/28；vendor 2/11
Registry.cs                      -> 64 个 FlowStoreModule(new X)；33 个不同 flow 类型
metrics_report.py                -> 1836 通过 / 0 失败
```

### 七、仍然 Unknown

- **`www.purpledotprice.com` 是什么**：**Unknown** —— 只有一条路径。
- **vendor 那 9 个各属哪个优先级**：**Unknown** —— 需逐个判。
- **「有路径的宿主」之外还有没有 store**：**本表只覆盖有路径的宿主**，
  **而 `Registry.cs` 有 64 个注册、镜像宿主只有 39 个 —— 两边数量本身就不对应，
  所以这张表不是一个完整的一一对照。**

### 八、教训

**两次修之前，数都看起来正常：7/28 和 16/28 都是「有零有整」的数，读起来不像坏了。**

**只有拿一个**已知答案**去试（Vans 一定该匹配）才把第一次的错暴露出来。**

**所以「数看起来合理」不验证判据 —— 一个已知的正例才验证。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R917", BLOCKER)
    ensure(RSTATUS, "R917", BLOCKER)
    ensure(RVERDICT, "第 917 轮", VERDICT)
    ensure(BACKLOG, "R917", BACKLOG_ADD)

    note = (
        "\n## R917 补充 — 判据 (f) 有了表（新工具 tools/core_coverage.py，未改产品代码）\n\n"
        "先确认：METRICS.md 里没有「核心覆盖」这一栏 → 判据 (f) 一直未满足。\n\n"
        "两边：Registry.cs 64 注册 / 33 flow 类型；镜像 154 条路径 39 宿主（store 28 · vendor 11）。\n\n"
        "工具修两次：① 只查 Registry.cs → vans 判 unmatched（R899 已证它在 DemandwareControllers 的 site-id 表里）"
        "→ 扫全 src：7/28 → 16/28。② api-search.dickssportinggoods 取成 api-search、prod-hk-actapi.popmart 取成 "
        "prod-hk-actapi（而 PopMart 是 flow）→ 每段都当候选：16/28 → 22/28。\n\n"
        "结果：store 22/28（未匹配 6）· vendor 2/11（未匹配 9）。\n"
        "store 6 里 sportsshoes 与 dickssportinggoods 是真缺口，另 4 个是支付商子域。\n\n"
        "matched = 标签出现在 src 某文件里（不证明店能用）；unmatched = 标签全库没出现（更强）。\n\n"
        "而 Registry 64 注册 vs 镜像 39 宿主 → 数量本身不对应，这不是完整的一一对照。\n\n"
        "下一轮：store 那 2 个真缺口（sportsshoes / dickssportinggoods）各差什么。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R917" not in h:
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
             for p, k in ((RBLOCK, "R917"), (RSTATUS, "R917"), (RVERDICT, "第 917 轮"), (BACKLOG, "R917")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R917: criterion (f) gets a table, which needed two corrections before it was worth reading\n\n"
         "Criterion (f) asks for a recomputable core coverage table -- the original's store and risk-vendor list from\n"
         " the binary against Registry.cs and Flows/Scripts, with a reason for every uncovered item. Checking first: no\n"
         " such column existed in METRICS.md, so the criterion had never been met.\n\n"
         "The two sides are sixty-four registrations across thirty-three flow types on the left, and thirty-nine hosts\n"
         " carrying the hundred and fifty-four recovered paths on the right, twenty-eight of them stores and eleven\n"
         " protection or payment vendors. core_coverage.py compares them per host.\n\n"
         "It needed two corrections. The first searched only Registry.cs and reported www.vans.com as unmatched, when\n"
         " R899 had already established that Vans is handled in DemandwareControllers' site-id table; that is the same\n"
         " fault as R911's missing Async suffix, a source too narrow, and widening it to the whole tree moved seven of\n"
         " twenty-eight to sixteen. The second took api-search.dickssportinggoods.com's label as api-search and\n"
         " prod-hk-actapi.popmart.com's as prod-hk-actapi -- and Pop Mart is a flow -- because it assumed a subdomain is\n"
         " either wholly generic or wholly meaningful, which hyphenated prefixes are neither; offering every segment as a\n"
         " candidate moved sixteen to twenty-two.\n\n"
         "Final: twenty-two of twenty-eight store hosts matched and six not, two of eleven vendors matched and nine not.\n"
         "Of the six, checkout.sportsshoes.com and payments.dickssportinggoods.com are genuine gaps, while\n"
         " braintreegateway, vipps, bigcommerce and purpledotprice are payment subdomains that may need no flow at all.\n\n"
         "Matched means a candidate label appears in some source file, which proves neither that the store works nor\n"
         " that its checkout is right. Unmatched is now the stronger statement, since the search covers the whole tree:\n"
         " the label appears nowhere in the replica.\n\n"
         "Unknown: what purpledotprice is, from one path; which priority each of the nine vendors belongs to; and\n"
         " whether hosts beyond those carrying paths exist -- the registry has sixty-four registrations against\n"
         " thirty-nine hosts, so the two counts do not correspond and this is not a one-to-one comparison.\n\n"
         "The lesson is that both faulty versions produced plausible numbers. Seven of twenty-eight and sixteen of\n"
         " twenty-eight are the kind of figure that looks fine, and only testing against a known answer -- Vans, which\n"
         " had to match -- showed the first one was wrong.\n\n"
         "New tool; no product code changed; suite carries at 1836."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()