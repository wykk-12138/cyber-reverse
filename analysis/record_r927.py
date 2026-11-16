"""Record R927: Settings 34/34, and the two names one member legitimately has."""

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
### `Settings` 补到 34/34 —— 而一个成员有两个名字（R927）

**R926 留下 6 个 RENAMED，覆盖率是下界。逐个核，5 个全覆盖，只有 `Settings` **33/34**。**

### 缺的那一个：`StartupPage`

**复刻件里是：**

```csharp
private StartupPage _startup = StartupPage.Home;
public StartupPage Startup { get => _startup; set => ... }
```

**属性叫 `Startup`，而绑定里是 `StartupPage`。**

**而 `StartupPage` 同时是个**枚举** —— 所以原版是「属性名与类型同名」的形态，C# 允许。**

### 改名之后，第二个东西红了

**改完跑全量：`LiveSchemaPinsTests.TheSettingsFileFieldsAllExist` 报
「44 live keys, missing: **startup**」。**

**而那个测试的名字清单是从**原版写出的备份**读的（R390 注明了这一点）—— 所以它是**文件键**，不是属性名。**

> **也就是说：这个成员**有两个名字**，而两个都是事实：
> 绑定叫它 `StartupPage`，而 settings 文件里叫 `startup`。**
> **改属性名满足了前一个，同时破坏了后一个。**

### 所以两个都钉住

```csharp
[Newtonsoft.Json.JsonProperty(\"startup\")]
public StartupPage StartupPage { get => _startup; set => ... }
```

**而那个钉也要改：它的清单是文件键，所以比对对象应该是**每个属性序列化成的名字**，
而不是属性名本身。**

**改完 34/34 与 44 键同时成立。**

### 数字

| 度量 | R926 | **R927** |
|---|---|---|
| 套件 | 1911 | **1911**（同数，见下） |
| **`Settings` 覆盖** | 33/34（97%） | **34/34** |

**套件数不变 —— 因为这一轮先加了一次失败（改名破坏了 schema 钉）再修回来。
**净数不动，而中间红过一次，那一次红的记录在下面的教训里。****

### 三件这一轮才算清的事

**① 覆盖率是下界，所以「RENAMED」不等于「齐」** —— 6 个里 1 个差一个成员。
**② 绑定名与文件键可以不同** —— 而「类型/成员改名允许」这条规则**只覆盖绑定**，不覆盖持久化格式。
**③ 一个按名字比的钉，比的是哪一边的名字，决定了它守的是什么。** 那条钉守的是文件，所以要比文件键。

### 教训

> **我改了一个属性名，而它同时是两个契约的一部分 —— 一个是 C# 里的绑定，一个是磁盘上的 JSON。
> 改名前我只想到了第一个。**
> **而把它告诉我的方式，是一条从**原版备份**读出来的键清单。**
"""

if "`Settings` 补到 34/34" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R927 appended")

VERDICT = """

---

## 第 927 轮：`Settings` 34/34 —— 而一个成员有两个名字

### 缺的那一个

**复刻件里属性叫 `Startup`，绑定里是 `StartupPage`。而 `StartupPage` 同时是个**枚举** ——
原版是「属性名与类型同名」，C# 允许。**

### 改名之后第二个东西红了

**`LiveSchemaPinsTests` 报「44 live keys, missing: **startup**」。
那个清单是从**原版写出的备份**读的，所以它是**文件键**，不是属性名。**

> **这个成员**有两个名字**，两个都是事实：绑定叫 `StartupPage`，settings 文件里叫 `startup`。
> 改属性名满足了前者，破坏了后者。**

### 两个都钉住

```csharp
[JsonProperty(\"startup\")]
public StartupPage StartupPage { ... }
```

**而那个钉也改了：清单是文件键，所以要比**每个属性序列化成的名字**，不是属性名。**

### 数字

| 度量 | R926 | **R927** |
|---|---|---|
| 套件 | 1911 | 1911（同数） |
| **`Settings` 覆盖** | 33/34 | **34/34** |

**套件数不变，因为先加了一次失败再修回来 —— 净数不动，而中间红过一次。**

### 三件这一轮才算清的事

**① 覆盖率是下界 → 「RENAMED」不等于「齐」**（6 个里 1 个差一个成员）
**② 绑定名与文件键可以不同 → 「改名允许」只覆盖绑定，不覆盖持久化格式**
**③ 一个按名字比的钉，比的是哪一边的名字，决定它守的是什么** —— 那条钉守文件，所以要比文件键

### 教训

> **我改了一个属性名，而它同时是两个契约的一部分 —— 一个是 C# 里的绑定，一个是磁盘上的 JSON。
> 改名前我只想到了第一个。**
> **而把它告诉我的方式，是一条从**原版备份**读出来的键清单。**
"""

BACKLOG_ADD = """

## 判据 (a) — `Settings` 34/34；绑定名与文件键分离（R927，**改产品代码 + 改一个钉**）

### 6 个 RENAMED 逐个核

**5 个全覆盖 · `Settings` 33/34 —— 缺 `StartupPage`（复刻件属性叫 `Startup`）。**

### 而改名引出第二个契约

**`LiveSchemaPinsTests` 报缺 `startup` —— 那个清单来自**原版备份**，是**文件键**。**

**→ 一个成员有两个名字：绑定 `StartupPage` + 文件 `startup`，两个都是事实。**

```csharp
[JsonProperty(\"startup\")] public StartupPage StartupPage { … }
```

**→ 那个钉改成比「每个属性序列化成的名字」，不是属性名。**

### 三条结论

1. **覆盖率是下界 → RENAMED ≠ 齐**
2. **「改名允许」只覆盖绑定，不覆盖持久化格式**
3. **按名字比的钉要比对的那一边的名字；那条钉守文件，就要比文件键**

### 数字

**套件 1911（同数 —— 先加一次失败再修回）· `Settings` 33/34 → **34/34** · 类型缺失 16（不变）**

| 仍 Unknown | |
|---|---|
| 其余 33 个成员的文件键是否都与属性名一致 | 未逐个核 |
| 7 个 UNKNOWN 判定 | 非区分 |
| 剩 5 个 RENAMED 的成员类型是否对 | 只核了名字 |

**纪律**：**一个属性名可以是两个契约的一部分。改名前要问：还有谁在用这个名字？**
"""

BLOCKER = """

---

## 351. `Settings` 34/34：一个成员有两个名字，而改一个只满足一边

> R927。**改产品代码 + 改一个钉。** 套件 **1911 通过 / 0 失败 / 0 跳过**。

### 一、6 个 RENAMED 逐个核

**5 个全覆盖；`Settings` **33/34** —— 缺 `StartupPage`（复刻件属性叫 `Startup`，而 `StartupPage` 同时是个枚举，
原版是「属性名与类型同名」）。**

### 二、改名之后第二个契约红了

**`LiveSchemaPinsTests.TheSettingsFileFieldsAllExist`：44 live keys, missing: **startup**。**

**那个清单是从**原版写出的备份**读的 → 它是**文件键**，不是属性名。**

**→ 这个成员有两个名字，两个都是事实：绑定 `StartupPage` · 文件 `startup`。**

### 三、两个都钉住

```csharp
[JsonProperty(\"startup\")]
public StartupPage StartupPage { get => _startup; set => ...; }
```

**而钉改成比「每个属性序列化成的名字」—— 它守的是文件，就该比文件键。**

### 四、数字

| 度量 | R926 | R927 |
|---|---|---|
| 套件 | 1911 | **1911** |
| **`Settings` 覆盖** | 33/34 | **34/34** |
| 类型缺失 | 16 | 16 |

**套件数不变 —— 先加了一次失败再修回来；净数不动而中间红过一次。**

### 五、验证

```
analysis/type_presence_triage.py   -> Settings: declares all 34 member(s)
test --filter LiveSchemaPinsTests  -> 10 通过（44 live keys, 0 missing）
metrics_report.py                  -> 1911 通过 / 0 失败
```

### 六、仍然 Unknown

- **其余 33 个成员的文件键是否都与属性名一致**：**Unknown** —— 未逐个核。
- **7 个 UNKNOWN 判定**：**Unknown** —— 非区分匹配。
- **剩 5 个 RENAMED 的成员**：**只核了名字，类型未核。**

### 七、教训

**一个属性名可以是**两个契约**的一部分：C# 里的绑定，和磁盘上的 JSON。改名前我只想到了第一个。**

**而把它告诉我的方式，是一条从原版备份读出来的键清单 —— 不是我的检查，是一个既有钉。**

**所以「改名允许」这条规则的范围要说清：它覆盖绑定，**不覆盖持久化格式**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R927", BLOCKER)
    ensure(RSTATUS, "R927", BLOCKER)
    ensure(RVERDICT, "第 927 轮", VERDICT)
    ensure(BACKLOG, "R927", BACKLOG_ADD)

    note = (
        "\n## R927 补充 — Settings 34/34；绑定名与文件键分离（改产品代码 + 改一个钉，套件 1911）\n\n"
        "6 个 RENAMED 逐个核：5 个全覆盖，Settings 33/34 —— 缺 StartupPage（复刻件属性叫 Startup，而 StartupPage 是枚举）。\n\n"
        "改名后 LiveSchemaPinsTests 报缺 startup —— 那个清单来自原版备份，是文件键。\n"
        "→ 一个成员有两个名字：绑定 StartupPage + 文件 startup，两个都是事实。\n"
        "→ 加 [JsonProperty(\"startup\")] 到 StartupPage 属性；钉改成比「每个属性序列化成的名字」。\n\n"
        "三条结论：① 覆盖率是下界 → RENAMED ≠ 齐 · ②「改名允许」只覆盖绑定不覆盖持久化格式 · "
        "③ 按名字比的钉要比对的那一边的名字。\n\n"
        "数字：套件 1911（同数，先加一次失败再修回）· Settings 33/34 → 34/34 · 类型缺失 16。\n\n"
        "纪律：一个属性名可以是两个契约的一部分。改名前要问 —— 还有谁在用这个名字？\n\n"
        "下一轮：其余 33 个成员的属性名与文件键是否一致（未逐个核）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R927" not in h:
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
             for p, k in ((RBLOCK, "R927"), (RSTATUS, "R927"), (RVERDICT, "第 927 轮"), (BACKLOG, "R927")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R927: Settings reaches thirty-four of thirty-four, and one member turns out to have two names\n\n"
         "R926 left six RENAMED types carrying a lower-bound coverage figure. Checking them one at a time, five are\n"
         " complete and Settings was at thirty-three of thirty-four: the property is named Startup while the binding calls\n"
         " it StartupPage, and StartupPage is also an enum, so the original has a member sharing its type's name.\n\n"
         "Renaming the property closed that and broke something else. LiveSchemaPinsTests reported forty-four live keys\n"
         " with startup missing -- and that list is read from a backup the original wrote, so it holds file keys rather\n"
         " than property names. One member therefore has two names and both are facts: the binding says StartupPage and\n"
         " the settings file says startup. Renaming satisfied the first and broke the second.\n\n"
         "So the property keeps the binding's name and carries a JsonProperty attribute holding the file's, and the pin\n"
         " now compares the name each property serialises to rather than the property name, because what that pin guards\n"
         " is the file.\n\n"
         "Three things are clearer for it. Coverage is a lower bound, so a RENAMED verdict does not mean complete -- one\n"
         " of six was a member short. A binding name and a file key may legitimately differ, which means the rule\n"
         " permitting renames covers bindings and not persistence. And a name-comparing pin guards whichever side's name\n"
         " it compares, so a file pin has to compare file names.\n\n"
         "Figures: suite carries at 1911, Settings from thirty-three to thirty-four, absent types unchanged at sixteen.\n"
         "The suite figure did not move because this round added a failure and then removed it.\n\n"
         "Unknown: whether the other thirty-three members' property names match their file keys, which was not checked;\n"
         " the seven unknown verdicts, where candidates cannot be distinguished; and whether the remaining five renamed\n"
         " types have members of the right type, since only their names were compared.\n\n"
         "The lesson is that one property name can belong to two contracts at once -- the binding in C# and the JSON on\n"
         " disk -- and I thought of only the first when renaming. What told me was an existing pin reading a list from the\n"
         " original's own backup.\n\n"
         "Product code and a pin changed; suite green at 1911."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()