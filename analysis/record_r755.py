"""Record R755: the icon verified on screen, and seven differences a side-by-side found."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 184. 复刻件跑起来了：**图标在屏幕上确认**；并排比较查出 7 处差异

> R755。未改产品代码。把复刻件 Debug 版跑起来（pid 11100），把它的 Settings → General 与原版并排看。

### 一、R754 的图标**渲染确认了**（3/4）

截图可见三行前面是**圆圈里一个 i**，不再是字符 `(i)`：

```
ⓘ Language            English
ⓘ Monitor Concurrency Unlimited | 3 | 0.1
ⓘ Startup Page        Home
```

**`Currency` 在折叠线下，滚动 6 行没到，没看到 —— 报 3/4 而不是 4/4。**

### 二、并排比较：**7 处差异**

| # | 项 | 原版 5.18.35 | 复刻件 | 性质 |
|---|---|---|---|---|
| 1 | **数字格式** | **`2,500`** | **`2500`** | **格式差异，有证据，可修** |
| 2 | `CHECK FOR UPDATES` | 绿色**文字链接** | **带框按钮** | 形状差异 |
| 3 | 分区外框 | **无边框** | 每块一个**圆角描边卡片** | 形状差异 |
| 4 | 顶栏 | **无标签图标按钮** | `Sign in / Sign out / License / Solver / Browser / Monitor / 3DS` **文字按钮** | 结构差异 |
| 5 | 窗口标题 | `Cybersole` | `Cybersole 5.18.32 — functional replica` | 有意区分 |
| 6 | 导航控件类型 | `RadioButton` | `TabItem` | a11y 树差异 |
| 7 | `Monitor Concurrency` / `Queue Presentation` / `ATC Browser Proxy` 的值 | `Maximum` / `Time remaining` / `None` | `Unlimited` / `Standard` / `Group 1` | **数据差异，不是分歧** |

**第 7 条不能当分歧**：那些值来自**各自的 settings**，而复刻件的 settings 是它自己写的
（AGENTS.md §2.2：复刻件自己写出的 settings 不得当实机证据）。**只有"全新安装的默认值"才可比，而我没有那一侧。**

### 三、一条正面的结果

**左侧 16 项分区顺序完全一致**（General … Data / `ADVANCED` / Captcha Providers … Payment / Need Help? / Log Out），
**`Version 5.18.32`** 也对 —— 它映的是对等目标版本，不是运行中的 5.18.35。这点是对的。

### 四、第 1 条单独说：**`2,500` 是格式差异，而修它要 35 个点联动**

原版 UIA 的 `value` 就是 **`"2,500"`**（Observation）。复刻件：

```csharp
public static TextBox Number(int? value, double width = 120) =>
    Text(value?.ToString(), "0", width);                       // ← 无分隔符
if (int.TryParse(monitor.Text, out var m)) s.MonitorDelay = m;   // ← 也不容忍逗号
```

**统计：`UiKit.Number` 调用点 35 个，对应的 `int.TryParse` 约 35 个。**

**所以只改显示会出静默数据丢失**：字段显示 `2,500`，`int.TryParse` 失败，
`s.MonitorDelay` 保持旧值 —— **用户改了、保存了、什么都没发生，没有任何提示。**

**本轮不做，理由**：这是 35 点联动的机械改，且有静默失败模式，
**应当独占一轮、带一个共享的回读助手（`UiKit.ReadNumber`）和测试**，
而不是塞在"验证图标"这一轮的尾巴上。

### 五、验证

```
本轮未改产品代码
完整套件保持 1731 通过 / 0 失败
复刻件进程 11100 已关闭
```

### 六、仍然 Unknown

- **第 1 条原版是否容忍用户输入不带逗号的 `2500`**：**Unknown** —— 要往原版设置框里打字，
  那会改动它的数据，**红线，不做**。
- `Currency` 那行是否也渲染成图标：**Unknown** —— 在折叠线下，滚动没到。
- 第 2/3/4 条是**有意简化**还是**遗漏**：**Unknown** —— 没有作者意图的证据。
- 原版顶栏那 5 个无标签按钮各是什么：**Unknown** —— a11y 树给的 name 是控件类型名。
"""

VERDICT = """

---

## 第 755 轮：复刻件跑起来，图标确认，并排查出 7 处差异

### R754 的图标确认了 —— 3/4

```
ⓘ Language            English
ⓘ Monitor Concurrency Unlimited | 3 | 0.1
ⓘ Startup Page        Home
```

**`Currency` 在折叠线下，没看到 —— 报 3/4 而不是 4/4。**

### 并排比较：7 处差异

| # | 项 | 原版 | 复刻件 |
|---|---|---|---|
| 1 | **数字格式** | **`2,500`** | **`2500`** |
| 2 | `CHECK FOR UPDATES` | 绿色文字链接 | 带框按钮 |
| 3 | 分区外框 | 无 | 圆角描边卡片 |
| 4 | 顶栏 | 无标签图标 | **7 个文字按钮** |
| 5 | 窗口标题 | `Cybersole` | `… — functional replica` |
| 6 | 导航控件 | RadioButton | TabItem |
| 7 | 三个下拉值 | 各自 settings | **数据差异，不是分歧** |

**第 7 条不能当分歧** —— 值来自各自的 settings，复刻件的 settings 是它自己写的。

### 一条正面结果

**16 项分区顺序完全一致**，`Version 5.18.32` 也对（映的是对等目标，不是运行中的 5.18.35）。

### `2,500` 单独说：修它要 35 个点联动

`UiKit.Number` 35 个调用点，对应约 35 个 `int.TryParse`。**只改显示会静默丢数据**：
显示 `2,500` → 解析失败 → 值保持旧 → **用户改了、保存了、什么都没发生**。

**本轮不做**，因为它该独占一轮、带一个共享回读助手和测试，**而不是塞在"验证图标"的尾巴上。**

### 一句话

> 我这一轮的目标是核实上一轮欠的那一步。**核实做到了 3/4，而顺手查出的东西比它自己更重要：**
> **一个数字格式差异，四度量看不见，改起来要 35 个点联动，改一半就静默丢数据。**

### 下一轮

做第 1 条：`UiKit.ReadNumber` + 35 处回读改造 + 测试钉住 `2,500` 能读回 2500。
"""


def main():
    for p, marker, text in ((P1, "R755", BLOCKER), (P3, "R755", BLOCKER), (P2, "第 755 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R755: the icon verified on screen, and a side-by-side found seven differences\n\n"
         "Ran the replica's Debug build and compared its Settings > General against the live original.\n"
         "R754's change works: three of the four rows now draw a circled i where the characters '(i)' used to sit.\n"
         "Currency is below the fold and the scroll did not reach it, so this is 3 of 4 and is recorded as such\n"
         "rather than rounded up.\n\n"
         "The comparison produced seven differences. Five are real: the thousands separator (the original shows\n"
         "2,500 where the replica shows 2500), CHECK FOR UPDATES drawn as a green text link versus a bordered\n"
         "button, section blocks with no border versus rounded outlined cards, a top bar of unlabelled icon\n"
         "buttons versus seven text buttons, and a window title that differs. One is an accessibility-tree\n"
         "artefact (RadioButton versus TabItem) and one is not a divergence at all -- three dropdown values come\n"
         "from each build's own settings, and the replica's settings are its own output, which the evidence rules\n"
         "forbid treating as a real-machine observation.\n\n"
         "There is also a positive result worth recording: all sixteen sections appear in the same order, and the\n"
         "version line reads 5.18.32, mirroring the parity target rather than the 5.18.35 that happens to be\n"
         "running.\n\n"
         "The separator is the finding worth its own round. UiKit.Number has thirty-five call sites and most are\n"
         "read back with a bare int.TryParse. Formatting the display without changing the read-back would make\n"
         "the field show 2,500, fail to parse on save, and silently keep the old value -- a data loss the user\n"
         "never sees. So it is not done here: it needs a shared read helper, thirty-five coordinated edits and\n"
         "tests, which is a round of its own rather than the tail of this one.\n\n"
         "No product code changed; suite remains 1731 pass / 0 fail; the replica process was closed."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
