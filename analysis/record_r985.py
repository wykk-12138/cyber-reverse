"""Record R985: the status-classification route is exhausted, and I misread a replica-history line as original evidence."""

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
### 状态码分类在字符串层**不可得**，而我把复刻件的历史当成了原版证据（R985）

**R984 留了两条路：取镜像侧证据判「404 各站应是什么」，或把 401/403/429 收进分类器让 23 处改用。
这一轮走第一条，撞到墙；而撞墙的过程中发现自己上一轮读错了一处。**

### ① 状态码分类没有字符串可查

```
ida.py str 403  -> 40 条命中，全是噪声：GUID 片段 · "Build_403" · "10403" · "11403"
ida.py str 429  -> 40 条，第一条是 Metalama 的公钥串
ida.py str 401  -> 40 条，前两条是版本号与 Avalonia 公钥
```

> **原因很直白：状态码分类在代码里是**整数比较**，不产生字符串。
> 所以字符串路线**在原理上**看不见它 —— 不是「这次没找到」。**
> **而唯一带点信息的命中是 `0<SolveCptChallenge>d__39`（一个验证码挑战状态机），
> 那属于「挑战求解」，不属于「状态码分类」。**

**→ 要它必须走代码，而代码路线已经失败两次（R827/R828：字符串无 xref，MethodTable 未通）。**

### ② 而我在 R984 引用过一条「原版分类」

**R984 之后我打算用 `replica/docs/HISTORY.md:1488` 的「状态码分类（401/403 可重试 vs 422 不可）」当原版证据。
读上下文发现它不是。**

**那一节标题是「6.73 空桩填实（R12）」，正文第一句：「R12 审计给出的缺口是 88 个空桩。这一轮把其中 39 个填成真实实现」。**

> **所以那是**复刻件 R12 时自己的实现描述**，不是对原版的观察。**
> **拿它推「原版怎么分类」就是循环论证 —— 与 AGENTS.md §2.2 记的同一类错误
> （「复刻件写出的 settings.json 不能当实机证据」）。**
> **而这一条比那个更滑：它读起来像是在描述原版，因为整节都在讲「我们补齐了什么」。**

### ③ 而它顺手暴露了复刻件的**第三处**自相矛盾

**`StoreFlowRunner.cs:242` 写：**

```csharp
401 => new MonitorResult { Status = MonitorStatus.Blocked, Error = message },
```

**而同一个仓的 `HISTORY.md` 写 401 是可重试的。**

> **两处描述同一个状态码，一处判「终止（Blocked）」，一处判「可重试」。**
> **而 401 本来的意思是「凭据过期」—— 那正是 `RefreshSession` 存在的理由。
> 把它判成终止，等于把刷新会话这条路**提前关掉**。**

**→ 而这一点我**没有**改：改 401 的语义同样是行为变化，同样缺原版证据。**

### ④ 所以这一轮的实际结论是**路线封死**，不是「又找到一个缺陷」

**`HandleBlock` 与「状态码分类」现在共用同一个墙：**

| 要的东西 | 字符串层 | 代码层 |
|---|---|---|
| `HandleBlock` 的实现 | 名字在，但只给位置不给内容 | 无 xref · MethodTable 未通 |
| 状态码分类 | **原理上不可得**（整数比较无字符串） | 同上 |

> **所以这两条不该再各占一轮。它们是一个阻塞：**在原版里，名字能不能落到代码上**。**

### 数字

| 度量 | R984 | **R985** |
|---|---|---|
| 套件 | 2203 | **2203（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 变异 36/36 | 是 | **是** |
| **`!IsSuccess`→Blocked 的点** | 23 | **23（守卫钉着）** |
| **原版状态码分类的证据** | 未测 | **字符串层不可得** |

### 教训

> **「读起来像在描述原版」和「是在描述原版」是两件事，而我的判断靠的是语的语气。
> 那一节的语气全是第三人称客观陈述，而它描述的是**我们自己的**一次改动。**
> **更省事的判据是看标题和第一句说主语是谁 —— 「R12 把 39 个填成真实实现」，主语是我们。**
"""

if "状态码分类在字符串层**不可得**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 985 轮：状态码分类在字符串层不可得，而我把复刻件的历史当成了原版证据

### ① 没有字符串可查

```
ida.py str 403  -> 40 条，全是噪声：GUID 片段 · "Build_403" · "10403" · "11403"
ida.py str 429  -> 第一条是 Metalama 公钥串
ida.py str 401  -> 前两条是版本号与 Avalonia 公钥
```

> **状态码分类在代码里是**整数比较**，不产生字符串 → 字符串路线**原理上**看不见它，
> 不是「这次没找到」。要它必须走代码，而代码路线已失败两次（R827/R828）。**

### ② 而我在 R984 后打算引用的一条，读上下文发现不是原版证据

**`replica/docs/HISTORY.md:1488`「状态码分类（401/403 可重试 vs 422 不可）」——
那一节标题是「6.73 空桩填实（R12）」，第一句「R12 审计给出的缺口是 88 个空桩。这一轮把其中 39 个填成真实实现」。**

> **那是**复刻件 R12 自己的实现描述**。拿它推原版就是循环论证 —— §2.2 同一类错误。
> 而它比 §2.2 更滑：整节都在讲「我们补齐了什么」，语气全是客观陈述，读起来像在描述原版。**

### ③ 而它顺手暴露了第三处自相矛盾

```csharp
// StoreFlowRunner.cs:242
401 => new MonitorResult { Status = MonitorStatus.Blocked, Error = message },
```

**而同一个仓的 `HISTORY.md` 说 401 可重试。**

> **401 的意思是「凭据过期」—— 那正是 `RefreshSession` 存在的理由。
> 把它判成终止，等于把刷新会话这条路**提前关掉**。**
> **这一点我**没有**改：改 401 语义同样是行为变化，同样缺原版证据。**

### ④ 实际结论是**路线封死**

| 要的东西 | 字符串层 | 代码层 |
|---|---|---|
| `HandleBlock` 的实现 | 名字在，只给位置不给内容 | 无 xref · MethodTable 未通 |
| 状态码分类 | **原理上不可得**（整数比较） | 同上 |

> **这两条不该再各占一轮 —— 它们是一个阻塞：**在原版里，名字能不能落到代码上**。**

### 数字

| 度量 | R984 | **R985** |
|---|---|---|
| 套件 | 2203 | **2203（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| `!IsSuccess`→Blocked 的点 | 23 | **23（守卫钉着）** |
| **原版状态码分类的证据** | 未测 | **字符串层不可得** |

### 教训

> **「读起来像在描述原版」和「是在描述原版」是两件事，而我的判断靠的是语气。
> 更省事的判据是看标题和第一句的主语是谁 —— 「R12 把 39 个填成真实实现」，主语是我们。**
"""

BACKLOG_ADD = """

## 优先级 ② — **状态码分类字符串层不可得；`HISTORY.md` 那条是复刻件历史不是原版证据**（R985）

### ① 字符串路线封死

```
ida.py str 403/429/401 -> 全是噪声（GUID、Build_403、10403、Metalama 公钥、版本号）
```

**原因：状态码分类是**整数比较**，不产生字符串 → 原理上不可得，不是「这次没找到」。**

### ② 自我更正

**`HISTORY.md:1488`「状态码分类（401/403 可重试 vs 422 不可）」属于「6.73 空桩填实（R12）」一节，
即**复刻件自己的实现描述**。拿它推原版 = 循环论证（§2.2 同一类）。**

### ③ 顺手发现的第三处矛盾

**`StoreFlowRunner.cs:242` 把 `401` 判 `Blocked`（终止）；而 `HISTORY.md` 说 401 可重试。
401 = 凭据过期，正是 `RefreshSession` 的理由 → 判终止等于提前关掉刷新会话。**
**未改：改 401 语义同样缺原版证据。**

### ④ 一个阻塞，不是两条待办

| 要的东西 | 字符串层 | 代码层 |
|---|---|---|
| `HandleBlock` 的实现 | 名字在，只给位置 | 无 xref · MethodTable 未通 |
| 状态码分类 | **原理上不可得** | 同上 |

**→ **在原版里，名字能不能落到代码上** —— 这是同一个墙。**

### 数字

**套件 2203（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 混淆点 23（守卫钉着）**

| 仍 Unknown | |
|---|---|
| 原版状态码分类 | 字符串层不可得；代码层未通 |
| `HandleBlock` 实现 | 同上 |

**纪律**：「读起来像在描述原版」靠的是语气；看主语是谁才靠得住。
"""

BLOCKER = """

---

## 409. **状态码分类字符串层不可得；`HISTORY.md` 那条是复刻件历史，不是原版证据**

> R985。**只取证 + 一处自我更正，未改代码。** 套件 **2203（R984 的记录仍有效）**。

### 一、字符串路线封死

```
ida.py str 403  -> 40 条，全是噪声：GUID 片段 · "Build_403" · "10403" · "11403"
ida.py str 429  -> 第一条是 Metalama 公钥串
ida.py str 401  -> 前两条是版本号与 Avalonia 公钥
```

**原因直白：状态码分类在代码里是**整数比较**，不产生字符串。
所以字符串路线**在原理上**看不见它 —— 不是「这次没找到」。**

**唯一带点信息的命中是 `0<SolveCptChallenge>d__39`，那属于「挑战求解」，不属于「状态码分类」。**

**→ 要它必须走代码；代码路线已失败两次（R827/R828：字符串无 xref，MethodTable 未通）。**

### 二、自我更正：一条被误读为原版证据的复刻件历史

**`replica/docs/HISTORY.md:1488` 写「状态码分类（401/403 可重试 vs 422 不可）」。
那一节标题是「6.73 空桩填实（R12）」，第一句：「R12 审计给出的缺口是 88 个空桩。这一轮把其中 39 个填成真实实现」。**

**→ 那是**复刻件 R12 自己的实现描述**，不是对原版的观察。拿它推原版 = 循环论证（§2.2 同一类）。
→ 而它比 §2.2 那条更滑：整节都在讲「我们补齐了什么」，语气全是客观陈述，**读起来像在描述原版**。**

### 三、而它顺手暴露了第三处自相矛盾

```csharp
// src/Cybersole.Stores/StoreFlowRunner.cs:242
401 => new MonitorResult { Status = MonitorStatus.Blocked, Error = message },
```

**而同一个仓的 `HISTORY.md` 说 401 可重试。**

**→ 401 的意思是「凭据过期」，那正是 `RefreshSession` 存在的理由。
把它判成终止，等于把刷新会话这条路**提前关掉**。**

**→ 未改：改 401 的语义同样是行为变化，同样缺原版证据。**

### 四、这两条是一个阻塞，不是两条待办

| 要的东西 | 字符串层 | 代码层 |
|---|---|---|
| `HandleBlock` 的实现 | 名字在，但只给位置不给内容 | 无 xref · MethodTable 未通 |
| 原版状态码分类 | **原理上不可得**（整数比较无字符串） | 同上 |

**→ 共同点：**在原版里，名字能不能落到代码上**。**

### 五、数字

| 度量 | R984 | R985 |
|---|---|---|
| 套件 | 2203 | **2203（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 变异 36/36 | 是 | **是** |
| `!IsSuccess`→Blocked 的点 | 23 | **23（守卫钉着）** |
| **原版状态码分类的证据** | 未测 | **字符串层不可得** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str 403   -> 40 条噪声
python analysis/ida.py str 429   -> 40 条，第一条 Metalama 公钥
python analysis/ida.py str 401   -> 40 条，版本号 / Avalonia 公钥
python -c "读 replica/docs/HISTORY.md 第 1483-1499 行"  -> 标题「6.73 空桩填实（R12）」
```

### 七、仍然 Unknown

- **原版状态码分类**：**Unknown** —— 字符串层不可得，代码层未通。
- **`HandleBlock` 的实现**：**Unknown** —— 同上。

### 八、教训

**「读起来像在描述原版」和「是在描述原版」是两件事，而我的判断靠的是语气。**

**更省事的判据是看标题和第一句的主语是谁 —— 「R12 把 39 个填成真实实现」，主语是我们。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R985", BLOCKER)
    ensure(RSTATUS, "R985", BLOCKER)
    ensure(RVERDICT, "第 985 轮", VERDICT)
    ensure(BACKLOG, "R985", BACKLOG_ADD)

    note = (
        "\n## R985 补充 — **状态码分类字符串层不可得；`HISTORY.md` 那条是复刻件历史不是原版证据**（套件 2203）\n\n"
        "① `ida.py str 403/429/401` 全是噪声（GUID、`Build_403`、`10403`、Metalama 公钥、版本号）。\n"
        "原因：状态码分类是**整数比较**，不产生字符串 → 字符串路线**原理上**不可得。要它得走代码，而已失败两次。\n\n"
        "② **自我更正**：`HISTORY.md:1488`「状态码分类（401/403 可重试 vs 422 不可）」属于「6.73 空桩填实（R12）」一节，\n"
        "是**复刻件自己的实现描述**，不是原版观察。拿它推原版 = 循环论证（§2.2 同类）。\n\n"
        "③ 顺手暴露第三处矛盾：`StoreFlowRunner.cs:242` 把 `401` 判 `Blocked`（终止），而 `HISTORY.md` 说 401 可重试。\n"
        "401 = 凭据过期，正是 `RefreshSession` 的理由 → 判终止等于提前关掉刷新会话。**未改**（同样缺原版证据）。\n\n"
        "④ 结论：`HandleBlock` 与「状态码分类」**共用一个阻塞** —— 在原版里名字能不能落到代码上。\n"
        "   两条不该再各占一轮。\n\n"
        "数字：套件 2203（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 混淆点 23（守卫钉着）。\n\n"
        "纪律：**「读起来像在描述原版」靠的是语气；看主语是谁才靠得住。**\n\n"
        "下一轮：换一条不靠名字定位的核心工作 —— 判据 (f) 的镜像→复刻件方向，或 flow 级别的行为证据。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R985" not in h:
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
             for p, k in ((RBLOCK, "R985"), (RSTATUS, "R985"), (RVERDICT, "第 985 轮"), (BACKLOG, "R985")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R985: status classification is not in the strings, and I misread replica history as original evidence\n\n"
         "R984 left two routes: get original-side evidence for what a 404 means at each store, or collect 401/403/429 into\n"
         " one classifier. This round took the first and hit a wall, and hit a reading error on the way.\n\n"
         "There is nothing to find. Searching the image for 403, 429 and 401 returns forty matches each and every one is\n"
         " noise: GUID fragments, a Build_403 label, 10403 and 11403, a Metalama public key, a version string. Status\n"
         " classification is integer comparison in code and produces no strings, so the string route cannot see it in\n"
         " principle, not merely this time. Reaching it needs code, and the code route failed twice already.\n\n"
         "The reading error matters more. I had intended to cite HISTORY.md for the claim that 401 and 403 are retryable\n"
         " while 422 is not. Reading its context shows the line sits under the heading for round 12's stub-filling, whose\n"
         " first sentence says round 12 took thirty-nine of eighty-eight stubs and gave them real implementations. So it\n"
         " describes what the replica did, not what the original does. Reasoning from it to the original is circular, the\n"
         " same error section 2.2 records about the replica's own settings files -- and slipperier, because the whole section\n"
         " is written in flat third person and reads like an account of the original.\n\n"
         "It also exposed a third internal contradiction. StoreFlowRunner maps 401 to Blocked, a terminal outcome, while the\n"
         " same repository's history calls 401 retryable. A 401 means the credential expired, which is precisely why\n"
         " RefreshSession exists; treating it as terminal closes that path before it can run. That is not changed either,\n"
         " because changing 401's meaning is a behaviour change and needs the same evidence nobody has.\n\n"
         "So the real result is that two items are one blocker. Whether the original's names can be made to reach its code\n"
         " governs both HandleBlock's implementation and its status classification, and they should stop taking a round each.\n\n"
         "Figures: suite 2203 unchanged, freshness zero, count 173,952, twenty-three conflated block sites still pinned.\n\n"
         "Unknown: the original's status classification, unavailable in the strings and unreached in the code; and\n"
         " HandleBlock's implementation, likewise.\n\n"
         "The lesson is that reading like a description of the original is not the same as being one, and my test for it was\n"
         " tone. Checking who the subject of the first sentence is costs nothing: round 12 did the filling, so the subject was\n"
         " us.\n\n"
         "No product code changed; one correction recorded."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()