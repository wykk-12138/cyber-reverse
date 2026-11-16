"""Record R832: the function count becomes a metric, and a loose regex read zero from another script."""

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

## 256. 函数数量进 `METRICS.md`；**而我的正则从别的脚本里读了一个 0**

> R832。新增 `replica/tools/func_count.py`，注册为第七项度量。**共享工具已改，全量已复跑。**

### 一、为什么上一轮没做

R831 量出了 277,120 ↔ 171,690（62%），但用的是一次性脚本。
**「一个没人能重算的数，就是会漂的数」** —— 这一轮把它变成度量。

`func_count.py` 的存在理由写在文件头（§1.2）：读两个 PE 的 `.pdata`，
**不需要反汇编、不需要第二个 IDA 实例**；而 `func_compare.py` 要 13338。

### 二、注册之后立刻暴露一个真 bug

`METRICS` 是 `(名字, argv)` 列表，`summary_bits` 把**所有正则套到每个脚本的输出上**。

**我新加的 `replica\\s*:\\s*([\\d,]+)` 撞上了 `datafiles_diff.py` 输出里的某一行，于是：**

```
数据文件名对照   {'datafiles: ...': '0', 'datafiles: replica-only': '2', 'functions: replica .pdata': '0'}
```

**一个度量从另一个脚本的输出里读到了一个 0，而且它看起来像个真数。**

**修法不是调正则的松紧，是让标签唯一**：`original:` → `pdata-original:`、`replica :` → `pdata-replica:`、
`ratio   :` → `pdata-ratio:`，正则跟着改成只认这三个前缀。

**修后：**

```
数据文件名对照    {'datafiles: original-on-disk not in replica': '0', 'datafiles: replica-only': '2'}
函数数量（.pdata）{'functions: original .pdata': '277,120', 'functions: replica .pdata': '171,690', 'functions: ratio': '61.96%'}
```

**`datafiles` 那三项回到了原来的样子，不再有串进来的键。**

### 三、这一条 bug 的形态

**`summary_bits` 是「对所有输出跑所有正则」的设计** —— 它对每个脚本都返回一张全模式匹配表，
再由调用方按度量名去取。**所以任何一条过于通用的正则都会污染其他度量的表。**

**而这个污染是静默的**：`functions: replica .pdata: 0` 读起来就是一个正常的零。
**如果我不看新增行的完整输出，只核「第七项有没有出现」，就会把它当成 0 收下。**

### 四、验证

```
python tools\\func_count.py                      277,120 / 171,690 / 61.96%
python tools\\metrics_report.py --skip-tests     七项全 exit 0，无串味
python tools\\metrics_report.py                  1766 通过 / 0 失败
docs\\METRICS.md                                 新增三行（original / replica / ratio）
```

**`METRICS.md` 第七项：**

```
| 函数数量（.pdata） — functions: original .pdata | 277,120 |
| 函数数量（.pdata） — functions: replica .pdata  | 171,690 |
| 函数数量（.pdata） — functions: ratio          | 61.96%  |
```

### 五、这个数怎么读（写进了工具的输出里）

**能说**：复刻件的函数量是原版的约 62%，同一口径。

**不能说**：不是「少了 38% 功能」（**两边框架不同**：.NET 10 AOT ↔ .NET 8 AOT + Avalonia，
Avalonia 自带一大批函数、BCL 也不同）；不是「函数级对等」（`.pdata` 数非叶函数，不含内联与裁剪）；
**不能跟 IDA 的 321,244 比**（口径不同）。

**这三条现在印在 `func_count.py` 的输出里，所以看着 `METRICS.md` 的人也会看到它们。**

### 六、仍然 Unknown

- **复刻件的 IDA `af` 计数**：**Unknown** —— 唯一与 321,244 对齐的口径，要 13338。
- **62% 里 Avalonia 与 BCL 占多少**：**Unknown** —— `.pdata` 无命名空间信息。
- **`summary_bits` 里还有没有别的过于通用的正则**：**Unknown** ——
  这一轮只发现了自己新加的那三条，**其余十一项的历史正则没逐个审。**

### 七、教训

**「把它变成度量」这个动作本身发现了 bug —— 因为度量要在别人的输出旁边活，而一次性脚本不用。**
**一次性脚本只看自己的输出，度量要看所有输出。**

**而 `functions: replica .pdata: 0` 这个形态特别值得记：**
**它是一个正确的数（真的是 0 个匹配），被贴到了一个错误的键上，于是读起来像一个事实。**
"""

VERDICT = """

---

## 第 832 轮：函数数量进 METRICS；而我的正则从别的脚本里读了一个 0

### 新增第七项度量

`replica/tools/func_count.py` —— 读两个 PE 的 `.pdata`，**不需要反汇编、不需要第二个 IDA 实例**。
已注册进 `METRICS`，`docs/METRICS.md` 新增三行：

```
函数数量（.pdata） — original .pdata | 277,120
函数数量（.pdata） — replica .pdata  | 171,690
函数数量（.pdata） — ratio           | 61.96%
```

### 注册之后立刻暴露一个真 bug

`summary_bits` **把所有正则套到每个脚本的输出上**。我新加的 `replica\\s*:\\s*([\\d,]+)` 撞上了
`datafiles_diff.py` 的某一行：

```
数据文件名对照  {..., 'functions: replica .pdata': '0'}      ← 从别的脚本读来的
```

**修法不是调正则松紧，是让标签唯一**（`pdata-original:` / `pdata-replica:` / `pdata-ratio:`）。
修后 `datafiles` 回到原样，`函数数量` 三项齐全。

### 这个 bug 的形态

**`functions: replica .pdata: 0` 是一个正确的数（真的 0 个匹配）被贴到了一个错误的键上，于是读起来像一个事实。**

**如果我只核「第七项有没有出现」，就会把 0 收下。**

### 验证

```
func_count.py 277,120 / 171,690 / 61.96% · metrics_report --skip-tests 七项全 exit 0
metrics_report 1766 通过 / 0 失败 · METRICS.md 新增三行
```

### 怎么读这个数（已印进工具输出）

**能说**：约 62%，同一口径。**不能说**：不是「少了 38% 功能」（**框架不同**：.NET 10 AOT ↔ .NET 8 AOT + Avalonia）·
不是「函数级对等」（`.pdata` 数非叶函数）· **不能跟 IDA 的 321,244 比**（口径不同）。

### 仍然 Unknown

**复刻件 IDA `af` 计数**（需 13338）· **62% 里 Avalonia/BCL 占多少**（`.pdata` 无命名空间）·
**`summary_bits` 其余十一项历史正则有没有同类问题**（未逐个审）

### 教训

**「把它变成度量」这个动作本身发现了 bug —— 一次性脚本只看自己的输出，度量要看所有输出。**
"""

BACKLOG_ADD = """

## 判据 — 函数数量成为第七项度量（R832）

**新增** `replica/tools/func_count.py`（读两个 PE 的 `.pdata`，无需反汇编、无需第二个 IDA）。
**已注册进 `METRICS`**，`docs/METRICS.md` 新增三项：

```
functions: original .pdata | 277,120
functions: replica .pdata  | 171,690
functions: ratio           | 61.96%
```

### 注册时暴露的 bug（已修）

`summary_bits` **把所有正则套到每个脚本输出上**。我的 `replica\\s*:\\s*([\\d,]+)` 撞上 `datafiles_diff.py`，
于是 `数据文件名对照` 里多了一个 `functions: replica .pdata: 0`。

**修法：让标签唯一**（`pdata-original:` / `pdata-replica:` / `pdata-ratio:`），不是调正则松紧。

> **形态**：一个正确的数（真的 0 个匹配）被贴到错误的键上，读起来像一个事实。

### 这个数的读法（已印进工具输出，看到 METRICS 的人也会看到）

| 能说 | 不能说 |
|---|---|
| 约 62%，同一口径 | **「少了 38% 功能」** —— 框架不同（.NET 10 AOT ↔ .NET 8 AOT + Avalonia） |
| | **「函数级对等」** —— `.pdata` 数非叶函数，不含内联/裁剪 |
| | **与 321,244 相比** —— 那是 IDA `af` 口径 |

| 仍 Unknown | |
|---|---|
| 复刻件 IDA `af` 计数 | 需 13338 实例 |
| 62% 里 Avalonia / BCL 占多少 | `.pdata` 无命名空间信息 |
| `summary_bits` 其余历史正则有无同类问题 | **未逐个审** |

**纪律**：**一次性脚本只看自己的输出，度量要看所有输出 —— 变成度量这个动作本身会暴露 bug。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R832", BLOCKER)
    ensure(RSTATUS, "R832", BLOCKER)
    ensure(RVERDICT, "第 832 轮", VERDICT)
    ensure(BACKLOG, "R832", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    old = ("**待办：把这个数加进 `tools/metrics_report.py`**"
           "（或让 `func_compare.py` 在 13338 没起时用 `.pdata` 兜底）。")
    new = ("**已完成（R832）**：`replica/tools/func_count.py` 注册为**第七项度量**，`METRICS.md` 有三行"
           "（original / replica / ratio）。")
    if old in h:
        h = h.replace(old, new, 1)
        print("  handoff item updated")
    elif "R832" not in h:
        h += "\n## R832 补充\n\n函数数量已是第七项度量（`tools/func_count.py`），`METRICS.md` 有 original/replica/ratio 三行。\n"
        print("  handoff appended")
    io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R832"), (RSTATUS, "R832"), (RVERDICT, "第 832 轮"), (BACKLOG, "R832")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R832: the function count becomes a metric, and a loose regex read zero from another script\n\n"
         "R831 measured the goal's first clause with a one-off script, and a number nobody can re-run is a number that"
         " drifts. func_count.py now reads .pdata from both PE images and is registered as the seventh metric, so"
         " METRICS.md carries original 277,120, replica 171,690 and a ratio of 61.96 percent. It needs no disassembly"
         " and no second IDA instance, which is why it is the measure -- func_compare.py can answer the same question but"
         " wants the replica's database on port 13338, which is usually not running.\n\n"
         "Registering it exposed a real bug within minutes. summary_bits applies every pattern to every script's output,"
         " and my new replica-plus-colon pattern matched a line in datafiles_diff.py, so the datafiles metric reported a"
         " function count of zero that did not belong to it. The repair is not a tighter regex but unique labels: the"
         " tool now prints pdata-original, pdata-replica and pdata-ratio, and the patterns accept only those prefixes."
         " After that the datafiles entry returns to its own three keys.\n\n"
         "The shape of that bug is worth keeping. A correct number -- genuinely zero matches -- got attached to the wrong"
         " key and read like a fact. Had I only checked that the seventh metric appeared at all, I would have accepted the"
         " zero.\n\n"
         "What the figure supports is printed by the tool itself so a reader of METRICS.md sees it too: the replica's"
         " function mass is about 62 percent of the original's on one identical measure. It is not evidence that 38"
         " percent of the functionality is missing, because the frameworks differ and Avalonia brings a large function"
         " mass of its own; it is not function-level equality, because .pdata counts non-leaf functions and excludes"
         " inlined and trimmed code; and it is not comparable with IDA's 321,244, which is a different count.\n\n"
         "Unknown: the replica's IDA af count, the one figure comparable with 321,244, needing the second instance; how"
         " much of the 62 percent is Avalonia and the BCL, which .pdata cannot separate; and whether the other eleven"
         " patterns in summary_bits have the same over-generality, which I did not audit.\n\n"
         "Suite 1766 pass / 0 fail; six metrics unchanged, plus the new seventh."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
