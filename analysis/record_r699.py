"""Record R699: every export now states whether symbols were loaded, and the asymmetry is visible."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
CLOSURE = r"D:\projects\cyber-reverse\docs\TRAP_ENTRY_CLOSURE.md"

BLOCKER = '''

---

## 132. §45 的门装上了：导出文件第一行自带口径 —— 而它立刻证出两侧**符号条件不对称**

> R699。改 `analysis/func_compare.py`（`EXPORT_TEMPLATE` + `export()`）。

### 一、判据（R698 已定）

> 导出文件**第一行**必须能回答「这个数带不带符号」。

### 二、怎么判（Inference，不是 Observation）

`server_health` **没有任何字段**报告符号是否加载。所以用**非 `sub_` 名字占比**作代理：
R613 自己的两个基线是 **93%**（带符号）与 **2.1%**（不带），相差一个数量级。

```
ratio > 0.5  -> symbols=yes
ratio < 0.1  -> symbols=no
否则         -> symbols=unknown
```

**并且把头行里印出原始 `ratio`**，读者可以不同意这个判定。

### 三、实测结果

```
original: # exportspec symbols=no   named=10041   total=321244 ratio=0.0313
replica : # exportspec symbols=yes  named=175495  total=187732 ratio=0.9348
```

**它立刻证出一件比 §45 原话更重的事：两侧的符号条件相差一个数量级，而之前所有"函数数对照"都在这个不对称下做的。**

- 原版 IDB：**3.13%** 有名字（10,041 条，来自 PE 导出表 / CRT，**从未加载过 PDB**）
- 复刻件 IDB：**93.48%** 有名字（175,495 条，**加载了 PDB**）

**所以 `321,244 ↔ 187,732` 这个对照，是"符号贫乏的一侧"对"符号丰富的一侧"。**
R613 为了消掉这一维，专门重建了不带 PDB 的库（得 186,732）——**那个数才是同口径的**。

### 四、验证

| 检查 | 结果 |
|---|---|
| 两个导出文件第一行都有 `# exportspec symbols=` | ✓ |
| `export()` 会**回读文件**校验头行（不信 stdout） | ✓ 缺头即 `SystemExit` |
| 下游 `load_rows` 跳过它 | ✓ 无制表符 → `len(parts) < 3` → 跳过 |
| 下游 `aot_member_coverage.py` 结果不变 | ✓ **仍 12 / 819 = 1.5%** |

### 五、仍然 Unknown

- `ratio` 代理在中间区（0.1–0.5）会判 `unknown`，**实测两侧都在区间外**，但中间情形未遇过。
- 原版如果加载 PDB 后函数数会变多少：**Unknown**（R613 只做了复刻件那一侧）。
- 同口径的 `321,244 ↔ 186,732` 与带符号的 `321,244 ↔ 187,732` 该用哪个作为"函数数量对等"的口径：**Unknown** —— 需要 YG 或更多证据决定，我不自行选。
'''

VERDICT_TEXT = '''

---

## 第 699 轮：§45 的门装上了，而它立刻证出两侧符号条件**不对称**

### 一、判据（上轮已定）

> 导出文件第一行必须能回答「这个数带不带符号」。

### 二、判法（Inference）

`server_health` 没有这个字段。用**非 `sub_` 名字占比**作代理 —— R613 的两个基线是 93% / 2.1%，差一个数量级。
头行同时印出原始 `ratio`，读者可以不同意判定。

### 三、实测：**不对称被写进数据**

```
original: symbols=no    ratio=0.0313   named=10,041  / 321,244
replica : symbols=yes   ratio=0.9348   named=175,495 / 187,732
```

**这比 §45 原话更重**：之前所有「函数数对照」都做在**符号贫乏侧 vs 符号丰富侧**之上。
R613 专门重建了不带 PDB 的库得 **186,732**，**那个才是同口径的**。

### 四、验证

```
两文件首行都有 exportspec        ✓
export() 回读文件校验（不信 stdout） ✓  缺头即 SystemExit
load_rows 跳过（无制表符）        ✓
aot_member_coverage 结果不变       ✓  仍 12/819 = 1.5%
```

### 五、一句话

> 我在数据里加了一行字，它证明的是：**我一直在拿两种不同的东西对比。**

> **口径不一致不会报错，它只会在数字里留下一个解释不了的差。
> 加一行口径说明，比把那个差解释清楚更省事 —— 也更诚实。**

### 六、下一轮（最后一轮）

本轮把 25 条清点里唯一的动作型差距补完了。最后一轮做**收尾核对**：
逐条走完成判据 (a)–(e)，列出每条的证据与**仍未满足的部分**，并把目标状态说清楚 ——
不为了"完成"而把未满足的写成满足。
'''

def main():
    for p, marker, text in ((P1, "R699", BLOCKER), (P3, "R699", BLOCKER), (P2, "第 699 轮", VERDICT_TEXT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # close the last open item in the closure document
    body = io.open(CLOSURE, encoding="utf-8").read()
    if "R699 已关闭" in body:
        print("  closure: already marked")
    else:
        body = body.replace(
            "| **§45（R612）** | \"同口径\"钉住了分析选项，但**没钉住符号输入** | 每次建 IDA 库都要选 PDB 是/否；R613 实测这改变 `cc`（129↔1）与函数数（186,732↔187,698） | **门不完整**：R697 的 `export()` 只查 `auto_analysis_ready`，**没有记录 PDB 是否加载** |",
            "| **§45（R612）** | \"同口径\"钉住了分析选项，但**没钉住符号输入** | 每次建 IDA 库都要选 PDB 是/否；R613 实测这与函数数相关（186,732 ↔ 187,698） | **R699 已关闭**：导出文件首行带 `# exportspec symbols=yes\\|no\\|unknown ... ratio=...`，`export()` 回读校验 |",
            1)
        io.open(CLOSURE, "w", encoding="utf-8").write(body)
        print("  closure: §45 marked closed")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R699: every function export states whether symbols were loaded\n\n"
         "BLOCKERS 45 recorded that the symbol input was never pinned. server_health has no such field,\n"
         "so the header uses the non-sub_ name ratio as a proxy (R613 baselines: 93% vs 2.1%).\n\n"
         "It immediately shows the two sides are asymmetric: original ratio 0.0313 (no PDB ever loaded),\n"
         "replica 0.9348 (PDB loaded). So 321,244 vs 187,732 compares a symbol-poor side with a\n"
         "symbol-rich one; R613's 186,732 (rebuilt without PDB) is the equal-option figure.\n"
         "export() reads the header back rather than trusting stdout. Downstream unchanged: 12/819."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
