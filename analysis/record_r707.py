"""Record R707 and refine the first-modal rule. Files only -- shell quoting ate two earlier attempts."""

import io
import subprocess

CHECKLIST = r"D:\projects\cyber-reverse\docs\IDA_STARTUP_CHECKLIST.md"
AUDIT = r"D:\projects\cyber-reverse\docs\COMPLETION_AUDIT.md"
P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

CHECKLIST_OLD_ANCHOR = "**Load existing**"
CHECKLIST_ADD = """

### R707 补充：第一个框的答案**取决于二进制有没有变**

R691 那份只写了「选 **Load existing**」。那是**二进制未变**时的正确选择。
本轮换了新产物（55,080,448 → 55,349,248 B）再开 IDA，正确的选择是 **覆盖(O)** ——
加载旧库等于拿旧字节的语义去解释新产物。

| 情形 | 选什么 |
|---|---|
| 二进制**没变**，只想恢复上次的分析 | **加载现有(L)** |
| 二进制**变了**（重建过、换过源码） | **覆盖(O)**，让 IDA 重新分析 |

**判断依据**：`Cybersole.Ui.exe` 的字节数/修改时间是否与开库时那只一致。
本轮实测：覆盖后 `ws` 322→567 MB，随后弹「加载新文件」，确定后 CPU 3→8.8 s，再弹 PDB 框，
选「是」后 CPU 8.8→51.2 s，约 **400 秒**后 `auto_analysis_ready: true`。

**另一个坑（本轮踩到）**：`analysis/wait_ready.py` 把「连接被拒」当致命错误，直接退出。
而插件在分析后段才绑端口，所以**前几分钟必然是连接被拒**。
改用 `python analysis/poll_ready.py <port> <timeout> <pid>`：它容忍拒绝，并打印 **CPU 增量**——
本轮那个增量稳定在 ~9.6 s/10 s，是判断「在算」还是「卡在框里」的唯一可靠信号。
"""

AUDIT_OLD = """**如实标注**：C6 / C10 的数字取自重测之前的产物（55,080,448 B）。11:49 的产物为 55,349,248 B，
**这两行未在新产物上重测**，重测需把新 EXE+PDB 重新载入 IDA。**报告可复算，不代表数字已刷新。**"""

AUDIT_NEW = """**已在 11:49 的产物上重测（R707）**：从零重建的 IDB（覆盖旧库 + 载入 PDB types/names），
`auto_analysis_ready: true` 后导出：

```
原版   321,244 个函数  symbols=no   命名 10,041（3.13%）
复刻件 189,090 个函数  symbols=yes  命名 176,784（93.49%）   ← 较旧产物 +1,358
C10    12 / 819 = 1.5%（比例未变：新增的是校验器，不是 view-model 代码）
```

**唯一仍未在新产物上重做的**：R613 的同口径（不带 PDB）数 186,732 —— 那需要另建一个不载 PDB 的库。"""

BLOCKER = """

---

## 136. 新产物上的重测：复刻件 **189,090** 个函数，C10 仍是 **12/819**

> R707。工具：`analysis/poll_ready.py`（新增）；重开 IDA 于新产物；`func_compare.py` / `aot_member_coverage.py`。

### 一、先把库建对

`replica/.publish-aot/Cybersole.Ui.exe` 已重建（55,349,248 B），旧 `.id0/.id1` 是旧字节的库。
**第一个模态框这次必须选「覆盖」** —— R691 清单只写了「加载现有」，那是二进制未变时的答案。已在清单里补条件。

过程（CPU 增量是唯一可靠信号）：

```
覆盖          ws 322 → 567 MB
加载新文件 确定  CPU 3 → 8.8 s
PDB 是         CPU 8.8 → 51.2 s
~400 s 后      auto_analysis_ready: true, input_path = .publish-aot\\Cybersole.Ui.exe
```

**顺带发现 `wait_ready.py` 的缺陷**：它把「连接被拒」当致命错误直接退出，而插件在分析后段才绑端口。
新增 `analysis/poll_ready.py`：容忍拒绝、打印 CPU 增量、只在 `auto_analysis_ready is True` 时退出。

### 二、重测结果

```
original: # exportspec symbols=no   named=10,041   total=321,244  ratio=0.0313
replica : # exportspec symbols=yes  named=176,784  total=189,090  ratio=0.9349
C10     : 12 / 819 = 1.5%   （上一版产物是 187,732 / 12; 比例为 1.5%，未变）
```

**新产物比上一版多 1,358 个函数**，而 C10 一点没动 —— 这两件事合起来说明：
新增的校验器确实**带来了实现**（函数数动了），但**没有让任何绑定成员变得可见**（它不是 view-model 代码）。
**如果没有 C10 这一项，+1,358 会被误读成"覆盖面变好了"。**

### 三、仍然 Unknown

- 同口径（不带 PDB）的复刻件函数数：R613 的 186,732 是**旧产物**的数，**未在新产物上重做**（需另建不载 PDB 的库）。
- C10 那 807 个不可见成员是裁剪 / 内联 / 只在元数据里：**Unknown**，判别器仍未建。
- `strings_cache_ready` 在 READY 时仍为 false / size 0：**未查原因**（不影响本次导出，但会让按字符串查找变慢）。
"""

VERDICT = """

---

## 第 707 轮：新产物上的重测

### 建对库

旧库里是旧字节的语义，所以这次第一个框选**覆盖**（R691 清单只写「加载现有」，那是二进制未变时的答案，已补条件）。
CPU 增量走的：3 → 8.8 → 51.2 s，约 400 秒后 ready。

**顺带修了一个工具缺陷**：`wait_ready.py` 把「连接被拒」当致命错误，而插件在分析后段才绑端口。
新增 `analysis/poll_ready.py`：容忍拒绝 + 打印 CPU 增量 + 只认 `auto_analysis_ready`。

### 数字

```
原版   321,244  symbols=no   命名 10,041（3.13%）
复刻件 189,090  symbols=yes  命名 176,784（93.49%）   ← 较旧产物 +1,358
C10    12 / 819 = 1.5%（未变）
```

**+1,358 个函数而 C10 不动** —— 合起来说明新增校验器带来了实现，但没让任何绑定成员变可见。
**没有 C10 这一项，+1,358 会被误读成"覆盖面变好了"。**

### 一句话

> 两个数字一起看才有意义：一个说"多了 1,358 个函数"，另一个说"一个绑定成员都没多出来"。

> **只盯着会涨的那个指标，涨本身就是好消息；两个一起看，才知道涨的是什么。**

### 下一轮

C10 的 807 个不可见成员要分开"裁剪 / 内联 / 只在元数据里"——那是 `docs` 里挂了很久的判别器。
先读 `BLOCKERS.md` §126/§127 的测量条件，再看能不能用「关 trimming 诊断构建 + 字符串指纹」两路对照。
"""


def main():
    body = io.open(CHECKLIST, encoding="utf-8").read()
    if "R707 补充" in body:
        print("  checklist: already refined")
    elif CHECKLIST_OLD_ANCHOR in body:
        # append at the end: the section is a reference, order is not load-bearing
        io.open(CHECKLIST, "a", encoding="utf-8").write(CHECKLIST_ADD)
        print("  checklist: added the overwrite-vs-load-existing condition")
    else:
        print("  checklist: anchor MISS (appending anyway)")
        io.open(CHECKLIST, "a", encoding="utf-8").write(CHECKLIST_ADD)

    body = io.open(AUDIT, encoding="utf-8").read()
    if AUDIT_OLD in body:
        io.open(AUDIT, "w", encoding="utf-8").write(body.replace(AUDIT_OLD, AUDIT_NEW, 1))
        print("  audit: (c) now cites the fresh measurement")
    elif "189,090" in body:
        print("  audit: already fresh")
    else:
        print("  audit: (c) anchor MISS")

    for p, marker, text in ((P1, "R707", BLOCKER), (P3, "R707", BLOCKER), (P2, "第 707 轮", VERDICT)):
        b = io.open(p, encoding="utf-8").read()
        if marker in b:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R707: re-measure on the rebuilt artifact -- replica 189,090 functions, C10 still 12/819\n\n"
         "Rebuilt the IDB from scratch on the 11:49 artifact (55,349,248 B): overwrote the stale\n"
         "database, loaded the PDB with types and names, waited for auto_analysis_ready.\n\n"
         "  original  321,244  symbols=no   named 10,041  (3.13%)\n"
         "  replica   189,090  symbols=yes  named 176,784 (93.49%)   +1,358 vs the previous artifact\n"
         "  C10       12/819 = 1.5%  (unchanged)\n\n"
         "+1,358 functions and no movement in C10 means the new validator added real implementation but\n"
         "made no binding member newly visible -- which is the point, and which the function count alone\n"
         "would have read as improved coverage.\n\n"
         "Two tool/document fixes: wait_ready.py treats a refused connection as fatal although the plugin\n"
         "binds its port only near the end of analysis (new analysis/poll_ready.py tolerates it and prints\n"
         "CPU deltas); and the IDA checklist's first modal now states that 'overwrite' is correct when the\n"
         "binary changed, which R691's version did not distinguish."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
