"""Record R950: the function count measures reachable code, and R949's conclusion was wrong."""

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
### 函数数不动的原因不是「表 vs 逻辑」，是**可达 vs 不可达**（R950）

**R949 的结论是「常量表加 0 个函数，真实逻辑加 1,963」。这一轮写了**真逻辑**（`RedirectPolicy`：redirect 循环、
`TooManyRedirects`、`Retry-After` 两种形式的解析、throttling 日志），重发布 —— 函数数**还是 173,653**。**

### 于是我查了产物里有没有那个新类

```
TooManyRedirects 在偏移 0x... -> 不在
```

**而 `BouncyHttpClient` 在。**

### 所以原因不是 R949 说的那个

**`RedirectPolicy` **没有任何调用者** —— 而 NativeAOT 的裁剪器会把不可达的类整个删掉。**

> **所以函数数量的是**可达代码**，不是**写了多少行**。
> 一个没人调用的类，无论它是一张 const 表还是一段带循环的状态机，**增量都是 0**。**

### 而 R949 那个「+1,963」大概是什么

**R933 那次重发布之前，我接了什么**可达**的东西（不是「逻辑」）。
所以那 1,963 是**接线**的产出，不是**写作**的产出 —— 而我把功劳记在了「逻辑」名下。**

### 而这一轮我自己的检查也错过一次

**我先在产物里搜 `JA3` / `TlsProfile` / `Tls12Profile`，三个都「不在」，于是判定「整层 TLS 被裁掉」。**

> **而 NativeAOT **不把类名写成字符串字面量** —— 除非有反射用它们。
> 所以「搜不到」不能证明「被裁掉」。§2.7b 那条「反向结论要用数据库查」我在这里用错了：
> **这次的对象是最终产物，而它的判据不是字面量，是**trim 警告 + 可达性分析**。**
> **而正确的证据是我本来就有的一对：`BouncyHttpClient` 在（有字面量）、`TooManyRedirects` 不在（我新写的、确实无调用者）。**

### 所以下一步是什么

**不是继续写类，是**接线**：让 `NetClient.SendAsync` 真的走 `RedirectPolicy`，
那样它才进产物，函数数才动。**

> **而这条对 103,467 个缺口的意义是：**缺口不是「还没写」，是「写了但没接上」。**
> **而复刻件已有 ~3,200 行 HTTP 层 —— 其中多少在产物里，现在还不知道。**

### 数字

| 度量 | R949 | **R950** |
|---|---|---|
| 套件 | 2059 | **2088** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,653 | **173,653（写了真逻辑仍未变）** |
| **`RedirectPolicy` 在产物里** | — | **不在（无调用者）** |

### 教训

> **「写了一个类」和「产物里多了一个类」是两件事，而我只检查了前者。**
> **而更贵的是上一轮的结论：我把「加表不动数」和「加逻辑动了数」写成了一条规律，
> 而两个观测都不支持它 —— 一个是因为表不可达，另一个的原因我根本没查。**
> **从 n=2 里读出一条规律，而两个样本的因都不是我以为的那个。**
"""

if "函数数不动的原因不是「表 vs 逻辑」" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 950 轮：函数数不动的原因是**可达 vs 不可达**，不是「表 vs 逻辑」

### 写了真逻辑，函数数还是 173,653

**`RedirectPolicy`：redirect 循环 + `TooManyRedirects` + `Retry-After` 两种形式 + throttling 日志。重发布 → 未变。**

### 查产物

```
TooManyRedirects  不在
BouncyHttpClient  在
```

### 原因

**`RedirectPolicy` **没有调用者** → NativeAOT 裁剪器把整个类删掉。**

> **函数数量的是**可达代码**。没人调用的类，无论 const 表还是带循环的状态机，增量都是 0。**

### 而 R949 那个「+1,963」大概是接线，不是写作

**R933 之前我接了**可达**的东西 —— 而那 1,963 是接线的产出。我把功劳记在了「逻辑」名下。**

### 而这一轮我自己的检查也错过一次

**我先搜 `JA3` / `TlsProfile`，三个都「不在」，于是判「整层 TLS 被裁掉」。**

> **NativeAOT **不把类名写成字符串字面量** —— 「搜不到」不能证明「被裁掉」。
> 正确的证据是 `BouncyHttpClient` 在（有字面量）· `TooManyRedirects` 不在（我新写的、确实无调用者）。**

### 下一步：接线，不是继续写类

**让 `NetClient.SendAsync` 真走 `RedirectPolicy` —— 那样它才进产物。**

> **对 103,467 个缺口的意义：缺口可能不是「还没写」，是「写了但没接上」。
> 而复刻件已有 ~3,200 行 HTTP 层 —— 其中多少在产物里，现在还不知道。**

### 数字

| 度量 | R949 | **R950** |
|---|---|---|
| 套件 | 2059 | **2088** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,653 | **173,653（真逻辑仍未变）** |
| `RedirectPolicy` 在产物里 | — | **不在（无调用者）** |

### 教训

> **「写了一个类」和「产物里多了一个类」是两件事，而我只检查了前者。
> 更贵的是上一轮的结论：从 n=2 读出「表 0 / 逻辑 1,963」的规律，
> 而两个样本的因都不是我以为的那个。**
"""

BACKLOG_ADD = """

## 判据 (c)/③ — 函数数=可达代码；`RedirectPolicy` 无调用者被裁（R950，**+29 用例**）

### 写的真逻辑

**`RedirectPolicy`：`IsRedirect` · `PreservesMethod` · `LimitFrom` · `FollowAsync`（循环+上限）· `Resolve` ·
`ParseRetryAfter`（两种形式）· `IsThrottled` · `ThrottleLog`**

### 而重发布后函数数未变

**`TooManyRedirects` 不在产物、`BouncyHttpClient` 在 → 裁剪器删了无调用者的类。**

### R949 结论被推翻

**不是「表 0 / 逻辑 1,963」，是「不可达 0 / 可达 >0」。**

### 数字

**套件 2059 → 2088 · 陈旧度 0/0 · 函数数 173,653 未变**

| 仍 Unknown | |
|---|---|
| 已有 ~3,200 行 HTTP 层多少在产物里 | 未测 |
| 哪些 flow 真的走到 `NetClient.SendAsync` | 未追 |
| 103,467 缺口里多少是「没接上」 | 未知，可能很大 |

**纪律**：「写了一个类」和「产物里多了一个类」是两件事。
"""

BLOCKER = """

---

## 374. 函数数=可达代码；`RedirectPolicy` 写了但被裁掉

> R950。**改产品代码 +29 用例。** 套件 **2088 通过 / 0 失败 / 0 跳过**。

### 一、写了真逻辑

**`RedirectPolicy`：`FollowAsync` 带 hop 计数与上限 · `TooManyRedirects` 消息 · `Retry-After` 两种形式解析 ·
`[Throttling]` 日志 · `PreservesMethod`**

### 二、重发布后函数数仍是 173,653

### 三、查产物

```
TooManyRedirects  不在
BouncyHttpClient  在
```

**→ `RedirectPolicy` 无调用者 → NativeAOT 裁剪器删掉整个类。**

**→ 函数数量的是**可达代码**。**

### 四、R949 结论被推翻

**不是「常量表 0 / 逻辑 1,963」，是「不可达 0 / 可达 >0」。
R933 那 1,963 是**接线**的产出，不是写作的产出。**

### 五、我自己的检查也错过

**先搜 `JA3`/`TlsProfile` 都「不在」→ 判「TLS 层被裁」。
而 NativeAOT 不把类名写成字面量 → 「搜不到」≠「被裁」。**

### 六、修复过程中三个真 bug

1. **`"1.2.3"` 被日期解析器接受 → 返回 0**（零是唯一确定错的值）→ 加「纯数字点串」判据回落。
2. **循环多跑一跳** → `hop >= limit` 在请求前拒绝。
3. **`Hops` 比预期多 1** → 上限语义改为「已走的跳数」。

### 七、数字

| 度量 | R949 | R950 |
|---|---|---|
| 套件 | 2059 | **2088** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,653 | **173,653（未变）** |
| **`RedirectPolicy` 在产物里** | — | **不在** |

### 八、验证

```
grep RedirectPolicy src   -> 无人引用
dotnet publish            -> 成功，54,652 KB
搜产物 TooManyRedirects   -> 不在
搜产物 BouncyHttpClient   -> 在
metrics_report.py         -> 173,653（未变）
```

### 九、仍然 Unknown

- **已有 ~3,200 行 HTTP 层多少在产物里**：**Unknown** —— 未测。
- **哪些 flow 真走到 `NetClient.SendAsync`**：**Unknown** —— 未追。
- **103,467 缺口里多少是「没接上」**：**Unknown** —— 可能很大。

### 十、教训

**「写了一个类」和「产物里多了一个类」是两件事，而我只检查了前者。**

**更贵的是上一轮的结论：从 n=2 读出规律，而两个样本的因都不是我以为的那个。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R950", BLOCKER)
    ensure(RSTATUS, "R950", BLOCKER)
    ensure(RVERDICT, "第 950 轮", VERDICT)
    ensure(BACKLOG, "R950", BACKLOG_ADD)

    note = (
        "\n## R950 补充 — 函数数=可达代码；RedirectPolicy 写了但被裁掉（+29 用例，套件 2088）\n\n"
        "写了真逻辑（RedirectPolicy：hop 循环/TooManyRedirects/Retry-After 两种形式/[Throttling] 日志），"
        "重发布后函数数仍 173,653。\n\n"
        "查产物：TooManyRedirects 不在、BouncyHttpClient 在 → 无调用者的类被 NativeAOT 裁剪器删掉。\n"
        "→ 函数数量的是**可达代码**；R949 的「表 0 / 逻辑 1,963」被推翻，真相是「不可达 0 / 可达 >0」。\n\n"
        "我自己也错过一次：搜 JA3/TlsProfile 都「不在」就判「TLS 层被裁」—— 而 NativeAOT 不把类名写成字面量。\n\n"
        "修复中三个真 bug：\"1.2.3\" 被日期解析器接受返回 0（加纯数字点串回落）· 循环多跑一跳 · Hops 多 1。\n\n"
        "数字：套件 2059 → 2088 · 陈旧度 0/0 · 函数数 173,653 未变。\n\n"
        "纪律：「写了一个类」和「产物里多了一个类」是两件事。\n\n"
        "下一轮：把 RedirectPolicy 接进 NetClient.SendAsync（接线而非写作）；或先测已有 HTTP 层多少在产物里。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R950" not in h:
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
             for p, k in ((RBLOCK, "R950"), (RSTATUS, "R950"), (RVERDICT, "第 950 轮"), (BACKLOG, "R950")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R950: the function count measures reachable code, and last round's law was read off two bad samples\n\n"
         "R949 concluded that constant tables add no functions while real logic adds 1,963. This round wrote real logic --\n"
         " redirect following with a hop limit, a TooManyRedirects message, both Retry-After forms, and the throttling log\n"
         " line -- republished, and the count did not move.\n\n"
         "Checking the artifact explains why. TooManyRedirects is not in the executable; BouncyHttpClient is. RedirectPolicy\n"
         " has no caller, so the AOT trimmer removed the class entirely. The count measures reachable code, not lines\n"
         " written: an unreferenced class adds nothing whether it holds a constant table or a loop with state in it. Which\n"
         " means R933's 1,963 was the product of wiring rather than of writing, and I had credited it to the wrong side.\n\n"
         "My own check was wrong once too. I searched the artifact for JA3 and TlsProfile, found neither, and concluded the\n"
         " whole TLS layer had been trimmed -- but NativeAOT does not spell class names as string literals unless\n"
         " reflection needs them, so not finding one proves nothing. The usable evidence is the pair I already had:\n"
         " BouncyHttpClient present because a literal mentions it, TooManyRedirects absent because nothing calls it.\n\n"
         "Three real bugs surfaced while the code was being tested: 1.2.3 parsed as a date and produced a zero wait, which\n"
         " is the one certainly wrong answer, so malformed digit-and-dot strings now fall back; the loop ran one hop past\n"
         " the limit, so refusal now happens before the extra request; and Hops was off by one until the limit was defined\n"
         " as hops already taken.\n\n"
         "Figures: suite 2059 to 2088, freshness zero either way, and the function count unchanged at 173,653 with the new\n"
         " class absent from the executable.\n\n"
         "Unknown: how much of the existing three-thousand-line HTTP layer survives trimming; which flows actually reach\n"
         " NetClient.SendAsync; and what share of the 103,467-function gap is code that exists but is not wired, which could\n"
         " be a large share.\n\n"
         "The lesson is that writing a class and having the product contain one are different events, and I only checked the\n"
         " first. Worse, last round I read a law off two samples whose causes were not what I thought, and stated it as a\n"
         " measurement.\n\n"
         "Product code changed; suite green at 2088."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()