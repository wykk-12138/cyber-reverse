"""Record R1050: the complete nine-change list for adding one vendor row."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 补一行**实际是九件事** —— 两轮都低估了，而这次拿到了完整清单（R1050）

**R1049 说「补一行是四件事」。这一轮把四步全做了（五个 patch 全 applied），而套件红了 **5** 个 —— 不是四件，是九件。**

### ① 第一次尝试：五处改了，五处红

| 改了 | 结果 |
|---|---|
| `AntiBotProtocol` += `["Vercel"] = "_vcrcs"` | ✓ |
| `VendorWiring` += 两行 | ✓ |
| `VendorWiringTests` 7→9 · wired 列表加两名字 | ✓ |
| `VendorSolvingModeTests` local 列表加两名字 | ✓ |
| `VendorSolvingModeTests` `localNotRelayed` 2→4 | ✓ |

**→ vendor 相关 15 个测试**全过**。而**全量**红了 **5** 个，全在别处：**

| 红 | 为什么 |
|---|---|
| `VendorNegativeClaimsTests.TheCookieTableHasFiveAndImpervaIsNotOne` | **名字里写「五」** —— 加了 `_vcrcs` 变 6 |
| `PerimeterXProtocolTests.FiveVendorsHaveCookiesAndPerimeterXIsOne` | 同上 |
| `AntiBotProtocolTests.FiveVendorsHaveCookieFamilies` | 同上 |
| **`AntiBotProtocolTests.EveryProtocolVendorIsAKnownVendor`** | **真问题**：`Vercel` 进了 cookie 表，但**不在 `AntiBotVendors`** |
| **`WallDispatchTests.OnlyWiredWallsAreDispatched`** | 两个新 `Wired` 行**没在 dispatch 表**里 |

**→ 前三个是「五」这个数字散落在三个测试名里；后两个是真缺口：一个新厂商要同时进 `AntiBotVendors` 与 wall dispatch。**
**→ 所以「补一行」的真实范围是 **九处**，而两轮我分别估成四和五。**

### ② 所以本轮再次回滚，而这次交的是**清单**

**回滚后：`rows=7 · missing=7` · 套件 **2258 / 0 / 0**。**

**→ 而那是对的处置：九处里有两处是**真判断**（新厂商要不要进 `AntiBotVendors`、要不要进 wall dispatch），
→ 硬塞会让那两处变成「为了让测试变绿而加的项」，而那正是 R48 说的移动失败。**

### ③ 完整清单（第三次尝试可一次做完）

| # | 文件 | 改动 | 性质 |
|---|---|---|---|
| 1 | `VendorWiring.cs` | + `Row("botdeflector", …)` | 数据 |
| 2 | `VendorWiring.cs` | + `Row("vercel", …)` | 数据 |
| 3 | `AntiBotProtocol.cs` | + `["Vercel"] = new[] { "_vcrcs" }` | 数据 |
| 4 | `VendorWiringTests.cs` | `7` → `9` | 计数 |
| 5 | `VendorWiringTests.cs` | wired 列表 + 两名（**行序**） | 枚举 |
| 6 | `VendorSolvingModeTests.cs` | local 列表 + 两名（**行序**） | 枚举 |
| 7 | `VendorSolvingModeTests.cs` | `localNotRelayed` `2` → `4` | 计数 |
| 8 | 三个测试的**「五」** | `TheCookieTableHasFive…` · `FiveVendorsHaveCookies…` · `FiveVendorsHaveCookieFamilies` | 计数（**含测试名**） |
| 9 | **`AntiBotVendors`** + **wall dispatch** | 新厂商要不要进这两张表 —— **真判断** | **判断** |

**→ 第 9 项是唯一的真判断，而它决定 8 与 1–3 的写法：
→ 若 `botdeflector`/`vercel` 该进 `AntiBotVendors` 与 dispatch，那 `EveryProtocolVendorIsAKnownVendor` 与
`OnlyWiredWallsAreDispatched` 是**在提示我漏了一处**；若不该进，那两个新行**不该是 `State.Wired`**。**

### ④ 而那是本轮真正的收获

**→ 九处里八处是机械的，一处是判断 —— 而那一处决定其余八处的正确形态。
→ 所以第三次尝试的第一步不是改代码，是**先答第 9 项**。**

### ⑤ 数字

| 度量 | R1049 | **R1050** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（回滚后）** |
| 产物陈旧度 | 1 / 277 | **2 / 429** |
| 函数数 | 174,293 | **174,293** |
| **改了几处** | 0 | **5（全部 applied）** |
| **transient 红** | — | **5（3 计数 + 2 真缺口）** |
| **vendor 测试** | — | **15 全过** |
| **`VendorWiring` 行数** | 7 | **7（回滚）** |
| **真厂商缺口** | 2 | **2（回滚）** |
| **真实范围** | 「4 件事」 | **9 件事（8 机械 + 1 判断）** |

### 教训

> **两轮都在同一个地方回滚 —— 而那说明我该交的不是第三次尝试，是**完整清单**。
> → 而清单里最有价值的一行是第 9 项：它说明**第 1–8 项的正确形态取决于一个新厂商该不该进另外两张表**。
> → 所以在答第 9 项之前，任何一次「把数字改绿」都是**为了让测试闭嘴**。**
"""

if "补一行**实际是九件事**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1050 —— **补一行实际是九件事；五处改了、五处红、回滚；完整清单已固化**（套件 2258 绿）

### 第一次尝试与结果

改了 5 处（`AntiBotProtocol` += Vercel cookie · `VendorWiring` += 两行 · 4 个守卫数字/列表），
**vendor 相关 15 个测试全过**，而**全量红 5 个**：

| 红 | 性质 |
|---|---|
| `TheCookieTableHasFiveAndImpervaIsNotOne` | **计数**（名字里写「五」） |
| `FiveVendorsHaveCookiesAndPerimeterXIsOne` | **计数** |
| `AntiBotProtocolTests.FiveVendorsHaveCookieFamilies` | **计数** |
| **`EveryProtocolVendorIsAKnownVendor`** | **真缺口**：`Vercel` 不在 `AntiBotVendors` |
| **`OnlyWiredWallsAreDispatched`** | **真缺口**：新 `Wired` 行不在 wall dispatch |

**⇒ 真实范围是 9 处：8 机械 + 1 判断。已回滚，套件 **2258 / 0 / 0**。**

### 完整清单（第三次尝试照此做）

1. `VendorWiring.cs` + `Row("botdeflector", "BotDeflector", null, State.Wired, …)`
2. `VendorWiring.cs` + `Row("vercel", "x-vercel-challenge-token", "_vcrcs", State.Wired, …)`
3. `AntiBotProtocol.cs` + `["Vercel"] = new[] { "_vcrcs" }`
4. `VendorWiringTests.cs` `7` → `9`
5. `VendorWiringTests.cs` wired 列表 + 两名（**行序**）
6. `VendorSolvingModeTests.cs` local 列表 + 两名（**行序**）
7. `VendorSolvingModeTests.cs` `localNotRelayed` `2` → `4`
8. 三处**「五」**：`TheCookieTableHasFive…` · `FiveVendorsHaveCookies…` · `FiveVendorsHaveCookieFamilies`
9. **真判断**：新厂商该不该进 `AntiBotVendors` 与 wall dispatch ⇒ **决定 1–8 的正确形态**

### 而第 9 项是必须先答的

**若该进 ⇒ 那两个红是「漏了一处」的提示；若不该进 ⇒ 两个新行**不该是 `State.Wired`**。
→ 在答它之前改任何数字都是**为了让测试闭嘴**。**

### 数字

| 度量 | R1049 | **R1050** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 陈旧度 | 1 / 277 | **2 / 429** |
| 函数数 | 174,293 | **174,293** |
| **改了几处** | 0 | **5（全 applied）** |
| **transient 红** | — | **5（3 计数 + 2 真缺口）** |
| **vendor 测试** | — | **15 全过** |
| **真实范围** | 「4 件事」 | **9 件事** |

**纪律**：两轮在同一处回滚 ⇒ 该交的是完整清单，不是第三次尝试。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1050", NOTE)
append(RBLOCK, "R1050", "\n---\n\n## 474. **补一行实际是九件事（8 机械 + 1 判断）；完整清单已固化**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1050: adding one vendor row is nine changes, and the ninth is a judgement\n\n"
     "R1049 estimated four changes and reverted. This round did all four -- five patches, all applied -- and the vendor\n"
     " tests went green, fifteen of them. The full suite then failed five elsewhere.\n\n"
     "Three of the five are a count spelled into three test names: the cookie table is described as having five\n"
     " entries, and registering _vcrcs makes six. Two are not counting. EveryProtocolVendorIsAKnownVendor says Vercel\n"
     " now appears in the cookie table without appearing in AntiBotVendors, and OnlyWiredWallsAreDispatched says two\n"
     " rows marked Wired are not in the wall dispatch table.\n\n"
     "So the real scope is nine: eight mechanical, one a judgement. And the judgement is first, because it decides the\n"
     " correct shape of the other eight. If a vendor is supposed to be known to AntiBotVendors and dispatched as a\n"
     " wall, then those two failures are telling me I missed a place. If it is not, then the two rows should not be\n"
     " State.Wired at all, and the rows themselves are wrong rather than the tables being incomplete.\n\n"
     "Everything went back. Suite green at 2258, seven rows, two genuine gaps, unchanged.\n\n"
     "Figures: suite 2258 green after the revert, freshness two files and 429 lines, count 174,293, five patches\n"
     " applied and reverted, five transient failures of which two were real gaps, fifteen vendor tests green, and the\n"
     " scope estimate moving from four to nine.\n\n"
     "Two rounds have now been reverted at the same place, which is the signal that what this round owed was not a\n"
     " third attempt but the complete list. The most valuable line in it is the ninth: everything above depends on an\n"
     " answer I have not given yet, and nudging numbers to make tests quiet before giving it would be the failure mode\n"
     " R48 named.\n\n"
     "Next: answer whether these two vendors belong in AntiBotVendors and the wall dispatch table. Then the eight\n"
     " mechanical changes follow from that answer."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
