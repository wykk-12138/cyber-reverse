"""Record R947: three of the eight verified true, three are not image claims, and one never existed."""

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
### 验那 8 条：4 真 · 3 自证 · **1 根本不存在**（R947）

**R946 说八条里七条开着、按 R944 比例大概两条是错的。验了。**

### 三条**真的**

```
datadome.co   n=33  —— 全是厂商自己的域：api-js.datadome.co · api-sdk.datadome.co
buy/carts     n=0
buy/orders    n=0
```

**而 `DataDomeRelay = "datadome.cybersole.io/"` —— **第一方中继**。
`datadome.co` 不是它的子串（第 10 个字符 `o` vs `y`），所以那条断言不仅真，而且**说的正是要紧的事**：
中继用的是自家域，不是厂商域。**

### 而三条**根本不是关于镜像的断言**

**`PopMartStepMap` 与 `JohnLewisStepMap` 都有 `UnmappedSteps` 列表 ——
所以 `Assert.Null(EndpointFor("CheckResult"))` 说的是「它在那个列表里」，**是复刻件自己的记账**，
一条已经写下来的事实，不是对二进制的陈述。**

> **而那意味着 R946 把它们列进「需镜像」是**错的归类** ——
> 而更早有人在别处已经把这条缺口记下来了（`UnmappedSteps`）。**
> **所以那个机制一直在；我只是没查它就开始分类。**

### 而一条**根本不存在**

**「`NikeEndpoints.OrderV5` 不含 `scheels`」—— 那条断言在仓库里没有任何一处。**

> **R946 把它写进清单，是根据**扫描样例**里的一行推断的，而**从没读过测试体**。
> 所以八条清单从一开始就有一条是编的 —— 而它编的方式和 R944 那条假缺席**一模一样**：
> **一个听起来合理的断言，没人去读它到底在不在。****

### 所以真正的结论：**需镜像的只有 3 条，而它们全是真的**

**而 R944 那个「3 条里 1 条假」的比例，在这次样本上没有重现 ——
因为那次的三条里有两条是**同一个错写了三遍**，不是三个独立的错。**

> **所以那个「比例」本身是我从 n=3 里外推的，而 n=3 里还有两条是同一件事。
> 真相是 n=1。****

### 数字

| 度量 | R946 | **R947** |
|---|---|---|
| 套件 | 2052 | **2053** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044** |
| 需镜像的否定 | 8（7 开） | **3（全真）· 3 自证 · 1 撤回 · 1 早结** |

### 教训

> **这一轮我没有找到一个错的否定，而是发现了三件关于**我自己那次分类**的事：
> 两条归错类（`UnmappedSteps` 早就记了）、一条是编的（没读测试体）、
> 而上一轮那个「比例」是从 n=1 外推出来的。**
> **而它们的共同形状是：**我在**描述**证据，而不是**读**证据。**
> **读一行扫描输出和读一个测试体，成本差十倍，而错误的代价是同一件事：一个数字被写进文档。**
"""

if "验那 8 条：4 真" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 947 轮：验那 8 条 —— 4 真 · 3 自证 · 1 根本不存在

### 三条真的

```
datadome.co  n=33  —— 全是厂商自己的域：api-js.datadome.co · api-sdk.datadome.co
buy/carts    n=0
buy/orders   n=0
```

**而 `DataDomeRelay = "datadome.cybersole.io/"` 是**第一方中继**。
`datadome.co` 不是它的子串（第 10 字符 `o` vs `y`）→ 那条断言真，且说的正是要紧的事。**

### 三条根本不是关于镜像的

**`PopMartStepMap` 与 `JohnLewisStepMap` 都有 `UnmappedSteps` ——
`Assert.Null(EndpointFor("CheckResult"))` 说的是「它在那个列表里」，是**复刻件自己的记账**。**

> **所以 R946 把它们归进「需镜像」是错归类 —— 而那个机制一直在，我没查就开始分类。**

### 一条根本不存在

**「`NikeEndpoints.OrderV5` 不含 `scheels`」在仓库里没有一处。
R946 是根据**扫描样例的一行**推断的，从没读过测试体。**

> **它编的方式和 R944 那条假缺席一模一样：一个听起来合理的断言，没人去读它到底在不在。**

### 而「3 条里 1 条假」这个比例是从 n=1 外推的

**R944 那三条里有两条是**同一个错写了三遍**，不是三个独立的错。真相是 n=1。**

### 数字

| 度量 | R946 | **R947** |
|---|---|---|
| 套件 | 2052 | **2053** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044** |
| 需镜像否定 | 8（7 开） | **3 全真 · 3 自证 · 1 撤回 · 1 早结** |

### 教训

> **这一轮没找到一个错的否定，而是发现三件关于**我那次分类**的事：
> 两条归错类、一条是编的、而那个「比例」是从 n=1 外推的。
> **共同形状：我在**描述**证据，而不是**读**证据。**
> **读一行扫描输出和读一个测试体，成本差十倍，而错误的代价是同一件事：一个数字被写进文档。**
"""

BACKLOG_ADD = """

## 判据 (a)/③ — 8 条验完：3 真 · 3 自证 · 1 撤回（R947，**改测例**）

### 三条真的（搜索）

**`datadome.co` n=33（厂商域）· `buy/carts` 0 · `buy/orders` 0**

**而 `DataDomeRelay = datadome.cybersole.io/` 是第一方中继，`datadome.co` 不是其子串。**

### 三条自证

**`PopMart`/`JohnLewis` 的 `Assert.Null(EndpointFor(x))` 说的是「在 `UnmappedSteps` 里」——
复刻件记账，不是镜像陈述。那个机制一直在。**

### 一条撤回

**「OrderV5 不含 scheels」不存在 —— R946 从扫描样例一行推断，没读测试体。**

### 而「3 条 1 假」是从 n=1 外推

**R944 的三条里两条是同一个错写三遍。**

### 数字

**套件 2052 → 2053 · 陈旧度不变 · 需镜像否定 8（7 开）→ 3 全真**

| 仍 Unknown | |
|---|---|
| 是否还有第 4 条需镜像 | 只查了带引号名字的 |
| `UnmappedSteps` 是否都有出处 | 未逐个核 |
| scheels 那 33 条用在何处 | 只知道存在 |

**纪律**：读一行扫描输出和读一个测试体，成本差十倍，而错误的代价相同：一个数字被写进文档。
"""

BLOCKER = """

---

## 371. 8 条验完：3 真 · 3 自证 · 1 撤回

> R947。**改测例。** 套件 **2053 通过 / 0 失败 / 0 跳过**。

### 一、三条真的

```
datadome.co  n=33（api-js / api-sdk，厂商自己的域）
buy/carts    n=0
buy/orders   n=0
```

**`DataDomeRelay = datadome.cybersole.io/` 是第一方中继；`datadome.co` 不是其子串（第 10 字符 o vs y）。
所以那条断言真，且说的正是要紧的事。**

### 二、三条不是关于镜像的

**`PopMartStepMap` / `JohnLewisStepMap` 有 `UnmappedSteps` →
`Assert.Null(EndpointFor(x))` = 「x 在列表里」= 复刻件记账。**

**→ R946 归错类；而那个机制一直在，我没查就开始分类。**

### 三、一条根本不存在

**「OrderV5 不含 scheels」在仓库里没有一处。R946 从扫描样例一行推断，没读测试体。
它编的方式和 R944 的假缺席一模一样。**

### 四、「3 条 1 假」是 n=1 外推

**R944 三条里两条是同一个错写三遍。**

### 五、数字

| 度量 | R946 | R947 |
|---|---|---|
| 套件 | 2052 | **2053** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044** |
| **需镜像否定** | 8（7 开） | **3（全真）· 3 自证 · 1 撤回 · 1 早结** |

### 六、验证

```
analysis/ida.py str "datadome"   -> 33，含 api-js / api-sdk
analysis/ida.py str "buy/carts"  -> 0
analysis/ida.py str "buy/orders" -> 0
grep scheels tests/              -> 无「OrderV5 不含 scheels」断言
test --filter NegativeClaimClassTests -> 5 通过
metrics_report.py                -> 2053 通过 / 0 失败
```

### 七、仍然 Unknown

- **是否还有第 4 条需镜像**：**Unknown** —— 只查了带引号名字的。
- **`UnmappedSteps` 是否都有出处**：**Unknown** —— 未逐个核。
- **scheels 那 33 条用在何处**：**Unknown** —— 只知道存在。

### 八、教训

**这一轮没找到一个错的否定，而是发现三件关于**我那次分类**的事：两条归错类、一条是编的、「比例」是 n=1 外推。**

**共同形状：我在描述证据，而不是读证据。**

**读一行扫描输出和读一个测试体，成本差十倍，而错误的代价是同一件事：一个数字被写进文档。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R947", BLOCKER)
    ensure(RSTATUS, "R947", BLOCKER)
    ensure(RVERDICT, "第 947 轮", VERDICT)
    ensure(BACKLOG, "R947", BACKLOG_ADD)

    note = (
        "\n## R947 补充 — 8 条验完：3 真 · 3 自证 · 1 撤回（套件 2053）\n\n"
        "三条真的：datadome.co n=33（厂商域 api-js/api-sdk）、buy/carts 0、buy/orders 0。"
        "而 DataDomeRelay=datadome.cybersole.io/ 是第一方中继，datadome.co 不是其子串（第10字符 o vs y）。\n\n"
        "三条自证：PopMart/JohnLewis 的 Assert.Null(EndpointFor(x)) 说的是「在 UnmappedSteps 里」—— 复刻件记账，"
        "不是镜像陈述。R946 归错类；那个机制一直在。\n\n"
        "一条撤回：「OrderV5 不含 scheels」不存在 —— R946 从扫描样例一行推断，没读测试体。\n"
        "而「3 条 1 假」是从 n=1 外推（R944 三条里两条是同一错写三遍）。\n\n"
        "数字：套件 2052 → 2053 · 陈旧度不变 · 需镜像否定 8（7 开）→ 3 全真。\n\n"
        "纪律：读一行扫描输出和读一个测试体，成本差十倍，而错误的代价相同：一个数字被写进文档。\n\n"
        "下一轮：核心覆盖表（判据 f）—— 原版站点与风控清单 ↔ Registry.cs 与 Flows/Scripts 逐条对。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R947" not in h:
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
             for p, k in ((RBLOCK, "R947"), (RSTATUS, "R947"), (RVERDICT, "第 947 轮"), (BACKLOG, "R947")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R947: three of the eight verified true, three were never image claims, and one never existed\n\n"
         "R946 ended with eight claims needing the image, seven open, and an expectation from R944's ratio that around two\n"
         " would be wrong. Checking them produced a different result: three are true, three were miscategorised, one does\n"
         " not exist, and the ratio itself was an extrapolation from a single case.\n\n"
         "The true ones: datadome.co returns 33 hits, all of them the vendor's own hosts at api-js and api-sdk, which is\n"
         " exactly why the relay must not contain it -- the relay is first-party at datadome.cybersole.io and datadome.co\n"
         " is not a substring of it, the tenth character being y rather than o. buy/carts and buy/orders return zero each,\n"
         " so NikeEndpoints is right to carry neither. And ScrapeProductBox was already settled in R938.\n\n"
         "The miscategorised three are not claims about the image at all. PopMartStepMap and JohnLewisStepMap both keep an\n"
         " UnmappedSteps list, so asserting EndpointFor returns null says the step is on that list -- a fact about the\n"
         " replica's own bookkeeping, already written down. The mechanism for exactly this kind of gap has been there all\n"
         " along and I classified without looking for it.\n\n"
         "And one never existed. There is no assertion anywhere that NikeEndpoints.OrderV5 avoids scheels; R946 put it in\n"
         " the list from a line in a scan sample without reading a test body. It was invented the same way R944's false\n"
         " absence was: a claim that sounds reasonable enough that nobody checks whether it is there.\n\n"
         "Which also disposes of the ratio. R944's three contained two copies of one mistake, so the sample size was one,\n"
         " and predicting two false claims from it was arithmetic on a number that had no distribution behind it.\n\n"
         "Figures: suite 2052 to 2053, freshness unchanged, and the eight claims resolved as four true, three\n"
         " self-proving and one withdrawn.\n\n"
         "Unknown: whether a fourth image claim exists outside the ones naming a quoted string; whether every UnmappedSteps\n"
         " entry has a source; and where the 33 scheels strings are used.\n\n"
         "The lesson is that this round found no false negative; it found three problems in my own classification -- two\n"
         " miscategorised, one invented, and a ratio extrapolated from one case. All three have the same shape, which is\n"
         " describing evidence instead of reading it. Reading one line of scan output and reading a test body differ tenfold\n"
         " in cost and cost the same when wrong: a number written into a document.\n\n"
         "Tests changed; no product code; suite green at 2053."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()