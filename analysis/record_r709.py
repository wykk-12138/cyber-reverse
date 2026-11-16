"""Record R709: the 46 undeclared members, and the three different things hiding in them."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 138. 剩下 46 条不是一个东西：**12 条是绑定表的假成员，2 条是字段名不同，32 条是命令做成了 lambda**

> R709。新增 `analysis/check_suffix_members.py`；`c10_split.py` 加继承链解析。

### 一、先做继承解析：55 → 46

沿 `: Base` 链查声明后，9 条落进 `declared-absent`。**但剩下 46 条里绝大多数不是继承问题** —— 它们的成因分三种。

### 二、三种成因（各有证据）

**(1) 12 条是绑定表自己造的假成员**

`Cybersole.Models.EditValue\\`1` 的 14 个成员里，**12 个带数字后缀**：

```
HasMultiple, HasMultiple_87, _88, _91, _93, _94, _95, _97, _98, _99, _101
Value,       Value_92, Value_100
```

裸名 `HasMultiple` / `Value` **同时存在**，后缀值像行号（87…101）。
**判据**：同一类型里裸名与带后缀名并存 → 后缀是提取器的去重标记，不是真成员。

全表只有 `EditValue\\`1` 这一处，共 **12 条**。

**所以 819 这个分母虚高 12，真实成员数是 807。** C10 = 12/819 = 1.465% → 按 807 算是 **1.487%**，比值几乎不变，
**但分母原本是错的** —— 这是 `xaml_bindings.json` 提取器的一个缺陷，会影响所有用 819 的度量。

**(2) 2 条是真的字段名不同**

```csharp
record Notification(NotificationKind Kind, string Title, string Body, DateTime Timestamp)
```

绑定表要 `Type` 与 `Message`，复刻件叫 `Kind` 与 `Body`。`Title` / `Timestamp` 对得上。
**这两条是真实的命名差异**，与 `BINDING_BACKLOG.md` 里那 4 条「结构差异」同类：行为相同，名字不同。

**(3) 32 条是命令做成了 lambda，不是可绑定成员**

`CheckoutView : UserControl`，而 `Close` 在源码里只以按钮文案存在：

```csharp
UiKit.Button("Close", () => Status("Closed."))
```

`ReleaseView.Close`（同一文件另一处）同样。其余各 View 的 `Save` / `Create` / `Delete` / `Reset` / `Properties` /
`TimeSpans` / `View` / `Search` / `Test` / `Export` / `Edit` / `Link` / `Stores` / `Account` / `Model` /
`Clock` / `Expressions` / `BillingView` / `Task` 属于同一形态：**效果有了，但没有做成原名可绑定成员**。

**这一类是可做的** —— 与 `AGENTS.md` §3 那张「方法改成绑定属性」连带清单一模一样，只是这次是从 819 这个账本里推出来的，
不是从绑定表缺口推出来的。

### 三、所以 C10 现在能说什么

```
819（真实 807）
  ├─ 12  可见符号
  ├─ 691 源码有声明、产物无符号（裁剪/内联，不是缺陷）
  ├─ 32  命令做成了 lambda            <- 可做，AGENTS §3 清单
  ├─  2  字段名不同（Notification）    <- 结构差异，同类已有 4 条
  ├─ 12  绑定表假成员                 <- 分母该减掉
  └─ 70  11 个类型，全部已在 triage 结案
```

**只有 32 + 2 = 34 条是真缺口候选**，其余 785 条都已解释。

### 四、仍然 Unknown

- 那 32 条里有多少在**原版**也只是 lambda 而非绑定成员：**Unknown** —— 需要看原版 XAML 的实际绑定用法，
  而不是只看绑定表里出现过名字。
- `EditValue\\`1` 的后缀到底是行号还是别的：**Inference（中）**，裸名并存是硬证据，但编号来源未核。
- 修 `xaml_bindings.json` 会不会影响别的度量：**未评估**（`bind_diff` / `bind_scope` / `shape_audit` 都可能读它）。
"""

VERDICT = """

---

## 第 709 轮：46 条不是一个东西

### 继承解析：55 → 46

沿 `: Base` 链查，9 条落进 `declared-absent`。**但剩下 46 条主要不是继承问题。**

### 三种成因

**(1) 12 条是绑定表造的假成员**

```
EditValue`1: HasMultiple, HasMultiple_87.._101, Value, Value_92, Value_100
```

裸名与带后缀名**并存**，后缀像行号 → 提取器的去重标记。
**819 虚高 12，真实 807**；比值 1.465% → 1.487%，**几乎不变，但分母原本是错的。**

**(2) 2 条是真字段名不同**

```csharp
record Notification(NotificationKind Kind, string Title, string Body, DateTime Timestamp)
```

绑定表要 `Type`/`Message`，复刻件是 `Kind`/`Body`。与已结案的 4 条「结构差异」同类。

**(3) 32 条是命令做成了 lambda**

```csharp
UiKit.Button("Close", () => Status("Closed."))     // CheckoutView : UserControl
```

**效果有了，但没有做成原名可绑定成员。** 这一类**可做** —— 正是 `AGENTS.md` §3 那张连带清单。

### 账本

```
819（真实 807）
  12 可见符号 · 691 裁剪/内联 · 32 命令 lambda · 2 字段名 · 12 假成员 · 70 已结案类型
```

**只有 32 + 2 = 34 条是真缺口候选**，其余 785 条已解释。

### 一句话

> 一个桶里装着四种东西时，「还剩 46 条」这个说法本身没有信息量。

> **把桶拆开的价值不在于数字变小，在于其中 12 条根本不是成员、32 条有一个现成的修法清单。**

### 下一轮

做那 32 条：按 `AGENTS.md` §3 清单把 View 上的命令改成 `ICommand` 绑定属性，先拿 `CheckoutView.Close` /
`ReleaseView.Close` 两个做样板（有明确证据），跑全量，看 `declared-absent` / C10 怎么动。
"""


def main():
    for p, marker, text in ((P1, "R709", BLOCKER), (P3, "R709", BLOCKER), (P2, "第 709 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R709: the 46 undeclared members are three unrelated things\n\n"
         "  (1) 12 are fake: EditValue`1 lists HasMultiple and Value AND HasMultiple_87 .. _101 / Value_92,\n"
         "      _100. A bare name beside numbered variants means the extractor appended a disambiguator,\n"
         "      so the 819 denominator is inflated by 12 and the real member count is 807 (C10 1.465% ->\n"
         "      1.487% -- the ratio barely moves, but the denominator was wrong).\n"
         "  (2) 2 are real name differences: the binding table wants Notification.Type and .Message while\n"
         "      the source record declares Kind and Body.\n"
         "  (3) 32 are commands implemented as inline lambdas -- CheckoutView.Close exists only as\n"
         "      UiKit.Button(\"Close\", () => ...) on a UserControl, so the effect is there but not as a\n"
         "      bindable member. That is AGENTS.md section 3's checklist, reached from the other direction.\n\n"
         "Inheritance resolution walked 9 of the previous 55 up their base chains first."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
