"""Record R1018: the image's captcha-delivery literals are DataDome's, not PerimeterX's."""

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
### 镜像那四条 `captcha-delivery` 是 **DataDome** 的，不是 PerimeterX 的（R1018）

**上一轮收尾说下一轮看优先级 ②。看的第一步是验 R998 那条 claim —— 而 claim 成立，**归属错了**。**

### ① 先说验对了的

**R998 声称「`geo.captcha-delivery.com` 与 `/interstitial/` 路径，共四条字面量」，而 `px-captcha` 一次不出现。
逐条查证：**

```
captcha-delivery  n=4
  0x1470689dc  https://geo.captcha-delivery.com
  0x147068a34  https://geo.captcha-delivery.com/
  0x147068a8c  https://geo.captcha-delivery.com/interstitial/
  0x147068b04  https://geo.captcha-delivery.com/interstitial/?initialCid=
px-captcha        n=0
```

**→ 「four literals in all」**精确正确**。`px-captcha` 确证 0。R998 的这两条都对。**

### ② 而它把**归属**搞错了

**同一个查询里还有一条它没引用的：**

```
0x1435260cb  (DdInterstitialClient
```

**→ `Dd` = **DataDome**。而 `geo.captcha-delivery.com` 就是 **DataDome 的 CAPTCHA host**。
→ 所以那四条字面量是 **datadome 的**，而 R998 把它们算给了 **perimeterx**，并让 `DetectAsync` **优先**测它们。**

### ③ 而分支顺序**掩盖**了这个错

**`DetectAsync` 的顺序（`StoreFlow.cs:380-392`）：**

```
381  cf-chl              → cloudflare
382  kpsdk               → kasada
383  _Incapsula_Resource → imperva
384  datadome            → datadome      ← 排在前面
388  captcha-delivery    → perimeterx   ← 而这是 datadome 的 host
389  px-captcha          → perimeterx
390  queue-it            → queue-it
```

**→ 一个自带 `datadome` 字样的页面在 **384** 就被认出 ⇒ 388 的错**看不出来**。
→ 而**唯一会被它改变的那类页面**是：一个 DataDome 的 **interstitial**，
  **只报出 host 而不报出厂商名**。→ **而那正是 CAPTCHA 墙serve 的那种页面。****

> **→ 那个页面原来被判成 `perimeterx`，然后交给**错误厂商的 solver**。
> → 而「大多数情况对」正是这类错误能活下来的方式。**

### ④ 改了什么

```csharp
body.Contains("captcha-delivery", StringComparison.OrdinalIgnoreCase) ? "datadome" :
body.Contains("px-captcha", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
```

**→ `captcha-delivery` 归 `datadome`；`perimeterx` 只剩 `px-captcha`（镜像无，但仍是它唯一能主张的页面级标记，
而 `MarkerFrom = Inferred` 如实写着）。**

**→ 并更新 `VendorWiring` 那行注释：R1018 说明 R998 的归属已改。**

**→ 加 3 条守卫（`CaptchaDeliveryAttributionTests`）：**
1. `captcha-delivery` 必须路由到 `datadome`，且 perimeterx 分支**不再**主张它
2. `px-captcha` 仍是 perimeterx 的标记，且审计行写明归属已改
3. 更正所依据的证据必须在源码里被引（`DdInterstitialClient` 与 `0x1435260cb`）

### ⑤ 数字

| 度量 | R1017 | **R1018** |
|---|---|---|
| 套件 | 2219 / 0 | **2222 / 0 / 0（+3 归属守卫）** |
| 产物陈旧度 | 2 / 3,365 | **3 / 3,522** |
| 函数数 | 174,336 | **174,336** |
| **`captcha-delivery` 的归属** | **perimeterx（错）** | **datadome（对）** |
| **会被误判的页面类型** | DataDome interstitial（只报 host） | **已消除** |
| **perimeterx 的 marker** | `px-captcha`（Inferred） | 不变，且注释写明 |

### 教训

> **一条 claim 可以逐字成立而结论是错的。R998 的四条字面量、零命中的 `px-captcha`、
> 「镜像里有一个可用的标记」—— 每句都对，而它把那个标记算给了错的厂商。**
> **→ 而派出这个错误只需要一个它没做的动作：问「这个 host 是**谁**的」。**
> **→ 而 `DdInterstitialClient` 就紧挨在那四个地址旁边的那个查询里 —— 它出现在我的输出里，
> 而我第一遍读的时候只看了那四条 URL。**
"""

if "镜像那四条 `captcha-delivery` 是" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1018 轮：镜像那四条 `captcha-delivery` 是 DataDome 的，不是 PerimeterX 的

### ① 先说验对了的

```
captcha-delivery  n=4
  0x1470689dc  https://geo.captcha-delivery.com
  0x147068a34  https://geo.captcha-delivery.com/
  0x147068a8c  https://geo.captcha-delivery.com/interstitial/
  0x147068b04  https://geo.captcha-delivery.com/interstitial/?initialCid=
px-captcha        n=0
```

**→ R998 的「four literals in all」**精确正确**，`px-captcha` 确证 0。两条都对。**

### ② 而它把**归属**搞错了

```
0x1435260cb  (DdInterstitialClient
```

**→ `Dd` = **DataDome**。`geo.captcha-delivery.com` 就是 DataDome 的 CAPTCHA host。
→ 那四条是 **datadome 的**，而 R998 算给了 **perimeterx**，还让 `DetectAsync` **优先**测它们。**

### ③ 而分支顺序**掩盖**了这个错

```
384  datadome          → datadome      ← 排在前面
388  captcha-delivery  → perimeterx   ← 而这是 datadome 的 host
```

**→ 自带 `datadome` 字样的页面在 384 就被认出 ⇒ 388 的错看不出来。
→ 唯一会被改变的那类页面是：DataDome 的 **interstitial，只报 host 不报厂商名**。
→ **而那正是 CAPTCHA 墙 serve 的那种页面。****

> **→ 那个页面原来被判成 perimeterx，然后交给**错误厂商的 solver**。
> → 「大多数情况对」正是这类错误能活下来的方式。**

### ④ 改了什么

```csharp
body.Contains("captcha-delivery", ...) ? "datadome" :
body.Contains("px-captcha", ...) ? "perimeterx" :
```

**并更新 `VendorWiring` 那行注释，加 3 条 `CaptchaDeliveryAttributionTests` 守卫。**

### ⑤ 数字

| 度量 | R1017 | **R1018** |
|---|---|---|
| 套件 | 2219 / 0 | **2222 / 0 / 0（+3）** |
| 产物陈旧度 | 2 / 3,365 | **3 / 3,522** |
| 函数数 | 174,336 | **174,336** |
| **`captcha-delivery` 的归属** | **perimeterx（错）** | **datadome（对）** |
| **会被误判的页面类型** | DataDome interstitial | **已消除** |

### 教训

> **一条 claim 可以逐字成立而结论是错的。R998 的四条字面量、零命中的 `px-captcha`、
> 「镜像里有一个可用的标记」—— 每句都对，而它把那个标记算给了错的厂商。**
> **→ 而派出这个错误只需要一个它没做的动作：问「这个 host 是**谁**的」。**
> **→ 而 `DdInterstitialClient` 就紧挨在那四个地址旁边的那个查询里 —— 它出现在我的输出里，
> 而我第一遍读的时候只看了那四条 URL。**
"""

BACKLOG_ADD = """

## 优先级 ② — **`captcha-delivery` 归 datadome 而非 perimeterx（R998 的归属错）**（R1018）

### R998 验对了两条

```
captcha-delivery n=4（geo.captcha-delivery.com · / · /interstitial/ · ?initialCid=）
px-captcha       n=0
```

**→ 「four literals in all」精确正确。**

### 而它把归属搞错

```
0x1435260cb  (DdInterstitialClient     ← Dd = DataDome
```

**→ `geo.captcha-delivery.com` 是 **DataDome** 的 CAPTCHA host ⇒ 那四条是 datadome 的。**

### 分支顺序掩盖了它

```
384  datadome → datadome         ← 先
388  captcha-delivery → perimeterx  ← 后，而它是 datadome 的
```

**→ 唯一被改变的是「DataDome interstitial 只报 host 不报厂商名」—— **那正是 CAPTCHA 墙的页面**。
→ 原来判成 perimeterx 并交给错厂商的 solver。**

### 修

**`captcha-delivery` → `datadome`；perimeterx 只剩 `px-captcha`（Inferred 不变）。
3 条守卫 `CaptchaDeliveryAttributionTests`。**

### 数字

**套件 2222（+3）· 陈旧度 3 / 3,522 · 函数数 174,336 · 归属 perimeterx → datadome · 误判页面类型已消除**

| 仍 Unknown | |
|---|---|
| perimeterx 的页面级 marker | 镜像无（只有 cookie 名） |

**纪律**：一条 claim 可以逐字成立而结论是错的 —— 派出错误只需要问「这个 host 是谁的」。
"""

BLOCKER = """

---

## 442. **镜像那四条 `captcha-delivery` 是 DataDome 的，不是 PerimeterX 的**

> R1018。**改 2 个源文件 + 加 1 个测试文件。** 套件 **2222 通过 / 0 失败 / 0 跳过**。

### 一、先说验对了的

**R998 声称「`geo.captcha-delivery.com` 与 `/interstitial/` 路径，共四条字面量」，而 `px-captcha` 一次不出现。
逐条查证：**

```
captcha-delivery  n=4
  0x1470689dc  https://geo.captcha-delivery.com
  0x147068a34  https://geo.captcha-delivery.com/
  0x147068a8c  https://geo.captcha-delivery.com/interstitial/
  0x147068b04  https://geo.captcha-delivery.com/interstitial/?initialCid=
px-captcha        n=0
```

**→ 「four literals in all」**精确正确**。`px-captcha` 确证 0。R998 的这两条都对。**

### 二、而它把**归属**搞错了

**同一个查询里还有一条它没引用的：**

```
0x1435260cb  (DdInterstitialClient
```

**→ `Dd` = **DataDome**。而 `geo.captcha-delivery.com` 就是 **DataDome 的 CAPTCHA host**。
→ 所以那四条字面量是 **datadome 的**，而 R998 把它们算给了 **perimeterx**，
  并让 `DetectAsync` **优先**测它们。**

### 三、而分支顺序**掩盖**了这个错

```
381  cf-chl              → cloudflare
382  kpsdk               → kasada
383  _Incapsula_Resource → imperva
384  datadome            → datadome      ← 排在前面
388  captcha-delivery    → perimeterx   ← 而这是 datadome 的 host
389  px-captcha          → perimeterx
390  queue-it            → queue-it
```

**→ 一个自带 `datadome` 字样的页面在 **384** 就被认出 ⇒ 388 的错**看不出来**。
→ 而**唯一会被它改变的那类页面**是：一个 DataDome 的 **interstitial**，
  **只报出 host 而不报出厂商名**。→ **而那正是 CAPTCHA 墙 serve 的那种页面。**

**→ 那个页面原来被判成 `perimeterx`，然后交给**错误厂商的 solver**。
→ 而「大多数情况对」正是这类错误能活下来的方式。**

### 四、改了什么

```csharp
body.Contains("captcha-delivery", StringComparison.OrdinalIgnoreCase) ? "datadome" :
body.Contains("px-captcha", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
```

**→ `captcha-delivery` 归 `datadome`；`perimeterx` 只剩 `px-captcha`（镜像无，
  但仍是它唯一能主张的页面级标记，而 `MarkerFrom = Inferred` 如实写着）。**

**→ 并更新 `VendorWiring` 那行注释：R1018 说明 R998 的归属已改。**

**→ 加 3 条守卫（`CaptchaDeliveryAttributionTests`）：**

1. `captcha-delivery` 必须路由到 `datadome`，且 perimeterx 分支**不再**主张它
2. `px-captcha` 仍是 perimeterx 的标记，且审计行写明归属已改
3. 更正所依据的证据必须在源码里被引（`DdInterstitialClient` 与 `0x1435260cb`）

### 五、数字

| 度量 | R1017 | R1018 |
|---|---|---|
| 套件 | 2219 / 0 | **2222 / 0 / 0（+3 归属守卫）** |
| 产物陈旧度 | 2 / 3,365 | **3 / 3,522** |
| 函数数 | 174,336 | **174,336** |
| **`captcha-delivery` 的归属** | **perimeterx（错）** | **datadome（对）** |
| **会被误判的页面类型** | DataDome interstitial（只报 host） | **已消除** |
| **perimeterx 的 marker** | `px-captcha`（Inferred） | 不变，且注释写明 |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "captcha-delivery"  -> {"n":4}（4 条，含 ?initialCid=）
python analysis/ida.py str "px-captcha"        -> {"n":0}
python analysis/ida.py str "interstitial"      -> {"n":4}（含 0x1435260cb "(DdInterstitialClient"）
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug   -> 已成功生成
dotnet test --filter "FullyQualifiedName~CaptchaDeliveryAttribution" -m:1 -> 3 通过
dotnet test --filter "FullyQualifiedName~Wall|FullyQualifiedName~VendorWiring" -m:1 -> 31 通过
python tools/metrics_report.py -> 完整套件 exit 0  2222 / 0 / 0
```

### 七、仍然 Unknown

- **perimeterx 的页面级 marker**：**镜像无** —— 只有 cookie 名（`_px3` · `_pxvid` · `PerimeterX-Token`）。

### 八、教训

**一条 claim 可以逐字成立而结论是错的。R998 的四条字面量、零命中的 `px-captcha`、
「镜像里有一个可用的标记」—— 每句都对，而它把那个标记算给了错的厂商。**

**→ 而派出这个错误只需要一个它没做的动作：问「这个 host 是**谁**的」。
→ 而 `DdInterstitialClient` 就紧挨在那四个地址旁边的那个查询里 —— 它出现在我的输出里，
  而我第一遍读的时候只看了那四条 URL。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1018", BLOCKER)
    ensure(RSTATUS, "R1018", BLOCKER)
    ensure(RVERDICT, "第 1018 轮", VERDICT)
    ensure(BACKLOG, "R1018", BACKLOG_ADD)

    note = (
        "\n## R1018 补充 — **镜像那四条 `captcha-delivery` 是 DataDome 的，不是 PerimeterX 的**（套件 2222）\n\n"
        "**R998 验对了两条**：`captcha-delivery` **4** 命中（`geo.captcha-delivery.com` · `/` · `/interstitial/` ·\n"
        "`?initialCid=`）· `px-captcha` **0**。「four literals in all」**精确正确**。\n\n"
        "**而它把归属搞错**：同一个查询里还有 `0x1435260cb  (DdInterstitialClient` —— **`Dd` = DataDome**，\n"
        "而 `geo.captcha-delivery.com` 就是 **DataDome 的 CAPTCHA host** ⇒ 那四条是 datadome 的，\n"
        "而 R998 算给了 perimeterx 并让 `DetectAsync` **优先**测。\n\n"
        "**分支顺序掩盖了它**：`384 datadome → datadome` 排在 `388 captcha-delivery → perimeterx` 前面 ⇒\n"
        "自带 `datadome` 字样的页面在 384 就被认出。**唯一被改变的是「DataDome interstitial 只报 host 不报厂商名」——\n"
        "那正是 CAPTCHA 墙的页面**，原来判成 perimeterx 并交给**错厂商的 solver**。\n\n"
        "**修**：`captcha-delivery` → `datadome`；perimeterx 只剩 `px-captcha`（Inferred 不变）。\n"
        "**加 3 条守卫** `CaptchaDeliveryAttributionTests`（归属 / 保留自己的 marker / 证据必须在源码里被引）。\n\n"
        "数字：套件 2222（+3）· 陈旧度 3 / 3,522 · 函数数 174,336 · 归属 perimeterx → **datadome** · 误判页面类型已消除。\n\n"
        "纪律：**一条 claim 可以逐字成立而结论是错的 —— 派出错误只需要问「这个 host 是谁的」。**\n"
        "而 `DdInterstitialClient` 就在我自己的输出里，我第一遍只看了那四条 URL。\n\n"
        "下一轮：perimeterx 的页面级 marker（镜像只有 cookie 名）；或继续 ② 的 imperva（7 种拼写全 0，已确证不在）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1018" not in h:
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
             for p, k in ((RBLOCK, "R1018"), (RSTATUS, "R1018"), (RVERDICT, "第 1018 轮"), (BACKLOG, "R1018")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1018: the image's captcha-delivery literals are DataDome's, not PerimeterX's\n\n"
         "The round after R1017 went back to priority two, and the first thing worth doing there was verifying R998's\n"
         " claim rather than adding to it. The claim holds exactly: four captcha-delivery literals, and px-captcha absent\n"
         " from the image in every occurrence.\n\n"
         "The attribution does not hold. The image carries DdInterstitialClient at 0x1435260cb, and geo.captcha-delivery.com\n"
         " is DataDome's challenge host -- the Dd prefix says whose it is. R998 counted those four literals to PerimeterX\n"
         " and put them ahead of everything else in the detection chain.\n\n"
         "The branch order concealed it. A page that names \"datadome\" is matched one line earlier, so a mistake on the\n"
         " next line changes almost nothing. Almost: the one page it did change is a DataDome interstitial that names its\n"
         " host and not its vendor, which is exactly the page a CAPTCHA wall serves. That page was labelled PerimeterX and\n"
         " routed to the wrong vendor's solver, and being right most of the time is how that kind of error survives.\n\n"
         "So captcha-delivery now routes to datadome, PerimeterX keeps px-captcha as the only marker it can claim, and the\n"
         " audit row says the attribution moved. Three guards pin it: the routing, the fact that the perimeterx branch no\n"
         " longer claims the literal, and the fact that the correction's evidence -- the class name and its address -- is\n"
         " quoted in the source so the next reader can check it.\n\n"
         "Figures: suite 2219 to 2222, freshness three files and 3,522 lines, count 174,336, the attribution moved from\n"
         " perimeterx to datadome, and the class of page that could be misclassified is gone.\n\n"
         "Unknown: a page-level marker for PerimeterX, since the image only names its cookies.\n\n"
         "The lesson is that a claim can be true sentence by sentence and still reach a false conclusion, and that the only\n"
         " step needed to catch it was asking whose host that was. DdInterstitialClient had been sitting in my own query\n"
         " output; on the first read I looked at the four URLs and nothing else.\n\n"
         "Two source files and one test file changed; suite green at 2222."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()