"""Record R752: the count-shaped instrument, its own defect, and the targets it produced."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
HANDOFF = r"D:\projects\cyber-reverse\docs\HANDOFF.md"

BLOCKER = """

---

## 181. 计数型文案的仪表：7 条复刻件从不引用；**而仪表自己的分组有缺陷**

> R752。新增 `analysis/count_shaped_copy.py`。本轮未改产品代码、未加测试（套件数不变）。

### 一、为什么要造这个仪表

R750 发现 ranking 只数带占位符的文案，于是 0/1/n 三段里 0 和 1 两档整类不可见；
R751 把判别式钉在**参数种类**上（计数 → 三段；名字或比较值 → 两段）。

**推论**：ranking 的盲区**不均匀**，它恰好落在计数型文案上。所以换一个方向问：

> **目录里哪些「文本以 `{0} ` 开头」的键，复刻件根本没有消费？**

`analysis/count_shaped_copy.py`（按 §1.2 注明为什么现有工具不覆盖：这是关于 locale 目录与复刻件源码的问题，
不是关于二进制的问题；`witness_ranking.py` 问的是另一个方向的映射，目录是纯 JSON）。

### 二、结果：41 条计数型文案，**7 条复刻件从不引用**

```
Accounts.AccountsFormat         '{0} Accounts'          （1 档 AccountsOne，无 0 档）
Notifications.HeaderFormatOne   '{0} Notification'
ProfileCsv.SubtitleFormat       '{0} · {1} profiles'
Settings.AccountCountFormat     '{0} Accounts'          （1 档 AccountCountOne）
…（共 7 条，见脚本输出）
```

**其中 `ProfileCsv.SubtitleFormat` 是第二条 R744 那类"自造文案"的对照物**：
目录里有 `{0} · {1} profiles`，而复刻件的 CSV 编辑器副标题是自造的。

### 三、而仪表**自己有缺陷**，必须写下来

它按**命名空间**给兄弟分组：`Accounts.AccountsFormat` 的"0 档"被判成 `Accounts.Subtitle`、
"1 档"判成 `AccountsOne`。**那只是同命名空间，不是同一组文案。**

**所以输出里那 18 组"三段"多数未经证实。** 只有 R750/R751 亲手读过的那几组是 Observation。

**这个缺陷的成因值得记**：兄弟关系在**目录里没有显式表达** —— 它只体现在函数的三个分支里。
**命名空间是唯一能在静态侧拿到的近似，而它明显不够。**

**要真的判组，得读函数**（这正是 AGENTS.md §1 那条「要判断是接线还是逻辑，读伪代码」的同一课）。

### 四、一条独立印证

`SmartActionsCreator.BehaviourFormat`（`{0} if`）被标为 **NO CONSUMER** ——
**这与 R751 独立得出的"未实现，因为另一支的槽没解"完全一致。**
两个不同方法给同一结论，这类交叉印证值得记。

### 五、仍然 Unknown

- 那 18 组"三段"里哪些是真的：**Unknown** —— 只有读过的几组是 Observation，其余是命名空间近似。
- 7 条未消费的计数型文案各自的原版产生点：**Unknown** —— 需按 `csv_key_functions.py` 的办法逐个扫。
- `ProfileCsv.SubtitleFormat` 是否就是 CSV 编辑器副标题的原版文案：**Inference（中）**，未核。
"""

VERDICT = """

---

## 第 752 轮：计数型文案仪表 —— 7 条未消费，而仪表自己有缺陷

### 为什么要造

ranking 只数带占位符的 → 0/1/n 里 0 和 1 两档不可见 → **盲区不均匀，恰好落在计数型文案上**。
所以反过来问：**哪些「`{0} ` 开头」的键，复刻件根本没消费？**

### 结果：41 条里 **7 条从不引用**

```
Accounts.AccountsFormat         '{0} Accounts'
Notifications.HeaderFormatOne   '{0} Notification'
ProfileCsv.SubtitleFormat       '{0} · {1} profiles'
Settings.AccountCountFormat     '{0} Accounts'
```

`ProfileCsv.SubtitleFormat` 是**第二条 R744 那类自造文案的对照物**。

### 而仪表自己有缺陷

它按**命名空间**给兄弟分组：`Accounts.Subtitle` 被当成 `Accounts.AccountsFormat` 的 0 档。
**那只是同命名空间，不是同一组文案。所以 18 组"三段"多数未经证实。**

> **成因值得记：兄弟关系在目录里没有显式表达 —— 它只体现在函数的三个分支里。
> 命名空间是静态侧唯一能拿到的近似，而它明显不够。**

**要真的判组，得读函数。**

### 一条独立印证

`BehaviourFormat` 被标 NO CONSUMER —— **与 R751 独立得出的"未实现"一致**。

### 一句话

> 我造了个仪表来找漏掉的文案，**它确实找到了 7 条 —— 同时它自己的分组方法不成立**。
> 如果我只报那 7 条不报这个缺陷，下一个人会拿 18 组数字去做决定。

### 验证

```
产品代码未改、未加测试（套件仍 1730 通过 / 0 失败）
四项度量不变
```
"""

HANDOFF_SECTION = """

---

## R752 交班快照（2026-11-16，重启前）

### 状态

```
完整套件        1730 通过 / 0 失败 / 0 跳过
四项度量        见 docs/METRICS.md（唯一来源，不在此硬编码）
已审候选        29 / 129（analysis/witness_ranking.tsv）
git             工作树干净
```

### 方法上的三条新结论（本轮最有价值的部分）

1. **ranking 有两处口径偏差**：R743 数「函数引用了什么」而非「目录里有什么」；
   R750 只数**带占位符**的，于是 0/1/n 三段里 0 和 1 两档整类不可见。
2. **判别式**：文案条数取决于**参数种类** —— 计数 → 三段（`No X` / `1 X` / `{0} X`）；
   名字或被比较的值 → 两段。**有因果，不是巧合。**
3. **兄弟关系在 catalog 里没有显式表达**，只体现在函数分支里。
   **按命名空间猜兄弟不成立**（`analysis/count_shaped_copy.py` 自己的缺陷，已写进 BLOCKERS §181）。

### 下一轮该做什么（按优先级）

1. **7 条未消费的计数型文案**：用 `analysis/csv_key_functions.py` 的办法，
   把每个键的引用函数扫出来再读。这是**有明确清单**的活。
2. **`analysis/count_shaped_copy.py` 的分组需要按函数修正**，否则它给出的 18 组是噪声。
3. 剩余 100 个候选按 `witness_ranking.tsv` 往下。

### 需要运行时才能解的（攒着，等凭据）

| 项 | 缺什么 |
|---|---|
| profiles 删确认的三层闸门 | 两个 delegate 的目标（R738/R739） |
| `ProfileCsv.Status.Imported` 的 `{1}` | Hex-Rays 对被折叠实参的还原；运行期可绕 |
| `EditValue\\`1` 那 12 个成员的类型 | AOT 元数据表（.NET 10 不再携带 `DEHYDRATED_DATA`） |
| Pin/Unpin 标志的方向 | 一个已知状态的样本 |

**这四项都需要原版跑起来 + 登录凭据。静态侧已到边界。**

### Cybersole 需不需要开着

**不需要**。R710 起的所有轮次都是对磁盘上 `target\\Cybersole.exe` 的静态反编译 + 改复刻件。
只有上表那四项需要它运行。
"""


def main():
    for p, marker, text in ((P1, "R752", BLOCKER), (P3, "R752", BLOCKER), (P2, "第 752 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(HANDOFF, encoding="utf-8").read()
    if "R752 交班快照" in body:
        print("  HANDOFF.md already has the R752 section")
    else:
        io.open(HANDOFF, "a", encoding="utf-8").write(HANDOFF_SECTION)
        print("  HANDOFF.md += R752 交班快照")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R752: an instrument for count-shaped copy, its seven unconsumed keys, and its own defect\n\n"
         "The ranking can only see sentences that carry a placeholder, and R750/R751 established that the\n"
         "blind spot is not even: it falls exactly on count-shaped labels, whose zero and one cases have no\n"
         "placeholder at all. So this asks the opposite question -- which catalogue sentences beginning '{0} '\n"
         "does the replica never reference.\n\n"
         "Seven of forty-one. One of them, ProfileCsv.SubtitleFormat, is the catalogue counterpart to another\n"
         "string the replica invents, the same shape as R744's finding.\n\n"
         "The instrument's own grouping is unsound and that is recorded rather than left for a reader to\n"
         "discover: it groups siblings by namespace, so Accounts.Subtitle counts as the zero case for\n"
         "Accounts.AccountsFormat. Those are neighbours in a dotted name and nothing more. Eighteen 'triples'\n"
         "are therefore mostly unverified, and only the groups read by hand in R750/R751 are observations.\n"
         "Sibling relationships are not expressed in the catalogue at all -- they live in the functions' three\n"
         "branches -- so naming is the only static approximation available and it is plainly too coarse.\n\n"
         "One cross-check worth keeping: the instrument marks BehaviourFormat as unconsumed, independently\n"
         "agreeing with R751, which declined to implement it because its other arm's slot is unresolved.\n\n"
         "No product code changed and no tests added; suite remains 1730 pass / 0 fail. HANDOFF.md gains a\n"
         "restart snapshot listing what needs the original running -- four items, all needing credentials."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
