"""Record R895: the upper bound replaced by an exact per-path count."""

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
### 逐条算准：**55 / 171 条路径**（32.2%）—— 上界换成精确值（R895）

**R894 报 17/45 族，并说「17 是上界，族段太泛可能误命中」。这一轮按路径逐条对，把它算准。**

### 判据（两种存储形式都认）

| 形式 | 判据 |
|---|---|
| **whole** | 整条路径作为字面量出现 |
| **tail** | 去掉族前缀的尾部作为字面量出现（`Base + "v2/orders"`） |
| **missing** | 两者都不是 |

### 结果

| | |
|---|---|
| 有宿主的族下的路径 | **171** |
| **whole** | **47** |
| **tail** | **8** |
| **missing** | **116** |
| **合计有** | **55（32.2%）** |

### 两个分母，两个数

| 度量 | 值 |
|---|---|
| 族级（R894） | **17 / 45 = 37.8%** |
| **路径级（本轮）** | **55 / 171 = 32.2%** |

**两个数不同，而**不是**谁错了：族级问「这个族有没有被提到」，路径级问「这个族下的每条有没有」。

**一个族里提到 1 条，族级算「有」，路径级算 1/N。**

**所以：族级高估覆盖率。**17/45** 读起来像「三分之一的端点有了」，而按路径是 **32.2%**，
且那 17 个族里有 12 个只提到了一部分。**

### 而这修正了 R894 的一个说法

**R894 说「17 是上界」—— 那是把**族级**当路径级的判断。**

**按族级它其实不是上界：判据是「族段出现」，而族段出现确实意味着这个族有东西，族级 17 是准的。
问题在于**族级本身不是覆盖率**，因为它给「提到 1 条」和「提到全部」同样的分。**

**所以真正要修的不是松紧，是**分母**。**
"""

if "逐条算准：**55 / 171 条路径**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R895 appended")

BLOCKER = """

---

## 319. 逐条算准 **55 / 171**（32.2%），而族级的 17/45 高估了覆盖率

> R895。未改产品代码。

### 一、判据

| 形式 | 判据 |
|---|---|
| **whole** | 整条路径是字面量 |
| **tail** | 去掉族前缀的尾部是字面量（`Base + "v2/orders"`） |
| **missing** | 两者都不是 |

### 二、结果

| | |
|---|---|
| 有宿主的族下的路径 | **171** |
| whole | **47** |
| tail | **8** |
| **missing** | **116** |
| **有** | **55（32.2%）** |

### 三、两个分母，而族级高估

| 度量 | 值 |
|---|---|
| 族级（R894） | 17 / 45 = **37.8%** |
| **路径级（本轮）** | **55 / 171 = 32.2%** |

**两个数不同，不是谁错了 —— 它们回答不同的问题。**
**族级问「这个族有没有被提到」；路径级问「这个族下每条有没有」。**

**一个族提到 1 条，族级给「有」，路径级给 1/N。**

**所以族级 17/45 读起来像「三分之一端点有了」，而按路径是 32.2%，
且那 17 个族里多数只提到了一部分。**

### 四、而 R894 的「17 是上界」这句话本身要修

**R894 把「族段太泛可能误命中」当成了 17 的松紧问题。这一轮发现那不是主要问题。**

**族级 17 是准的（判据是族段出现，出现就意味着有东西）。问题是**族级不是覆盖率** ——
它给「提到 1 条」和「提到全部」同样的分。**

**所以真正要改的不是判据松紧，是**分母**：报覆盖率要用路径级，族级只能用来数「涉及了几个族」。**

### 五、验证

```
exactpaths.py（IDA 侧）  -> 45 族带宿主，族下共 171 条路径
exactdiff.py             -> whole 47 / tail 8 / missing 116 / covered 55（32.2%）
族级对照（R894）          -> 17 / 45（37.8%）
本轮未改产品代码；套件沿用 1783
```

### 六、仍然 Unknown

- **那 116 条缺失里有多少是「站点本来就不需要」**：**Unknown** ——
  **比如 `_jobs` 族的路径（`checkout_previews_jobs`、`partner_cart_preorder_jobs`）可能是异步轮询的副本，
  复刻件用一个循环就能覆盖，不必逐条有常量。**
- **tail 那 8 条是不是真的对**：**Unknown** ——
  **尾部匹配比整路径松（`"v2/orders"` 这种也可能命中别的 base）。**
- **171 条里有多少属于支付商而非站**：**Unknown** ——
  **混着算让 32.2% 这个数含义不清，与 R894 的同一个问题。**

### 七、教训

**R894 我担心的是判据太松，于是说「17 是上界」。这一轮发现真问题是分母太小。**

**「上界/下界」是关于**同一个度量的精度**；而这次要换的是**度量本身**。**

**两件事我混在一起说了。而区分它们的方法很简单：**
**问「如果我把它算准，数字会变吗」——会变的是精度问题；问「如果我把分母换掉，数字会变吗」——会变的是定义问题。**

**这一轮两个答案都是「会」，而我只报了第一个。**
"""

VERDICT = """

---

## 第 895 轮：逐条算准 55 / 171（32.2%）—— 族级的 17/45 高估了覆盖率

### 判据

**whole（整条路径字面量）· tail（去掉族前缀的尾部字面量）· missing（两者都不是）**

### 结果

| | |
|---|---|
| 有宿主的族下的路径 | **171** |
| whole | **47** |
| tail | **8** |
| **missing** | **116** |
| **有** | **55（32.2%）** |

### 两个分母

| 度量 | 值 |
|---|---|
| 族级（R894） | 17 / 45 = **37.8%** |
| **路径级（本轮）** | **55 / 171 = 32.2%** |

> **两个数不同，不是谁错了 —— 它们回答不同的问题。
> 族级问「这个族有没有被提到」，路径级问「这个族下每条有没有」。
> 一个族提到 1 条，族级给「有」，路径级给 1/N。**
> **所以 17/45 读起来像「三分之一端点有了」，实际按路径是 32.2%，且那 17 个族里多数只提到了一部分。**

### 而这修正了 R894 的「17 是上界」

**族级 17 本身是准的（族段出现就意味着有东西）。问题是**族级不是覆盖率** ——
它给「提到 1 条」和「提到全部」同样的分。**

> **所以真正要改的不是判据松紧，是**分母**。族级只能用来数「涉及了几个族」。**

### 仍然 Unknown

**116 条缺失里多少是「站点本来不需要」**（如 `_jobs` 族可能是异步轮询副本，一个循环覆盖）·
**tail 那 8 条是不是真对**（尾部匹配比整路径松）·
**171 条里多少属支付商而非站**（**混着算让 32.2% 含义不清，与 R894 同一个问题**）

### 教训

> **R894 我担心判据太松，于是说「17 是上界」。这一轮发现真问题是分母太小。**
> **「上界/下界」是关于**同一个度量的精度**；而这次要换的是**度量本身**。两件事我混在一起说了。**
> **区分方法很简单：问「算准它数字会变吗」是精度问题；问「换掉分母数字会变吗」是定义问题。
> 这一轮两个答案都是「会」，而我只报了第一个。**
"""

BACKLOG_ADD = """

## 判据 — 路径级 **55 / 171**（32.2%），族级 17/45 高估（R895）

### 判据三态

**whole（整条字面量）· tail（去掉族前缀的尾部字面量）· missing**

| | |
|---|---|
| 有宿主的族下的路径 | **171** |
| whole | 47 |
| tail | 8 |
| **missing** | **116** |
| **有** | **55（32.2%）** |

### 两个分母

| 度量 | 值 |
|---|---|
| 族级（R894） | 17/45 = 37.8% |
| **路径级（R895）** | **55/171 = 32.2%** |

**族级问「族有没有被提到」，路径级问「族下每条有没有」。提到 1 条，族级给满分。**

### 修正 R894 的「17 是上界」

**族级 17 是准的；问题是**族级不是覆盖率** —— 真问题不是判据松紧，是**分母**。**
**→ 族级只能用来数「涉及几个族」；报覆盖率用路径级。**

| 仍 Unknown | |
|---|---|
| 116 条缺失里多少「本来不需要」 | `_jobs` 族可能是轮询副本 |
| tail 那 8 条对否 | 尾部匹配比整路径松 |
| 171 里多少属支付商 | **混着算让 32.2% 含义不清** |

**纪律**：**「算准它会变吗」= 精度问题；「换分母它会变吗」= 定义问题。别只报第一个。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R895", BLOCKER)
    ensure(RSTATUS, "R895", BLOCKER)
    ensure(RVERDICT, "第 895 轮", VERDICT)
    ensure(BACKLOG, "R895", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R895" not in h:
        h += ("\n## R895 补充 — 路径级 **55 / 171（32.2%）**（**未改产品代码**）\n\n"
              "**判据三态**：whole（整条字面量）47 · tail（去族前缀的尾部字面量）8 · **missing 116** · **有 55（32.2%）**。\n"
              "**两个分母**：族级 17/45 = 37.8% vs **路径级 55/171 = 32.2%**。**族级问「族有没有被提到」，路径级问「族下每条有没有」→ 提到 1 条族级给满分 → 族级高估覆盖率。**\n"
              "**修正 R894**：族级 17 本身准；真问题不是判据松紧，是**分母**。**族级只用来数「涉及几个族」，覆盖率用路径级。**\n"
              "**纪律**：「算准它会变吗」= 精度问题；「换分母它会变吗」= 定义问题 —— 别只报第一个。\n"
              "**下一轮**：116 条缺失里多少「本来不需要」（`_jobs` 族可能是轮询副本）；171 里多少属支付商。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R895"), (RSTATUS, "R895"), (RVERDICT, "第 895 轮"), (BACKLOG, "R895")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R895: fifty-five of a hundred and seventy-one paths, and the family-level figure was the wrong denominator\n\n"
         "R894 reported seventeen of forty-five families and called that an upper bound, on the worry that generic\n"
         " segments like api/v1 could match unrelated code. This round counted per path instead, accepting both known\n"
         " storage forms: a whole path as a literal, or a base plus a tail.\n\n"
         "Under the forty-five host-attributed families the image names a hundred and seventy-one paths. Forty-seven\n"
         " appear whole, eight appear as tails, and a hundred and sixteen appear in neither form, so fifty-five are\n"
         " covered -- thirty-two point two percent.\n\n"
         "The family figure and the path figure are not in conflict. They answer different questions: whether a family\n"
         " is mentioned at all, and whether each of its paths is. One mention in a family of six scores the family as\n"
         " present and one sixth of the paths. So seventeen of forty-five reads like a third of the endpoint surface\n"
         " when the path figure is under a third, and most of those seventeen families are only partly there.\n\n"
         "That also corrects what I said last round. Calling seventeen an upper bound framed the problem as looseness\n"
         " in the criterion, and the criterion is fine: a family segment appearing does mean that family has something.\n"
         " What is wrong is the denominator. A family count answers how many families are touched, not how much of them.\n"
         " So the remedy is not a tighter test but a different divisor, and family counts should be reported as reach\n"
         " rather than as coverage.\n\n"
         "Unknown: how many of the hundred and sixteen missing paths are ones the store does not need, since the _jobs\n"
         " families look like asynchronous polling duplicates that one loop would cover rather than needing a constant\n"
         " each; whether the eight tail matches are genuine, since tail matching is looser than whole-path matching and\n"
         " v2/orders could sit under a different base; and how many of the hundred and seventy-one belong to payment\n"
         " providers rather than stores, which is the same mixing problem R894 flagged and which leaves thirty-two point\n"
         " two percent with an unclear meaning.\n\n"
         "The lesson separates two things I had run together. Whether a figure gets more precise, and whether its\n"
         " divisor changes, are different questions with different remedies, and I reported only the first last round\n"
         " when both applied.\n\n"
         "No product code changed; suite carries at 1783."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
