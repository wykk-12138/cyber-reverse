"""Record R751: the 0/1/n generalisation is refuted -- the discriminator is the argument's kind."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 180. 「整簇都是 0/1/n」——**被证伪**。判别式是**参数的种类**，不是屏幕

> R751。新增 `SmartActionTriggerLabel.cs`、对应 5 条探针；`0x1405ffd50` 记为待解。

### 一、上一轮我差一步就写下"整簇通例"

R750 在 filters / actions 两个统计上确认了 **0 / 1 / n**，于是自然的下一步推论是
「整个 `SmartActionsCreator` 区域都是三段」。**这一轮读两个，不成立。**

### 二、两个都是两段，而且原因清楚

**`sub_1405FFFA0`（17 行，全读）：**

```c
if ( a2 )
{
    box = *(_QWORD *)(a2 + 24);            // ← 一个**名字**，不是计数
    return format(&off_146E912C8, box);     // "{0} Trigger"
}
else
    return localise(&off_146E910C8);        // "No Trigger"
```

**两段。没有"1 Trigger"这一档** —— 因为参数是名字，一个触发器不是特殊情况。

**`sub_1405FFD50`（54 行）：**

```c
if ( v8 != *(_QWORD *)(v3 + 16) )
{
    box = property(2);
    return format(&off_146E90B10, box);     // "{0} if"
}
return localise(&off_146E90C18);            // ← 另一条
```

**也是两段**，而它的分支条件是**一次比较**，不是计数。

### 三、于是判别式浮出来了

| 参数是什么 | 文案条数 | 例子 |
|---|---|---|
| **计数** | **三段（0/1/n）** | `No Filters` / `1 Filter Saved` / `{0} Filters Saved` |
| **名字** | 两段 | `No Trigger` / `{0} Trigger` |
| **一个被比较的值** | 两段 | `{0} if` / 另一条 |

**所以「整簇 0/1/n」是错的通例。** 而且这个判别式有**可解释的因果**：
**只有当参数是计数时，"1"才值得一条独立句子。**

### 四、这个区分对度量覆盖率有什么用

R750 说 ranking 的盲区是「只数带占位符的」。
**现在可以补一句更准的**：**只有计数型的标签才有那种"无占位符的兄弟"**，
所以 ranking 的盲区**恰好落在计数型的文案上** —— 而这类正好是 0/1/n 里被藏起来的两档。

**盲区不是均匀分布的。** 这决定了下一轮该往哪儿找漏掉的文案。

### 五、验证

```
SmartActionTriggerLabelTests   5 / 5 通过
完整套件                       1730 通过 / 0 失败（1725 + 5）
四项度量                       4 / 0 / 17 / 78 / 0（未变）
已审候选                       29 / 129
```

### 六、仍然 Unknown

- `off_146E90C18`（`{0} if` 的另一支）是什么文案：**Unknown** —— 槽位未解。
  `SmartActionsCreator.AlwaysRun` = "This smart action will always run when triggered"
  **读起来像对应物（条件式 vs 总是运行），但那是猜，不是映射。**
- `{0} if` 那个 `{0}` 填什么：**Unknown**（`property(2)`，类型未解）。
- `sub_1405FFD50` 里前三行的那几个 `<= 1` 守卫各自判什么：**Unknown**（未逐行解）。
"""

VERDICT = """

---

## 第 751 轮：「整簇 0/1/n」被证伪 —— 判别式是参数种类

### 差一步就写下错通例

R750 在 filters/actions 上确认了 0/1/n，**自然的下一步推论是「整个区域都三段」。这一轮读两个，不成立。**

### 两个都是两段

```c
// sub_1405FFFA0 —— 17 行
if (a2) { box = *(a2 + 24); return format("{0} Trigger", box); }   // 参数是**名字**
else      return localise("No Trigger");

// sub_1405FFD50 —— 54 行
if (v8 != *(v3 + 16)) { return format("{0} if", property(2)); }     // 条件是**一次比较**
else                    return localise(另一条);
```

**没有"1 Trigger"这一档** —— 因为参数是名字，一个触发器不是特殊情况。

### 判别式

| 参数 | 条数 | 例 |
|---|---|---|
| **计数** | **三段** | `No Filters` / `1 Filter Saved` / `{0} Filters Saved` |
| **名字** | 两段 | `No Trigger` / `{0} Trigger` |
| **被比较的值** | 两段 | `{0} if` / 另一条 |

**有可解释的因果：只有参数是计数时，「1」才值得一条独立句子。**

### 这对度量覆盖率的补充

R750 说 ranking 盲区是「只数带占位符的」。**现在更准了：只有计数型标签才有那种无占位符的兄弟。**

> **所以盲区不是均匀分布的 —— 它恰好落在计数型文案上，而这类正是 0/1/n 里被藏起来的两档。**
> **这决定了下一轮该往哪儿找漏掉的文案。**

### 验证

```
SmartActionTriggerLabelTests   5 / 5
完整套件                       1730 通过 / 0 失败
四项度量                       4 / 0 / 17 / 78 / 0（未变）
已审候选                       29 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R751", BLOCKER), (P3, "R751", BLOCKER), (P2, "第 751 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    anchor = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if anchor in body:
        add = ("| `0x1405fffa0` | `SmartActionsCreator.NoTrigger/TriggerFormat` | **已实现**（R751，5 条探针） | "
               "**两段**（名字型，无 1 档）；与 R750 的 0/1/n 相反 —— **判别式是参数种类** |\n"
               "| `0x1405ffd50` | `SmartActionsCreator.BehaviourFormat`（`{0} if`） | **待解** | "
               "两段，条件是一次**比较**；另一支的槽 `off_146E90C18` 未解，`{0}` 填什么 Unknown |\n")
        body = body.replace(anchor, add + anchor, 1)
        body = body.replace("## 已审：28 / 129", "## 已审：29 / 129")
        body = body.replace("**R750 发现 ranking 的第二种偏差**",
                            "**R751 补充**：ranking 的盲区**只落在计数型文案上**（只有它们才有无占位符的兄弟），"
                            "而 0/1/n 的三段里被藏起来的正是那两档。**盲区不是均匀分布的。**\n\n"
                            "**R750 发现 ranking 的第二种偏差**")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R751: the 0/1/n generalisation is refuted -- the discriminator is the argument's kind\n\n"
         "After confirming 0/1/n on two counters last round, the obvious next step was to call the whole\n"
         "SmartActionsCreator area three-sentence. Reading two more members refutes it, and the reason is\n"
         "instructive rather than incidental.\n\n"
         "sub_1405FFFA0 takes a NAME: 'No Trigger' or '{0} Trigger', with no single-trigger case, because one\n"
         "trigger is not a special quantity. sub_1405FFD50 branches on a comparison: '{0} if' in one arm and a\n"
         "second sentence in the other. So the split follows the argument -- a count gets 0/1/n, a name or a\n"
         "compared value gets two sentences -- and the causal reading is that only a count makes the digit 1\n"
         "worth its own sentence.\n\n"
         "That sharpens last round's measurement point. Only count-shaped labels have a placeholder-free\n"
         "sibling, so the ranking's blind spot is not spread evenly across the area: it falls exactly on the\n"
         "count-shaped texts, which are the ones whose zero and one cases the ranking hides. Where to look for\n"
         "the next omissions follows from that.\n\n"
         "Implemented the trigger label with five probes. Left {0} if unimplemented: its other arm's slot\n"
         "off_146E90C18 is unresolved, and 'This smart action will always run when triggered' reads like a\n"
         "plausible counterpart but a plausible reading is not a mapping.\n\n"
         "Suite 1730 pass / 0 fail; four metrics unchanged; 29 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
