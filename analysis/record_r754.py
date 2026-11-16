"""Record R754: the (i) marker now renders as a glyph, and Language gains the fourth one."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 183. `(i)` 不再作为字符上屏：`Row` 自己解释它；`Language` 补上第四个标记

> R754。改 `UiKit.cs`（`Row` + 新的 `MarkedLabel`）与 `SettingsViews.cs`（`Language` 一行）；
> `GeneralSettingsLayoutTests` +2 条断言。

### 一、改了什么

**`UiKit.Row` 把标签交给 `MarkedLabel`**，后者识别前缀 `"(i)"` 并画一个圆圈 i：

```
Border(14×14, CornerRadius 7, BorderThickness 1, BorderBrush = UiKit.Dim)
  └ TextBlock("i", FontSize 10, Foreground = UiKit.Dim)
```

**颜色用 `UiKit.Dim`**（这份文件里本来就有：`FromArgb(0xB0,0xC8,0xC8,0xC8)`）——**没有引入新颜色常量**。

**`Language` 那行补上标记**：活窗口有 4 行带图标（`Language` / `Monitor Concurrency` / `Startup Page` / `Currency`），
源码只有 3 处带标记，**缺的正是 `Language`**。

### 二、为什么改在 `Row` 里而不是改三个调用点

标记留在字符串里，是因为**那三行本来就是这么写的**；把它变成参数会改动三个调用点，
而**在 `Row` 里解释它一次就把全部修好**，并且让"标记"有了唯一含义。

### 三、**这条改动没有被渲染验证** —— 必须写清

**这个仓库的 UI 测试不构造控件，它们读源码文本做断言。** `GeneralSettingsLayoutTests` 第 100–102 行
本来就是三个 `Assert.Contains("UiKit.Row(\\"(i)  …\\"", source)`。

所以新增的两条也是同一形态：

- `Assert.Contains("UiKit.Row(\\"(i)  Language\\"", source)` —— 钉住第四个标记
- `TheMarkerIsInterpretedRatherThanPrinted` —— 断言 `Row` 委托给 `MarkedLabel`、
  `MarkedLabel` 存在、`const string marker = "(i)"` 存在、`text[marker.Length..]` 存在

**它们证明的是"这段代码在那里"，不是"屏幕上画出了圈**i"。**

**要真的验证渲染，得把复刻件跑起来截图。** 本轮没做，记为下一步：
`dotnet run` 复刻件 UI（Debug 比 AOT 发布快得多），开 Settings → General，看那四行。

**这一条要写进文档，因为它是本轮唯一未被验证的部分** —— 而"改了代码 + 测试绿"很容易被当成"验证过了"。

### 四、验证

```
GeneralSettingsLayoutTests   5 / 5 通过（+2 条）
完整套件                     1731 通过 / 0 失败（1730 + 1）
四项度量                     4 / 0 / 17 / 78 / 0（未变）
```

### 五、仍然 Unknown

- **复刻件渲染出来是不是圈 i**：**Unknown** —— 无测试构造控件，本轮也没跑起来看。
- 原版那个 glyph 的确切颜色与尺寸：**Inference（低）** —— `Dim` 是"看起来接近"，**没有采样像素**。
  活窗口截图里的 `ⓘ` 是淡灰蓝，`Dim` 是 `0xC8C8C8` 半透明；**相近但不等同**。
- `FontSize 10 / 14px / 圆角 7` 三个数字：**Inference（低）** —— 按截图目测，未量。
- 除 `General` 面板外是否还有别的地方带这个标记：**Unknown**（只统计了 `UiKit.Row` 的首参）。
"""

VERDICT = """

---

## 第 754 轮：`(i)` 不再上屏；`Language` 补第四个标记

### 改了什么

`UiKit.Row` 交给新的 `MarkedLabel`，后者识别前缀 `"(i)"` 并画一个 14px 圆圈、里面一个 `i`，颜色用文件里已有的 `UiKit.Dim`。**没有引入新颜色常量。**

`Language` 补上标记 —— 活窗口 4 行带图标，源码 3 处，缺的正是它。

### 改在 `Row` 里，不改三个调用点

标记留在字符串里是因为那三行本来就这么写的；**在 `Row` 里解释一次就把全部修好**。

### **这条改动没有被渲染验证 —— 必须写清**

**这个仓库的 UI 测试不构造控件，只读源码文本。** 新增的两条断言证明的是**「这段代码在那里」**，
**不是「屏幕上画出了圈 i」**。

> **而「改了代码 + 测试绿」很容易被当成「验证过了」。这一条得单独写，因为它是本轮唯一未验证的部分。**

要真验证得把复刻件跑起来截图 —— 记为下一步。

### 连颜色都是近似的

活窗口的 `ⓘ` 是淡灰蓝，`Dim` 是 `0xC8C8C8` 半透明：**相近但不等同，我没有采样像素。**
`FontSize 10 / 14px / 圆角 7` 也是目测，未量。

### 验证

```
GeneralSettingsLayoutTests   5 / 5（+2）
完整套件                     1731 通过 / 0 失败
四项度量                     4 / 0 / 17 / 78 / 0（未变）
```

### 下一轮

**把复刻件跑起来**（`dotnet run` Debug），开 Settings → General，截图核那四行。
这是唯一能把"代码里有"变成"屏幕上有"的办法。
"""


def main():
    for p, marker, text in ((P1, "R754", BLOCKER), (P3, "R754", BLOCKER), (P2, "第 754 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R754: the (i) marker renders as a glyph, and Language gains the fourth one\n\n"
         "R753 found the literal characters '(i)' standing in for the window's info icon on three labels while\n"
         "the live pane showed four icon rows. UiKit.Row now hands its label to a new MarkedLabel that turns the\n"
         "prefix into a 14px circle containing an i, coloured with the UiKit.Dim brush this file already had, so\n"
         "no new colour constant was introduced. Interpreting the marker in Row fixes all three call sites at\n"
         "once and gives the marker a single meaning; Language, the row that was missing it, now carries it.\n\n"
         "The honest part of this round is what did NOT get verified. The UI tests in this repo do not construct\n"
         "controls -- they read source text and assert on it, which is how the three existing markers were pinned\n"
         "in the first place. The two assertions added here follow that idiom, so they prove the delegation and\n"
         "the marker handling exist in the file, not that a circle is drawn on screen. Rendering it would mean\n"
         "running the replica and taking a screenshot, which is the next step.\n\n"
         "Even the appearance is approximate and labelled as such: the live glyph reads as a pale grey-blue while\n"
         "UiKit.Dim is 0xC8C8C8 with alpha, and the 14px/7 radius/10pt figures were eyeballed from a screenshot\n"
         "rather than measured.\n\n"
         "Suite 1731 pass / 0 fail; four metrics unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
