"""Record R930: ConcurrencyMode's third value was invented, and Both's rule is implemented."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### `ConcurrencyMode` 的第三个值是**发明的**，而 `Both` 有一条成文的规则（R930）

**R929 留下「`ConcurrencyMode` 的三个值未核」。核了。**

### 二进制里只有类型名一个字符串

```
ConcurrencyMode    (0x1432312cd)   ← 就这一个
```

**枚举**成员名没单独出现**。所以值只能从 locale 推 —— 而 locale 给了三项：**

```
"Settings.General.MonitorConcurrency.Maximum": "Maximum:"
"Settings.General.MonitorConcurrency.Ratio": "Ratio:"
"Settings.General.MonitorConcurrency.Both": "Both:"
"Settings.General.MonitorConcurrency.Max": "max"
```

**而 `BothDesc` 把规则写下来了：**

> **「Allows you to set both a maximum and ratio. The amount of monitoring tasks will be equal to **whichever is greater**.」**

### 而复刻件是 `Unlimited / Maximum / Ratio`

**第三项写成 `Unlimited` —— 而 `Concurrency.Unlimited` 在镜像里 **0 匹配**。
5 个 `Unlimited` 全是无关的（TTS 引擎的 `UnlimitedStorage`、一个叫 Games Unlimited 的店）。**

> **所以 `Unlimited` 也是我的发明 —— 第二个。而它比 R929 那个 `int` 更隐蔽：
> 「不限并发」是一个听起来很自然的能力，而三项里空出一项时，填一个“无限制”比填一个“两个都算”容易想到。**

### 改成 `Maximum / Ratio / Both`，并把那条规则实现出来

```csharp
public enum ConcurrencyMode { Maximum = 0, Ratio = 1, Both = 2 }
```

**`Models/ConcurrencyLimit.cs`：**

| 模式 | 规则 | 依据 |
|---|---|---|
| `Maximum` | `min(max, tasks)`；`max <= 0` 时等于全部 | 名字 |
| `Ratio` | `floor(tasks × ratio)` | 名字 |
| **`Both`** | **`max(maximum, floor(tasks × ratio))`，再 `min(tasks, …)`** | **locale 的 `BothDesc` 原文「whichever is greater」** |

### 三个刻意的决定

**① `max <= 0` 当作「没有上限」，不当「零个任务」。**
**一个什么都没设的 settings 文件应该表现为不限，而不是一个都不跑。**

**② `Ratio` 向下取整，且标注为 Inference。**
**没有任何恢复到的材料说小数怎么处理；向下取整因为**多启动监控池是要防的失败** —— 这个模式存在的目的是限制并发，不是达到目标。**

**③ 一个函数，三个调用方。**
**任务引擎的门、设置预览、测试都要这个数，而这么小的规则正是那种会被各写一遍、各差一点的东西。**

### 数字

| 度量 | R929 | **R930** |
|---|---|---|
| 套件 | 1915 | **1928** |
| 类型缺失 | 16 | 16 |
| 成员形状 | 94 / 17 | 94 / 17 |

### 教训

> **两轮之内我发明了两样东西：一个 `int MonitorConcurrency`（R929）和一个 `Unlimited` 枚举值（R930）。
> 两个都被「听起来合理」保护着。**
> **而两次的判据是同一个动作：**去镜像里搜那个词**。一次搜出 `<MonitorConcurrency>k__BackingField`，
> 一次搜出 0 匹配。**
> **发明不需要证据，而**搜索只要一分钟**。**
"""

if "`ConcurrencyMode` 的第三个值是**发明的**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R930 appended")

VERDICT = """

---

## 第 930 轮：`ConcurrencyMode` 的第三个值是发明的，而 `Both` 有成文规则

### 二进制只有类型名一个字符串

**`ConcurrencyMode` (0x1432312cd) —— 枚举**成员名没单独出现**。值只能从 locale 推。**

```
"Settings.General.MonitorConcurrency.Maximum": "Maximum:"
"Settings.General.MonitorConcurrency.Ratio": "Ratio:"
"Settings.General.MonitorConcurrency.Both": "Both:"
"Settings.General.MonitorConcurrency.BothDesc": "…will be equal to whichever is greater."
```

### 而复刻件是 `Unlimited / Maximum / Ratio`

**`Concurrency.Unlimited` 在镜像里 **0 匹配**；5 个 `Unlimited` 全是无关的（TTS 的 `UnlimitedStorage`、一个店名）。**

> **`Unlimited` 是我的发明 —— 第二个（第一个是 R929 那个 `int`）。
> 而它更隐蔽：「不限并发」是个自然的能力，三项里空出一项时，填「无限制」比填「两个都算」容易想到。**

### 改成 `Maximum / Ratio / Both` 并实现规则

**`Models/ConcurrencyLimit.cs`：`Maximum` = `min(max, tasks)` · `Ratio` = `floor(tasks × ratio)` ·
**`Both` = `max(maximum, floor(tasks × ratio))` 再 `min(tasks, …)` —— 依据是 locale 的原文「whichever is greater」****

### 三个决定

**① `max <= 0` = 没有上限，不是零个任务**（空 settings 应表现不限，而不是一个不跑）
**② `Ratio` 向下取整，标 Inference** —— 没有材料说小数怎么处理；向下因为**多启动监控池是要防的失败**
**③ 一个函数三个调用方** —— 这么小的规则会被各写一遍、各差一点

### 数字

| 度量 | R929 | **R930** |
|---|---|---|
| 套件 | 1915 | **1928** |
| 类型缺失 | 16 | 16 |
| 成员形状 | 94 / 17 | 94 / 17 |

### 教训

> **两轮之内发明了两样东西，两个都被「听起来合理」保护着。
> 而两次的判据是同一个动作：**去镜像里搜那个词** —— 一次搜出 backing field，一次搜出 0 匹配。**
> **发明不需要证据，而搜索只要一分钟。**
"""

BACKLOG_ADD = """

## 判据 (a) — `ConcurrencyMode`：`Unlimited` 是发明的，改为 `Both` 并实现其规则（R930，**改产品代码 +13 用例**）

### 证据

**二进制仅有类型名 `ConcurrencyMode` 一个字符串；locale 三项 `Maximum` / `Ratio` / `Both`，
且 `BothDesc` 原文给规则：「equal to whichever is greater」。**
**`Concurrency.Unlimited` → **0 匹配**（5 个 `Unlimited` 全无关）。**

### 改动

```csharp
public enum ConcurrencyMode { Maximum = 0, Ratio = 1, Both = 2 }
```

**`Models/ConcurrencyLimit.cs`：`Resolve(mode, tasks, max, ratio)`**
**`Maximum` = `min(max,tasks)` · `Ratio` = `floor(tasks×ratio)` · `Both` = `min(tasks, max(maximum, ratio))`**

**`Profiles.cs` 默认值 `Unlimited` → `Both`。**

### 三个决定

**`max<=0` = 无上限（非零任务）· `Ratio` 向下取整（标 Inference）· 一个函数三个调用方**

### 数字

**套件 1915 → 1928 · 类型缺失 16 · 成员形状 94/17**

| 仍 Unknown | |
|---|---|
| `StartupPage` 的 6 个值 | 同法未核 |
| 其余枚举 | 同法未核 |
| `Ratio` 的取整方向 | Inference |

**纪律**：两轮发明两样东西，都靠「听起来合理」。判据是同一个动作 —— 去镜像里搜那个词。
"""

BLOCKER = """

---

## 354. `ConcurrencyMode`：`Unlimited` 是发明的，改为 `Both` 并实现规则

> R930。**改产品代码 +13 用例。** 套件 **1928 通过 / 0 失败 / 0 跳过**。

### 一、二进制只有类型名

**`ConcurrencyMode` (0x1432312cd) —— 枚举成员名没单独出现。值只能从 locale 推：**

```
"Settings.General.MonitorConcurrency.Maximum": "Maximum:"
"Settings.General.MonitorConcurrency.Ratio": "Ratio:"
"Settings.General.MonitorConcurrency.Both": "Both:"
"Settings.General.MonitorConcurrency.BothDesc": "…will be equal to whichever is greater."
```

### 二、而复刻件是 `Unlimited / Maximum / Ratio`

**`Concurrency.Unlimited` → **0 匹配**。5 个 `Unlimited` 全是无关的（TTS 的 `UnlimitedStorage`、一个叫 Games Unlimited 的店）。**

**→ `Unlimited` 是我的发明 —— 两轮内第二个（第一个是 R929 的 `int MonitorConcurrency`）。**

### 三、改动

```csharp
public enum ConcurrencyMode { Maximum = 0, Ratio = 1, Both = 2 }
```

**`Models/ConcurrencyLimit.cs`：**

| 模式 | 规则 |
|---|---|
| `Maximum` | `min(max, tasks)`；`max<=0` → 全部 |
| `Ratio` | `floor(tasks × ratio)` |
| **`Both`** | **`min(tasks, max(maximum, floor(tasks×ratio)))` —— locale 原文「whichever is greater」** |

**`Profiles.cs` 默认 `Unlimited` → `Both`。**

### 四、三个决定

1. **`max<=0` 当「没有上限」，不当「零个任务」** —— 空 settings 应表现不限。
2. **`Ratio` 向下取整，标 Inference** —— 多启动监控池是要防的失败。
3. **一个函数三个调用方** —— 这么小的规则会被各写一遍、各差一点。

### 五、数字

| 度量 | R929 | R930 |
|---|---|---|
| 套件 | 1915 | **1928** |
| 类型缺失 | 16 | 16 |
| 成员形状 | 94 / 17 | 94 / 17 |

### 六、验证

```
analysis/ida.py str "Concurrency.Unlimited"  -> 0 匹配
analysis/ida.py str "ConcurrencyMode"        -> 仅类型名一个
test --filter ConcurrencyModeTests           -> 13 通过
metrics_report.py                            -> 1928 通过 / 0 失败
```

### 七、仍然 Unknown

- **`StartupPage` 的 6 个值**：**Unknown** —— 同法未核。
- **其余枚举**：**Unknown** —— 同法未核。
- **`Ratio` 的取整方向**：**Inference**。

### 八、教训

**两轮之内发明了两样东西：`int MonitorConcurrency`（R929）与 `Unlimited`（R930）。两个都被「听起来合理」保护着。**

**而两次的判据是同一个动作：**去镜像里搜那个词**。一次搜出 `<MonitorConcurrency>k__BackingField`，一次搜出 0 匹配。**

**发明不需要证据，而搜索只要一分钟。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R930", BLOCKER)
    ensure(RSTATUS, "R930", BLOCKER)
    ensure(RVERDICT, "第 930 轮", VERDICT)
    ensure(BACKLOG, "R930", BACKLOG_ADD)

    note = (
        "\n## R930 补充 — ConcurrencyMode：Unlimited 是发明的，改为 Both 并实现规则（+13 用例，套件 1928）\n\n"
        "二进制仅有类型名 ConcurrencyMode 一个字符串；locale 三项 Maximum/Ratio/Both，BothDesc 原文"
        "「equal to whichever is greater」。Concurrency.Unlimited → 0 匹配。\n\n"
        "→ Unlimited 是发明的（两轮内第二个，第一个是 R929 的 int MonitorConcurrency）。\n\n"
        "改成 Maximum=0/Ratio=1/Both=2；新增 Models/ConcurrencyLimit.cs：Maximum=min(max,tasks) · "
        "Ratio=floor(tasks×ratio) · Both=min(tasks, max(maximum, ratio)) —— 依据 locale 原文。\n"
        "Profiles.cs 默认 Unlimited → Both。\n\n"
        "三个决定：max<=0 当无上限（非零任务）· Ratio 向下取整标 Inference · 一个函数三个调用方。\n\n"
        "数字：套件 1915 → 1928 · 类型缺失 16 · 成员形状 94/17。\n\n"
        "纪律：发明不需要证据，而搜索只要一分钟。\n\n"
        "下一轮：StartupPage 的 6 个值同法核。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R930" not in h:
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h + note)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R930"), (RSTATUS, "R930"), (RVERDICT, "第 930 轮"), (BACKLOG, "R930")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R930: ConcurrencyMode's third value was invented, and Both has a written rule\n\n"
         "R929 left the enum's values unchecked. The image carries only the type name, so the values have to come from\n"
         " the locale, and it names three: Maximum, Ratio and Both. The replica had Unlimited, Maximum and Ratio -- and a\n"
         " search for a concurrency-scoped Unlimited returns nothing, with the five Unlimited strings in the image being\n"
         " a TTS storage size and a shop called Games Unlimited. So Unlimited was invented, the second invention in two\n"
         " rounds after R929's int MonitorConcurrency, and the more insidious of the two: an unlimited mode sounds like a\n"
         " natural capability, and when one of three slots is empty, no-cap is easier to reach for than both-apply.\n\n"
         "Both does have a written rule, though, and it is the only specification of this arithmetic recovered anywhere:\n"
         " the amount of monitoring tasks will be equal to whichever is greater of the maximum and the ratio. That is\n"
         " implemented once in ConcurrencyLimit, with Maximum and Ratio following from their names, so the task engine's\n"
         " gate, the settings screen and the tests cannot disagree about so small a rule.\n\n"
         "Three choices are deliberate. A maximum of zero or less means no cap rather than zero tasks, since an empty\n"
         " settings file should behave as unlimited and not as start-nothing. Ratio rounds down, labelled as inference,\n"
         " because no recovered material says which way a fractional count goes and over-starting a monitor pool is the\n"
         " failure this mode exists to prevent. And the rule lives in one function rather than three callers.\n\n"
         "Figures: suite 1915 to 1928, absent types sixteen and shape ninety-four with seventeen core unchanged.\n\n"
         "Unknown: StartupPage's six values, unchecked by the same method; the remaining enums, likewise; and which way\n"
         " Ratio rounds, which is inference.\n\n"
         "The lesson is that invention needs no evidence while searching takes a minute. Two rounds, two plausible\n"
         " inventions, and both times the decisive move was the same one -- search the image for the word.\n\n"
         "Product code changed; suite green at 1928."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()