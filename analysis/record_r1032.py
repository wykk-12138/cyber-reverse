"""Record R1032: the ledger was six short, and the script that would fix it split a URL in half."""

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
### 账差 6 条；而补账的脚本把 URL 劈成了两半（R1032）

**R1031 说下一轮「不删，让 12 条与两张表对齐，找出**两边都没登记**的」。找了，也动手了，而动手的脚本坏了两个文件，已全部回滚。**

### ① 差在哪儿（精确到路径）

**工具的 12 条去重后是 6 个不同路径，而其中的归属：**

| 路径 | `Sent` | `DocumentedOnly` | 判定 |
|---|---|---|---|
| `/api/checkout/v1/basket/{basketId}` | ✓ | | 已登记 |
| `.../shipping` | ✓ | | 已登记 |
| `.../place-order` | ✓ | | 已登记 |
| **`/api/ff-products/v1/products/{pid}/`** | | | **两边都没有** |
| **`/api/basket/v1/`** | | （只有 `/api/basket/v1/items`，不同串） | **两边都没有** |
| **`.../payment`** | | | **两边都没有** |
| **`api.nike.com/buy/carts/v2/...`** | | | **两边都没有** |
| **`/discount/`** | | | **两边都没有** |
| **`/api/payments/`** | | | **两边都没有** |

**→ 所以「12 条」里 **6 条真的没有账**，而另外 3 类（5 处出现）是已登记的。
→ 而那 6 条不是新的 —— 它们**一直在发**，只是没人记。**

### ② 所以 `SentCeiling = 10` 是**账的记录**，不是**预算**

**加了 6 条之后 `Sent` 会有 16 个不同路径 ⇒ 上限必须调到 16。
→ 而那个调整**不是放宽**：`SentCeiling` 记的是「已经存在的无据债务」，
→ 而「防增长」的意思是**别再冒出第七条**，不是「这六条不能存在」。**

### ③ 而补标注那一步，我的脚本把两个文件改坏了

**棘轮要求：每一条**真的用到**那个路径的行都要带 `inferred: no image evidence`。
→ 我写了一个脚本去补，而它用 `if "//" in line` 找注释边界。**

**→ 而 `$"https://api.nike.com/buy/carts/v2/..."` 里的 `//` 被当成了注释起点：
→ 那一行被劈成 `$"https:` + 我的标注 + 剩下的 URL。**

```
改坏后：  $"https:  // inferred: no image evidence (R294)   // api.nike.com/buy/carts/v2/{CountryCode}/...
```

**→ 而那是 AGENTS 里 R764 那条（花括号计数被字符串里的 `{` 打乱）的**同族错误**：
用 `//` 找注释边界，撞上 URL 里的 `//`。**

**→ 而 `EveryUnbackedEndpointIsStillInItsFile` 立刻报了 `the path is gone` ——
守卫在这一步是救回来的那一个。**

### ④ 而同一轮里还有第二个同族错误：我把工具的截断当成了字面量

**工具打印的是 `https://api.nike.com/buy/carts/v2/{...}` —— 那个 `{...}` 是**工具自己的截断**，
而真实字面量是 `https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format...`。**

**→ 我照着截断后的样子写进 `Sent`，于是 `EveryUnbackedEndpointIsStillInItsFile` 又说「路径不见了」。
→ 而那是 R1016 的那个问题的**新位置**：上次是地址列没剥，这次是显示被截断。**

### ⑤ 所以本轮**净改动为零**，而交付是两个**具体的**前置条件

| 前置条件 | 为什么必须先有 |
|---|---|
| **补标注不能用 `//` 找注释边界** | `https://` 里有 `//`；该用「行尾已有 `//` 之后才切」或干脆整行替换 |
| **账要写**真实**字面量** | 工具显示会截断成 `{...}`；要 `grep` 原文而不是抄输出 |

**→ 而那两条都是**机械的**，一旦写下，补账是一件 20 分钟的事。
→ 而这一轮它们的代价是两次回滚 —— 因为我在**改之前**没有先把它们写下来。**

### ⑥ 数字

| 度量 | R1031 | **R1032** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（已回滚）** |
| 产物陈旧度 | 5 / 4,199 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **工具的未登记无据端点** | 12（6 个不同路径） | **12（6 个不同路径）** |
| **真正**没有账**的路径** | 未算 | **6** |
| **已登记、被误算进「12」的** | 未算 | **3 类（5 处）** |
| **本轮净代码改动** | — | **0（三次回滚）** |
| **同族错误（用语法符号找边界）** | R764 一次 | **R764 + 本轮两次** |

### 教训

> **这一轮我犯了两个「用语法符号找边界」的错，而两个都被守卫当场抓住。**
> **→ 而它们的共同点是：我拿一个**在人写的代码里**成立的规则（`//` 之后是注释），
> 去处理**机器写的内容**（URL、工具输出）。**
> **→ 而 R764 那次是 `{`，R1016 那次是地址列 —— 三次的形状相同。
> → 所以下次动手前该问的是：**我用来切分的那个符号，在被切的东西里会不会合法地出现。****
"""

if "账差 6 条" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1032 轮：账差 6 条；而补账的脚本把 URL 劈成了两半

### ① 差在哪儿（精确到路径）

**工具 12 条去重后 6 个路径，其中 3 类已登记（`basket/{id}` · `/shipping` · `/place-order`，共 5 处），
而 **6 条真的没有账**：**

```
/api/ff-products/v1/products/{pid}/     Farfetch
/api/basket/v1/                         Farfetch（DocumentedOnly 只有 /api/basket/v1/items，不同串）
/api/checkout/v1/basket/{id}/payment    Farfetch
api.nike.com/buy/carts/v2/...           Nike
/discount/                              StoreFlow
/api/payments/                          StoreFlow
```

**→ 那 6 条不是新的 —— 它们**一直在发**，只是没人记。
→ 所以 `SentCeiling = 10` 是**账的记录**，不是**预算**：调它到 16 不是放宽，而是把已存在的债务记上。**

### ② 而补标注那一步，我的脚本把两个文件改坏了

**脚本用 `if "//" in line` 找注释边界 —— 而 `$"https://..."` 里的 `//` 被当成了注释起点：**

```
改坏后：  $"https:  // inferred: no image evidence (R294)   // api.nike.com/buy/carts/v2/...
```

**→ 那是 R764（花括号计数被字符串里的 `{` 打乱）的**同族错误**。
→ 而 `EveryUnbackedEndpointIsStillInItsFile` 立刻报 `the path is gone` —— 守卫救回来了。**

### ③ 而同一轮还有第二个同族错误：把工具的**截断**当字面量

**工具打印 `.../carts/v2/{...}` —— `{...}` 是**它的截断**，真实是 `{CountryCode}/Nike/SNKRS?format...`。
→ 我照着截断的样子写进账，守卫又说「路径不见了」。
→ 那是 R1016 那个问题的**新位置**：上次是地址列没剥，这次是显示被截断。**

### ④ 所以本轮净改动为零，交付是两个**机械的**前置条件

| 前置条件 | 为什么 |
|---|---|
| **补标注不能用 `//` 找注释边界** | `https://` 里有 `//`；该整行替换或只在行尾注释处切 |
| **账要写**真实**字面量** | 工具显示会截断成 `{...}`；要 `grep` 原文，不抄输出 |

**→ 两条都是机械的，写下之后补账是 20 分钟的事。
→ 而这一轮它们的代价是**三次回滚** —— 因为我在改之前没先把它们写下来。**

### ⑤ 数字

| 度量 | R1031 | **R1032** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（已回滚）** |
| 产物陈旧度 | 5 / 4,199 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **工具的未登记无据端点** | 12 | **12（6 个不同路径）** |
| **真正没有账的路径** | 未算 | **6** |
| **被误算进「12」的已登记项** | 未算 | **3 类（5 处）** |
| **净代码改动** | — | **0（三次回滚）** |

### 教训

> **这一轮我犯了两个「用语法符号找边界」的错，两个都被守卫当场抓住。
> → 共同点：我拿一个**在人写的代码里**成立的规则（`//` 之后是注释），去处理**机器写的内容**（URL、工具输出）。
> → R764 是 `{`，R1016 是地址列，本轮是 `//` —— 三次同形。
> → 所以下次动手前该问：**我用来切分的那个符号，在被切的东西里会不会合法地出现。****
"""

BACKLOG_ADD = """

## 判据 (f) — **账差 6 个路径；而补账脚本用 `//` 找注释边界把 URL 劈开（已回滚）**（R1032）

### 6 个真正没有账的路径

```
/api/ff-products/v1/products/{pid}/     Farfetch
/api/basket/v1/                         Farfetch（DocOnly 只有 /api/basket/v1/items）
/api/checkout/v1/basket/{id}/payment    Farfetch
api.nike.com/buy/carts/v2/...           Nike
/discount/                              StoreFlow
/api/payments/                          StoreFlow
```

**另外 3 类（5 处出现）已登记，被误算进「12」。**
**→ `SentCeiling = 10` 是**账的记录**不是预算；调 16 是把已存在的债务记上，不是放宽。**

### 两个前置条件（机械的，必须先写下）

| 条件 | 原因 |
|---|---|
| 补标注不能用 `if "//" in line` | `https://` 里的 `//` 会被当注释起点，劈开 URL |
| 账要写**真实**字面量 | 工具显示截断成 `{...}`；要 grep 原文 |

### 而同轮两次回滚都是守卫救的

`EveryUnbackedEndpointIsStillInItsFile` 两次报 `the path is gone` —— 一次因 URL 被劈，一次因抄了截断。

### 数字

**套件 2243/0/0（已回滚）· 陈旧度 5 / 4,199 · 函数数 174,336 · 未登记 12（6 路径）· 真缺口 6 ·
误算 3 类 · 净改动 0**

| 仍 Unknown | |
|---|---|
| 那 6 条是否该继续发（还是像 Nike 那样改报告） | 需先记账再判 |

**纪律**：动手前先问 —— 我用来切分的那个符号，在被切的东西里会不会合法地出现。
"""

BLOCKER = """

---

## 456. **账差 6 个路径；而补账的脚本用 `//` 找注释边界把 URL 劈开**

> R1032。**全部回滚，净改动为零。** 套件 **2243 通过 / 0 失败 / 0 跳过**。

### 一、差在哪儿（精确到路径）

| 路径 | `Sent` | `DocumentedOnly` | 判定 |
|---|---|---|---|
| `/api/checkout/v1/basket/{basketId}` | ✓ | | 已登记 |
| `.../shipping` | ✓ | | 已登记 |
| `.../place-order` | ✓ | | 已登记 |
| **`/api/ff-products/v1/products/{pid}/`** | | | **两边都没有** |
| **`/api/basket/v1/`** | | （只有 `/api/basket/v1/items`，不同串） | **两边都没有** |
| **`.../payment`** | | | **两边都没有** |
| **`api.nike.com/buy/carts/v2/...`** | | | **两边都没有** |
| **`/discount/`** | | | **两边都没有** |
| **`/api/payments/`** | | | **两边都没有** |

**→ 「12 条」里 **6 个路径真的没有账**，另外 3 类（5 处出现）是已登记的。
→ 而那 6 条不是新的 —— 它们**一直在发**，只是没人记。**

### 二、所以 `SentCeiling = 10` 是**账的记录**，不是**预算**

**加 6 条后 `Sent` 有 16 个不同路径 ⇒ 上限调到 16。
→ 那**不是放宽**：`SentCeiling` 记的是「已经存在的无据债务」，
→ 「防增长」的意思是**别再冒出第七条**，不是「这六条不能存在」。**

### 三、而补标注那一步，我的脚本把两个文件改坏了

**棘轮要求：每一条**真的用到**那个路径的行都要带 `inferred: no image evidence`。
→ 我写脚本去补，而它用 `if "//" in line` 找注释边界。**

**→ 而 `$"https://api.nike.com/buy/carts/v2/..."` 里的 `//` 被当成了注释起点：
→ 那一行被劈成 `$"https:` + 我的标注 + 剩下的 URL。**

```
改坏后：  $"https:  // inferred: no image evidence (R294)   // api.nike.com/buy/carts/v2/{CountryCode}/...
```

**→ 而那是 AGENTS 里 R764 那条（花括号计数被字符串里的 `{` 打乱）的**同族错误**：
  用 `//` 找注释边界，撞上 URL 里的 `//`。**

**→ 而 `EveryUnbackedEndpointIsStillInItsFile` 立刻报了 `the path is gone` ——
  守卫在这一步是救回来的那一个。**

### 四、而同一轮里还有第二个同族错误：把工具的**截断**当成了字面量

**工具打印的是 `https://api.nike.com/buy/carts/v2/{...}` —— 那个 `{...}` 是**工具自己的截断**，
  而真实字面量是 `https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format...`。**

**→ 我照着截断后的样子写进 `Sent`，于是守卫又说「路径不见了」。
→ 那是 R1016 那个问题的**新位置**：上次是地址列没剥，这次是显示被截断。**

### 五、所以本轮**净改动为零**，交付是两个**机械的**前置条件

| 前置条件 | 为什么必须先有 |
|---|---|
| **补标注不能用 `//` 找注释边界** | `https://` 里有 `//`；该整行替换或只在行尾注释处切 |
| **账要写**真实**字面量** | 工具显示会截断成 `{...}`；要 `grep` 原文而不是抄输出 |

**→ 两条都是机械的，写下之后补账是 20 分钟的事。
→ 而这一轮它们的代价是**三次回滚** —— 因为我在**改之前**没有先把它们写下来。**

### 六、数字

| 度量 | R1031 | R1032 |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0（已回滚）** |
| 产物陈旧度 | 5 / 4,199 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **工具的未登记无据端点** | 12 | **12（6 个不同路径）** |
| **真正没有账的路径** | 未算 | **6** |
| **被误算进「12」的已登记项** | 未算 | **3 类（5 处）** |
| **净代码改动** | — | **0（三次回滚）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
git status --short                                   -> 干净
cd replica
python tools/endpoint-provenance.py                  -> 未登记 12 · exit 1
python tools/metrics_report.py -> 完整套件 exit 0    2243 / 0 / 0
```

### 八、仍然 Unknown

- **那 6 条是否该继续发**（还是像 Nike 那样改成报告）：**需先记账再判**。

### 九、教训

**这一轮我犯了两个「用语法符号找边界」的错，而两个都被守卫当场抓住。**

**→ 而它们的共同点是：我拿一个**在人写的代码里**成立的规则（`//` 之后是注释），
  去处理**机器写的内容**（URL、工具输出）。**

**→ 而 R764 那次是 `{`，R1016 那次是地址列 —— 三次的形状相同。
→ 所以下次动手前该问的是：**我用来切分的那个符号，在被切的东西里会不会合法地出现。****
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1032", BLOCKER)
    ensure(RSTATUS, "R1032", BLOCKER)
    ensure(RVERDICT, "第 1032 轮", VERDICT)
    ensure(BACKLOG, "R1032", BACKLOG_ADD)

    note = (
        "\n## R1032 补充 — **账差 6 个路径；补账脚本用 `//` 找注释边界把 URL 劈开（已回滚，净改动 0）**（套件 2243）\n\n"
        "**6 个真正没有账的路径**：`/api/ff-products/v1/products/{pid}/` · `/api/basket/v1/` ·\n"
        "`.../payment` · `api.nike.com/buy/carts/v2/...` · `/discount/` · `/api/payments/`。\n"
        "另外 3 类（5 处）已登记，被误算进「12」。\n"
        "→ **`SentCeiling = 10` 是**账的记录**不是预算**；调 16 是把已存在的债务记上。\n\n"
        "**两个前置条件（必须先写下再动手）**：\n"
        "1. 补标注**不能**用 `if \"//\" in line` 找注释边界 —— `https://` 里的 `//` 会被当注释起点，劈开 URL（本轮实测）。\n"
        "2. 账要写**真实**字面量 —— 工具显示截断成 `{...}`，要 grep 原文（R1016 的新位置）。\n\n"
        "**两次回滚都是守卫救的**：`EveryUnbackedEndpointIsStillInItsFile` 两次报 `the path is gone`。\n\n"
        "数字：套件 2243/0/0（已回滚）· 陈旧度 5 / 4,199 · 函数数 174,336 · 未登记 12（6 路径）· 真缺口 6 · 净改动 **0**。\n\n"
        "纪律：**动手前先问 —— 我用来切分的那个符号，在被切的东西里会不会合法地出现。**\n\n"
        "下一轮：按那两条前置条件补账（6 条 + 相应标注），再判那 6 条该发还是该改报告。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1032" not in h:
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
             for p, k in ((RBLOCK, "R1032"), (RSTATUS, "R1032"), (RVERDICT, "第 1032 轮"), (BACKLOG, "R1032")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1032: the ledger is six paths short, and the script meant to fix it split a URL in half\n\n"
         "R1031 asked which of the twelve unregistered endpoints were in neither ledger. Reconciling them gives a\n"
         " sharper answer than the number suggested: the twelve occurrences reduce to six distinct paths, three of them\n"
         " are already recorded, and six are genuinely absent. Those six are not new -- every one was being sent before\n"
         " this round -- so SentCeiling at ten was a record of what someone had counted, not a budget, and moving it to\n"
         " sixteen books existing debt rather than relaxing a rule.\n\n"
         "Fixing it went wrong twice, and both times a guard caught it.\n\n"
         "The first: the ratchet requires every line that actually uses an unbacked path to carry the annotation, so I\n"
         " wrote a pass that found the comment boundary with a substring search for two slashes. In an interpolated URL\n"
         " string that search lands on the slashes inside https, and the line came out as a scheme, a comment, and the\n"
         " reste of the URL. StillInItsFile reported the path gone immediately.\n\n"
         "The second: the provenance tool prints paths with a brace-truncated tail, and I copied that display into the\n"
         " ledger instead of the literal it stands for. StillInItsFile caught that too.\n\n"
         "Both are the same mistake as R764's, where counting braces ran into a brace inside a string, and as R1016's,\n"
         " where a column was not stripped before comparing. In each case I applied a rule that holds in hand-written\n"
         " code to content a machine produced: a comment marker, a display ellipsis, an address column.\n\n"
         "So the round ends with no net change and two mechanical preconditions written down: do not find comment\n"
         " boundaries by searching for slashes, and record literals rather than printed approximations. With those two\n"
         " in hand the reconciliation is small work. Without them it cost three reverts, because I started editing\n"
         " before I had written them down.\n\n"
         "Figures: suite 2243 unchanged after the reverts, freshness five files and 4,199 lines, count 174,336, twelve\n"
         " unregistered occurrences resolving to six paths, and no net code change.\n\n"
         "Unknown: whether those six should keep being sent or become reports like Nike's.\n\n"
         "The lesson is to ask, before splitting anything, whether the symbol I am splitting on can legally appear\n"
         " inside the thing I am splitting.\n\n"
         "No net code change; suite green at 2243."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()