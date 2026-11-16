"""Record R731: TaskButtonLabel, and the asymmetry that a tidier implementation would lose."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 160. 第二个见证实现：任务按钮文案 —— 一个**不对称比较**，和一次没解出来的槽位

> R731。新增 `replica/src/Cybersole.Core/Reporting/TaskButtonLabel.cs`、
> `replica/tests/Cybersole.Tests/TaskButtonLabelTests.cs`（12 条）、
> `analysis/resolve_button_slots.py`（保留，作为槽位解析失败的记录）。

### 一、候选与反编译

`0x140594500`，引用 `TaskCreator.Button.CreateTask` / `CreateTasksFormat` / `SaveTask` / `SaveTasksFormat`。
86 行伪代码，读出两个属性（一个 byte 标志、一个计数）和四个分支：

```c
if (flag) {                       // save
    if (count == 1) return &off_146EB85E8;       // 单数
    // 否则落到共享的复数路径
}
else if (count >= 2) {            // create
    goto plural;
}
return &off_146EB8538;            // create 的剩余情形

plural:
    slot = flag ? &off_146EB8638 : &off_146EB8588;
    return format(localise(slot), count);
```

### 二、**两个比较不一样**，这是这一轮的全部价值

- save 走 `count == 1` → **0 落到复数**
- create 走 `count >= 2` → **0 落到单数**

所以：

```
save,   count=0  →  "Save 0 Tasks"
create, count=0  →  "Create Task"
```

**一个"整理"成 `count > 1` 两处一致的实现，会在所有正常输入上给出正确答案，只在这里错。**
这正是行为探针该抓的东西，也正好被 `AZeroCountTakesDifferentArmsInEachMode` 钉住。

### 三、槽位没解出来 —— 记下来而不是绕过

四个 `off_` 槽位指向什么，我想从镜像里读出来，把「槽位→键」从 Inference 变成 Observation。
**失败**：四个槽位读回同一个不合理的长度值（1155229432），说明它们**不是字符串指针**，
而是某种描述符结构，布局我没掌握。

**没有硬凑。** 结论分层写清：

- **Observation**：分支顺序、两个比较、四个不同槽位、目录里恰好四条语义吻合的键
- **Inference（高置信）**：哪个槽位是哪条键 —— 依据是分支形状钉死了单/复数与存/建，且没有别的自洽赋值
- **未建立**：两个属性各自的身份；标志读作"保存"是因为只有在那个读法下四条文案才成对

**关键一点**：**行为由分支结构决定，不由槽位身份决定。** 所以槽位没解出来**不阻碍**忠实实现，
只让"哪条文案"这一层多了一个推断 —— 而这一层即使错了，错的是文案而非分支逻辑。

### 四、实现与探针

`TaskButtonLabel.Describe(bool saving, int count, Func<string,string> copy)`，分支照抄；
12 条探针覆盖四象限、零值不对称、无占位符的文案不走 `string.Format`、以及负数按同样比较走
（**记下来是因为代码就是这么做的，不是因为有意义**）。

### 五、验证

```
TaskButtonLabelTests   12 / 12 通过
完整套件               1671 通过 / 0 失败（1659 + 12）
四项度量               4 / 0 / 17 / 78 / 0（未变 —— 又一处"文案在、行为不在"）
```

### 六、仍然 Unknown

- 四个槽位指向的对象是什么：**Unknown**（读回值不合理，未深究）。
- 标志与计数在原版里对应哪两个属性：**Unknown**。
- `save + 负数` 的真实行为：**Inference**，按 `== 1` 推的，未实测。
"""

VERDICT = """

---

## 第 731 轮：任务按钮文案 —— 一个不对称比较

### 反编译

`0x140594500`，两个属性 + 四个分支：

```c
if (flag) { if (count == 1) → 单数; 否则 → 复数 }
else if (count >= 2) → 复数
return 单数
```

### 两个比较不一样，这是全部价值

```
save,   count=0  →  "Save 0 Tasks"     （走 == 1，所以 0 落复数）
create, count=0  →  "Create Task"      （走 >= 2，所以 0 落单数）
```

**一个"整理"成 `count > 1` 两处一致的实现，会在所有正常输入上正确，只在这里错。**

### 槽位没解出来，记下来而不是绕过

四个 `off_` 槽位读回同一个不合理长度（1155229432）—— **不是字符串指针，是某种描述符**。**没有硬凑。**

分层写清：**Observation**（分支、比较、四槽位、四键）／**Inference 高置信**（槽位↔键，依据分支形状唯一自洽）／
**未建立**（两个属性身份）。

> **关键：行为由分支结构决定，不由槽位身份决定。** 所以槽位没解出来不阻碍忠实实现。

### 验证

```
TaskButtonLabelTests   12 / 12
完整套件               1671 通过 / 0 失败
四项度量               4 / 0 / 17 / 78 / 0（未变 —— 又一处"文案在、行为不在"）
```

### 一句话

> 这一轮抓到的不是"少了个功能"，是**一个只在一个输入上错的比较**。
> **四度量不会告诉我它存在，人工读反编译才会。**

### 下一轮

继续读。下一个候选挑引用 `Utilities.StoreGroups.Delete.MessageFormat` 的那个（`0x140579e40`）——
**又一个带格式化参数的确认文案**，同一形状，预计还有不对称。
"""


def main():
    for p, marker, text in ((P1, "R731", BLOCKER), (P3, "R731", BLOCKER), (P2, "第 731 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R731: task button label -- an asymmetric comparison, and one slot resolution that failed\n\n"
         "sub_140594500 reads a byte flag and a count, then picks between four TaskCreator.Button.* texts. The\n"
         "two comparisons are not the same: save tests count == 1, so zero takes the plural, while create tests\n"
         "count >= 2, so zero takes the singular.\n\n"
         "   save,   0 -> 'Save 0 Tasks'\n"
         "   create, 0 -> 'Create Task'\n\n"
         "An implementation that tidies both branches into count > 1 is right on every realistic input and\n"
         "wrong here, which is exactly what a behaviour probe is for and what the four metrics cannot see.\n\n"
         "I tried to resolve the four off_ slots to string objects so the slot-to-key mapping would be an\n"
         "observation rather than an inference. All four read back the same implausible length (1155229432), so\n"
         "they are descriptors rather than string pointers. Not forced: the observation/inference split is\n"
         "recorded, and behaviour follows from the branch structure, not from slot identity -- so failing to\n"
         "resolve them does not block a faithful implementation, only leaves the text-to-slot layer inferred.\n\n"
         "12 probes, suite 1671 pass / 0 fail, four metrics unchanged because this is behaviour and not members."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
