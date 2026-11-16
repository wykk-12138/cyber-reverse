"""Record R929: MonitorConcurrency settled from the binary, and the replica was wrong."""

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
### `MonitorConcurrency` 定了 —— 而复刻件是**错的**（R929）

**R928 把 `MonitorConcurrency` 钉成「契约有、键被占」的矛盾。这一轮问二进制，答案对复刻件不利。**

### 三组证据，指向同一件事

**① locale 把 `Maximum` / `Ratio` / `Both` / `Max` 挂在 `MonitorConcurrency` 底下：**

```
"Settings.General.MonitorConcurrency": "Monitor Concurrency"
"Settings.General.MonitorConcurrency.Tooltip": "Configures the amount of monitoring tasks when using the \\"Shared Monitor\\" monitor mode."
"Settings.General.MonitorConcurrency.Maximum": "Maximum:"
"Settings.General.MonitorConcurrency.Ratio": "Ratio:"
"Settings.General.MonitorConcurrency.Both": "Both:"
"Settings.General.MonitorConcurrency.Max": "max"
```

**② 绑定描述符同时列了这两个：**

```
Cybersole.Global.Settings,Cybersole.Core.MonitorConcurrency!Getter
Cybersole.Models.Concurrency,Cybersole.Core.Maximum!Getter
```

**③ 而 `<MonitorConcurrency>k__BackingField` 与 `set_Clock,get_MonitorConcurrency@` 说明它是一个**字段支撑的属性**。**

### 所以

> **`MonitorConcurrency` **就是**那个 `Models.Concurrency` 对象本身（有 Maximum / Ratio / Mode），
> 不是它旁边的一个 `int`。**

**而复刻件有两个：`ConcurrencySettings Concurrency` + **凭空造的 `int MonitorConcurrency = 10`**。**

**那个 `int` 是我的发明 —— 而它看起来完全合理，因为「并发数」听起来就是个数字。**

### 合成一个

```csharp
[JsonProperty(\"concurrency\")]
public ConcurrencySettings MonitorConcurrency { get; set; } = new();
```

**一个属性，名字取绑定那边的，键取文件那边的 —— 与 R927 的 `StartupPage` 同一手法。**

### 而改的时候我第二次犯了同一个错

**第一次我用正则把所有 `.Concurrency` 改成 `.MonitorConcurrency` —— **17 处**。
构建报错：`ProviderViews.cs` 里 `c.Concurrency` / `picked.Concurrency` 是 **`CaptchaProvider` 自己的 `Concurrency`**
（描述符表里就有 `CaptchaProviders.CaptchaProvider,Cybersole.Core.Concurrency!Getter`）。**

**回滚，改成按**接收者**限定：`settings.` 与 `s.` 两个，共 **8 处**。**

> **R927 的教训我写过：「改名前要问还有谁在用这个名字」。
> 而这一轮我改的是**后缀**，不是名字 —— 于是同一个词在两个类型上，正则分不出来。
> **「谁是接收者」比「名字长什么样」更能定住一处引用。****

### 而我自己 R928 的两个测例因此红了

**它们编码的是**旧事实**（`MonitorConcurrency` 是 int、`Concurrency` 是对象）。
改成合并后的真相：`MonitorConcurrency` 是对象、序列化名 `concurrency`、**没有 int 兄弟**、且其类型上有 `Maximum` / `Ratio`。**

### 数字

| 度量 | R928 | **R929** |
|---|---|---|
| 套件 | 1915 | **1915** |
| 类型缺失 | 16 | 16 |
| 成员形状 | 94 / 17 | 94 / 17 |
| **设置不匹配成员** | 4 | **3**（`MonitorConcurrency` 有键了） |

**套件与形状三个数都没动 —— 因为这一轮修的是一个**成员的类型与名字**，
而那两个度量数的是**类型存在性**与**成员集合**，不是成员类型。**

> **所以「没动」不说明「没改」：这一轮把一个 `int` 换成了一个对象，而 1915 / 16 / 94 三个数一个都没变。**
"""

if "`MonitorConcurrency` 定了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R929 appended")

VERDICT = """

---

## 第 929 轮：`MonitorConcurrency` 定了 —— 而复刻件是错的

### 三组证据

**① locale 把 `Maximum` / `Ratio` / `Both` / `Max` 挂在 `Settings.General.MonitorConcurrency` 底下**
**② 绑定描述符同列 `Settings.MonitorConcurrency` 与 `Models.Concurrency.Maximum`**
**③ `<MonitorConcurrency>k__BackingField` —— 它是字段支撑的属性**

### 所以

> **`MonitorConcurrency` **就是**那个 `Models.Concurrency` 对象（Maximum/Ratio/Mode），不是旁边一个 `int`。**

**而复刻件有两个：`ConcurrencySettings Concurrency` + **凭空造的 `int MonitorConcurrency = 10`**。**

> **那个 `int` 是我的发明。而它看起来完全合理 —— 因为「并发数」听起来就是个数字。**

### 合成一个（与 R927 的 `StartupPage` 同一手法）

```csharp
[JsonProperty(\"concurrency\")]
public ConcurrencySettings MonitorConcurrency { get; set; } = new();
```

### 而改的时候我第二次犯了同一个错

**第一次正则改所有 `.Concurrency` → 17 处 → 构建报错：
`c.Concurrency` / `picked.Concurrency` 是 **`CaptchaProvider` 自己的**（描述符表里有）。**

**回滚，按**接收者**限定：`settings.` 与 `s.`，共 8 处。**

> **R927 我写过「改名前要问还有谁在用这个名字」。
> 而这一轮我改的是**后缀**，不是名字 —— 同一个词在两个类型上，正则分不出来。
> 「谁是接收者」比「名字长什么样」更能定住一处引用。**

### 而我 R928 的两个测例因此红了

**它们编码的是**旧事实**。改成合并后的真相：是对象、序列化名 `concurrency`、**没有 int 兄弟**、
类型上有 `Maximum`/`Ratio`。**

### 数字

| 度量 | R928 | **R929** |
|---|---|---|
| 套件 | 1915 | 1915 |
| 类型缺失 | 16 | 16 |
| 成员形状 | 94 / 17 | 94 / 17 |
| **设置不匹配成员** | 4 | **3** |

### 教训

> **三个数一个都没动 —— 因为这一轮修的是**成员的类型与名字**，
> 而那两个度量数的是**类型存在性**与**成员集合**。**
> **所以「没动」不说明「没改」：这一轮把一个 `int` 换成了一个对象。**
"""

BACKLOG_ADD = """

## 判据 (a) — `MonitorConcurrency` 从二进制定案：复刻件是错的（R929，**改产品代码 + 改写 2 用例**）

### 三组证据

**locale：`Settings.General.MonitorConcurrency.{,Tooltip,Maximum,MaximumDesc,Ratio,RatioDesc,Both,BothDesc,Max}`**
**描述符：`Settings.MonitorConcurrency!Getter` + `Models.Concurrency.Maximum!Getter`**
**符号：`<MonitorConcurrency>k__BackingField`**

### 定案

**`MonitorConcurrency` 就是 `Models.Concurrency` 对象；复刻件凭空加了一个 `int MonitorConcurrency = 10`。**

```csharp
[JsonProperty(\"concurrency\")] public ConcurrencySettings MonitorConcurrency { get; set; } = new();
```

### 一次过宽的改名（第二次同类错）

**正则改所有 `.Concurrency` → 17 处 → `CaptchaProvider.Concurrency` 被误改 → 回滚。
按**接收者**限定 `settings.` / `s.` → 8 处。**
**→ 「谁是接收者」比「名字长什么样」更能定住引用。**

### 两个自己的测例红了（编码旧事实）

**改写成：是对象 · 序列化名 `concurrency` · 没有 int 兄弟 · 类型上有 `Maximum`/`Ratio`。**

### 数字

**套件 1915（不变）· 类型缺失 16（不变）· 成员形状 94/17（不变）· 设置不匹配 4 → **3****

| 仍 Unknown | |
|---|---|
| `ClockFormat` / `StoreGroups` 该不该持久化 | 不在契约 |
| `Enums.ConcurrencyMode` 的三个值 | 未核 |
| 其余成员的**类型**是否对 | 只核了名字 |

**纪律**：**「没动」不说明「没改」—— 这一轮把一个 int 换成了对象，而三个度量数一个都没变。**
"""

BLOCKER = """

---

## 353. `MonitorConcurrency` 定案：复刻件凭空造了一个 int

> R929。**改产品代码 + 改写 2 用例。** 套件 **1915 通过 / 0 失败 / 0 跳过**。

### 一、三组证据

```
locale   "Settings.General.MonitorConcurrency": "Monitor Concurrency"
         "Settings.General.MonitorConcurrency.Maximum": "Maximum:"
         "Settings.General.MonitorConcurrency.Ratio": "Ratio:"
         "Settings.General.MonitorConcurrency.Both": "Both:"
描述符   Cybersole.Global.Settings,Cybersole.Core.MonitorConcurrency!Getter
         Cybersole.Models.Concurrency,Cybersole.Core.Maximum!Getter
符号     <MonitorConcurrency>k__BackingField
```

### 二、定案

**`MonitorConcurrency` **就是** `Models.Concurrency` 那个对象（Maximum/Ratio/Mode），不是旁边的 `int`。**

**复刻件有 `ConcurrencySettings Concurrency` + 凭空造的 `int MonitorConcurrency = 10`。
那个 int 是我的发明 —— 而它看起来合理，因为「并发数」听起来就是个数字。**

### 三、合成一个（同 R927 的 `StartupPage` 手法）

```csharp
[JsonProperty(\"concurrency\")]
public ConcurrencySettings MonitorConcurrency { get; set; } = new();
```

### 四、而改名时我第二次犯同类错

**正则改所有 `.Concurrency` → 17 处 → `ProviderViews.cs` 的 `c.Concurrency` / `picked.Concurrency`
是 `CaptchaProvider` 自己的（描述符表里有）→ 构建报错 → 回滚。
按**接收者**限定（`settings.` / `s.`）→ 8 处 → 通过。**

**→ 「谁是接收者」比「名字长什么样」更能定住一处引用。**

### 五、我 R928 的两个测例红了

**它们编码旧事实。改写为：是对象 · 序列化名 `concurrency` · 没有 int 兄弟 · 类型上有 `Maximum`/`Ratio`。**

### 六、数字

| 度量 | R928 | R929 |
|---|---|---|
| 套件 | 1915 | **1915** |
| 类型缺失 | 16 | 16 |
| 成员形状 | 94 / 17 | 94 / 17 |
| **设置不匹配成员** | 4 | **3** |

**三个度量数一个没动 —— 因为这一轮修的是成员的类型与名字，而它们数的是类型存在性与成员集合。**

### 七、验证

```
analysis/ida.py str "oncurrency"   -> locale 的 Maximum/Ratio/Both/Max 全在 MonitorConcurrency 下
test --filter SettingsUnmatchedMembersTests -> 4 通过
metrics_report.py                  -> 1915 通过 / 0 失败
```

### 八、仍然 Unknown

- **`ClockFormat` / `StoreGroups` 该不该持久化**：**Unknown** —— 不在契约。
- **`Enums.ConcurrencyMode` 的三个值**：**Unknown** —— 未核。
- **其余成员的**类型**是否对**：**Unknown** —— 只核了名字。

### 九、教训

**「没动」不说明「没改」。这一轮把一个 `int` 换成了一个对象，而 1915 / 16 / 94 三个数一个都没变。**

**所以度量不动的时候，要先问它数的是什么，再判断这一轮有没有做成事。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R929", BLOCKER)
    ensure(RSTATUS, "R929", BLOCKER)
    ensure(RVERDICT, "第 929 轮", VERDICT)
    ensure(BACKLOG, "R929", BACKLOG_ADD)

    note = (
        "\n## R929 补充 — MonitorConcurrency 定案：复刻件凭空造了一个 int（改产品代码 + 改写 2 用例，套件 1915）\n\n"
        "三组证据：locale 把 Maximum/Ratio/Both/Max 挂在 Settings.General.MonitorConcurrency 下 · 描述符同列 "
        "Settings.MonitorConcurrency 与 Models.Concurrency.Maximum · <MonitorConcurrency>k__BackingField。\n"
        "→ MonitorConcurrency 就是 Models.Concurrency 对象，不是旁边的 int。\n\n"
        "合成一个：[JsonProperty(\"concurrency\")] public ConcurrencySettings MonitorConcurrency。\n\n"
        "改名时第二次犯同类错：正则改所有 .Concurrency → 17 处 → CaptchaProvider 自己的 Concurrency 被误改 → 回滚 → "
        "按接收者限定 settings./s. → 8 处。→ 「谁是接收者」比「名字长什么样」更能定住引用。\n\n"
        "R928 的两个测例编码旧事实 → 改写成合并后的真相。\n\n"
        "数字：套件 1915 / 类型缺失 16 / 成员形状 94-17 三个都没动 · 设置不匹配 4 → 3。\n\n"
        "纪律：「没动」不说明「没改」—— 把一个 int 换成对象，三个度量数一个没变。\n\n"
        "下一轮：Enums.ConcurrencyMode 的三个值；或其余成员的**类型**是否对（只核了名字）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R929" not in h:
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
             for p, k in ((RBLOCK, "R929"), (RSTATUS, "R929"), (RVERDICT, "第 929 轮"), (BACKLOG, "R929")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R929: MonitorConcurrency settled from the binary, and the replica had invented an int\n\n"
         "R928 pinned MonitorConcurrency as an open contradiction: the contract lists it, the file's concurrency key is\n"
         " already an object. Asking the binary settled it against the replica. The locale puts Maximum, Ratio, Both and\n"
         " Max underneath Settings.General.MonitorConcurrency, the binding descriptor names Settings.MonitorConcurrency\n"
         " and Models.Concurrency.Maximum in the same table, and the symbol table carries\n"
         " <MonitorConcurrency>k__BackingField. So MonitorConcurrency IS the Models.Concurrency object rather than a\n"
         " scalar beside it.\n\n"
         "The replica had both: a ConcurrencySettings Concurrency and a MonitorConcurrency int defaulting to ten. The int\n"
         " was invented, and it looked plausible for exactly the reason that made it dangerous -- a concurrency count\n"
         " sounds like a number. They are now one property, holding the binding's name and the file's key, which is the\n"
         " same treatment StartupPage needed in R927.\n\n"
         "The rename went too wide the first time and by the same fault as the round before. Replacing every .Concurrency\n"
         " hit seventeen references and broke the build, because CaptchaProvider carries its own Concurrency and the\n"
         " descriptor table says so. Constraining by receiver -- settings and s -- took it to eight. Naming the receiver\n"
         " pins a reference better than the shape of the name does, since a suffix cannot tell two types apart.\n\n"
         "Two of my own R928 tests then failed, correctly, because they encoded the old facts. They now assert the\n"
         " merged truth: the property is the object, its file name is concurrency, no scalar sits beside it, and the type\n"
         " it holds Maximum and Ratio.\n\n"
         "Figures: suite 1915, absent types sixteen and shape ninety-four with seventeen core all unchanged, and the\n"
         " unmatched settings members go from four to three. Three measures did not move because this round changed a\n"
         " member's type and name, while those measures count type presence and member sets.\n\n"
         "Unknown: whether ClockFormat and StoreGroups should be persisted, neither being in the contract; the three\n"
         " values of ConcurrencyMode, unchecked; and whether the remaining members have the right types, since only\n"
         " their names were compared.\n\n"
         "The lesson is that a measure holding still does not mean nothing changed. This round replaced an int with an\n"
         " object and all three figures stayed put, so asking what a measure counts has to come before reading no change\n"
         " as no work.\n\n"
         "Product code and two tests changed; suite green at 1915."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()