"""Record R915: coverage measured against code rather than prose, and the ten names that were only prose."""

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
### 去掉注释再数：覆盖 **23.4%**，而 10 个名字只活在注释里（R915）

**R914 报了 372（24.0%），并说那个 +1 是我自己的注释。这一轮把整件事量清。**

### 三个数

| 判据 | 名字 | 占比 |
|---|---|---|
| **在代码里** | **362** | **23.4%** |
| **只在注释里** | **10** | **0.6%** |
| **两者都没有** | **1175** | **76.0%** |

**而「只在注释里」那 10 个，全部是我在文档注释里点过名、却从没实现的名字：**

```
CheckVerification · ExecuteConfigure · FindProductMultiInstore · GetThreeDsJwtQuery ·
MultipartScanEpilogueAsync · ParseMessageAsync · Purchase · RunShield ·
SubmitSaleRegistration · SubmitWebRtc
```

**这是一张「声称过但不存在」的清单 —— 而 R850 说的「有形状无内容」在这里换了个形态：
**有名字，没有形状，而且名字在文档里。****

### 去注释器为什么不能是正则

**`//` 剥到行尾的正则会撞上字符串里的 URL：**

```
var u = "https://example.test/a"; var after = 1;
                    ^^ 从这两个 / 开始剥，后面的真实代码全没了
```

**而剥掉代码比剥不掉注释**更坏** —— 它让存在的名字看起来不存在。
所以 `strip_comments` 是一个字符扫描器，跟踪四种字面量（普通串、verbatim 串、raw 串、字符字面量）。**

### 9 个用例，其中一个专门钉住这个

| 用例 | 钉什么 |
|---|---|
| **`AUrlInsideAStringDoesNotStartAComment`** | **字符串里的 URL 不开启注释，且其后的代码仍在** |
| `CodeSurvivesStripping` | **纯代码严格不变**（这是「剥多了」的守卫） |
| `AQuoteInsideABlockCommentDoesNotOpenAString` | 注释里的引号不开启字符串 |
| `VerbatimStringDoubledQuotesAreHandled` | `@""` 的转义不提前收尾 |
| `AnEscapedQuoteInAStringDoesNotEndIt` | `\\"` 同理 |
| `ACharLiteralHoldingAQuoteIsNotAString` | `'"'` 不开启字符串 |
| `TheTreeSplitsCodeFromComments` | **三个数相加 = 1547** |

### 而测试自身踩了两次坑

**① 第一次全红，因为 `python -c` 的参数被按空格拆开** —— 脚本在第一个空格处变成语法错误。
**② 第二次 `TheTreeSplitsCodeFromComments` 红，因为我用 `Where(char.IsDigit)` 抓数字，
把行尾的百分比也抓进去了（`362  23.4%` → `362234`）。** 改成只取冒号后第一段数字。

### 数字与代价

| 度量 | R914 | **R915** |
|---|---|---|
| 套件 | 1821 | **1830** |
| **异步覆盖（去注释）** | 372（24.0%，含假阳性） | **362（23.4%）** |
| 缺失名承载出现次数 | 1303 | **1313** |

**而代价：那 9 个用例跑了 **1 分 16 秒**，因为每个 `Strip` 起一个 python 进程。
**套件从 4 分钟涨到 6 分钟。这是可接受但我该写在案的成本。****
"""

if "去掉注释再数" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R915 appended")

VERDICT = """

---

## 第 915 轮：去掉注释再数 —— 23.4%，而 10 个名字只活在注释里

### 三个数

| 判据 | 名字 | 占比 |
|---|---|---|
| **在代码里** | **362** | **23.4%** |
| **只在注释里** | **10** | **0.6%** |
| **两者都没有** | **1175** | **76.0%** |

**那 10 个全部是我在文档注释里点过名、却从没实现的名字：**

```
CheckVerification · ExecuteConfigure · FindProductMultiInstore · GetThreeDsJwtQuery ·
MultipartScanEpilogueAsync · ParseMessageAsync · Purchase · RunShield ·
SubmitSaleRegistration · SubmitWebRtc
```

> **这是一张「声称过但不存在」的清单 —— R850 的「有形状无内容」在这里换了形态：
> **有名字，没有形状，而且名字在文档里。****

### 去注释器为什么不能是正则

```
var u = "https://example.test/a"; var after = 1;
                    ^^ 从这里剥到行尾，后面的真实代码全没了
```

> **剥掉代码比剥不掉注释**更坏** —— 它让存在的名字看起来不存在。**
> **所以 `strip_comments` 是字符扫描器，跟踪四种字面量。**

### 9 个用例

**`AUrlInsideAStringDoesNotStartAComment` · `CodeSurvivesStripping`（「剥多了」的守卫）·
`AQuoteInsideABlockCommentDoesNotOpenAString` · `VerbatimStringDoubledQuotesAreHandled` ·
`AnEscapedQuoteInAStringDoesNotEndIt` · `ACharLiteralHoldingAQuoteIsNotAString` ·
`TheTreeSplitsCodeFromComments`（**三个数相加 = 1547**）**

### 而测试自身踩了两次坑

**① `python -c` 的参数被按空格拆开 → 脚本在第一个空格变成语法错误 → 全红。
② `Where(char.IsDigit)` 把行尾百分比也抓进去（`362  23.4%` → `362234`）。**

### 数字与代价

| 度量 | R914 | **R915** |
|---|---|---|
| 套件 | 1821 | **1830** |
| **异步覆盖** | 372（24.0%，含假阳性） | **362（23.4%）** |
| 缺失承载出现次数 | 1303 | **1313** |

**代价：那 9 个用例 1 分 16 秒（每个起一个 python 进程）→ 套件 4 分钟涨到 6 分钟。可接受，但该写在案。**

### 教训

> **R914 的 +1 是假阳性，我把它写出来了。这一轮量清：假阳性一共 10 个，而它们全是我自己的文档。**
> **所以「覆盖 24.0%」这个数一直偏高了 0.6 个百分点，而**来源是我讲过的那些名字**。**
> **一个数被自己的注释抬高 —— 这是最难发现的一种，因为注释读起来像证据。**
"""

BACKLOG_ADD = """

## 判据 — 覆盖 **23.4%**（去注释）；10 个名字只在注释里（R915，**新工具 `tools/comment_split.py` +9 用例**）

### 三个数

| 判据 | 名字 | 占比 |
|---|---|---|
| **在代码里** | **362** | **23.4%** |
| **只在注释里** | **10** | **0.6%** |
| 两者都没有 | 1175 | 76.0% |

**那 10 个「声称过但不存在」：** `CheckVerification` `ExecuteConfigure` `FindProductMultiInstore`
`GetThreeDsJwtQuery` `MultipartScanEpilogueAsync` `ParseMessageAsync` `Purchase` `RunShield`
`SubmitSaleRegistration` `SubmitWebRtc`

### `strip_comments` 是字符扫描器，不是正则

**正则 `//` 剥到行尾会撞字符串里的 `https://` → **剥掉真实代码**，比剥不掉更坏。**
**四种字面量都跟踪：普通串 · verbatim `@""` · raw `\"\"\"` · 字符字面量。**

### 两个工具已改用去注释文本

`async_method_coverage.py` · `absent_by_leverage.py` 现在 `import comment_split` 并 `strip_comments(text)`。

### 数字与代价

**套件 1821 → 1830 · 覆盖 372（含假阳性）→ **362 = 23.4%** · 缺失承载 1303 → 1313**
**代价：9 个用例 1 分 16 秒（每 Strip 起一个 python 进程）→ 套件 4 分钟涨到 6 分钟。**

### 测试自身两次坑

**① `python -c` 参数按空格拆开 → 全红。② `Where(char.IsDigit)` 抓进百分比 → `362234`。**

| 仍 Unknown | |
|---|---|
| 那 10 个里哪些该实现 | `RunShield`/`SubmitWebRtc` 已知，其余未判 |
| 注释假阳性还会不会再产生 | 工具已修，但**新注释仍会增**（现在会被正确分类） |

**纪律**：**一个数被自己的注释抬高 —— 这是最难发现的一种，因为注释读起来像证据。**
"""

BLOCKER = """

---

## 339. 覆盖 **23.4%**（去注释）；10 个名字只活在注释里

> R915。**新工具 + 改两个工具 + 9 用例。** 套件 **1830 通过 / 0 失败 / 0 跳过**。

### 一、三个数

| 判据 | 名字 | 占比 |
|---|---|---|
| **在代码里** | **362** | **23.4%** |
| **只在注释里** | **10** | **0.6%** |
| 两者都没有 | **1175** | 76.0% |

**那 10 个「声称过但不存在」：**

`CheckVerification` `ExecuteConfigure` `FindProductMultiInstore` `GetThreeDsJwtQuery`
`MultipartScanEpilogueAsync` `ParseMessageAsync` `Purchase` `RunShield` `SubmitSaleRegistration` `SubmitWebRtc`

**→ R850 的「有形状无内容」在这里换了形态：**有名字，没有形状，而且名字在文档里。****

### 二、`strip_comments` 不能是正则

```
var u = "https://example.test/a"; var after = 1;
                    ^^ 从这里剥到行尾，后面的真实代码全没了
```

**剥掉代码比剥不掉注释**更坏**——它让存在的名字看起来不存在。**

**所以是字符扫描器，跟踪四种字面量：普通串 · verbatim 串 · raw 串 · 字符字面量。**

### 三、9 个用例

**`AUrlInsideAStringDoesNotStartAComment` · `CodeSurvivesStripping`（「剥多了」守卫）·
`AQuoteInsideABlockCommentDoesNotOpenAString` · `VerbatimStringDoubledQuotesAreHandled` ·
`AnEscapedQuoteInAStringDoesNotEndIt` · `ACharLiteralHoldingAQuoteIsNotAString` ·
`TheTreeSplitsCodeFromComments`（三数相加 = 1547）等。**

### 四、而测试自身踩了两次

**① `python -c` 参数被按空格拆开 → 脚本在第一个空格变语法错误 → 9 个全红。
② `Where(char.IsDigit)` 把行尾百分比抓进去（`362  23.4%` → `362234`）→ 第 9 个红。**

**两次都是**测试写错而不是代码写错**，而第二次是「解析得太宽」——与 R911 的锚点过宽同一类。**

### 五、数字与代价

| 度量 | R914 | R915 |
|---|---|---|
| 套件 | 1821 | **1830** |
| 异步覆盖 | 372（含假阳性） | **362 = 23.4%** |
| 缺失承载出现次数 | 1303 | 1313 |

**代价：9 个用例 1 分 16 秒（每 Strip 起一个 python 进程）→ 套件 4 分钟涨到 6 分钟。**

### 六、仍然 Unknown

- **那 10 个里哪些该实现**：**Unknown** —— `RunShield` 与 `SubmitWebRtc` 已知（后者已实现防护但名字只在注释里），
  其余八个未判。
- **注释假阳性还会不会再产生**：**会** —— 工具现在能正确分类，但新写的注释仍会把名字计入「只在注释里」那一格，
  而那一格现在是可见的。

### 七、教训

**一个数被自己的注释抬高 —— 这是最难发现的一种，因为**注释读起来像证据**。**

**R914 我只发现了一个（`SubmitWebRtc`）。这一轮量出是 10 个，而它们全部来自我讲过的名字。**

**所以「我提到过它」和「它存在」之间的差，是 10 个名字。而工具之前把两者当同一件事。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R915", BLOCKER)
    ensure(RSTATUS, "R915", BLOCKER)
    ensure(RVERDICT, "第 915 轮", VERDICT)
    ensure(BACKLOG, "R915", BACKLOG_ADD)

    note = (
        "\n## R915 补充 — 去注释再数：覆盖 23.4%，10 个名字只在注释里（新工具 comment_split.py +9 用例）\n\n"
        "三数：代码里 362（23.4%）· 只在注释里 10（0.6%）· 都没有 1175（76.0%）。\n\n"
        "那 10 个是「声称过但不存在」：CheckVerification ExecuteConfigure FindProductMultiInstore GetThreeDsJwtQuery "
        "MultipartScanEpilogueAsync ParseMessageAsync Purchase RunShield SubmitSaleRegistration SubmitWebRtc。\n\n"
        "strip_comments 是字符扫描器不是正则（正则 // 会撞字符串里的 https:// → 剥掉真实代码，比剥不掉更坏）。"
        "跟踪四种字面量。两个覆盖工具已改用它。\n\n"
        "数字：套件 1821 → 1830 · 覆盖 372（含假阳性）→ 362 = 23.4% · 缺失承载 1303 → 1313。\n"
        "代价：9 个用例 1 分 16 秒（每 Strip 起 python 进程）→ 套件 6 分钟。\n\n"
        "测试自身两次坑：python -c 参数按空格拆开（全红）· Where(char.IsDigit) 抓进百分比（362234）。\n\n"
        "下一轮：从「只在注释里」那 10 个里挑真该实现的（RunShield 已知）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R915" not in h:
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
             for p, k in ((RBLOCK, "R915"), (RSTATUS, "R915"), (RVERDICT, "第 915 轮"), (BACKLOG, "R915")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R915: coverage counted against code, and ten names that existed only in prose\n\n"
         "R914 reported coverage at 372 and admitted the increment was its own comment. This round measured the whole\n"
         " thing: three hundred and sixty-two names are in code, twenty-three point four percent; ten exist only in\n"
         " comments; eleven hundred and seventy-five are absent from both.\n\n"
         "The ten are exactly the names I had named in doc comments and never implemented -- CheckVerification,\n"
         " ExecuteConfigure, FindProductMultiInstore, GetThreeDsJwtQuery, MultipartScanEpilogueAsync, ParseMessageAsync,\n"
         " Purchase, RunShield, SubmitSaleRegistration and SubmitWebRtc. That is a claimed-but-absent list, and it is\n"
         " R850's shape without content in a new form: a name, no shape, and the name lives in documentation.\n\n"
         "The stripper cannot be a regex. Stripping from // to end of line cuts a string literal holding a URL and takes\n"
         " the real code after it, which is worse than leaving a comment in place because it makes present names look\n"
         " absent. So comment_split scans characters and tracks four literal forms: ordinary, verbatim, raw and\n"
         " character. Both coverage tools now import it.\n\n"
         "Nine tests cover it, including one that asserts a URL inside a string does not open a comment, one that\n"
         " asserts pure code survives unchanged, and one that runs the tool over the whole tree and checks the three\n"
         " figures sum to the image's name count.\n\n"
         "Two of those tests failed first for reasons that were the test's fault: python -c arguments were split on\n"
         " spaces, so the script became a syntax error at the first one and all nine failed; and Where(char.IsDigit)\n"
         " collected the percentage as well, turning 362 and 23.4 into 362234. The second is the same shape as R911's\n"
         " anchor being too wide -- parsing more than was meant.\n\n"
         "Figures: suite 1821 to 1830, coverage 372 to 362 or twenty-three point four percent, absent names carrying\n"
         " 1313 occurrences up from 1303. The cost is real and belongs in the record: the nine tests take a minute and\n"
         " sixteen seconds because each strip spawns a python process, and the suite went from four minutes to six.\n\n"
         "Unknown: which of the ten deserve implementing, RunShield and SubmitWebRtc being known and the other eight not\n"
         " judged; and whether comment false positives continue, which they will, though the tool now puts them in a\n"
         " visible column instead of the implemented one.\n\n"
         "The lesson is that a figure was being raised by its own commentary, which is the hardest kind to notice\n"
         " because commentary reads like evidence. R914 caught one instance; there were ten, and all ten were names I\n"
         " had talked about.\n\n"
         "Tools and tests changed; suite green at 1830."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()