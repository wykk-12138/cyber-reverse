"""Record R933: republished, +1,963 functions, and the freshness measure reads current."""

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
### 重发布：**+1,963** 个函数，61.96% → **62.66%**（R933）

**R932 说下一轮内存够就重发布。这一轮 2.16 GB，够，发布了。**

```
dotnet publish -c Release -r win-x64 -p:PublishAot=true -p:UseSharedCompilation=false -m:1 -o .publish-aot-new
→ exit 0 · 54,652 KB（旧 54,052 KB）· 只有 Jint / DataTable 的 trim 警告
```

### 而 R932 那个度量立刻给出结论

| 度量 | 旧产物 | **新产物** |
|---|---|---|
| 复刻件函数 | 171,690 | **173,653** |
| **比例** | 61.96% | **62.66%** |
| 产物陈旧度 | **59 文件 / 23,815 行** | **0 文件 / 状态 current** |

> **59 个文件、23,815 行换来 **+1,963** 个函数（+0.70 pp）。
> 也就是约**每 12 行代码一个函数** —— 而这个比值本身是个有用的刻度：
> 它说这个项目的代码密度，也说「再涨 1 pp 需要写多少」。**

### 而 1,963 这个数分得清

**R920–R929 六家 vendor 集成 + R926 `KeyGesture` + R930 `ConcurrencyLimit` + R930 的枚举与属性合并 ——
这些是**新函数**。而 +1,963 里有多少是它们、多少是 AOT 把之前内联的边界重新展开，**分不开**。**

> **所以这个数只能说「这一版比上一版多 1,963 个非叶函数」，
> 不能说「我写了 1,963 个函数」。—— 后者会是 R918 那种「净数藏住反向移动」再犯一次。**

### 距离目标还剩多少

| | 数 |
|---|---|
| 原版 | 277,120 |
| 复刻件 | 173,653 |
| **差** | **103,467** |
| 按 12 行/函数估算 | **≈124 万行** |

**这个估算必须标明是估算：12 行/函数是从一个 59 文件的样本得出的，而不同代码类型密度差很多。**

### 数字

| 度量 | R932 | **R933** |
|---|---|---|
| 套件 | 1932 | 1932（待跑） |
| **函数比例** | 61.96% | **62.66%** |
| **产物陈旧度** | 59 / 23,815 | **0 / current** |

### 教训

> **R932 加那个度量的价值，这一轮兑现了：它不只是「提醒可能过期」，
> 它是**一个可以关掉的红灯**。**
> **而关掉它的方式只有一条：重发布。**
> **一个度量如果不能被关掉，它就只是一句抱怨。**
"""

if "重发布：**+1,963** 个函数" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R933 appended")

VERDICT = """

---

## 第 933 轮：重发布 —— +1,963 个函数，61.96% → 62.66%

### 发布

```
dotnet publish -c Release -r win-x64 -p:PublishAot=true -p:UseSharedCompilation=false -m:1
→ exit 0 · 54,652 KB（旧 54,052）· 只有 Jint / DataTable 的 trim 警告
```

### 而 R932 那个度量立刻给出结论

| 度量 | 旧产物 | **新产物** |
|---|---|---|
| 复刻件函数 | 171,690 | **173,653** |
| **比例** | 61.96% | **62.66%** |
| 陈旧度 | 59 文件 / 23,815 行 | **0 / current** |

> **59 个文件、23,815 行换来 +1,963 个函数（+0.70 pp）——
> 约**每 12 行代码一个函数**。这个比值本身是个有用的刻度。****

### 而 1,963 这个数分得清

**六家 vendor 集成 + `KeyGesture` + `ConcurrencyLimit` + 枚举合并是**新函数**；
而其中有多少是它们、多少是 AOT 把之前内联的边界重新展开，**分不开**。**

> **所以只能说「这一版比上一版多 1,963 个非叶函数」，
> 不能说「我写了 1,963 个函数」—— 后者是 R918「净数藏住反向移动」再犯一次。**

### 距离目标

| | 数 |
|---|---|
| 原版 | 277,120 |
| 复刻件 | 173,653 |
| **差** | **103,467** |
| 按 12 行/函数估算 | **≈124 万行**（估算，样本只有 59 文件） |

### 教训

> **R932 那个度量不只是「提醒可能过期」，它是**一个可以关掉的红灯**。
> 而关掉它的方式只有一条：重发布。**
> **一个度量如果不能被关掉，它就只是一句抱怨。**
"""

BACKLOG_ADD = """

## 判据 (c) — 重发布：+1,963 函数，61.96% → **62.66%**（R933，**新产物**）

### 发布命令

```
dotnet publish -c Release -r win-x64 -p:PublishAot=true -p:UseSharedCompilation=false -m:1 -o .publish-aot-new
exit 0 · 54,652 KB · 只有 Jint/DataTable trim 警告
```

### 结果

| 度量 | 旧 | **新** |
|---|---|---|
| 复刻件 .pdata | 171,690 | **173,653** |
| 比例 | 61.96% | **62.66%** |
| 陈旧度 | 59 / 23,815 | **0 / current** |

### 两条纪律

**① +1,963 只能说「这一版比上一版多」** —— 新函数与 AOT 重新展开的边界分不开。
**② ≈124 万行是估算** —— 12 行/函数来自 59 文件样本。

### 距离

**差 103,467 个非叶函数。**

| 仍 Unknown | |
|---|---|
| 1,963 里新增与展开各占多少 | 分不开 |
| 12 行/函数的普适性 | 单一样本 |
| 旧产物 | 保留为 `.publish-aot-prev` |

**纪律**：**一个度量如果不能被关掉，它就只是一句抱怨。**
"""

BLOCKER = """

---

## 357. 重发布完成：+1,963 函数，62.66%；陈旧度归零

> R933。**新产物，未改代码。** 套件待跑。

### 一、发布

```
dotnet publish -c Release -r win-x64 -p:PublishAot=true -p:UseSharedCompilation=false -m:1 -o .publish-aot-new
→ exit 0 · 54,652 KB（旧 54,052 KB）· 只有 Jint / DataTable trim 警告
```

**旧产物保留为 `.publish-aot-prev`。**

### 二、结果

| 度量 | 旧产物 | 新产物 |
|---|---|---|
| 复刻件 .pdata | 171,690 | **173,653** |
| **函数比例** | 61.96% | **62.66%** |
| **产物陈旧度** | 59 文件 / 23,815 行 | **0 文件 / current** |

**→ 59 个文件、23,815 行 = +1,963 个非叶函数（+0.70 pp），约每 12 行一个函数。**

### 三、两条必须说明的限定

1. **+1,963 只能说「这一版比上一版多 1,963 个非叶函数」。**
   其中多少是 R920–R930 的新函数、多少是 AOT 把之前内联的边界重新展开，**分不开**。
   说「我写了 1,963 个函数」是 R918「净数藏住反向移动」的再犯。
2. **≈124 万行是估算。** 12 行/函数来自 59 个文件的单一样本。

### 四、距离目标

| | 数 |
|---|---|
| 原版 | 277,120 |
| 复刻件 | 173,653 |
| **差** | **103,467** |

### 五、验证

```
func_count.py            -> 277,120 / 173,653 / 62.66%
artifact_freshness.py    -> 0 files newer；state current
```

### 六、仍然 Unknown

- **1,963 里新增与展开各占多少**：**Unknown** —— 分不开。
- **12 行/函数的普适性**：**Unknown** —— 单一样本。
- **旧产物**：保留在 `.publish-aot-prev`，未删。

### 七、教训

**R932 那个度量不只是「提醒可能过期」，它是**一个可以关掉的红灯**。**

**而关掉它的方式只有一条：重发布。**

**一个度量如果不能被关掉，它就只是一句抱怨。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R933", BLOCKER)
    ensure(RSTATUS, "R933", BLOCKER)
    ensure(RVERDICT, "第 933 轮", VERDICT)
    ensure(BACKLOG, "R933", BACKLOG_ADD)

    note = (
        "\n## R933 补充 — 重发布：+1,963 函数，61.96% → 62.66%；陈旧度归零（新产物）\n\n"
        "2.16 GB 够 → dotnet publish -c Release -r win-x64 -p:PublishAot=true -m:1 → exit 0 · 54,652 KB。\n"
        "旧产物保留为 .publish-aot-prev。\n\n"
        "结果：171,690 → 173,653（+1,963）· 61.96% → 62.66% · 陈旧度 59/23,815 → 0/current。\n"
        "约每 12 行一个非叶函数。\n\n"
        "两条限定：① +1,963 只能说「这一版比上一版多」—— 新函数与 AOT 重新展开分不开；② ≈124 万行是估算（单一样本）。\n\n"
        "距离：差 103,467 个非叶函数。\n\n"
        "纪律：一个度量如果不能被关掉，它就只是一句抱怨。\n\n"
        "下一轮：跑全量套件确认 1932 仍绿，然后继续推进函数数。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R933" not in h:
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
             for p, k in ((RBLOCK, "R933"), (RSTATUS, "R933"), (RVERDICT, "第 933 轮"), (BACKLOG, "R933")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R933: republished, and the function count moves for the first time in a while\n\n"
         "R932 found the function ratio came from an artifact fifty-nine source files out of date, added a measure for\n"
         " it, and stopped short of publishing because memory sat under two gigabytes. This round memory read 2.16, so\n"
         " the publish went through: exit zero, a fifty-four megabyte native executable, and nothing but trim warnings\n"
         " from Jint and DataTable reflection.\n\n"
         "The replica's non-leaf function count moves from 171,690 to 173,653, and the ratio from 61.96% to 62.66%. Those\n"
         " fifty-nine files and twenty-three thousand lines bought 1,963 functions, which is roughly one function per\n"
         " twelve lines -- a ratio worth keeping, since it says both the density of this code and how much writing\n"
         " another percentage point costs.\n\n"
         "Two limits on the number. It can only be read as this build having 1,963 more non-leaf functions than the last\n"
         " one; how much of that is the six vendor integrations, KeyGesture and ConcurrencyLimit, and how much is the\n"
         " AOT compiler re-expanding boundaries it had inlined before, cannot be separated. Saying I wrote 1,963\n"
         " functions would be R918's net-figure-hides-opposite-movements again. And the estimate of 1.24 million lines to\n"
         " close the remaining 103,467 functions rests on a twelve-lines-per-function figure drawn from a single sample\n"
         " of fifty-nine files.\n\n"
         "Figures: replica 173,653 against the original's 277,120, ratio 62.66%, freshness down from fifty-nine files\n"
         " and 23,815 lines to zero and current. The previous artifact is kept at .publish-aot-prev rather than deleted.\n\n"
         "Unknown: the split between new functions and re-expanded ones; whether twelve lines per function holds beyond\n"
         " this sample; and the suite, which has not been run since the publish.\n\n"
         "The lesson is that R932's measure turned out to be more than a warning. It is a light that can be turned off,\n"
         " and the only way to turn it off is to republish. A measure that cannot be cleared is just a complaint.\n\n"
         "Artifact republished; no source changed; suite not yet rerun."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()