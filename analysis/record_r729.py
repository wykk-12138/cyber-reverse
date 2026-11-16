"""Record R729: the first implementation driven by the stable-witness selection, with 20 probes."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 158. 第一个由「稳定见证」选出来的函数：相对时间格式化器，**复刻件里原本没有实现**

> R729。新增 `replica/src/Cybersole.Core/Reporting/RelativeTime.cs`、
> `replica/tests/Cybersole.Tests/RelativeTimeTests.cs`（20 条）；
> 新增 `analysis/witness_keys.py`、`analysis/witness_candidates.txt`。

### 一、候选池怎么来的（全部基于已有证据）

1. R720：**239 个**函数引用应用 locale 键 → 是应用代码
2. R728：**76,547 个**函数的字符串签名两版一致 → 版本稳定
3. **交集 = 129 个**

**两条判据都不是我拍的**：一条是"引用了只有这个应用才有的字符串"，一条是"官方两个版本之间没动它的字符串引用"。

### 二、用键名认职能，不靠读 200 行伪代码

129 个各自的 locale 键一打印，职能自己浮出来：

```
0x14125fc80  22 keys  KeyBinds.*            → 键位注册
0x1410e2b60   7 keys  TimeAgo.*Format       → 相对时间格式化器
0x1405d9c60   7 keys  TaskGroup.TimeSpan.*  → 时间段选项
0x1406d8d30   6 keys  Proxies.Action.*      → 代理工具栏
```

**这比看 prologue 有用得多。** 选 `0x1410e2b60`：纯函数、输出可断言、键名直接说明它在干什么。

### 三、反编译读出分支结构

```c
v4 = now - a1;                     // TimeSpan ticks
v5 = v4 / 864000000000;            // 整日
if      (v5 > 1)        DaysAgoFormat(v5)
else if (v5 == 1)       OneDayAgo
else if (hours > 1)     HoursAgoFormat(hours)
else if (hours == 1)    OneHourAgo
else if (minutes > 1)   MinutesAgoFormat(minutes)
else if (minutes == 1)  OneMinuteAgo
else                    JustNow
```

**七个字面量偏移（`off_146EF0410/_0518/_0450/_0550/_04D0/_0590/_0498`）与目录里的七条 `TimeAgo.*` 键一一对应** ——
这正是把它认出来的依据；单靠反编译认不出，单靠键名也认不出。

### 四、复刻件里**只有文案，没有实现**

```
Cybersole.Locales.en.json   14 hits（七个键 × 两处）
其它 .cs                    0 hits
```

**七条文案在，没有任何代码产生它们。** 四度量测不到这个（它们数成员，不数行为），
**这是 C7c 应该抓、而四项度量抓不到的那类缺口。**

### 五、实现与探针

`RelativeTime.Describe(TimeSpan, Func<string,string>)`，七分支照抄；
`RelativeTimeTests` **20 条**，期望值来自两处独立证据：反编译的分支结构 + 目录里的实际文案。

**边界是重点**（`>` 与 `==` 是严格的）：
- `59s` → just now，`60s` → 1 min，`119s` → 1 min，`120s` → 2 mins
- `86399s` → 23 hours，`86400s` → 1 day，`172799s` → **1 day**，`172800s` → 2 days
- `45h` → **1 day**（截断），`49h` → 2 days

### 六、我标注的不确定点（不藏）

**Observation**：日那一步是 `ticks / 864000000000`（整日截断）—— 反编译直读。
**Inference（高置信）**：`sub_141D2FEB0` / `sub_141D2FFD0` 是**整小时 / 整分钟**。
理由：与日那步同一个 `v4`、同一个 `>1`/`==1` 模式，且若读成 `TimeSpan.Hours` 的 0–23 分量，
「3 天前」的分钟层会给出荒谬结果 —— 而日分支会先命中，所以那种读法与代码不矛盾但产出错误。
**未排除的备择解释**：确实是 0–23 分量。**要排除它需要看那两个函数的反编译，本轮没做。**

### 七、验证

```
RelativeTimeTests            20 / 20 通过
完整套件                     1659 通过 / 0 失败（1639 + 20）
四项度量                     4 / 0 / 17 / 78 / 0（未变 —— 本轮加的是行为不是成员）
```

### 八、仍然 Unknown

- `sub_141D2FEB0` / `sub_141D2FFD0` 的确切语义：**Unknown**（未反编译，见第六节）。
- 这个格式化器在原版里被谁调用：**Unknown**（未查 xrefs）。
- 129 个候选里其余 128 个：**未处理**（每个都要一轮）。
"""

VERDICT = """

---

## 第 729 轮：第一个由「稳定见证」选出来的实现 —— 相对时间格式化器

### 候选池（两条判据都不是我拍的）

```
R720  239 个函数引用应用 locale 键        → 应用代码
R728  76,547 个函数字符串签名两版一致     → 版本稳定
交集  129 个
```

### 用键名认职能

```
0x1410e2b60   7 keys  TimeAgo.*Format  → 相对时间格式化器
0x14125fc80  22 keys  KeyBinds.*       → 键位注册
```

**比看 prologue 有用得多。**

### 反编译出的结构

```
days > 1 → DaysAgoFormat(days)   days == 1 → OneDayAgo
hours > 1 → HoursAgoFormat       hours == 1 → OneHourAgo
mins  > 1 → MinutesAgoFormat     mins  == 1 → OneMinuteAgo
否则       → JustNow
```

七个字面量偏移与七条 `TimeAgo.*` 键**一一对应** —— 单靠反编译认不出，单靠键名也认不出。

### 复刻件里只有文案、没有实现

**七条键在 JSON 里，`.cs` 里 0 命中。** 四度量测不到这个 —— **它们数成员，不数行为。**

### 实现 + 20 条探针

`RelativeTime.Describe`，七分支照抄。边界是重点（比较是严格的 `>` / `==`）：

```
59s→just now  60s→1 min  119s→1 min  120s→2 mins
86399s→23 hours  86400s→1 day  172799s→1 day  172800s→2 days
45h→1 day（截断）  49h→2 days
```

### 标注的不确定点

**Observation**：日那步是 `ticks / 864000000000`（截断）。
**Inference（高置信）**：小时/分钟是整单位 —— 同一模式、同一输入。
**未排除**：它们是 0–23 分量。**要排除需反编译那两个函数，本轮没做。**

### 一句话

> 这一轮最有价值的不是写了 30 行格式化器，是**证明了那条链能产出可做的活**：
> 应用代码 + 版本稳定 → 键名认职能 → 反编译定分支 → 可断言的行为。

> 而且它抓到的是**四度量结构上看不见的缺口**：**文案在、行为不在。**

### 验证

```
RelativeTimeTests   20 / 20
完整套件            1659 通过 / 0 失败
四项度量            4 / 0 / 17 / 78 / 0（未变，本轮加的是行为不是成员）
```
"""


def main():
    for p, marker, text in ((P1, "R729", BLOCKER), (P3, "R729", BLOCKER), (P2, "第 729 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R729: the first implementation picked by stable-witness selection -- RelativeTime, 20 probes\n\n"
         "Candidate pool from two evidence-based filters, neither of them a judgement call: the 239 functions\n"
         "that reference app locale keys (R720), intersected with the 76,547 whose string signature is\n"
         "identical across 5.18.32 and 5.18.35 (R728). That is 129.\n\n"
         "Printing the keys each candidate loads identifies them without reading pseudocode: 0x1410e2b60\n"
         "carries TimeAgo.DaysAgoFormat, OneDayAgo, HoursAgoFormat, OneHourAgo, MinutesAgoFormat,\n"
         "OneMinuteAgo and JustNow, and its decompilation is a chain of divisions with >1 / ==1 arms that\n"
         "matches those seven strings one for one. Neither the decompilation alone nor the keys alone would\n"
         "identify it.\n\n"
         "The replica had the seven strings and no code producing them: the four metrics count members, not\n"
         "behaviour, so this gap was invisible to them. RelativeTime.Describe implements the seven branches\n"
         "and 20 probes pin the boundaries, where a strict > against == is the only thing separating the\n"
         "singular arm from the plural.\n\n"
         "Labelled rather than hidden: the day step reads as ticks/864000000000 straight from the\n"
         "decompilation; that sub_141D2FEB0 and sub_141D2FFD0 are whole hours and minutes is an inference,\n"
         "and reading them as the 0-23 components is not excluded -- settling it needs those two functions\n"
         "decompiled, which this round did not do.\n\n"
         "Suite 1659 pass / 0 fail; the four metrics are unchanged, because this added behaviour and not\n"
         "members."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
