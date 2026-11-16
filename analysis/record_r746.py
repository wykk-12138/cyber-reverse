"""Record R746: the ApplyCore fix, and a red suite that must not be reported as green."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 175. ApplyCore 的第二处同 bug 已修；**但套件变红了，且我没查清原因**

> R746。改 `ProfileViews.cs` 的 `ApplyCore()` 一处。

### 一、修的是什么（有证据）

R745 修了 `Preview()` 里 `StatusNoHeader` 单独显示的问题（原版是**抛出**这句、由外层 `ParseFailed` 包起来）。
**`ApplyCore()` 里有一模一样的一处**，而且它的注释还写着「same message as Preview」——

```csharp
if (!HeaderHasKnownColumn())
{
    // R653: same message as Preview -- the header names no column this editor knows.
    _status.Text = Text("StatusNoHeader");   // ← R745 已证这句在原版里是被包起来的
    return;
}
```

已改成 `string.Format(Text("StatusParseFailed"), Text("StatusNoHeader"))`。

### 二、顺带查出一批**自造文案**，但都没动

`_status.Text` 的 16 处赋值里，**10 处是目录里没有的文字**：

| 行 | 复刻件 | 目录里 |
|---|---|---|
| 725 | `$"Imported {rows.Count} profile(s) into {group.Name}."` | **有 `Status.Imported` = `Merged {0} rows from {1}`** |
| 669 | `"Nothing to import."` | 无 |
| 720 | `$"{FixErrors} — {errors[0]}"` | 无（连接符是自造的） |
| 806 / 883 / 890 / 1057 / 1118 / 1162 / 1189 / 1200 | `"Copied …"` / `"Group deleted."` / … | 无 |

**只有第 725 行有明确的目录对应物。** 但 `ApplyCore` 的来源是编辑器本身，**不是文件名**，
所以 `Merged {0} rows from {1}` 的 `{1}` 该填什么 —— **Unknown**。**没改。**

其余 9 处**目录里没有对应键**，所以它们要么该消失、要么该换成我还没找到的文案 —— **两种都是 Unknown。没改。**

### 三、套件变红了，如实报

```
完整套件   1707 通过 / 1 失败 / 0 跳过
失败       Cybersole.Tests.HomePageParityTests.ThePagerBelongsToTheReleasesNotThePeriod
```

**上一轮（R745）是 1708 / 0。** 所以必须查。

**已查到的**：

1. **单独跑它 → 6 / 6 通过**
2. **把它和 `ProfileCsv*` 一起跑 → 28 / 28 通过**
3. **重跑全量 → 同样失败**（不是随机）
4. 断言是 `Assert.InRange(view.ReleasePage, 1, view.ReleasePages)` ——
   **若 `ReleasePages == 0`，`InRange(x, 1, 0)` 直接抛**（min > max），与 12ms 的失败时长吻合

**所以最可能的机制**：`ReleasePages` 由**共享数据**算出，前面的某个测试把它弄成 0。
`TestServices.Create()` 的注释说「isolated from the user's real settings」，**但隔离机制在
`AppServices.Create` 里，我没有查到底。**

**没查清的部分**：哪个测试弄脏了它、以及为什么 R745 那一轮没碰到。

### 四、这一轮不能按"完成"记

**判据 (e) 要求全量套件绿。现在不绿。** 所以：

- R746 的代码改动**在证据上是对的**（与 R745 同一处 bug 的第二份）
- **但这一轮不能算通过**，套件红着
- **`docs/METRICS.md` 现在写的是 1 失败** —— 这是事实，不掩盖

### 五、仍然 Unknown

- `ReleasePages` 为 0 的来源：**Unknown** —— 未查到哪个测试弄脏共享状态
- `AppServices.Create` 的隔离机制：**Unknown** —— 未读
- 那 10 处自造文案的原版对应物：**Unknown**（第 725 行除外，它有键但参数缺）
"""

VERDICT = """

---

## 第 746 轮：第二处同 bug 修了，但套件红了

### 修了什么

R745 修了 `Preview()`；**`ApplyCore()` 里有一模一样的一处**，注释还写着「same message as Preview」。已改。

### 顺带查出 10 处自造状态文案，都没动

| 行 | 复刻件 | 目录里 |
|---|---|---|
| 725 | `Imported {N} profile(s) into {group}.` | **有 `Merged {0} rows from {1}`** |
| 669 | `"Nothing to import."` | 无 |
| 720 | `$"{FixErrors} — {errors[0]}"` | 无 |
| 806…1200 | `"Copied …"` / `"Group deleted."` / … | 无 |

**第 725 行有对应键，但 `{1}`（来源）在 `ApplyCore` 里没有 —— Unknown，不改。**
其余 9 处目录里根本没有，**要么该消失要么该换，两种都 Unknown，不改。**

### 套件红了，如实报

```
1707 通过 / 1 失败
失败: HomePageParityTests.ThePagerBelongsToTheReleasesNotThePeriod
上一轮是 1708 / 0
```

**已查**：单独跑通过、与 `ProfileCsv*` 一起跑通过、全量重跑**仍失败**。
断言是 `Assert.InRange(view.ReleasePage, 1, view.ReleasePages)`，
**若 `ReleasePages == 0` 会直接抛**，与 12ms 时长吻合 → **指向共享数据被前面的测试弄脏**。

**没查清**：哪个测试弄脏了它，以及为什么 R745 那轮没碰到。

### 这一轮不能算通过

**判据 (e) 要求全量绿。现在不绿。**

> 代码改动在证据上是对的，**但红着就是红着**。把它写成"完成"，就是拿一条红换一次自我感觉良好。

### 下一轮

**先修红，再做别的。** 第一步：读 `AppServices.Create` 的隔离机制，
找出 `ReleasePages` 依赖什么；第二步：定位哪个测试把它弄成 0。
"""


def main():
    for p, marker, text in ((P1, "R746", BLOCKER), (P3, "R746", BLOCKER), (P2, "第 746 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R746: the second NoHeader call site fixed -- and the suite is red, reported as red\n\n"
         "R745 corrected Preview(); ApplyCore() carried the same mistake, including a comment claiming it\n"
         "matched Preview. Fixed the same way: the sentence is an exception message that the parse-failure\n"
         "handler wraps.\n\n"
         "While there, ten status strings turned out to have no catalogue counterpart -- 'Nothing to import.',\n"
         "'Copied ...', 'Group deleted.', and the import success line, which the catalogue does have as\n"
         "'Merged {0} rows from {1}'. None changed: the import line needs a source argument that ApplyCore does\n"
         "not have, and the other nine have no counterpart at all, so replacing them would be a guess.\n\n"
         "The suite is now 1707 pass / 1 fail. HomePageParityTests.ThePagerBelongsToTheReleasesNotThePeriod\n"
         "fails in the full run and passes alone, and passes alongside the ProfileCsv classes, so the cause is\n"
         "not my change in any direct way. Its assertion is Assert.InRange(ReleasePage, 1, ReleasePages), which\n"
         "throws outright when ReleasePages is zero, and that points at shared test state. I have not found\n"
         "which test dirties it or why the R745 run did not hit it.\n\n"
         "Criterion (e) requires a green suite, so this round does not pass and METRICS records the failure.\n"
         "Reporting it as done would be trading one red for a better feeling.\n\n"
         "Next round starts by fixing the red."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
