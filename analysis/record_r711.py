"""Record R711: two bound commands implemented, and the three numbers that moved."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 140. 第一条真缺口落地：`CheckoutView.Close` / `ReleaseView.Close` 成了绑定成员

> R711。改 `AnalyticsViews.cs`、`DeadButtonTests.cs`。

### 一、证据先说清

原版字符串池里，这两个名字是**描述符**，不是按钮文案：

```
Cybersole.Ui.Views.Analytics.Modals.CheckoutView,Cybersole.UI.Close!Getter
Cybersole.Ui.Views.Analytics.Modals.ReleaseView,Cybersole.UI.Close!Getter
```

**所以"做"是有据的**：原版把 `Close` 当绑定成员，复刻件只把它当中文案上的按钮标签。

### 二、改了什么

`CheckoutView` 与 `ReleaseView` 各加：

```csharp
public ICommand Close { get; }        // 构造里 Close = new RelayCommand(() => Status("Closed."));
```

按钮从 `UiKit.Button("Close", () => Status("Closed."))` 改成 `Close.Execute(null)`。
**形状与同文件里已有的 `Previous` / `Next` / `OpenTracking` / `ShowGuide` / `ShowSitelist` 一致** ——
它们是 R472/R500 就用这个形状做的，不是我新发明的。

### 三、三个数字

| 度量 | 改前 | 改后 | 为什么 |
|---|---|---|---|
| `c10_split` 的 `undeclared` | 46 | **44** | 两条从"未声明"变成"已声明" |
| 成员形状差异 | 80 | **78** | 这两条原来是 getter-only 的属性写法，与描述符不符；改成 `ICommand` 后形状对上 |
| 完整套件 | 1624 | **1624** | 一条测试需要更新清单，见下 |

### 四、一个守卫红了 —— 是清单过期，不是行为坏了

`DeadButtonTests.EveryKnownEntryStillExists` 断言「清单里每条都还真的存在」。
`Views/Analytics/AnalyticsViews.cs:Close` 那条现在**不再是死按钮**（它有命令了），所以清单过期。

**处置**：从清单移除该条，并写明原因 —— 照 R181/R303/R256 的既有格式。
**没有放宽断言、没有删测试。** 那句注释还写着这个测试的局限：

> 「`EveryKnownEntryStillExists` 分不出**按钮还在**和**理由还成立**」——
> 这条正是「按钮还在、理由不成立了」的情形。

### 五、验证

```
dotnet build                      0 errors
DeadButtonTests                   2/2 通过
完整套件                          1624 通过 / 0 失败 / 0 跳过
c10_split --undeclared            46 -> 44（两个 Close 已消失）
形状差异                          80 -> 78
```

### 六、仍然 Unknown

- `Close` 在原版的**行为**（是关窗口、还是清空、还是别的）：**Unknown** —— 只证明了它是绑定成员。
  复刻件保留原有行为（写状态行），没有假装知道更多。
- 剩下 44 条里还有多少是同类（描述符证明是真成员）：**未逐条核**。
- `CheckoutView.Checkout` / `Properties` 这两条的名字在原版描述符里长什么样：**未查**。
"""

VERDICT = """

---

## 第 711 轮：第一条真缺口落地

### 证据

```
Cybersole.Ui.Views.Analytics.Modals.CheckoutView,Cybersole.UI.Close!Getter
Cybersole.Ui.Views.Analytics.Modals.ReleaseView,Cybersole.UI.Close!Getter
```

原版把 `Close` 当**绑定成员**；复刻件只把它当按钮标签。**所以"做"有据，不是猜。**

### 改了什么

两个类各加 `public ICommand Close { get; }`，按钮改 `Close.Execute(null)`。
形状与同文件已有的 `Previous`/`Next`/`OpenTracking` 一致（R472/R500 就是这个形状）。

### 三个数字

| 度量 | 改前 | 改后 |
|---|---|---|
| `undeclared` | 46 | **44** |
| 形状差异 | 80 | **78** |
| 套件 | 1624 | 1624 |

### 一个守卫红了，是清单过期

`DeadButtonTests` 断言清单每条都还在。`AnalyticsViews.cs:Close` 现在有命令了 → 清单过期。
**移除该条并写明原因**，没放宽断言。

那条测试自己的注释写着它分不出「按钮还在」和「理由还成立」——这次正是后者不成立。

### 一句话

> 加一个属性，三个数字一起动：一个降、一个降、一个不动但清单要改。

> **`undeclared` 降是目的，形状降是意外的收获，清单要改是必须承认的副作用 ——
> 只报第一个就是挑好看的报。**

### 下一轮

继续 44 条，但**先逐条核描述符**（像这轮一样），而不是照名字猜该不该做。
`CheckoutView.Checkout` / `Properties` 的原始描述符先查清楚。
"""


def main():
    for p, marker, text in ((P1, "R711", BLOCKER), (P3, "R711", BLOCKER), (P2, "第 711 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R711: Close becomes a bindable member on both analytics views\n\n"
         "The original's compiled-XAML descriptors carry `...CheckoutView,Cybersole.UI.Close!Getter` and\n"
         "`...ReleaseView,Cybersole.UI.Close!Getter`, so Close is a binding member there, not a caption.\n"
         "Both views now expose `public ICommand Close` and their buttons run it -- the same shape the\n"
         "file already used for Previous/Next/OpenTracking/ShowGuide/ShowSitelist.\n\n"
         "  c10_split undeclared   46 -> 44\n"
         "  shape mismatches       80 -> 78   (the getter-only property did not match the descriptor)\n"
         "  suite                  1624 pass / 0 fail\n\n"
         "DeadButtonTests went red because its known-dead-button list still named AnalyticsViews.cs:Close.\n"
         "The entry was removed with the reason recorded -- a button that runs a command is not what that\n"
         "list is for -- rather than loosening the assertion. Its own comment notes it cannot distinguish\n"
         "'the button still exists' from 'the reason is still true'; this was the latter failing."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
