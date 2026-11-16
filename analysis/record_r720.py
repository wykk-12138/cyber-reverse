"""Record R720: the app-belonging criterion works, and the two criteria are 20.8x apart in median size."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 149. 换判据成功：**239 个函数**可证是应用代码，中位尺寸是胶水判据的 **20.8 倍**

> R720。新增 `analysis/app_string_functions.py`；产出 `analysis/app_string_functions.tsv`。

### 一、判据（先定）

R719 证明「按调用者数」选出来的是胶水。替换判据：**引用应用特有字符串的函数**——
locale 键是只有这个应用才有的字符串，引用了它的函数，可证是应用代码。

**复用而不是重写**：`analysis/disp32_scan_any.py`（R702 为对齐盲点写的）本来就是**集合式**的：
一次 numpy 过 `.text`，`searchsorted` 判成员，一遍能吃 1142 个目标。**直接 import。**

### 二、结果

```
locale 键总数              1142
IDA 能定位到的键            985   (86.3%)
解析到这些键的 lea 站点     1162
去重后的函数                239
```

**口径必须说清**：只定位到 86.3% 的键，所以 **239 是下限，不是总数**。

### 三、验证判据本身（这一步不能省）

```
239 个函数：min=41  中位数=1411  max=53,709
≥512 字节的有 145 个 (61%)
最大的一个 53,709 字节
```

**和 R719 的胶水直接对比**：

```
R719 判据（调用者最多的 15 个）：中位尺寸    68 B
R720 判据（引用应用字符串的 239 个）：中位尺寸 1,411 B
比值：20.8 倍
```

**同一个二进制、同一个尺寸字段，两个判据差了 20 倍。** 这不需要再争论哪个选得对。

### 四、这解决了什么

R718 之后的问题是「187,000 个函数先做哪个探针」。现在有一个 **239 个函数**的清单，
且**每一条都满足一个可证的性质**（引用了本应用独有的字符串）。

**候选面从 187,000 降到 239，且降的理由是证据不是启发式。**

### 五、仍然 Unknown

- 剩下 157 个键（13.7%）为什么 IDA 定位不到：**Unknown**（可能是打包 blob 内的碎片，R715 记过同类）。
- 这 239 个里有多少**已经有行为探针**：**Unknown** —— 目前只有 R718 那 15 条，覆盖的是一个校验器。
- 这 239 个是否覆盖了绑定表相关的行为：**Unknown**（未交叉）。

### 六、下一轮

从 239 里挑**最大的几个**做第一批探针目标——尺寸在这里是「逻辑密度」的代理，
且 R719 已经证明小函数是胶水。第一个候选：`sub_1405ABBF0`（53,709 字节）。
"""

VERDICT = """

---

## 第 720 轮：换判据成功，239 个函数，20.8 倍

### 判据

**引用应用特有字符串的函数**——locale 键只有这个应用才有。复用 R702 的 `disp32_scan_any.py`（本来就是集合式的）。

### 结果

```
locale 键 1142 → IDA 定位到 985 (86.3%)
lea 站点 1162 → 去重函数 239
```

**239 是下限**（只定位到 86.3% 的键）。

### 验证判据本身

```
239 个函数：中位数 1,411 B，最大 53,709 B，≥512 B 的 145 个
R719 胶水判据的 15 个：中位数 68 B
比值 20.8 倍
```

**同一个二进制、同一个尺寸字段，两个判据差 20 倍。** 不用再争哪个选得对。

### 这解决了什么

R718 之后的问题「187,000 先做哪个」，现在有一个 **239 条、每条都有可证性质**的清单。
**候选面从 187,000 降到 239，降的理由是证据不是启发式。**

### 一句话

> R719 我用一个坏判据得到一个荒谬答案（4 字节的函数"最重要"），
> **然后没有去调参数，而是把判据本身换掉，并给新判据一个可证的定义。**

> 换对了的信号不是"看起来更合理"，是 **20.8 倍**。

### 下一轮

从 239 里挑最大的几个做探针。第一个候选 `sub_1405ABBF0`（53,709 B）。
"""


def main():
    for p, marker, text in ((P1, "R720", BLOCKER), (P3, "R720", BLOCKER), (P2, "第 720 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R720: select probe targets by app belonging -- 239 functions, 20.8x the glue criterion's median size\n\n"
         "R719 showed caller-count ranking selects four-byte field getters. The replacement criterion is\n"
         "app belonging: a function that loads one of the app's own locale keys is app code by construction.\n"
         "analysis/disp32_scan_any.py already matched a SET of target addresses in one numpy pass, so it is\n"
         "imported rather than rewritten.\n\n"
         "  1142 locale keys -> 985 located by IDA (86.3%) -> 1162 lea sites -> 239 distinct functions\n\n"
         "239 is a floor, since 13.7% of the keys were not located.\n\n"
         "The criterion is validated by contrast rather than by assertion: median function size is 1,411 B\n"
         "under this criterion against 68 B for R719's top fifteen, on the same binary and the same size\n"
         "field -- a factor of 20.8. Candidate set drops from 187,000 to 239, and the reduction is evidence\n"
         "rather than a heuristic."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
