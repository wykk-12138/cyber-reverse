"""Record R1024: akamai was missing from an audit that already listed it elsewhere."""

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
### 原版解**六个**厂商；而台账漏了最有据的那个（R1024）

**R1023 说下一轮定 `DetectedOnly` 该改成什么。要定它，先得知道**原版解哪些** —— 于是把 `Solving …` 形一次问完。**

### ① 而第一次问又撞上截断 —— 这次是**工具**的

**`ida.py str "Solv"` 返回 `n=40`，而**40 就是它的返回上限**，不是真实数量。
→ 40 条里**没有** `Solving PerimeterX`。
→ 所以我**又一次**读了一个被截断的答案 —— 而 R1023 才刚立过这条纪律。**

**→ 正解不是读前 40 条，是**把问题问小**：用 `"Solving Cloudflare"` / `"Solving Akamai"` 这种窄 probe，
让结果落在上限内。那与「截断自己的输出」是同一件事的两面：**问得宽，答案就被砍。****

### ② 而窄了之后，答案完整了

| probe | n | 内容 |
|---|---|---|
| `Solving Cloudflare` | **14** | 8 条阶段（`analyzing` · `loading challenge` · `queued` · `reloading` · `(1)` · `(2)`）+ `Failed Solving Cloudflare (no clearance)` / `(too many rounds)` |
| `Solving Kasada` | 2 | `Failed solving Kasada` · `(TL)` |
| `Solving DataDome` | 1 | `Solving DataDome (I)` |
| **`Solving Incapsula`** | **0** | **imperva 的第三个独立证据** |
| `Solving Akamai` | **3** | `(` · `(SBSD)` · `(SDS)` |
| `Solving Queue` | 1 | `Error Solving Queue-it (Softblock)` |
| `Solving PerimeterX` | 1 | `Solving PerimeterX` |

**→ 原版解 **cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx** —— 六个。
→ 而 **`Solving Incapsula` = 0**，imperva 现在有三个独立来源说它不在（六拼写 · 台账 · 无 solver 文案）。**

### ③ 而 `Solving Akamai` 三条，加上 `endpoints.md` 的 25 条 —— 台账里**没有 akamai**

**`AntiBotVendors.All` 有 8 个厂商，含 Akamai；而 `VendorWiring.Rows` 只有 6 行，**不含 akamai**。**

**→ 镜像是真的**详细**记录它：**
```
检测   AkamaiGHost · AkamaiQueueName · AkamaiReferer
解     "Solving Akamai (" · "(SBSD)" · "(SDS)"
失败   "Akamai Failed" · "Akamai Failed (Rotating)" · "Akamai Blocked (IP)" · "Akamai block"
控制   SkipAkamai · "Akamai disabled"
内部   GetAkamaiCookie · AkamaiHandler · AkamaiQueueHandler · AkamaiPixel · AkamaiGenerator*
```

### ④ 而 akamai 这一行正好演示 `Gap` 与 `State` 是**两个问题**

| 列 | akamai 的值 | 含义 |
|---|---|---|
| **`Gap`** | **`None`** | marker（`AkamaiGHost`）是**镜像的** |
| **`State`** | **`DetectedOnly`** | **复刻件没有 akamai solver** |

**→ 所以 `DetectedOnly` 说的是**复刻件**，不是**镜像**。
→ 而那回答了 R1023 那个问题：**`DetectedOnly` 不该改** —— 它本来就没在说镜像。
→ **它说的东西需要被**说清**（Note 里现在写了），而不是被改掉。****

### ⑤ 六 → 七行，四条守卫跟着动

| 守卫 | 从 | 到 |
|---|---|---|
| `ThreeOfSixAreWired` | 6 行 | **`ThreeOfSevenAreWired`（7 行）** |
| `TheGapsAreClassified` | `Gaps` = 3 个 | **4 个（按**行序**，akamai 在 imperva 前）** |
| 同上 | — | **加 `akamai.Gap == None` 且 `State == DetectedOnly` 的并列断言** |
| `OnlyWiredWallsAreDispatched` | `Gaps.Count == 3` | **`== 4`** |

**→ 而 `Gaps` 是**行序**不是字母序 —— 我第一版按字母序写，红了。那是 R1009 的老账，又犯一次。**

### ⑥ 数字

| 度量 | R1023 | **R1024** |
|---|---|---|
| 套件 | 2233 / 0 | **2233 / 0 / 0** |
| 产物陈旧度 | 4 / 3,795 | **4 / 3,816** |
| 函数数 | 174,336 | **174,336** |
| **`VendorWiring.Rows`** | 6 | **7（+akamai）** |
| **原版解几个厂商** | 未测 | **6（cloudflare · kasada · datadome · akamai · queue-it · perimeterx）** |
| **imperva 的独立证据** | 2 | **3（+`Solving Incapsula` = 0）** |
| **`DetectedOnly` 该改吗** | 待定 | **不该 —— 它说的是复刻件** |

### 教训

> **「把 `Solv` 一次问完」这个动作本身撞上了工具的 40 条上限 —— 而我第一眼读的是 40 条，不是「40 是上限」。**
> **→ 那与 R1023 的 `[:4]` 是同一件事，只是这次截断不在我的脚本里，在工具里。
> → 而**同样的教训隔一轮就复发**，说明「不截断」不能只靠记住 —— 要靠**看到 n 等于上限就警觉**。
> → 而这一轮真正把它解决的不是警觉，是**把问题问小**。**
"""

if "原版解**六个**厂商" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1024 轮：原版解六个厂商；而台账漏了最有据的那个

### ① 第一次问又撞上截断 —— 这次是**工具**的

**`ida.py str "Solv"` 返回 `n=40`，而**40 是它的返回上限**，不是真实数量 —— 40 条里没有 `Solving PerimeterX`。
→ R1023 才刚立过「不截断」的纪律，隔一轮就复发。
→ **正解不是读前 40 条，是**把问题问小**（窄 probe），让结果落在上限内。**

### ② 窄了之后答案完整

| probe | n |
|---|---|
| `Solving Cloudflare` | **14**（8 条阶段 + `no clearance` / `too many rounds`） |
| `Solving Kasada` · `Solving DataDome` · `Solving PerimeterX` | 2 · 1 · 1 |
| **`Solving Incapsula`** | **0** ← imperva 的第三个证据 |
| `Solving Akamai` | **3**（`(` · `(SBSD)` · `(SDS)`） |
| `Solving Queue` | 1（`Error Solving Queue-it (Softblock)`） |

**→ 原版解**六个**：cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx。**
**→ `Solving Incapsula` = 0 ⇒ imperva 三个独立来源说它不在。**

### ③ 而台账里**没有 akamai**

**`AntiBotVendors.All` 有 8 个含 Akamai；`VendorWiring.Rows` 只有 6 行，不含它。
而镜像是真的**详细**记录它：检测（`AkamaiGHost`/`AkamaiQueueName`/`AkamaiReferer`）· 解（三阶段）·
失败（`Failed (Rotating)` · `Blocked (IP)`）· 控制（`SkipAkamai` · `disabled`）· 内部（5 个 handler/generator）。**

### ④ akamai 这一行正好演示 `Gap` 与 `State` 是两个问题

| 列 | 值 | 含义 |
|---|---|---|
| **`Gap`** | **`None`** | marker 是**镜像的** |
| **`State`** | **`DetectedOnly`** | **复刻件没有 solver** |

**→ 那回答了 R1023 的问题：`DetectedOnly` **不该改** —— 它说的是**复刻件**，不是镜像。
→ 它需要被**说清**（Note 里写了），不是被改掉。**

### ⑤ 六 → 七行，四条守卫跟着动

`ThreeOfSixAreWired` → **`ThreeOfSevenAreWired`** · `Gaps` 3 → **4（按**行序**）** ·
加 `akamai.Gap == None` 与 `State == DetectedOnly` 并列断言 · `OnlyWiredWallsAreDispatched` 3 → **4**

**→ 我第一版按**字母序**写 `Gaps`，红了 —— 那是 R1009 的老账，又犯一次。**

### ⑥ 数字

| 度量 | R1023 | **R1024** |
|---|---|---|
| 套件 | 2233 / 0 | **2233 / 0 / 0** |
| 产物陈旧度 | 4 / 3,795 | **4 / 3,816** |
| 函数数 | 174,336 | **174,336** |
| **`Rows`** | 6 | **7（+akamai）** |
| **原版解几个厂商** | 未测 | **6** |
| **imperva 独立证据** | 2 | **3** |
| **`DetectedOnly` 该改吗** | 待定 | **不该** |

### 教训

> **「把 `Solv` 一次问完」撞上了工具的 40 条上限 —— 而我第一眼读的是 40 条，不是「40 是上限」。
> → 与 R1023 的 `[:4]` 是同一件事，只是这次截断在工具里不在我的脚本里。
> → 同样的教训隔一轮就复发，说明「不截断」不能只靠记住，要靠**看到 `n` 等于上限就警觉**。
> → 而这一轮真正解决它的不是警觉，是**把问题问小**。**
"""

BACKLOG_ADD = """

## 优先级 ② — **原版解六个厂商；`Rows` 补 akamai（第 7 行）；`DetectedOnly` 说的是复刻件**（R1024）

### 而我又一次读了被截断的答案

**`ida.py str "Solv"` → `n=40`，而 40 是**返回上限**。正解是**把问题问小**（窄 probe），不是读前 40 条。**

### 完整答案（窄 probe）

| probe | n | 备注 |
|---|---|---|
| `Solving Cloudflare` | **14** | 8 条阶段 + `no clearance` / `too many rounds` |
| `Solving Kasada` · `Solving DataDome` · `Solving PerimeterX` | 2 · 1 · 1 | |
| **`Solving Incapsula`** | **0** | **imperva 第三个独立证据** |
| `Solving Akamai` | **3** | `(` · `(SBSD)` · `(SDS)` |
| `Solving Queue` | 1 | `Error Solving Queue-it (Softblock)` |

**→ 原版解**六个**：cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx。**

### 补 akamai（第 7 行）

**`Gap = None`（`AkamaiGHost` 镜像有）而 `State = DetectedOnly`（复刻件无 solver）
⇒ 那一行演示两个列是两个问题。**
**→ 回答 R1023：`DetectedOnly` **不该改** —— 它说的是**复刻件**，不是镜像；需要被**说清**而非改掉。**

### 四条守卫跟着动

`ThreeOfSixAreWired` → `ThreeOfSevenAreWired` · `Gaps` 3 → 4（**行序**，不是字母序 —— 我第一版写错） ·
`OnlyWiredWallsAreDispatched` 3 → 4

### 数字

**套件 2233/0/0 · 陈旧度 4 / 3,816 · 函数数 174,336 · Rows 6 → 7 · 原版解 6 个 · imperva 证据 2 → 3**

| 仍 Unknown | |
|---|---|
| akamai 的 `(SBSD)` / `(SDS)` 各是什么 | 未取证 |
| queue-it softblock 的 solver | 与 `NotAChallenge` 矛盾，待判 |

**纪律**：看到 `n` 等于上限就警觉；更好的解法是把问题问小。
"""

BLOCKER = """

---

## 448. **原版解六个厂商；`Rows` 补 akamai；`DetectedOnly` 说的是复刻件**

> R1024。**改 2 个源文件 + 2 个测试文件。** 套件 **2233 通过 / 0 失败 / 0 跳过**。

### 一、第一次问又撞上截断 —— 这次是**工具**的

**`ida.py str "Solv"` 返回 `n=40`，而**40 就是它的返回上限**，不是真实数量。
→ 40 条里**没有** `Solving PerimeterX`。
→ 所以我**又一次**读了一个被截断的答案 —— 而 R1023 才刚立过这条纪律。**

**→ 正解不是读前 40 条，是**把问题问小**：用 `"Solving Cloudflare"` 这种窄 probe，
  让结果落在上限内。**

### 二、而窄了之后，答案完整了

| probe | n | 内容 |
|---|---|---|
| `Solving Cloudflare` | **14** | 8 条阶段 + `Failed Solving Cloudflare (no clearance)` / `(too many rounds)` |
| `Solving Kasada` | 2 | `Failed solving Kasada` · `(TL)` |
| `Solving DataDome` | 1 | `Solving DataDome (I)` |
| **`Solving Incapsula`** | **0** | **imperva 的第三个独立证据** |
| `Solving Akamai` | **3** | `(` · `(SBSD)` · `(SDS)` |
| `Solving Queue` | 1 | `Error Solving Queue-it (Softblock)` |
| `Solving PerimeterX` | 1 | `Solving PerimeterX` |

**→ 原版解 **cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx** —— 六个。
→ 而 **`Solving Incapsula` = 0**，imperva 现在有三个独立来源说它不在。**

### 三、而 `Solving Akamai` 三条，加上 `endpoints.md` 的 25 条 —— 台账里**没有 akamai**

**`AntiBotVendors.All` 有 8 个厂商，含 Akamai；而 `VendorWiring.Rows` 只有 6 行，**不含 akamai**。**

```
检测   AkamaiGHost · AkamaiQueueName · AkamaiReferer
解     "Solving Akamai (" · "(SBSD)" · "(SDS)"
失败   "Akamai Failed" · "Akamai Failed (Rotating)" · "Akamai Blocked (IP)" · "Akamai block"
控制   SkipAkamai · "Akamai disabled"
内部   GetAkamaiCookie · AkamaiHandler · AkamaiQueueHandler · AkamaiPixel · AkamaiGenerator*
```

### 四、akamai 这一行正好演示 `Gap` 与 `State` 是**两个问题**

| 列 | akamai 的值 | 含义 |
|---|---|---|
| **`Gap`** | **`None`** | marker（`AkamaiGHost`）是**镜像的** |
| **`State`** | **`DetectedOnly`** | **复刻件没有 akamai solver** |

**→ 所以 `DetectedOnly` 说的是**复刻件**，不是**镜像**。
→ 而那回答了 R1023 那个问题：**`DetectedOnly` 不该改** —— 它本来就没在说镜像。
→ **它说的东西需要被**说清**（Note 里现在写了），而不是被改掉。**

### 五、六 → 七行，四条守卫跟着动

| 守卫 | 从 | 到 |
|---|---|---|
| `ThreeOfSixAreWired` | 6 行 | **`ThreeOfSevenAreWired`（7 行）** |
| `TheGapsAreClassified` | `Gaps` = 3 个 | **4 个（按**行序**）** |
| 同上 | — | **加 `akamai.Gap == None` 且 `State == DetectedOnly` 的并列断言** |
| `OnlyWiredWallsAreDispatched` | `Gaps.Count == 3` | **`== 4`** |

**→ 而 `Gaps` 是**行序**不是字母序 —— 我第一版按字母序写，红了。那是 R1009 的老账，又犯一次。**

### 六、数字

| 度量 | R1023 | R1024 |
|---|---|---|
| 套件 | 2233 / 0 | **2233 / 0 / 0** |
| 产物陈旧度 | 4 / 3,795 | **4 / 3,816** |
| 函数数 | 174,336 | **174,336** |
| **`VendorWiring.Rows`** | 6 | **7（+akamai）** |
| **原版解几个厂商** | 未测 | **6** |
| **imperva 的独立证据** | 2 | **3** |
| **`DetectedOnly` 该改吗** | 待定 | **不该 —— 它说的是复刻件** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "Solving Incapsula"  -> {"n":0}
python analysis/ida.py str "Solving Akamai"     -> {"n":3}
python analysis/ida.py str "Solving Cloudflare" -> {"n":14}
python analysis/ida.py str "Solving PerimeterX" -> {"n":1}
python analysis/ida.py str "Solving Queue"      -> {"n":1}
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~Vendor|~Imperva|~PerimeterX" -m:1 -> 59 通过
python tools/metrics_report.py -> 完整套件 exit 0  2233 / 0 / 0
```

### 八、仍然 Unknown

- **akamai 的 `(SBSD)` / `(SDS)` 各是什么**：**未取证**。
- **queue-it softblock 的 solver**：**与 `NotAChallenge` 矛盾，待判**。

### 九、教训

**「把 `Solv` 一次问完」这个动作本身撞上了工具的 40 条上限 —— 而我第一眼读的是 40 条，不是「40 是上限」。**

**→ 那与 R1023 的 `[:4]` 是同一件事，只是这次截断不在我的脚本里，在工具里。
→ 而**同样的教训隔一轮就复发**，说明「不截断」不能只靠记住 —— 要靠**看到 n 等于上限就警觉**。
→ 而这一轮真正把它解决的不是警觉，是**把问题问小**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1024", BLOCKER)
    ensure(RSTATUS, "R1024", BLOCKER)
    ensure(RVERDICT, "第 1024 轮", VERDICT)
    ensure(BACKLOG, "R1024", BACKLOG_ADD)

    note = (
        "\n## R1024 补充 — **原版解六个厂商；`Rows` 补 akamai（第 7 行）；`DetectedOnly` 说的是复刻件**（套件 2233）\n\n"
        "**又一次读了被截断的答案**：`ida.py str \"Solv\"` → **n=40**，而 40 是**返回上限**。\n"
        "→ 正解是**把问题问小**（窄 probe），不是读前 40 条。与 R1023 的 `[:4]` 同形，只是截断在工具里。\n\n"
        "**完整答案**：`Solving Cloudflare` **14**（8 条阶段 + `no clearance`/`too many rounds`）·\n"
        "`Solving Kasada` 2 · `Solving DataDome` 1 · **`Solving Incapsula` 0** · `Solving Akamai` **3**\n"
        "（`(` · `(SBSD)` · `(SDS)`）· `Solving Queue` 1（`Error Solving Queue-it (Softblock)`）· `Solving PerimeterX` 1。\n"
        "→ **原版解六个**：cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx。\n"
        "→ **`Solving Incapsula` = 0 ⇒ imperva 第三个独立证据。**\n\n"
        "**补 akamai（第 7 行）**：`Gap = None`（`AkamaiGHost` 镜像有）而 `State = DetectedOnly`（复刻件无 solver）。\n"
        "→ **那回答了 R1023 的问题：`DetectedOnly` 不该改，它说的是**复刻件**不是镜像** —— 需要被**说清**而非改掉。\n\n"
        "**四条守卫跟着动**：`ThreeOfSevenAreWired` · `Gaps` 3 → 4（**行序**，我第一版按字母序写红了，R1009 老账）·\n"
        "加 `akamai.Gap == None` 与 `State == DetectedOnly` 并列断言 · `OnlyWiredWallsAreDispatched` 3 → 4。\n\n"
        "数字：套件 2233/0/0 · 陈旧度 4 / 3,816 · 函数数 174,336 · Rows 6 → **7** · 原版解 **6** 个 · imperva 证据 2 → **3**。\n\n"
        "纪律：**看到 `n` 等于上限就警觉；更好的解法是把问题问小。**\n\n"
        "下一轮：queue-it softblock（`Error Solving Queue-it (Softblock)` 与 `NotAChallenge` 矛盾）—— 那是下一个语义冲突。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1024" not in h:
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
             for p, k in ((RBLOCK, "R1024"), (RSTATUS, "R1024"), (RVERDICT, "第 1024 轮"), (BACKLOG, "R1024")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1024: the original solves six vendors, and the audit was missing the best-documented one\n\n"
         "R1023 left one question open -- what DetectedOnly should become, given that the image carries \"Solving\n"
         " PerimeterX\". Answering it meant finding out which vendors the image actually solves, so I asked for every\n"
         " Solv spelling at once and hit the tool's forty-match cap, then read all forty as if they were the answer.\n"
         " Solving PerimeterX was not among them. That is the same mistake as R1023 one round later, except the cut was\n"
         " in the tool rather than in my script.\n\n"
         "The fix is not to read more carefully, it is to ask a smaller question. Narrow probes fit under the cap and give\n"
         " complete answers: Cloudflare fourteen with eight stage strings, Kasada two, DataDome one, Akamai three,\n"
         " Queue-it one, PerimeterX one, and Incapsula zero. So the original solves six vendors, and Imperva now has a\n"
         " third independent witness -- no cast, no inventory entry, no solving narration.\n\n"
         "Akamai is the surprise. It has three solving strings and endpoints.md lists twenty-five literals for it, and the\n"
         " audit did not have a row for it at all, while AntiBotVendors has listed it for many rounds. It joins as the\n"
         " seventh row, and it is the clearest demonstration of what the two new columns are for: its Gap is None, because\n"
         " AkamaiGHost is the image's, and its State is DetectedOnly, because this workspace has no Akamai solver. The two\n"
         " facts are not in tension, they are about different subjects.\n\n"
         "Which answers R1023. DetectedOnly does not need to change; it was never claiming anything about the artifact. It\n"
         " claims this replica recognises the vendor and does nothing about it, and that is true. What it needed was to\n"
         " say so where a reader would see it.\n\n"
         "Four guards moved with the row, and one of them caught me writing the gap list in alphabetical order when it is\n"
         " in row order -- the same mistake R1009 recorded.\n\n"
         "Figures: suite 2233 unchanged, freshness four files and 3,816 lines, count 174,336, rows six to seven, six\n"
         " vendors known to be solved, and Imperva's witnesses up from two to three.\n\n"
         "Unknown: what Akamai's SBSD and SDS modes are, and how the Queue-it softblock solver squares with the row that\n"
         " calls a queue a queue rather than a challenge.\n\n"
         "The lesson is that a cap looks exactly like a complete answer, that my own script truncated a listing one round\n"
         " ago and the tool truncated a broader one this round, and that the way out is to narrow the question rather than\n"
         " to resolve to read more carefully.\n\n"
         "Two source files and two test files changed; suite green at 2233."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()