"""Record R745: NoHeader is an exception message, not a status -- and the replica composed it wrong."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 174. `NoHeader` 是**异常消息**不是状态；复刻件把两句的**组合**做成了单句

> R745。改 `ProfileViews.cs` 的 `Preview()` 一处；新增 `ProfileCsvSentenceCompositionTests`（3 条）。

### 一、先把 CSV 键的产生点画出来

`analysis/csv_key_functions.py`：16 个 CSV 键 → **14 个函数**。

```
0x140f75ee0  size=2041  ProfileCsv.Status.NoHeader          ← 唯一引用 NoHeader
0x140713b20  size=1792  ProfileCsv.Status.Imported          ← 唯一引用 Imported
0x1407145a0  size= 250  ProfileCsv.Status.IgnoredColumns
0x140713888  size=  88  ProfileCsv.Status.ParseFailed
0x140721030  size= 915  ProfileCsv.Clipboard
0x140711f50  size=1631  FixErrors + Summary.*
…
```

**两个 R744 留下的缺口函数都定位到了。**

### 二、`0x140F75EE0` 读了 363 行，只有一个 locale 载入

第 213 行的上下文：

```c
if ( (unsigned int)sub_142DE6B80(v18, v29) )
{
    v55 = localise(&off_146E4D768);      // ProfileCsv.Status.NoHeader
    sub_141D144F0(v54, v55);
    sub_1430291D0(v54);
    __debugbreak();                       // ← 抛出
}
```

**`__debugbreak()` 在这个二进制里就是抛异常**（与 `sub_141BF8DF0(n); __debugbreak();` 同一族）。

**所以 `NoHeader` 是一句异常消息，不是一条状态文本。** 它**没有分支竞争** ——
整个 363 行函数**只产生这一条文案**。

### 三、于是两句是**组合**关系，不是二选一

抛出后由外层解析失败处理器包一层：

```
Couldn't read the CSV: The CSV needs a header row with known column names
```

**用户看到的是这一句。** 而复刻件（R653 的实现）显示的是**内层那句单独出现**。

**R653 把键找对了，把机制判错了。** 它写的是「so that case reports the image's sentence」——
**原版不在那种情况"报告那句"，而是"抛出那句，然后被外层包起来"。**

### 四、改了什么（一处，有证据支持）

```csharp
// 之前
_status.Text = !HeaderHasKnownColumn() ? Text("StatusNoHeader") : …

// 现在
_status.Text = !HeaderHasKnownColumn()
    ? string.Format(Text("StatusParseFailed"), Text("StatusNoHeader"))
    : …
```

**没改的**：兜底那句 `"{0} profile(s) parsed."`。**R744 已记：它的原版对应物 Unknown。**
**没有证据就不动。**

### 五、探针与验证

```
ProfileCsvSentenceCompositionTests   3 / 3
ProfileCsvCopyTests（原有）            通过（它断言的是键的文案，不受影响）
完整套件                             1708 通过 / 0 失败（1705 + 3）
四项度量                             4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- `Imported`（`Merged {0} rows from {1}`）在哪个上下文产生：**Unknown** —— 函数 `0x140713b20`（1,792 B）已定位，未读。
- `Preview()` 兜底那句的原版对应物：**Unknown**（R744 记）。
- `0x140F75EE0` 那 363 行里其余 14 个 CSV 键的调用关系：**Unknown**（只读了 NoHeader 一处）。
"""

VERDICT = """

---

## 第 745 轮：`NoHeader` 是异常消息，复刻件把组合做成了单句

### 先画出 CSV 键的产生点

16 个键 → **14 个函数**，两个缺口函数都定位到了：

```
0x140f75ee0  NoHeader   0x140713b20  Imported
0x1407145a0  IgnoredColumns   0x140713888  ParseFailed
```

### 读了 363 行，只有一个 locale 载入

```c
if (check_fails) {
    v55 = localise(&off_146E4D768);   // NoHeader
    ...
    __debugbreak();                    // ← 抛出
}
```

**`__debugbreak()` 在这里就是抛异常。所以 `NoHeader` 是异常消息，不是状态文本，也没有分支竞争。**

### 于是两句是组合关系

抛出后外层包装：

```
Couldn't read the CSV: The CSV needs a header row with known column names
```

**用户看到的是这一句。而复刻件显示的是内层那句单独出现。**

> **R653 把键找对了，把机制判错了**：它写的是「报告那句」，原版是「抛出那句然后被包起来」。

### 改了，也只改了有证据的那一处

兜底那句 **没动** —— R744 已记它的原版对应物 Unknown。**没有证据就不动。**

### 验证

```
ProfileCsvSentenceCompositionTests   3 / 3
完整套件                             1708 通过 / 0 失败
四项度量                             4 / 0 / 17 / 78 / 0（未变）
```

### 一句话

> 上一轮我挡住了「把一条错文案换成另一条错文案」。**这一轮找到了真原因：不是我该选哪条，是这两条在原版里是套在一起的。**

### 下一轮

`0x140713b20`（1,792 B，唯一引用 `Imported`）—— 读出它，就能回答 R744 的另一个缺口。
"""


def main():
    for p, marker, text in ((P1, "R745", BLOCKER), (P3, "R745", BLOCKER), (P2, "第 745 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R745: NoHeader is an exception message, and the replica had the composition wrong\n\n"
         "Mapping every CSV key to the functions that reference it gave fourteen functions and located both\n"
         "of R744's gaps: 0x140f75ee0 for NoHeader and 0x140713b20 for Imported.\n\n"
         "Reading the first — 363 lines with exactly one locale load — shows the sentence followed by\n"
         "__debugbreak(), which in this binary is a throw. So NoHeader is an exception message, not a status\n"
         "text, and it competes with no other sentence. The parse-failure handler wraps whatever it caught, so\n"
         "the user sees 'Couldn't read the CSV: The CSV needs a header row with known column names'.\n\n"
         "That corrects R653's mechanism while keeping its key: R653 read 'that case reports the image's\n"
         "sentence', but the image throws the sentence and the wrapper surfaces it. The replica was showing\n"
         "the inner sentence alone, which the image never does in that situation.\n\n"
         "Changed one line in Preview() to compose the two keys, with three probes pinning the order and\n"
         "pinning that the bare remark is not what the user sees. Left the invented fallback alone, because\n"
         "R744 recorded that its counterpart is still unknown and there is no evidence for a replacement.\n\n"
         "Suite 1708 pass / 0 fail; four metrics unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
