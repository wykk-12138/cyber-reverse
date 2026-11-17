"""Record R1035: the endpoint gate is all-zero, and unresolved meant shape rather than evidence."""

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
### 端点门**三项全零**；而 `unresolved` 说的是形式不是证据（R1035）

**R1034 说下一轮做 `unresolved 4`（Warhammer 的 `IdentityHost` 模板）。做了，而它和上一轮是同一个病。**

### ① 那 4 条其实**逐字有据**

工具把它们报成 `unresolved`（解析不了 `IdentityHost + "/path"` 的拼接）。而镜像里：

```
0x1470718ac  https://login.mywarhammer.com/usernamepassword/login
0x147071824  https://login.mywarhammer.com/usernamepassword/challenge
0x1470717bc  https://login.mywarhammer.com/oauth/token
0x14707174c  https://login.mywarhammer.com/login/callback
```

**→ 四条**完整 URL（含 host）**逐字在镜像里。
→ 所以 `unresolved` 不是「缺证据」，是**这个文件的形式让工具看不见**。**

### ② 而拼接形式**比完整串更不忠实**

**镜像存的是**每条端点一个完整字面量，没有拼接**。
→ 而 `IdentityHost + "/usernamepassword/login"` 是运行时拼出来的 —— 那是我方的形状，不是镜像的形状。
→ **所以写全是更忠实的写法，不是妥协。**

**→ 而那与 R1034 的修法是同一件事的两面：**
| 轮 | 谁看不见 | 修法 |
|---|---|---|
| R1034 | 工具看不见**含模板**的台账条目 | 比对时接受两种形 |
| **R1035** | 工具看不见**常量拼接** | **把拼接改成完整字面量** |

**→ 两次都不是放宽判据，是**让写法与证据的形式对齐**。**

### ③ 结果：三项全零

```
修前:  endpoint constants: 210   verbatim in pool: 210   invented: 0   unresolved: 4
修后:  endpoint constants: 214   verbatim in pool: 214   invented: 0   unresolved: 0
       inline literals: 331   not in pool: 41   registered: 41
       unknown: 0   baseline: 0   exit 0
```

**→ 常量从 210 增到 **214** —— 那 4 条从「看不见」变成了「看见且逐字有据」。
→ 而 `verbatim in pool: 214 / 214` ⇒ **全部常量都逐字在镜像里。**
→ **`invented: 0` · `unresolved: 0` · `unknown: 0` —— 端点门的三项第一次同时为零。****

### ④ 而 `IdentityHost` **没有删**

**它还在，因为两处**真的是**拼出来的：`$"{IdentityHost}/api/me"` 与 `$"{IdentityHost}/api/v1/login"`
（前者在 R787 记录过、`/api/me` 是 assembled）。
**→ 所以守卫不去禁这个标识符，而是逐条点名那 4 个常量 —— 禁 Identifier 会断言一件对文件为假的事。**

### ⑤ 5 条守卫

| 守卫 | 断言 |
|---|---|
| `EachIsWrittenOutInFull` ×4（`[Theory]`） | 每个常量是完整 URL 字面量，且不含 `IdentityHost +` |
| `TheHostConstantStaysForTheAssembledSites` | `IdentityHost` **仍在**（那两处真的拼） |

**→ 第 2 条是防「过度清理」：一条把 `IdentityHost` 全禁掉的守卫，会逼着把两处**真拼接**也写成假字面量。**

### ⑥ 数字

| 度量 | R1034 | **R1035** |
|---|---|---|
| 套件 | 2247 / 0 | **2252 / 0 / 0（+5）** |
| 产物陈旧度 | 5 / 4,199 | **6 / 5,786**（`RetailFlows.cs` 进陈旧集） |
| 函数数 | 174,336 | **174,336** |
| **`endpoint constants`** | 210 | **214** |
| **`verbatim in pool`** | 210 / 210 | **214 / 214** |
| **`unresolved`** | **4** | **0** |
| **`invented`** | 0 | **0** |
| **`unknown`** | 0 | **0** |
| **端点门 exit** | 0 | **0** |
| **三项同时为零** | **否** | **是（第一次）** |

### 教训

> **R1034 我以为修的是「两份台账」；R1035 发现修的是**同一个病的第二次**：
> 判据看不见某种写法，而「看不见」在输出里长得和「没有」一样。**
> **→ 而两次的正确反应都不是让判据更宽松，而是**让写法去贴合证据的形式**。**
> **→ 那条更深的规则是：**当镜像存一个完整串时，我们的代码也该有一个完整串** ——
> 拼接是我方抽象带来的，而抽象会同时藏起证据和缺陷。**
"""

if "端点门**三项全零**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1035 轮：端点门三项全零；而 `unresolved` 说的是形式不是证据

### ① 那 4 条其实**逐字有据**

```
0x1470718ac  https://login.mywarhammer.com/usernamepassword/login
0x147071824  https://login.mywarhammer.com/usernamepassword/challenge
0x1470717bc  https://login.mywarhammer.com/oauth/token
0x14707174c  https://login.mywarhammer.com/login/callback
```

**→ 四条**完整 URL（含 host）逐字在镜像里。
→ 所以 `unresolved` 不是「缺证据」，是**这个文件的拼接形式让工具看不见**。**

### ② 而拼接形式**比完整串更不忠实**

**镜像存的是每条端点**一个完整字面量、无拼接**；而 `IdentityHost + "/path"` 是运行时拼的 ——
那是我方的形状。所以写全是更忠实的写法。**

**→ 与 R1034 是同一个病的两面：**

| 轮 | 判据看不见什么 | 修法 |
|---|---|---|
| R1034 | 含**模板**的台账条目 | 比对时接受两种形 |
| **R1035** | **常量拼接** | 把拼接改成完整字面量 |

**→ 两次都不是放宽判据，是**让写法贴合证据的形式**。**

### ③ 结果：三项全零

```
修前  210 / 210 / invented 0 / unresolved 4
修后  214 / 214 / invented 0 / unresolved 0      ← 常量增到 214，即那 4 条被看见了
      inline 331 / not in pool 41 / registered 41 / unknown 0 / exit 0
```

**→ `verbatim in pool: 214 / 214` ⇒ 全部常量逐字在镜像里。
→ `invented: 0` · `unresolved: 0` · `unknown: 0` —— **三项第一次同时为零**。**

### ④ 而 `IdentityHost` **没有删**

**它还在，因为 `$"{IdentityHost}/api/me"` 与 `$"{IdentityHost}/api/v1/login"` **真的是拼的**。
→ 守卫逐条点名那 4 个常量，而不是禁这个标识符 —— 禁它会断言一件对文件为假的事。**

### ⑤ 5 条守卫

`EachIsWrittenOutInFull` ×4（`[Theory]`）+ `TheHostConstantStaysForTheAssembledSites`（防过度清理）

### ⑥ 数字

| 度量 | R1034 | **R1035** |
|---|---|---|
| 套件 | 2247 / 0 | **2252 / 0 / 0（+5）** |
| 产物陈旧度 | 5 / 4,199 | **6 / 5,786** |
| 函数数 | 174,336 | **174,336** |
| **`endpoint constants`** | 210 | **214** |
| **`verbatim in pool`** | 210 / 210 | **214 / 214** |
| **`unresolved`** | **4** | **0** |
| **三项同时为零** | **否** | **是（第一次）** |

### 教训

> **R1034 我以为修的是「两份台账」；R1035 发现修的是**同一个病的第二次**：
> 判据看不见某种写法，而「看不见」在输出里与「没有」同形。**
> **→ 两次的正确反应都不是让判据更宽松，而是**让写法去贴合证据的形式**。**
> **→ 更深的规则：**当镜像存一个完整串时，代码也该有一个完整串** ——
> 拼接是我方抽象带来的，而抽象会同时藏起证据和缺陷。**
"""

BACKLOG_ADD = """

## 判据 (d)(f) — **端点门三项全零；`unresolved` 说的是形式不是证据**（R1035）

### 那 4 条逐字有据

```
0x1470718ac  https://login.mywarhammer.com/usernamepassword/login
0x147071824  https://login.mywarhammer.com/usernamepassword/challenge
0x1470717bc  https://login.mywarhammer.com/oauth/token
0x14707174c  https://login.mywarhammer.com/login/callback
```

**而代码里是 `IdentityHost + "/path"` ⇒ 工具解析不了拼接，报 `unresolved`。**
**→ 镜像存的是每条**一个完整字面量、无拼接** ⇒ 写全是**更忠实**，不是妥协。**

### 与 R1034 同一个病

| 轮 | 判据看不见 | 修法 |
|---|---|---|
| R1034 | 含模板的台账条目 | 比对接受两种形 |
| R1035 | 常量拼接 | 改成完整字面量 |

### 结果

```
210 / 210 / invented 0 / unresolved 4    →    214 / 214 / invented 0 / unresolved 0
unknown 0 · exit 0                          ← 三项第一次同时为零
```

### 5 条守卫

`EachIsWrittenOutInFull` ×4 + `TheHostConstantStaysForTheAssembledSites`（**防过度清理**：
`/api/me` 与 `/api/v1/login` 真的拼，禁 `IdentityHost` 会断言假事）

### 数字

**套件 2252（+5）· 陈旧度 6 / 5,786 · 函数数 174,336 · constants 210 → 214 · unresolved 4 → 0 ·
三项同时为零（第一次）**

| 仍 Unknown | |
|---|---|
| 那 6 条 `sent` 该继续发还是改报告 | 有 `sent` 格，可判了 |
| 产物需重新 publish（RetailFlows 进陈旧集） | 待下一轮或收尾时做 |

**纪律**：当镜像存一个完整串时，代码也该有一个完整串 —— 拼接是抽象，而抽象同时藏证据与缺陷。
"""

BLOCKER = """

---

## 459. **端点门三项全零；而 `unresolved` 说的是形式不是证据**

> R1035。**改 1 个源文件 + 1 个测试文件。** 套件 **2252 通过 / 0 失败 / 0 跳过**。
> **端点门 `invented` · `unresolved` · `unknown` 全部为零，第一次。**

### 一、那 4 条其实**逐字有据**

**工具把它们报成 `unresolved`（解析不了 `IdentityHost + "/path"`）。而镜像里：**

```
0x1470718ac  https://login.mywarhammer.com/usernamepassword/login
0x147071824  https://login.mywarhammer.com/usernamepassword/challenge
0x1470717bc  https://login.mywarhammer.com/oauth/token
0x14707174c  https://login.mywarhammer.com/login/callback
```

**→ 四条**完整 URL（含 host）逐字在镜像里。
→ 所以 `unresolved` 不是「缺证据」，是**这个文件的拼接形式让工具看不见**。**

### 二、而拼接形式**比完整串更不忠实**

**镜像存的是每条端点**一个完整字面量、无拼接**。
→ 而 `IdentityHost + "/usernamepassword/login"` 是运行时拼出来的 —— 那是我方的形状，不是镜像的形状。
→ **所以写全是更忠实的写法，不是妥协。**

**→ 与 R1034 是同一个病的两面：**

| 轮 | 判据看不见什么 | 修法 |
|---|---|---|
| R1034 | 含**模板**的台账条目 | 比对时接受两种形 |
| **R1035** | **常量拼接** | 把拼接改成完整字面量 |

**→ 两次都不是放宽判据，是**让写法与证据的形式对齐**。**

### 三、结果：三项全零

```
修前:  endpoint constants: 210   verbatim in pool: 210   invented: 0   unresolved: 4
修后:  endpoint constants: 214   verbatim in pool: 214   invented: 0   unresolved: 0
       inline literals: 331   not in pool: 41   registered: 41
       unknown: 0   baseline: 0   exit 0
```

**→ 常量从 210 增到 **214** —— 那 4 条从「看不见」变成了「看见且逐字有据」。
→ `verbatim in pool: 214 / 214` ⇒ **全部常量都逐字在镜像里。**
→ **`invented: 0` · `unresolved: 0` · `unknown: 0` —— 端点门的三项第一次同时为零。**

### 四、而 `IdentityHost` **没有删**

**它还在，因为两处**真的是**拼出来的：`$"{IdentityHost}/api/me"` 与 `$"{IdentityHost}/api/v1/login"`
（前者在 R787 记录过）。

**→ 所以守卫不去禁这个标识符，而是逐条点名那 4 个常量 —— 禁 Identifier 会断言一件对文件为假的事。**

### 五、5 条守卫

| 守卫 | 断言 |
|---|---|
| `EachIsWrittenOutInFull` ×4（`[Theory]`） | 每个常量是完整 URL 字面量，且不含 `IdentityHost +` |
| `TheHostConstantStaysForTheAssembledSites` | `IdentityHost` **仍在**（那两处真的拼） |

**→ 第 2 条是防「过度清理」：一条把 `IdentityHost` 全禁掉的守卫，会逼着把两处**真拼接**也写成假字面量。**

### 六、数字

| 度量 | R1034 | R1035 |
|---|---|---|
| 套件 | 2247 / 0 | **2252 / 0 / 0（+5）** |
| 产物陈旧度 | 5 / 4,199 | **6 / 5,786**（`RetailFlows.cs` 进陈旧集） |
| 函数数 | 174,336 | **174,336** |
| **`endpoint constants`** | 210 | **214** |
| **`verbatim in pool`** | 210 / 210 | **214 / 214** |
| **`unresolved`** | **4** | **0** |
| **`invented`** | 0 | **0** |
| **`unknown`** | 0 | **0** |
| **端点门 exit** | 0 | **0** |
| **三项同时为零** | **否** | **是（第一次）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse\\replica
python tools/endpoint-provenance.py  -> constants 214 / verbatim 214 / invented 0 / unresolved 0
                                        inline 331 / not in pool 41 / registered 41 / unknown 0 / exit 0
dotnet test --filter "FullyQualifiedName~WarhammerIdentityLiteral" -m:1 -> 5 通过
python tools/metrics_report.py -> 完整套件 exit 0  2252 / 0 / 0
```

### 八、仍然 Unknown

- **那 6 条 `sent` 该继续发还是改成报告**：**有 `sent` 格，可判了**。
- **产物需重新 publish**（`RetailFlows.cs` 进了陈旧集）：**待收尾时做**。

### 九、教训

**R1034 我以为修的是「两份台账」；R1035 发现修的是**同一个病的第二次**：
判据看不见某种写法，而「看不见」在输出里长得和「没有」一样。**

**→ 而两次的正确反应都不是让判据更宽松，而是**让写法去贴合证据的形式**。**

**→ 那条更深的规则是：**当镜像存一个完整串时，我们的代码也该有一个完整串** ——
  拼接是我方抽象带来的，而抽象会同时藏起证据和缺陷。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1035", BLOCKER)
    ensure(RSTATUS, "R1035", BLOCKER)
    ensure(RVERDICT, "第 1035 轮", VERDICT)
    ensure(BACKLOG, "R1035", BACKLOG_ADD)

    note = (
        "\n## R1035 补充 — **端点门三项全零；`unresolved` 说的是形式不是证据**（套件 2252）\n\n"
        "**那 4 条逐字有据**：`0x1470718ac/824/7bc/74c` 四条 `https://login.mywarhammer.com/...` 完整 URL 在镜像里。\n"
        "→ 代码里是 `IdentityHost + \"/path\"` ⇒ 工具解析不了拼接，报 `unresolved`。\n"
        "→ **镜像存的是每条一个完整字面量、无拼接 ⇒ 写全是**更忠实**，不是妥协。**\n\n"
        "**与 R1034 同一个病**：\n"
        "| 轮 | 判据看不见 | 修法 |\n|---|---|---|\n"
        "| R1034 | 含模板的台账条目 | 比对接受两种形 |\n"
        "| R1035 | 常量拼接 | 改成完整字面量 |\n"
        "→ **两次都不是放宽判据，是让写法贴合证据的形式。**\n\n"
        "```\n210/210/invented 0/unresolved 4  →  214/214/invented 0/unresolved 0\nunknown 0 · exit 0                   ← 三项第一次同时为零\n```\n\n"
        "**`IdentityHost` 没删**（`/api/me` 与 `/api/v1/login` 真的拼）；守卫逐条点名 4 个常量 + 一条防过度清理。\n"
        "**5 条守卫**（`WarhammerIdentityLiteralTests`）。\n\n"
        "数字：套件 2252（+5）· 陈旧度 6 / 5,786 · 函数数 174,336 · constants **210 → 214** · unresolved **4 → 0** ·\n"
        "三项同时为零 **第一次**。\n\n"
        "纪律：**当镜像存一个完整串时，代码也该有一个完整串 —— 拼接是抽象，抽象同时藏证据与缺陷。**\n\n"
        "下一轮：判那 6 条 `sent` 该继续发还是改报告；或重新 publish 让陈旧度归零。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1035" not in h:
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
             for p, k in ((RBLOCK, "R1035"), (RSTATUS, "R1035"), (RVERDICT, "第 1035 轮"), (BACKLOG, "R1035")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1035: the endpoint gate is all-zero, and unresolved meant shape rather than evidence\n\n"
         "R1034 closed by pointing at four unresolved constants in Warhammer's identity host. Looking at them shows the\n"
         " same defect as the round before, one layer along.\n\n"
         "All four are evidenced, verbatim and in full, at four addresses: login.mywarhammer.com with\n"
         " usernamepassword/login, usernamepassword/challenge, oauth/token and login/callback. The replica built them as\n"
         " IdentityHost plus a path at run time, and the tool cannot see through a constant concatenation, so it reported\n"
         " them as unresolved -- which reads as missing evidence and was really a statement about this file's shape.\n\n"
         "The artifact stores one complete literal per endpoint and no composition. Writing them out in full is therefore\n"
         " the more faithful form rather than a concession, and it is the second time in two rounds that the right\n"
         " response to a criterion that could not see something was to move the code toward the shape of the evidence\n"
         " rather than to loosen the criterion.\n\n"
         "Constants went from 210 to 214 because four that had been invisible are now counted, and all 214 are verbatim in\n"
         " the pool. Invented, unresolved and unknown are simultaneously zero for the first time.\n\n"
         "IdentityHost stays, because two sites genuinely compose -- /api/me and /api/v1/login -- so the guard names the\n"
         " four constants instead of banning the identifier, and a second guard asserts the constant is still there to stop\n"
         " a later clean-up from flattening the two that really are assembled.\n\n"
         "Figures: suite 2247 to 2252, freshness six files and 5,786 lines since RetailFlows is now newer than the\n"
         " published artifact, count 174,336, and a gate with nothing left to report.\n\n"
         "Unknown: whether the six sent endpoints should keep being sent or become reports, and a publish to bring\n"
         " freshness back to zero.\n\n"
         "The lesson is that invisible and absent print the same, twice now, and that composition is our abstraction\n"
         " rather than the artifact's -- so it hides the evidence and the defect in the same gesture.\n\n"
         "One source file and one test file changed; suite green at 2252."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()