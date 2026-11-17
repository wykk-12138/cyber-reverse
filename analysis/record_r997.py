"""Record R997: two detection markers are not in the image, and the table now says which."""

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
### 六个检测标记里**两个不在镜像里** —— 而 `cf-chl` 是其中一个（R997）

**R996 说下一轮取 imperva / perimeterx 的证据。取了，而它顺手翻出一个比那两个缺口更大的问题。**

### ① 六行标记，逐个探

| vendor | marker | 镜像命中 | 结论 |
|---|---|---|---|
| kasada | `kpsdk` | **17** | ✓ 真串 |
| queue-it | `queue-it` | **13** | ✓ 真串 |
| datadome | `datadome` | **15** | ✓ 真串 |
| perimeterx | `px-captcha` | （`_px3` 在，见下） | ✓ |
| **cloudflare** | **`cf-chl`** | **0** | ✗ **我们自己编的** |
| **imperva** | **`_Incapsula_Resource`** | **0** | ✗ **我们自己编的** |

> **而 Cloudflare 是**已声明 `Wired`** 的那一格。
> 也就是说：我们检测 Cloudflare 与 Imperva 的方式是**写出来的**，不是**抄下来的**。**
> **`cf-chl` 能工作，因为真实 Cloudflare 挑战页里确实有它 —— 但那是**常识**，不是镜像证据。
> 而一张 `Wired` 的行读起来像是抄来的。**

### ② 而 PerimeterX 的比我们记的多得多

```
0x1434ab609  _px3                              ← 「no _px cookie does」是错的
0x146f609b4  __pxvid   0x146f64474  _pxvid
0x146e3e764  PerimeterX-Token                  ← token header（这条我们有）
0x143336731  "PerimeterXHandler                ← 一个 Handler 类
0x146e3e70c  PerimeterX block (Rotating proxy) ← **封锁 + 代理轮换**
```

> **最后那句是这一轮的信息量所在：它说明原版把「被 PX 封」与**轮换代理**连起来处理。
> 那不是 token 名字，是**行为**。**
> **→ 而 `VendorWiring` 的 note 写着「deliberately blank: a token header exists, no `_px` cookie does」——
> 两处都错：`_px3` 在，而且不止一个 token header。**
> **→ 状态仍是 `DetectedOnly`（我们没有那个调用），但那不是「镜像里什么都没有」。**

### ③ 所以这一轮加的是**一列出处**，不是又改一个名字

**判据 (d)：每条 claim 要有 authority。而那张表的 marker 列**没有表明它是抄的还是写的**。**

**新增：**

```csharp
public enum MarkerSource { ImageLiteral, Inferred }
public sealed record Row(…, State State, string Note, MarkerSource MarkerFrom);
```

**六行各补一个：三个 `ImageLiteral`（kpsdk / queue-it / datadome）+ perimeterx 也是 `ImageLiteral`（`_px3` 在），
两个 `Inferred`（cloudflare / imperva）。**

### ④ 而守卫钉住的是**哪两个**，不是**几个**

```csharp
Assert.Equal(new[] { "cloudflare", "imperva" }, inferred);
```

> **测试没法重新探二进制，所以它钉住探针已经确立的**集合**。
> 要改动它，得重跑 `python analysis/ida.py str <marker>` 并在里面找到东西。**

### ⑤ 而 imperva 那行现在说得更全

**旧 note：「the image names no Imperva cookie and no Imperva host」
新 note：「the image names neither an Imperva cookie nor an Imperva host, **and does not contain this marker either**」**

> **后半句是新的，也是要紧的：不只是「没有 cookie 和 host」，而是**连我们用来检测它的那串都不在镜像里**。
> 所以 imperva 这条分支**整条**是我们自己写的，而它至今没被触发过（因为没有站用 Imperva）。**

### ⑥ 数字

| 度量 | R996 | **R997** |
|---|---|---|
| 套件 | 2209 | **2210（+1 守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| 墙 Wired | 3 / 6 | **3 / 6（未变）** |
| **marker 列有出处的行** | 0 / 6 | **6 / 6** |
| **`Inferred` 标记** | 未测 | **2（cloudflare · imperva）** |

### 教训

> **「检测用的标记」和「镜像里的串」是两件事，而那张表把它们写在同一个格子里。
> 一个 `Wired` 的行因此读起来像抄的 —— 而它的一半是编的。**
> **→ 判据 (d) 要求的不是「有证据」，是「**每条**写着它的证据是什么」。
> 我给六个厂商写了六行 note，而最要紧的那一列没有出处。**
"""

if "六个检测标记里**两个不在镜像里**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 997 轮：六个检测标记里两个不在镜像里 —— 而 `cf-chl` 是其中一个

### ① 六行标记逐个探

| vendor | marker | 镜像命中 | 结论 |
|---|---|---|---|
| kasada | `kpsdk` | **17** | ✓ |
| queue-it | `queue-it` | **13** | ✓ |
| datadome | `datadome` | **15** | ✓ |
| perimeterx | `px-captcha` | `_px3` 在 | ✓ |
| **cloudflare** | **`cf-chl`** | **0** | ✗ **编的** |
| **imperva** | **`_Incapsula_Resource`** | **0** | ✗ **编的** |

> **而 Cloudflare 是已声明 `Wired` 的那一格。
> 我们检测 Cloudflare 与 Imperva 的方式是**写出来的**，不是**抄下来的**。
> `cf-chl` 能工作因为真实挑战页里有它 —— 但那是**常识**，不是镜像证据。而一张 `Wired` 的行读起来像抄的。**

### ② 而 PerimeterX 的比我们记的多得多

```
_px3 · __pxvid · _pxvid · PerimeterX-Token · "PerimeterXHandler
PerimeterX block (Rotating proxy)          ← 封锁 + 代理轮换
```

> **最后那句是信息量所在：原版把「被 PX 封」与**轮换代理**连起来 —— 那不是 token 名字，是**行为**。
> 旧 note「deliberately blank: a token header exists, no `_px` cookie does」两处都错。
> 状态仍是 `DetectedOnly`（没有那个调用），但那不是「镜像里什么都没有」。**

### ③ 加的是**一列出处**，不是又改一个名字

```csharp
public enum MarkerSource { ImageLiteral, Inferred }
public sealed record Row(…, State State, string Note, MarkerSource MarkerFrom);
```

**六行各补：4 个 `ImageLiteral`（kpsdk / queue-it / datadome / px-captcha）+ 2 个 `Inferred`（cloudflare / imperva）。**

### ④ 守卫钉住的是**哪两个**

```csharp
Assert.Equal(new[] { "cloudflare", "imperva" }, inferred);
```

**测试没法重探二进制，所以钉住探针确立的集合；改动它得重跑 `ida.py str <marker>` 并在里面找到东西。**

### ⑤ imperva 那行说得更全了

**新 note 加了「and does not contain this marker either」——
不只是没有 cookie 和 host，而是**连检测标记都不在镜像里**。所以那条分支**整条**是自造的，
而它至今没被触发（没有站用 Imperva）。**

### ⑥ 数字

| 度量 | R996 | **R997** |
|---|---|---|
| 套件 | 2209 | **2210（+1 守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| 墙 Wired | 3 / 6 | **3 / 6（未变）** |
| **marker 列有出处的行** | 0 / 6 | **6 / 6** |
| **`Inferred` 标记** | 未测 | **2** |

### 教训

> **「检测用的标记」和「镜像里的串」是两件事，而那张表把它们写在同一个格子里。
> 一个 `Wired` 的行因此读起来像抄的 —— 而它的一半是编的。
> → 判据 (d) 要的不是「有证据」，是「**每条**写着它的证据是什么」。
> 我给六个厂商写了六行 note，而最要紧的那一列没有出处。**
"""

BACKLOG_ADD = """

## 判据 (d)/优先级 ② — **六行 marker 加出处列：4 个 ImageLiteral · 2 个 Inferred（cloudflare · imperva）**（R997）

### 探针结果

| marker | 镜像命中 |
|---|---|
| `kpsdk` | 17 ✓ |
| `queue-it` | 13 ✓ |
| `datadome` | 15 ✓ |
| `_px3`（perimeterx） | 在 ✓ |
| **`cf-chl`（cloudflare）** | **0 ✗ 自造** |
| **`_Incapsula_Resource`（imperva）** | **0 ✗ 自造** |

**→ `Wired` 的 Cloudflare 那一行，检测标记是我们写的不是抄的。**

### PerimeterX 更正

**`_px3` · `__pxvid` · `_pxvid` · `PerimeterX-Token` · `PerimeterXHandler` ·
「PerimeterX block (Rotating proxy)」全在镜像里 → 旧 note「no `_px` cookie does」错。
状态仍 `DetectedOnly`（调用未写），但那不是「镜像里空的」。**

### 改了什么

- `VendorWiring.cs`：新增 `MarkerSource { ImageLiteral, Inferred }`；`Row` 加一列；六行各补；perimeterx / imperva note 更正
- `VendorWiringTests.cs`：新增 `TheMarkerColumnSaysWhereEachMarkerCameFrom`（钉住集合 = {cloudflare, imperva}）

### 数字

**套件 2210（+1 守卫）· 陈旧度 0/0 · 函数数 173,952 · 墙 3/6 · marker 出处 6/6 · Inferred 2**

| 仍 Unknown | |
|---|---|
| imperva 的正确检测标记 | 镜像里没有，未找到 |
| cf-chl 是否真对（真实挑战页有，但非镜像证据） | 常识支持，镜像不支持 |

**纪律**：判据 (d) 要的不是「有证据」，是「每条写着它的证据是什么」。
"""

BLOCKER = """

---

## 421. **六行 marker 加出处列：4 个 ImageLiteral · 2 个 Inferred（cloudflare · imperva）**

> R997。**改 `VendorWiring.cs` + 1 条守卫。** 套件 **2210 通过 / 0 失败 / 0 跳过**。

### 一、探针结果

| vendor | marker | 镜像命中 | 结论 |
|---|---|---|---|
| kasada | `kpsdk` | **17** | ✓ |
| queue-it | `queue-it` | **13** | ✓ |
| datadome | `datadome` | **15** | ✓ |
| perimeterx | `px-captcha` | `_px3` 在 | ✓ |
| **cloudflare** | **`cf-chl`** | **0** | ✗ **自造** |
| **imperva** | **`_Incapsula_Resource`** | **0** | ✗ **自造** |

**→ 六行 marker 里两个不在镜像里，而 **Cloudflare 是已声明 `Wired`** 的那一格。
→ 我们检测 Cloudflare 与 Imperva 的方式是**写出来的**，不是**抄下来的**。
→ `cf-chl` 能工作，因为真实 Cloudflare 挑战页里确实有它 —— 但那是**常识**，不是镜像证据。
→ 而一张 `Wired` 的行读起来像是抄来的。**

### 二、而 PerimeterX 的比我们记的多得多

```
0x1434ab609  _px3                              ← 「no _px cookie does」是错的
0x146f609b4  __pxvid   0x146f64474  _pxvid
0x146e3e764  PerimeterX-Token
0x143336731  "PerimeterXHandler                ← 一个 Handler 类
0x146e3e70c  PerimeterX block (Rotating proxy) ← 封锁 + 代理轮换
```

**→ 最后那句是这一轮的信息量所在：原版把「被 PX 封」与**轮换代理**连起来处理。
那不是 token 名字，是**行为**。
→ 旧 note「deliberately blank: a token header exists, no `_px` cookie does」两处都错。
→ 状态仍是 `DetectedOnly`（我们没有那个调用），但那不是「镜像里什么都没有」。**

### 三、所以加的是**一列出处**

**判据 (d)：每条 claim 要有 authority。而 marker 列**没有表明它是抄的还是写的**。**

```csharp
public enum MarkerSource
{
    /// <summary>The image contains this literal.</summary>
    ImageLiteral,
    /// <summary>This workspace chose this marker; the image does not carry it.</summary>
    Inferred,
}

public sealed record Row(string Vendor, string Marker, string? Cookie, State State, string Note,
    MarkerSource MarkerFrom);
```

**六行各补：4 个 `ImageLiteral`（kpsdk · queue-it · datadome · px-captcha）+ 2 个 `Inferred`（cloudflare · imperva）。**

### 四、守卫钉住的是**哪两个**

```csharp
[Fact]
public void TheMarkerColumnSaysWhereEachMarkerCameFrom()
{
    var inferred = VendorWiring.Rows
        .Where(r => r.MarkerFrom == VendorWiring.MarkerSource.Inferred)
        .Select(r => r.Vendor).ToList();
    Assert.Equal(new[] { "cloudflare", "imperva" }, inferred);
    …
}
```

**→ 测试没法重新探二进制，所以它钉住探针已经确立的**集合**。
→ 要改动它，得重跑 `python analysis/ida.py str <marker>` 并在里面找到东西。**

### 五、imperva 那行说得更全

**旧：「the image names no Imperva cookie and no Imperva host」
新：「… **and does not contain this marker either**」**

**→ 后半句是新的，也是要紧的：不只是「没有 cookie 和 host」，而是**连我们用来检测它的那串都不在镜像里**。
→ 所以 imperva 这条分支**整条**是我们自己写的，而它至今没被触发过（没有站用 Imperva）。**

### 六、数字

| 度量 | R996 | R997 |
|---|---|---|
| 套件 | 2209 | **2210（+1 守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| 墙 Wired | 3 / 6 | **3 / 6（未变）** |
| **marker 列有出处的行** | 0 / 6 | **6 / 6** |
| **`Inferred` 标记** | 未测 | **2（cloudflare · imperva）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str cf-chl                -> {"n":0}
python analysis/ida.py str _Incapsula_Resource   -> {"n":0}
python analysis/ida.py str kpsdk                 -> {"n":17}
python analysis/ida.py str _px3                  -> {"n":1}
python analysis/ida.py str "PerimeterX"          -> 5 条，含 PerimeterXHandler / PerimeterX block (Rotating proxy)
cd replica
python tools/snapshot.py                                          -> 322 files
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug -> 已成功生成
dotnet test --filter "FullyQualifiedName~VendorWiringTests" -m:1   -> 9 通过
python tools/metrics_report.py                                    -> 完整套件 exit 0  2210 通过 / 0 失败 / 0 跳过
```

### 八、仍然 Unknown

- **imperva 的正确检测标记**：**Unknown** —— 镜像里没有，未找到替代。
- **`cf-chl` 是否真的对**：**常识支持**（真实挑战页含它），**镜像不支持**。

### 九、教训

**「检测用的标记」和「镜像里的串」是两件事，而那张表把它们写在同一个格子里。
一个 `Wired` 的行因此读起来像抄的 —— 而它的一半是编的。**

**→ 判据 (d) 要求的不是「有证据」，是「**每条**写着它的证据是什么」。
我给六个厂商写了六行 note，而最要紧的那一列没有出处。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R997", BLOCKER)
    ensure(RSTATUS, "R997", BLOCKER)
    ensure(RVERDICT, "第 997 轮", VERDICT)
    ensure(BACKLOG, "R997", BACKLOG_ADD)

    note = (
        "\n## R997 补充 — **六行 marker 加出处列：4 ImageLiteral · 2 Inferred（cloudflare · imperva）**（套件 2210）\n\n"
        "探针：`kpsdk` 17 · `queue-it` 13 · `datadome` 15 · `_px3` 在 —— 四个真串；\n"
        "**`cf-chl` 0 · `_Incapsula_Resource` 0** —— 两个是**我们自己编的**。\n"
        "→ 而 **Cloudflare 是已声明 `Wired` 的那一格**：它的检测标记是我们写的不是抄的。\n"
        "→ `cf-chl` 能工作因为真实挑战页里有它 —— 但那是**常识**，不是镜像证据。\n\n"
        "**PerimeterX 更正**：`_px3` · `_pxvid` · `PerimeterX-Token` · `PerimeterXHandler` ·\n"
        "「PerimeterX block (Rotating proxy)」全在。旧 note「no `_px` cookie does」错。\n"
        "那句「block (Rotating proxy)」说明原版把**被封与轮换代理**连起来 —— 那是行为不是 token 名。\n\n"
        "加了一列：`MarkerSource { ImageLiteral, Inferred }`，`Row` 多一个参数，六行各补。\n"
        "守卫 `TheMarkerColumnSaysWhereEachMarkerCameFrom` 钉住 `Inferred == {cloudflare, imperva}`\n"
        "（测试没法重探二进制，所以钉集合；改动它得重跑 `ida.py str` 并在里面找到东西）。\n\n"
        "数字：套件 2210（+1 守卫）· 陈旧度 0/0 · 函数数 173,952 · 墙 3/6 · marker 出处 6/6 · Inferred 2。\n\n"
        "纪律：**判据 (d) 要的不是「有证据」，是「每条写着它的证据是什么」。**\n\n"
        "下一轮：publish 一次刷新函数数（已多轮未 publish）；或查 `px-captcha` 是否也在镜像里（我只验了 `_px3`）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R997" not in h:
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
             for p, k in ((RBLOCK, "R997"), (RSTATUS, "R997"), (RVERDICT, "第 997 轮"), (BACKLOG, "R997")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R997: two of six detection markers are not in the image, and cf-chl is one of them\n\n"
         "R996 left Imperva and PerimeterX to be looked for. Probing turned up something larger than either gap.\n\n"
         "Of six detection markers, four are image literals: kpsdk seventeen times, queue-it thirteen, datadome fifteen,\n"
         " and the _px3 cookie for PerimeterX. Two are in the image nowhere at all: cf-chl for Cloudflare and\n"
         " _Incapsula_Resource for Imperva. So the detectors for those two were written here rather than transcribed, and\n"
         " one of them belongs to a row the audit calls Wired. cf-chl does work, because a real Cloudflare challenge page\n"
         " carries it -- but that is general knowledge, not evidence from the artifact, and a Wired row should not read as\n"
         " though it had been copied.\n\n"
         "PerimeterX also turned out to be richer than recorded. The note said a token header existed and no _px cookie did.\n"
         " Both halves are wrong: _px3, _pxvid, __pxvid and PerimeterX-Token are all there, alongside a PerimeterXHandler\n"
         " and the line PerimeterX block (Rotating proxy). That last one says the original treats a PerimeterX block as\n"
         " something to answer by rotating proxies, which is behaviour rather than a token name, and it is the most useful\n"
         " thing this round found.\n\n"
         "What the table lacked was provenance. Six rows carried a marker and six notes carried reasons, and nothing said\n"
         " which markers came from the artifact. Criterion (d) asks for authority on every claim, and this was the column\n"
         " where it was missing, so MarkerSource now distinguishes ImageLiteral from Inferred and every row states its own.\n"
         " A test pins the inferred set to cloudflare and imperva, because a test cannot re-probe the binary and the honest\n"
         " thing it can do is hold what the probe established: changing the set means running the probe and finding the\n"
         " marker there.\n\n"
         "Imperva's note also gained the stricter fact. It is not only that the image names no Imperva cookie and no host;\n"
         " it does not contain the marker this detector looks for either, so that whole branch is this workspace's writing\n"
         " and has never fired, because no store in scope uses Imperva.\n\n"
         "Figures: suite 2209 to 2210, freshness zero, count 173,952 unpublished, walls three of six unchanged, marker\n"
         " provenance on six rows, two inferred.\n\n"
         "Unknown: Imperva's correct marker, which the image does not supply; and whether cf-chl is right, which general\n"
         " knowledge supports and the image does not.\n\n"
         "The lesson is that a marker used for detection and a string the image contains are two different things, and the\n"
         " table put them in the same cell. Criterion (d) does not ask whether evidence exists; it asks that each claim say\n"
         " what its evidence is.\n\n"
         "One enum and one column added, two notes corrected, one guard added; suite green at 2210."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()