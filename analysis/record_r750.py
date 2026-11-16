"""Record R750: the 0/1/n split the ranking was blind to, and two counters implemented from it."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 179. **0 / 1 / n** 三段文案：我的 ranking 只数了 `{0}` 那一条，漏了三分之二

> R750。新增 `replica/src/Cybersole.Core/Reporting/SmartActionSavedCounts.cs`、对应 9 条探针。

### 一、读完整函数，是三段不是两段

`sub_140600020`（31 行，全读）：

```c
v4 = a2;                                  // 计数
if ( (_DWORD)a2 )                          // != 0
{
    if ( (_DWORD)a2 == 1 )
        return localise(&off_146E90CC8);         // "1 Filter Saved"
    else
    {
        *(_DWORD *)(box + 8) = v4;
        return format(&off_146E90D18, box);      // "{0} Filters Saved"
    }
}
else
    return localise(&off_146E91018);             // "No Filters"
```

**0 / 1 / n —— 而 `1` 那一档有独立句子、数字是写死的。**

**与 R731 的 `TaskButtonLabel` 是同一种不对称**（那里是 `count == 1` 对 `count >= 2`）。

### 二、我先前那一眼只看到两段 —— 因为分支里还套着分支

第一遍我只看到 if/else 两支（`{0} Filters Saved` 与一条无占位符的），
**以为"两条文案"**。读完整才发现 `if` 里面还套了 `== 1`。

**31 行的函数也不能只看前 14 行。**

### 三、ranking 的系统性盲区（第二次发现）

`analysis/witness_ranking.py` 按**带占位符的文案**排序。而这一簇的每条统计有**三条**：

| count | filters | actions |
|---|---|---|
| 0 | `NoFilters` = "No Filters" | `NoActions` = "No Actions" |
| **1** | **`FilterOne` = "1 Filter Saved"** | **`ActionOne` = "Action One Saved"** |
| n | `FiltersFormat` = "{0} Filters Saved" | `ActionsFormat` = "{0} Actions Saved" |

**ranking 只露出 n 那一条。** R743 在 CSV 簇上发现过同类偏差（ranking 数「函数引用了什么」而非「目录里有什么」）；
**这次是第二种偏差：只数带占位符的，于是 0 和 1 那两档整类不可见。**

**两条偏差的后果相同：我的候选表低估了区域规模。**

### 四、探针钉的是**边界**，不是文本

- `TheFiltersCounterSplitsAtZeroAndOne`（0/1/2/7）
- `OneIsItsOwnSentenceNotTheFormat`：**`Filters(1)` 既不是 `{0}…` 代入 1，也不是 "1 Filters Saved" 的复数错写**
- `ANegativeCountIsFormattedRatherThanTreatedAsNone`：**反编译的条件是「非零、再等于一」，没有下界**
  —— 所以 `-2` 走格式化那支，输出 `-2 Filters Saved`。**一个"更合理"的实现会把它当归零处理。**

### 五、验证

```
SmartActionSavedCountsTests   9 / 9 通过
完整套件                      1725 通过 / 0 失败（1716 + 9）
四项度量                      4 / 0 / 17 / 78 / 0（未变）
已审候选                      28 / 129（`0x140600020`、`0x1406000e0` 实现）
```

### 六、仍然 Unknown

- `sub_1406000E0`（actions）的逐行分支：**Inference（高）** —— 同为 31 行同形，尾部读过，**未逐行比对**
- `SmartActionsCreator.BehaviourFormat` = `{0} if`（`0x1405ffd50`）是否也是 0/1/n：**Unknown**，未读
- 负数计数在原版里是否真会出现：**Unknown** —— 只知代码没有下界守卫
"""

VERDICT = """

---

## 第 750 轮：0 / 1 / n 三段文案

### 读完整函数，是三段

```c
if (a2) {
    if (a2 == 1) return "1 Filter Saved";       // 数字写死
    else         return format("{0} Filters Saved", a2);
} else return "No Filters";
```

**与 R731 是同一种不对称。**

### 我先前那一眼只看到两段

第一遍只看到 if/else 两支，**以为"两条文案"**。读完整才发现 `if` 里还套了 `== 1`。

> **31 行的函数也不能只看前 14 行。**

### ranking 的第二次系统性盲区

它按**带占位符的文案**排序。而这一簇每条统计有**三条**：`No X` / `1 X Saved` / `{0} X Saved`。

**ranking 只露出 n 那一条 —— 0 和 1 那两档整类不可见。**

R743 在 CSV 簇上发现过第一种偏差（数「函数引用了什么」而非「目录里有什么」）；
**这是第二种：只数带占位符的。两条偏差后果相同 —— 我都低估了区域规模。**

### 探针钉边界，不钉文本

- `Filters(1)` **既不是** `{0}…` 代入 1，**也不是** "1 Filters Saved" 的复数错写
- **`-2` 走格式化那支** —— 反编译条件是「非零、再等于一」，**没有下界**。
  **一个"更合理"的实现会把它当归零。**

### 验证

```
SmartActionSavedCountsTests   9 / 9
完整套件                      1725 通过 / 0 失败
四项度量                      4 / 0 / 17 / 78 / 0（未变）
已审候选                      28 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R750", BLOCKER), (P3, "R750", BLOCKER), (P2, "第 750 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    anchor = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if anchor in body:
        add = ("| `0x140600020` | `SmartActionsCreator.Filters*` | **已实现**（R750，9 条探针） | "
               "**0/1/n 三段**：`No Filters` / `1 Filter Saved`（数字写死）/ `{0} Filters Saved`；"
               "条件无下界，负数走格式化 |\n"
               "| `0x1406000e0` | `SmartActionsCreator.Actions*` | **已实现**（R750） | 同上，同形 31 行 |\n")
        body = body.replace(anchor, add + anchor, 1)
        body = body.replace("## 已审：26 / 129", "## 已审：28 / 129")
        body = body.replace("**R743 发现 ranking 口径偏差**",
                            "**R750 发现 ranking 的第二种偏差**：只数带占位符的文案，"
                            "于是 0/1/n 三段里 0 和 1 那两档整类不可见（`No Filters` / `1 Filter Saved` 都无占位符）。"
                            "\n\n**R743 发现的第一种**")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R750: the 0/1/n split -- three sentences per counter, and the ranking only ever saw one\n\n"
         "sub_140600020 is 31 lines and reads as if it has two branches. Reading all 31 shows the non-zero\n"
         "branch holds another branch on == 1, so there are three sentences: 'No Filters', '1 Filter Saved'\n"
         "with the digit written out, and '{0} Filters Saved' from two upwards. A negative count is formatted\n"
         "rather than treated as none, because the condition tests non-zero then equality with one and has no\n"
         "lower bound.\n\n"
         "Implemented both counters with nine probes that pin the boundaries rather than the wording: that one\n"
         "is neither the format substituted with 1 nor a mis-pluralised '1 Filters Saved', and that -2 is\n"
         "formatted. A tidier implementation would classify -2 as none.\n\n"
         "The reason this was missed is the ranking. It orders candidates by placeholder-carrying texts, and\n"
         "each of these counters has three sentences of which only the formatted one carries a placeholder -- so\n"
         "the zero and one cases were invisible as a class. That is the second口径 fault found in that script;\n"
         "R743 found the first when it counted 'keys a function references' rather than 'keys in the catalogue'.\n"
         "Both understated how large an area really is.\n\n"
         "Also worth keeping: I looked at 14 lines of a 31-line function the first time and concluded 'two\n"
         "sentences'. Partial reads mislead even at this size.\n\n"
         "Suite 1725 pass / 0 fail; four metrics unchanged; 28 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
