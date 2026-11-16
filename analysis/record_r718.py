"""Record R718: behaviour probes whose expectations come from decompilation, not from the replica."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
CLAIMS = r"D:\projects\cyber-reverse\docs\PARITY_CLAIMS.md"

BLOCKER = """

---

## 147. C7c 有了第一批**期望值来自反编译**的行为探针（15 条）

> R718。新增 `replica/tests/Cybersole.Tests/DecompilationDerivedValidationProbes.cs`。

### 一、C7c 卡在哪，以及这一轮的绕法

C7c（"每个函数功能相等"）= `unknown`，理由是「缺原版符号，伪代码等价做不了；正路是**行为探针**」。
而行为探针要跑原版 —— 那需要登录凭据，属 YG 那一类。**所以原版那一侧跑不了。**

**这一轮做的是次好的那件事**：**期望值不来自复刻件的当前行为，而来自反编译**。

**这个区别是全部意义所在**：断言"复刻件现在这样、所以它应该这样"只是在测"实现等于自己"；
断言"反编译说它会这样"才是在测"实现等于原版"。

### 二、探针覆盖的四条，每条都引了反编译出处

| 性质 | 反编译依据 |
|---|---|
| Trim 只动两端、不合并中间空白 | `sub_141CFA390`：只在**首或尾**是空白时才调 `sub_141CFA500`，否则**原样返回** |
| 空白字符集等于 `char.IsWhiteSpace` | 同上：`<0x100` 走 `sub_141D073A0`、`≥0x100` 走 `sub_141D45100` —— 正是 `char.IsWhiteSpace` 的两半 |
| 大小写不敏感、**不展开缩写、不是前缀匹配** | `sub_141DC1950`：先序数比较，失败后按折叠表 `a4 \| 1u` 重试；**没有缩略/前缀分支** |
| 空国家/空州放行；无州表的国家接受任意州 | `sub_140F77350` / `sub_140F777E0`：`if (!len \|\| …) return 0`；`v7 = row ? *(row+96) : 0`，`if (!v7 \|\| size<=0 …) return 0` |
| 州文案第二参是**国家行自己的名字** | 同一函数尾部 `sub_141CF6BF0(v8, a2, *(v6+72))` |

**15 条断言**，含判别力强的几个：
- `"United  States of America"`（中间双空格）→ **拒绝**（Trim 不合并中间空白）
- `"united states"` → **拒绝**（前缀不等于相等）
- `"US"` / `"U.S."` / `"USA"` → **拒绝**（无缩写展开）
- `"AL"` 作为州 → **拒绝**（州比较只看 `[+96]`，不查 `state_abbr`）
- `"  united states of america  "` → **通过**（Trim + 折叠）

### 三、一个正面结论：Trim 不 divergence

`sub_141CFA390` 的空白判定 = `char.IsWhiteSpace`，所以 **C# `String.Trim()` 是等价操作**。
这条现在是**被断言锁住的**：以后若有人把 `Trim()` 改成 `TrimEnd()`、或加 `ToLowerInvariant()`，
探针会红。

### 四、验证

```
dotnet test --filter DecompilationDerived     15 / 15 通过
python tools/metrics_report.py                1639 通过 / 0 失败（1624 + 15）
四项度量                                       4 / 0 / 17 / 78 / 0（未变，本轮只加测试）
```

### 五、这离 C7c 还有多远（不夸大）

**这一步证明的是：**「按反编译读出的规则，复刻件的这四条与之一致」。

**它不能证明：**
- 反编译的**读法**本身对不对 —— 若我把 `sub_141CFA390` 读错了，探针锁住的是**我的误读**
- 其余 ~187,000 个函数里的任何一个
- 原版**实际运行**时的行为（探针没有跑原版）

**所以 C7c 仍是 `unknown`。** 这一轮把它的证据从"没有"变成"有 15 条、每条指得出反编译地址"，
**但没有把它变成 pass**。

### 六、仍然 Unknown

- 反编译读法的正确性：**没有独立校验**（原版跑不起来，无法对拍）。
- 其余函数的行为：**Unknown**，一个函数一条探针的话工作量不可行，需要先解决"选哪些函数"的问题。
- 原版运行期行为：**Unknown**，卡在登录凭据（YG 那一类）。
"""

VERDICT = """

---

## 第 718 轮：第一批期望值来自反编译的行为探针

### C7c 卡在哪

它要"同输入 → 两侧输出对照"，而**原版跑不起来**（需登录凭据，YG 那一类）。

**绕法**：期望值不来自复刻件的当前行为，**而来自反编译**。

> 断言"复刻件现在这样、所以该这样"只是在测"实现等于自己"；
> 断言"反编译说它会这样"才是在测"实现等于原版"。

### 覆盖的四条（各有出处）

| 性质 | 依据 |
|---|---|
| Trim 只动两端、不合并中间空白 | `sub_141CFA390`：仅首/尾空白时调 trim，否则原样返回 |
| 空白集 = `char.IsWhiteSpace` | 同上：`<0x100` 走 `sub_141D073A0`、`≥0x100` 走 `sub_141D45100` |
| 大小写不敏感、无缩写、非前缀 | `sub_141DC1950`：序数比较后按折叠表重试，无缩略分支 |
| 空值放行、无州表接受任意州 | `sub_140F77350` / `sub_140F777E0` |

**15 条断言**，含四个判别力强的反例：中间双空格、`"united states"`、`"US"/"U.S."`、州用 `"AL"`。

### 一个正面结论

空白判定 = `char.IsWhiteSpace`，**C# `Trim()` 等价** —— 现在被断言锁住：谁改成 `TrimEnd()` 或加 `ToLower`，
探针就红。

### 验证

```
探针       15 / 15
完整套件   1639 通过 / 0 失败（1624 + 15）
四项度量   4 / 0 / 17 / 78 / 0（未变）
```

### 不夸大：C7c 仍是 unknown

**证明的是**「按反编译读出的规则，这四条一致」。

**不能证明**：反编译**读法**对不对（读错了就锁住误读）；其余 ~187,000 个函数；原版**实际运行**行为。

> **把证据从"没有"变成"15 条、每条指得出地址"，不等于把它变成 pass。**

### 下一轮

"选哪些函数做探针"是下一个真问题：一个函数一条不可行。
候选判据：按**调用者数量**或**是否在绑定表里**排序，先做被引用最多的。
"""


def main():
    for p, marker, text in ((P1, "R718", BLOCKER), (P3, "R718", BLOCKER), (P2, "第 718 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # C7c gains the evidence in the claim table
    body = io.open(CLAIMS, encoding="utf-8").read()
    old = "| C7c | 任意两函数的**伪代码等价** | **unknown** |"
    if old in body:
        new = ("| C7c | 任意两函数的**伪代码等价** | **unknown**（**R718 起有 15 条行为探针**） |")
        io.open(CLAIMS, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  claims: C7c annotated with the probe count")
    else:
        print("  claims: C7c row MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R718: first behaviour probes whose expectations come from decompilation\n\n"
         "C7c needs same-input/same-output comparison against the original, which needs credentials. What\n"
         "can be done without them is to read the decompiled guards, derive what they must return, and\n"
         "assert the replica agrees -- the expectation then comes from the binary, not from my own code.\n\n"
         "Fifteen assertions across four properties, each citing an address:\n"
         "  sub_141CFA390  trims only when the first or last char is whitespace, so interior runs survive\n"
         "  sub_141D073A0 / sub_141D45100  the two halves of char.IsWhiteSpace, so String.Trim() is equivalent\n"
         "  sub_141DC1950  ordinal first, then a fold-table retry; no abbreviation and no prefix branch\n"
         "  sub_140F77350 / sub_140F777E0  empty passes; a null or empty state list passes anything\n"
         "  sub_141CF6BF0  the state message's second argument is [country+72], the row's own name\n\n"
         "Discriminating negatives: 'United  States of America' (interior double space) rejected,\n"
         "'united states' (prefix) rejected, 'US'/'U.S.'/'USA' rejected, 'AL' as a state rejected.\n\n"
         "Suite 1639 pass / 0 fail. C7c stays unknown: this shows the replica matches MY READING of the\n"
         "decompilation, not that the reading is right, and covers one validator out of ~187,000 functions."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
