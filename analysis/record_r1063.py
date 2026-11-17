"""Record R1063: freshness back to zero, and the guard ran for the first time."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 陈旧度归零；而路径校验**第一次真的跑了**（R1063）

**R1062 结束时陈旧度是 **16 文件 / 8,626 行** —— 那是 snapshot 与多处源码/工具改动累积的。
(c) 要求产物与源码同步，所以这一轮先清它。**

### ① publish + 轮转

```
publish exit=0   →   .publish-aot-new
轮转后：.publish-aot 22:30（新）· .publish-aot-prev 19:15（旧）
exe present: True
产物陈旧度：0 文件 / 0 行
完整套件：2258 通过 / 0 失败 / 0 跳过
函数数：277,120 / 174,293 / 62.89%
```

**→ (c)「产物级对照可复算」重新成立：函数数量那一行来自**与源码同步**的产物。**

### ② 而这次路径校验**真的执行了**

**R1042 那次我写的是：**

```powershell
if (Test-Path $p -and $p -notlike "$root\\.publish-aot*") { ... }   ← 语法错，**静默失败**
```

**→ 校验没跑，而删除与移动照旧执行。当时我说：「结果对是因为路径由 `(Get-Location)` 构造，
是运气不是校验；而校验存在而没执行，比没有校验更坏。」**

**而这次写成：**

```powershell
foreach ($p in @($prev,$cur,$new)) {
  if ((Test-Path $p) -and -not ($p -like "$root\\.publish-aot*")) { $bad += $p }
}
if ($bad.Count -gt 0) { "!! REFUSE"; exit 1 }
```

**→ 加了括号，并把拒绝条件改成**先收集再判**（而不是在循环里逐条 exit）。
→ 而脚本自己打印了 `paths verified under … (guard actually ran this time)` ——
**那句话是**断言**，不是装饰：它只在 `$bad` 为空时到达。**

**→ 所以这一轮不只是「陈旧度归零」，也是**那条纪律第一次被执行**（R1042 记录它、R1063 验证它）。**

### ③ 而 (c) 现在的状态

| (c) 的子项 | 状态 |
|---|---|
| 产物存在且可算 | **是**（`.publish-aot\Cybersole.Ui.exe`） |
| 产物与源码同步 | **是 —— 陈旧度 0 / 0** |
| 函数数量来自该产物 | **是 —— 277,120 / 174,293 / 62.89%** |
| 轮转可回溯 | **是 —— `.publish-aot-prev` 保留上一版** |

### ④ 数字

| 度量 | R1062 | **R1063** |
|---|---|---|
| **产物陈旧度** | **16 / 8,626** | **0 / 0** |
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| 比例 | 62.89% | **62.89%** |
| **publish** | 未做 | **exit 0** |
| **轮转** | — | **`.publish-aot` 22:30 · prev 19:15** |
| **路径校验是否执行** | R1042 那次**否**（静默） | **是（带括号 + 先收集再判）** |
| **(c)** | 失效（16 文件陈旧） | **成立** |

### 教训

> **「校验存在而没执行，比没有校验更坏」这句话我在 R1042 写过，而 R1063 才第一次让它真的运行。
> → 而让这件事可验证的不是纪律，是脚本自己打印的那句 `guard actually ran this time` ——
> 它只在通过时到达，所以它的出现本身是证据。**
> **→ 与「工具把 staleness 写在输出里」同族：让**状态可见**比让人记得更可靠。**
"""

if "陈旧度归零；而路径校验**第一次真的跑了**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1063 —— **陈旧度 16/8,626 → 0/0；(c) 成立；而路径校验第一次真的跑了**

### publish + 轮转

```
publish exit=0 → .publish-aot-new → 轮转
.publish-aot 22:30（新）· .publish-aot-prev 19:15 · exe present
产物陈旧度 **0 / 0** · 套件 **2258 / 0 / 0** · 函数数 277,120 / 174,293 / 62.89%
```

**⇒ (c)「产物级对照可复算」重新成立 —— 函数数量那一行来自与源码同步的产物。**

### 而这次路径校验真的执行了

R1042 那次：`if (Test-Path $p -and ...)` ⇒ **语法错，静默失败**，删除/移动照旧执行。
这次：先收集 `$bad` 再判 + `exit 1`，且脚本打印 `guard actually ran this time`
—— **那句话只在 `$bad` 为空时到达，所以它的出现本身是证据。**

**⇒ 这一轮不只是陈旧度归零，也是那条纪律**第一次被执行**（R1042 记录、R1063 验证）。**

### (c) 的状态

| 子项 | 状态 |
|---|---|
| 产物存在且可算 | **是（exe 在）** |
| 产物与源码同步 | **是 —— 0 / 0** |
| 函数数量来自该产物 | **是** |
| 轮转可回溯 | **是（prev 保留）** |

### 数字

| 度量 | R1062 | **R1063** |
|---|---|---|
| 产物陈旧度 | **16 / 8,626** | **0 / 0** |
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| publish | 未做 | **exit 0** |
| 轮转 | — | **22:30 / prev 19:15** |
| 路径校验执行 | **否**（R1042） | **是** |
| (c) | 失效 | **成立** |

**纪律**：让**状态可见**比让人记得更可靠 —— 与「工具把 staleness 写在输出里」同族。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1063", NOTE)
append(RBLOCK, "R1063", "\n---\n\n## 487. **陈旧度 16/8,626 → 0/0；(c) 成立**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1063: freshness is zero again, and the path guard ran for the first time\n\n"
     "R1062 closed with sixteen source files newer than the artifact, eight and a half thousand lines, accumulated from\n"
     " snapshot runs and several rounds of source and tool edits. Criterion (c) wants the artifact and the source in\n"
     " step, so this round published and rotated first.\n\n"
     "The publish exits zero, the rotation puts the new build at twenty-two thirty with the previous one kept beside it,\n"
     " and the freshness check reads zero files and zero lines. The suite is green at 2258 and the count is unchanged at\n"
     " 174,293 of 277,120, so the ratio line now rests on an artifact that matches its source.\n\n"
     "The second thing worth recording is smaller and older. In R1042 I wrote that a check which exists and does not\n"
     " execute is worse than no check, because it leaves the impression something was confirmed -- and that round's own\n"
     " check had silently failed on a missing parenthesis while the delete and the moves went ahead. This round the\n"
     " guard collects refusals first and exits once, and the script prints that it actually ran. That sentence is only\n"
     " reached when nothing was refused, so its presence is evidence rather than decoration.\n\n"
     "It took ten rounds for a written rule to become a run check. The thing that made it verifiable was not the rule\n"
     " but the printed line, which is the same reason the mutation tool printing its own staleness beats any instruction\n"
     " to re-run it.\n\n"
     "Figures: freshness from sixteen files and 8,626 lines to zero and zero, suite green at 2258, count 174,293 at\n"
     " 62.89 per cent, publish exiting zero, the previous artifact retained for rollback, and the path guard executing\n"
     " for the first time.\n\n"
     "The lesson is that making a state visible is more reliable than remembering to check it."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
