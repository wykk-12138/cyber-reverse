"""Record R1015: the endpoint scanner skipped every interpolated template, and fixing that found 11."""

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
### 端点扫描器**跳过所有插值模板** —— 修掉之后一次查出 11 个（R1015）

**R1014 说下一轮换一个站。而 R1014 自己的教训是「读到手边的文件」——
所以换之前先跑现成的 `endpoint-provenance.py`，问它为什么没抓到 Nike 那 4 处。**

### ① 答案在 165 行，而且它**明确写了**

```python
for m in INLINE.finditer(body):
    value = m.group(1)
    # skip interpolated templates and obvious fragments
    if "{" in value or value.endswith("/"):
        continue
```

**→ 带 `{` 的值被**明确跳过**，注释说那是「interpolated templates」。
→ 而 Nike 那 4 处**全是** `$"https://api.nike.com/buy/orders/v2/US/{c.Session.CartId}/delivery"` 这个形。**

> **→ 所以工具的「invented: 0」是**真的**（对它的定义域），而 Nike 的缺陷**在界外**。
> → 这是 R1010「判据有定义域」的**第二次** —— 而这次在代码里，有行号。**

### ② 修法：插值模板的前缀是一个可以判的主张

**`$".../buy/orders/v2/US/{cart}/delivery"` 对 `".../buy/orders/v2/US/"` 提出了一个主张，
而那个主张要么在镜像里，要么不在。**
**→ 而一个**只到 host** 的前缀不是主张（`https://api.nike.com/` 什么都不断言），所以不管它。**

**实现：`static_prefix()` 取第一个 `{` 之前的部分；只在它带路径时才判；
并且结尾的 `/` 单独查（`proven(x) or proven(x.rstrip('/'))`）。**

### ③ 而修完后，一次查出 **11 个**

```
inline URL/path literals: 268 → 328      （多扫到 60 个）
not in pool:              29 → 40
unknown (unregistered):    0 → 11        baseline 0 → FAIL
```

| 文件 | 行 | 前缀 |
|---|---|---|
| FarfetchFlow.cs | 62 | `/api/ff-products/v1/products/{…}` |
| FarfetchFlow.cs | 174 | `/api/basket/v1/` |
| FarfetchFlow.cs | 201 · 207 · 237 · 272 · 289 | `/api/checkout/v1/basket/{…}` |
| NikeFlow.cs | 235 | `https://api.nike.com/product_feed/threads/v2/` |
| NikeFlow.cs | 652 | `https://api.nike.com/buy/carts/v2/{…}` |
| StoreFlow.cs | 768 | `/discount/` |
| StoreFlow.cs | 1272 | `/api/payments/` |

### ④ 而 11 个**不是** 11 个缺陷 —— 那是 R1010 的教训

**Nike 那 2 个我已经知道真假：**
- `:652 buy/carts/v2/{…}` —— **确实不存在**（镜像 0 命中，R1013 已证）
- `:235 product_feed/threads/v2/` —— 那在 `NikeEndpoints.ProductFeedThreads` 里是**镜像有的**，
  而这里报 absent 是因为**结尾 `/` 与 `?fields=` 的形不同** ⇒ **可能是假阳性**

**→ 所以这 11 个是**待判清单**，而其中至少 1 个已经看出是假阳性。**

### ⑤ 而**不登记进 ledger**

**`BASELINE = 0` 与 `ledger_classes()` 是一个**收紧守卫**的设计：任何新的 absent 端点都要先被判过才能登记。
把 11 个直接登记进去，就等于把「我们不知道」写进白名单 —— 那正是这个工具存在的反面。**

**→ 所以工具现在**红着**（`FAIL: 11 unregistered inline endpoints`），而那是正确的状态：它报出了一个真的待办。
→ 而它不影响套件（`metrics_report.py` 跑的是 dotnet test，不是这个脚本）。**

### ⑥ 数字

| 度量 | R1014 | **R1015** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0**（未改产品代码） |
| 函数数 | 174,336 | **174,336** |
| **扫描到的内联字面量** | 268 | **328（+60，插值模板进来了）** |
| **判为不在池里** | 29 | **40** |
| **未登记的** | **0**（假的 0） | **11（真的待判）** |
| **`endpoint-provenance.py` 退出码** | 0 | **1（红，且应当红）** |

### 教训

> **一个「invented: 0」的守卫可以同时是真的和没用的 —— 只要它的定义域排除了缺陷所在的那一类。
> → 而排除是**写在一行 `continue` 里的**，注释还坦白说了「skip interpolated templates」。
> → 我读了那份输出五行，从来没问过「它扫了哪些」。**
> **→ 而 R1010 的教训（判据有定义域）刚在上一轮立过，这一轮就在它自己身上又遇见一次。**
"""

if "端点扫描器**跳过所有插值模板**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1015 轮：端点扫描器跳过所有插值模板 —— 修掉之后一次查出 11 个

### ① 答案在 165 行，而且它明确写了

```python
# skip interpolated templates and obvious fragments
if "{" in value or value.endswith("/"):
    continue
```

**→ 带 `{` 的值被**明确跳过**。而 Nike 那 4 处**全是**插值模板 ⇒ 全在界外。
→ 工具的「invented: 0」是**真的**（对它的定义域），而缺陷**在界外**。
→ 这是 R1010「判据有定义域」的**第二次** —— 这次在代码里，有行号。**

### ② 修法：插值模板的前缀是一个可以判的主张

**`$".../buy/orders/v2/US/{cart}/delivery"` 对 `".../buy/orders/v2/US/"` 提出一个主张，
而那个主张要么在镜像里，要么不在。而**只到 host** 的前缀不是主张，所以不管它。**

**`static_prefix()` 取第一个 `{` 之前；只在带路径时判；结尾 `/` 单独查。**

### ③ 修完后一次查出 **11 个**

```
inline literals: 268 → 328    not in pool: 29 → 40    unknown: 0 → 11
```

| 文件 | 行 | 前缀 |
|---|---|---|
| FarfetchFlow.cs | 62 · 174 · 201 · 207 · 237 · 272 · 289 | `/api/ff-products/v1/products/{…}` · `/api/basket/v1/` · `/api/checkout/v1/basket/{…}` ×5 |
| NikeFlow.cs | 235 · 652 | `product_feed/threads/v2/` · `buy/carts/v2/{…}` |
| StoreFlow.cs | 768 · 1272 | `/discount/` · `/api/payments/` |

### ④ 而 11 个**不是** 11 个缺陷

**Nike 那 2 个我已知道真假：**
- `:652 buy/carts/v2/{…}` —— **确实不存在**（镜像 0 命中）
- `:235 product_feed/threads/v2/` —— 那在 `NikeEndpoints.ProductFeedThreads` 里是**镜像有的**，
  这里报 absent 是因为**结尾 `/` 与 `?fields=` 的形不同** ⇒ **疑似假阳性**

### ⑤ 而**不登记进 ledger**

**`BASELINE = 0` 是**收紧守卫**：任何新的 absent 端点都要先被判过才能登记。
把 11 个直接登记，就是把「我们不知道」写进白名单 —— 那正是这个工具存在的反面。**

**→ 所以工具现在**红着**（`FAIL: 11 unregistered inline endpoints`），那是正确的状态。
→ 而它不影响套件（metrics 跑 dotnet test，不是这个脚本）。**

### ⑥ 数字

| 度量 | R1014 | **R1015** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0**（未改产品代码） |
| 函数数 | 174,336 | **174,336** |
| **扫到的内联字面量** | 268 | **328（+60）** |
| **不在池里** | 29 | **40** |
| **未登记** | **0（假的 0）** | **11（真的待判）** |
| **工具退出码** | 0 | **1（红，且应当红）** |

### 教训

> **一个「invented: 0」的守卫可以同时是真的和没用的 —— 只要它的定义域排除了缺陷所在的那一类。
> → 而排除是**写在一行 `continue` 里的**，注释还坦白说了「skip interpolated templates」。
> → 我读了那份输出五行，从来没问过「它扫了哪些」。**
"""

BACKLOG_ADD = """

## 判据 (c)/(f) — **端点扫描器跳过所有插值模板（一行 continue）；修掉后一次查出 11 个待判**（R1015）

### 盲区

```python
# skip interpolated templates and obvious fragments
if "{" in value or value.endswith("/"):
    continue
```

**→ Nike 那 4 处全是插值模板 ⇒ 全在界外 ⇒ 工具的「invented: 0」是真的但没用（R1010 定义域的第二次，这次有行号）。**

### 修法

**`static_prefix()` 取第一个 `{` 之前；只在带路径时判；`proven(x) or proven(x.rstrip('/'))`。
只到 host 的前缀不管（它什么都不断言）。**

### 而修完后

```
inline literals: 268 → 328    not in pool: 29 → 40    unknown: 0 → 11    baseline 0 → FAIL
```

| 文件 | 行 |
|---|---|
| `FarfetchFlow.cs` | 62 · 174 · 201 · 207 · 237 · 272 · 289 |
| `NikeFlow.cs` | 235 · 652 |
| `StoreFlow.cs` | 768 · 1272 |

### 两个已能判的

- `NikeFlow.cs:652` `buy/carts/v2/{…}` —— **确实不存在**（镜像 0 命中）
- `NikeFlow.cs:235` `product_feed/threads/v2/` —— 那在 `NikeEndpoints.ProductFeedThreads` 里**镜像有**，
  报 absent 是**结尾 `/` 与 `?fields=` 形不同** ⇒ **疑似假阳性**

### 不登记进 ledger

**`BASELINE = 0` 是收紧守卫；把 11 个登记进去等于把「不知道」写进白名单。**
**→ 工具现在红着，那是正确状态；不影响套件（metrics 跑 dotnet test）。**

### 数字

**套件 2219/0 · 函数数 174,336 · 内联字面量 268 → 328 · 不在池 29 → 40 · 未登记 0 → 11 · 工具退出码 1**

| 仍 Unknown | |
|---|---|
| 那 11 个里哪些真不存在 | 待逐个判（1 个疑似假阳性） |

**纪律**：一个「0」可以同时是真的和没用的 —— 只要定义域排除了缺陷那一类。
"""

BLOCKER = """

---

## 439. **端点扫描器跳过所有插值模板（一行 continue）；修掉后一次查出 11 个待判**

> R1015。**改 1 个工具。** 套件 **2219 通过 / 0 失败**（未改产品代码）。

### 一、盲区在 165 行，而且它明确写了

```python
for m in INLINE.finditer(body):
    value = m.group(1)
    # skip interpolated templates and obvious fragments
    if "{" in value or value.endswith("/"):
        continue
```

**→ 带 `{` 的值被**明确跳过**，注释说那是「interpolated templates」。
→ 而 Nike 那 4 处**全是** `$"https://api.nike.com/buy/orders/v2/US/{c.Session.CartId}/delivery"` 这个形。**

**→ 所以工具的「invented: 0」是**真的**（对它的定义域），而 Nike 的缺陷**在界外**。
→ 这是 R1010「判据有定义域」的**第二次** —— 而这次在代码里，有行号。**

### 二、修法

**`$".../buy/orders/v2/US/{cart}/delivery"` 对 `".../buy/orders/v2/US/"` 提出了一个主张，
而那个主张要么在镜像里，要么不在。
→ 而一个**只到 host** 的前缀不是主张，所以不管它。**

**实现 `static_prefix()`：取第一个 `{` 之前的部分；只在它带路径时才判；
并且结尾的 `/` 单独查（`proven(x) or proven(x.rstrip('/'))`）。**

### 三、修完后一次查出 11 个

```
inline URL/path literals: 268 → 328      （多扫到 60 个）
not in pool:              29 → 40
unknown (unregistered):    0 → 11        baseline 0 → FAIL
```

| 文件 | 行 | 前缀 |
|---|---|---|
| `FarfetchFlow.cs` | 62 | `/api/ff-products/v1/products/{…}` |
| `FarfetchFlow.cs` | 174 | `/api/basket/v1/` |
| `FarfetchFlow.cs` | 201 · 207 · 237 · 272 · 289 | `/api/checkout/v1/basket/{…}` |
| `NikeFlow.cs` | 235 | `https://api.nike.com/product_feed/threads/v2/` |
| `NikeFlow.cs` | 652 | `https://api.nike.com/buy/carts/v2/{…}` |
| `StoreFlow.cs` | 768 | `/discount/` |
| `StoreFlow.cs` | 1272 | `/api/payments/` |

### 四、而 11 个**不是** 11 个缺陷（R1010 的教训）

**Nike 那 2 个我已经知道真假：**

- `:652 buy/carts/v2/{…}` —— **确实不存在**（镜像 0 命中，R1013 已证）
- `:235 product_feed/threads/v2/` —— 那在 `NikeEndpoints.ProductFeedThreads` 里是**镜像有的**，
  这里报 absent 是因为**结尾 `/` 与 `?fields=` 的形不同** ⇒ **疑似假阳性**

**→ 所以这 11 个是**待判清单**，而其中至少 1 个已经看出是假阳性。**

### 五、而**不登记进 ledger**

**`BASELINE = 0` 与 `ledger_classes()` 是一个**收紧守卫**的设计：
任何新的 absent 端点都要先被判过才能登记。
把 11 个直接登记进去，就等于把「我们不知道」写进白名单 —— 那正是这个工具存在的反面。**

**→ 所以工具现在**红着**（`FAIL: 11 unregistered inline endpoints`），而那是正确的状态：
它报出了一个真的待办。
→ 而它不影响套件（`metrics_report.py` 跑的是 dotnet test，不是这个脚本）。**

### 六、数字

| 度量 | R1014 | R1015 |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0（未改产品代码）** |
| 函数数 | 174,336 | **174,336** |
| **扫描到的内联字面量** | 268 | **328（+60）** |
| **判为不在池里** | 29 | **40** |
| **未登记的** | **0（假的 0）** | **11（真的待判）** |
| **`endpoint-provenance.py` 退出码** | 0 | **1（红，且应当红）** |

### 七、验证

```
cd replica
python tools/endpoint-provenance.py
  -> endpoint constants: 210 · verbatim in pool: 210 · invented: 0 · unresolved: 4
  -> inline URL/path literals: 328 · not in pool: 40 · registered in ledger: 29
  -> unknown (invented and unregistered): 11 · baseline: 0
  -> FAIL: 11 unregistered inline endpoints, above the 0 baseline
python tools/metrics_report.py -> 完整套件 exit 0  2219 / 0 / 0
```

### 八、仍然 Unknown

- **那 11 个里哪些真不存在**：**待逐个判** —— 已看出 1 个疑似假阳性（`product_feed/threads/v2/`）。

### 九、教训

**一个「invented: 0」的守卫可以同时是真的和没用的 ——
只要它的定义域排除了缺陷所在的那一类。**

**→ 而排除是**写在一行 `continue` 里的**，注释还坦白说了「skip interpolated templates」。
→ 我读了那份输出五行，从来没问过「它扫了哪些」。**

**→ 而 R1010 的教训（判据有定义域）刚在上一轮立过，这一轮就在它自己身上又遇见一次。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1015", BLOCKER)
    ensure(RSTATUS, "R1015", BLOCKER)
    ensure(RVERDICT, "第 1015 轮", VERDICT)
    ensure(BACKLOG, "R1015", BACKLOG_ADD)

    note = (
        "\n## R1015 补充 — **端点扫描器跳过所有插值模板（一行 continue）；修掉后一次查出 11 个待判**\n\n"
        "**盲区在 `endpoint-provenance.py` 第 165-167 行，而且明确写了**：\n"
        "```python\n# skip interpolated templates and obvious fragments\nif \"{\" in value or value.endswith(\"/\"):\n    continue\n```\n"
        "→ Nike 那 4 处**全是**插值模板 ⇒ 全在界外 ⇒ 工具的「invented: 0」**是真的但没用**。\n"
        "→ **R1010「判据有定义域」的第二次，这次在代码里，有行号。**\n\n"
        "**修法**：`static_prefix()` 取第一个 `{` 之前；只在带路径时判；`proven(x) or proven(x.rstrip('/'))`。\n"
        "只到 host 的前缀不管（它什么都不断言）。\n\n"
        "**修完后**：`inline literals 268 → 328` · `not in pool 29 → 40` · `unknown 0 → 11` · 工具**退出码 1**。\n"
        "11 个分布：`FarfetchFlow.cs` ×7 · `NikeFlow.cs` ×2 · `StoreFlow.cs` ×2。\n\n"
        "**已能判的 2 个**：`NikeFlow.cs:652 buy/carts/v2/{…}` **确实不存在**；\n"
        "`NikeFlow.cs:235 product_feed/threads/v2/` 在 `NikeEndpoints.ProductFeedThreads` 里**镜像有** ⇒ **疑似假阳性**\n"
        "（结尾 `/` 与 `?fields=` 形不同）。\n\n"
        "**不登记进 ledger**：`BASELINE = 0` 是收紧守卫；登记 11 个等于把「不知道」写进白名单。\n"
        "→ 工具**红着是正确状态**；不影响套件（metrics 跑 dotnet test）。\n\n"
        "数字：套件 2219/0 · 函数数 174,336 · 内联字面量 328 · 不在池 40 · 未登记 11 · 工具退出码 1。\n\n"
        "纪律：**一个「0」可以同时是真的和没用的 —— 只要定义域排除了缺陷所在的那一类。**\n\n"
        "下一轮：判那 11 个（先修假阳性判定，再逐个对镜像）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1015" not in h:
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
             for p, k in ((RBLOCK, "R1015"), (RSTATUS, "R1015"), (RVERDICT, "第 1015 轮"), (BACKLOG, "R1015")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1015: the endpoint scanner skipped every interpolated template\n\n"
         "R1014's lesson was to read the file already in front of me, so before moving to another store I ran the\n"
         " endpoint scanner that should have caught Nike and asked why it did not.\n\n"
         "The answer is on line 165, and it is typed out: values containing a brace are skipped as interpolated\n"
         " templates. Nike's four bad calls are all that shape, so all four were outside the question the tool asks. The\n"
         " invented count of zero was true and useless at the same time -- true for the domain it measures, and the domain\n"
         " excluded the class where the defect lived. That is R1010's lesson about a criterion's domain for the second\n"
         " time, and this time it had a line number.\n\n"
         "The fix rests on noticing that an interpolated template still makes a checkable claim. A call to\n"
         " buy/orders/v2/US/{cart}/delivery asserts something about buy/orders/v2/US/, and that either appears in the image\n"
         " or it does not. A prefix that stops at the host asserts nothing, so those are left alone. static_prefix takes\n"
         " the part before the first hole, and the trailing slash is checked in both spellings.\n\n"
         "With that in place the scan sees sixty more literals and reports eleven unregistered, where it used to report\n"
         " none. Seven are Farfetch paths, two in Nike, two in StoreFlow. Eleven is not eleven defects -- one of the Nike\n"
         " two is already visible as a false positive, because product_feed/threads/v2 is in NikeEndpoints and is in the\n"
         " image, and it only reads as absent because the literal ends in a slash where the constant carries a query\n"
         " string.\n\n"
         "I did not register the eleven in the ledger. The zero baseline and the ledger are a tightening design: a name\n"
         " gets registered after someone judges it, and registering eleven now would write \"we do not know\" into the\n"
         " allowlist, which is the opposite of what the tool is for. So it fails, and failing is the right state for it\n"
         " to be in. It has no bearing on the suite, which runs dotnet test.\n\n"
         "Figures: suite 2219 with no failures and no product code touched, count 174,336, inline literals 268 to 328,\n"
         " not-in-pool 29 to 40, unregistered zero to eleven, scanner exit code one.\n\n"
         "Unknown: which of the eleven really do not exist, pending a per-item judgement that has already found one false\n"
         " positive.\n\n"
         "The lesson is that a guard reporting zero can be honest and useless at once, if its domain excludes the class\n"
         " where the defect lives -- and that the exclusion was a single continue with a comment saying what it was doing.\n"
         " I had read that output five times and never once asked what it scanned.\n\n"
         "One tool changed; suite green at 2219 and the scanner correctly red at eleven."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()