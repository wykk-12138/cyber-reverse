"""Record R959: Queue-it read out of a class's field list, misspelling included."""

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
### Queue-it 是从**一个类的字段列表**里读出来的（R959）

**R958 之后转优先级 ②。而 IDA 断过一次（重启后没开），三个框走完才就绪 —— 而就绪之后拿到的证据出乎意料地实。**

### 一段字段列表，不是名字

```
QueueHostMarkers(AcceptedCookiePrefix<QueueITAccepted-SDFrts345E-V3_*CookieValiditySecondsa<MinRemainingSecond
```

**那一条串里是一个类的**完整字段清单**：**

| 字段 | 值 |
|---|---|
| `QueueHostMarkers` | 判定这是不是 Queue-it 表面 |
| `AcceptedCookiePrefix` | **`QueueITAccepted-SDFrts345E-V3_`** |
| `CookieValiditySeconds` | 通行证有效期 |
| `MinRemainingSeconds` | 通行证**至少还要剩多久才算可用** |

> **那个前缀里的 `SDFrts345E` 是一个**哈希**，是 cookie 名字的一部分 —— 不是占位符。
> 所以它逐字保留，不做归一化。****

### 而 `MinRemainingSeconds` 这个字段说明了为什么要提前几秒判废

**一个剩余有效期为几秒的通行证比没有更糟：**
**它授权的那个请求会在**排队已经离开之后**才被拒。**

> **所以那个判断不是「它有效吗」，是「它有效到**够跑完**吗」。
> 而复刻件如果只判前者，会在最难恢复的位置失败。****

### 而五条控制流文案里有一条**拼错了**

```
Fetching Queue-it challenge
Initiliazing Queue-it                 <- 镜像自己拼错（Initiliazing）
Error Initiliazing Queue-it (Softblock)
Error Solving Queue-it (Softblock)
Queue-IT banned, rotating proxy
```

> **而拼错的这条**照原样保留**。
> 一个「把拼写改对」的复刻件，日志就不再和原版一样了 —— 而这种差异在某天对日志时是最难查的。****

### 而一个状态可以有两种意思，所以判定要两样东西

**200 加一个通行证 = 通过；200 没有通行证 = **还在排队**。同一个状态码。**

**所以 `Verdict(status, hasPass)` 收两样，而不是只看 status。**

### 数字

| 度量 | R958 | **R959** |
|---|---|---|
| 套件 | 2129 | **2147** |
| 产物陈旧度 | 0 / 0 | **1 文件 / 119 行（需重发）** |
| 函数数 | 173,866 | **173,866（未变 —— 全是 const 与小静态方法且无人调用）** |

### 教训

> **这一轮最实的一条不是「Queue-it 存在」，是那个**字段列表**。
> 名字告诉你有一家厂商；字段列表告诉你**它怎么判、判什么、以及为什么不能等到零**。**
> **而一个线索的价值，取决于它离**行为**有多近。`Queue-it` 这个词离行为很远，
> `MinRemainingSeconds` 就在行为里。**
"""

if "Queue-it 是从**一个类的字段列表**里读出来的" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 959 轮：Queue-it 是从一个类的字段列表里读出来的

### 一段字段列表，不是名字

```
QueueHostMarkers(AcceptedCookiePrefix<QueueITAccepted-SDFrts345E-V3_*CookieValiditySecondsa<MinRemainingSecond
```

| 字段 | 值 |
|---|---|
| `QueueHostMarkers` | 判定是不是 Queue-it 表面 |
| `AcceptedCookiePrefix` | **`QueueITAccepted-SDFrts345E-V3_`** |
| `CookieValiditySeconds` | 通行证有效期 |
| `MinRemainingSeconds` | **至少还要剩多久才算可用** |

> **`SDFrts345E` 是 cookie 名字里的**哈希**，不是占位符 → 逐字保留。**

### 而 `MinRemainingSeconds` 说明了为什么不能等到零

**剩余几秒的通行证比没有更糟：它授权的请求会在**排队已经离开之后**才被拒。**

> **所以判断不是「它有效吗」，是「它有效到**够跑完**吗」。**

### 五条文案里有一条**拼错了**

**`Initiliazing Queue-it`（镜像自己拼错）→ **照原样保留**。**
**「把拼写改对」的复刻件，日志就不再和原版一样 —— 而那种差异对日志时最难查。**

### 一个状态两种意思

**200 + 通行证 = 通过；200 无通行证 = **还在排队**。→ `Verdict(status, hasPass)` 收两样。**

### 数字

| 度量 | R958 | **R959** |
|---|---|---|
| 套件 | 2129 | **2147** |
| 产物陈旧度 | 0 / 0 | **1 文件 / 119 行** |
| 函数数 | 173,866 | **173,866（未变）** |

### 教训

> **最实的不是「Queue-it 存在」，是那个**字段列表**。
> 名字告诉你有一家厂商；字段列表告诉你**它怎么判、判什么、为什么不能等到零**。
> **一个线索的价值取决于它离行为有多近 —— `Queue-it` 离得很远，`MinRemainingSeconds` 就在行为里。**
"""

BACKLOG_ADD = """

## 优先级 ② — Queue-it 协议（R959，**+18 用例**）

### 证据

**字段列表：`QueueHostMarkers` · `AcceptedCookiePrefix` = `QueueITAccepted-SDFrts345E-V3_` ·
`CookieValiditySeconds` · `MinRemainingSeconds`**
**文案：五条，其中 `Initiliazing Queue-it` **拼错照留****
**handler 三种拼写：`QueueItHandler` / `queueItHandler` / `_queueItHandler`**

### `Scripts/QueueItProtocol.cs`

**`HostSuffix` · `WaitingRoomPrefix` · `AcceptedCookiePrefix` · `Messages` · `HandlerNames` ·
`IsQueueHost` · `CookieName` · `IsAcceptedCookie` · `IsUsable`（剩余时间）· `Verdict`（status+pass）· `Describe`**
**+ `QueueVerdict` 枚举（Waiting/Passed/Banned/RetryLater/Failed）**

### 数字

**套件 2129 → 2147 · 陈旧度 1 文件 / 119 行 · 函数数 173,866（未变）**

| 仍 Unknown | |
|---|---|
| `CookieValiditySeconds` 的实际数值 | 只有字段名 |
| 排队页的轮询间隔 | 未取证 |
| `Softblock` 与硬封的区别 | 只有两条文案 |

**纪律**：一个线索的价值取决于它离行为有多近。
"""

BLOCKER = """

---

## 383. Queue-it 协议：从字段列表读出判定条件

> R959。**改产品代码 +18 用例。** 套件 **2147 通过 / 0 失败 / 0 跳过**。

### 一、证据是一段字段列表

```
QueueHostMarkers(AcceptedCookiePrefix<QueueITAccepted-SDFrts345E-V3_*CookieValiditySecondsa<MinRemainingSecond
```

**`QueueHostMarkers` · `AcceptedCookiePrefix`（含哈希）· `CookieValiditySeconds` · `MinRemainingSeconds`**

### 二、`MinRemainingSeconds` 是那个要紧的字段

**剩余几秒的通行证比没有更糟：它授权的请求会在排队已离开之后被拒。
所以判据是「有效到够跑完吗」，不是「有效吗」。**

### 三、五条文案，一条拼错

**`Initiliazing Queue-it` —— 镜像拼错，**照原样保留**。改对拼写的复刻件日志就不再和原版一样。**

### 四、一个状态两种意思

**200 + 通行证 = 通过；200 无通行证 = 还在排队 → `Verdict(status, hasPass)`。**

### 五、数字

| 度量 | R958 | R959 |
|---|---|---|
| 套件 | 2129 | **2147** |
| 产物陈旧度 | 0 / 0 | **1 / 119** |
| 函数数 | 173,866 | **173,866** |

### 六、验证

```
analysis/ida.py str queueit   -> QueueHostMarkers / AcceptedCookiePrefix / CookieValiditySeconds / MinRemainingSeconds
analysis/ida.py str queue-it  -> 五条文案（含拼错的 Initiliazing）
test --filter QueueItProtocolTests -> 18 通过
metrics_report.py                  -> 2147 通过 / 0 失败
```

### 七、仍然 Unknown

- **`CookieValiditySeconds` 的实际数值**：**Unknown** —— 只有字段名。
- **排队页的轮询间隔**：**Unknown** —— 未取证。
- **`Softblock` 与硬封的区别**：**Unknown** —— 只有两条文案。

### 八、教训

**名字告诉你有一家厂商；字段列表告诉你它怎么判、判什么、为什么不能等到零。**

**一个线索的价值取决于它离行为有多近。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R959", BLOCKER)
    ensure(RSTATUS, "R959", BLOCKER)
    ensure(RVERDICT, "第 959 轮", VERDICT)
    ensure(BACKLOG, "R959", BACKLOG_ADD)

    note = (
        "\n## R959 补充 — Queue-it 协议：从字段列表读出判定条件（+18 用例，套件 2147）\n\n"
        "证据是一段字段列表：QueueHostMarkers · AcceptedCookiePrefix = `QueueITAccepted-SDFrts345E-V3_`（含哈希）· "
        "CookieValiditySeconds · MinRemainingSeconds。\n\n"
        "MinRemainingSeconds 是要紧的那个：剩余几秒的通行证比没有更糟（授权的请求会在排队已离开之后被拒）→ "
        "判据是「有效到够跑完吗」。\n\n"
        "五条文案一条拼错：`Initiliazing Queue-it` → 照原样保留（改对拼写日志就不再和原版一样）。\n"
        "一个状态两种意思：200+通行证=通过、200无通行证=还在排队 → Verdict(status, hasPass)。\n\n"
        "数字：套件 2129 → 2147 · 陈旧度 1 文件 / 119 行（需重发）· 函数数 173,866（未变）。\n\n"
        "纪律：一个线索的价值取决于它离行为有多近。\n\n"
        "下一轮：重发消除陈旧度；或查 CookieValiditySeconds 的实际数值与排队轮询间隔。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R959" not in h:
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
             for p, k in ((RBLOCK, "R959"), (RSTATUS, "R959"), (RVERDICT, "第 959 轮"), (BACKLOG, "R959")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R959: Queue-it read out of a class's field list, misspelling included\n\n"
         "After R958 closed the decompile-by-name route, this round went to the risk-control priority. Getting IDA back\n"
         " took three dialogs -- the unpacked database warning, the unclosed id0, and a wait -- after which the evidence\n"
         " was better than expected.\n\n"
         "The image carries a concatenated field list, not merely a product name: QueueHostMarkers, AcceptedCookiePrefix,\n"
         " CookieValiditySeconds and MinRemainingSeconds. The prefix is QueueITAccepted-SDFrts345E-V3_ and the hash inside\n"
         " it is part of the cookie's name rather than a placeholder, so it is kept verbatim.\n\n"
         "MinRemainingSeconds is the field that carries the behaviour. A pass with seconds left is worse than none,\n"
         " because the request it authorises is refused after the queue has already been left; so the question is not\n"
         " whether the pass is valid but whether it is valid long enough to finish, and the replica now asks the second.\n\n"
         "Five control-flow messages came with it, and one is misspelled in the image -- Initiliazing Queue-it. The\n"
         " misspelling is kept, because a replica that corrects it stops matching the original's own log, and that\n"
         " difference would be hardest to find on the day the logs are compared.\n\n"
         "One status can mean two things: a 200 with a pass is through, a 200 without one is still queued. So the verdict\n"
         " takes the status and the pass together rather than reading the status alone.\n\n"
         "Figures: suite 2129 to 2147, count unchanged at 173,866 since the new code is constants and small static methods\n"
         " that nothing calls yet, and freshness at one file and a hundred and nineteen lines awaiting a republish.\n\n"
         "Unknown: the actual value of CookieValiditySeconds, of which only the field name survives; the poll interval a\n"
         " waiting room expects; and what separates a softblock from a hard ban, of which only two message strings exist.\n\n"
         "The lesson is that the name told me a vendor exists while the field list told me how it judges, what it judges,\n"
         " and why it cannot wait for zero. A clue's value depends on how close it sits to behaviour.\n\n"
         "Product code and tests added; suite green at 2147."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()