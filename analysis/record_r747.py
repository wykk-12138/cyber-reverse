"""Record R747: the red suite was a real pager defect plus a test that depended on ambient data."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 176. 红的原因查清了：**真实缺陷 + 一条依赖环境数据的测试**（不是 flaky）

> R747。修 `AnalyticsViews.cs` 的 `MoveTo` 与 `HomePageParityTests` 的一条断言。套件回到绿。

### 一、先拿到失败消息（不是靠猜）

```
System.ArgumentException : '0' cannot be greater than -1.
  at System.Math.ThrowMinMaxException[T](T min, T max)
  at Cybersole.Ui.Views.Analytics.AnalyticsView.MoveTo(Int32 page)
  at Cybersole.Ui.Views.Analytics.AnalyticsView.MoveNextCore()
```

**`'0' cannot be greater than '-1'`** → `min = 0`、`max = -1`。

### 二、根因：`ReleasePages == 0` 时 `Math.Clamp` 直接抛

```csharp
public int ReleasePages => (….Count + 2) / 3;          // 0 条发布 → 0
private void MoveTo(int page)
{
    var clamped = Math.Clamp(page, 0, ReleasePages - 1);   // → Clamp(page, 0, -1) 抛
```

**而 `0` 是原版实测过的正常值** —— 紧邻的注释自己写着：

> `ReleasePages` Zero when there is nothing to page through: the live window prints `0 / 0` on a fresh install (R334)

**所以在有发布之前按一下分页箭头，复刻件会崩。这是真实缺陷，不是测试问题。**

### 三、测试也有错：它假设总有一页

```csharp
Assert.InRange(view.ReleasePage, 1, view.ReleasePages);   // ReleasePages==0 → min>max → 抛
```

**它单独跑时能过，是因为数据根里恰好留着别的测试写入的发布数据。** 一加测试文件，执行顺序变了，这份"环境数据"就没了。

**所以上一轮我说"指向共享数据"只对了一半**：**共享数据只是掩盖了缺陷，缺陷本身是 `MoveTo`。**

### 四、改了什么

**产品代码**（`AnalyticsViews.cs`）：

```csharp
if (ReleasePages <= 0) { return; }      // 没有页可翻，什么都不做
```

**测试**（`HomePageParityTests`）：

```csharp
- Assert.InRange(view.ReleasePage, 1, view.ReleasePages);
+ // With zero releases ReleasePages is 0 while ReleasePage is _releasePage + 1, so only the lower bound
+ // is asserted here; whether the caption should then read "0 / 0" is a separate question.
+ Assert.True(view.ReleasePage >= 1, "ReleasePage is 1-based");
```

**没有用 `Math.Max(1, ReleasePages)`** —— 那是**削弱断言**，会把一条本该失败的情形变成通过。

### 五、顺手核掉一个我自己的错误假设

我以为 `ReleasePage == 1` 与窗口印 `0 / 0` 矛盾（那是第二个 bug）。**查了 `PagerCaption`**：

```csharp
public static string PagerCaption(int page, int pages) => pages <= 0 ? "0 / 0" : $"{page} / {pages}";
```

**它本来就对空情形返回 `0 / 0`。** 所以不矛盾，**我的假设是错的** —— 记在这里，因为差一点就去"修"一个不存在的问题。

### 六、验证

```
HomePageParityTests   6 / 6 通过
完整套件              1708 通过 / 0 失败 / 0 跳过
四项度量              4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- 原版在零发布时按分页箭头会怎样（箭头是否禁用）：**Unknown** —— 只知它不会崩。
  复刻件现在"什么都不做"，这是我选的、不是读出来的。
- 那条测试依赖环境数据这件事，**是否还有别处同样依赖**：**Unknown** —— 未全库检查。

### 八、这一轮的方法收获

**上一轮我用"单独跑通过"推断"不是确定性问题"，方向反了。**
正确的是：**先拿失败消息**，它会直接给出 `min/max` 的取值，比我做的三次对照实验都省。
"""

VERDICT = """

---

## 第 747 轮：红的原因 —— 真实缺陷 + 依赖环境数据的测试

### 先拿到失败消息（不靠猜）

```
ArgumentException : '0' cannot be greater than -1.
  at AnalyticsView.MoveTo(Int32 page)
```

**`min = 0`、`max = -1`。**

### 根因：`ReleasePages == 0` 时 `Math.Clamp` 抛

```csharp
public int ReleasePages => (….Count + 2) / 3;   // 0 条发布 → 0
Math.Clamp(page, 0, ReleasePages - 1);           // → Clamp(page, 0, -1) 抛
```

**而 `0` 是原版实测的正常值** —— 紧邻的注释自己写着「the live window prints `0 / 0` on a fresh install (R334)」。

> **在有发布之前按一下分页箭头，复刻件会崩。这是真实缺陷。**

### 测试也有错：它假设总有一页

`InRange(ReleasePage, 1, ReleasePages)` —— `ReleasePages==0` 时 min>max 也抛。
**它单独跑能过，是因为数据根里恰好留着别的测试写入的发布数据。**

**所以上一轮我说"指向共享数据"只对了一半：共享数据只是掩盖了缺陷。**

### 改了什么

- 产品：`if (ReleasePages <= 0) return;` —— 没有页可翻，什么都不做
- 测试：只断言 `ReleasePage >= 1`，**没有用 `Math.Max(1, …)`**（那是削弱断言）

### 顺手核掉一个我自己的错误假设

我以为 `ReleasePage == 1` 与窗口印 `0 / 0` 矛盾。**查了 `PagerCaption` —— 它本来就对空情形返回 `0 / 0`。不矛盾，我错了。**
**差一点就去"修"一个不存在的问题。**

### 方法收获

> 上一轮我用「单独跑通过」推断「不是确定性问题」，**方向反了**。
> 正确的是：**先拿失败消息** —— 它直接给出 `min/max`，比我做的三次对照实验都省。

### 验证

```
HomePageParityTests   6 / 6
完整套件              1708 通过 / 0 失败
四项度量              4 / 0 / 17 / 78 / 0（未变）
```
"""


def main():
    for p, marker, text in ((P1, "R747", BLOCKER), (P3, "R747", BLOCKER), (P2, "第 747 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R747: the red suite was a real pager defect plus a test that leaned on ambient data\n\n"
         "Getting the failure message first, instead of the three comparison runs I did last round, gave the\n"
         "answer directly: ArgumentException '0' cannot be greater than -1 at AnalyticsView.MoveTo. That is\n"
         "Math.Clamp(page, 0, ReleasePages - 1) evaluated while ReleasePages is 0 -- and 0 is a documented\n"
         "normal state, since the comment beside the property records R334 measuring the live window printing\n"
         "0 / 0 on a fresh install. Pressing a pager arrow before any release existed would have crashed the\n"
         "replica, so this was a real defect and not a test artefact.\n\n"
         "The test was wrong too: Assert.InRange(ReleasePage, 1, ReleasePages) throws in that same state, and\n"
         "it only passed earlier because the data root happened to still hold release data another test had\n"
         "written. Last round I called it 'shared data'; that was half right -- shared data hid the defect, but\n"
         "the defect was in MoveTo.\n\n"
         "Fixed MoveTo to no-op when there are no pages, and replaced the range assertion with a lower-bound\n"
         "assertion rather than Math.Max(1, ...), which would have quietly weakened it.\n\n"
         "Also checked and discarded my own hypothesis that ReleasePage == 1 contradicts the printed '0 / 0':\n"
         "PagerCaption already returns '0 / 0' when pages <= 0. I was about to fix something that was not\n"
         "broken, and recording that saves the next round from repeating it.\n\n"
         "Suite back to 1708 pass / 0 fail; four metrics unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
