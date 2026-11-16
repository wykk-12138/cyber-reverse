"""Record R910: leverage-ranked selection, four HTTP lifecycle names, and a clean 58-for-58 verification."""

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
### 让数据挑目标：最高杠杆的四个名字全在 HTTP 客户端上（R910）

**前面几轮的目标是「碰巧注意到的」。这一轮按镜像里的出现次数排序缺失名字。**

**新工具 `tools/absent_by_leverage.py`。排序后前四名：**

| 名字 | 镜像引用次数 |
|---|---|
| **`StartAsync`** | **19** |
| **`HandleResponse`** | **18** |
| **`StopAsync`** | **14** |
| `WriteToAsync` | 7 |
| `ScrapeProduct` · `ScrapeJson` · `GetOwnProperties` · `DisposeAsyncCore` | 各 7 |

### 而前四名里三个是 HTTP 客户端的生命周期

**查过：`BouncyHttpClient` 在，但 `StartAsync` / `StopAsync` / `HandleResponse` / `DisposeAsyncCore`
**全库一个都没有**。**

**而它的 `Dispose()` 是**空体** —— `public void Dispose() { }`，正是 R850 的「有形状无内容」，换了个名字。**

### 改了什么

| 改动 | 依据 |
|---|---|
| `ParseResponse` → **`HandleResponse`** | **同一概念，用镜像的名字** |
| `+ StartAsync` · `+ StopAsync` · `+ IsRunning` | 生命周期 |
| `+ DisposeAsyncCore` · `+ IAsyncDisposable` | 异步释放 |
| `Dispose()` 不再空 | `StopAsync` 里 `_analytics?.Flush()` |

**而 `StartAsync` 在 `StopAsync` 之后**拒绝启动**（抛 `NetException`）—— 不是因为镜像这么做，
是因为**允许复活已释放的客户端会让错误推到后面的 socket 失败上**。**

### 数字，而这一轮可以验算

| 度量 | R909 | **R910** |
|---|---|---|
| 套件 | 1808 | **1815** |
| 异步覆盖 | 311（20.1%） | **315（20.4%）** |
| **缺失名承载的出现次数** | **1523** | **1465** |

**58 的差，正好等于那四个名字的引用次数之和：19 + 18 + 14 + 7 = **58**。**

**这是这一串度量工作里第一次出现**事先可算的预测与实际相符**：
加哪些名字之前就知道会减去多少，而结果一分不差。**

### 而新的缺失榜首已经换人了

`WriteToAsync` 7 · `ScrapeProduct` 7 · `ScrapeJson` 7 · `GetOwnProperties` 7 · `WriteRawAsync` 6

**其中 `ScrapeProduct` / `ScrapeJson` 属优先级 ①（抓商品），`WriteToAsync` / `WriteRawAsync` 属 ③（IO）。**
"""

if "让数据挑目标：最高杠杆的四个名字" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R910 appended")

VERDICT = """

---

## 第 910 轮：让数据挑目标 —— 最高杠杆的四个名字全在 HTTP 客户端上

### 按镜像出现次数排序缺失名字

| 名字 | 次数 |
|---|---|
| **`StartAsync`** | **19** |
| **`HandleResponse`** | **18** |
| **`StopAsync`** | **14** |
| `WriteToAsync` | 7 |
| `ScrapeProduct` · `ScrapeJson` · `GetOwnProperties` · `DisposeAsyncCore` | 各 7 |

### 而前四名里三个是 HTTP 客户端的生命周期

**`BouncyHttpClient` 在，但 `StartAsync` / `StopAsync` / `HandleResponse` / `DisposeAsyncCore` **全库没有**。**

> **而它的 `Dispose()` 是**空体** —— `public void Dispose() { }`，正是 R850 的「有形状无内容」，换了个名字。**

### 改了什么

| 改动 | 依据 |
|---|---|
| `ParseResponse` → **`HandleResponse`** | 同一概念，用镜像的名字 |
| `+ StartAsync` · `+ StopAsync` · `+ IsRunning` | 生命周期 |
| `+ DisposeAsyncCore` · `+ IAsyncDisposable` | 异步释放 |
| `Dispose()` 不再空 | `_analytics?.Flush()` |

**`StartAsync` 在 `StopAsync` 之后拒绝启动（抛 `NetException`）—— 不是镜像这么做，而是
**允许复活已释放的客户端会把错误推到后面的 socket 失败上**。**

### 数字，而这一轮可以验算

| 度量 | R909 | **R910** |
|---|---|---|
| 套件 | 1808 | **1815** |
| 异步覆盖 | 311（20.1%） | **315（20.4%）** |
| **缺失名承载的出现次数** | **1523** | **1465** |

> **58 的差 = 19 + 18 + 14 + 7。**
> **这是这一串度量工作里第一次出现**事先可算的预测与实际相符** —— 加哪些名字之前就知道会减去多少，结果一分不差。**

### 新的缺失榜首

**`WriteToAsync` 7 · `ScrapeProduct` 7 · `ScrapeJson` 7 · `GetOwnProperties` 7 · `WriteRawAsync` 6**
**→ `ScrapeProduct`/`ScrapeJson` 属 ①（抓商品）；`WriteToAsync`/`WriteRawAsync` 属 ③（IO）。**

### 教训

> **前面几轮我挑目标的依据是「刚注意到什么」，而这一轮是「哪里被引用得最多」。**
> **两者差别的证据是：这一轮的数字可以**事先算出来**，而之前的不能。**
> **一个可以被预测的改进，说明选择依据是结构而不是记忆。**
"""

BACKLOG_ADD = """

## 优先级 ③ — HTTP 客户端生命周期四个名字（R910，**改产品代码 +7 用例**）

### 选择依据换成杠杆

**`tools/absent_by_leverage.py` 按镜像引用次数排序缺失名：`StartAsync` 19 · `HandleResponse` 18 · `StopAsync` 14 · `DisposeAsyncCore` 7。**

### 而这三个是 HTTP 客户端生命周期，全库没有；`Dispose()` 是空体（R850 同形）

**改动**：`ParseResponse` → `HandleResponse` · `+StartAsync` · `+StopAsync` · `+IsRunning` ·
`+DisposeAsyncCore` · `+IAsyncDisposable` · `Dispose()` 不再空

**`StartAsync` 在 `StopAsync` 后拒绝启动** —— 防止复活已释放的客户端把错误推到 socket 层。

### 数字（可验算）

| 度量 | R909 | **R910** |
|---|---|---|
| 套件 | 1808 | **1815** |
| 异步覆盖 | 311（20.1%） | **315（20.4%）** |
| **缺失名承载出现次数** | **1523** | **1465** |

**58 的差 = 19+18+14+7，**事先可算，结果一分不差** —— 这一串度量里第一次。**

### 新榜首

**`WriteToAsync` 7 · `ScrapeProduct` 7 · `ScrapeJson` 7 · `GetOwnProperties` 7 · `WriteRawAsync` 6**

| 仍 Unknown | |
|---|---|
| `StartAsync` 原版里具体做什么 | 可能预热连接池或预协商 TLS |
| `ScrapeProduct`/`ScrapeJson` 是否同族 | 属 ① |
| `GetOwnProperties` 属什么层 | 反射 |

**纪律**：**一个可以被预测的改进，说明选择依据是结构而不是记忆。**
"""

BLOCKER = """

---

## 334. HTTP 客户端生命周期四名字；缺失出现次数 1523 → 1465（可验算）

> R910。**改产品代码 +7 用例。** 套件 **1815 通过 / 0 失败 / 0 跳过**。

### 一、选择依据换成杠杆

**新增 `tools/absent_by_leverage.py`：按镜像引用次数排序缺失名。**

| 名字 | 次数 |
|---|---|
| **`StartAsync`** | **19** |
| **`HandleResponse`** | **18** |
| **`StopAsync`** | **14** |
| `WriteToAsync` | 7 |
| `ScrapeProduct` · `ScrapeJson` · `GetOwnProperties` · `DisposeAsyncCore` | 各 7 |

### 二、前四名里三个是 HTTP 客户端生命周期，全库没有

**而 `BouncyHttpClient.Dispose()` 是**空体** —— R850 的「有形状无内容」，换了名字。**

### 三、改动

| 改动 | 依据 |
|---|---|
| `ParseResponse` → `HandleResponse` | 同一概念，用镜像名字 |
| `+ StartAsync` · `+ StopAsync` · `+ IsRunning` | 生命周期 |
| `+ DisposeAsyncCore` · `+ IAsyncDisposable` | 异步释放 |
| `Dispose()` 不再空 | `_analytics?.Flush()` |

**`StartAsync` 在 `StopAsync` 之后抛 `NetException`** —— 防止复活已释放的客户端。

### 四、数字可验算

| 度量 | R909 | **R910** |
|---|---|---|
| 套件 | 1808 | **1815** |
| 异步覆盖 | 311（20.1%） | **315（20.4%）** |
| 缺失名承载出现次数 | **1523** | **1465** |

**58 = 19 + 18 + 14 + 7。事先可算，结果一分不差。**

### 五、一次编译错

**`DisposeAsyncCore` 第一次写成 `protected virtual`，而 `BouncyHttpClient` 是 `sealed` → CS0549。
改成 `private`，并在注释里写明「这个类的密封使得惯常的 override 点不存在」。**

### 六、仍然 Unknown

- **`StartAsync` 在原版里具体做什么**：**Unknown** —— 可能预热连接池、预协商 TLS，或别的。
  **名字说明有生命周期，不说生命周期里有什么。**
- **`ScrapeProduct` / `ScrapeJson` 是否同族**：**Unknown**，属优先级 ①。
- **`GetOwnProperties` 属哪层**：**Unknown** —— 名字像反射。

### 七、教训

**前面几轮挑目标的依据是「刚注意到什么」，这一轮是「哪里被引用得最多」。**

**而两者差别的证据是：这一轮的数字可以**事先算出来**，而之前的不能。**

**一个可以被预测的改进，说明选择依据是结构而不是记忆。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R910", BLOCKER)
    ensure(RSTATUS, "R910", BLOCKER)
    ensure(RVERDICT, "第 910 轮", VERDICT)
    ensure(BACKLOG, "R910", BACKLOG_ADD)

    note = (
        "\n## R910 补充 — HTTP 客户端生命周期四名字（改产品代码 +7 用例，套件 1808→1815）\n\n"
        "新工具 tools/absent_by_leverage.py 按镜像引用次数排序缺失名：StartAsync 19 · HandleResponse 18 · StopAsync 14 · "
        "DisposeAsyncCore 7 —— 这四个全库没有，而 BouncyHttpClient.Dispose() 是空体（R850 同形）。\n\n"
        "改动：ParseResponse → HandleResponse · +StartAsync · +StopAsync · +IsRunning · +DisposeAsyncCore · +IAsyncDisposable · Dispose 不再空。\n\n"
        "数字：套件 1815 · 异步覆盖 311 → 315（20.4%）· 缺失名承载出现次数 1523 → 1465。\n"
        "58 的差 = 19+18+14+7 —— 事先可算，结果一分不差。这一串度量里第一次。\n\n"
        "新榜首：WriteToAsync 7 · ScrapeProduct 7 · ScrapeJson 7 · GetOwnProperties 7 · WriteRawAsync 6。\n"
        "ScrapeProduct/ScrapeJson 属 ①（抓商品）—— 下一轮从这里挑。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R910" not in h:
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
             for p, k in ((RBLOCK, "R910"), (RSTATUS, "R910"), (RVERDICT, "第 910 轮"), (BACKLOG, "R910")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R910: leverage-ranked selection finds the HTTP client lifecycle, and the drop is 58 for 58\n\n"
         "Earlier rounds picked their target by what happened to be noticed. This one ranks absent async names by how\n"
         " many places the original references them, and the top four are StartAsync at nineteen, HandleResponse at\n"
         " eighteen, StopAsync at fourteen and DisposeAsyncCore at seven.\n\n"
         "The replica had none of them. BouncyHttpClient existed with an empty Dispose body, which is R850's shape\n"
         " without content wearing a different name, and ParseResponse was the same concept as HandleResponse under a\n"
         " name the image does not use.\n\n"
         "So ParseResponse is renamed, and the client gains StartAsync, StopAsync, IsRunning, DisposeAsyncCore and the\n"
         " IAsyncDisposable interface. StartAsync refuses after StopAsync rather than reopening, because a client whose\n"
         " resources have been released should fail where the mistake was made and not at the next socket error.\n\n"
         "The figures: suite from 1808 to 1815, async coverage from 311 to 315, twenty point one to twenty point four,\n"
         " and the occurrence count carried by absent names from 1523 to 1465. That difference is 58, which is exactly\n"
         " nineteen plus eighteen plus fourteen plus seven -- predictable before the change and exact after it. It is\n"
         " the first time in this stretch of measurement work that a figure could be predicted rather than explained.\n\n"
         "One compile error is worth a line: DisposeAsyncCore was written protected virtual, and BouncyHttpClient is\n"
         " sealed, so CS0549. It is private now, with a note that the class's sealing removes the usual override point.\n\n"
         "Unknown: what StartAsync does in the original, whether it warms a pool or negotiates TLS early, since the\n"
         " name establishes a lifecycle and not its contents; whether ScrapeProduct and ScrapeJson are one family, which\n"
         " belongs to the checkout priority; and what layer GetOwnProperties belongs to, its name suggesting reflection.\n\n"
         "The lesson is about how a choice can be checked. This round's improvement could be computed in advance, and\n"
         " the earlier ones could only be described afterwards, which is the difference between choosing by structure\n"
         " and choosing by memory.\n\n"
         "Product code changed; suite green at 1815."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
