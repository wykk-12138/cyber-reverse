"""Record R831: the first measurement of the goal's first clause."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 255. **第一次量「函数数量对等」**：277,120 ↔ 171,690（62%）

> R831。未改产品代码。目标第一句是「函数数量对等」，**而 `METRICS.md` 里从来没有这一项。**

### 一、为什么此前没量

`METRICS.md` 的六项是：名字级绑定缺口 · 类型级绑定缺口 · 类型缺失 · 成员形状 · 文案 · 完整套件。
**全是「声明层」的度量。函数数没在里面。**

`analysis/func_compare.py` 能度量它，但它要**两个 IDA 实例**（原版 13337、复刻件 13338）。
**13338 现在没起：**

```
original <- http://127.0.0.1:13337/mcp
  original: symbols=no named=10041 total=321244 ratio=0.0313
  -> analysis/original_funcs.txt（321,244 行）
replica  <- http://127.0.0.1:13338/mcp
  ConnectionRefusedError: [WinError 10061]
```

**但不必开第二个 IDA —— `.pdata` 里的 `RUNTIME_FUNCTION` 表能直接从 PE 读出来。**

### 二、结果

| 产物 | `.pdata` 函数数 |
|---|---|
| **原版** `target\\Cybersole.exe` | **277,120** |
| **复刻件** `replica\\.publish-aot\\Cybersole.Ui.exe` | **171,690** |

**171,690 / 277,120 = 61.95%。**

**顺带交代一个偏差**：文档里记的 `.pdata` 条目是 **277,094**，我数到 277,120，**差 26**。
**`.pdata` 的 rawsize 可能含尾部填充，`rawsize / 12` 会把填充算成一两条。**
**所以这两个数都是「约 277,000」，不是精确值。**

### 三、这个数能说明什么，不能说明什么

**能说**：**复刻件的函数量是原版的约 62%** —— 同一个量（`.pdata` 条目）在两边的比。

**不能说**：

- **不能说是「少了 38% 的功能」** —— 两边是不同的框架（原版 .NET 10 NativeAOT；
  复刻件 .NET 8 NativeAOT + Avalonia），**Avalonia 自己带来一大批函数，BCL 版本也不同**。
- **不能说是「函数级对等」** —— `.pdata` 数的是**非叶函数**，不含内联与被裁剪的。
- **不能跟 321,244 直接比** —— 那是 IDA 的 `af` 计数，**口径不同**。要跟它比就得在复刻件上也跑 IDA。

### 四、把它变成一条可复算的度量

**这次是一次性脚本。要让它进 `METRICS.md`，得：**

1. 把「两个产物的 `.pdata` 计数」加进 `tools/metrics_report.py`
2. 或把 `func_compare.py` 的复刻件侧改成 `.pdata` 兜底（13338 没起时）

**本轮没改 `metrics_report.py`** —— 那要改共享工具并复跑全量，
**而这一轮先把数字拿出来、把口径讲清更重要。**

### 五、验证

```
python analysis\\func_compare.py                原版 321,244（IDA af）；复刻件侧 13338 拒连
.pdata rawsize/12:  原版 277,120 · 复刻件 171,690  -> 61.95%
本轮未改产品代码
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- **复刻件的 IDA `af` 计数**：**Unknown** —— 需要 13338 那个实例，
  **而它是复刻件侧唯一能与 321,244 对齐的口径。**
- **62% 里 Avalonia 占多少**：**Unknown** —— 要区分「框架自带」与「我们写的」，
  得按命名空间分组，**而 `.pdata` 没有命名空间信息。**
- **`.pdata` 的 26 条偏差是否真的是填充**：**Inference（中）** —— 没逐条核。

### 七、教训

**目标的第一句话，是最后才被量的一句。**
**因为前六项度量都在数「声明」，而函数数要数「产物」—— 数声明比数产物容易得多，所以一直没做。**
"""

VERDICT = """

---

## 第 831 轮：第一次量「函数数量对等」—— 277,120 ↔ 171,690（62%）

### 为什么此前没量

`METRICS.md` 六项全是**声明层**度量（绑定缺口、类型缺失、形状、文案、套件）。**函数数不在里面。**

`func_compare.py` 能量，但要两个 IDA 实例；**13338 没起**（`ConnectionRefused`）。原版侧跑通了：`total=321244, named=10041`。

**但 `.pdata` 能直接从 PE 读。**

### 结果

| 产物 | `.pdata` 函数数 |
|---|---|
| 原版 | **277,120** |
| 复刻件 | **171,690** |

**61.95%。**

**偏差交代**：文档记 277,094，我数到 277,120，**差 26** —— `.pdata` rawsize 含尾部填充，`rawsize/12` 会多算一两条。**两个都是「约 277,000」。**

### 能说 / 不能说

**能说**：复刻件函数量约原版的 62%（同一个量在两边的比）。

**不能说**：① 不是「少了 38% 功能」—— 两边框架不同（.NET 10 AOT ↔ .NET 8 AOT + Avalonia），**Avalonia 自带一大批函数**；② 不是「函数级对等」—— `.pdata` 数非叶函数，不含内联与裁剪；③ **不能跟 321,244 比** —— 那是 IDA `af` 口径。

### 没做成的一条

**没把它加进 `metrics_report.py`** —— 那要改共享工具并复跑全量。**本轮先把数字和口径拿出来更重要。**

### 仍然 Unknown

**复刻件的 IDA `af` 计数**（唯一与 321,244 对齐的口径，需 13338）· **62% 里 Avalonia 占多少**（`.pdata` 无命名空间信息）· **26 条偏差是否真是填充**

### 教训

> **目标的第一句话，是最后才被量的一句。**
> **因为前六项度量都在数「声明」，而函数数要数「产物」—— 数声明比数产物容易，所以一直没做。**
"""

BACKLOG_ADD = """

## 判据 — 「函数数量对等」首次测量（R831）

**首次数字**（此前 `METRICS.md` 六项全是声明层，无函数数）：

| 产物 | `.pdata` 函数数 |
|---|---|
| 原版 `target\\Cybersole.exe` | **277,120** |
| 复刻件 `.publish-aot\\Cybersole.Ui.exe` | **171,690** |

**61.95%。** 口径：`.pdata` 的 `RUNTIME_FUNCTION`（12 字节）条数。

**偏差**：文档记 277,094，实测 277,120，**差 26** —— rawsize 含尾部填充。

### 能不能说「少了 38% 功能」

**不能。** 两边框架不同（.NET 10 AOT ↔ .NET 8 AOT + Avalonia），**Avalonia 自带一大批函数**；
`.pdata` 数非叶函数，不含内联与裁剪；**与 IDA `af` 的 321,244 不同口径。**

### 待办

**把「两产物 `.pdata` 计数」加进 `tools/metrics_report.py`**（或让 `func_compare.py` 在 13338 没起时用 `.pdata` 兜底）。**本轮未做** —— 要改共享工具并复跑全量。

| 仍 Unknown | |
|---|---|
| 复刻件 IDA `af` 计数 | 需 13338 实例；唯一与 321,244 对齐的口径 |
| 62% 里 Avalonia 占多少 | `.pdata` 无命名空间信息 |
| 26 条偏差是否填充 | Inference（中），未逐条核 |

**纪律**：**目标的第一句话是最后才被量的一句 —— 因为数声明比数产物容易。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R831", BLOCKER)
    ensure(RSTATUS, "R831", BLOCKER)
    ensure(RVERDICT, "第 831 轮", VERDICT)
    ensure(BACKLOG, "R831", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R831" not in h:
        h += ("\n## R831 补充 — 函数数量（目标第一句，首次测量）\n\n"
              "`.pdata` 的 `RUNTIME_FUNCTION` 数：**原版 277,120 · 复刻件 171,690 · 62%**。\n"
              "口径差异：与 IDA `af` 的 321,244 不可直接比；`.pdata` 数非叶函数，不含内联与裁剪。\n"
              "**不能读成「少了 38% 功能」** —— 两边框架不同（原版 .NET 10 AOT；复刻件 .NET 8 AOT + Avalonia）。\n"
              "**待办：把这个数加进 `tools/metrics_report.py`**（或让 `func_compare.py` 在 13338 没起时用 `.pdata` 兜底）。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R831"), (RSTATUS, "R831"), (RVERDICT, "第 831 轮"), (BACKLOG, "R831")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R831: the first measurement of the goal's first clause\n\n"
         "The goal opens with function counts being equal, and METRICS.md has never held that number. Its six metrics"
         " all count declarations -- binding gaps, absent types, member shapes, copy, the suite -- and counting"
         " declarations is easier than counting artifacts, which is why the artifact count went unmeasured.\n\n"
         "func_compare.py can measure it but needs two IDA instances, and the replica's on 13338 is not running. The"
         " original side works: 321,244 functions by IDA's af count, 10,041 of them named. The .pdata RUNTIME_FUNCTION"
         " table needs no second instance, so both artifacts were counted the same way.\n\n"
         "Original 277,120 runtime function entries, replica 171,690, a ratio of 61.95 percent. The documented figure"
         " for the original is 277,094 and I count 277,120; the difference of twenty-six is probably trailing padding in"
         " the section, since rawsize divided by twelve is not exact. So both are approximately 277,000 rather than"
         " exact.\n\n"
         "What the number supports is narrow. It says the replica's function mass is about 62 percent of the original's,"
         " on one measure applied to both. It does not say 38 percent of the functionality is missing, because the"
         " frameworks differ -- .NET 10 NativeAOT against .NET 8 NativeAOT plus Avalonia, and Avalonia brings a large"
         " function mass of its own along with a different BCL. It does not establish function-level equality, since"
         " .pdata counts non-leaf functions and excludes inlining and trimming. And it cannot be compared with 321,244,"
         " which is IDA's count and a different measure entirely.\n\n"
         "I did not fold it into metrics_report.py. That edits a shared tool and requires a full re-run, and this round"
         " was better spent getting the number and stating the measure than wiring it in half-checked.\n\n"
         "Unknown: the replica's IDA af count, which is the only figure comparable with 321,244 and needs the second"
         " instance; how much of the 62 percent is Avalonia and the BCL rather than the replica's own code, which .pdata"
         " cannot separate since it carries no namespace information; and whether the twenty-six-entry difference is"
         " padding, which I did not check row by row.\n\n"
         "No product code changed; four metrics unchanged at 4 / 0 / 17 / 78 / 0."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
