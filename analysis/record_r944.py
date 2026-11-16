"""Record R944: PerimeterX's cookie existed all along, and the false absence was written three times."""

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
### 转优先级 ② 第一件事：`_px3` **一直都在**，而那个「没有」被写了三遍（R944）

**十轮做完 ①，转 ②。查五个厂商，四个全在：**

```
Kasada 40 · DataDome 15 · PerimeterX 5 (+ _px 4) · Queue-it 13
```

**而 `AntiBotProtocol.cs` 已经覆盖六家：Kasada · Akamai · DataDome · Cloudflare · Queue-it · TrustDecision。**

### 而它**不含 PerimeterX**，理由写在注释里

> 「PerimeterX is the exception: the image names the vendor and a token, but no `_px` cookie —
> so it is deliberately absent here rather than filled in from memory.」

**那句话写得很好 —— 它甚至防了「凭记忆填」。而它**是错的**：**

```
_px (n=4) → _px3 · _pxHandler · __pxvid · _pxvid
```

### 而同一个假缺席被写了**三遍**

| 位置 | 内容 |
|---|---|
| `AntiBotProtocol.cs` 的类注释 | 「no `_px` cookie」 |
| `VendorWiringTests` | `Assert.Null(CookiesFor("PerimeterX"))` |
| `AntiBotProtocolTests` | `Assert.Null(CookiesFor("PerimeterX"))` |

> **三遍。而这就是它从没被查的原因 —— **一个被重复的断言读起来像被印证的事实。****
> **而三处里有两处是**测例**。测例本来是防这件事的，而它们在这里**保存**了那件事。**
> **一个错被写成断言，就变成了「已验证」；写成三次，就变成了「显然」。**

### 补上了什么

```
_px3              主 cookie
__pxvid · _pxvid  两个访客 id（只差一个下划线，刻意不合并）
PerimeterX-Token  请求头（保留镜像的大小写）
PerimeterXHandler handler 名
"Solving PerimeterX" · "PerimeterX block (Rotating proxy)"   镜像自己的措辞，不解释
```

**而「两个访客 id 不合并」是刻意的：镜像有两种拼法，而没有东西说它们同值。**

### 而 cookie 表是 **5** 家不是 7

**Queue-it 用路由、TrustDecision 用脚本 —— 把它们算进 cookie 表就是断言一个它们没有的 cookie。**
**（我第一版测例写的 7，被自己的断言纠正了。）**

### 数字

| 度量 | R943 | **R944** |
|---|---|---|
| 套件 | 2036 | **2043** |
| 产物陈旧度 | 9 文件 / 920 行 | **10 文件 / 1044 行** |
| **cookie 表覆盖厂商** | 4 | **5（+PerimeterX）** |

### 教训

> **这一轮最值钱的不是补上 PerimeterX，是发现那个「刻意不填」的注释是错的。**
> **它之所以能活十轮，不是因为它隐蔽，而是因为它**被写得很有纪律** ——
> 「deliberately absent rather than filled in from memory」正是我会赞同的那种句子。**
> **而一个听起来像纪律的错误，比一个听起来像错误的错误贵得多。**
"""

if "`_px3` **一直都在**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R944 appended")

VERDICT = """

---

## 第 944 轮：`_px3` 一直都在，而那个「没有」被写了三遍

### 转优先级 ②，四个厂商全在

```
Kasada 40 · DataDome 15 · PerimeterX 5 (+_px 4) · Queue-it 13
```

**而 `AntiBotProtocol.cs` 覆盖六家，**不含 PerimeterX**，理由写在注释里：**

> 「the image names the vendor and a token, but no `_px` cookie — so it is deliberately absent here rather than filled
> in from memory.」

**那句话写得很好 —— 它甚至防了「凭记忆填」。而它**是错的**：`_px (n=4) → _px3 · __pxvid · _pxvid · _pxHandler`。**

### 而同一个假缺席被写了**三遍**

| 位置 | 内容 |
|---|---|
| 类注释 | 「no `_px` cookie」 |
| `VendorWiringTests` | `Assert.Null(...)` |
| `AntiBotProtocolTests` | `Assert.Null(...)` |

> **三遍。而这就是它从没被查的原因 —— 一个被重复的断言读起来像被印证的事实。**
> **三处里两处是**测例**。测例本来防这件事，而它们在这里**保存**了那件事。**
> **一个错被写成断言就变成「已验证」；写成三次就变成「显然」。**

### 补上的

**`_px3` · `__pxvid`/`_pxvid`（刻意不合并）· `PerimeterX-Token` · `PerimeterXHandler` · 两条镜像措辞**

### 而 cookie 表是 5 家不是 7

**Queue-it 用路由、TrustDecision 用脚本 —— 算进来就是断言一个它们没有的 cookie。
（第一版测例写 7，被自己的断言纠正。）**

### 数字

| 度量 | R943 | **R944** |
|---|---|---|
| 套件 | 2036 | **2043** |
| 产物陈旧度 | 9 / 920 | **10 / 1044** |
| cookie 表厂商 | 4 | **5** |

### 教训

> **最值钱的不是补上 PerimeterX，是发现那个「刻意不填」的注释是错的。
> 它能活十轮不是因为隐蔽，而是因为**它被写得很有纪律** ——
> 「deliberately absent rather than filled in from memory」正是我会赞同的那种句子。
> **一个听起来像纪律的错误，比一个听起来像错误的错误贵得多。**
"""

BACKLOG_ADD = """

## 优先级 ② — PerimeterX 补上；假缺席被写了三遍（R944，**改产品代码 +7 用例 + 修 3 处旧断言**）

### 发现

**`_px3` 一直在（n=1），而类注释说「no `_px` cookie」，并有两处 `Assert.Null` 把它钉住 —— 三遍。**

### 补上

**`_px3` · `__pxvid`/`_pxvid` · `PerimeterX-Token` · `PerimeterXHandler` · 「Solving PerimeterX」·
「PerimeterX block (Rotating proxy)」**

### cookie 表 4 → 5

**Queue-it 用路由、TrustDecision 用脚本，不算 cookie 家庭。**

### 数字

**套件 2036 → 2043 · 陈旧度 9/920 → 10/1044 · cookie 表厂商 4 → 5**

| 仍 Unknown | |
|---|---|
| Imperva 是否有 cookie | 未查（仍是未验证断言，已标注） |
| PerimeterX 的求解流程 | 只有名字与两条措辞 |
| `_pxvid` 与 `__pxvid` 是否同值 | 无证据 |

**纪律**：一个错被写成断言就变成「已验证」；写成三次就变成「显然」。
"""

BLOCKER = """

---

## 368. PerimeterX 补上；假缺席被写了三遍

> R944。**改产品代码 +7 用例 + 修 3 处旧断言。** 套件 **2043 通过 / 0 失败 / 0 跳过**。

### 一、转优先级 ②，四个厂商全在

```
Kasada 40 · DataDome 15 · PerimeterX 5 (+_px 4) · Queue-it 13
```

**`AntiBotProtocol.cs` 覆盖六家，缺 PerimeterX，理由在注释里：**

> 「the image names the vendor and a token, but no `_px` cookie — so it is deliberately absent here rather than filled
> in from memory.」

**而 `_px (n=4) → _px3 · _pxHandler · __pxvid · _pxvid`。那句话是错的。**

### 二、同一个假缺席被写了三遍

| 位置 | 内容 |
|---|---|
| `AntiBotProtocol.cs` 类注释 | 「no `_px` cookie」 |
| `VendorWiringTests` | `Assert.Null(CookiesFor("PerimeterX"))` |
| `AntiBotProtocolTests` | `Assert.Null(CookiesFor("PerimeterX"))` |

**三处里两处是测例 —— 测例本来防这件事，而它们在这里保存了那件事。**

### 三、补上的

**`_px3` · `__pxvid`/`_pxvid`（刻意不合并）· `PerimeterX-Token` · `PerimeterXHandler` ·
「Solving PerimeterX」·「PerimeterX block (Rotating proxy)」（镜像措辞，不解释）**

### 四、cookie 表 4 → 5，不是 7

**Queue-it 用路由、TrustDecision 用脚本 —— 算进 cookie 表就是断言它们没有的 cookie。**

### 五、数字

| 度量 | R943 | R944 |
|---|---|---|
| 套件 | 2036 | **2043** |
| 产物陈旧度 | 9 / 920 | **10 / 1044** |
| **cookie 表厂商** | 4 | **5** |

### 六、验证

```
analysis/ida.py str "_px"        -> 4：_px3 · _pxHandler · __pxvid · _pxvid
analysis/ida.py str "PerimeterX" -> 5：含 PerimeterX-Token / Handler
test --filter PerimeterXProtocolTests -> 7 通过
metrics_report.py                -> 2043 通过 / 0 失败
```

### 七、仍然 Unknown

- **Imperva 是否有 cookie**：**Unknown** —— 未查，仍是未验证断言（已在测例里标注）。
- **PerimeterX 的求解流程**：**Unknown** —— 只有名字与两条措辞。
- **`_pxvid` 与 `__pxvid` 是否同值**：**Unknown** —— 无证据。

### 八、教训

**最值钱的不是补上 PerimeterX，是发现那个「刻意不填」的注释是错的。**

**它能活十轮不是因为隐蔽，而是因为**它被写得很有纪律** ——
「deliberately absent rather than filled in from memory」正是我会赞同的那种句子。**

**一个听起来像纪律的错误，比一个听起来像错误的错误贵得多。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R944", BLOCKER)
    ensure(RSTATUS, "R944", BLOCKER)
    ensure(RVERDICT, "第 944 轮", VERDICT)
    ensure(BACKLOG, "R944", BACKLOG_ADD)

    note = (
        "\n## R944 补充 — PerimeterX 补上；假缺席被写了三遍（+7 用例 + 修 3 处，套件 2043）\n\n"
        "转优先级 ②：Kasada 40 · DataDome 15 · PerimeterX 5(+_px 4) · Queue-it 13 —— 四个全在。\n"
        "AntiBotProtocol.cs 覆盖六家但缺 PerimeterX，注释说「no _px cookie」—— 而 _px 有 4 条（_px3/__pxvid/_pxvid/_pxHandler）。\n\n"
        "同一个假缺席写了三遍：类注释 + VendorWiringTests 的 Assert.Null + AntiBotProtocolTests 的 Assert.Null。\n"
        "→ 三处里两处是测例；测例本来防这件事，而它们在这里保存了那件事。\n\n"
        "补上：_px3 · __pxvid/_pxvid（刻意不合并）· PerimeterX-Token · PerimeterXHandler · 两条镜像措辞。\n"
        "cookie 表 4 → 5（不是 7：Queue-it 用路由、TrustDecision 用脚本）。\n\n"
        "数字：套件 2036 → 2043 · 陈旧度 9/920 → 10/1044。\n\n"
        "纪律：一个听起来像纪律的错误，比一个听起来像错误的错误贵得多。\n\n"
        "下一轮：Imperva 是否也有 cookie（同一类未验证断言）；或 ③ 请求与指纹层。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R944" not in h:
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
             for p, k in ((RBLOCK, "R944"), (RSTATUS, "R944"), (RVERDICT, "第 944 轮"), (BACKLOG, "R944")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R944: PerimeterX's cookie existed all along, and the false absence was written three times\n\n"
         "Moving to the risk-control priority: all four remaining vendors turned out to be in the image -- Kasada,\n"
         " DataDome, PerimeterX, Queue-it -- and six of the seven were already covered by AntiBotProtocol. PerimeterX was\n"
         " the exception, and the reason was written down: the image names the vendor and a token but no _px cookie, so it\n"
         " was deliberately absent rather than filled in from memory. That sentence is careful, and it is wrong. A search\n"
         " for _px returns four matches, _px3 among them.\n\n"
         "The same false absence was written in three places: the class comment, Assert.Null in VendorWiringTests, and\n"
         " Assert.Null again in AntiBotProtocolTests. Two of the three were tests -- guards written to prevent exactly this,\n"
         " which here preserved it. A claim repeated reads like a corroborated fact; written into an assertion it becomes\n"
         " verified, and written three times it becomes obvious. That is why ten rounds passed without anyone looking.\n\n"
         "PerimeterX is now recorded from its own literals: the _px3 cookie, the two visitor ids kept apart because the\n"
         " image has both spellings and nothing says they hold the same value, the header in the image's capitalisation,\n"
         " the handler name, and two message strings recorded verbatim rather than interpreted.\n\n"
         "The cookie table goes from four vendors to five, not to seven: Queue-it works through join routes and\n"
         " TrustDecision through script names, so counting either here would assert a cookie it does not have. My first\n"
         " test said seven and its own assertion corrected me.\n\n"
         "Figures: suite 2036 to 2043, freshness from nine files to ten and nine hundred and twenty lines to a thousand\n"
         " and forty-four, and the cookie table from four vendors to five.\n\n"
         "Unknown: whether Imperva has a cookie, since no search was run and that assertion is now labelled unverified\n"
         " rather than trusted; PerimeterX's solving flow, of which only names and two message strings survive; and whether\n"
         " _pxvid and __pxvid hold the same value.\n\n"
         "The lesson is that a wrong claim which sounds disciplined costs more than one that sounds wrong. Deliberately\n"
         " absent rather than filled in from memory is the kind of sentence I would agree with, and agreeing with it is\n"
         " what stopped me checking.\n\n"
         "Product code and three assertions changed; suite green at 2043."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()