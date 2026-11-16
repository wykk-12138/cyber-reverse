"""Record R753: live Settings evidence, a false absence from my own scan, and the (i) placeholder."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
HANDOFF = r"D:\projects\cyber-reverse\docs\HANDOFF.md"

BLOCKER = """

---

## 182. 首次用活窗口取证据：拿到 Settings 全表；**我的扫描报了个假缺席**；**`(i)` 是图标占位符**

> R753。未改产品代码（内存 2.45 GB，不构建）。证据来源：运行中的 **5.18.35**（pid 30936）。
> **身份声明**：观测对象是 5.18.35，不是对等目标 `target\\Cybersole.exe`（5.18.32）。
> YG 说明「小版本更新都是个别网站的微调，不影响前端界面」—— 这是 **user-statement 级**依据，
> 不是 5.18.32 的 tool-evidence。**本节的每条 UI 观测都带着这个限定。**

### 一、活窗口给出的 Settings 全表（Observation）

窗口自己印 **`Version 5.18.35`** + `CHECK FOR UPDATES`。

左侧 16 项，中间有 `ADVANCED` 分隔：

```
General  Appearance  Notifications  Webhooks  Email Accounts  Google Accounts
PayPal Accounts  Data
--- ADVANCED ---
Captcha Providers  Cloudflare Providers  Keyboard Shortcuts
Custom Stores  Custom Sizes  Payment  Need Help?  Log Out
```

General 面板的标签与值：

```
Language = English
Default Delays: Default Monitor 2,500 ms | Default Error 2,500 ms | Default Timeout 10 sec
Quicktask Settings: Default Profiles None | Default Proxies None
Shopify Settings: ATC Browser Proxy None | Queue Presentation "Time remaining"
Monitor Concurrency = Maximum / 3 max
Startup Page = Home
Currency = USD
Enable clock
```

**Home 页另有两个可校核点**：`Releases ‹ 1 / 1 ›`（3 张卡 → `(3+2)/3 = 1` 页，
印证 R747 修的分页模型：`0 / 0` 是空态、`1 / 1` 是常态），
以及三句空态文案逐字一致（R205 钉的 `EmptyHeadline` / `EmptyPeriodBody` / `EmptyFeedBody`）。

### 二、**我的扫描报了个假缺席**

我按 `"Startup Page"`（引号紧邻）扫复刻件源码，报 **ABSENT**。

**实际存在** —— `SettingsViews.cs:362`：

```csharp
UiKit.Row("(i)  Startup Page", startup)
```

**真实标签是 `"(i)  Startup Page"`，我的规则要求 `"` 紧跟 `Startup`。**
按子串重扫：**16/16 分区在、15/15 General 标签在。**

> **这正是我反复写进 AGENTS.md 的那一条：缺席的证据 ≠ 行为不存在。**
> **这次踩它的是我自己的工具，而不是我的判断 —— 而工具比判断更危险，因为它看起来客观。**

**另一条更重要的限定**：即使子串命中，也只证明**字符串存在于源码**，
**不证明那一行被渲染**。所以「15/15」是覆盖率的上界，不是渲染确认。

### 三、**`(i)` 是字面文字冒充图标**

`"(i)  Startup Page"` 里的 `(i)` 是**图标占位符**。活窗口那几行前面是 `ⓘ` 字形。

统计：**`UiKit.Row` 共 259 处调用，只有 3 处首参以 `"(i)"` 开头，全在 `SettingsViews.cs`。**

**而活窗口的 General 面板有 4 行带 `ⓘ`**：`Language`、`Monitor Concurrency`、`Startup Page`、`Currency`。

**所以复刻件渲染时那三行会显示字符 `(i)`，而不是图标** —— 与原版可见的差异。
**四度量结构上看不到这类差异**（它们数成员与类型，不数渲染）。

### 四、下一轮该做什么

1. **把 `(i)` 换成真图标**（`UiKit.Row` 加一个 icon 参数，3 处调用改）——
   需要一次构建，本轮内存不足。
2. 补 `Language` 那行缺的图标。
3. 回 `analysis/count_shaped_copy.py` 的 7 条未消费文案。

### 五、仍然 Unknown

- 那 4 个 `ⓘ` 图标的确切字形与位置：**Inference（中）**，从截图看出、未取字形资源。
- `Language` 行为何没有 `(i)` 前缀：**Unknown** —— 可能用别的机制，也可能是漏的。
- 5.18.32 的 Settings 是否与这 16 项完全一致：**Unknown** —— 只有 5.18.35 的观测 + YG 的口头判断。
- General 各下拉框的**完整选项集**：**Unknown**（只看到当前值）。
"""

VERDICT = """

---

## 第 753 轮：第一次用活窗口取证据

### 拿到了 Settings 全表

16 个分区 + `ADVANCED` 分隔 + General 面板 14 个标签与当前值，全部记进 BLOCKERS §182。
**Home 页另印证两处**：`Releases ‹ 1 / 1 ›`（3 卡 → 1 页，印证 R747 的分页模型）、三句空态逐字一致（印证 R205）。

### 我的扫描报了个假缺席

按 `"Startup Page"` 扫源码 → ABSENT。**实际是 `"(i)  Startup Page"`，引号没紧跟。**

> **正是我反复写进 AGENTS.md 的那条：缺席的证据 ≠ 行为不存在。
> 这次踩它的是我的工具而不是我的判断 —— 而工具更危险，因为它看起来客观。**

**而且还有一层限定**：「字符串在源码里」≠「那行被渲染出来」。**所以 15/15 是上界。**

### `(i)` 是字面文字冒充图标

`UiKit.Row` 259 处调用里 **只有 3 处**首参带 `"(i)"`，全在 `SettingsViews.cs`。
**而活窗口有 4 行带 `ⓘ`。**

**所以复刻件渲染时那三行显示字符 `(i)`，不是图标。** 四度量看不到这类差异。

### 这一轮真正的价值

> **有了活窗口，我能看见四度量结构上看不到的那一类差异：渲染。**
> 而它第一次就给出一个 —— `(i)` 冒充 `ⓘ`。

### 验证

```
产品代码未改（内存 2.45 GB，不构建）
完整套件保持 1730 通过 / 0 失败
```

### 下一轮

把 `(i)` 换成真图标（`UiKit.Row` 加 icon 参数 + 3 处调用），需要一次构建。然后补 `Language` 那行。
"""


def main():
    for p, marker, text in ((P1, "R753", BLOCKER), (P3, "R753", BLOCKER), (P2, "第 753 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(HANDOFF, encoding="utf-8").read()
    old = "**不需要**。R710 起的所有轮次都是对磁盘上 `target\\Cybersole.exe` 的静态反编译 + 改复刻件。\n只有上表那四项需要它运行。"
    new = """**不需要**。R710 起的所有轮次都是对磁盘上 `target\\Cybersole.exe` 的静态反编译 + 改复刻件。
只有上表那四项需要它运行。

### R753 起：活窗口已可用，且它能看到四度量看不到的东西

运行中的是 **5.18.35**（`%LOCALAPPDATA%\\Cybersole\\current`），**不是对等目标 5.18.32**。
YG 判定「小版本不动前端」，所以 UI 观测可用，但**每条都要标注观测对象是 5.18.35**。

**已经用它找到第一类新差异**：复刻件用字面文字 `(i)` 冒充 `ⓘ` 图标（3 处，活窗口有 4 行带图标）。
**这类渲染差异四度量结构上看不见。**

下一步待办：`(i)` → 真图标（`UiKit.Row` 加 icon 参数 + 3 处调用），需一次构建。"""
    if old in body:
        io.open(HANDOFF, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  HANDOFF.md updated with the live-window note")
    else:
        print("  HANDOFF.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R753: first live-window evidence -- and two things it caught that static reading could not\n\n"
         "Captured the running build's Settings structure: sixteen sections, the ADVANCED divider, and the\n"
         "General pane's labels with their current values, plus the Home page's '1 / 1' release pager and three\n"
         "empty-state sentences that match R205's constants verbatim. The pager figure also corroborates R747:\n"
         "three cards give (3+2)/3 = 1 page, which is the non-empty case the fix was written for.\n\n"
         "The observation target is 5.18.35, not the parity target 5.18.32. YG states that minor releases are\n"
         "per-site tweaks and do not change the frontend, which is user-statement evidence rather than a tool\n"
         "measurement of 5.18.32, and that is recorded with every observation rather than quietly assumed.\n\n"
         "Two findings came out of it.\n\n"
         "First, my own scan produced a false absence. Searching for the quoted string \"Startup Page\" reported\n"
         "the row missing; it is actually UiKit.Row(\"(i)  Startup Page\", ...). That is the same mistake the\n"
         "evidence rules warn about -- absence of evidence is not absence of behaviour -- except this time the\n"
         "offender was my instrument rather than my judgement, which is worse because an instrument looks\n"
         "objective. Rescanning by substring gives 16 of 16 sections and 15 of 15 labels, with the further caveat\n"
         "that a string existing in source does not prove the row is rendered, so 15/15 is an upper bound.\n\n"
         "Second, the literal characters '(i)' stand in for the info icon: three of 259 UiKit.Row calls use that\n"
         "prefix and the live window has four icon rows. The replica will therefore render '(i)' where the\n"
         "original draws a glyph. No count-based metric could see that, which is the point of having a window.\n\n"
         "No product code changed; memory was too tight to build; suite remains 1730 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
