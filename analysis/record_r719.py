"""Record R719: caller-count ranking selects glue; the criterion is rejected with decompiled evidence."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 148. 「按调用者数选探针目标」**证否**：top 15 全是胶水，反编译三个坐实

> R719。新增 `analysis/rank_callers.py`（保留，作为判据错误的记录）。

### 一、判据（先定）

R718 留的问题：187,000 个函数，探针先做哪个？候选判据「被调用越多越是好证人」。
测法：数 `idautils.XrefsTo(ea, 0)`，按调用者数排序。

### 二、结果：top 15 全是无名小数

样本 **6,000 / 321,244**（低地址端，`page=1000`、6 页）：

```
0x1400fe270  callers=4046  size=97     0x1400f7f40  callers=865  size=4
0x1400f70f0  callers=3980  size=288    0x140110140  callers=818  size=182
0x1400f74e0  callers=3494  size=109    0x140111120  callers=767  size=102
0x140110430  callers=2916  size=68
```

**口径必须说清**：这是**样本内**的 top，不是全局 top（只跑了 6000 个）。

### 三、反编译三个，坐实是胶水

```c
sub_1400F7F40 (865 callers, 4 B)   return *(unsigned int *)(a1 + 80);      // 纯字段读取
sub_1400FDEB0 (868 callers, 66 B)  if (*(_BYTE *)(a1 + 74)) { ... }        // 标志位 + 转发
sub_140110430 (2916 callers, 68 B) sub_141DC3360(&unk_144B55D18, a2)       // 全局表查找
```

**4 字节、被调 865 次** —— 那不是"行为"，是每个代码路径都碰的东西。

### 四、为什么这个判据必然错（不是样本太小）

**入度高的函数是"所有代码都碰的东西"**，而"所有代码都碰的东西"恰恰是**运行期与编译器胶水**。
它对「应用是否被复刻」**没有证人力** —— 胶水对等不说明任何业务行为对等。

**这是判据结构上的错，不是取样量的问题。** 跑满 321,244 个，top 只会更胶水。

### 五、换成什么判据：**按"属于应用"选，不按入度选**

候选：**引用了应用特有字符串的函数**。理由：

- locale 键（`ProfileCsv.Error.UnknownCountry` 等）与绑定描述符是**只有这个应用才有的**字符串
- R703 已证明这类引用可以定位：`lea reg, [rip+disp32]`，disp32 是代码里的裸字节
- 于是"引用应用字符串的函数"是**可证的应用程序**，而不是靠名字或入度猜

**这是下一轮的方案，本轮未实施。**

### 六、仍然 Unknown

- 全局（321,244）的入度分布：**Unknown**（只跑了 6,000 样本）。
- 「引用应用字符串」能覆盖多少比例的应用程序：**Unknown**（未实施）。
- 反编译里 `sub_141DC3360(&unk_144B55D18, …)` 这类全局表查找属于什么语义：**Unknown**。

### 七、这一轮的判断

> 我把"被引用得多"当成了"重要"。**在一个 321k 函数的二进制里，被引用得最多的是没人会去写的那种代码。**

**判据错了就换判据，但要把"为什么错"写下来** —— 否则下一轮会有人再想一遍"按调用次数排序不是挺合理吗"。
"""

VERDICT = """

---

## 第 719 轮：按调用者数选探针目标 —— 证否

### 判据

187,000 个函数，先做哪个？候选：**被调用越多越是好证人**。

### 结果（6,000 / 321,244 样本）

```
0x1400fe270  callers=4046  size=97      0x1400f7f40  callers=865  size=4
0x1400f70f0  callers=3980  size=288     0x140110140  callers=818  size=182
0x140110430  callers=2916  size=68
```

**top 15 全是无名小函数。** 口径：样本内 top，非全局。

### 反编译坐实

```c
sub_1400F7F40 (865 callers, 4 B)   return *(unsigned int *)(a1 + 80);   // 纯字段读取
sub_1400FDEB0 (868 callers)        if (*(a1 + 74)) { ... }              // 标志位转发
sub_140110430 (2916 callers)       sub_141DC3360(&unk_144B55D18, a2)    // 全局表查找
```

**4 字节、被调 865 次** —— 那不是行为，是每个路径都碰的东西。

### 这是结构性的错，不是样本太小

**入度高 = 所有代码都碰 = 运行期胶水。** 跑满 321k，top 只会更胶水。

### 换判据：按「属于应用」选，不按入度选

**引用应用特有字符串的函数**（locale 键、绑定描述符）—— 那些字符串只有这个应用才有，
且 R703 已证明这类引用可用 `lea [rip+disp32]` 定位。

**这是可证的应用程序，而不是靠入度或名字猜。** 下一轮做。

### 一句话

> 我把「被引用得多」当成了「重要」。**在 321k 函数的二进制里，被引用得最多的是没人会去写的那种代码。**

> **判据错了就换，但要把「为什么错」写下来 —— 否则下一轮还会有人想「按调用次数排序不是挺合理吗」。**

### 下一轮

按「引用应用字符串」选目标。第一步：用 R703 的 disp32 扫描，对 locale 键与描述符字符串找引用函数，
量出这个集合有多大、覆盖多少应用面。
"""


def main():
    for p, marker, text in ((P1, "R719", BLOCKER), (P3, "R719", BLOCKER), (P2, "第 719 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R719: ranking probe targets by caller count selects glue -- criterion rejected\n\n"
         "On a 6,000-of-321,244 sample the top fifteen by inbound references are all unnamed functions of\n"
         "4 to 288 bytes with 700 to 4,000 callers. Three decompiled: a bare field read (4 bytes, 865\n"
         "callers), a flag test that delegates, and a global-table lookup. That is infrastructure, and\n"
         "infrastructure matching says nothing about whether the app's behaviour matches.\n\n"
         "The error is structural, not a sampling issue: high fan-in means every code path touches it,\n"
         "which is precisely where runtime and compiler glue lives. Reaching all 321,244 would only make\n"
         "the top more glue-like.\n\n"
         "Replacement criterion, not yet implemented: select by app belonging -- functions that reference\n"
         "app-specific strings (locale keys, binding descriptors), which R703 showed are reachable through\n"
         "lea [rip+disp32] byte scanning. That is provable app code rather than a guess from fan-in."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
