"""Record R748: two hypotheses refuted, one tool limitation named -- Imported's argument can't be read."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 177. `Imported` 的参数：**两个假设都被证伪，最后卡在反编译还原本身**

> R748。本轮未改代码。查 `ProfileCsv.Status.Imported` 的 `{1}` 是什么。

### 一、假设一（被证伪）：只传一个参数会留下 `{1}`

R746 我看到 `0x140713B20` 里 `v51 = sub_141CF6BF0(v49)` —— **只显示一个实参**，
而 `Imported` = `Merged {0} rows from {1}` **有两个占位符**。所以怀疑「`{1}` 会原样留着」。

**去反编译那个 helper，假设不成立：**

```c
// sub_141CF6BB0(template, arg)   —— 一个值
v5 = a2; v3 = &v5; v4 = 1;
return sub_141CF6EA0(0, a1, &v3);          // 1 元数组

// sub_141CF6BF0(template)        —— 内部造 2 元数组
sub_141D1FDF0(&v4);
sub_142D3D750(&v3, &off_1449848A0, &v4, 2);
return sub_141CF6EA0(0, a1, &v3);          // 2 元数组
```

**`sub_141CF6BF0` 用两个参数格式化。** 所以两个占位符都会被填。**假设一死。**

### 二、假设二（也被证伪）：第二个参数是「来源名」

`sub_141D1FDF0(&v4)` 看起来像"填入来源"。**反编译它：**

```c
__int64 sub_141D1FDF0(_QWORD *a1)
{
  *a1 = 0;
  a1[1] = 0;
  sub_143028EE0(a1);
  return sub_143028EE0(a1 + 1);
}
```

**它只是把两个槽清零并初始化成 GC 句柄**（`sub_143028EE0` 是同族里反复出现的引用计数初始化）。
**不是"来源名"。假设二死。**

### 三、然后撞上一个**反编译还原本身的问题**

调用方（`0x140713B20` 第 225–228 行）做了这些：

```c
v49 = localise(&off_146E4D718);                        // Imported 模板
v50 = *(v5 + 8);
*(DWORD*)(sub_143028C10(&unk_144DB9458) + 8) = *(DWORD*)(v50 + 16);   // 把计数装箱进一个对象
v51 = sub_141CF6BF0(v49);                              // ← 却只传模板
```

**装箱对象在下一行没有被传进去。** 而 `sub_141CF6BF0` 的两个参数是
`&off_1449848A0`（静态）与 `&v4`（被清零的句柄对）。

**两者对不上。** 两种可能：

1. Hex-Rays 把一次调用折叠了，**实参在寄存器里但它没显示出来** —— 这在此前已经出现过（R731 四个 `off_` 槽读回不合理长度）
2. 装箱对象真的被丢弃 —— 那 `Imported` 会印成 `Merged <静态值> rows from <空>`，**一个已发布的文案不该长这样**

**我没有办法在静态层面区分这两者。** 所以：

> **`Imported` 的 `{1}` 是什么 —— Unknown，缺的是「Hex-Rays 对这次调用的实参还原」，
> 而这一层能力（精确读出被折叠的实参）当前工具链没有。**

**这不是"行为未知"，是"读不到"。两者要分开记。**

### 四、于是 R744 的缺口保持开着，但形状更清楚了

- **已知**：`Imported` 是**成功状态**（在合并完成后设置），`NoHeader` 是抛出，`IgnoredColumns` 随后可能覆盖
- **已知**：两个占位符都会被填（假设一证伪）
- **Unknown**：`{1}` 的具体来源

**所以复刻件要正确产生 `Imported`，缺的不是"知道它在哪产生"，而是"`{1}` 填什么"。**
**在 `ApplyCore` 里我同样没有来源对象** —— 两边的缺是同一件事。

### 五、验证

```
本轮未改产品代码
完整套件   1708 通过 / 0 失败（与 R747 相同）
四项度量   4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- `Imported` 的 `{1}`：**Unknown**，缺 Hex-Rays 对被折叠实参的还原。
- `off_1449848A0` 是什么：**Unknown**（静态对象，可能是装箱类型描述符）。
- 那 9 处自造文案的原版对应物：**Unknown**（R746 记）。
"""

VERDICT = """

---

## 第 748 轮：两个假设都被证伪，最后卡在反编译还原本身

### 假设一：只传一个参数会留下 `{1}` —— 死

反编译 helper：

```c
sub_141CF6BF0(template):
    sub_141D1FDF0(&v4);
    sub_142D3D750(&v3, &off_1449848A0, &v4, 2);   // 2 元数组
```

**它用两个参数格式化。两个占位符都会被填。**

### 假设二：第二个参数是来源名 —— 也死

```c
sub_141D1FDF0(a1):  *a1 = 0; a1[1] = 0; 初始化两个 GC 句柄
```

**不是来源名。**

### 然后撞上反编译还原本身

调用方把计数装箱，**却只把模板传给 helper**。装箱对象在下一行没被传进去。

**两者对不上。** 要么 Hex-Rays 折叠了调用（实参在寄存器但没显示），要么装箱真的被丢弃
—— 后者意味着已发布文案会印成 `Merged <静态值> rows from <空>`，不像真的。

> **`Imported` 的 `{1}` 是什么 —— Unknown。缺的不是行为证据，是「精确读出被折叠实参」这个能力。**

**这两者要分开记：不是"行为未知"，是"读不到"。**

### 于是缺口形状更清楚了

- 已知：`Imported` 是**成功状态**，`NoHeader` 是抛出，`IgnoredColumns` 随后可能覆盖
- 已知：两个占位符都会被填
- **Unknown：`{1}` 填什么**

**复刻件要正确产生 `Imported`，缺的正是这个 —— 而 `ApplyCore` 里我同样没有来源对象。两边的缺是同一件事。**

### 一句话

> 上一轮我准备"再实现一个"，发现已经实现。这一轮我准备"读出参数"，发现读不出。
> **两轮都在缩小"我到底不知道什么"，这本身是进展 —— 但都没让数字动。**

### 验证

```
产品代码未改
完整套件   1708 通过 / 0 失败
四项度量   4 / 0 / 17 / 78 / 0（未变）
```
"""


def main():
    for p, marker, text in ((P1, "R748", BLOCKER), (P3, "R748", BLOCKER), (P2, "第 748 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R748: two hypotheses about Imported's argument refuted, and the limit named\n\n"
         "First hypothesis: the format helper is shown taking one argument while Imported has two\n"
         "placeholders, so {1} would survive literally. Decompiling it refutes that -- sub_141CF6BF0 builds\n"
         "a two-element argument array, so both placeholders are filled.\n\n"
         "Second hypothesis: the second argument is the source name. Decompiling sub_141D1FDF0 refutes that\n"
         "too -- it zeroes a pair of GC handles and initialises them; it is not a source.\n\n"
         "Then the trail hits the decompiler itself. The caller boxes the row count and then passes only the\n"
         "template, while the helper's two arguments are a static object and a cleared handle pair. Those two\n"
         "accounts do not fit: either Hex-Rays folded the call and did not show the argument in the register,\n"
         "or the boxed value really is dropped -- and a shipped sentence that would print 'Merged <static> rows\n"
         "from <empty>' does not look real.\n\n"
         "I cannot separate those two statically, so Imported's {1} stays Unknown, and the missing thing is\n"
         "specifically 'reading the folded argument back', which this toolchain does not offer. That is a\n"
         "reading limit, not absent behaviour, and the two are recorded separately.\n\n"
         "The gap R744 opened therefore stays open, but its shape is sharper: the replica needs a source\n"
         "object to produce Imported, and ApplyCore has none either. Both sides are missing the same thing.\n\n"
         "No product code changed; suite 1708 pass / 0 fail; four metrics unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
