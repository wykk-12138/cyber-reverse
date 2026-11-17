"""Record R998: R997 checked the wrong column, and the image carries a better PerimeterX marker."""

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
### R997 标错了**一列** —— 而镜像里有一个更好的 PerimeterX 标记（R998）

**R997 给六行加了 `MarkerSource`，四个标 `ImageLiteral`。这一轮去验 perimeterx 那一行，发现它标错了，
而错的方式正是那一列要防的事。**

### ① 我验的是 cookie 列，而 `ImageLiteral` 说的是 marker 列

| 探测 | 命中 |
|---|---|
| **`px-captcha`**（marker 列写的） | **0** |
| `_px3`（cookie 列写的） | 1 |

> **R997 我查了 `_px3` 就标了 `ImageLiteral`，而那一列说的是**marker**。
> `px-captcha` 在镜像里**一次都不出现**。
> → 所以 `Inferred` 的集合是 **3 个**：cloudflare · imperva · **perimeterx**。**

**而这正是 `MarkerSource` 存在的理由 —— 它也抓到了写它的人。**

### ② 而镜像里有一个**可用**的 PerimeterX 标记

```
0x1470689dc  https://geo.captcha-delivery.com
0x147068a34  https://geo.captcha-delivery.com/
0x147068a8c  https://geo.captcha-delivery.com/interstitial/
```

**`captcha-delivery` 命中 4 次。`geo.captcha-delivery.com` 是 PerimeterX 的挑战域。**

> **所以我们一直在测一个自造的串（`px-captcha`），而镜像里有一个 host 级的、更可靠的标记。
> → 这不是「缺证据」：证据一直在，只是没去找。**
> **→ 而 R997 说 perimeterx「`_px3` 在，所以 `ImageLiteral`」—— 那句把**cookie 的存在**当成了**标记的存在**。**

### ③ 所以改了三处

**① `VendorWiring.cs`：perimeterx 行 → `MarkerSource.Inferred`；note 写明**
「R998 corrects R997's own row … R997 labelled the row ImageLiteral by checking the cookie column instead of the
marker column. The image does carry a usable marker: geo.captcha-delivery.com and its /interstitial/ path」。

**② `StoreFlow.DetectAsync`：加 `captcha-delivery` 分支，排在 `px-captcha` 之前。**

```csharp
// R998: the image names geo.captcha-delivery.com and its /interstitial/ path, four literals, and never
// px-captcha. Testing the marker the artifact actually carries is worth more than testing the one this
// workspace wrote from general knowledge, so both are accepted and the image's comes first.
body.Contains("captcha-delivery", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
body.Contains("px-captcha", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
```

**③ `VendorWiringTests.cs`：`Inferred` 集合 → `{ "cloudflare", "imperva", "perimeterx" }`。**

> **② 那一步不是「加个串」，是**检测方式从常识换成镜像证据**：
> 之前只有一个标记能认出 PerimeterX，而那一个不在产物里；现在先测产物里那个。**

### ④ 而 `DetectAsync` 的检测能力实际变强了

| 之前 | 现在 |
|---|---|
| `px-captcha`（镜像 0 命中） | `captcha-delivery`（镜像 4 命中）**优先**，`px-captcha` 后备 |

> **所以这一轮不只是修一个标注 —— 它让 PerimeterX 的检测**真的可能命中**，
> 而之前那条分支只能靠一个镜像里不存在的串去命中。**

### ⑤ 数字

| 度量 | R997 | **R998** |
|---|---|---|
| 套件 | 2210 | **2210** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| 墙 Wired | 3 / 6 | **3 / 6（未变）** |
| **`Inferred` 标记** | 2 | **3（+perimeterx）** |
| **`DetectAsync` 里镜像有据的标记** | 4 / 6 | **5 / 6** |

### 教训

> **一列「出处」写下去的第一件事，是暴露**写它的人**没按那一列的定义去填。
> 我标 `ImageLiteral` 时看的是「这个厂商有镜像证据吗」，而那一列问的是「**这个格子里的串**在镜像里吗」。**
> **→ 两个问题的答案不同，而更宽的那个更容易让人满意。
> 一个刚加上的字段就能抓住作者 —— 这是它值得加的最好证据。**
"""

if "R997 标错了**一列**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 998 轮：R997 标错了一列 —— 而镜像里有一个更好的 PerimeterX 标记

### ① 我验的是 cookie 列，而 `ImageLiteral` 说的是 marker 列

| 探测 | 命中 |
|---|---|
| **`px-captcha`**（marker 列） | **0** |
| `_px3`（cookie 列） | 1 |

> **R997 我查了 `_px3` 就标了 `ImageLiteral`，而那一列说的是**marker**。
> `px-captcha` 在镜像里一次都不出现 → `Inferred` 集合是 **3 个**：cloudflare · imperva · **perimeterx**。
> **而 `MarkerSource` 存在的理由，正是抓到写它的人。**

### ② 而镜像里有一个**可用**的 PerimeterX 标记

```
https://geo.captcha-delivery.com
https://geo.captcha-delivery.com/
https://geo.captcha-delivery.com/interstitial/
```

**`captcha-delivery` 命中 4 次 —— `geo.captcha-delivery.com` 是 PerimeterX 的挑战域。**

> **我们一直在测一个自造的串，而镜像里有一个 host 级、更可靠的标记。
> 这不是「缺证据」：证据一直在，只是没去找。
> R997 说「`_px3` 在所以 `ImageLiteral`」—— 那句把**cookie 的存在**当成了**标记的存在**。**

### ③ 改了三处

1. `VendorWiring.cs` — perimeterx → `Inferred`；note 写明 `geo.captcha-delivery.com` 才是镜像里的标记
2. `StoreFlow.DetectAsync` — 加 `captcha-delivery` 分支，**排在 `px-captcha` 之前**
3. `VendorWiringTests.cs` — `Inferred` → `{cloudflare, imperva, perimeterx}`

### ④ 而 `DetectAsync` 的检测能力实际变强了

| 之前 | 现在 |
|---|---|
| `px-captcha`（镜像 0 命中） | `captcha-delivery`（镜像 4 命中）**优先**，`px-captcha` 后备 |

> **不只是修标注 —— 它让 PerimeterX 的检测**真的可能命中**。之前那条分支只能靠一个镜像里不存在的串。**

### ⑤ 数字

| 度量 | R997 | **R998** |
|---|---|---|
| 套件 | 2210 | **2210** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| 墙 Wired | 3 / 6 | **3 / 6（未变）** |
| **`Inferred` 标记** | 2 | **3（+perimeterx）** |
| **`DetectAsync` 里镜像有据的标记** | 4 / 6 | **5 / 6** |

### 教训

> **一列「出处」写下去的第一件事，是暴露**写它的人**没按那一列的定义去填。
> 我标 `ImageLiteral` 时看的是「这个厂商有镜像证据吗」，而那一列问的是「**这个格子里的串**在镜像里吗」。
> → 两个问题答案不同，而更宽的那个更容易让人满意。
> 一个刚加上的字段就能抓住作者 —— 这是它值得加的最好证据。**
"""

BACKLOG_ADD = """

## 判据 (d)/优先级 ② — **perimeterx 标记改 Inferred；`DetectAsync` 改用镜像里的 `captcha-delivery`**（R998）

### 探针

| 探测 | 命中 |
|---|---|
| `px-captcha`（marker 列） | **0** |
| `_px3`（cookie 列） | 1 |
| **`captcha-delivery`** | **4**（`geo.captcha-delivery.com` · `/` · `/interstitial/`） |

**→ R997 标 `ImageLiteral` 时看的是 cookie 列；那一列说的是 marker。`Inferred` 现为 3 个。**

### 改了什么

1. `VendorWiring.cs` — perimeterx → `MarkerSource.Inferred`，note 写明镜像里真正的标记
2. `StoreFlow.DetectAsync` — 新增 `captcha-delivery` 分支，**排在 `px-captcha` 之前**
3. `VendorWiringTests.cs` — `Inferred` → `{cloudflare, imperva, perimeterx}`

### 效果

**PerimeterX 的检测从「只靠一个镜像里不存在的串」变成「先测镜像里那个」。
`DetectAsync` 里镜像有据的标记 4/6 → 5/6。**

### 数字

**套件 2210 · 陈旧度 0/0 · 函数数 173,952 · 墙 3/6 · Inferred 3 · 有据标记 5/6**

| 仍 Unknown | |
|---|---|
| imperva 的正确标记 | 镜像里未找到 |
| `cf-chl` 是否真对 | 常识支持，镜像不支持 |

**纪律**：一个刚加上的字段就能抓住写它的人。
"""

BLOCKER = """

---

## 422. **perimeterx 标记改 Inferred；`DetectAsync` 改用镜像里的 `captcha-delivery`（5/6 有据）**

> R998。**改 2 个源 + 1 处断言。** 套件 **2210 通过 / 0 失败 / 0 跳过**。

### 一、R997 标错了一列

| 探测 | 命中 |
|---|---|
| **`px-captcha`**（marker 列写的） | **0** |
| `_px3`（cookie 列写的） | 1 |

**→ R997 我查了 `_px3` 就标了 `ImageLiteral`，而那一列说的是**marker**。
→ `px-captcha` 在镜像里一次都不出现。
→ 所以 `Inferred` 的集合是 **3 个**：cloudflare · imperva · **perimeterx**。**
**→ 而这正是 `MarkerSource` 存在的理由 —— 它也抓到了写它的人。**

### 二、而镜像里有一个**可用**的 PerimeterX 标记

```
0x1470689dc  https://geo.captcha-delivery.com
0x147068a34  https://geo.captcha-delivery.com/
0x147068a8c  https://geo.captcha-delivery.com/interstitial/
```

**`captcha-delivery` 命中 4 次。`geo.captcha-delivery.com` 是 PerimeterX 的挑战域。**

**→ 我们一直在测一个自造的串（`px-captcha`），而镜像里有一个 host 级的、更可靠的标记。
→ 这不是「缺证据」：证据一直在，只是没去找。
→ 而 R997 说「`_px3` 在，所以 `ImageLiteral`」—— 那句把**cookie 的存在**当成了**标记的存在**。**

### 三、改了三处

**① `VendorWiring.cs`：perimeterx 行 → `MarkerSource.Inferred`，note 写明**
「R998 corrects R997's own row … R997 labelled the row ImageLiteral by checking the cookie column instead of the
marker column. The image does carry a usable marker: geo.captcha-delivery.com and its /interstitial/ path」。

**② `StoreFlow.DetectAsync`：加 `captcha-delivery` 分支，排在 `px-captcha` 之前。**

```csharp
// R998: the image names geo.captcha-delivery.com and its /interstitial/ path, four literals, and never
// px-captcha. Testing the marker the artifact actually carries is worth more than testing the one this
// workspace wrote from general knowledge, so both are accepted and the image's comes first.
body.Contains("captcha-delivery", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
body.Contains("px-captcha", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
```

**③ `VendorWiringTests.cs`：`Assert.Equal(new[] { "cloudflare", "imperva", "perimeterx" }, inferred);`**

### 四、而检测能力实际变强了

| 之前 | 现在 |
|---|---|
| `px-captcha`（镜像 0 命中） | `captcha-delivery`（镜像 4 命中）**优先**，`px-captcha` 后备 |

**→ 不只是修标注：它让 PerimeterX 的检测**真的可能命中**，
而之前那条分支只能靠一个镜像里不存在的串去命中。**

### 五、数字

| 度量 | R997 | R998 |
|---|---|---|
| 套件 | 2210 | **2210** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| 墙 Wired | 3 / 6 | **3 / 6（未变）** |
| **`Inferred` 标记** | 2 | **3（+perimeterx）** |
| **`DetectAsync` 里镜像有据的标记** | 4 / 6 | **5 / 6** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str px-captcha        -> {"n":0}
python analysis/ida.py str captcha-delivery  -> {"n":4}
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~VendorWiringTests|FullyQualifiedName~WallDispatchTests|FullyQualifiedName~WallSolvingTests" -m:1  -> 19 通过
python tools/metrics_report.py               -> 完整套件 exit 0  2210 通过 / 0 失败 / 0 跳过
```

### 七、仍然 Unknown

- **imperva 的正确标记**：**Unknown** —— 镜像里未找到。
- **`cf-chl` 是否真对**：**常识支持**，**镜像不支持**（0 命中）。

### 八、教训

**一列「出处」写下去的第一件事，是暴露**写它的人**没按那一列的定义去填。**

**我标 `ImageLiteral` 时看的是「这个厂商有镜像证据吗」，而那一列问的是「**这个格子里的串**在镜像里吗」。
两个问题的答案不同，而更宽的那个更容易让人满意。**

**→ 一个刚加上的字段就能抓住作者 —— 这是它值得加的最好证据。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R998", BLOCKER)
    ensure(RSTATUS, "R998", BLOCKER)
    ensure(RVERDICT, "第 998 轮", VERDICT)
    ensure(BACKLOG, "R998", BACKLOG_ADD)

    note = (
        "\n## R998 补充 — **perimeterx 标记改 Inferred；`DetectAsync` 改用镜像里的 `captcha-delivery`（5/6 有据）**（套件 2210）\n\n"
        "**R997 标错了一列**：`px-captcha` 镜像 **0** 命中，而 `_px3` 是 **cookie** 列的东西。\n"
        "我标 `ImageLiteral` 时看的是「这个厂商有镜像证据吗」，而那一列问的是「**这个格子里的串**在镜像里吗」。\n"
        "→ `Inferred` 现为 **3 个**：cloudflare · imperva · **perimeterx**。\n\n"
        "**而镜像里有一个可用的标记**：`captcha-delivery` **4** 命中（`geo.captcha-delivery.com` · `/` · `/interstitial/`）。\n"
        "→ `DetectAsync` 新增 `captcha-delivery` 分支，**排在 `px-captcha` 之前**。\n"
        "→ 检测能力实际变强：之前只靠一个镜像里不存在的串，现在先测镜像里那个。\n\n"
        "数字：套件 2210 · 陈旧度 0/0 · 函数数 173,952（未 publish）· 墙 3/6 · Inferred 3 · **有据标记 5/6**。\n\n"
        "纪律：**一个刚加上的字段就能抓住写它的人 —— 这是它值得加的最好证据。**\n\n"
        "下一轮：publish 一次刷新函数数（已多轮未 publish）；或 imperva 的标记（5/6 里最后那个没据的）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R998" not in h:
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
             for p, k in ((RBLOCK, "R998"), (RSTATUS, "R998"), (RVERDICT, "第 998 轮"), (BACKLOG, "R998")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R998: R997 checked the wrong column, and the image does carry a PerimeterX marker\n\n"
         "R997 added a provenance column and marked four of six rows as image literals. This round went to verify the\n"
         " PerimeterX row and found the marking wrong in exactly the way that column exists to prevent.\n\n"
         "px-captcha, the string in the marker column, appears nowhere in the image. _px3 does, once -- but _px3 is in the\n"
         " cookie column, and ImageLiteral is a claim about the marker. I had checked that the vendor had image evidence\n"
         " rather than that this cell's string did. So the inferred set is three: cloudflare, imperva, perimeterx. A field\n"
         " added one round earlier caught its author.\n\n"
         "The image also turns out to carry a usable PerimeterX marker that nobody had looked for: geo.captcha-delivery.com\n"
         " with its interstitial path, four literals in all. So the situation was never a lack of evidence. DetectAsync now\n"
         " tests captcha-delivery first and falls back to px-captcha, which means the PerimeterX branch can actually fire;\n"
         " before, its only marker was a string the artifact does not contain.\n\n"
         "Three edits: the row's provenance and note, the detector's marker order, and the guard's expected set. The note on\n"
         " the row now records that R997 made this mistake and why, because the mistake is more instructive than the\n"
         " correction.\n\n"
         "Figures: suite 2210 unchanged, freshness zero, count 173,952 unpublished, walls three of six unchanged, inferred\n"
         " markers three, detection markers with image support five of six.\n\n"
         "Unknown: Imperva's correct marker, which the image does not appear to supply, and whether cf-chl is right, which\n"
         " general knowledge supports and the artifact does not.\n\n"
         "The lesson is that the first thing a provenance column does is expose that whoever wrote it was answering a\n"
         " broader question than the column asks, and the broader question is the more satisfying one to answer.\n\n"
         "Two sources and one assertion changed; suite green at 2210."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()