"""Record R697: the trap-entry inventory, and gating the export at its source."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = '''

---

## 130. 清点 123 条坑的「操作入口」：**25 条只停在报告里** —— 而"分析中途截断"这一族是其中之一

> R697。工具：`analysis/trap_entry_inventory.py`；改 `analysis/func_compare.py`。

### 一、判据（先定）

一条坑算「有操作入口」需其一：① 某脚本**文件头**（前 45 行，§1.2 要求在那里写理由）提到它的 `R` 编号；
② 某测试文件提到它；③ 操作手册里有对应步骤。否则算「只停在报告里」。

### 二、结果

```
traps (BLOCKERS.md sections carrying round ids): 123
have an operational entry point : 98
report only                     : 25
```

**这个 98 是上界、25 是下界** —— 匹配是宽松的（某 `R` 编号出现在任何测试文件里就算，不一定是为它写的测试）。
**所以「25 条只停在报告里」是可以确信的那一半。**

### 三、25 条里有一条正中要害

```
R610/611  §44. 两侧函数数都曾被"分析中途"截断 —— 差值两端必须同状态
R612      §45. "同口径"钉住了分析选项，但没钉住符号输入
```

**R694 踩的坑属于这一族，而这一族一个操作入口都没有。**

R433 踩过一次（写进 `PARITY_PRODUCT.md` §8）、R610/611 又记了一次（写进 `BLOCKERS.md` §44）、
R694 我第三次踩 —— **三次都写在报告里，三次都没有东西在动手时拦住。**

### 四、修法：把门放在**导出函数**里

`func_compare.py` 的 `export()` 本来就取了 `server_health`，**但拿回来就不看**。现在：

```python
ready = _ready(health)
if ready is not True:
    raise SystemExit(
        "%s: auto_analysis_ready is %r -- refusing to export.\\n"
        "  Port-open is not readiness; functions are still being recognised.\\n"
        "  Wait first:  python analysis/wait_ready.py <port> <timeout>\\n"
        "  Background:  BLOCKERS 44/45 and 129, PARITY_PRODUCT section 8, IDA_STARTUP_CHECKLIST."
        % (label, ready))
```

`_ready()` 兼容四种回包形状（dict 直取、dict 嵌套一层、JSON 文本、缺键）。

**为什么放在这里**：这个坑从来没有在"报告"里被踩到 —— 它只在**运行导出命令**时被踩。
把门放在别处，等于再写一份报告。

### 五、验证到什么程度（不夸大）

```
_ready 单测（5 种回包）:
  dict ready -> True / dict not ready -> False / nested -> True / json text -> True / missing key -> None
```

**已验**：辅助函数对五种形状判断正确；`if ready is not True` 对 `False` 与 `None` 都会抛。
**未验**：**没有对真实「未就绪」实例跑过一次**（两个端口现在都就绪，13339 无监听 → 会先在连接处失败）。
**所以这只是「单测 + 代码审读」，不是「实测拦下」。**

### 六、仍然 Unknown

- 其余 23 条 report-only 的坑要不要同样加门：**Unknown**（逐条判断成本高，且多数是"结论"而不是"动作"）。
- 「98 条有入口」里有多少是**误计**（某 R 编号只是被顺带提到）：**Unknown**。
- 是否需要把这套清点接进 `metrics_report.py` 作为常驻度量：**Unknown**（会引入第五个度量，需 YG 同意）。
'''

VERDICT_TEXT = '''

---

## 第 697 轮：123 条坑，25 条只停在报告里；把门放进导出函数

### 一、判据与结果

> 一条坑算「有入口」需：脚本文件头提到它 / 有测试提到它 / 手册有步骤。

```
123 条坑 → 98 有入口（上界）→ 25 只停在报告里（下界）
```

匹配宽松，所以**能确信的是那 25 条**。

### 二、25 条里有一条正中要害

```
R610/611  §44. 两侧函数数都曾被"分析中途"截断
R612      §45. "同口径"钉住了分析选项，但没钉住符号输入
```

**R694 踩的坑属于这一族，而这一族一个入口都没有。**
R433 写过、R610/611 写过、R694 我第三次踩 —— **三次都在报告里，没有东西在动手时拦住。**

### 三、修法：把门放进 `export()`

`export()` 本来取了 `server_health` 却不看。现在 `auto_analysis_ready is not True` 就 `SystemExit`，
错误信息里带 `wait_ready.py` 的等待命令与三处背景出处。

**为什么放这里**：这个坑只在**运行导出命令**时被踩。门放在别处，等于再写一份报告。

### 四、验到什么程度（不夸大）

```
_ready 单测 5 种回包：True / False / nested True / json text True / missing None
```

**已验**：辅助函数判断正确，`False` 与 `None` 都会抛。
**未验**：**没有对真实未就绪实例跑过一次** —— 所以这是「单测 + 审读」，不是「实测拦下」。

### 五、一句话

> 我一直在给同一条坑写更好的报告，而它需要的是一个门。

> **一份记录被引用了三次、三次都没拦住事 —— 那说明它缺的不是措辞，是位置。**

### 六、下一轮

门已就位。剩下 23 条 report-only 里，多数是「结论」而非「动作」，不该都加门。
下一轮挑其中**会重复动作**的几条（例如 §37 持久化文件布局、§47/48/49 函数大小归因），
判断哪条值得同样的处置 —— 其余在 `BLOCKERS.md` 里标注「结论型，无需门」，把这份清点结掉。
'''


def main():
    for p, marker, text in ((P1, "R697", BLOCKER), (P3, "R697", BLOCKER), (P2, "第 697 轮", VERDICT_TEXT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R697: record the trap-entry inventory (25 report-only, incl. the truncation family)"],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:150]))


if __name__ == "__main__":
    main()
