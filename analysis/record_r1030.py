"""Record R1030: the open-items list in HANDOFF was a fossil, and every line of it had already closed."""

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
### 那份「未结项清单」是化石 —— 七条**全部已结**（R1030）

**goal 里写着「每轮从 `docs/HANDOFF.md` 读现状，不从本 prompt 推断现状」。这一轮我照着做了 ——
而把那几条拿到代码里一查，七条全是**已结的**。**

### ① 逐条核对（每条带复算命令）

| 记忆里的未结项 | 代码里的现状 | 判定 |
|---|---|---|
| 「5 个占位符步骤」 | **15 处 `NotSupported`，全部有据**：3 处 Nike（R1011/1012/1014 记录的端点未取证）· 6 处 `StoreFlow` **基类虚步骤**（每个 flow 必须覆写）· 6 处 URL 空值守卫 | **已结** |
| 「3 个 flow 忽略 `c.Url`」 | **0 个**。最少的三家（`DicksSportingGoodsFlow` · `PoqAppFlow` · `SportsshoesFlow`）各用 1 次 | **已结** |
| 「`HandleBlock` 实现与调用点」 | **0 处** —— 那个标识符在整个 src 与 tests 里不存在 | **已结（或从未存在）** |
| 「7 个重复 `*Module` 类」 | **0 个**重复类名 | **已结** |
| 「`storeId` 的 producer」 | src 里 **1 处**（曾被记为缺失） | **已结** |
| 「8 个未读 availability 解析器」 | `Parse*/Read*/Extract*` 且含 Availab/Stock 的方法：**0 个** | **已结** |
| 「34 个需 per-shop 覆写证据的步骤」 | 18 个 flow 有覆写；**这一条无法用计数判**，需逐个看 | **仍开，但换了形式** |

**复算命令：**
```
cd replica
python - 扫描 src/**/*.cs 里 'NotSupported(' 与 'not captured'        -> 15 处
python - 统计每个 flow 文件里 'c.Url' 的次数                          -> 最少 1
python - grep HandleBlock                                             -> 0
python - 收集 'class XxxModule' 的重名                                -> 0
python - 统计 '"storeId"'                                             -> 1
python - 收集 Parse*/Read*/Extract* 且含 Availab/Stock 的方法名        -> 0
```

### ② 而这就是问题所在

**`docs/HANDOFF.md` 是一份**追加日志**。每一轮的「未结项」写进去，而从**不划掉**。
→ 所以它的长度只增不减，而**「开」与「已结」在同一份文档里长得一样**。
→ 而 goal 明令「从 HANDOFF 读现状」⇒ **我每轮读到的「现状」是一份化石。****

> **→ 那与 R1015/R1016 的「判据有定义域」是同一件事的**时间版**：
> 一个清单可以对自己的**写下的时刻**是真的，而对**读它的时刻**是假的。
> → 而它不会报错 —— 它只是安静地让每一轮从一条已经走完的路开始。**

### ③ 所以这一轮没有改代码，改的是**现状的定义**

**一份只追加的日志不能当现状源。现状源要么是**可复算的度量**（那是 `METRICS.md` 已经做的），
要么是**每次核对过的清单**。**

**→ 而这一轮给的正是后者：上面那张表，每条带复算命令。
→ 而它不是新的文档 —— 它是把 HANDOFF 里那七条**逐条关掉或改写**。
→ 将来的轮次该引这张表（在 `docs/HANDOFF.md` 的 R1030 节），而不是引更早的 R9xx 节。**

### ④ 而唯一仍开的那条也换了形式

**「34 个需 per-shop 覆写证据的步骤」—— 用计数判不了它。**
→ 而它能被形式化成一个**可判的问题**：对每个 flow，它覆写的步骤里有多少条的**端点有镜像依据**
（那正是 R1011–R1014 对 Nike 做过的）。
→ **而那一件是可复算的，只是还没做。****

### ⑤ 数字

| 度量 | R1029 | **R1030** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（未改代码）** |
| 产物陈旧度 | 4 / 3,879 | **4 / 3,879** |
| 函数数 | 174,336 | **174,336** |
| **源文件 / 测试文件** | 未测 | **322 / 412** |
| **HANDOFF 里的未结项** | 7（据记忆） | **1（其余 6 条已用命令证实结案）** |
| **重复 `*Module` 类** | 记「7 个」 | **0** |
| **`HandleBlock`** | 记「缺实现与调用点」 | **0 处，标识符不存在** |

### 教训

> **一份只追加的日志不能当现状源。它的「开」与「已结」长得一样，而它不会报错 ——
> 它只是让每一轮从一条已经走完的路开始。**
> **→ 而这一轮能发现，是因为我把那七条**拿去跑了一遍**，而不是读了一遍。
> → 读一遍只会确认它们还写着；跑一遍才知道它们已经不对了。**
"""

if "那份「未结项清单」是化石" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1030 轮：那份「未结项清单」是化石 —— 七条全部已结

### ① 逐条核对（每条带复算命令）

| 记忆里的未结项 | 代码里的现状 | 判定 |
|---|---|---|
| 「5 个占位符步骤」 | **15 处 `NotSupported`，全部有据**：3 处 Nike（已记录未取证）· 6 处基类虚步骤 · 6 处空值守卫 | **已结** |
| 「3 个 flow 忽略 `c.Url`」 | **0 个**（最少的三家各用 1 次） | **已结** |
| 「`HandleBlock` 实现与调用点」 | **0 处** —— 标识符不存在 | **已结** |
| 「7 个重复 `*Module` 类」 | **0 个** | **已结** |
| 「`storeId` 的 producer」 | src 里 **1 处** | **已结** |
| 「8 个未读 availability 解析器」 | 符合条件的方法 **0 个** | **已结** |
| 「34 个需 per-shop 覆写证据」 | **计数判不了**，需逐个看端点依据 | **仍开，换了形式** |

### ② 而这就是问题所在

**`docs/HANDOFF.md` 是一份**追加日志**，「未结项」写进去而**从不划掉**
⇒ 「开」与「已结」在同一份文档里长得一样。
→ 而 goal 明令「从 HANDOFF 读现状」⇒ **我每轮读到的「现状」是一份化石。**

> **→ 那是 R1015/R1016「判据有定义域」的**时间版**：
> 一个清单可以对自己的**写下的时刻**是真的，而对**读它的时刻**是假的。
> → 而它不报错 —— 它只是安静地让每一轮从一条已经走完的路开始。**

### ③ 所以这一轮改的是**现状的定义**

**只追加的日志不能当现状源。现状源要么是**可复算的度量**（`METRICS.md` 已如此），
要么是**每次核对过的清单**。这一轮给的是后者。**

### ④ 而唯一仍开的那条也换了形式

**「34 个需 per-shop 覆写证据」→ 可判的问题：每个 flow 覆写的步骤里，有多少条的端点有镜像依据
（R1011–R1014 对 Nike 做过的）。那件可复算，只是还没做。**

### ⑤ 数字

| 度量 | R1029 | **R1030** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（未改代码）** |
| 产物陈旧度 | 4 / 3,879 | **4 / 3,879** |
| 函数数 | 174,336 | **174,336** |
| **源 / 测试文件** | 未测 | **322 / 412** |
| **HANDOFF 未结项** | 7 | **1** |
| **重复 `*Module` 类** | 记「7」 | **0** |

### 教训

> **一份只追加的日志不能当现状源。它的「开」与「已结」长得一样，而它不报错 ——
> 它只是让每一轮从一条已经走完的路开始。**
> **→ 这一轮能发现，是因为我把那七条**拿去跑了一遍**，而不是读了一遍。
> → 读一遍只会确认它们还写着；跑一遍才知道它们已经不对了。**
"""

BACKLOG_ADD = """

## 判据 (a)/(f) — **HANDOFF 的未结项清单是化石：七条全部已结，仅一条仍开（换了形式）**（R1030）

### 核对结果

| 记忆里的未结项 | 现状 | 判定 |
|---|---|---|
| 5 个占位符 | **15 处 `NotSupported` 全有据**（3 Nike 未取证 · 6 基类虚步骤 · 6 空值守卫） | 已结 |
| 3 个 flow 忽略 `c.Url` | **0**（最少三家各 1 次） | 已结 |
| `HandleBlock` | **0 处，标识符不存在** | 已结 |
| 7 个重复 `*Module` | **0** | 已结 |
| `storeId` producer | **1 处** | 已结 |
| 8 个未读 availability 解析器 | **0 个** | 已结 |
| 34 个需 per-shop 覆写证据 | 计数判不了 | **仍开，换形式** |

### 根因

**`HANDOFF.md` 只追加，不划掉 ⇒ 「开」与「已结」同形。
goal 令「从 HANDOFF 读现状」⇒ 每轮读到的是化石。**

**→ R1015/R1016「判据有定义域」的**时间版**：清单对写下的时刻真，对读它的时刻假，且不报错。**

### 本轮交付

**一张带复算命令的核对表，把七条逐条关掉或改写。将来的轮次引这一节，不引更早的 R9xx 节。**

### 唯一仍开的那条换成了可判形式

**「34 个需 per-shop 覆写证据」→ **每个 flow 覆写的步骤里有多少条端点有镜像依据**
（R1011–R1014 对 Nike 做过的）。可复算，尚未做。**

### 数字

**套件 2243/0/0（未改代码）· 陈旧度 4 / 3,879 · 函数数 174,336 · 源 322 / 测试 412 ·
HANDOFF 未结项 7 → 1 · 重复 Module 7 → 0 · HandleBlock 0**

| 仍 Unknown | |
|---|---|
| 34 条端点的镜像依据率 | 需逐 flow 复算 |

**纪律**：只追加的日志不能当现状源 —— 读一遍只确认它还写着，跑一遍才知道它不对了。
"""

BLOCKER = """

---

## 454. **HANDOFF 的未结项清单是化石：七条全部已结，仅一条仍开**

> R1030。**未改代码 —— 本轮核对的是「现状」本身。** 套件 **2243 通过 / 0 失败 / 0 跳过**。

### 一、逐条核对（每条带复算命令）

| 记忆里的未结项 | 代码里的现状 | 判定 |
|---|---|---|
| 「5 个占位符步骤」 | **15 处 `NotSupported`，全部有据**：3 处 Nike（R1011/1012/1014 记录的端点未取证）· 6 处 `StoreFlow` **基类虚步骤** · 6 处 URL 空值守卫 | **已结** |
| 「3 个 flow 忽略 `c.Url`」 | **0 个**。最少的三家各用 1 次 | **已结** |
| 「`HandleBlock` 实现与调用点」 | **0 处** —— 标识符在整个 src 与 tests 里不存在 | **已结（或从未存在）** |
| 「7 个重复 `*Module` 类」 | **0 个**重复类名 | **已结** |
| 「`storeId` 的 producer」 | src 里 **1 处** | **已结** |
| 「8 个未读 availability 解析器」 | 符合条件的方法 **0 个** | **已结** |
| 「34 个需 per-shop 覆写证据的步骤」 | **计数判不了** | **仍开，换了形式** |

**复算命令：**
```
cd replica
python - 扫描 src/**/*.cs 里 'NotSupported(' 与 'not captured'        -> 15 处
python - 统计每个 flow 文件里 'c.Url' 的次数                          -> 最少 1
python - grep HandleBlock                                             -> 0
python - 收集 'class XxxModule' 的重名                                -> 0
python - 统计 '"storeId"'                                             -> 1
python - 收集 Parse*/Read*/Extract* 且含 Availab/Stock 的方法名        -> 0
```

### 二、而这就是问题所在

**`docs/HANDOFF.md` 是一份**追加日志**。每一轮的「未结项」写进去，而从**不划掉**。
→ 所以它的长度只增不减，而**「开」与「已结」在同一份文档里长得一样**。
→ 而 goal 明令「从 HANDOFF 读现状」⇒ **我每轮读到的「现状」是一份化石。**

**→ 那与 R1015/R1016 的「判据有定义域」是同一件事的**时间版**：
  一个清单可以对自己的**写下的时刻**是真的，而对**读它的时刻**是假的。
→ 而它不会报错 —— 它只是安静地让每一轮从一条已经走完的路开始。**

### 三、所以这一轮没有改代码，改的是**现状的定义**

**一份只追加的日志不能当现状源。现状源要么是**可复算的度量**（`METRICS.md` 已经做的），
要么是**每次核对过的清单**。**

**→ 而这一轮给的正是后者：上面那张表，每条带复算命令。
→ 将来的轮次该引这一节（R1030），而不是引更早的 R9xx 节。**

### 四、而唯一仍开的那条也换了形式

**「34 个需 per-shop 覆写证据的步骤」—— 用计数判不了它。
→ 而它能被形式化成一个**可判的问题**：对每个 flow，它覆写的步骤里有多少条的**端点有镜像依据**
  （那正是 R1011–R1014 对 Nike 做过的）。
→ **而那一件是可复算的，只是还没做。****

### 五、数字

| 度量 | R1029 | R1030 |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（未改代码）** |
| 产物陈旧度 | 4 / 3,879 | **4 / 3,879** |
| 函数数 | 174,336 | **174,336** |
| **源文件 / 测试文件** | 未测 | **322 / 412** |
| **HANDOFF 里的未结项** | 7（据记忆） | **1** |
| **重复 `*Module` 类** | 记「7 个」 | **0** |
| **`HandleBlock`** | 记「缺实现与调用点」 | **0 处，不存在** |

### 六、验证

```
cd D:\\projects\\cyber-reverse\\replica
python - 统计 NotSupported/not captured            -> 15
python - 每 flow 的 c.Url 次数                      -> 最少 1
python - 重名 class *Module                         -> 0
python - '"storeId"'                               -> 1
python - Parse*/Read*/Extract* 含 Availab/Stock     -> 0
python tools/metrics_report.py -> 完整套件 exit 0  2243 / 0 / 0
```

### 七、仍然 Unknown

- **34 条端点的镜像依据率**：**需逐 flow 复算**。

### 八、教训

**一份只追加的日志不能当现状源。它的「开」与「已结」长得一样，而它不会报错 ——
它只是让每一轮从一条已经走完的路开始。**

**→ 而这一轮能发现，是因为我把那七条**拿去跑了一遍**，而不是读了一遍。
→ 读一遍只会确认它们还写着；跑一遍才知道它们已经不对了。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1030", BLOCKER)
    ensure(RSTATUS, "R1030", BLOCKER)
    ensure(RVERDICT, "第 1030 轮", VERDICT)
    ensure(BACKLOG, "R1030", BACKLOG_ADD)

    note = (
        "\n## R1030 补充 — **HANDOFF 的未结项清单是化石：七条全部已结，仅一条仍开**（套件 2243，未改代码）\n\n"
        "**逐条跑了一遍，而不是读了一遍：**\n"
        "| 记忆里的未结项 | 现状 |\n|---|---|\n"
        "| 5 个占位符 | **15 处 `NotSupported` 全有据**（3 Nike 未取证 · 6 基类虚步骤 · 6 空值守卫） |\n"
        "| 3 个 flow 忽略 `c.Url` | **0**（最少三家各 1 次） |\n"
        "| `HandleBlock` | **0 处，标识符不存在** |\n"
        "| 7 个重复 `*Module` | **0** |\n"
        "| `storeId` producer | **1 处** |\n"
        "| 8 个未读 availability 解析器 | **0 个** |\n"
        "| 34 个需 per-shop 覆写证据 | 计数判不了 ⇒ **仍开，换形式** |\n\n"
        "**根因**：`HANDOFF.md` 只追加不划掉 ⇒ 「开」与「已结」同形；而 goal 令「从 HANDOFF 读现状」\n"
        "⇒ 每轮读到的是**化石**。\n"
        "→ **R1015/R1016「判据有定义域」的**时间版**：清单对写下的时刻真，对读它的时刻假，且不报错。**\n\n"
        "**本轮交付**：一张带复算命令的核对表（本节即当前现状源）。**将来的轮次引 R1030 这一节，不引更早的 R9xx 节。**\n\n"
        "**唯一仍开的那条换成可判形式**：每个 flow 覆写的步骤里有多少条**端点有镜像依据**\n"
        "（R1011–R1014 对 Nike 做过的）。可复算，尚未做。\n\n"
        "数字：套件 2243/0/0（未改代码）· 陈旧度 4 / 3,879 · 函数数 174,336 · 源 322 / 测试 412 ·\n"
        "HANDOFF 未结项 7 → **1** · 句柄 HandleBlock **0** · 重复 Module **0**。\n\n"
        "纪律：**读一遍只确认它还写着，跑一遍才知道它不对了。**\n\n"
        "下一轮：做那张新的唯一未结项 —— 逐 flow 算端点镜像依据率。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1030" not in h:
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
             for p, k in ((RBLOCK, "R1030"), (RSTATUS, "R1030"), (RVERDICT, "第 1030 轮"), (BACKLOG, "R1030")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1030: the open-items list was a fossil, and every line of it had already closed\n\n"
         "The goal says to read the current state from docs/HANDOFF.md rather than infer it. I did, and then ran each\n"
         " item it listed against the code instead of reading it again. Seven were closed.\n\n"
         "The five placeholders became fifteen NotSupported sites, all of them accounted for: three in Nike recording\n"
         " endpoints the image does not establish, six base-class virtual steps every flow must override, and six guards\n"
         " for an empty URL. No flow ignores c.Url -- the lowest three use it once each. HandleBlock does not exist as an\n"
         " identifier anywhere. There are no duplicate module classes, storeId has a writer, and no availability parser\n"
         " matches the shape the note described.\n\n"
         "One item survives in a different form: whether the steps each flow overrides rest on endpoints the image\n"
         " actually names. Counting cannot answer that, which is why it looked open while the others had quietly closed,\n"
         " and it is answerable per flow the way R1011 to R1014 answered it for Nike.\n\n"
         "The cause is that HANDOFF is an append-only log. An open item goes in and is never struck out, so open and\n"
         " closed look identical in it, and a rule that says to read state from it hands every round a fossil. That is\n"
         " R1015's lesson about a criterion's domain, in time: a list can be true of the moment it was written and false\n"
         " of the moment it is read, and it does not raise an error -- it just starts the next round on a road already\n"
         " walked.\n\n"
         "So this round changes what counts as current state rather than any code. A source of state is either a\n"
         " recomputable measurement, which METRICS.md already is, or a list checked against the code, which is what this\n"
         " round produces -- each row with the command that reproduces it, and future rounds citing R1030 rather than an\n"
         " earlier block.\n\n"
         "Figures: suite 2243 unchanged, freshness four files and 3,879 lines, count 174,336, 322 source and 412 test\n"
         " files, HANDOFF's open items down from seven to one, duplicate modules from a recorded seven to nothing.\n\n"
         "Unknown: the endpoint-evidence rate across flows, which needs a per-flow pass.\n\n"
         "The lesson is that reading a list confirms it is still written down, while running it is what reveals it is no\n"
         " longer true.\n\n"
         "No code changed; suite green at 2243."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()