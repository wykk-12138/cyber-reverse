"""Record R740: the pin toggle, and one behaviour the replica cannot express."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 169. Pin/Unpin 开关，以及一条**复刻件表达不出来**的原版行为

> R740。新增 `replica/src/Cybersole.Core/Reporting/TaskGroupPinLabel.cs`、对应 6 条探针。

### 一、反编译

`sub_1405C52E0`（44 行）：

```c
v13 = read_property(0)
if (v13 && *(void**)v13 == &unk_144DB79D0 && *(BYTE*)(v13 + 8))
    v14 = &off_146EB9D88;                  // "Unpin {0}"
else
    v14 = &off_146EB9C98;                  // "Pin {0}"
return format(localise(v14), read_property(1));   // 第二个属性是组名
```

**判据是三段合取**：读成功 **且** 类型标签等于 `&unk_144DB79D0` **且** 那个字节非零。

### 二、那条**复刻件表达不出来**的行为

**类型标签不对时，走 else，即当作「未钉」。**

C# 里那个标志只有一种类型，**所以"类型不对"这个分支在复刻件里根本不存在**。
原版在这种情况下降级为「未钉」，复刻件没有对应物。

**这是两个程序之间一个真实的结构差异，而且没有任何探针能表达它** ——
探针只能对"输入"断言，而这里缺的是一个**类型错误的输入**。

**写进源码注释与本节，不写成"已对齐"。**

### 三、Inference 与备择解释

**Observation**：三段条件、两个槽、第二个属性被代入。

**Inference（高）**：非零 = **已经钉住**，所以显示的是**相反动作**（"Unpin"）。
依据：右键菜单项命名的是**点它会做什么**。

**备择解释（未排除）**：那个标志的含义是"未钉"，于是非零对应 "Pin"。
**两种读法都与代码相容**，我按语境选了前者。**要排除它需要一个已知状态的样本**，没有。

### 四、验证

```
TaskGroupPinLabelTests   6 / 6 通过
完整套件                 1703 通过 / 0 失败（1697 + 6）
四项度量                 4 / 0 / 17 / 78 / 0（未变）
已审候选                 16 / 129（11 实现 + 3 不可探 + 2 合并/待读）
```

### 五、仍然 Unknown

- 那个字节到底是"已钉"还是"未钉"：**Inference（高）**，备择解释未排除。
- 类型标签不对时原版的完整行为（不只是"当作未钉"）：**Observation 到此为止**，
  后面还有没有别的降级没读。
- `read_property(1)` 是组名：**Inference（高）**，依据文案里的 `{0}` 与上下文菜单。
"""

VERDICT = """

---

## 第 740 轮：Pin/Unpin 开关，和一条表达不出来的行为

### 反编译

```c
if (read_ok && type_tag == &unk_144DB79D0 && *(BYTE*)(v13 + 8))
    → "Unpin {0}"
else
    → "Pin {0}"
return format(..., name)
```

**三段合取。**

### 复刻件表达不出来的那条

**类型标签不对 → 走 else → 当作「未钉」。**

C# 里那个标志只有一种类型，**所以这个分支在复刻件里不存在**。
**这是两个程序之间一个真实的结构差异，而且没有任何探针能表达它** ——
探针能对输入断言，而这里缺的输入是**一个类型错误的值**。

**写进源码注释，不写成「已对齐」。**

### Inference 与备择

**高置信**：非零 = 已钉 → 显示相反动作（菜单项命名的是点它会做什么）。
**未排除**：标志含义是"未钉"，非零对应 "Pin"。**两种都与代码相容，要排除需要一个已知状态的样本，没有。**

### 一句话

> 这一轮最该记的不是"又实现一个"，是**我遇到了一个"复刻不了"的点，而且它不是缺证据，是类型系统不同。**

> **这类差异用探针抓不到，只能写在源码里。**

### 验证

```
TaskGroupPinLabelTests   6 / 6
完整套件                 1703 通过 / 0 失败
四项度量                 4 / 0 / 17 / 78 / 0（未变）
已审候选                 16 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R740", BLOCKER), (P3, "R740", BLOCKER), (P2, "第 740 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    anchor = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if anchor in body:
        add = ("| `0x1405c52e0` | `TaskGroups.Context.Pin/UnpinFormat` | **已实现**（R740，6 条探针） | "
               "三段合取条件；非零 = 已钉 → 显示相反动作（**Inference 高，备择未排除**）；"
               "**类型标签不对时降级为「未钉」—— 复刻件表达不出来** |\n")
        body = body.replace(anchor, add + anchor, 1)
        body = body.replace("## 已审：9 个实现 + 3 个不可探 + 2 个合并/待读，共 14 个\n\n剩下的 **115 个待审**。",
                            "## 已审：10 个实现 + 3 个不可探 + 2 个合并/待读，共 15 个\n\n剩下的 **114 个待审**。"
                            "\n\n**store-groups（R732）是 2 条文案（title + message），没有 ActionFormat** —— "
                            "所以它不是三槽位形态，R732 的实现已经完整。")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R740: the pin toggle, and one original behaviour the replica cannot express\n\n"
         "sub_1405C52E0 chooses between 'Pin {0}' and 'Unpin {0}' on a three-part condition: the read\n"
         "succeeded, the value's type tag matches, and its byte is non-zero. Implemented as a bool toggle.\n\n"
         "The part worth recording is the type-tag check. When the tag does not match, the original takes the\n"
         "else branch and behaves as 'not pinned'. In C# the flag has one type, so that branch cannot occur in\n"
         "the replica -- a real structural difference between the two programs that no probe can express,\n"
         "because a probe asserts over inputs and the missing input here is a value of the wrong type. Noted in\n"
         "the source and in BLOCKERS rather than reported as aligned.\n\n"
         "Also labelled: that non-zero means 'already pinned' (so the label offers the opposite action) is an\n"
         "inference from menu-item convention, and the reading where the flag means 'not pinned' is equally\n"
         "consistent with the code. Settling it needs a sample whose state is known.\n\n"
         "6 probes, suite 1703 pass / 0 fail, four metrics unchanged, 15 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
