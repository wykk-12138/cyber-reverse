"""Record R744: two CSV gaps found, and a wrong fix avoided by reading the enclosing method."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 173. CSV 键选择对账：**两个真缺口**，以及一次**没有做出去的错改**

> R744。本轮未改产品代码 —— 原因见第三节。

### 一、先看以前的轮次做没做过

`ProfileViews.cs` 里三处带注释：R653（无已知表头）、R654（有被忽略的列）、R661（解析失败）。
**条件都是从镜像推的，写得有理有据。** 所以「这一簇完全没查过」是错的 —— 查过，而且查得对。

### 二、然后看到两个新东西

| | 原版有 | 复刻件 |
|---|---|---|
| `ProfileCsv.Status.Imported` = `Merged {0} rows from {1}` | **有**（目录里） | **从不产生** —— 只在字典字面量里出现一次 |
| `"{0} profile(s) parsed."` | **目录里没有这条键** | **自己造的**，`Preview()` 的兜底 |

**复刻件显示了一句原版没有的话，同时不显示原版有的一句。**

**而且这两处都没有任何测试钉着** —— 那句自造文案从来没被测过，**所以没有任何东西会抓到它**。

### 三、我差点改错，查了上下文才发现

第一反应：把 `"{0} profile(s) parsed."` 换成 `Imported`。

**差一步就错了。** 去看那个方法，它是：

```csharp
private void Preview()          // 没有源参数
{
    ...
    _status.Text = !HeaderHasKnownColumn() ? Text("StatusNoHeader")
                 : unknown.Count > 0 ? format(StatusIgnoredColumns, joined)
                 : $"{rows.Count} profile(s) parsed.";
}
```

**`Preview()` 是预览步骤，而 `Imported`（`Merged {0} rows from {1}`）属于真正的导入动作 —— 两个不同上下文。**
`Imported` 需要两个参数（行数、来源），而 `Preview()` 连源参数都没有。

**所以它们不是替换关系。改了就是把一条错文案换成另一条错文案。**

### 四、于是记成两个缺口，不改

| 缺口 | 缺什么 |
|---|---|
| 复刻件从不产生 `Status.Imported` | 需要一个**真正的导入动作**去产生它；`Preview()` 不是那个位置 |
| `Preview()` 的兜底是自造文案 | **原版在「一切正常」时显示什么 —— Unknown**，未读到对应函数 |

**第二个缺口的诚实说法**：`"{0} profile(s) parsed."` 在原版目录里**没有对应键**，
所以它要么该换成某条我还没找到的文案，**要么原版在这种情况下根本不显示状态**。
**两种可能都指向"未知"，而不是"换成 Imported"。**

### 五、这件事本身值得记

这已经是**第五次**「动手前读一眼上下文，避免了错改」：

| 轮 | 差点做错 | 读上下文后发现 |
|---|---|---|
| R468–R499 | 七次改成绑定属性漏步骤 | （已写进 AGENTS.md §3 清单） |
| **R744** | 把 Preview 的兜底换成 Imported | **两个不同上下文，参数都不够** |

**所以"读一眼上下文"不是谨慎，是必要步骤。** 记在这里，因为它每次都能省下一个错改。

### 六、验证

```
本轮未改产品代码
完整套件   1705 通过 / 0 失败（与 R743 相同）
已审候选   25 / 129（不变 —— 这一簇已在 R743 记过）
```

### 七、仍然 Unknown

- **原版 `Preview()` 那种情况（表头正常、无未知列）显示什么**：**Unknown**，未读到对应函数。
- 原版在哪个上下文产生 `Imported`：**Unknown**（只知道它有这条键）。
- `ProfileCsv.Clipboard` = `clipboard` 是否是 `Imported` 的 `{1}` 取值之一：**Inference（中）**，未证实。
"""

VERDICT = """

---

## 第 744 轮：两个真缺口，和一次没做出去的错改

### 以前的轮次查过

R653 / R654 / R661 已经把这个区域的条件从镜像推出来了，注释写得有理有据。**说"这簇没查过"是错的。**

### 但看到两个新东西

| | 原版有 | 复刻件 |
|---|---|---|
| `ProfileCsv.Status.Imported` = `Merged {0} rows from {1}` | **有** | **从不产生**（只在字典里） |
| `"{0} profile(s) parsed."` | **目录里没有** | **自己造的** |

**而且两处都没有测试钉着。**

### 我差点改错

第一反应是把自造兜底换 `Imported`。**去看那个方法，它是 `Preview()` —— 预览步骤，没有源参数。**

而 `Imported` 属于**真正的导入动作**，要两个参数。**两个不同上下文。**

> **改了就是把一条错文案换成另一条错文案。**

### 于是记成两个缺口，不改

- 复刻件从不产生 `Imported` —— 需要一个**真正的导入动作**，`Preview()` 不是那个位置
- `Preview()` 的兜底是自造的 —— **原版在"一切正常"时显示什么，Unknown**

**第二种可能：原版在这种情况下根本不显示状态。** 两种可能都指向"未知"，**不是"换成 Imported"**。

### 第五次「读一眼上下文避免了错改」

**所以这不是谨慎，是必要步骤。**

### 一句话

> 这一轮唯一产出是**没有把一条错文案换成另一条错文案**。
> 在一个已经通过 1705 条测试的项目里，**能挡住一次这样的改动，比再写 6 条探针值。**

### 验证

```
产品代码未改
完整套件   1705 通过 / 0 失败
已审候选   25 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R744", BLOCKER), (P3, "R744", BLOCKER), (P2, "第 744 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R744: two CSV gaps recorded, and one wrong fix avoided by reading the enclosing method\n\n"
         "R653, R654 and R661 already derived this area's conditions from the image, so the cluster was not\n"
         "unexamined. Two new gaps though: the replica never produces ProfileCsv.Status.Imported even though\n"
         "the catalogue has it, and Preview() falls back to '{0} profile(s) parsed.', a string with no\n"
         "catalogue key at all. Neither is pinned by any test, which is why neither has been caught.\n\n"
         "I nearly fixed the second by swapping in Status.Imported. Reading the enclosing method stopped it:\n"
         "that method is Preview(), a preview step with no source parameter, while 'Merged {0} rows from {1}'\n"
         "belongs to the import action and needs both a count and a source. Different contexts -- the swap\n"
         "would have replaced one wrong string with another.\n\n"
         "So both are recorded as gaps instead. For the fallback, the honest statement is that what the\n"
         "original shows when the header is fine and nothing is unknown is Unknown; it may show no status at\n"
         "all. Either reading points at 'not yet known', not at 'use Imported'.\n\n"
         "Fifth time reading the surrounding context has prevented a wrong edit. That is a required step,\n"
         "not caution.\n\n"
         "No product code changed; suite 1705 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
