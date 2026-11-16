"""Record R826: two more scrapers read, and the length guard turns a wrong page into out-of-stock."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 250. 又读两个：`NikeFlow` 是结构化读取，而**长度守卫会把「不是商品页」判成缺货**

> R826。未改产品代码（内存 1.63 GB，只读）。

### 一、`NikeFlow`（31 行）—— 好的那一类

```csharp
if (!c.Session.Vars.TryGetValue("thread", out var threadJson))
    return StepOutcome.Fail("nike: no thread loaded");
var thread = JObject.Parse(threadJson);
var infos = thread["productInfo"] as JArray;
if (infos is null) return StepOutcome.Fail("nike: thread has no productInfo");
...
var skuAvailable = sku["available"]?.ToObject<bool?>() ?? available;
if (skuAvailable) anyAvailable = true;
...
if (string.Equals(status, "ACTIVE", ...) && available) anyAvailable = true;
c.Session.Vars["available"] = anyAvailable ? "true" : "false";
```

**三条值得记**：

1. **结构化读取**（`JObject`/`JArray`），不是子串探针
2. **缺输入时明确失败**（`"nike: no thread loaded"`），**不是给一个默认值**
3. **判据是「任何一个 SKU 有货」或「状态 ACTIVE 且 available」** —— 与 Nike 的实际语义相符

### 二、`ScheelsFlow`（25 行）—— 模式正确，但藏了一个转换

```csharp
var soldOut = body.Contains("OutOfStock", ...) || body.Contains("\\"inStock\\":false", ...);
c.Session.Vars["available"] = !soldOut && body.Length > 200 ? "true" : "false";
```

**`body.Length > 200` 这个守卫的意图是「这看起来像一页真页面」。**
**但它把三类情况压成同一个答案 `available = false`：**

| 真实情况 | 现在的判定 |
|---|---|
| 真的缺货 | `false` ✓ |
| 响应体很短（重定向页、错误页、captcha 插页） | **`false` ✗ 看起来像缺货** |
| 响应体为空（请求失败但没抛） | **`false` ✗ 同上** |

**`BstnFlow` 是同一种形状，只是阈值是 `body.Length > 2000`。**

**这是本会话反复出现的那一类：一个可以接受的失败被转换成一个具体的、错误的断言。**

### 三、为什么这比「多判一次缺货」更严重

**监控的存在意义是「有货就去抢」。**

- **误报 `available = true`** → 白跑一次 checkout，代价是一次失败的下单
- **误报 `available = false`** → **错过 drop，而 drop 是不可重来的**

**后者不可挽回，而它由「响应体长度」这个与商品无关的量决定。**

### 四、为什么没改

**改法有两种，而选哪种需要证据：**

1. **长度不足时 `return StepOutcome.Fail("scheels: response is not a product page")`** —— 诚实，但会让监控在这一步停下
2. **先看 `lastStatus`，403/429 判 `Blocked`** —— 更准，但 `ScrapeVariantAvailabilityAsync` 现在不读状态槽

**镜像怎么做，得读反编译。内存 1.63 GB，IDA 没开。**

**而且这两个流程的覆盖率判据目前算它们「已实现」—— 改成失败会让那个数字下降（R800 的教训：诚实可能不动数字，也可能动）。**

### 五、验证

```
本轮未改产品代码
通读累计 12 / 20（新增 NikeFlow 31 行 · ScheelsFlow 25 行）
未跑全量（内存 1.63 GB < 2 GB）
四项度量沿用：4 / 0 / 17 / 78 / 0
```

### 六、仍然 Unknown

- **`body.Length > N` 这个守卫在镜像里是否存在**：**Unknown** —— 可能形象也是这么做的（那就不是缺陷而是忠实复刻），
  也可能形象用的是状态码。**这条只有反编译能答。**
- **其余 8 个未通读的实现里还有几个用长度守卫**：**Unknown** ——
  本轮只读了 Nike/Scheels，**而 `BstnFlow` 是偶然撞见的。**
- **`NikeFlow` 的 `JObject.Parse` 在畸形 JSON 上会不会抛**：**Inference（中）会** ——
  抛了会被 `GuardAsync` 的 catch 转成失败，**所以不会静默，但错误信息会是 JSON 解析器的。**
"""

VERDICT = """

---

## 第 826 轮：`NikeFlow` 是结构化读取；长度守卫会把「不是商品页」判成缺货

### `NikeFlow`（31 行）—— 好的那一类

```csharp
if (!c.Session.Vars.TryGetValue("thread", out var threadJson))
    return StepOutcome.Fail("nike: no thread loaded");
```

**三条**：结构化 `JObject`/`JArray` 读取 · **缺输入时明确失败** · 判据是「任一 SKU 有货」或「ACTIVE 且 available」。

### `ScheelsFlow`（25 行）—— 藏了一个转换

```csharp
c.Session.Vars["available"] = !soldOut && body.Length > 200 ? "true" : "false";
```

| 真实情况 | 判定 |
|---|---|
| 真缺货 | `false` ✓ |
| **响应体短（错误页 / captcha 插页）** | **`false` ✗ 看起来像缺货** |
| 响应体空（请求失败未抛） | **`false` ✗ 同上** |

**`BstnFlow` 同形，阈值 `2000`。**

### 为什么严重

- **误报有货** → 白跑一次 checkout
- **误报缺货** → **错过 drop，不可重来**

**后者由「响应体长度」这个与商品无关的量决定。**

### 为什么没改

**两种改法都需要证据**：① 长度不足时明确失败；② 先看 `lastStatus` 判 `Blocked`。
**镜像怎么做要读反编译 —— 内存 1.63 GB，IDA 没开。**

**而且改成失败会让覆盖率数字下降（R800 的教训：诚实可能动数字）。**

### 验证

```
通读累计 12 / 20 · 未改产品代码 · 未跑全量 · 度量沿用 4 / 0 / 17 / 78 / 0
```

### 教训

**一个可以接受的失败，被转换成了一个具体的、错误的断言。**
**而它由一个与商品无关的量（响应体长度）决定。**
"""

BACKLOG_ADD = """

## 优先级 ① — 长度守卫把「不是商品页」判成缺货（R826）

**通读累计 12 / 20。**

| 流程 | 判据 | 评价 |
|---|---|---|
| `NikeFlow` 31 行 | `JObject` 解析 thread，任一 SKU 有货 或 ACTIVE+available | **好的那一类**：结构化 · 缺输入明确失败 |
| `ScheelsFlow` 25 行 | `!soldOut && body.Length > 200` | **长度守卫有问题** |
| `BstnFlow` 13 行 | `!soldOut && body.Length > 2000` | **同形** |

```
c.Session.Vars["available"] = !soldOut && body.Length > 200 ? "true" : "false";
```

**三类情况压成同一个 `false`**：真缺货 ✓ · **响应体短（错误页/captcha 插页）✗** · 响应体空 ✗

**为什么严重**：误报有货 = 白跑一次下单；**误报缺货 = 错过 drop，不可重来**。后者由「响应体长度」这个与商品无关的量决定。

**未修原因**：① 长度不足时明确失败 / ② 先看 `lastStatus` 判 `Blocked` —— **两种都需要镜像证据，IDA 未开（内存 1.63 GB）**。
**且改成失败会让覆盖率数字下降（R800）。**

| 仍 Unknown | |
|---|---|
| `body.Length > N` 在镜像里是否存在 | **只有反编译能答**；若形象也这么做，则不是缺陷而是忠实复刻 |
| 其余 8 个未通读里有几个用长度守卫 | `BstnFlow` 是偶然撞见的 |
| `JObject.Parse` 在畸形 JSON 上是否抛 | Inference（中）会；被 `GuardAsync` 转成失败，不静默 |
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R826", BLOCKER)
    ensure(RSTATUS, "R826", BLOCKER)
    ensure(RVERDICT, "第 826 轮", VERDICT)
    ensure(BACKLOG, "R826", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    note = ("\n## R826 补充\n\n"
            "**长度守卫问题**：`ScheelsFlow`（`body.Length > 200`）与 `BstnFlow`（`> 2000`）把「响应体短/空」"
            "也判成 `available=false` ——\n"
            "**误报缺货 = 错过 drop，不可重来**，而它由与商品无关的量决定。\n"
            "**通读累计 12/20**（`NikeFlow` 31 行是好的那一类：结构化读取 + 缺输入明确失败）。\n"
            "**未修**：两种改法都要镜像证据；IDA 未开（内存 1.63 GB）。\n")
    if "R826" not in h:
        h += note
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")
    else:
        print("  handoff already has R826")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R826"), (RSTATUS, "R826"), (RVERDICT, "第 826 轮"), (BACKLOG, "R826")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R826: NikeFlow reads structurally, and a length guard turns a wrong page into out-of-stock\n\n"
         "Two more of the twenty availability scrapers read, at the long end where a wrong rule is most likely.\n\n"
         "NikeFlow, thirty-one lines, is the good kind: it parses the thread JSON, walks productInfo for"
         " merchProduct.status, availability.available and each sku's available flag, and decides available when any SKU"
         " is up or the product is ACTIVE and available. It fails honestly with \"nike: no thread loaded\" rather than"
         " defaulting, which is the property that matters most.\n\n"
         "ScheelsFlow, twenty-five lines, probes for OutOfStock and \"inStock\":false and then writes"
         " `!soldOut && body.Length > 200 ? \"true\" : \"false\"`. The length guard is meant to say \"this looks like a"
         " real page\", and it collapses three different situations into one answer: genuinely sold out, which is"
         " correct; a short body such as an error page or a captcha interstitial, which reads as sold out; and an empty"
         " body from a failed request that did not throw, same. BstnFlow has the identical shape at a threshold of two"
         " thousand.\n\n"
         "That matters more than a spurious true would. A false available costs one wasted checkout; a false"
         " unavailable loses the drop, and drops do not repeat. Here the verdict is decided by response body length, a"
         " quantity with nothing to do with the product.\n\n"
         "I did not change it, because both repairs need evidence from the image: fail explicitly when the body is too"
         " short, or read lastStatus first and report Blocked for 403 and 429. Which one the image does requires the"
         " decompilation, and memory is 1.63 GB so IDA stayed shut. Changing it also moves the coverage numbers, and"
         " R800 established that honesty can move them rather than leave them alone.\n\n"
         "Unknown: whether the length guard exists in the image at all, in which case it is faithful reproduction rather"
         " than a defect; how many of the eight unread implementations use one, since BstnFlow was found by accident; and"
         " whether JObject.Parse throwing on malformed JSON is handled anywhere but GuardAsync's catch, which converts it"
         " to a failure but reports the parser's message.\n\n"
         "Twelve of twenty now read through. No product code changed; suite not run at 1.63 GB; metrics at"
         " 4 / 0 / 17 / 78 / 0."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
