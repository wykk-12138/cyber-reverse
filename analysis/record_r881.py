"""Record R881: the ceiling test, and my own bad measurement that it caught."""

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
### 给那个句式加天花板 —— 而它当场抓到我算错（R881）

**R880 说：真正该修的不是数字，是「N 个模块」这个句式。**

**做法不是削守卫，是加一条**只允许降、不允许升**的天花板测试：**

```
TheModuleCountPhraseDoesNotSpread
  ceiling = 16
  「N 个模块」(N>=20) 的处数 <= 16，超出就红，消息写着「改这句话，不要抬天花板」
```

**为什么不削守卫：`TheModuleCountInVerdictMatchesTheCatalogue` 抓的是「数字不对」，
而它分不清「目录有这么多个」（断言）与「某轮处理了这么多个」（事实）。
削它会一起削掉真断言；加天花板只针对**增长**。**

**为什么不改历史：那 16 句今天全都对。改对的东西会把证据改成叙述。**

### 而它第一次跑就红了 —— 因为我的天花板是错的

**我先用一段 python 数出 13，把 13 写成 ceiling。测试报 16。**

**查下来：**我的 python 脚本数错了**（围栏剥离里用了 `chr(10)` 与反引号模式，结果不可靠），
**同一个文件、同一个正则，C# 数出 16。**

**我又用一份写进文件的干净脚本复核：raw 16 · 剥围栏 16 —— 都是 16。**
**所以 13 是我的测量错误，16 是真值。**

**这件事本身就是这条测试的价值：一个从**手工计数**得来的天花板，是一个用我没核对过的工具断言出来的数字。**

### 三句话

| 我要的 | 拿到的 |
|---|---|
| 一个不增长的句式 | 一条 ceiling 测试 |
| ceiling 的初值 | **被自己的测试纠正：13 → 16** |
| 一个记录 | 一条「别用手工计数当基准」的实例 |
"""

if "给那个句式加天花板" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R881 appended")

BLOCKER = """

---

## 305. 天花板测试：那个句式只许降不许升 —— 而它当场纠正了我

> R881。**改测试，不改产品代码。** 套件 **1780 通过 / 0 失败 / 0 跳过**（原 1779 + 1）。

### 一、R880 说要改句式，这轮改的是机制

**新增 `DocsConsistencyTests.TheModuleCountPhraseDoesNotSpread`：**

```
ceiling = 16
散文里「<数字> 个模块」(数字>=20) 的处数 <= 16
超出即红，消息：改这句话（引 docs/METRICS.md），不要抬天花板
```

**三条理由：**

| 选择 | 为什么 |
|---|---|
| **不削 `TheModuleCountInVerdictMatchesTheCatalogue`** | 它抓「数字不对」；它分不清「目录有这么多个」（断言）与「某轮处理了这么多个」（事实）。削它会连真断言一起削掉 |
| **不改那 16 句历史** | 它们今天全对。改对的东西，是把证据改成叙述 |
| **只针对**增长** | 句式随改稿变少是好的；变多就是习惯在长 |

### 二、它第一次跑就红 —— 而错的是我的天花板

**我先用一段 python 数出 13，把 13 写成 ceiling。测试报 16。**

**复核：同一文件、同一正则，写进文件的干净脚本给出 raw 16 / 剥围栏 16。
所以 13 是我的测量错误，16 是真值。**

**而那条 python 的毛病很具体：我在 here-string 里用 `chr(10)` 配反引号模式做围栏剥离，
反引号在 PowerShell here-string 里逃不掉 —— 这条坑我前面已经踩过并写过「写成文件跑」。**

**所以这一轮抓到的不是「数字写错」，是**我又用了一个没核对的工具去定基准**。**

### 三、这条测试真正的用处

**它不只防「下次又写 N 个模块」，它防的是「拿手工计数当基准」。**

**一个 ceiling 如果来自一个我没复核过的脚本，那它和 R876 那个「相邻就是归属」是同一类错误 ——
只是这次错在数字而不是名字。**

### 四、验证

```
snapshot 20261116-222059
D:\\tools\\dotnet8\\dotnet.exe test --filter DocsConsistencyTests  -> 8 通过 / 0 失败
新测试首跑                                                        -> 红：spread from 13 to 16
复核脚本（写进文件）                                              -> raw 16 / stripped 16
改 ceiling 13 -> 16                                               -> 8 通过
python tools\\metrics_report.py                                    -> 1780 通过 / 0 失败 / 0 跳过
```

### 五、仍然 Unknown

- **天花板该不该随改写下降而收紧**：**Unknown** ——
  **现在它允许 16，如果哪轮把几处改成不带数字，16 就该调低。而「该调低」这件事需要一个动作，
  现在没人会做。**
- **那 16 句里有几句其实该改**：**Unknown** ——
  **它们是对的，但有的（如表格里「VERDICT | 63 个模块 | 事实」）是**在把数字当锚点**，
  那种句式最该改。本轮没动。**
- **这个测试会不会太松**：**可能会** —— 16 是个不小的余量。

### 六、教训

**我这一轮原本的意图是「加一条机制，防止自己再犯」。
而它做的第一件事是抓住我：我给它定的基准是错的。**

**这比它拦住未来的错更有用 —— 因为它证明这条机制不是「我规定的规则」，
而是「能反驳我的检查」。**

**R878 说「能用算术回答的就不该靠推断」。这一轮的版本是：
能用**可复核的工具**回答的，就不该靠手工计数。**
"""

VERDICT = """

---

## 第 881 轮：天花板测试 —— 它第一次跑就纠正了我

### 加的是什么

**`DocsConsistencyTests.TheModuleCountPhraseDoesNotSpread`：散文里「<数字> 个模块」的处数只许降不许升（ceiling 16）。**

| 选择 | 为什么 |
|---|---|
| **不削既有守卫** | 它抓「数字不对」，但分不清「目录有那么多个」与「某轮处理了那么多个」；削它会连真断言一起削 |
| **不改那 16 句历史** | 它们今天全对。改对的东西，是把证据改成叙述 |
| **只针对增长** | 句式随改稿变少是好的；变多就是习惯在长 |

### 而它第一次跑就红了 —— 错的是我的基准

**我先数出 13 写进 ceiling，测试报 16。复核（写进文件的干净脚本）：raw 16 / 剥围栏 16。**

**所以 13 是我的测量错误。**毛病具体：here-string 里用 `chr(10)` 配反引号做围栏剥离 —— 这个坑我踩过并写过「写成文件跑」。**

### 它真正的用处

> **不只防「下次又写这个句式」，它防的是「拿手工计数当基准」。**
> **一个 ceiling 如果来自我没复核过的脚本，那它和 R876 那个「相邻就是归属」是同一类错误 —— 只是错在数字而不是名字。**

### 验证

```
DocsConsistencyTests 8 通过 · 新测试首跑红（13→16）· 复核后改 13→16 · 全量 1780 通过 / 0 失败
```

### 仍然 Unknown

**天花板该不该随改写下降收紧**（该调低，但没人会做）·
**那 16 句里有几句其实该改**（表格里把数字当锚点那几句最该改，本轮没动）·
**16 这个余量是否太松**（可能会）

### 教训

> **我原本的意图是「加一条机制防止自己再犯」。而它做的第一件事是抓住我：我给它定的基准是错的。**
> **这比拦住未来的错更有用 —— 它证明这条机制不是「我规定的规则」，而是「能反驳我的检查」。**
> **R878 说「能用算术回答的不该靠推断」；这一轮的版本是：能用**可复核的工具**回答的，就不该靠手工计数。**
"""

BACKLOG_ADD = """

## 方法 — 句式天花板测试（R881）

**`DocsConsistencyTests.TheModuleCountPhraseDoesNotSpread`**：散文里「<数字> 个模块」(>=20) 的处数 **<= 16**，只许降不许升。

| 选择 | 为什么 |
|---|---|
| 不削 `TheModuleCountInVerdictMatchesTheCatalogue` | 它分不清断言与事实陈述，削它会连真断言一起削 |
| 不改那 16 句历史 | 它们今天全对；改对的东西 = 把证据改成叙事 |
| 只针对增长 | 变少是改稿，变多是习惯 |

### 它第一次跑就纠正了我

**我先数出 13 当 ceiling，测试报 16 → 复核（写进文件的脚本）raw 16 / stripped 16 → 13 是测量错误。**
**毛病：here-string 里 `chr(10)` + 反引号做围栏剥离。**

> **它防的不只是「再写这个句式」，是「拿手工计数当基准」。**

### 验证

`DocsConsistencyTests` 8 通过 · 全量 **1780 通过 / 0 失败**（原 1779 + 1）

| 仍 Unknown | |
|---|---|
| 天花板该不该随改写收紧 | 该调低，但没动作会做 |
| 那 16 句里有几句该改 | 表格里把数字当锚点的最该改 |
| 16 余量是否太松 | 可能会 |

**纪律**：**能用可复核工具回答的，就不该靠手工计数。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R881", BLOCKER)
    ensure(RSTATUS, "R881", BLOCKER)
    ensure(RVERDICT, "第 881 轮", VERDICT)
    ensure(BACKLOG, "R881", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R881" not in h:
        h += ("\n## R881 补充 — 句式天花板测试\n\n"
              "**新增 `DocsConsistencyTests.TheModuleCountPhraseDoesNotSpread`**：散文里「<数字> 个模块」(>=20) 处数 **<= 16**，只许降不许升。"
              "**不削既有守卫、不改历史、只针对增长。**\n"
              "**它第一次跑就纠正我**：我先数出 13 当 ceiling，测试报 16 → 复核 16 才对（毛病：here-string 里 `chr(10)` + 反引号）。"
              "**所以它防的不只是句式，是「拿手工计数当基准」。**\n"
              "**套件 1780 通过 / 0 失败（原 1779 + 1）。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    # The new verdict text must not add a "N 个模块" sentence, or the ceiling test fails next run.
    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling -- fix the verdict wording before committing")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R881"), (RSTATUS, "R881"), (RVERDICT, "第 881 轮"), (BACKLOG, "R881")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R881: a ceiling on the phrase that has broken four times, and the ceiling corrected itself first\n\n"
         "TheModuleCountInVerdictMatchesTheCatalogue has gone red at R457, R464, R813 and R880, and each repair changed\n"
         " the number, which holds only until the next module lands. R880 concluded the phrase itself is the trap and\n"
         " left the mechanism for this round.\n\n"
         "The new test does not weaken that guard, because the guard catches a real problem and cannot distinguish a\n"
         " claim about the catalogue's size from a sentence reporting that some round handled that many modules.\n"
         " Instead it fixes a ceiling: the count may fall as sentences are reworded and may not rise, so the habit is\n"
         " caught where it forms rather than four rounds later. History is left alone; those sentences are correct\n"
         " today, and editing correct sentences to satisfy a linter turns evidence into narrative.\n\n"
         "The test corrected me before it corrected anything else. I counted thirteen manually and wrote thirteen as the\n"
         " ceiling; the test reported sixteen. Checking with a script written to a file rather than inlined gave sixteen\n"
         " both raw and with fenced blocks stripped, so thirteen was my measurement error, caused by using chr(10) with\n"
         " a backtick pattern inside a PowerShell here-string -- a trap this session already recorded and I walked into\n"
         " again.\n\n"
         "That makes the test more useful than intended. A ceiling derived from a hand count is a number asserted from a\n"
         " tool I had not checked, which is the same species of error as R876 treating adjacency as ownership, except\n"
         " in digits rather than names. What it guards is not just the phrase but the habit of taking an unverified\n"
         " count as a baseline.\n\n"
         "Unknown: whether the ceiling should tighten as sentences are reworded away, since it permits sixteen and\n"
         " nothing will bring it down without an explicit act; which of the sixteen sentences actually deserve editing,\n"
         " where the ones that use the number as an anchor in a table are the worst offenders and were not touched this\n"
         " round; and whether sixteen leaves too much slack.\n\n"
         "R878 said that what arithmetic can settle should not be settled by inference. This round's version is that\n"
         " what a checkable tool can settle should not be settled by a hand count.\n\n"
         "Suite green at 1780, the previous 1779 plus one."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
