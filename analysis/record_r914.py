"""Record R914: the WebRTC surface, the fifth of its kind, and the false positive it caused."""

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
### 第五个表面：WebRTC —— 而它不是「报告一个值」，是「不报告一个地址」（R914）

**R913 说补变体前要先知道每个变体差什么。从名字最清楚的一组开始：指纹四个。**

### 先查那四个

| 名字 | 复刻件 |
|---|---|
| `SubmitFingerprint` | 概念在（`BrowserIdentity` / `BrowserFingerprint`） |
| `SubmitClientData` | 概念在（`KasadaSolver.cs` 的 `ClientData`） |
| `SubmitBrowserData` | 概念在（`AppPaths.cs` 的 `BrowserData`） |
| **`SubmitWebRtc`** | **完全没有** |

**所以四个里三个只是名字不同，一个是真缺。**

### 而 `Scripts/` 里有 57 个文件，其中五个「表面」

`CanvasSurface` · `WebGlSurface` · `FontMediaSurface` · `MediaQuerySurface` · `VoiceTable` ——
**加上 `WebAssemblySurface` · `NavigatorCensus` · `WindowBaseline` 等。**

**它们都是「让浏览器报告一个和 persona 一致的值」。而 WebRTC 不同：**

> **它不报告值，它**打开通道**，而通道会用网络地址回答。
> 页面构造一个 offer、收集 ICE candidate，就能读到本机私有地址，并且在没有强制中继时读到公网地址。
> **挂代理时，那两个地址正是代理存在的理由。**

### 所以姿态是反的

| 其他表面 | WebRTC |
|---|---|
| 报告一个**必须与 persona 一致**的值 | **不报告 persona 没声称过的地址** |

**两类泄漏：`host` candidate（私有地址，或 Chromium 的 mDNS 名 —— 不指名地址但每台机器稳定，仍能关联会话）与
`srflx` candidate（问 STUN 服务器「我这个源地址看起来是什么」，挂代理时是代理地址，不挂时是真公网地址）。**

### 写了 `WebRtcSurface.cs`

**`Rule` · `CandidateLeaks` · `BodyJs()` · `RequiredFor(bool behindProxy)`，与其他 surface 同形。**

**而 `BodyJs()` 关的是**两半**：**

1. `onicecandidate` 事件里过滤掉 `srflx`/`host`
2. `localDescription` 的 getter 里把同样的 candidate 从 SDP 剥掉

> **只关第一半，直接读 `localDescription.sdp` 的页面仍然看得见。
> 两个同类 surface 的注释里都写过「两半都得对，不是一半」（`matchMedia` 的 `.media` 与 `.matches`）——
> 这里是同一句话的另一个实例。**

**而连接仍然可构造：`Wrapped.prototype = PC.prototype` 且 `Object.setPrototypeOf(Wrapped, PC)`。
**让 `RTCPeerConnection` 抛错会和泄漏一样容易被检出。****

### 6 个用例

`BothCandidateKindsAreNamed` · **`BothHalvesOfTheLeakAreClosed`** · `TheConnectionRemainsConstructible` ·
`ItDoesNothingWhenTheApiIsAbsent` · `TheGuardIsOnlyRequiredBehindAProxy` · `TheRuleStatesTheReasoningRatherThanAClaim`

### 数字，以及一个我必须说清的 +1

| 度量 | R913 | **R914** |
|---|---|---|
| 套件 | 1815 | **1821** |
| 异步覆盖 | 371（24.0%） | **372（24.0%）** |

**那个 +1 是 `SubmitWebRtc` 被算成「有了」—— 而它只出现在我写的**文档注释**里
（「The image names `<c>SubmitWebRtc</c>`」）。**

**所以 `async_method_coverage.py` 会把**文档里提到的名字**算作实现。这是一个已知的假阳性，
而它在**注释引用镜像名字**这种写法下必然出现 —— 而那种写法正是我一直在用的。**

**下一轮该修的是这个：扫描应排除注释，或至少分开统计「出现在代码里」与「只出现在注释里」。**
"""

if "第五个表面：WebRTC" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R914 appended")

VERDICT = """

---

## 第 914 轮：第五个表面 WebRTC —— 而它的姿态是反的

### 先查指纹四个

| 名字 | 复刻件 |
|---|---|
| `SubmitFingerprint` | 概念在（`BrowserIdentity`） |
| `SubmitClientData` | 概念在（`KasadaSolver.cs`） |
| `SubmitBrowserData` | 概念在（`AppPaths.cs`） |
| **`SubmitWebRtc`** | **完全没有** |

**三个只是名字不同，一个是真缺。**

### 而 `Scripts/` 里已有五个同类表面

`CanvasSurface` · `WebGlSurface` · `FontMediaSurface` · `MediaQuerySurface` · `VoiceTable`

**它们都是「让浏览器报告一个与 persona 一致的值」。WebRTC 不同：**

> **它不报告值，它打开通道，而通道用网络地址回答。
> `host` candidate 给私有地址（或每机器稳定的 mDNS 名），`srflx` candidate 给公网地址 ——
> **挂代理时那两个地址正是代理存在的理由。**

### 写了 `WebRtcSurface.cs`

**`BodyJs()` 关两半：`onicecandidate` 过滤 + `localDescription` 的 SDP 剥离。**

> **只关第一半，直接读 SDP 的页面仍看得见。
> `MediaQuerySurface` 的注释写过「两半都得对，不是一半」（`.media` 与 `.matches`）——
> 这里是同一句话的另一个实例。**

**而连接仍可构造（`Wrapped.prototype = PC.prototype`）—— 让 `RTCPeerConnection` 抛错会和泄漏一样容易被检出。**

### 数字，以及一个我必须说清的 +1

| 度量 | R913 | **R914** |
|---|---|---|
| 套件 | 1815 | **1821** |
| 异步覆盖 | 371 | **372** |

> **那个 +1 是 `SubmitWebRtc` 被算成「有了」—— 而它只出现在我写的**文档注释**里。
> 所以 `async_method_coverage.py` 把**注释里提到的名字**算作实现。
> 这是已知假阳性，而在「注释引用镜像名字」这种写法下必然出现 —— 而那种写法我一直在用。**

### 教训

> **这一轮加了一个真表面（WebRTC 防护），同时给自己的度量工具制造了一个假阳性。**
> **两件事都真实：产品多了一个表面，而覆盖数多了一个不该多的名字。**
> **如果我只报「372，涨了 1」，那个 1 会被当成进展。**
"""

BACKLOG_ADD = """

## 优先级 ③ — WebRTC 表面（R914，**改产品代码 +6 用例**）

### 指纹四个的实况

**`Fingerprint` / `ClientData` / `BrowserData` 概念在（不同名字）· **`WebRtc` 真缺**。**

### 已写 `WebRtcSurface.cs`

**`Rule` · `CandidateLeaks` · `BodyJs()` · `RequiredFor(behindProxy)` —— 与五个同类表面同形。**
**`BodyJs()` 关两半：`onicecandidate` 过滤 + `localDescription` SDP 剥离。连接仍可构造。**

### 数字

**套件 1815 → 1821 · 异步覆盖 371 → 372**

### 而那个 +1 是假阳性（必须写明）

**`SubmitWebRtc` 只出现在**文档注释**里，被文本扫描算成「有」。
→ `async_method_coverage.py` 把注释里提到的名字算作实现；而「注释引用镜像名字」是我一直在用的写法。**

| 仍 Unknown | |
|---|---|
| 原版 `SubmitWebRtc` 是拦、伪装还是只记录 | 名字不说 |
| 注释假阳性有多少个 | **未测** —— 下一轮该分开统计 |

**纪律**：**加一个真东西的同时可能给度量制造一个假的东西；只报总数会把两者混在一起。**
"""

BLOCKER = """

---

## 338. WebRTC 表面（第五个同类表面）；以及一个 +1 的假阳性

> R914。**改产品代码 +6 用例。** 套件 **1821 通过 / 0 失败 / 0 跳过**。

### 一、指纹四个的实况

| 名字 | 复刻件 |
|---|---|
| `SubmitFingerprint` | 概念在（`BrowserIdentity`） |
| `SubmitClientData` | 概念在（`KasadaSolver.cs` 的 `ClientData`） |
| `SubmitBrowserData` | 概念在（`AppPaths.cs` 的 `BrowserData`） |
| **`SubmitWebRtc`** | **完全没有** |

**三个只是名字不同，一个是真缺。**

### 二、WebRTC 的姿态与同类表面相反

**`Scripts/` 已有 `CanvasSurface` · `WebGlSurface` · `FontMediaSurface` · `MediaQuerySurface` · `VoiceTable` ——
都是「报告一个与 persona 一致的值」。**

**WebRTC 不报告值，它**打开通道**，而通道用网络地址回答：
`host` 给私有地址（或每机稳定的 mDNS 名）· `srflx` 给公网地址 —— 挂代理时那两个地址正是代理存在的理由。**

### 三、`WebRtcSurface.cs`

**`Rule` · `CandidateLeaks` · `BodyJs()` · `RequiredFor(behindProxy)`。
`BodyJs()` 关两半：`onicecandidate` 过滤 + `localDescription` 的 SDP 剥离。
连接仍可构造：`Wrapped.prototype = PC.prototype`。**

### 四、数字与一个假阳性

| 度量 | R913 | R914 |
|---|---|---|
| 套件 | 1815 | **1821** |
| 异步覆盖 | 371 | **372** |

**那个 +1 是 `SubmitWebRtc` 被算成「有了」—— 而它只出现在我写的**文档注释**里。**

**→ `async_method_coverage.py` 把注释里提到的名字算作实现。**
**→ 这是已知假阳性，而在「注释引用镜像名字」这种写法下必然出现 —— 而那种写法我一直在用。**

### 五、验证

```
test --filter WebRtcSurfaceTests -> 6 通过
async_method_coverage.py         -> 372 / 1547（含 1 个注释假阳性）
metrics_report.py                -> 1821 通过 / 0 失败
```

### 六、仍然 Unknown

- **原版 `SubmitWebRtc` 是拦、伪装、还是只记录**：**Unknown** —— 名字不说，这一轮实现的是
  **挂代理的浏览器需要的那个防护**，并把它写成选择而不是原版行为。
- **注释假阳性共有几个**：**Unknown，未测** —— 下一轮该把「出现在代码里」与「只出现在注释里」分开统计。

### 七、教训

**这一轮加了一个真表面，同时给度量工具制造了一个假阳性。**

**两件事都真实：产品多了一个表面，而覆盖数多了一个不该多的名字。**

**如果我只报「372，涨了 1」，那个 1 会被当成进展。
而它实际上是我的工具把我的注释读成了代码。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R914", BLOCKER)
    ensure(RSTATUS, "R914", BLOCKER)
    ensure(RVERDICT, "第 914 轮", VERDICT)
    ensure(BACKLOG, "R914", BACKLOG_ADD)

    note = (
        "\n## R914 补充 — WebRTC 表面（改产品代码 +6 用例，套件 1815→1821）\n\n"
        "指纹四个：Fingerprint/ClientData/BrowserData 概念在（不同名字），SubmitWebRtc 真缺。\n\n"
        "Scripts/ 已有五个同类表面（Canvas/WebGl/FontMedia/MediaQuery/Voice），都是「报告与 persona 一致的值」；"
        "WebRTC 相反 —— 它打开通道，host candidate 给私有地址、srflx 给公网地址，挂代理时那两个正是代理要藏的。\n\n"
        "写了 WebRtcSurface.cs：Rule · CandidateLeaks · BodyJs()（关两半：onicecandidate 过滤 + localDescription SDP 剥离）· "
        "RequiredFor(behindProxy)。连接仍可构造。\n\n"
        "数字：套件 1821 · 异步覆盖 372（含 **1 个假阳性**：SubmitWebRtc 只在文档注释里）。\n\n"
        "下一轮：把「出现在代码里」与「只出现在注释里」分开统计 —— 注释假阳性必然出现在「注释引用镜像名字」这种写法下。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R914" not in h:
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
             for p, k in ((RBLOCK, "R914"), (RSTATUS, "R914"), (RVERDICT, "第 914 轮"), (BACKLOG, "R914")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R914: the fifth surface is WebRTC, whose posture is the opposite of its four siblings\n\n"
         "R913 said variants need reading before they can be added, so this round took the clearest-named group, the four\n"
         " fingerprint names. Three of the four exist under other names -- Fingerprint in BrowserIdentity, ClientData in\n"
         " KasadaSolver, BrowserData in AppPaths -- and SubmitWebRtc exists nowhere.\n\n"
         "The Scripts directory already held five surfaces of one kind: canvas, WebGL, font metrics, media queries and\n"
         " voices. All of them make the browser report a value that must agree with the persona. WebRTC is the opposite\n"
         " kind, because it does not report a value -- it opens channels that answer with network addresses. Host\n"
         " candidates name the private address or an mDNS name stable per machine; srflx candidates name the public\n"
         " address. Under a proxy those are exactly the addresses the proxy exists to hide.\n\n"
         "So WebRtcSurface closes both halves: the icecandidate handler drops srflx and host candidates, and the\n"
         " localDescription getter strips the same lines from the SDP, because a page reading the description directly\n"
         " would otherwise see what the handler suppressed. MediaQuerySurface already records that rule in another form --\n"
         " both halves have to be right, not just .matches -- and this is the same rule in a different place. The\n"
         " connection stays constructible, since making RTCPeerConnection throw would be as detectable as a leak.\n\n"
         "The suite goes from 1815 to 1821. Async coverage goes from 371 to 372, and that single increment is a false\n"
         " positive: SubmitWebRtc is now reported present only because I wrote it inside a doc comment explaining that\n"
         " the image names it. The coverage tool counts names mentioned in comments as implementations, which was always\n"
         " true and which this round's own writing style triggered.\n\n"
         "Unknown: whether the original's SubmitWebRtc blocks, spoofs or merely records, since the name does not say and\n"
         " this surface implements the guard a proxied browser needs while labelling it as a choice; and how many comment\n"
         " false positives exist overall, which was not measured and which the next round should separate out.\n\n"
         "The lesson is that adding something real can add something fake to the measurement in the same move. Product\n"
         " gained a surface and the coverage figure gained a name that should not be there, and reporting only the\n"
         " figure would have turned my own comment into progress.\n\n"
         "Product code changed; suite green at 1821."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()