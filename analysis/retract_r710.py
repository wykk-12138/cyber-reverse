"""Retract R709's "12 fake members" claim with the string-pool evidence that refutes it. (R710)

R709 said the 819 denominator was inflated by 12 because `EditValue`1` listed `HasMultiple` beside
`HasMultiple_87 .. _101`. The reasoning was that a bare name beside numbered variants means the extractor appended a
disambiguator.

It did not. The original's own compiled-XAML descriptors read:

    Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Getter
    Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Setter
    Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_88!Getter

so those suffixed names are the real property names, and the extractor (`analysis/_xaml_bindings.py`) only ever takes
`member.split('.')[-1]` -- it has no mechanism to append anything. The 12 are genuine gaps, the denominator was always
right, and the claim has to be withdrawn rather than quietly softened.

Why it went wrong: I judged the names implausible and stopped there. `plausibility is not evidence` -- the string pool
was one command away and I did not run it.
"""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

RETRACT = """

---

## 139. **撤回 §138 的一条**：那 12 个带后缀的成员是**真的**，我判"假成员"判错了

> R710。证据：`analysis/pe_strings.txt` 原文。

### 一、原文是这么写的

```
0x0321ffbd  Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Getter
0x0321ffff  Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Setterz...
0x03220297  Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_88!Getter
0x032202d9  Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_88!Setter
```

**`_87` 是原版真实的属性名。** 提取器 `analysis/_xaml_bindings.py` 只做 `member.split('.')[-1]`，
**它没有任何追加后缀的机制** —— 我 §138 说"提取器加的"是凭空推断。

### 二、连带更正

| §138 的说法 | 现在 |
|---|---|
| 「12 条是绑定表自己造的假成员」 | **错** —— 12 条是真缺口 |
| 「819 虚高 12，真实 807」 | **错** —— 819 一直是准的 |
| 「C10 = 12/807 = 1.487%」 | **撤回** —— 仍是 **12/819 = 1.465%** |

### 三、46 条的真实构成（全部是真缺口候选）

```
46 = 12  EditValue`1 的 _87/_88/_91/_93.._101/_92/_100（名字古怪但真实）
   +  2  Notification.Message / .Type（源码叫 Body / Kind）
   + 32  命令做成了 lambda（CheckoutView.Close 等）
```

### 四、为什么错

**我判断"这不像真成员"，然后就停在那儿了。** 字符串池离我一条命令的距离，我没跑。

> **plausibility 不是 evidence。名字古怪只说明它古怪，不说明它不存在。**

这与本轮早先那四次「旧工具对、我错」是同一个毛病的不同面向：
**那四次是我把规则简化错了，这一次是我把"看起来不合理"当成了"不存在"。**

### 五、仍然 Unknown

- 那 12 个名字（`HasMultiple_87` 等）在原版里承担什么语义：**Unknown** —— 只知道它们是真实绑定属性。
- 为什么原版会有一族带数字后缀的属性：**Unknown**（可能是混淆、可能是代码生成、可能是历史残留）。
"""

VERDICT = """

---

## 第 710 轮：撤回上一轮的一个判断

### 原文证据

```
Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Getter
Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Setter
```

**`_87` 是原版真实属性名。** 提取器只做 `split('.')[-1]`，没有任何追加机制。

### 连带更正

| R709 说 | 现在 |
|---|---|
| 12 条是假成员 | **真缺口** |
| 819 虚高，真实 807 | **819 准** |
| C10 1.487% | **12/819 = 1.465%** |

### 46 条的真实构成

```
12  EditValue`1 的 _87..（名字古怪但真实）
 2  Notification.Message / .Type
32  命令做成了 lambda
```

### 为什么错

**我判断「这不像真成员」，然后停在那儿了。** 字符串池离我一条命令，我没跑。

> **plausibility 不是 evidence。名字古怪只说明它古怪，不说明它不存在。**

本轮早先四次是我把规则简化错了；这一次是我把"看起来不合理"当成了"不存在"。

### 下一轮

按证据处理那 32 条 lambda 命令（描述符是真的，实现成 `ICommand` 属性有据）。
"""


def main():
    for p, marker, text in ((P1, "R710", RETRACT), (P3, "R710", RETRACT), (P2, "第 710 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R710: retract R709's fake-member claim -- the suffixed names are real\n\n"
         "pe_strings.txt contains, verbatim:\n"
         "  Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Getter\n"
         "  Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Setter\n"
         "so _87 is part of the property name, and _xaml_bindings.py only does member.split('.')[-1] --\n"
         "it has no mechanism to append a suffix. The 819 denominator was never inflated; the 12 are\n"
         "genuine gaps; C10 stays 12/819.\n\n"
         "The error was judging the names implausible and stopping there. The string pool was one\n"
         "command away. Plausibility is not evidence."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
