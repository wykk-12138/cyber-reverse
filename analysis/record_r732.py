"""Record R732: StoreGroupDeletePrompt -- the same "text present, behaviour absent" gap a second time."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 161. 第三处「文案在、行为不在」：store-group 删除确认的**分支选择**缺失

> R732。新增 `replica/src/Cybersole.Core/Reporting/StoreGroupDeletePrompt.cs`、
> `replica/tests/Cybersole.Tests/StoreGroupDeletePromptTests.cs`（7 条）。

### 一、反编译

`sub_140579E40`（57 行）：读组名与一个使用计数，然后

```c
if (v6)                                   // 真值判断，不是 > 0
{
    args = { name, box(v6) };             // 两个占位符
    message = localise(&off_146F19900, args);
}
else
{
    args = { name };                      // 一个占位符
    message = localise(&off_146F19828, args);
}
title = localise(&off_146F19898, name);   // "Delete {0}?"
```

### 二、复刻件的现状：两条文案在字典里，**没有任何代码消费它们**

```
UtilitiesViews.cs:54   ["DeleteMessageFormat"] = ...
UtilitiesViews.cs:55   ["DeleteUsedMessageFormat"] = ...
代码里其它引用：0
```

**第三次遇到同一形状**（R729 相对时间、R731 任务按钮、本轮）：
**四度量数成员不数行为，所以「文案齐全但选择逻辑不存在」这类缺口它们结构上看不见。**

### 三、`if (v6)` 不是 `if (v6 > 0)`

反编译里是真值判断。**负数会走两参数分支**，而写 `> 0` 在所有正常输入上给出同样答案。
与 R731 那个 `== 1` / `>= 2` 是同一类：**自然的写法与二进制不一致，且只在边界上暴露。**

已写探针 `ANegativeCountStillTakesTheInUseText`。

### 四、实现范围与不做的部分（写清）

**做了**：title 与 message 的文本选择和参数绑定 —— 这是该函数可断言的全部输出。

**没做**：对话框本身。反编译尾部把确认模型装箱并调用 show 助手（带槽位号），
**复刻件的对话框管道按设计是它自己的**，而"弹出了一个对话框"是窗口级测试，不是行为探针。
**明确记在这里，不当成已完成。**

### 五、另一条探针值得单说

`TheGroupNameIsASubstitutionArgument`：组名含 `{0}` 时，它作为**参数**代入而不是被再次格式化。
反编译里名字是 `args[0]`，所以这是**结构决定的**，不是风格选择。

### 六、验证

```
StoreGroupDeletePromptTests   7 / 7 通过
完整套件                      1678 通过 / 0 失败（1671 + 7）
四项度量                      4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- `sub_142E74000(off_14491CFA0, v5)` 是不是"引用该组的 smart action 数"：**Inference（高）**，
  依据是文案里的 `{1} smart action filter(s)`；未反编译该函数确认。
- 四个槽位的实际内容：**Inference**（两个参数的必是带 `{1}` 的那条，只有一个候选符合）。
- 负使用计数在原版里的真实行为：**Inference**，按 `if (v6)` 推的。
"""

VERDICT = """

---

## 第 732 轮：第三处「文案在、行为不在」

### 反编译

`sub_140579E40`：

```c
if (v6)  → args{name, count} → UsedMessageFormat   （两个占位符）
else     → args{name}        → MessageFormat       （一个占位符）
title = TitleFormat(name)
```

### 复刻件的现状

`UtilitiesViews.cs:54-55` 两条文案都在，**代码里没有一处消费它们**。

**第三次遇到同一形状**（R729 相对时间、R731 任务按钮）。
**四度量数成员不数行为，所以这类缺口它们结构上看不见。**

### `if (v6)` 不是 `if (v6 > 0)`

真值判断。**负数走两参数分支**，而写 `> 0` 在所有正常输入上答案相同。
与 R731 的 `== 1` / `>= 2` 同类：**自然的写法与二进制不一致，只在边界暴露。**

### 范围写清

**做了**：title/message 的选择与参数绑定。
**没做**：对话框本身 —— 复刻件的对话框管道按设计是自己的，"弹了个框"是窗口级测试。
**明确记录，不当成已完成。**

### 一句话

> 三处缺口，同一个形状：**文案齐全，选择逻辑不存在。**
> **而三处的选择逻辑都藏着一个是非此即彼就会踩错的比较。**

### 验证

```
StoreGroupDeletePromptTests   7 / 7
完整套件                      1678 通过 / 0 失败
四项度量                      4 / 0 / 17 / 78 / 0（未变）
```

### 下一轮

继续读。下一个候选：`0x140601620`（`SmartActions.ChangeTrigger.Message/Title`）。
"""


def main():
    for p, marker, text in ((P1, "R732", BLOCKER), (P3, "R732", BLOCKER), (P2, "第 732 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R732: the store-group delete confirmation -- third 'text present, behaviour absent' gap\n\n"
         "sub_140579E40 picks between two catalogue messages on a usage count and substitutes either one or\n"
         "two arguments. The replica has both texts at UtilitiesViews.cs:54-55 and no code consuming them.\n\n"
         "That is the third occurrence of the same shape -- RelativeTime in R729, TaskButtonLabel in R731, this\n"
         "one now. The four metrics count members rather than behaviour, so none of the three was visible to\n"
         "them.\n\n"
         "The branch is `if (v6)` -- truthiness, not `> 0` -- so a negative count takes the two-argument text.\n"
         "Same class as R731's `== 1` against `>= 2`: the natural way to write it agrees on every realistic\n"
         "input and differs only at a boundary.\n\n"
         "Scope stated rather than implied: the title and message selection is implemented and probed; the\n"
         "dialog is not, because the replica's dialog plumbing is its own by design and 'a dialog appeared' is\n"
         "a window-level test rather than a behaviour probe.\n\n"
         "One probe worth naming: a group name containing {0} is substituted as an argument, not re-formatted,\n"
         "because the decompiled code passes it in args[0].\n\n"
         "7 probes, suite 1678 pass / 0 fail, four metrics unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
