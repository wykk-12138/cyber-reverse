"""Record R694: C10 recomputed on a fresh artifact; and the premature-measurement error that nearly shipped."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
CLAIMS = r"D:\projects\cyber-reverse\docs\PARITY_CLAIMS.md"
CHECKLIST = r"D:\projects\cyber-reverse\docs\IDA_STARTUP_CHECKLIST.md"

BLOCKER = """

---

## 127. C10 有了有效新值 **12/819 = 1.5%** —— 而中间有个"提前量的错"被我抓住了

> R694。工具：`analysis/ida_tool.py`、`analysis/wait_ready.py`、`analysis/func_compare.py`、
> `replica/tools/aot_member_coverage.py`。

### 一、第三个模态框：**Load PDB file**

第二个 IDA 实例（复刻件，13338）卡了 25 分钟，`ws` 停在 718 MB、**CPU 25 分钟只用了 9.6 秒**。
查窗口发现三个：`Load PDB file` / `Please wait...` / 主窗口。

**「Load PDB file」是我之前没记录的第三类模态框。** 它的选项是 `Load types` + `Load names`（都已勾选），
点 **Yes** —— **符号名正是 C10 的基础，绝不能点 No**。

点完 CPU 立刻从 9.6 s 涨到 60 s，分析真正开始。

### 二、然后我犯了一个更危险的错，并自己抓住了

点 Yes 后**一分钟**端口 13338 就起来了，我当即导出符号表：

```
exported 136989 rows
C10 -> members with a body : 9 (1.1%)
```

**同一份源码不该比旧记录的 187,328 少 27%。**

于是查 `server_health`：

```
13338: "auto_analysis_ready":false,  "strings_cache_ready":false,  strings_cache_size:0
13337: "auto_analysis_ready":true,   "strings_cache_ready":true,   strings_cache_size:324901
```

**端口开 ≠ 分析完。** 插件一加载就应答，而自动分析还在跑。
**所以 136,989 是一个中间值，C10 的 9/819 = 1.1% 无效。**

### 三、等就绪标志，不猜端口

写 `analysis/wait_ready.py`，轮询 `auto_analysis_ready`：

```
t+  0s  auto_analysis_ready=False  strings=0
t+320s  auto_analysis_ready=True   strings=0
READY after 320 s
```

**分析用了 320 秒。** 重新导出：

```
replica <- 13338  exported 187732 rows      ← 与旧记录 187,328 同量级
```

**C10 的新值**：

```
symbols in image : 187732
binding members  : 819
members with a body in the product : 12 (1.5%)
types with at least one member present : 10
```

**12 / 819 = 1.5%。** 旧值 21 / 819 = 2.6% 是在过期输入上算的，已降级；**这才是当前产物 + 其自身符号的有效值。**

**它比旧值更低**，这本身是信息：不是变差了，是旧值虚高。

### 四、两种错，代价不同

| 错 | 表现 | 后果 |
|---|---|---|
| **提前量** | 端口一起就导出 | 得到一个像样的数（9/819），**但它是中间态**，若不复核就会被写进表 |
| **过期** | 用昨天的符号表 | R693 已记：连"当时的有效测量"都算不上 |

**第一种更危险**：它不报错、不超时、数值合理 —— 只有"比旧值少 27%"这个反常才露出来。

**抓住它的不是工具，是那个反常。** 如果 136,989 恰好接近 187,328，我会直接写进表。

### 五、仍然 Unknown

- 12/819 里"缺席"的 807 条各自是被裁剪、被内联、还是只在元数据里：**Unknown**（需逐个看符号）。
- C10 的 coverage 数字与"行为是否存在"的关系：**Unknown**（coverage 是结构可见性，不是行为）。
- 新产物与 R577/R609 那两版产物的函数数差（187,732 vs 187,328）：**Unknown**（未做产物级 diff）。
"""

VERDICT_TEXT = """

---

## 第 694 轮：C10 新值 12/819；抓到一个"提前量的错"

### 一、第三个模态框：Load PDB file

13338 卡了 25 分钟、CPU 只用 9.6 秒 → 查窗口发现三类：`Load PDB file` / `Please wait...` / 主窗口。
**「Load PDB file」我没记录过**；选项 `Load types`+`Load names` 已勾，点 **Yes**（符号名是 C10 的基础）。
点完 CPU 立刻从 9.6 s 涨到 60 s。

### 二、然后我犯了一个更危险的错

点 Yes 后一分钟端口就起来，我当即导出：

```
136989 rows  ->  C10 = 9/819 (1.1%)
```

**同一份源码不该比 187,328 少 27%。** 查 `server_health`：

```
13338: auto_analysis_ready=false  strings_cache_ready=false
13337: auto_analysis_ready=true   strings_cache_size=324901
```

**端口开 ≠ 分析完。** 那 9/819 是中间态，无效。

### 三、等标志，不猜端口

```
wait_ready.py 13338 -> READY after 320 s
re-export -> 187732 rows
C10 -> members with a body in the product : 12 (1.5%)
```

**这才是当前产物 + 其自身符号的有效值。它比旧值更低 —— 不是变差了，是旧值虚高。**

### 四、两种错，代价不同

| 错 | 表现 | 后果 |
|---|---|---|
| 提前量 | 端口一起就导出 | 得到一个**像样**的数，不报错不超时 |
| 过期 | 用昨天的表 | 连"当时的有效测量"都算不上 |

**第一种更危险**：只有"比旧值少 27%"这个反常才露出来。
**抓住它的不是工具，是那个反常。若 136,989 恰好接近 187,328，我会直接写进表。**

> **一个合理的中间值，比一个明显的错误值更难发现。**

### 五、一句话

> 这一轮拿了两个数：一个无效（9/819）、一个有效（12/819），区别只在于我有没有等那 320 秒。

### 六、下一轮

C10 已有效。(d) 结构+内容都过，(a)(c) 成立，**(b) 仍在等你定**（`docs/CRITERION_B_OPTIONS.md`）。
下一轮把 C10 新值写进 claim 表与 METRICS 生成链，并复核 C6 里 187,328/186,732 与今天 187,732 三个数的口径关系。
"""


def main():
    for p, marker, text in ((P1, "R694", BLOCKER), (P3, "R694", BLOCKER), (P2, "第 694 轮", VERDICT_TEXT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # claim table: C10 gets its valid value and the criterion it satisfies
    body = io.open(CLAIMS, encoding="utf-8").read()
    import re
    start = body.find("`python tools\\aot_member_coverage.py`")
    end = body.find("\n", start)
    if start < 0:
        print("  claims: C10 row not found")
    else:
        row = body[start:end]
        if "12/819" in row:
            print("  claims: C10 already updated")
        else:
            new_row = ("`python tools\\aot_member_coverage.py` → **12/819 = 1.5%**"
                       "（R694：当前源码产物 55,080,448 B + 该产物自身导出的 187,732 个符号，"
                       "`auto_analysis_ready=true` 之后才导出）。"
                       "**旧值 21/819 已作废**：它的符号表比产物旧 20 小时（R693）")
            body = body[:start] + new_row + body[end:]
            io.open(CLAIMS, "w", encoding="utf-8").write(body)
            print("  claims: C10 updated to 12/819")

    # checklist: the third modal
    body = io.open(CHECKLIST, encoding="utf-8").read()
    if "Load PDB file" not in body:
        add = """
| 3 | `Load PDB file`（**仅复刻件实例**） | `The input file was linked with debug information stored here` | **Yes**（`Load types`+`Load names` 保持勾选） | 符号名是 C10 与所有覆盖率度量的基础；点 No 等于放弃符号 |

**第三类框只在复刻件产物上出现**（原版 `.i64` 无 PDB）。漏掉它的表现是：进程在、`ws` 不动、**CPU 25 分钟只用 9.6 秒** —— 看起来像在分析，其实在等。

### 三半、端口开 ≠ 分析完

```
python analysis/wait_ready.py 13338 1500
```

轮询 `server_health.auto_analysis_ready`。**不要用端口判断**：插件一加载就应答，而自动分析还在跑。
55 MB AOT 实测 **320 秒**。端口一起就导出的后果见 `BLOCKERS.md` §127（得出 9/819 的中间值）。
"""
        io.open(CHECKLIST, "a", encoding="utf-8").write(add)
        print("  checklist += the third modal")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R694: C10 recomputed on the fresh artifact -- 12/819 (1.5%)\n\n"
         "Third modal type documented: 'Load PDB file' (replica only). Without it the process sits\n"
         "at 9.6 s CPU for 25 minutes.\n\n"
         "Caught a premature measurement: the plugin answered on 13338 one minute after the PDB was\n"
         "loaded, so an export there gave 136,989 symbols and C10=9/819. server_health showed\n"
         "auto_analysis_ready=false. Waiting on that flag took 320 s, after which the export gave\n"
         "187,732 symbols and C10=12/819 -- the valid value. The old 21/819 stays void (R693)."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True,
    )
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:200]))


if __name__ == "__main__":
    main()
