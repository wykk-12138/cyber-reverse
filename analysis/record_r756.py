"""Record R756: the separator fixed on both sides, verified on screen, plus two corrections."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 185. `2,500`：显示与回读**一起**改，屏幕上确认；并纠正我自己两条说法

> R756。改 `UiKit.cs`（`Number` 格式 + 新增 `TryReadInt`）；6 个文件 **36 处**回读改成 `UiKit.TryReadInt`；
> 新增 `NumberFieldTests`（14 条）。

### 一、改了什么

```csharp
// 之前
Text(value?.ToString(), "0", width)                      // → "2500"
if (int.TryParse(monitor.Text, out var m)) …             // 不容忍逗号

// 现在
Text(value?.ToString("#,0", CultureInfo.InvariantCulture), "0", width)   // → "2,500"
if (UiKit.TryReadInt(monitor.Text, out var m)) …         // 剥掉逗号再解析
```

`TryReadInt` 先 `Replace(",", "")` 再 `int.TryParse`，**两种写法都收**（`2,500` 与 `2500`）。

**范围**：只改 6 个**已引用 `UiKit.`** 的文件（`ProviderViews` 5 / `SettingsViews` 7 / `SettingsModals` 5 /
`StaggerStartView` 6 / `TasksViews` 12 / `ProxyGroupView` 1 = 36 处）。
`TaskEditorWindow` 用自己的框、`ProfileViews` 那处解析的是局部字符串，**都未受影响**。

### 二、屏幕上确认了（不是只有测试绿）

复刻件跑起来，Settings → General：

```
Default Monitor   2,500      Default Error   2,500      Default Timeout   10
```

**与活窗口的 `2,500` 一致；`10` 不加分隔符，正确。三个 `ⓘ` 图标仍在。**

### 三、纠正我自己说的两条

**纠正一（R754/R755）**：我写过「这个仓库的 UI 测试不构造控件」。**错了** ——
`UiKit.Number(...)` 在测试里构造得好好的，`NumberFieldTests` 14 条全过，不需要 Avalonia app。
**准确的说法是：既有 UI 测试*选择了*读源码文本做断言，不是*不能*构造控件。**
这条重要，因为它决定下一轮什么可验证 —— **能构造，就能对行为断言，而不只是对存在断言。**

**纠正二（本轮开头）**：我一度以为 36 点改动会静默丢数据。**实际不会** ——
因为显示与回读是**同一次改动**，且回读比原来更宽容。**风险在"只改一半"，而我没有只改一半。**

### 四、`shape_audit.py` 的那次崩溃：**按崩溃记，不按失败记**

第一次全量跑出现：

```
shape_audit.py exited -1073741819     ← 0xC0000005 访问违例
```

按 AGENTS.md §2.6：**「没跑成」既不等于通过也不等于失败**，单列。

**查证**：直接跑 `shape_audit.py` **5 次，全部 exit 0**（78 处 mismatch，与平时一致）。
**所以是偶发，且与我的改动无关**（改动是 C#，崩溃是 Python 的原生访问违例）。

**但它是套件的一个不稳来源** —— 记在这里，下次全量红在 `ShapeAuditGuardTests` 时先想它。

### 五、验证

```
NumberFieldTests      14 / 14 通过（含 0/1/999/2500/12345/999999/1000000 的往返）
完整套件              1745 通过 / 0 失败 / 0 跳过（1731 + 14）
四项度量              4 / 0 / 17 / 78 / 0（未变）
屏幕                  2,500 / 2,500 / 10 亲眼确认
```

### 六、仍然 Unknown

- 原版**其它**数字框是否也带分隔符：**Unknown** —— 只观测过 Default Monitor / Default Error / Timeout。
  我按"同一个 `UiKit.Number` 控件"的理由推广到全部，**这是 Inference（中）**，不是 Observation。
- 原版是否容忍用户输入不带逗号的 `2500`：**Unknown**（要往它框里打字，红线）。
- `shape_audit.py` 偶发崩溃的触发条件：**Unknown** —— 5 次未复现，与内存压力无关（17 GB 空闲时也出过一次）。
"""

VERDICT = """

---

## 第 756 轮：`2,500` 修好了，屏幕上确认

### 显示与回读一起改

```csharp
Text(value?.ToString("#,0", …), "0", width)     // → "2,500"
UiKit.TryReadInt(monitor.Text, out var m)        // 剥逗号再解析，两种写法都收
```

**6 个文件 36 处回读**（只改已引用 `UiKit.` 的文件）。

### 屏幕上确认

```
Default Monitor  2,500     Default Error  2,500     Default Timeout  10
```

**与活窗口一致；`10` 不加分隔符，正确。**

### 纠正我自己两条

**纠正一**：我说过「这个仓库的 UI 测试不构造控件」。**错了。**
`UiKit.Number` 在测试里构造得好好的，14 条全过。
**准确说法是：既有测试*选择了*读源码文本，不是*不能*构造控件。**
**这决定下一轮什么可验证 —— 能构造，就能对行为断言。**

**纠正二**：我以为 36 点改动会静默丢数据。**实际不会**，因为显示与回读是同一次改动，且回读更宽容。
**风险在"只改一半"，而我没有只改一半。**

### `-1073741819` 按崩溃记

`shape_audit.py` 一次访问违例。**直接跑 5 次全 exit 0** → 偶发、与我的改动无关。
**但它是套件的不稳来源**，下次全量红在那条守卫上先想它。

### 验证

```
NumberFieldTests   14 / 14（含七个值的往返）
完整套件           1745 通过 / 0 失败
四项度量           4 / 0 / 17 / 78 / 0（未变）
```

### 仍然 Unknown

- 原版**其它**数字框是否也带分隔符：**Inference（中）** —— 按"同一个控件"推广，不是观测
- 原版是否容忍不带逗号的输入：**Unknown**（红线）
- 崩溃的触发条件：**Unknown**（5 次未复现）
"""


def main():
    for p, marker, text in ((P1, "R756", BLOCKER), (P3, "R756", BLOCKER), (P2, "第 756 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R756: thousands separators on the number field, with the reader changed in the same breath\n\n"
         "R755 read 2,500 off the live Default Monitor field while the replica showed 2500, and warned that\n"
         "changing only the display would leave every reader failing to parse what the field prints. So both\n"
         "sides moved together: Number formats with '#,0' and a new UiKit.TryReadInt strips separators before\n"
         "parsing, which is strictly more tolerant than the bare int.TryParse it replaces. Thirty-six read sites\n"
         "in the six files that already import UiKit were converted; TaskEditorWindow builds its own boxes and\n"
         "ProfileViews parses a local string, so neither was touched.\n\n"
         "Verified on screen, not only in tests: the running replica now shows 2,500 / 2,500 / 10, matching the\n"
         "live window, with 10 correctly left unseparated and the three info glyphs still drawn. Fourteen\n"
         "probes cover the format and a round trip across seven values.\n\n"
         "Two of my own statements needed correcting. In R754 I wrote that this repo's UI tests do not construct\n"
         "controls; they can -- UiKit.Number builds fine in a test and all fourteen pass without an Avalonia app.\n"
         "What is true is that the existing tests chose source-text assertions, not that construction is\n"
         "impossible, and that distinction decides what the next round can prove. Earlier in this round I also\n"
         "expected silent data loss from thirty-six coordinated edits; there is none, because display and read\n"
         "changed together and the read is now more permissive. The hazard was doing half of it.\n\n"
         "One suite run failed with shape_audit.py exiting -1073741819, an access violation. Per the evidence\n"
         "rules that is a crash, not a failed assertion, and it is recorded separately. Running the script\n"
         "directly five times gave exit 0 every time with the usual 78 mismatches, so it is intermittent and\n"
         "unrelated to a C# change -- but the suite now has a known flake and that is written down.\n\n"
         "Suite 1745 pass / 0 fail; four metrics unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
