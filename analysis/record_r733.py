"""Record R733: two more candidates adjudicated, and the ledger that stops the next 123 being re-read."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
HB = r"D:\projects\cyber-reverse\docs\HANDOFF_BLOCKERS.md"

BLOCKER = """

---

## 162. 又两个候选不可探，以及建起的**候选台账**

> R733。新增 `docs/WITNESS_LEDGER.md`。

### 一、`0x140601620`（`SmartActions.ChangeTrigger.*`）：闸门是三个不透明谓词

```c
if ( !*(BYTE*)(a1+1268)                                  // 一个"已确认过"标志
  && (unsigned int)off_147328250(*(_QWORD*)(a3+40))      // 谓词 P（不透明）
  )
{
  item = element0(collection);
  if ( item && ( A(...) || B(...) ) )                    // 又是两个不透明谓词
  {
     *(BYTE*)(v5+24) = 1;                                // 先把"已确认"置上
     // 固定标题 + 固定消息 + 两个按钮
     show(...)
  }
}
```

**可断言的只有「弹出时标题与消息是这两条常量」** —— 而且这还要先知道框会不会弹。
`off_147328250` / `off_14734BF30` / `off_14734BAE0` 三个委托作用在未知对象上，
**从这个函数里读不出语义**。**不合格。**

顺带记一个真实行为：`*(BYTE*)(v5+24) = 1` 在 `show` **之前**执行 ——
**即使用户取消，那个"不再问"的标志也已经置上了。** 这个行为有意思，但**没有谓词语义就断言不了**。

### 二、`0x140654480`（`Common.Hour12/Hour24/Disabled` 等）：label 在解不出的槽位里

构造了两个选项列表：

```
三项：{label=&off_146B99670, value=0}, {&off_146B99710, 1}, {&off_146B99740, 2}
两项：{label=…, value=0}, {label=…, value=1}
```

**结构能读出来（3 项 / 2 项、值域 0..2 / 0..1），但 `label↔value` 的对应在槽位里** ——
与 R731 同一个问题，四个槽位读回来是不合理的长度值。

**只靠"有 3 项"断言不了任何行为。不合格。**

### 三、于是建了台账

`docs/WITNESS_LEDGER.md`：已审 6 个（4 实现 + 2 不可探），剩 123。

**为什么必须有**：R730 裁定"读伪代码，人工判断"，代价是每个候选一轮。
129 个候选 = 129 轮 —— **每个读过的都必须留结论，否则会被重读。**

### 四、台账里写下的一条经验（不是判据）

6 个样本里：

- **已实现的 3 个**，形状一样：读属性 → 一串比较 → 选 locale 文案 → 代入参数
- **不可探的 3 个**，形状也一样：输出不是文案选择，而是控件属性赋值 / 不透明谓词后的弹框 / 槽位里的 label

**所以：候选引用的文案里带 `{0}`/`{1}` 时大概率可探；引用短标签（`Disabled`、`Beta`、`Create`）时大概率是接线。**

**明确标注：这是经验，不是判据。** 判据仍然是读伪代码（R730）。但它能决定先读哪个，
`analysis/witness_candidate_keys.txt` 里有每个候选的键名，可以据此排序。

### 五、验证

```
本轮未改产品代码
完整套件        1678 通过 / 0 失败（与 R732 相同）
已审候选        6 / 129
```

### 六、仍然 Unknown

- 那三个委托（`off_147328250` 等）的语义：**Unknown**（未反编译）。
- 六个选项槽位的 label：**Unknown**（读回值不合理）。
- 剩下 123 个候选的形状分布：**Unknown** —— 台账会一个轮次一个轮次填。
"""

VERDICT = """

---

## 第 733 轮：又两个不可探，建起台账

### `0x140601620`：闸门是三个不透明谓词

```c
if (!flag && P(a3[40])) { if (item && (A(...) || B(...))) { set flag; show(fixed title, fixed message) } }
```

**能断言的只有"框里的两条文案"**，而框弹不弹取决于三个我读不出语义的委托。**不合格。**

顺带记一个真实行为：`set flag` 在 `show` **之前**——**用户取消也一样置上了**。有意思，但断言不了。

### `0x140654480`：label 在解不出的槽位里

读出 3 项（值 0/1/2）与 2 项（值 0/1）两个选项列表，**但 label↔value 在槽位里**（同 R731）。**不合格。**

### 于是建了台账

`docs/WITNESS_LEDGER.md`：**已审 6 / 129**（4 实现 + 2 不可探），剩 123。

> R730 裁定"读伪代码"，代价是每个候选一轮。**每个读过的都必须留结论，否则会被重读。**

### 一条经验（明确不是判据）

| 已实现（3 个） | 不可探（3 个） |
|---|---|
| 读属性 → 比较 → 选文案 → 代入参数 | 控件属性赋值 / 不透明谓词后弹框 / 槽位里的 label |

**引用的文案带 `{0}`/`{1}` → 大概率可探；引用短标签 → 大概率接线。**
**这是排序用的经验，判据仍是读代码。**

### 一句话

> 三个能做的形状一模一样，三个不能做的也一模一样。
> **差别不在函数大小，在它的输出是不是"一条带参数的文案"。**

### 验证

```
产品代码未改
完整套件   1678 通过 / 0 失败
已审       6 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R733", BLOCKER), (P3, "R733", BLOCKER), (P2, "第 733 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(HB, encoding="utf-8").read()
    if "WITNESS_LEDGER" not in body:
        io.open(HB, "a", encoding="utf-8").write(
            "\n\n## 见证候选台账\n\n`docs/WITNESS_LEDGER.md` —— **读任何候选之前先查这张表**："
            "已审 6 / 129，每个读过、判过的都留了结论与依据，避免重读。\n")
        print("  HANDOFF_BLOCKERS.md += WITNESS_LEDGER pointer")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R733: two more candidates unprobeable, and a ledger so the other 123 are not re-read\n\n"
         "sub_140601620 gates a fixed-text dialog behind three opaque predicates (off_147328250,\n"
         "off_14734BF30, off_14734BAE0) applied to unknown objects; the only assertable fact is the text, and\n"
         "even that depends on whether the dialog opens. Worth recording separately: it sets its 'already\n"
         "confirmed' flag before calling show, so a cancel still sets it.\n\n"
         "sub_140654480 builds option lists -- three items with values 0/1/2 and two with 0/1 -- but the\n"
         "label-to-value mapping lives in slots that read back implausible lengths (the R731 problem). 'There\n"
         "are three items' asserts no behaviour.\n\n"
         "docs/WITNESS_LEDGER.md now records all six adjudicated candidates with conclusion and basis: four\n"
         "implemented, two unprobeable, 123 to go. R730 ruled that telling wiring from logic means reading the\n"
         "pseudocode, which costs a round per candidate, so every candidate read must leave its conclusion\n"
         "behind or it gets read again.\n\n"
         "One observation, explicitly labelled experience and not a criterion: the three implemented\n"
         "candidates all pick between locale texts that carry {0}/{1}, while the three rejected ones produce\n"
         "property assignments, a dialog behind opaque predicates, or a slot-held label. That orders the\n"
         "reading; it does not replace it."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
