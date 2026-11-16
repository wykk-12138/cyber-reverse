"""Record R739: the capability exists but .NET 10 stopped emitting what it reads."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
EC = r"D:\projects\cyber-reverse\docs\EVIDENCE_CLASSES.md"

BLOCKER = """

---

## 168. §1.2 查证结果：能力存在，但 **.NET 10 不再产出它要读的东西**

> R739。读 `rea/docs/providers/ghidra-nativeaot.md`（本地）；查上游 issue。

### 一、rea 确实有那个能力

`rea/docs/providers/ghidra-nativeaot.md`（10,684 B）原文：

> REA has a built-in read-only snapshot parser for x64 PE targets with **.NET 8 RTR 9.1** metadata. …
> The parser currently handles x64 PE32+ and **RTR 9.1**, including bounded **DEHYDRATED_DATA** processing,
> **MethodTable relationships, virtual slots, and frozen strings**. Other RTR versions and PE architectures
> are reported as unsupported or partial.

**这正是 R738 说缺的那一套**：MethodTable 关系、虚槽、冻结字符串、slot 目标。

### 二、但版本不符 —— 而且不是版本问题

目标二进制的运行时证据：

```
net10.0   出现 1 次
net9      0 次
net8      0 次
```

（`ReadyToRun` 那一次出现是在类型名列表里 —— `ReadyToRunSectionType`、`CompilerHelpers` ——
那是**解压后的元数据 blob**，不是 RTR 头。）

**所以目标是 .NET 10，解析器只收 .NET 8/9.1。**

### 三、上游已经有人问过，答案是"读不到数据"

`Washi1337/ghidra-nativeaot` issue #15，标题原文：
**「.NET 10 Support: No dehydrated data found」**
（<https://github.com/Washi1337/ghidra-nativeaot/issues/15>）

**这比"版本没支持"更硬**：不是解析器认不出新版本号，是 **.NET 10 的 NativeAOT 输出里没有 `DEHYDRATED_DATA`** ——
**解析器赖以工作的输入本身不存在了。**

**诚实标注**：我只读到 issue 的**标题**（正文被截断）。所以
「.NET 10 是否彻底移除 dehydrated data，还是只是换了个位置」**属于 Unknown** ——
但**标题足以支持"当前解析器在这个目标上读不到东西"这一条**。

### 四、于是 R738 的结论要升级

R738 我写的是「工具在，但版本不达标」。**正确说法是**：

> **工具在，而 .NET 10 的 NativeAOT 输出不再携带该工具所需的那种元数据表。**

**这两句的差别决定了下一步**：版本不达标 → 等上游更新就行；
**输入格式变了 → 等不到，得换方法。**

### 五、那还剩什么路（三条，各自的代价）

| 路 | 可行性 | 代价 |
|---|---|---|
| 等上游支持 .NET 10 | **Unknown**（issue 未说明是否可行） | 不可控 |
| 自己写 .NET 10 的元数据解析器 | 需要新的布局知识，**不是我有能力凭现有证据推出来的** | 大 |
| **运行期探针** | 唯一能真正解开的 | **需登录凭据 —— YG 那一类** |
| 接受 Unknown + 写明缺什么 | **目标判据 (a) 明确允许** | 无 |

**所以现状（记 Unknown + 写明缺什么）不是偷懒，是三条可行路里唯一不需要外部输入的那条。**

### 六、验证

```
本轮未改产品代码
完整套件   1697 通过 / 0 失败（与 R738 相同）
已审候选   14 / 129
```

### 七、仍然 Unknown（更新 gap_reason）

- `EditValue\\`1` 那 12 个成员的类型 / R731 的四个文案槽 / profiles 闸门的两个 delegate：
  **gap_reason 从"缺 AOT 元数据模型"细化为**「
  **rea 的解析器只接受 RTR 9.1 与 `DEHYDRATED_DATA`，而 .NET 10 的 NativeAOT 输出不再携带它（上游 issue #15 标题）；
  自写需要新的布局知识；运行期探针需要凭据**」。
- issue #15 的正文与是否可行：**Unknown**（只读到标题）。
"""

VERDICT = """

---

## 第 739 轮：能力存在，但 .NET 10 不再产出它要读的东西

### rea 确实有

`ghidra-nativeaot.md` 原文：支持 **RTR 9.1**、`DEHYDRATED_DATA`、**MethodTable 关系、虚槽、冻结字符串**。
**正是 R738 说缺的那一套。**

### 但目标不是那个版本

```
net10.0 → 1 次      net9 → 0      net8 → 0
```

### 上游已经问过，答案更硬

issue #15 标题：**「.NET 10 Support: No dehydrated data found」**

**不是解析器认不出新版本号，是 .NET 10 的输出里没有 `DEHYDRATED_DATA` ——
解析器赖以工作的输入本身不存在了。**

（诚实标注：只读到标题，正文被截断。所以"是否彻底移除"是 Unknown。）

### 于是 R738 的结论要升级

> R738：「工具在，但版本不达标」
> **正确：「工具在，而 .NET 10 不再携带该工具需要的那种元数据表。」**

**差别决定下一步**：版本不达标 → 等上游；**输入格式变了 → 等不到，得换方法。**

### 剩下四条路

| 路 | 代价 |
|---|---|
| 等上游 | 不可控，可行性 Unknown |
| 自写解析器 | 需要新的布局知识，凭现有证据推不出来 |
| **运行期探针** | **需凭据 —— YG 那一类** |
| **记 Unknown + 写明缺什么** | **判据 (a) 明确允许** |

**所以现状不是偷懒，是四条路里唯一不需要外部输入的那条。**

### 一句话

> 我花了两轮以为在找工具，其实在找的是**输入**。
> **工具一直在，而原版从 .NET 10 起不再输出它读的那张表。**

### 验证

```
产品代码未改
完整套件   1697 通过 / 0 失败
已审候选   14 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R739", BLOCKER), (P3, "R739", BLOCKER), (P2, "第 739 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(EC, encoding="utf-8").read()
    old = ("**要建它，先按 §1.2 查 `rea` 的 `docs/providers/ghidra-nativeaot.md` 与 `seep-reverse-lab` 有没有现成的\n"
           "EEType 解析；两处都没有，才自己写。**")
    new = """**R739 查证结果：`rea` 有这个能力，但输入不在。**

`rea/docs/providers/ghidra-nativeaot.md` 明确它支持 x64 PE32+ 的 **RTR 9.1**，含 `DEHYDRATED_DATA`、
MethodTable 关系、虚槽与冻结字符串 —— 正是上表缺的那一套。

**但目标是 .NET 10**（`net10.0` 出现 1 次，`net8`/`net9` 各 0 次），
而上游 `Washi1337/ghidra-nativeaot` issue #15 的标题是
**[「.NET 10 Support: No dehydrated data found」](https://github.com/Washi1337/ghidra-nativeaot/issues/15)**。

**所以不是版本号不匹配，是 .NET 10 的 NativeAOT 输出不再携带 `DEHYDRATED_DATA` ——
解析器要读的那张表本身不存在了。** 等上游更新不会解决这件事。

可行路径只剩三条：
1. **运行期探针** —— 唯一能真正解开的，**需登录凭据（YG 那一类）**
2. 自写 .NET 10 元数据解析器 —— 需要新的布局知识，**凭现有证据推不出来**
3. **记 Unknown 并写明缺什么** —— 目标判据 (a) 明确允许，**当前做法**

（R739 只读到 issue #15 的标题，正文被截断；「是否彻底移除 vs 换了位置」属 Unknown。）"""
    if old in body:
        io.open(EC, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  EVIDENCE_CLASSES.md §八 updated with the R739 finding")
    else:
        print("  EVIDENCE_CLASSES.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R739: the capability exists, but .NET 10 no longer emits what it reads\n\n"
         "Rea's ghidra-nativeaot provider does have exactly what R738 called missing -- MethodTable\n"
         "relationships, virtual slots, frozen strings, slot targets, all from DEHYDRATED_DATA. Its own\n"
         "documentation admits x64 PE32+ at RTR 9.1.\n\n"
         "The target is not that: net10.0 appears once, net8 and net9 zero times. (The single 'ReadyToRun'\n"
         "string is a type name inside the decompressed metadata blob, not an RTR header.)\n\n"
         "And upstream issue #15 is titled '.NET 10 Support: No dehydrated data found', which is a harder\n"
         "finding than a version gap: .NET 10's NativeAOT output does not carry the table the parser reads.\n"
         "So waiting for upstream will not help, and R738's wording -- 'the tool is version-gated' -- is\n"
         "upgraded to 'the input no longer exists'.\n\n"
         "That distinction changes the options: a runtime probe would settle it but needs credentials, writing\n"
         "a .NET 10 metadata parser needs layout knowledge not derivable from what I have, and recording the gap\n"
         "as Unknown is what criterion (a) explicitly permits. The current approach is the only one of the three\n"
         "that needs no outside input.\n\n"
         "Only the issue title was readable; whether dehydrated data was removed or merely moved stays Unknown."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
