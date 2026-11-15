"""Record R698: the closure, the three false negatives, and the single remaining ungate."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = '''

---

## 131. 清点结案：**真正没门的动作型只有 1 条**（R697 写的 2 条里有一条本来就有门）

> R698。新增 `docs/TRAP_ENTRY_CLOSURE.md`。

### 一、清点工具量的是「引用」，不是「覆盖」

三处假阴性暴露同一个结构缺陷：**一棵坑由"发现它的那一轮"编号，而修它的工具由"修它的那一轮"编号。**

| 段 | 坑的轮号 | 门在哪 | 门的轮号 | 为什么漏 |
|---|---|---|---|---|
| §37 | **R599** | `replica/tools/datafiles_diff.py`（已接进 `metrics_report.py`） | **R600** | **差一轮**，按编号匹配连不起来 |
| §54 | R621 | 该节自己写着「有守卫」 | — | 守卫测试没引用 `R621` |
| §118 | R655/683/685 | `type_presence_triage.py` + `TypePresenceTriageTests` | — | 同上 |

**所以 98 是上界、25 是下界，两者都不是真值。** 它量的是「有没有人写下那个编号」。

### 二、§37 不但有门，门还把它标 Unknown 的那点答了

`python tools/datafiles_diff.py`（R698 复跑）：

```
files on disk : 11          image literals: 23          replica references: 12
original-on-disk but not written by the replica : 0
literal-only (a string in the image, not a file) : 13   ... products.json, public.json, sku-stores.json ...
replica-referenced, found in neither source      : 1    license.json
```

**§37 当时判 Unknown 的正是**「原版是否真的写 `products.json` / `sku-stores.json` / `public.json`」。
**答案：它们是 literal-only —— 只是镜像里的字符串，磁盘上没有这些文件。**
而 **`original-on-disk but not written by the replica: 0`** —— 原版真正写的 11 个文件，复刻件全写。

**§37 说的"5 个不重合"，实际只剩 1 个真差异**（`license.json`）。

### 三、唯一真的没门的一条：§45

| 段 | 坑 | 现状 |
|---|---|---|
| **§45（R612）** | "同口径"钉住了分析选项，但**没钉住符号输入** | R697 的 `export()` 只查 `auto_analysis_ready`，**没记录 PDB 是否加载** |

**为什么这条算动作型**：每次建 IDA 库都要选 PDB 是/否，而 R613 实测这改变 `cc`（129 ↔ 1）
与函数数（186,732 ↔ 187,698）。**不记录它，186,732 与 187,698 这种差会被当成"产物变了"。**

### 四、结案账

```
25 条 report-only
  ├─ 假阴性   3 条  →  §37 / §54 / §118 本来就有门
  ├─ 待定     2 条  →  等 YG（判据 b 口径，同一主题）
  ├─ 结论型  19 条  →  不加门，正确
  └─ 动作型   1 条  →  §45 的门缺 PDB 维度 ← 唯一待办
```

**R697 写「动作型 2 条」是错的 —— 把已关门的 §37 算了进去。**

### 五、仍然 Unknown

- §45 的门加完后能否复现 186,732/187,698 的差：**Unknown**（未做）。
- 用**主题**（文件名/函数名/指标名）替代轮号匹配，能查出多少今天算错的：**Unknown**（改造未做）。
- `license.json` 在原版里是否以别的名字存在：**Unknown**（`datafiles_diff.py` 说两处源都没有）。
'''

VERDICT_TEXT = '''

---

## 第 698 轮：清点结案 —— 真正没门的只有 **1 条**

### 一、工具量的是「引用」，不是「覆盖」

三处假阴性同一个根因：**坑由"发现轮"编号，门由"修复轮"编号。**

| 段 | 坑的轮号 | 门的轮号 | 为什么漏 |
|---|---|---|---|
| §37 | **R599** | **R600**（`datafiles_diff.py`） | **差一轮** |
| §54 | R621 | 该节自写「有守卫」 | 守卫未引用编号 |
| §118 | R655/683/685 | `TypePresenceTriageTests` | 同上 |

**98 是上界、25 是下界，都不是真值。**

### 二、§37 有门，而且门把它标 Unknown 的那点答了

```
files on disk 11   literal-only 13   original-on-disk-but-not-written-by-replica: 0
products.json / sku-stores.json / public.json 是 literal-only —— 镜像字符串，磁盘上没有
```

**§37 的"5 个不重合"实际只剩 1 个真差异**（`license.json`）。

### 三、唯一真没门：§45（PDB 维度）

`export()` 只查 `auto_analysis_ready`，**没记录 PDB 是否加载** —— 而 R613 实测这改变 `cc`(129↔1)
与函数数(186,732↔187,698)。**不记它，这种差会被误当成"产物变了"。**

### 四、结案账（修正 R697）

```
假阴性 3 · 待定 2 · 结论型 19 · 动作型 1
```

**R697 写「动作型 2 条」是错的 —— 把已关门的 §37 算了进去。**

### 五、一句话

> 我用一个量「引用」的工具去量「覆盖」，然后把量出来的差当成了待办清单。

> **上界和下界之间那 73 条的差，不是"不确定"，是我问错了问题。
> 真正该问的是"这个动作有没有门"，而门不一定会写下那个编号。**

### 六、下一轮（最后一轮之前）

只剩 **§45 的 PDB 维度**。下一轮把它加进 `export()`：
导出时读 `list_funcs` 之外的符号视图，**记录"是否加载符号"并写进导出文件头**，
使 186,732 与 187,698 这类差在数据里自带口径说明。判据先定：导出文件第一行必须能回答"这个数带不带符号"。
'''

def main():
    for p, marker, text in ((P1, "R698", BLOCKER), (P3, "R698", BLOCKER), (P2, "第 698 轮", VERDICT_TEXT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R698: closure -- only one trap (§45 PDB dimension) is truly ungated\n\n"
         "Three false negatives (§37, §54, §118) because a trap is numbered by the round that found\n"
         "it while the gate is numbered by the round that fixed it: §37's gate is datafiles_diff.py,\n"
         "cited R600 vs the section's R599. So the inventory measures citations, not coverage.\n\n"
         "§37's gate also answers what §37 left Unknown: products/sku-stores/public are literal-only,\n"
         "and original-on-disk-but-not-written-by-the-replica is 0."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
