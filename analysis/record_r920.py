"""Record R920: Purple Dot reclassified and integrated, closing the store bucket."""

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
### `purpledotprice` 不是店 —— 它是预售服务，而且带一个硬编码 key（R920）

**R919 说剩 4 个未匹配，`purpledotprice` 是唯一非支付商的那个。查了，一条字面量就说清了：**

```
https://www.purpledotprice.com/api/v1/products/preorder-state?api_key=c114b1fe-63fa-4216-9d7c-07a87697fccd&handle=
```

**Purple Dot 是给店铺做**预售/缺货登记**的服务。所以：**

1. **它不是店 → 该进 vendor 桶。而我把它分进 store 是因为它不在 `VENDOR_HINTS` 里 —— **分类清单漏了一项**，不是判据错。**
2. **它带一个**硬编码 API key**，在二进制里。这是这次核到的唯一一个「原版自带的第三方 key」。**
3. **端点语义是「按 handle 查这个商品是不是预售」。**

### 所以 store 桶清空了

**修正分类后：store **27** 个（原 28）· vendor **12** 个（原 11）· **store 匹配 24/27，未匹配 3**。**

**而那 3 个全是支付商：`braintreegateway` · `vipps` · `bigcommerce`。**

> **也就是说：**镜像里所有带路径的 store 宿主，复刻件现在都认得。**
> **判据 (f) 的 store 侧闭合了 —— 而它闭合的方式是 R917 建表、R918/R919 补两个店、R920 修正一个分类。**

### 写了 `PurpleDot.cs`

| 成员 | 作用 |
|---|---|
| `Host` · `PreorderState` · `ApiKey` | 三个恢复到的常量 |
| `UrlFor(handle)` | 拼出与镜像同形的 URL（**query string，不是 header**） |
| `QueryAsync(...)` | 三态：预售 / 现货 / **不可读** |
| `IsBuyable(session)` | 监控需要的那个判断 |

### 而最关键的是第三个状态

**不可读的响应**不设状态**，`IsBuyable` 因此返 false。**

> **因为反过来会是灾难：一个把「读不懂」当成「不是预售」的监控，会去买一个几个月后才发货的预售品。
> 所以这个类的默认答案是「不买」，而不是「买」。**

### 一处我把正则写窄了

**第一次 `(true|""[^""]*"")` 漏了 `false`，于是 `{"isPreorder":false}` 落进「不可读」分支 ——
**方向上是安全的（不买），但也意味着最常见的答案永远成功不了。** 测试把它抓出来了。**

### 数字

| 度量 | R919 | **R920** |
|---|---|---|
| 套件 | 1850 | **1857** |
| **store 宿主未匹配** | 3（含 1 个误分类） | **3（全是支付商）** |
| **store 桶** | 24 / 28 | **24 / 27** |

**比例没变好，而**分母变小了** —— 因为一个被误分类的宿主移出了这一桶。**
"""

if "`purpledotprice` 不是店" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R920 appended")

VERDICT = """

---

## 第 920 轮：`purpledotprice` 是预售服务 —— store 桶清空了

### 一条字面量

```
https://www.purpledotprice.com/api/v1/products/preorder-state?api_key=c114b1fe-…&handle=
```

**Purple Dot 是给店铺做预售/缺货登记的服务。所以：**

1. **它不是店 → 该进 vendor 桶。我把它分进 store 是因为它不在 `VENDOR_HINTS` 里 —— **分类清单漏了一项**，不是判据错。**
2. **它带一个硬编码 API key —— 这次核到的唯一一个「原版自带的第三方 key」。**
3. **语义是「按 handle 查这个商品是不是预售」。**

### store 桶清空

**store 27（原 28）· vendor 12（原 11）· **匹配 24/27，未匹配 3**，而 3 个全是支付商
（`braintreegateway` · `vipps` · `bigcommerce`）。**

> **镜像里所有带路径的 store 宿主，复刻件现在都认得。**
> **判据 (f) 的 store 侧闭合 —— 闭合方式是 R917 建表、R918/R919 补两个店、R920 修正一个分类。**

### `PurpleDot.cs` 的四件

**`Host`/`PreorderState`/`ApiKey` 常量 · `UrlFor` 拼同形 URL（query 而非 header）·
`QueryAsync` 三态 · `IsBuyable`**

### 最关键是第三个状态

**不可读的响应**不设状态**，`IsBuyable` 返 false。**

> **反过来会是灾难：一个把「读不懂」当成「不是预售」的监控，会去买一个几个月后才发货的预售品。
> 所以默认答案是「不买」。**

### 一处把正则写窄了

**`(true|""[^""]*"")` 漏了 `false` → `{"isPreorder":false}` 落进「不可读」分支。
方向安全（不买），但最常见的答案永远成功不了。测试抓出来了。**

### 数字

| 度量 | R919 | **R920** |
|---|---|---|
| 套件 | 1850 | **1857** |
| store 宿主未匹配 | 3（含 1 个误分类） | **3（全是支付商）** |
| store 桶 | 24 / 28 | **24 / 27** |

**比例没变好，而**分母变小了** —— 一个误分类的宿主移出了这一桶。**

### 教训

> **「比例没变好」和「没有进展」不是一回事。这一轮的分母变了，而**分母变小和分子变大是两种进展**，
> 只看比例会把后者藏起来。**
"""

BACKLOG_ADD = """

## 优先级 ①/③ — Purple Dot 集成（R920，**改产品代码 +7 用例 + 修正分类**）

### 一条字面量说清三件事

```
https://www.purpledotprice.com/api/v1/products/preorder-state?api_key=c114b1fe-63fa-4216-9d7c-07a87697fccd&handle=
```

**→ 预售服务（不是店）· 硬编码 API key · 按 handle 查预售状态**

### 分类修正

**`VENDOR_HINTS` 漏了它 → 加入 `purpledotprice` / `purpledot`。**
**store 28→27 · vendor 11→12 · **store 匹配 24/27，未匹配 3 全是支付商**（braintreegateway/vipps/bigcommerce）。**

### `Payments/PurpleDot.cs`

**`Host`/`PreorderState`/`ApiKey` · `UrlFor(handle)`（query 而非 header）· `QueryAsync` 三态 · `IsBuyable`**

**不可读响应 → 状态不设 → `IsBuyable` 返 false。**默认答案是「不买」，因为把读不懂当「不是预售」
会去买几个月后发货的东西。**

### 一处正则写窄了

**`(true|"…")` 漏 `false` → `{"isPreorder":false}` 落进不可读分支。方向安全但最常见答案永远失败。测试抓到。**

### 数字

**套件 1850 → 1857 · store 桶 24/28 → **24/27**（分母变小，因一个误分类移出）**

| 仍 Unknown | |
|---|---|
| API key 是每次安装的还是公共的 | 一条字符串看不出 |
| 响应体真实形状 | 三个候选字段名 |
| vendor 桶 12 个里还有几个该实现 | 未逐个判 |

**纪律**：**分母变小与分子变大是两种进展，只看比例会把后者藏起来。**
"""

BLOCKER = """

---

## 344. Purple Dot：预售服务 + 硬编码 key；store 桶清空（24/27，未匹配全是支付商）

> R920。**改产品代码 +7 用例 + 修正分类。** 套件 **1857 通过 / 0 失败 / 0 跳过**。

### 一、一条字面量说清三件事

```
https://www.purpledotprice.com/api/v1/products/preorder-state?api_key=c114b1fe-63fa-4216-9d7c-07a87697fccd&handle=
```

**→ 预售服务（不是店）· 硬编码 API key · 按 handle 查预售状态**

### 二、分类修正，而 store 桶因此清空

**`VENDOR_HINTS` 漏了 purpledotprice → 加入。**

| 度量 | R919 | R920 |
|---|---|---|
| store 宿主 | 28 | **27** |
| vendor 宿主 | 11 | **12** |
| **store 匹配** | 24 / 28 | **24 / 27** |
| store 未匹配 | 3 | **3（全是支付商）** |

**`braintreegateway` · `vipps` · `bigcommerce` —— 三个支付商子域，都判为不需要 flow。**

**→ 镜像里所有带路径的 store 宿主，复刻件现在都认得。判据 (f) 的 store 侧闭合。**

### 三、`Payments/PurpleDot.cs`

| 成员 | |
|---|---|
| `Host` · `PreorderState` · `ApiKey` | 三个恢复到的常量 |
| `UrlFor(handle)` | 与镜像同形的 URL（**query string，不是 header**） |
| `QueryAsync(...)` | 三态：预售 / 现货 / **不可读** |
| `IsBuyable(session)` | 监控需要的判断 |

**不可读 → 状态不设 → `IsBuyable` 返 false。默认答案是「不买」，
因为把读不懂当「不是预售」会去买几个月后发货的东西。**

### 四、一处正则写窄了

**`(true|""[^""]*"")` 漏了 `false` → `{"isPreorder":false}` 落进不可读分支。
方向安全（不买），但**最常见的答案永远成功不了**。7 个用例抓出来了。**

### 五、验证

```
core_coverage.py            -> store 24/27；vendor 12；purpledotprice 已入 vendor 桶
test --filter PurpleDotTests -> 7 通过
metrics_report.py           -> 1857 通过 / 0 失败
```

### 六、仍然 Unknown

- **API key 是每次安装的还是公共的**：**Unknown** —— 一条字符串看不出作用域。
- **响应体真实形状**：**Unknown** —— 三个候选字段名，都可能是它自己编的。
- **vendor 桶 12 个里还有几个该实现**：**Unknown** —— 未逐个判。

### 七、教训

**「比例没变好」和「没有进展」不是一回事。这一轮 store 桶从 24/28 变成 24/27 ——
分子的数没变，分母小了，因为一个误分类的宿主移了出去。**

**分母变小与分子变大是两种进展，而只看比例会把后者藏起来。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R920", BLOCKER)
    ensure(RSTATUS, "R920", BLOCKER)
    ensure(RVERDICT, "第 920 轮", VERDICT)
    ensure(BACKLOG, "R920", BACKLOG_ADD)

    note = (
        "\n## R920 补充 — Purple Dot：预售服务 + 硬编码 key；store 桶清空（改产品代码 +7 用例，套件 1857）\n\n"
        "一条字面量：https://www.purpledotprice.com/api/v1/products/preorder-state?api_key=c114b1fe-…&handle=\n"
        "→ 预售服务（不是店）· 硬编码 API key（原版自带的唯一一个）· 按 handle 查预售。\n\n"
        "分类修正：VENDOR_HINTS 漏了它。store 28→27 · vendor 11→12 · **store 匹配 24/27，未匹配 3 全是支付商**"
        "（braintreegateway/vipps/bigcommerce）→ 判据 (f) 的 store 侧闭合。\n\n"
        "Payments/PurpleDot.cs：Host/PreorderState/ApiKey · UrlFor（query 而非 header）· QueryAsync 三态 · IsBuyable。"
        "不可读 → 状态不设 → IsBuyable 返 false（默认答案「不买」）。\n\n"
        "一处正则写窄：漏 false → {\"isPreorder\":false} 落进不可读分支。测试抓到。\n\n"
        "数字：套件 1850 → 1857 · store 桶 24/28 → 24/27（分母变小，误分类移出）。\n\n"
        "下一轮：vendor 桶 12 个逐个判（含 Cloudflare/AYCD/Paynamics/PurpleDot 已做，还剩若干）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R920" not in h:
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
             for p, k in ((RBLOCK, "R920"), (RSTATUS, "R920"), (RVERDICT, "第 920 轮"), (BACKLOG, "R920")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R920: Purple Dot is a preorder service, and its reclassification empties the store bucket\n\n"
         "R919 left four unmatched hosts, one of them the only non-payment provider among them. One literal explains it:\n"
         " purpledotprice carries a preorder-state endpoint, a handle parameter and an API key in a single URL. Purple\n"
         " Dot sells preorder and back-in-stock handling to shops, so the host is not a storefront -- and the reason it\n"
         " sat in the store bucket is that the vendor list did not name it, which is a gap in a list rather than a fault\n"
         " in a criterion.\n\n"
         "With it moved, the store bucket holds twenty-seven hosts rather than twenty-eight, twenty-four of them matched,\n"
         " and the three unmatched are all payment subdomains already judged not to need a flow. So every store host\n"
         " carrying a path in the image is now known to the replica, which closes the store side of criterion (f) --\n"
         " built by R917, filled in by R918 and R919, and corrected here.\n\n"
         "Purple Dot is integrated as a vendor beside the payment gateways, carrying the host, the path and the recovered\n"
         " key, building a URL with both parameters in the query string as the image does, and answering in three states\n"
         " rather than two. The third is the one that matters: an answer in a shape this does not recognise leaves the\n"
         " state unset, so the buyability question answers no. Reading an unreadable answer as not-a-preorder would send\n"
         " a monitor to buy something that ships months later.\n\n"
         "One regex was written too narrow: the alternation accepted true or a string but not false, so the commonest\n"
         " answer fell through to the unrecognised branch. That fails in the safe direction and still makes the common\n"
         " case impossible, and the tests caught it.\n\n"
         "Figures: suite 1850 to 1857, store bucket twenty-four of twenty-eight to twenty-four of twenty-seven.\n\n"
         "Unknown: whether the key is per-install or shared, which one string cannot show; the response body's real\n"
         " shape, of which three field names are guesses; and how many of the twelve vendor hosts deserve integrating.\n\n"
         "The lesson is that a ratio holding still is not progress stopping. The numerator did not move this round and\n"
         " the denominator shrank, because a misclassified host left the bucket -- and reporting the ratio alone would\n"
         " have hidden that.\n\n"
         "Product code and a tool changed; suite green at 1857."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()