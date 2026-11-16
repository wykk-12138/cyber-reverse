"""Record R931: StartupPage has no member strings, so the nav is the evidence -- and one name disagrees."""

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
### `StartupPage` 没有成员字符串 —— 所以证据是**导航**，而有一个名字对不上（R931）

**R930 说下一轮用同法核 `StartupPage`。查了，而这次方法**不够用**。**

### 二进制只给了这些

```
Cybersole.Global.Settings,Cybersole.Core.StartupPage!Getter / !Setter / !Property
<StartupPage>k__BackingField
get_StartupPage / set_StartupPage
"Settings.General.StartupPage": "Startup Page"
"Settings.General.StartupPage.Tooltip": "Which page to show on startup."
```

**类型名、绑定、backing field、locale 键 —— **没有一个是成员名**。**

> **所以 R930 那个方法（去镜像里搜那个词）在这里只能证明「`StartupPage` 存在」，
> 不能证明「它的六个值叫什么」。方法有边界，而这是它的边界。**

### 但 locale 给了**导航** —— 而导航正好六项

```
Nav.Home · Nav.Tasks · Nav.Proxies · Nav.Billing · Nav.Accounts · Nav.Settings
```

### 而复刻件是 `Home, Tasks, Accounts, Proxies, Analytics, Settings`

**六项对六项，五个字母都不差。第五个：导航说 `Billing`，枚举说 `Analytics`。**

### 而这一个我没有改

**因为证据只说「导航提供哪六个页面」，不说「启动选项存的是哪个值」。
而 `AnalyticsView` 在资源索引里存在 —— **两个界面都是真的**。**

> **所以可能是：`StartupPage.Billing` 是打开 Analytics 的那个键；
> 也可能是复刻件的 `Analytics` 就是 `Billing` 的改名。**
> **而这两种在字符串层面**完全不可分**。**

**所以我钉住差异，不选一个。（R772 的教训：两种表面并存时，按一种改会被另一种否掉。）**

### 新增 4 个测例

| 测例 | 守什么 |
|---|---|
| `TheEnumHasSixValues` | 六对六 |
| `FiveNamesMatchTheNavigation` | **列名而非计数** —— 把 A 改名成 B 时总数仍会是 5 |
| `TheFifthNameDisagreesAndThatIsRecorded` | **差异本身** |
| `HomeIsTheZeroValue` | 两个来源都同意的那一个 |

### 数字

| 度量 | R930 | **R931** |
|---|---|---|
| 套件 | 1928 | **1932** |
| 类型缺失 | 16 | 16 |

### 教训

> **上一轮的方法这一轮用不了，而**它用了才发现**。
> 如果我先假设「同法可核」，我会把「搜不到成员名」读成「枚举只有一个值」或者「枚举没有值」——
> **那正是 §2.7b 说的：反向结论不能从抽样里得。**
> **而这一轮的出路是换证据源，不是换判据：从**类型名**换到**导航**。**
"""

if "`StartupPage` 没有成员字符串" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R931 appended")

VERDICT = """

---

## 第 931 轮：`StartupPage` 没有成员字符串 —— 换证据源，找到一个差异

### 二进制只给了类型与绑定，没有成员名

```
Settings,Cybersole.Core.StartupPage!Getter / !Setter / !Property
<StartupPage>k__BackingField
"Settings.General.StartupPage": "Startup Page"
```

> **R930 那个方法（搜那个词）在这里只能证明「`StartupPage` 存在」，
> 不能证明「它的六个值叫什么」。方法有边界。**

### 但 locale 给了导航，而导航正好六项

```
Nav.Home · Nav.Tasks · Nav.Proxies · Nav.Billing · Nav.Accounts · Nav.Settings
```

### 而复刻件第五个是 `Analytics`

**六对六，五个字母都不差；导航说 `Billing`，枚举说 `Analytics`。**

### 而这一个我没有改

**证据只说「导航提供哪六个页面」，不说「启动选项存的是哪个值」。
而 `AnalyticsView` 在资源索引里存在 —— **两个界面都是真的**。**

> **可能是 `StartupPage.Billing` 打开 Analytics；也可能是 `Analytics` 就是 `Billing` 的改名。
> 这两种在字符串层面**完全不可分**。**

**所以钉住差异，不选一个**（R772：两种表面并存时，按一种改会被另一种否掉）。

### 四个测例

**六对六 · 五个名字**列名而非计数** · 差异本身 · `Home` 是零值（两个来源都同意的那一个）**

### 数字

| 度量 | R930 | **R931** |
|---|---|---|
| 套件 | 1928 | **1932** |
| 类型缺失 | 16 | 16 |

### 教训

> **上一轮的方法这一轮用不了，而**它用了才发现**。
> 如果我先假设「同法可核」，我会把「搜不到成员名」读成「枚举没有值」—— 那正是 §2.7b。
> **出路是换证据源，不是换判据：从**类型名**换到**导航**。**
"""

BACKLOG_ADD = """

## 判据 (a) — `StartupPage`：成员名不可得，换用导航做证据；一个名字差异被钉住（R931，**+4 用例**）

### 二进制

**只有类型名、绑定描述符、backing field、locale 键 —— 无成员名。**

### 换证据源：导航

```
Nav.Home · Nav.Tasks · Nav.Proxies · Nav.Billing · Nav.Accounts · Nav.Settings
```

### 差异

**复刻件：`Home, Tasks, Accounts, Proxies, **Analytics**, Settings`。**
**第五个：导航 `Billing` vs 枚举 `Analytics`。**

**不改的理由：`AnalyticsView` 也在资源索引里 → 两个界面都真；
`Billing` 打开 Analytics 与 `Analytics` 是 `Billing` 的改名，在字符串层不可分。**

### `StartupPageTests`（4 例）

**六对六 · 五个名字（列名非计数）· 差异本身 · `Home` = 0**

### 数字

**套件 1928 → 1932 · 类型缺失 16**

| 仍 Unknown | |
|---|---|
| 第五个值的真名 | 导航说 Billing，枚举说 Analytics |
| 其余五个的**数值** | 只有名字，没有序号 |
| 其余枚举 | 同法未核 |

**纪律**：方法有边界。R930 的搜词法只能证存在，不能证成员名。出路是换证据源，不是换判据。
"""

BLOCKER = """

---

## 355. `StartupPage`：成员名不可得，换证据源；一个差异被钉住

> R931。**+4 用例，未改产品代码。** 套件 **1932 通过 / 0 失败 / 0 跳过**。

### 一、二进制没有成员名

```
Settings,Cybersole.Core.StartupPage!Getter / !Setter / !Property
<StartupPage>k__BackingField
"Settings.General.StartupPage": "Startup Page"
"Settings.General.StartupPage.Tooltip": "Which page to show on startup."
```

**→ R930 的搜词法只能证「类型存在」，不能证「六个值叫什么」。**

### 二、换证据源：导航正好六项

```
Nav.Home · Nav.Tasks · Nav.Proxies · Nav.Billing · Nav.Accounts · Nav.Settings
```

### 三、差异

**复刻件 `Home, Tasks, Accounts, Proxies, Analytics, Settings` —— 第五个导航说 `Billing`，枚举说 `Analytics`。**

**不改的理由：`AnalyticsView` 也在资源索引里 → 两个界面都真；
「`Billing` 打开 Analytics」与「`Analytics` 是 `Billing` 的改名」在字符串层不可分。**

### 四、`StartupPageTests`（4 例）

**六对六 · 五个名字**列名而非计数** · 差异本身 · `Home` = 0**

### 五、数字

| 度量 | R930 | R931 |
|---|---|---|
| 套件 | 1928 | **1932** |
| 类型缺失 | 16 | 16 |

### 六、验证

```
analysis/ida.py str "StartupPage"   -> 只有类型名/绑定/backing field/locale 键
test --filter StartupPageTests      -> 4 通过
metrics_report.py                   -> 1932 通过 / 0 失败
```

### 七、仍然 Unknown

- **第五个值的真名**：**Unknown** —— 导航说 Billing，枚举说 Analytics。
- **其余五个的数值**：**Unknown** —— 只有名字，没有序号。
- **其余枚举**：**Unknown** —— 同法未核。

### 八、教训

**上一轮的方法这一轮用不了，而**它用了才发现**。**

**如果我先假设「同法可核」，我会把「搜不到成员名」读成「枚举没有值」—— 那正是 §2.7b 说的反向不可用。**

**出路是换证据源，不是换判据：从**类型名**换到**导航**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R931", BLOCKER)
    ensure(RSTATUS, "R931", BLOCKER)
    ensure(RVERDICT, "第 931 轮", VERDICT)
    ensure(BACKLOG, "R931", BACKLOG_ADD)

    note = (
        "\n## R931 补充 — StartupPage：成员名不可得，换用导航做证据（+4 用例，套件 1932）\n\n"
        "二进制只有类型名/绑定描述符/backing field/locale 键，无成员名 → R930 的搜词法只能证存在。\n\n"
        "换证据源：Nav.Home/Tasks/Proxies/Billing/Accounts/Settings —— 正好六项。\n"
        "复刻件 Home,Tasks,Accounts,Proxies,**Analytics**,Settings —— 第五个导航说 Billing，枚举说 Analytics。\n"
        "不改：AnalyticsView 也在资源索引里 → 两个界面都真；两种解释在字符串层不可分。\n\n"
        "StartupPageTests 4 例：六对六 · 五个名字（列名非计数）· 差异本身 · Home=0。\n\n"
        "数字：套件 1928 → 1932 · 类型缺失 16。\n\n"
        "纪律：方法有边界。出路是换证据源，不是换判据。\n\n"
        "下一轮：StartupPage 其余五个值的序号不可得；转其他枚举或 (a) 的剩余项。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R931" not in h:
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
             for p, k in ((RBLOCK, "R931"), (RSTATUS, "R931"), (RVERDICT, "第 931 轮"), (BACKLOG, "R931")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R931: StartupPage carries no member names, so the navigation becomes the evidence\n\n"
         "R930 closed ConcurrencyMode by searching the image for the word and finding zero matches. The same method\n"
         " does not work for StartupPage, and it took using it to find that out: the image carries the type name, the\n"
         " binding descriptors, the backing field and the locale entry with its tooltip, and not one member name. A\n"
         " search can show that a type exists; it cannot show what its values are called, so the method has a boundary\n"
         " and this is it.\n\n"
         "What can be read is the navigation, because the locale names exactly six destinations: Home, Tasks, Proxies,\n"
         " Billing, Accounts and Settings. The replica's enum has six values too and five names match exactly. The fifth\n"
         " is Analytics where the navigation says Billing.\n\n"
         "That disagreement is pinned rather than resolved. The evidence says which six pages the navigation offers, not\n"
         " which value a startup choice stores, and AnalyticsView exists in the resource index, so both screens are real.\n"
         " Billing might be the key that opens Analytics, or Analytics might be the replica's rename of Billing, and the\n"
         " two are indistinguishable at the level of names. Changing it on a guess is how R772 went wrong, where two\n"
         " surfaces coexisted and picking one was refuted by the other.\n\n"
         "Four tests hold the ground: six values against six pages, the five shared names listed rather than counted so\n"
         " that renaming one into another cannot keep the total, the disagreement itself, and Home as the zero value\n"
         " that both sources agree on.\n\n"
         "Figures: suite 1928 to 1932, absent types unchanged at sixteen.\n\n"
         "Unknown: the fifth value's real name; the numeric order of the other five, since only names survive; and the\n"
         " remaining enums, unchecked by either method.\n\n"
         "The lesson is that a method working once does not make it general, and the way to find its edge is to use it\n"
         " until it fails. Had I assumed the search would work again, not finding member names would have read as an enum\n"
         " with no values -- which is section 2.7b's warning about reverse conclusions. The way out was a different\n"
         " source of evidence, not a different criterion.\n\n"
         "Tests added; no product code changed; suite green at 1932."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()