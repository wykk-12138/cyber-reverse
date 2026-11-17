"""Record R1016: the pool's lines carry an address column, so the prefix rule matched nothing."""

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
### 池子的行带地址列，所以我的前缀规则一次都没生效；修完 11 → 10，而 10 个全是真的（R1016）

**R1015 说下一轮判那 11 个，先修假阳性。修了，而修的**第一版**也是坏的。**

### ① 第一版前缀规则：加对了，跑起来什么都没变

**想法是对的：`proven()` 只做**完全相等**判定，而 `product_feed/threads/v2/` 对镜像的
`product_feed/threads/v2?fields=` 不相等 —— 所以加一条「池里有串**以此前缀开头**」。**

**→ 跑完仍是 **11**，而 `NikeFlow.cs:235` 还在。**
**→ 所以那条规则一次都没命中。**

### ② 原因：`pe_strings.txt` 的行是 `0x地址  串`，不是裸串

```
RAW: '0x0705312c  https://api.nike.com/product_feed/threads/v2?fields='
```

**→ 我用 `line.strip()` 建集合，地址列跟着留下来。
→ 于是 `startswith("https://…")` 在问「这一行以 URL 开头吗」，而行以 `0x0705…` 开头 —— **永不成立**。**

**→ 而 `proven()` 里原来的 `value in pool` 一直是对的，因为那是**全文子串**搜索，
地址列不影响它。**所以「相等」路径好，「前缀」路径死** —— 而两条路径的输出混在同一份报告里，
看起来像「前缀规则证明它们真的不在」。**

### ③ 修第二版：剥掉地址列

```python
if line.startswith("0x"):
    parts = line.split("  ", 1)
    if len(parts) == 2:
        line = parts[1]
```

**→ 再跑：`not in pool 40 → 39` · `unknown 11 → 10`，而消失的正是 `NikeFlow.cs:235`。**
**→ 那个假阳性**上一轮就预测到了**，而这一轮它自己消失了 —— 那是修对了的判据。**

### ④ 而剩下 10 个，逐个问 IDB：**全部真的不存在**

**§2.7b：抽样池找不到不代表镜像没有。所以六个不同前缀逐个查 `ida.py str`：**

| 前缀 | IDB | n |
|---|---|---|
| `/api/ff-products/v1/products` | **NOT IN IMAGE** | 0 |
| `/api/basket/v1` | **NOT IN IMAGE** | 0 |
| `/api/checkout/v1/basket` | **NOT IN IMAGE** | 0 |
| `buy/carts/v2` | **NOT IN IMAGE** | 0 |
| `/discount` | **NOT IN IMAGE** | 0 |
| `/api/payments` | **NOT IN IMAGE** | 0 |

**→ 所以那 10 行**全是自造的**：Farfetch ×7 · Nike ×1 · StoreFlow ×2。**

**→ 而 `/discount` 与 `/api/payments` 让我意外 —— 那是**通用词**，我原以为会命中。
→ 0 命中说明那两个打点也是自造的。**

### ⑤ 所以工具现在**红着 10，而那是准确的状态**

**→ 10 个都经 IDB 定性为不存在，所以它们**不是**假阳性、**不是**待判 —— 是**真的缺陷**。
→ 而把 10 个登记进 ledger 会把真缺陷写进白名单 ⇒ 仍然不登记。**

**→ 而这 10 个的修法与 Nike 那 4 处同类：需要知道每个站的**真实**端点，而那要取证。
→ 留作下一轮。**

### ⑥ 数字

| 度量 | R1015 | **R1016** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0**（未改产品代码） |
| 函数数 | 174,336 | **174,336** |
| **扫到的内联字面量** | 328 | **328** |
| **不在池里** | 40 | **39** |
| **未登记（真缺陷）** | 11 | **10** |
| **其中经 IDB 定性** | 1（另 10 未判） | **10（全 0 命中）** |
| **假阳性** | 1（预测） | **1（已消除）** |
| **工具两处缺陷** | 插值跳过 | **+ 池行带地址列** |

### 教训

> **一个修好的判据如果**没有输出变化**，那不是「确认了原结论」，是「新判据没生效」。
> → 而我第一版前缀规则跑完没变化时，第一反应是「所以它们真的不在」—— 而正确的反应是
> 「这条规则**测过**吗」。**
> **→ 那是 R1015 那条教训的同一层：一个「0」可以是真的和没用的。这次它是**没用的 0**，
> 而我没有先问它有没有生效。**
"""

if "池子的行带地址列" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1016 轮：池子的行带地址列，所以前缀规则一次都没生效

### ① 第一版前缀规则：加对了，跑起来什么都没变

**`proven()` 只做**完全相等**判定，而 `product_feed/threads/v2/` 对镜像的 `product_feed/threads/v2?fields=`
不相等 —— 所以加一条「池里有串以此前缀开头」。**
**→ 跑完仍是 **11**，`NikeFlow.cs:235` 还在 ⇒ **那条规则一次都没命中。**

### ② 原因：`pe_strings.txt` 的行是 `0x地址  串`

```
RAW: '0x0705312c  https://api.nike.com/product_feed/threads/v2?fields='
```

**→ `line.strip()` 保留地址列 ⇒ `startswith("https://…")` 在问「这一行以 URL 开头吗」，而行以 `0x…` 开头。
→ 而 `value in pool`（全文子串）一直是对的，地址列不影响它 ⇒ **「相等」路径好，「前缀」路径死，
两条路径的输出混在同一份报告里，看起来像「前缀规则证明它们真的不在」。**

### ③ 修第二版：剥掉地址列

**→ 再跑：`not in pool 40 → 39` · `unknown 11 → 10`，而消失的正是 `NikeFlow.cs:235`。**
**→ 那个假阳性**上一轮就预测到了**，这一轮它自己消失了 —— 那是修对了的判据。**

### ④ 而剩下 10 个，逐个问 IDB：**全部真的不存在**

| 前缀 | IDB |
|---|---|
| `/api/ff-products/v1/products` · `/api/basket/v1` · `/api/checkout/v1/basket` | **0 命中** |
| `buy/carts/v2` · `/discount` · `/api/payments` | **0 命中** |

**→ 那 10 行全是自造的：Farfetch ×7 · Nike ×1 · StoreFlow ×2。**
**→ `/discount` 与 `/api/payments` 是**通用词**，我原以为会命中 —— 0 命中说明那两个打点也是自造的。**

### ⑤ 所以工具现在**红着 10，而那是准确的状态**

**→ 10 个都经 IDB 定性为不存在 ⇒ 不是假阳性、不是待判，是**真缺陷**。
→ 登记进 ledger 会把真缺陷写进白名单 ⇒ 仍然不登记。
→ 修法与 Nike 那 4 处同类：需要每个站的**真实**端点，那要取证。留作下一轮。**

### ⑥ 数字

| 度量 | R1015 | **R1016** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0**（未改产品代码） |
| 函数数 | 174,336 | **174,336** |
| **不在池里** | 40 | **39** |
| **未登记（真缺陷）** | 11 | **10** |
| **其中经 IDB 定性** | 1 | **10（全 0 命中）** |
| **假阳性** | 1（预测） | **1（已消除）** |

### 教训

> **一个修好的判据如果**没有输出变化**，那不是「确认了原结论」，是「新判据没生效」。
> → 而我第一版前缀规则跑完没变化时，第一反应是「所以它们真的不在」—— 而正确的反应是「这条规则**测过**吗」。**
> **→ 那是 R1015 那条教训的同一层：一个「0」可以是真的和没用的。这次它是**没用的 0**，
> 而我没有先问它有没有生效。**
"""

BACKLOG_ADD = """

## 判据 (c)/(f) — **池行带地址列 ⇒ 前缀规则一次没生效；修完 11 → 10，而 10 个经 IDB 全 0 命中**（R1016）

### 两处工具缺陷

1. **R1015：插值模板被一行 `continue` 跳过**（已修）
2. **R1016：`pool_lines` 用 `line.strip()`，而 `pe_strings.txt` 的行是 `0x地址  串`**
   ⇒ `startswith(URL)` 永不成立 ⇒ **新加的前缀规则一次都没命中，而输出看起来没变化**

**→ 不变量：一个修好的判据如果**没有输出变化**，先问「它测过吗」。**

### 修完的结果

```
not in pool: 40 → 39      unknown: 11 → 10
消失的那一条 = NikeFlow.cs:235（product_feed/threads/v2/）—— R1015 预测的假阳性，自己消失了
```

### 剩下 10 个经 IDB 定性：**全部真的不存在**

| 前缀 | n |
|---|---|
| `/api/ff-products/v1/products` · `/api/basket/v1` · `/api/checkout/v1/basket` | **0** |
| `buy/carts/v2` · `/discount` · `/api/payments` | **0** |

**→ Farfetch ×7 · Nike ×1 · StoreFlow ×2，全是自造端点。**

### 不登记进 ledger

**10 个都经 IDB 定性为不存在 ⇒ 是真缺陷，不是待判。登记 = 把真缺陷写进白名单。**

### 数字

**套件 2219/0 · 函数数 174,336 · 内联字面量 328 · 不在池 39 · 未登记 10 · IDB 定性 10/10 全 0 · 假阳性 1（已消）**

| 仍 Unknown | |
|---|---|
| Farfetch 的真实端点 | 待取证 |
| Shopify `/discount` 与 `/api/payments` 的真实形 | 待取证 |

**纪律**：判据修好后输出没变，先问它测过没有。
"""

BLOCKER = """

---

## 440. **池行带地址列 ⇒ 前缀规则一次没生效；修完 11 → 10，10 个经 IDB 全 0 命中**

> R1016。**改 1 个工具。** 套件 **2219 通过 / 0 失败**（未改产品代码）。

### 一、第一版前缀规则：加对了，跑起来什么都没变

**`proven()` 只做**完全相等**判定，而 `product_feed/threads/v2/` 对镜像的
`product_feed/threads/v2?fields=` 不相等 —— 所以加一条「池里有串**以此前缀开头**」。**

**→ 跑完仍是 **11**，而 `NikeFlow.cs:235` 还在。
→ 所以那条规则一次都没命中。**

### 二、原因：`pe_strings.txt` 的行是 `0x地址  串`，不是裸串

```
RAW: '0x0705312c  https://api.nike.com/product_feed/threads/v2?fields='
```

**→ 我用 `line.strip()` 建集合，地址列跟着留下来。
→ 于是 `startswith("https://…")` 在问「这一行以 URL 开头吗」，而行以 `0x0705…` 开头 —— **永不成立**。**

**→ 而 `proven()` 里原来的 `value in pool` 一直是对的，因为那是**全文子串**搜索，地址列不影响它。
→ **所以「相等」路径好，「前缀」路径死** —— 而两条路径的输出混在同一份报告里，
  看起来像「前缀规则证明它们真的不在」。**

### 三、修第二版：剥掉地址列

```python
if line.startswith("0x"):
    parts = line.split("  ", 1)
    if len(parts) == 2:
        line = parts[1]
```

**→ 再跑：`not in pool 40 → 39` · `unknown 11 → 10`，而消失的正是 `NikeFlow.cs:235`。
→ 那个假阳性**上一轮就预测到了**，而这一轮它自己消失了 —— 那是修对了的判据。**

### 四、剩下 10 个，逐个问 IDB：**全部真的不存在**

| 前缀 | IDB | n |
|---|---|---|
| `/api/ff-products/v1/products` | **NOT IN IMAGE** | 0 |
| `/api/basket/v1` | **NOT IN IMAGE** | 0 |
| `/api/checkout/v1/basket` | **NOT IN IMAGE** | 0 |
| `buy/carts/v2` | **NOT IN IMAGE** | 0 |
| `/discount` | **NOT IN IMAGE** | 0 |
| `/api/payments` | **NOT IN IMAGE** | 0 |

**→ 所以那 10 行**全是自造的**：Farfetch ×7 · Nike ×1 · StoreFlow ×2。
→ 而 `/discount` 与 `/api/payments` 让我意外 —— 那是**通用词**，我原以为会命中。
  0 命中说明那两个打点也是自造的。**

### 五、工具现在红着 10，而那是准确的状态

**→ 10 个都经 IDB 定性为不存在，所以它们**不是**假阳性、**不是**待判 —— 是**真的缺陷**。
→ 而把 10 个登记进 ledger 会把真缺陷写进白名单 ⇒ 仍然不登记。
→ 修法与 Nike 那 4 处同类：需要知道每个站的**真实**端点，而那要取证。留作下一轮。**

### 六、数字

| 度量 | R1015 | R1016 |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0（未改产品代码）** |
| 函数数 | 174,336 | **174,336** |
| **扫到的内联字面量** | 328 | **328** |
| **不在池里** | 40 | **39** |
| **未登记（真缺陷）** | 11 | **10** |
| **其中经 IDB 定性** | 1（另 10 未判） | **10（全 0 命中）** |
| **假阳性** | 1（预测） | **1（已消除）** |
| **工具两处缺陷** | 插值跳过 | **+ 池行带地址列** |

### 七、验证

```
cd replica
python tools/endpoint-provenance.py
  -> inline URL/path literals: 328 · not in pool: 39 · registered in ledger: 29
  -> unknown (invented and unregistered): 10 · baseline: 0
  -> FAIL: 10 unregistered inline endpoints, above the 0 baseline
cd ..
python analysis/ida.py str "/api/ff-products/v1/products"  -> {"n":0}
python analysis/ida.py str "/api/basket/v1"                -> {"n":0}
python analysis/ida.py str "/api/checkout/v1/basket"       -> {"n":0}
python analysis/ida.py str "buy/carts/v2"                  -> {"n":0}
python analysis/ida.py str "/discount"                     -> {"n":0}
python analysis/ida.py str "/api/payments"                 -> {"n":0}
cd replica && python tools/metrics_report.py -> 完整套件 exit 0  2219 / 0 / 0
```

### 八、仍然 Unknown

- **Farfetch 的真实端点**：**待取证**。
- **Shopify `/discount` 与 `/api/payments` 的真实形**：**待取证**。

### 九、教训

**一个修好的判据如果**没有输出变化**，那不是「确认了原结论」，是「新判据没生效」。**

**→ 而我第一版前缀规则跑完没变化时，第一反应是「所以它们真的不在」——
而正确的反应是「这条规则**测过**吗」。**

**→ 那是 R1015 那条教训的同一层：一个「0」可以是真的和没用的。这次它是**没用的 0**，
而我都没有先问它有没有生效。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1016", BLOCKER)
    ensure(RSTATUS, "R1016", BLOCKER)
    ensure(RVERDICT, "第 1016 轮", VERDICT)
    ensure(BACKLOG, "R1016", BACKLOG_ADD)

    note = (
        "\n## R1016 补充 — **池行带地址列 ⇒ 前缀规则一次没生效；修完 11 → 10，10 个经 IDB 全 0 命中**\n\n"
        "**第一版前缀规则加对了，跑起来什么都没变**（仍 11，`NikeFlow.cs:235` 还在）⇒ 它**一次都没命中**。\n"
        "**原因**：`pe_strings.txt` 的行是 `0x地址  串`：\n"
        "`'0x0705312c  https://api.nike.com/product_feed/threads/v2?fields='`\n"
        "→ `line.strip()` 保留地址列 ⇒ `startswith(URL)` 永不成立。\n"
        "→ 而 `value in pool`（全文子串）一直对 ⇒ **「相等」路径好，「前缀」路径死，两条输出混在一份报告里。**\n\n"
        "**修第二版**（剥掉 `0x…  ` 前缀）后再跑：`not in pool 40 → 39` · `unknown 11 → 10`，\n"
        "而消失的正是 `NikeFlow.cs:235` —— **R1015 预测的假阳性，自己消失了。**\n\n"
        "**剩 10 个逐个问 IDB：六个不同前缀**全** 0 命中**：\n"
        "`/api/ff-products/v1/products` · `/api/basket/v1` · `/api/checkout/v1/basket` ·\n"
        "`buy/carts/v2` · `/discount` · `/api/payments`。\n"
        "→ **10 行全是自造**：Farfetch ×7 · Nike ×1 · StoreFlow ×2。\n"
        "→ 而 `/discount` 与 `/api/payments` 是通用词，我原以为会命中 —— 0 说明那两个打点也自造。\n\n"
        "**工具红着 10 是准确状态**：10 个经 IDB 定性为不存在 ⇒ 真缺陷，不是待判 ⇒ 仍不登记进 ledger。\n\n"
        "数字：套件 2219/0 · 函数数 174,336 · 内联字面量 328 · 不在池 39 · 未登记 10 · IDB 定性 10/10 全 0。\n\n"
        "纪律：**判据修好后输出没变，先问它测过没有。**\n\n"
        "下一轮：取证 Farfetch 与 Shopify 的真实端点，改那 10 处。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1016" not in h:
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
             for p, k in ((RBLOCK, "R1016"), (RSTATUS, "R1016"), (RVERDICT, "第 1016 轮"), (BACKLOG, "R1016")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1016: the pool's lines carry an address column, so the prefix rule matched nothing\n\n"
         "R1015 ended by predicting that one of the eleven reported names was a false positive, because\n"
         " product_feed/threads/v2 is in the image and only reads as absent when compared for equality against a\n"
         " constant that carries a query string. The fix for that is a prefix rule.\n\n"
         "I wrote the rule and the numbers did not move. Eleven before, eleven after, the same name still listed. My\n"
         " first reading was that this confirmed them -- and the right reading was to ask whether the new rule had run\n"
         " at all.\n\n"
         "It had not. pe_strings.txt stores one string per line as an address and a string: 0x0705312c followed by two\n"
         " spaces followed by the URL. My line set kept the address column, so asking whether a line starts with\n"
         " https:// was asking whether it starts with 0x, and the answer was always no. The equality path was never\n"
         " affected because that one searches the file's whole text as a substring, which is why the two paths sat in\n"
         " one report looking like agreement when one of them was dead.\n\n"
         "Stripping the column moved the numbers exactly as predicted: not-in-pool 40 to 39 and unregistered 11 to 10,\n"
         " with product_feed/threads/v2 disappearing on its own. A prediction that the fix then realises is what makes\n"
         " it a fix rather than a rewrite.\n\n"
         "The ten that remain were then asked of the IDB one by one, six distinct prefixes behind ten lines, and every\n"
         " one returns zero. So they are not false positives and not pending: seven Farfetch paths, one Nike cart path\n"
         " and two Shopify paths, all invented. Two of them surprised me -- /discount and /api/payments read like\n"
         " general vocabulary and I expected hits, and zero means those two call sites are invented as well.\n\n"
         "The scanner therefore fails with ten, and ten is the accurate count, so I still do not register them. A name\n"
         " goes into the ledger once someone judges it; writing these in would put a real defect on an allowlist.\n\n"
         "Figures: suite 2219 with no failures, count 174,336, inline literals 328, not-in-pool 39, unregistered 10, all\n"
         " ten judged absent by the IDB, one false positive eliminated, two defects fixed in the scanner across two\n"
         " rounds.\n\n"
         "Unknown: Farfetch's real endpoints, and the real shape of the two Shopify paths.\n\n"
         "The lesson is that a corrected check producing no change means the check did not run, not that the old\n"
         " answer stands -- which is R1015's lesson one layer down, since a zero can be honest and useless at once and\n"
         " I did not stop to ask whether this one had even executed.\n\n"
         "One tool changed; suite green at 2219 and the scanner correctly red at ten."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()