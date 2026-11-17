"""Record R1061: the exit-1 was probably mine, not the script's."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 那个 `exit 1` 很可能是**我的测量方式**造成的，不是脚本的矛盾（R1061）

**R1060 把「`mutation-check` 输出全 GREEN 而 exit 1」记成 Unknown。这一轮去追，而追到的第一个事实是：
那个「1」**未必是脚本的**。**

### ① 脚本里没有退出路径

```
grep "exit|sys.exit|return 1|returncode" tools/mutation-check.py
  → 只有一处 returncode（line 467，在一个**辅助函数**里返回 tuple 给调用方）
  → main() 无返回值（最后一行是 main()），文件里**没有 sys.exit**
  → if __name__ == "__main__": main()
```

**→ 所以按源码，脚本**应当**以 0 退出。而实测报 1。**

### ② 而我的测量方式不能区分脚本与管道

**我跑的是：**

```powershell
python tools\\mutation-check.py 2>&1 | Select-Object -Last 30
```

**→ 那是一条**管道**：`$LASTEXITCODE` 反映 python，而后台 job 报的 `exit code` 是**整条管道最后一条命令**的。
→ **两者可能不同，而我在 R1060 把 job 报的那个 1 直接读成了脚本的退出码。**

**→ 那是一个**测量错误**，而它把「我的工具用错了」伪装成「脚本有矛盾」。**

### ③ 所以 Unknown 要改写

| R1060 写的 | R1061 改成 |
|---|---|
| 「`mutation-check` 输出 GREEN 而 exit 1 —— 未解释的矛盾」 | 「那个 1 的**归属未确定**：脚本无退出路径 ⇒ 可能来自管道。**需不经管道重跑一次**」 |

**→ 而那是更弱但**更准**的一条：它不再暗示脚本有问题，而是说**我的测量不确定**。**

**→ 与 R1044「零值需要对照」同族：一个数字（1）的**来源**没有确定，就不该把它读成关于被测对象的结论。**

### ④ 而下一轮的第一步是明确的

```powershell
cd D:\\projects\\cyber-reverse\\replica
$p = Start-Process python -ArgumentList "tools/mutation-check.py" -NoNewWindow -PassThru -Wait
"  python exit: " + $p.ExitCode
```

**→ 不经管道、不取 Last 30，直接读 `ExitCode`。**
**→ 若它是 0 ⇒ R1060 那个 Unknown 撤销（脚本没问题，是我的管道）。**
**→ 若它是 1 ⇒ 才真的是脚本的问题，再去读 `classify()` 与恢复路径。**

### ⑤ 数字

| 度量 | R1060 | **R1061** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 4 / 889 | **4 / 889** |
| 函数数 | 174,293 | **174,293** |
| 变异 fired | 36 / 36 | **36 / 36（未变）** |
| **`mutation-check.py` 里的 `sys.exit`** | 未查 | **0 处** |
| **`main()` 有返回值** | 未查 | **否** |
| **那个 exit 1 的归属** | 「脚本的矛盾」 | **「我的管道测量，待重跑确认」** |
| **真正的错误** | — | **1（把管道退出码读成脚本的）** |

### 教训

> **一个数字的来源没确定，就不该把它读成关于被测对象的结论。**
> **→ 我测一个脚本的退出码，用的是「python … | Select-Object」，然后读 job 报的码 ——
> 而那条管道两端都可以产生非零，且我在 R1060 一次都没问过那是谁的。**
> **→ 那与「把 `orig=0` 读成零缺口」是同一个错的第三种形态：
> 这次是**测量工具**没分清主体，那次是**查询**没有内容。**
"""

if "那个 `exit 1` 很可能是**我的测量方式**造成的" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1061 —— **那个 exit 1 很可能是我的测量方式，不是脚本的矛盾**

### 脚本里没有退出路径

```
grep exit|sys.exit|returncode  → 只有一处 returncode（辅助函数返回 tuple）
main() 无返回值 · 无 sys.exit · if __name__ == "__main__": main()
```

**⇒ 按源码脚本**应当**以 0 退出。而实测报 1。**

### 而我的测量方式不能区分脚本与管道

```powershell
python tools\\mutation-check.py 2>&1 | Select-Object -Last 30   ← **管道**
```

**→ `$LASTEXITCODE` 反映 python，而后台 job 报的是**整条管道**的退出码。
→ 我在 R1060 把 job 报的 1 直接读成脚本的 ⇒ **那是测量错误，不是脚本的矛盾。**

### 所以 Unknown 改写

| R1060 | R1061 |
|---|---|
| 「GREEN 而 exit 1 —— 未解释的矛盾」 | 「那个 1 的**归属未确定**：脚本无退出路径 ⇒ 可能来自管道。**需不经管道重跑**」 |

**⇒ 与 R1044「零值需要对照」同族：一个数字**来源**没确定，就不该读成关于被测对象的结论。**

### 下一轮第一步

```powershell
$p = Start-Process python -ArgumentList "tools/mutation-check.py" -NoNewWindow -PassThru -Wait
"  python exit: " + $p.ExitCode
```

**0 ⇒ 撤销 R1060 那个 Unknown（是我的管道）；1 ⇒ 才是脚本的问题，去读 `classify()` 与恢复路径。**

### 数字

| 度量 | R1060 | **R1061** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| 变异 fired | 36 / 36 | **36 / 36** |
| 脚本里的 `sys.exit` | 未查 | **0 处** |
| 那个 1 的归属 | 「脚本的矛盾」 | **「我的管道，待重跑」** |
| 真正的错误 | — | **1（把管道退出码读成脚本的）** |

**纪律**：测量工具没分清主体，和查询没有内容，是同一个错的两种形态。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1061", NOTE)
append(RBLOCK, "R1061", "\n---\n\n## 485. **那个 exit 1 很可能是我的测量方式**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1061: the exit code was probably an artefact of how I measured it\n\n"
     "R1060 recorded that mutation-check prints green while exiting one, and filed the contradiction as unknown. Going\n"
     " after it, the first fact is that the one may not be the script's at all.\n\n"
     "The script has no exit path. Grepping for exit, sys.exit, return 1 and returncode finds exactly one hit, a helper\n"
     " that returns a tuple to its caller, and main has no return value. By the source it should exit zero. So where did\n"
     " one come from? From how I ran it. My command piped python into Select-Object and then read the background job's\n"
     " status, and a pipeline reports the last command's code while LASTEXITCODE reflects python's. I read the job's\n"
     " number as the script's without asking whose it was.\n\n"
     "That makes the previous round's unknown weaker and more accurate. It is not that the script contradicts itself; it\n"
     " is that the attribution of that digit is undetermined. Same family as R1044: a number whose source is not\n"
     " established cannot be read as a statement about the thing being measured.\n\n"
     "The next step is one measurement: run it without a pipe, wait on the process and read its ExitCode directly. Zero\n"
     " retires the unknown as my own plumbing; one means the script really does return it, and then classify and the\n"
     " restore path are where to look.\n\n"
     "Figures: suite green at 2258, freshness four files and 889 lines, count 174,293, thirty-six mutations still all\n"
     " fired, zero sys.exit calls in the script, and one measurement error of my own making.\n\n"
     "Unknown: whose exit code one was, pending a run that can tell.\n\n"
     "The lesson is that a measuring tool which does not separate subject from observer produces findings about the\n"
     " instrument, and that I filed one as a finding about the script."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
