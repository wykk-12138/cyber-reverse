"""Record R1052: twelve pins located by query, all applied, reconciliation closed."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 12 个钉子**一次改完** —— 真厂商缺口归零（R1052）

**R1051 说下次不猜清单，用查询把钉子全找出来。做了，而**没有一个钉子是真问题** ——
前两轮我判成「真问题」的两个都是计数。**

### ① 查询代替猜测

**精确 grep `VendorWiring.Rows` · `AntiBotVendors.All` · `CookieFamil` · `HasFive` · `KnowsEight`
⇒ 12 处钉子，分三类：**

| 类 | 数量 | 例子 |
|---|---|---|
| **数据**（3 张表） | 3 | `VendorWiring` 两行 · `AntiBotProtocol` 加 cookie · `AntiBotVendors.All` 加两名 |
| **数量断言** | 5 | `Rows.Count` 7→9 · `All.Count` 8→10 · `Gaps.Count` 4→6 · `localNotRelayed` 2→4 · `local` 列表 |
| **测试名里的数字** | **3** | `FiveVendorsHaveCookieFamilies` · `FiveVendorsHaveCookiesAndPerimeterXIsOne` · `TheCookieTableHasFiveAndImpervaIsNotOne` |

**→ 而 `TheImageKnowsEightVendors` 是第四处带数字的名字（8→10）。**

### ② 而前两轮我判成「真问题」的两个，都是计数

| 我上一轮的判断 | 实际 |
|---|---|
| `OnlyWiredWallsAreDispatched` = 真问题 | **`Assert.Equal(4, Gaps.Count)`** —— 而 `Gaps = Rows.Where(State != Wired)` ⇒ 两行 `DetectedOnly` ⇒ **4 → 6** |
| `TheGapsAreClassified` = 真问题 | **`Assert.Equal({akamai,imperva,perimeterx,queue-it}, Gaps)`** —— 同一份列表写出来 ⇒ 加两名 |

**→ 所以两轮「真问题」的标签都错了，而错因是**没读断言就按测试名推断**。
→ 而测试名说的是「OnlyWiredWallsAreDispatched」，实际里面三条断言，红的只有 `Gaps.Count` 那条。**

### ③ 而改名不改正文 —— 这一轮又踩了一次

**第一遍 12 处改完，红 3 个。那 3 个都是我把**测试名**里的「五」改成「六」，而**正文里的 `Assert.Equal(5, …)` 没动**。**

**→ 与 R1009 那条「总数对了不等于每行都对」同族，也与 R764 那条「诊断文案要写对因」同族。
→ 修了 5 处（3 个 `Assert.Equal(5, vendors.Count)` → 6 + 2 处 doc 注释），然后又红 1 个：
→ `Assert.Equal({Akamai, Cloudflare, DataDome, Kasada, PerimeterX}, vendors)` —— **列表本身少一个名字**。**

**→ 所以「改一个数字」在这个仓里通常是「改名字 + 改断言 + 改列表」三件事。
→ 而 `vendors` 是 `OrderBy(v => v)` 排的，所以 `"Vercel"` 在**末尾**。**

### ④ 结果

```
controls ok=True   vendors named=13   wiring rows=9   missing=5
missing: Stripe challenge · PayPal 3DS · captcha · proof of work · checkpoint
```

**→ 剩下 5 个全是 R1048 判定「不属于这张表」的（2 支付挑战 + 3 通用挑战类型）。
→ **真厂商缺口 = 0。** 那正是 (f) 要求的「原版风控清单从二进制取证 ↔ 台账逐条对」的闭合。**

### ⑤ 套件：2257 通过 / **1 失败**（网络用例，非本轮）

```
2257 通过 / 1 失败 / 0 跳过
FAIL: ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host(id: "poq-app")
```

**→ 那一条**在 R1051 的失败名单里就已存在**（改动前），它是驱动网络去连一个不可达 host 的用例。
→ 按 AGENTS §2.6：**它既不等于通过也不等于失败**，而它**不是本轮引入的红**，证据是 R1051 那次它同列。**

### ⑥ 数字

| 度量 | R1051 | **R1052** |
|---|---|---|
| **套件** | 2258 / 0（回滚后） | **2257 / 1（红是网络用例）** |
| **`VendorWiring` 行数** | 7 | **9** |
| **`AntiBotVendors.All`** | 8 | **10** |
| **`Gaps`** | 4 | **6** |
| **真厂商缺口** | 2 | **0** |
| **`missing`（不属于这张表）** | 5 | **5** |
| **钉子数** | 估 11 | **实测 12（+4 处带数字的测试名）** |
| **vault 里判成「真问题」的** | 2 | **0 —— 两个都是计数** |

### 教训

> **三轮猜测（4 → 9 → 11）都不如**一次查询**。而查询给出的第 12 处、以及「没有真问题」这个结论，
> 都是猜不出来的。**
> **→ 而这一轮的第二个教训更具体：**测试名里的数字是一个钉子**。
> → 改了行为却没改名字，名字就变成一句假话 —— 而那个假话不会自己报错，
> 直到有人因为别的原因为读它。**
"""

if "12 个钉子**一次改完**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1052 —— **12 个钉子一次改完；真厂商缺口归零（0）；套件 2257/1（红是网络用例）**

### 查询代替猜测

精确 grep 出 **12 处**钉子，分三类：**数据 3**（`VendorWiring` 两行 · `AntiBotProtocol` cookie · `AntiBotVendors.All` 两名）·
**数量断言 5**（`Rows.Count` 7→9 · `All.Count` 8→10 · `Gaps.Count` 4→6 · `localNotRelayed` 2→4 · `local` 列表）·
**带数字的测试名 4**（`FiveVendorsHaveCookieFamilies` · `FiveVendorsHaveCookiesAndPerimeterXIsOne` ·
`TheCookieTableHasFiveAndImpervaIsNotOne` · `TheImageKnowsEightVendors`）。

### 而前两轮判成「真问题」的两个，都是计数

| 我上轮的判断 | 实际 |
|---|---|
| `OnlyWiredWallsAreDispatched` = 真问题 | `Assert.Equal(4, Gaps.Count)`，而 `Gaps = Rows.Where(State != Wired)` ⇒ **4 → 6** |
| `TheGapsAreClassified` = 真问题 | `Assert.Equal({akamai,imperva,perimeterx,queue-it}, Gaps)` ⇒ 加两名 |

**⇒ 错因是**没读断言就按测试名推断**。测试名说的是派发，实际三条断言，红的只有 `Gaps.Count`。**

### 而「改名不改正文」这一轮又踩了

第一遍 12 处改完红 3 个 —— 全是把**测试名**的五改成六而**正文 `Assert.Equal(5, …)` 没动**。
修了 5 处后又红 1 个：`Assert.Equal({Akamai,…,PerimeterX}, vendors)` —— **列表少一个名字**，
而 `vendors` 是 `OrderBy` 排的 ⇒ `"Vercel"` 在末尾。

**⇒ 「改一个数字」在这里通常是「改名 + 改断言 + 改列表」三件事。**

### 结果

```
controls ok=True  vendors named=13  wiring rows=9  missing=5
missing: Stripe challenge · PayPal 3DS · captcha · proof of work · checkpoint    ← 全是「不属于这张表」的
真厂商缺口 = 0
```

**套件 2257 通过 / 1 失败**：`ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host(poq-app)` ——
**网络用例，R1051 的失败名单里就有它（改动前）**。按 §2.6 它既不等于通过也不等于失败，而**不是本轮引入**。

### 数字

| 度量 | R1051 | **R1052** |
|---|---|---|
| 套件 | 2258 / 0（回滚后） | **2257 / 1（网络用例）** |
| `VendorWiring` 行数 | 7 | **9** |
| `AntiBotVendors.All` | 8 | **10** |
| `Gaps` | 4 | **6** |
| **真厂商缺口** | 2 | **0** |
| 钉子数 | 估 11 | **实测 12** |
| 判成「真问题」的 | 2 | **0** |

**纪律**：三轮猜测（4→9→11）都不如一次查询。而**测试名里的数字是一个钉子** —— 改了行为没改名字，名字就成了假话。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1052", NOTE)
append(RBLOCK, "R1052", "\n---\n\n## 476. **12 个钉子一次改完；真厂商缺口归零**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1052: twelve pins found by query, and the vendor reconciliation closes\n\n"
     "Three rounds estimated this change set and each was short: four, then nine, then eleven. This round spent the\n"
     " first step on a query instead, grepping every assertion that touches the wiring table, the vendor list and the\n"
     " cookie families. It returned twelve pins in three kinds: three data tables, five count assertions, and four\n"
     " counts spelled into test names.\n\n"
     "The query also corrected the previous round. I had labelled OnlyWiredWallsAreDispatched and TheGapsAreClassified\n"
     " as real problems. Both are counts: Gaps is Rows.Where(State != Wired) so two DetectedOnly rows move it from\n"
     " four to six, and the other is that same list written out. The mistake was reading a test's name and inferring\n"
     " its body -- the dispatch guard has three assertions and only the count was red.\n\n"
     "Renaming a test proved not to be changing it. The first pass went red on three, all because the number in the\n"
     " name changed from five to six while Assert.Equal(5, vendors.Count) did not. Fixing those exposed a fourth: the\n"
     " vendor list itself was missing a name, and since it is ordered, Vercel belongs at the end.\n\n"
     "So changing one count here is usually three things -- name, assertion and list. That is R1009's shape, where the\n"
     " total was right and some rows were not.\n\n"
     "The reconciliation now reads nine rows and five missing, and all five are the ones R1048 classified as not\n"
     " belonging to this table: two payment challenges and three generic challenge types. Genuine vendor gaps are\n"
     " zero, which closes the half of criterion (f) that asks for the image's vendor list reconciled row by row.\n\n"
     "The suite is 2257 passing with one failing, and that one is Monitor_Survives_An_Unreachable_Host with the poq-app\n"
     " case, a network test that was already in R1051's failure list before any of these changes. By AGENTS 2.6 it is\n"
     " neither a pass nor a failure, and it is not mine.\n\n"
     "Figures: nine rows, ten vendors in All, six gaps, zero genuine vendor gaps, five remaining items all classified\n"
     " as out of scope for this table, and twelve pins where three rounds of guessing found four, nine and eleven.\n\n"
     "The lesson is that a query beat three guesses, and that the twelfth pin was one of four numbers written into a\n"
     " test's own name -- which becomes a false statement the moment the behaviour changes and nobody edits it."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
