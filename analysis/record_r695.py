"""Record R695: the three replica function counts are three measurement conditions, and the R694 trap was documented."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
CLAIMS = r"D:\projects\cyber-reverse\docs\PARITY_CLAIMS.md"

BLOCKER = """

---

## 128. C6 的三个数不是矛盾，是**三种测量条件**；而 R694 那个坑 **R433 早就写进文档了**

> R695。工具：`docs/PARITY_PRODUCT.md` 全文检索。

### 一、三个数各自的成立条件

| 数 | 条件 | 出处 |
|---|---|---|
| **187,328** | **带 PDB** | R433（第一次取到 **136,798**，重取后为 187,328） |
| **187,698** | **带 PDB** | R613 的表里那一列 |
| **186,732** | **不带 PDB**（同口径基准） | R613 重建库时 PDB 选 No |
| **187,732** | **带 PDB** + 当前源码产物（55,080,448 B） | R694 |

**R613 已经把条件列成表**：`auto_analysis_ready`、是否加载 PDB、`cc`、函数数、有符号名 —— 六项对齐。

**所以 186,732 与 187,698/187,732 不是矛盾的两份测量，是「不带 PDB」与「带 PDB」两种口径。**
带 PDB 的三个数（187,328 / 187,698 / 187,732）差 370，是**三版产物**，不是三次误差。

### 二、更难堪的发现：R694 那个坑，R433 已经写下来了

`PARITY_PRODUCT.md` §8 里原文写着：

> **踩过的坑（R433）**：第一次取复刻件函数数得 136,798，重取得 187,328。
> 原因是 **IDA 插件端口 open ≠ 自动分析完成** —— 端口在 PDB 加载阶段就监听了，函数还在持续识别。
> 判据是**窗口标题不再带 `Loading`** 且**连续两次取值相同**（187,328 两次一致）。

**而 R613 用的判据就是 `auto_analysis_ready: true`（t=240s）。**

**所以 R694 我不是发现了一个新陷阱，是重复了一个已经写在文档里的陷阱。**
而且我当时写的"抓住它的不是工具，是那个反常"—— **那句话说得太客气了**：
真正该抓住它的是那份文档，我只要在导出前读一眼 §8 就不会发生。

### 三、两次现象的对比（说明这个坑很稳定）

| | 第一次（错误） | 第二次（正确） | 倍数 |
|---|---|---|---|
| R433 | 136,798 | 187,328 | 0.730 |
| R694 | 136,989 | 187,732 | **0.730** |

**同一个比值，隔了 260 多轮。** 这说明它不是偶发，是**IDB 自动分析在 PDB 加载阶段的一个稳定中间态**。

**这个"稳定"反而危险**：任何人在那个窗口内取数，都会得到一个**看起来合理、且两次可能相同**的偏小数。

### 四、已做处置

`PARITY_CLAIMS.md` 的 C6 已补上三个数的条件；`docs/IDA_STARTUP_CHECKLIST.md` 已有「端口开 ≠ 分析完」一节
（R694 写的，判据是 `wait_ready.py`）。

**现在两份文档都说这件事**：一份在产物对照里（历史记录），一份在启动清单里（操作手册）。
**问题是它们互不引用。**

### 五、仍然 Unknown

- 187,328 / 187,698 / 187,732 三版产物之间除了函数数还有哪些差：**Unknown**（未做产物级 diff）。
- `.pdata` 口径 170,137 与 186,732 的换算关系：**Unknown**（C9 仍 unknown）。
- R433 那次 136,798 与 R694 的 136,989 差 191：**Unknown**（不同产物，比值相同）。
"""

VERDICT_TEXT = """

---

## 第 695 轮：C6 三个数是三种条件；R694 的坑 R433 早写过

### 一、三个数的条件

| 数 | 条件 | 出处 |
|---|---|---|
| **187,328** | 带 PDB | R433（首取 136,798） |
| **187,698** | 带 PDB | R613 |
| **186,732** | **不带 PDB**（同口径基准） | R613 |
| **187,732** | 带 PDB + 当前产物 | R694 |

**186,732 与 187,698 不是矛盾，是两种口径。** 带 PDB 的三个数差 370，是**三版产物**。

### 二、更难看的部分

`PARITY_PRODUCT.md` §8 原文：

> **踩过的坑（R433）**：第一次得 136,798，重取得 187,328。
> 原因是 **IDA 插件端口 open ≠ 自动分析完成**。判据是**窗口标题不带 `Loading`** 且**连续两次取值相同**。

**而 R613 用的判据就是 `auto_analysis_ready`。**

**所以 R694 我不是发现了新陷阱，是重复了一个写在文档里的陷阱。**
我当时写「抓住它的不是工具，是那个反常」——**这句话太客气了：该抓住它的是那份文档。**

### 三、这个坑很稳定，所以更危险

| | 错误值 | 正确值 | 比值 |
|---|---|---|---|
| R433 | 136,798 | 187,328 | 0.730 |
| R694 | 136,989 | 187,732 | **0.730** |

**同一个比值，隔 260 多轮。** 它不是偶发，是自动分析在 PDB 阶段的一个**稳定中间态**。
**稳定 = 任何人取两次都可能得到同一个偏小数，然后以为一致。**

### 四、一句话

> 教训写在文档里，不等于教训生效。

> **这一轮真正的发现不是"三个数怎么回事"，是"我重复了一个已经记下来的错"。
> 文档写对了、判据也有了、工具也做了 —— 唯独没在动手前读它。**

### 五、下一轮

两份文档（`PARITY_PRODUCT.md` §8 与 `IDA_STARTUP_CHECKLIST.md`）现在各说一遍同一件事却**互不引用**。
下一轮把它们相互链接，并在 `wait_ready.py` 的文件头注明它替代了 R433 的"窗口标题"判据 ——
让下一次的人（或我）在读代码时就被拦住。
"""


def main():
    for p, marker, text in ((P1, "R695", BLOCKER), (P3, "R695", BLOCKER), (P2, "第 695 轮", VERDICT_TEXT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # name the three conditions in C6
    body = io.open(CLAIMS, encoding="utf-8").read()
    old = "**R613 同口径复测为 321,244 ↔ 186,732**（两侧分析选项一致后，见 `PARITY_PRODUCT.md` R613 节）"
    new = ("**三个复刻件数各有条件，不是三份矛盾的测量**：187,328（R433，带 PDB）、"
           "187,698（R613，带 PDB）、**186,732（R613，不带 PDB，即同口径基准）**、"
           "187,732（R694，带 PDB + 当前源码产物）。"
           "带 PDB 的三个数差 370 是**三版产物**，不是误差；186,732 与它们的差是 **PDB 口径**（R613 实测 PDB 影响 +966 = 0.5%）")
    if new in body:
        print("  claims: C6 already annotated")
    elif old in body:
        io.open(CLAIMS, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  claims: C6 now names the conditions")
    else:
        print("  claims: C6 MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R695: C6's three replica counts are three conditions, and R694's trap was already documented\n\n"
         "187,328 (R433, with PDB), 187,698 (R613, with PDB), 186,732 (R613, WITHOUT PDB -- the\n"
         "equal-option baseline), 187,732 (R694, with PDB, current artifact). The 370 gap between the\n"
         "with-PDB numbers is three artifact generations, not error.\n\n"
         "PARITY_PRODUCT.md section 8 already recorded this exact premature-measurement trap at R433 and\n"
         "gave a criterion for it; R613 used auto_analysis_ready too. So R694 repeated a documented\n"
         "lesson rather than discovering one. The wrong/right ratio is 0.730 in both cases, 260 rounds\n"
         "apart, which makes the intermediate state stable enough that two samples can agree on it."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True,
    )
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:200]))


if __name__ == "__main__":
    main()
