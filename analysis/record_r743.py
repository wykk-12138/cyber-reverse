"""Record R743: the CSV cluster is already implemented in the replica; the open question changes shape."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 172. CSV 簇：**复刻件已经实现了这个区域**，问题从「缺实现」变成「键选择是否一致」

> R743。本轮未改产品代码。

### 一、读了两个，一个太小一个太大

| 候选 | 规模 | 结论 |
|---|---|---|
| `0x140713888` | **16 行** | 解析失败的提示格式化器：取模板、取 `ex.Message`、格式化、弹提示 |
| `0x14071fd80` | **200+ 行、50 个局部变量** | 导出**编排器**，`Exported {0} rows to {1}` 只是其中一句 |

**16 行的可断言，但只有一句 `string.Format`；200 行的不可探。两个都不值得单独写实现。**

### 二、于是去查复刻件有没有这个区域 —— 有

```
Cybersole.Ui\Views\Profiles\ProfileViews.cs      Csv. 引用 50 处
                                                 Couldn / Exported / Ignored unknown columns 各命中
```

**复刻件的 CSV 编辑/导入/导出流程已经存在。** 而它取的键与目录里的文案都对得上
（目录本身就是从原版抽出来的，所以文案一致是**构造上就成立**的）。

### 三、而目录露出的 CSV 文案比我 ranking 里的**多**

`analysis/witness_ranking.py` 只按「函数引用了哪些键」聚合，所以只露出被那 4 个函数引用的几条。
把目录里所有 CSV 键列出来，是 **8 条带占位符的**：

```
ProfileCsv.Status.ParseFailed      Couldn't read the CSV: {0}          ← ranking 里有
ProfileCsv.Status.Exported         Exported {0} rows to {1}            ← 有
ProfileCsv.Status.IgnoredColumns   Ignored unknown columns: {0}        ← 有
ProfileCsv.Status.Imported         Merged {0} rows from {1}            ← **没有**
ProfileCsv.Status.Replaced         Replaced {0} values                 ← 没有
ProfileCsv.ConfirmDeleteFormat     Apply and delete {0} profiles       ← 没有
ProfileCsv.Menu.SelectedCells      {0} CELLS SELECTED                  ← 没有
ProfileCsv.Summary.*               {0} edited / errors / new / removed ← 没有
```

**ranking 的口径是"函数引用了什么"，不是"目录里有什么"。** 两者不等，这一轮才看清。

### 四、于是真正待查的东西变了

**不是**「CSV 簇缺 4 个实现」，**而是**：

> **复刻件在什么条件下选哪条 CSV 文案，与原版是否一致？**

**这个问题可查、有界，而且是新的一类检查**：

- 已知：文案一致（同源目录）、复刻件有这个区域
- **未知：键的选择条件是否一致**

### 五、验证

```
本轮未改产品代码
完整套件        1705 通过 / 0 失败（与 R742 相同）
已审候选        25 / 129（新增 4 个：2 个"复刻件已实现"、1 个"太大"、1 个"太薄"）
```

### 六、仍然 Unknown

- **复刻件选键的条件与原版是否一致**：**Unknown** —— 这是本轮新提出的问题，未查。
- ranking 口径（函数引用）与目录口径（键存在）的差有多大：**Unknown** —— 只在这一簇上看到了。
- `0x14071fd80` 那 200 行里除 `Exported` 之外的行为：**Unknown**（未读；读了也超出探针范围）。
"""

VERDICT = """

---

## 第 743 轮：CSV 簇 —— 复刻件已经实现了它

### 两个候选，一个太小一个太大

| 候选 | 规模 | 结论 |
|---|---|---|
| `0x140713888` | 16 行 | 提示格式化器，可断言但只有一句 `Format` |
| `0x14071fd80` | 200+ 行 | 导出**编排器**，`Exported {0} rows to {1}` 只是其中一句 |

### 复刻件有这个区域

`ProfileViews.cs` 里 **50 处 `Csv.` 引用**，`Couldn` / `Exported` / `Ignored unknown columns` 都命中。

**文案一致是构造上成立的**（目录就是从原版抽的）。

### 而目录里的 CSV 文案比 ranking 多

ranking 的口径是「**函数引用了什么**」，不是「**目录里有什么**」。**两者不等。**

目录里有 **8 条带占位符的 CSV 文案**，ranking 只露了 3 条。

### 于是真正待查的变了

> **不是「CSV 簇缺实现」，而是「复刻件在什么条件下选哪条文案，与原版是否一致」。**

**这是新的一类检查，而且是可查有界的。**

### 一句话

> 我这一轮本来准备"再实现一个"，结果发现**这块早就有了**。
> **而更有用的事是：我发现了自己那张 ranking 表的口径偏差 —— 它数的是函数引用，不是目录内容。**

> **一个判据的口径偏了，它给出的"候选数"就是错的。**

### 验证

```
产品代码未改
完整套件   1705 通过 / 0 失败
已审候选   25 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R743", BLOCKER), (P3, "R743", BLOCKER), (P2, "第 743 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    anchor = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if anchor in body:
        add = ("| `0x140713888` | `ProfileCsv.Status.ParseFailed` | **复刻件已实现**（R743） | "
               "16 行的提示格式化器；`ProfileViews.cs` 已经在用这个键 |\n"
               "| `0x140720f8a` | `ProfileCsv.Status.ParseFailed` | **复刻件已实现**（R743） | 同上，另一个捕获点 |\n"
               "| `0x14071fd80` | `ProfileCsv.Status.Exported` | **不可探**（R743） | 200+ 行、50 局部变量的导出**编排器**；"
               "`Exported` 只是其中一句 |\n"
               "| `0x1407145a0` | `ProfileCsv.Status.IgnoredColumns` | **复刻件已实现**（R743） | 同上 |\n")
        body = body.replace(anchor, add + anchor, 1)
        body = body.replace("## 已审：21 / 129",
                            "## 已审：25 / 129")
        body = body.replace("下一步按 `analysis/witness_ranking.tsv` 读 1 个占位符那一档："
                            "CSV 导入导出簇（`Couldn't read the CSV`、`Exported {0} rows to {1}`、`Ignored unknown columns`）。",
                            "**R743 发现 ranking 口径偏差**：它数的是「函数引用了哪些键」，"
                            "而目录里有 **8 条**带占位符的 CSV 文案，ranking 只露出 3 条。\n\n"
                            "**CSV 区域复刻件已经实现**（`ProfileViews.cs` 有 50 处 `Csv.` 引用）。"
                            "所以真正待查的不是「缺实现」，而是**「在什么条件下选哪条文案，与原版是否一致」** —— "
                            "这是新的一类检查，未见做过。")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R743: the CSV cluster is already implemented -- and the ranking's口径 was measuring the wrong thing\n\n"
         "Two candidates read: 0x140713888 is a sixteen-line toast formatter (assertable but one string.Format),\n"
         "and 0x14071fd80 is a 200-line export orchestrator with fifty locals (not probe material). Neither\n"
         "justifies a new implementation.\n\n"
         "Checking the replica instead: ProfileViews.cs already carries fifty Csv. references, including the\n"
         "three texts the ranking surfaced. The CSV area exists, and the texts match by construction because\n"
         "the catalogue was extracted from the original.\n\n"
         "The finding that matters is about the ranking itself. It aggregates by 'which keys does this function\n"
         "reference', but the catalogue holds eight CSV texts with placeholders while the ranking surfaced\n"
         "three. Those are different questions, and treating the first as if it answered the second\n"
         "understated the area.\n\n"
         "So the open question changes: not 'the CSV cluster lacks four implementations' but 'under what\n"
         "conditions does the replica choose each of these texts, and does that match the original'. That is a\n"
         "bounded, checkable question of a kind not attempted yet.\n\n"
         "No product code changed; suite 1705 pass / 0 fail; 25 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
