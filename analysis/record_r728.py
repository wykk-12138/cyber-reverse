"""Record R728: string-reference signatures are relocation invariant -- 90.8% against byte hashing's 25.1%."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
EC = r"D:\projects\cyber-reverse\docs\EVIDENCE_CLASSES.md"

BLOCKER = """

---

## 157. 字符串引用签名确实是重排不变的：**90.8%** vs 字节法的 **25.1%**

> R728。新增 `analysis/string_signature_compare.py`；复用 `disp32_scan_any.scan` 与 `pdata_unwind`。

### 一、要解决什么

R726 量出字节哈希给 25.1%，掩码后 29.4%，**被重排污染**。R727 查完两个参考仓库后确认：
`rea` 的字节层自己也写着 `relocations are not normalized`，撞同一堵墙。
于是走它剩下的那层思路的一个便宜版本：**一个函数引用了哪些字符串内容，是重排不变的。**

### 二、做法

1. 纯字节抽两侧字符串并记 **VA**（`ASCII[\\x20-\\x7e]{6,}` 与 `UTF-16 (?:[\\x20-\\x7e]\\x00){6,}`）
2. `disp32_scan_any.scan` 一次过 `.text`，命中点即「某条 `lea` 的位移解析到这个字符串地址」
3. 命中点 → 所属函数：`.pdata` 的 RVA 区间 + `bisect`
4. 每函数签名 = 其引用字符串内容的**排序后哈希**
5. 两侧比签名多重集

### 三、结果

```
5.18.32  函数 277,094   有签名 25,116 个不同值
5.18.35  函数 277,265   有签名 25,063 个不同值

无字符串引用的函数   193,526 / 193,712   （排除，见第五节）
签名相同             75,897
只在 5.18.32          7,671
只在 5.18.35          7,656
相同率（非空）        90.8%
```

**同一对镜像，字节法 25.1%，字符串签名 90.8% —— 3.6 倍。**
差额正是被重排污染的那部分，**这说明这个方法确实把重排噪声剔掉了**。

### 四、这一轮我先写错了一次，值得记

第一版输出「两侧所有函数签名都是空」——277,094 / 277,094 全无签名。

**原因**：`D.scan` 返回的是**文件偏移**，我写 `site + TEXT_VA - TEXT_OFF` 得到 **VA**，
却把变量命名为 `rva`，而 `.pdata` 的 `begin` 是 **RVA**。`bisect_right(starts, VA)` 落到表尾，
`rva < end` 永远假，`per_func` 全空。

**修法**：`va = site + TEXT_VA - TEXT_OFF; rva = va - base`。

**这个 bug 的形状值得记住**：**VA 和 RVA 差一个 image base，而两者都能"看起来像地址"，
任何一处混用都会安静地产生 0 而不是报错。**

### 五、这个方法能证明什么、不能证明什么（不夸大）

**能证明**：两个函数引用了同一批字符串内容 → **它们的差异不能由重排解释**。

**不能证明**：
- **签名相同 ≠ 行为相同**。两个函数可以引用同一批字符串而顺序、条件、组合完全不同。
  **签名是必要条件，不是充分条件。**
- **70% 的函数没有签名**（193,526 / 277,094 = 69.9% 无任何字符串引用），这个方法**对它们什么都不说**。
- `.pdata` 只覆盖 86.2%，**叶子函数不在内**。

**所以 90.8% 的正确读法是**：「在有字符串引用的那 30.1% 非叶函数里，90.8% 的字符串引用集合两版一致。」
**不是**「91% 的函数没变」。

### 六、这给了 C7c 什么

R726 缺的是「把版本特有逻辑从见证候选里剔掉」。现在有了：

- **75,897 个函数**：字符串引用在两版之间一致 → **可作为稳定见证候选**
- **15,327 个函数**（7,671 + 7,656）：字符串引用变了 → **是版本特有逻辑，当见证不具代表性**
- **193,526 个函数**：这个方法不覆盖，**Unknown**

**候选集第一次有了一个不依赖我判断的筛子。**

### 七、仍然 Unknown

- 那 15,327 个「变了」的函数里，有多少是**真的逻辑改动**、多少是**字符串被加/删导致的连带**：**Unknown**。
- 签名相同的那 75,897 个里有多少**行为真相同**：**Unknown**（必要非充分）。
- 无字符串引用的 69.9% 该怎么筛：**Unknown**（需要另一种重排不变的特征，如调用图指纹）。
"""

VERDICT = """

---

## 第 728 轮：字符串引用签名 —— 90.8%，字节法只有 25.1%

### 做法

抽两侧字符串并记 VA → `disp32_scan_any` 一次扫 `.txt` 找 `lea` 命中 → `.pdata` 归属到函数 →
每函数签名 = 引用内容的排序哈希 → 比多重集。

### 结果

```
有签名      25,116 / 25,063 distinct
签名相同    75,897
只在 32      7,671      只在 35      7,656
相同率      90.8%   ←  字节法 25.1%
```

**同一对镜像，3.6 倍。差额正是被重排污染的那部分。**

### 我先写错了一次

第一版两侧签名**全空**。原因：`D.scan` 返回文件偏移，我算出 **VA** 却把变量叫 `rva`，
而 `.pdata` 的 `begin` 是 **RVA** —— `bisect` 落到表尾，全部落空。

> **这个 bug 的形状值得记住：VA 和 RVA 差一个 image base，两者都"看起来像地址"，
> 混用会安静地产生 0 而不是报错。**

### 不夸大

**能证明**：引用同一批字符串内容 → 差异不能由重排解释。
**不能证明**：签名相同 ≠ 行为相同（**必要非充分**）；**70% 的函数无字符串引用，这方法对它们什么都不说**；`.pdata` 只覆盖 86.2%。

**90.8% 的正确读法**：「在有字符串引用的 30.1% 非叶函数里，90.8% 的引用集合两版一致。」
**不是**「91% 的函数没变」。

### 这给了 C7c 什么

- **75,897 个**：两版一致 → **稳定见证候选**
- **15,327 个**：变了 → **版本特有逻辑，当见证不具代表性**
- **193,526 个**：不覆盖，**Unknown**

> **候选集第一次有了一个不依赖我判断的筛子。**

### 下一轮

用这 75,897 个当池子，从中选见证；15,327 个明确排除并写进文档。
"""


def main():
    for p, marker, text in ((P1, "R728", BLOCKER), (P3, "R728", BLOCKER), (P2, "第 728 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(EC, encoding="utf-8").read()
    old = "**不可用于选稳定函数**；可靠的只有 `+171` 个新增 `.pdata` 条目"
    if old in body:
        new = ("**字节法不可用**；**字符串引用签名可用**（R728：90.8% vs 25.1%，覆盖有字符串引用的 30.1% 非叶函数）；"
               "另 `+171` 个新增 `.pdata` 条目")
        io.open(EC, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  EVIDENCE_CLASSES.md: class 7 updated with the working method")
    else:
        print("  EVIDENCE_CLASSES.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R728: string-reference signatures are relocation invariant -- 90.8% against byte hashing's 25.1%\n\n"
         "R726 showed byte hashing cannot separate logic change from relayout. This measures the invariant\n"
         "that can: which string CONTENTS a function references. Extract strings with their VAs from raw\n"
         "bytes, scan .text with the existing disp32 scanner, attribute hits to functions through .pdata,\n"
         "and compare the per-function sets.\n\n"
         "  5.18.32 25,116 distinct non-empty signatures, 5.18.35 25,063\n"
         "  75,897 identical\n"
         "  7,671 only in 32, 7,656 only in 35\n"
         "  90.8% identical among non-empty, against 25.1% for byte hashing -- 3.6x\n\n"
         "That gap is the relayout noise being removed, which is the whole point.\n\n"
         "First version reported every signature empty on both sides: D.scan returns file offsets, I turned\n"
         "one into a VA and named it `rva`, and .pdata begin/end are RVAs, so the bisect landed past the\n"
         "last function. VA and RVA differ by an image base and both look like addresses; mixing them\n"
         "produces a quiet zero instead of an error.\n\n"
         "Limits: equal signature is necessary, not sufficient, for equal behaviour; 69.9% of non-leaf\n"
         "functions reference no string at all and this method says nothing about them; .pdata covers 86.2%.\n"
         "So 90.8% reads as 'among the 30.1% of non-leaf functions that reference strings, 90.8% reference\n"
         "the same ones in both builds', not as '91% of functions are unchanged'."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
