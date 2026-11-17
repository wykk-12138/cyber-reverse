"""Record R1019: cf-chl is in the image zero times, and it was the first test in the chain."""

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
### 六个 vendor 的 marker 一次问完 —— 而**第一个**就是自造的（R1019）

**R1018 的教训是「问这个 host 是谁的」。这一轮把那个动作推广：把六个 vendor 的 marker 与拼写一次全问，
像 R1009 问会话键那样。**

### ① 台账（19 个拼写，全部问 IDB）

| vendor | 拼写 | n |
|---|---|---|
| **cloudflare** | **`cf-chl`** | **0** |
| | `cf_clearance` | 2 |
| | `cloudflare` | 40 |
| | `__cf_bm` | 1 |
| | `challenge-platform` | **2** |
| kasada | `kpsdk` | 17 |
| | `x-kpsdk-ct` · `-cd` · `-st` | 1 · 1 · 1 |
| | `kasada` | 40 |
| **imperva** | `_Incapsula_Resource` · `incap_ses` · `visid_incap` · `incapsula` · `imperva` · `nlbi_` | **0 · 0 · 0 · 0 · 0 · 0** |
| datadome | `datadome` | 15 |
| | `geo.captcha-delivery.com` | 4 |
| **perimeterx** | **`px-captcha`** | **0** |
| | `_px3` · `_pxvid` · `PerimeterX-Token` · `PerimeterXHandler` | 1 · 2 · 1 · 1 |
| queue-it | `queue-it` · `queue-it-set-cookie` · `queueit` | 13 · 1 · 24 |

### ② 而 **`cf-chl` 是 0**，而它是 `DetectAsync` 的**第一个**分支

```csharp
381  body.Contains("cf-chl", ...) ? "cloudflare" :      ← 0 命中
```

**→ 所以检测链条的**第一个**判断用的就是一个自造串。
→ 而镜像里有 `challenge-platform` 两处（`/cdn-cgi/challenge-platform/` 路径，**页面级**）、
  `cf_clearance` 两处、`__cf_bm` 一处 —— 而**后两个是 cookie 名**，而 `DetectAsync` 读的是**响应体**。**

**→ 所以正确的页面级 marker 是 `challenge-platform`，而 `cf_clearance` 该留在 cookie 列（它本来就在那里）。**

### ③ 改了什么

```csharp
body.Contains("challenge-platform", ...) ? "cloudflare" :
body.Contains("cf-chl", ...) ? "cloudflare" :          // 降为后备
```

**→ `VendorWiring` 的 cloudflare 行：marker 改 `challenge-platform`，`MarkerFrom` 由 `Inferred` 改 **`ImageLiteral`**。**

### ④ 而守卫**抓住了**我

**`TheMarkerColumnSaysWhereEachMarkerCameFrom` 钉着 `Inferred == {cloudflare, imperva, perimeterx}`，
而我改完就红了。而那正是那条守卫的设计 —— 它的注释写着「Changing it means re-run
`python analysis/ida.py str <marker>` and finding something there」。**

**→ 我做了那件事（`challenge-platform` n=2），所以集合改成 `{imperva, perimeterx}`，理由写进注释。**

**→ 现在 `Inferred` = 2（imperva · perimeterx），`ImageLiteral` = 4（cloudflare · kasada · datadome · queue-it）。**

### ⑤ 而两个 `Inferred` 的性质不同

| vendor | marker | 镜像 | 性质 |
|---|---|---|---|
| **imperva** | `_Incapsula_Resource` | **0**（6 拼写全 0） | **整站风控不在镜像里** |
| **perimeterx** | `px-captcha` | **0** | **只有 cookie 名，没有页面级 marker** |

**→ 两者都标 `Inferred`，而**原因不同**：imperva 是「这个厂商不在」，perimeterx 是「这个厂商在，而它没有
一个能在响应体里找的字面量」。**
**→ 那个区别现在只在注释里，而在台账里看不出来 —— 下一轮该把它变成字段或第二张表。**

### ⑥ 数字

| 度量 | R1018 | **R1019** |
|---|---|---|
| 套件 | 2222 / 0 | **2222 / 0 / 0** |
| 产物陈旧度 | 3 / 3,522 | **3 / 3,531** |
| 函数数 | 174,336 | **174,336** |
| **已验证的 marker 拼写** | 6 | **19** |
| **`Inferred` 数** | 3 | **2（cloudflare 升为 ImageLiteral）** |
| **检测链第一个串** | `cf-chl`（0 命中） | **`challenge-platform`（2）** |

### 教训

> **R1018 花了三轮才发现一个归属错，而它的形状是「自造串」。这一轮把「自造串」当问题一次问完，
> 第一个分支就中。**
> **→ 而那个错从 R140 起就在那里 —— 因为 `cf-chl` 读起来太像真东西（所有 Cloudflare 文档都那么写），
> 而它确实**曾经**是。**
> **→ 「看起来对」是这类错误的唯一保护色，而唯一的解法是把每个串都问一遍镜像。**
"""

if "六个 vendor 的 marker 一次问完" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1019 轮：六个 vendor 的 marker 一次问完 —— 而第一个就是自造的

### ① 台账（19 个拼写，全部问 IDB）

| vendor | 拼写 | n |
|---|---|---|
| **cloudflare** | **`cf-chl`** | **0** |
| | `cf_clearance` · `cloudflare` · `__cf_bm` · `challenge-platform` | 2 · 40 · 1 · **2** |
| kasada | `kpsdk` · `x-kpsdk-ct/cd/st` · `kasada` | 17 · 1/1/1 · 40 |
| **imperva** | 6 拼写 | **全 0** |
| datadome | `datadome` · `geo.captcha-delivery.com` | 15 · 4 |
| **perimeterx** | **`px-captcha`** | **0** |
| | `_px3` · `_pxvid` · `PerimeterX-Token` · `PerimeterXHandler` | 1 · 2 · 1 · 1 |
| queue-it | `queue-it` · `queue-it-set-cookie` · `queueit` | 13 · 1 · 24 |

### ② 而 **`cf-chl` 是 0**，而它是 `DetectAsync` 的**第一个**分支

**→ 检测链条的**第一个**判断用的就是自造串。
→ 镜像里有 `challenge-platform` 两处（`/cdn-cgi/challenge-platform/`，**页面级**）；
  `cf_clearance` 与 `__cf_bm` 是 **cookie 名**，而 `DetectAsync` 读的是**响应体**。
→ 所以正确的页面级 marker 是 `challenge-platform`。**

### ③ 改了什么

```csharp
body.Contains("challenge-platform", ...) ? "cloudflare" :
body.Contains("cf-chl", ...) ? "cloudflare" :          // 降为后备
```

**→ `VendorWiring` cloudflare 行：marker 改 `challenge-platform`，`MarkerFrom` `Inferred` → **`ImageLiteral`**。**

### ④ 而守卫**抓住了**我

**`TheMarkerColumnSaysWhereEachMarkerCameFrom` 钉着 `Inferred == {cloudflare, imperva, perimeterx}`，
改完就红了 —— 那正是它的设计（注释写着「Changing it means re-run the probe and find something there」）。
→ 我做了那件事（`challenge-platform` n=2），集合改成 `{imperva, perimeterx}`，理由写进注释。**

**→ 现在 `Inferred` = 2，`ImageLiteral` = 4。**

### ⑤ 而两个 `Inferred` 的性质不同

| vendor | marker | 镜像 | 性质 |
|---|---|---|---|
| **imperva** | `_Incapsula_Resource` | **0**（6 拼写全 0） | **整站风控不在镜像里** |
| **perimeterx** | `px-captcha` | **0** | **只有 cookie 名，无页面级 marker** |

**→ 那个区别现在只在注释里，台账里看不出来 —— 下一轮该把它变成字段或第二张表。**

### ⑥ 数字

| 度量 | R1018 | **R1019** |
|---|---|---|
| 套件 | 2222 / 0 | **2222 / 0 / 0** |
| 产物陈旧度 | 3 / 3,522 | **3 / 3,531** |
| 函数数 | 174,336 | **174,336** |
| **已验证的 marker 拼写** | 6 | **19** |
| **`Inferred` 数** | 3 | **2** |
| **检测链第一个串** | `cf-chl`（0） | **`challenge-platform`（2）** |

### 教训

> **R1018 花三轮才发现一个归属错，形状是「自造串」。这一轮把「自造串」当问题一次问完，第一个分支就中。
> → 那个错从 R140 起就在那里 —— 因为 `cf-chl` 读起来太像真东西（所有 Cloudflare 文档都那么写），
> 而它确实**曾经**是。**
> **→ 「看起来对」是这类错误的唯一保护色，而唯一的解法是把每个串都问一遍镜像。**
"""

BACKLOG_ADD = """

## 优先级 ② — **六个 vendor 的 19 个 marker 拼写全问完：`cf-chl` 0 命中而它是检测链第一个分支**（R1019）

### 台账

| vendor | 有据 | 无据 |
|---|---|---|
| cloudflare | `cf_clearance` 2 · `cloudflare` 40 · `__cf_bm` 1 · `challenge-platform` **2** | **`cf-chl` 0** |
| kasada | `kpsdk` 17 · `x-kpsdk-ct/cd/st` 各 1 · `kasada` 40 | — |
| imperva | **无** | 6 拼写全 0 |
| datadome | `datadome` 15 · `geo.captcha-delivery.com` 4 | `dd_cookie` · `datadome-sensor` 0 |
| perimeterx | `_px3` 1 · `_pxvid` 2 · `PerimeterX-Token` 1 · `PerimeterXHandler` 1 | `px-captcha` 0 · `px-ct` 0 |
| queue-it | `queue-it` 13 · `queue-it-set-cookie` 1 · `queueit` 24 | — |

### 修

**`DetectAsync` 第一分支 `cf-chl`（0）→ `challenge-platform`（2，页面级）；`cf-chl` 降为后备。
`VendorWiring` cloudflare 行 `MarkerFrom` `Inferred` → `ImageLiteral`。**
**→ `cf_clearance` / `__cf_bm` 是 cookie 名，不进响应体检测（`cf_clearance` 本就在 cookie 列）。**

### 守卫抓住了我

**`TheMarkerColumnSaysWhereEachMarkerCameFrom` 钉 `Inferred == {cloudflare, imperva, perimeterx}`，改完红了。**
**→ 按它的注释重跑 probe（`challenge-platform` n=2）后改为 `{imperva, perimeterx}`。**

### 两个 Inferred 性质不同

- **imperva**：6 拼写全 0 ⇒ **整站风控不在镜像里**
- **perimeterx**：`px-captcha` 0，而 cookie 名 4 条有 ⇒ **厂商在，但没有页面级 marker**

**→ 那个区别只在注释里 ⇒ 下一轮该变成字段或第二张表。**

### 数字

**套件 2222/0/0 · 陈旧度 3 / 3,531 · 函数数 174,336 · 已验证拼写 6 → 19 · Inferred 3 → 2 · 链首串 `cf-chl`(0) → `challenge-platform`(2)**

| 仍 Unknown | |
|---|---|
| perimeterx 的页面级 marker | 镜像无 |
| imperva 是否真被原版处理 | 无任何字面量 |

**纪律**：「看起来对」是自造串的唯一保护色 —— 解法是把每个串都问一遍镜像。
"""

BLOCKER = """

---

## 443. **六个 vendor 的 19 个 marker 拼写全问完：`cf-chl` 0 命中而它是检测链第一个分支**

> R1019。**改 2 个源文件 + 1 个测试文件。** 套件 **2222 通过 / 0 失败 / 0 跳过**。

### 一、台账（19 个拼写，全部问 IDB）

| vendor | 拼写 | n |
|---|---|---|
| **cloudflare** | **`cf-chl`** | **0** |
| | `cf_clearance` | 2 |
| | `cloudflare` | 40 |
| | `__cf_bm` | 1 |
| | `challenge-platform` | **2** |
| kasada | `kpsdk` | 17 |
| | `x-kpsdk-ct` · `-cd` · `-st` | 1 · 1 · 1 |
| | `kasada` | 40 |
| **imperva** | `_Incapsula_Resource` · `incap_ses` · `visid_incap` · `incapsula` · `imperva` · `nlbi_` | **0 · 0 · 0 · 0 · 0 · 0** |
| datadome | `datadome` | 15 |
| | `geo.captcha-delivery.com` | 4 |
| **perimeterx** | **`px-captcha`** | **0** |
| | `_px3` · `_pxvid` · `PerimeterX-Token` · `PerimeterXHandler` | 1 · 2 · 1 · 1 |
| queue-it | `queue-it` · `queue-it-set-cookie` · `queueit` | 13 · 1 · 24 |

### 二、而 **`cf-chl` 是 0**，而它是 `DetectAsync` 的**第一个**分支

```csharp
381  body.Contains("cf-chl", ...) ? "cloudflare" :      ← 0 命中
```

**→ 所以检测链条的**第一个**判断用的就是一个自造串。
→ 而镜像里有 `challenge-platform` 两处（`/cdn-cgi/challenge-platform/` 路径，**页面级**）、
  `cf_clearance` 两处、`__cf_bm` 一处 —— 而**后两个是 cookie 名**，而 `DetectAsync` 读的是**响应体**。**

**→ 所以正确的页面级 marker 是 `challenge-platform`，而 `cf_clearance` 该留在 cookie 列（它本来就在那里）。**

### 三、改了什么

```csharp
body.Contains("challenge-platform", StringComparison.OrdinalIgnoreCase) ? "cloudflare" :
body.Contains("cf-chl", StringComparison.OrdinalIgnoreCase) ? "cloudflare" :          // 降为后备
```

**→ `VendorWiring` 的 cloudflare 行：marker 改 `challenge-platform`，
  `MarkerFrom` 由 `Inferred` 改 **`ImageLiteral`**。**

### 四、而守卫**抓住了**我

**`TheMarkerColumnSaysWhereEachMarkerCameFrom` 钉着 `Inferred == {cloudflare, imperva, perimeterx}`，
而我改完就红了。而那正是那条守卫的设计 —— 它的注释写着
「Changing it means re-run `python analysis/ida.py str <marker>` and finding something there」。**

**→ 我做了那件事（`challenge-platform` n=2），所以集合改成 `{imperva, perimeterx}`，理由写进注释。
→ 现在 `Inferred` = 2（imperva · perimeterx），`ImageLiteral` = 4（cloudflare · kasada · datadome · queue-it）。**

### 五、而两个 `Inferred` 的性质不同

| vendor | marker | 镜像 | 性质 |
|---|---|---|---|
| **imperva** | `_Incapsula_Resource` | **0**（6 拼写全 0） | **整站风控不在镜像里** |
| **perimeterx** | `px-captcha` | **0** | **只有 cookie 名，没有页面级 marker** |

**→ 两者都标 `Inferred`，而**原因不同**：imperva 是「这个厂商不在」，perimeterx 是「这个厂商在，
  而它没有一个能在响应体里找的字面量」。
→ 那个区别现在只在注释里，而在台账里看不出来 —— 下一轮该把它变成字段或第二张表。**

### 六、数字

| 度量 | R1018 | R1019 |
|---|---|---|
| 套件 | 2222 / 0 | **2222 / 0 / 0** |
| 产物陈旧度 | 3 / 3,522 | **3 / 3,531** |
| 函数数 | 174,336 | **174,336** |
| **已验证的 marker 拼写** | 6 | **19** |
| **`Inferred` 数** | 3 | **2（cloudflare 升为 ImageLiteral）** |
| **检测链第一个串** | `cf-chl`（0 命中） | **`challenge-platform`（2）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "cf-chl"              -> {"n":0}
python analysis/ida.py str "challenge-platform"  -> {"n":2}
python analysis/ida.py str "cf_clearance"        -> {"n":2}
python analysis/ida.py str "__cf_bm"             -> {"n":1}
python analysis/ida.py str "px-captcha"          -> {"n":0}
python analysis/ida.py str "_Incapsula_Resource" -> {"n":0}
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~Wall|~VendorWiring|~CaptchaDelivery" -m:1 -> 34 通过
python tools/metrics_report.py -> 完整套件 exit 0  2222 / 0 / 0
```

### 八、仍然 Unknown

- **perimeterx 的页面级 marker**：**镜像无** —— 只有 cookie 名。
- **imperva 是否真被原版处理**：**无任何字面量** —— 6 种拼写全 0。

### 九、教训

**R1018 花了三轮才发现一个归属错，而它的形状是「自造串」。这一轮把「自造串」当问题一次问完，
第一个分支就中。**

**→ 而那个错从 R140 起就在那里 —— 因为 `cf-chl` 读起来太像真东西（所有 Cloudflare 文档都那么写），
  而它确实**曾经**是。**
**→ 「看起来对」是这类错误的唯一保护色，而唯一的解法是把每个串都问一遍镜像。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1019", BLOCKER)
    ensure(RSTATUS, "R1019", BLOCKER)
    ensure(RVERDICT, "第 1019 轮", VERDICT)
    ensure(BACKLOG, "R1019", BACKLOG_ADD)

    note = (
        "\n## R1019 补充 — **六个 vendor 的 19 个 marker 拼写全问完：`cf-chl` 0 命中而它是检测链第一个分支**（套件 2222）\n\n"
        "**台账要点**：\n"
        "- **cloudflare**：`cf-chl` **0** · `cf_clearance` 2 · `cloudflare` 40 · `__cf_bm` 1 · `challenge-platform` **2**\n"
        "- kasada：`kpsdk` 17 · `x-kpsdk-ct/cd/st` 各 1 · `kasada` 40\n"
        "- **imperva**：6 拼写**全 0**（确证不在镜像里）\n"
        "- datadome：`datadome` 15 · `geo.captcha-delivery.com` 4\n"
        "- **perimeterx**：`px-captcha` **0** · `_px3` 1 · `_pxvid` 2 · `PerimeterX-Token` 1 · `PerimeterXHandler` 1\n"
        "- queue-it：`queue-it` 13 · `queue-it-set-cookie` 1 · `queueit` 24\n\n"
        "**修**：`DetectAsync` 第一分支 `cf-chl`（0）→ **`challenge-platform`（2，页面级）**，`cf-chl` 降后备。\n"
        "→ `cf_clearance`/`__cf_bm` 是 **cookie 名**，不进响应体检测。\n"
        "→ `VendorWiring` cloudflare 行 `MarkerFrom` `Inferred` → **`ImageLiteral`**。\n\n"
        "**守卫抓住了我**：`TheMarkerColumnSaysWhereEachMarkerCameFrom` 钉 `Inferred == {cloudflare, imperva, perimeterx}`，\n"
        "改完红了。按它的注释重跑 probe 后改为 `{imperva, perimeterx}`。**现在 Inferred 2 / ImageLiteral 4。**\n\n"
        "**两个 Inferred 性质不同**：imperva = 厂商不在镜像里；perimeterx = 厂商在但没有页面级 marker。\n"
        "→ 那个区别只在注释里 ⇒ **下一轮该变成字段或第二张表。**\n\n"
        "数字：套件 2222/0/0 · 陈旧度 3 / 3,531 · 函数数 174,336 · 已验证拼写 6 → 19 · Inferred 3 → 2。\n\n"
        "纪律：**「看起来对」是自造串的唯一保护色 —— 解法是把每个串都问一遍镜像。**\n\n"
        "下一轮：把那两个 Inferred 的**不同原因**变成结构（字段或第二张表）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1019" not in h:
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
             for p, k in ((RBLOCK, "R1019"), (RSTATUS, "R1019"), (RVERDICT, "第 1019 轮"), (BACKLOG, "R1019")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1019: cf-chl is in the image zero times and it was the first test in the chain\n\n"
         "R1018 spent three rounds on one misattribution, and its shape was an invented string. This round treated\n"
         " invented strings as the question and asked all six vendors at once: nineteen spellings, each put to the IDB.\n\n"
         "The first branch of the detection chain fails. cf-chl is absent from the image, while challenge-platform is\n"
         " there twice as /cdn-cgi/challenge-platform/, cf_clearance twice and __cf_bm once. The last two are cookie\n"
         " names and DetectAsync reads a response body, so the page-level marker has to be the path. cloudflare's row\n"
         " now tests challenge-platform first, keeps cf-chl as a fallback for an edge that spells it that way, and its\n"
         " marker source moves from inferred to an image literal.\n\n"
         "The other five: kasada is solid at seventeen for kpsdk, queue-it at thirteen and twenty-four, datadome at\n"
         " fifteen plus the four captcha-delivery literals R1018 reassigned to it. Imperva is absent in all six\n"
         " spellings, which is a stronger statement than a missing marker. PerimeterX has four cookie-side literals and\n"
         " no page-level marker at all, which is a different state again.\n\n"
         "That last contrast is the useful part and it is not yet in the data. Two rows say inferred, and one means the\n"
         " vendor is not in the artifact while the other means it is present and simply has nothing to grep for. The\n"
         " distinction currently lives in prose inside a note, where a reader scanning the table cannot see it.\n\n"
         "The marker-source guard caught my edit and made me re-run the probe before widening its pinned set, which is\n"
         " exactly what its own comment asks for -- changing the set means finding the literal in the image first.\n\n"
         "Figures: suite 2222 unchanged, freshness three files and 3,531 lines, count 174,336, spellings verified up\n"
         " from six to nineteen, inferred rows down from three to two, and the chain's first test moved from a string\n"
         " the image does not contain to one it carries twice.\n\n"
         "Unknown: a page-level marker for PerimeterX, and whether the original handles Imperva at all.\n\n"
         "The lesson is that looking right is the only camouflage an invented string has -- cf-chl reads like real\n"
         " Cloudflare because it once was, and every document says so -- and the only way through it is to ask the\n"
         " image about every string rather than the ones that feel doubtful.\n\n"
         "Two source files and one test file changed; suite green at 2222."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()