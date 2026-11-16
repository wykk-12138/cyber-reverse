"""Record R894: the per-host coverage table, 17 of 45, with the false-positive caveat."""

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
### 按宿主的覆盖：**17 / 45**，而分布比总数有用（R894）

**R893 给了族↔宿主表。这一轮加上「复刻件有没有」这一列。**

### 总数

| | |
|---|---|
| 有宿主的族 | **45** |
| 复刻件有 | **17** |
| 复刻件无 | **28** |

### 而按宿主看才有信息

| 宿主 | 有/共 | 读法 |
|---|---|---|
| **`api.nike.com`** | **11/11** | **Nike 全覆盖** |
| `checkout.johnlewis.com` | 1/4 | 只有 `bff/v2` |
| `checkoutshopper-live.adyen.com` | 1/2 | 缺 `paybylink/v1` |
| `id.asics.com` · `www.goat.com` · `www.nike.com` · `inbox-api.aycd.io` | 各 1/1 | 单族，齐 |
| **`www.vans.com`** | **0/3** | **`cart/v1` · `cart/v2` · `products/v2` 全缺** |
| **`challenges.cloudflare.com`** | **0/1** | **Turnstile 端点缺** |
| **`prod-hk-actapi.popmart.com`** | **0/1** | **`/activity/v1/` 缺** |
| 其余 18 个宿主 | 各 0/1 | 全是支付商或基础设施 |

### 三条具体结论

1. **Nike 的 11 个族全在复刻件里** —— 这是第一个能说「这个站端点层齐了」的站。
2. **Vans 的 3 个族一个没有** —— 而 R762 说复刻件有 62 个店模块。**所以 Vans 的模块在，端点不在。**
3. **`www.ibm.com` + `/dtd/v11/` 也在 0/1 里** —— 而 R893 就怀疑它是误收的字符串。

### 一个必须说的告诫

**「有」的判据是「族段（如 `api/v1`、`bff/v2`）在源码里出现」。**

**而 `api/v1`、`api/v2`、`bff/v2` 这种段太泛 —— 可能命中**不相关的代码**。**

**所以 17 这个数是**上界**，不是精确值。要精确得按宿主把每条路径都对一遍，
而那是 45 × 平均 2 条 = 约 100 次对比。这一轮没做。**

**这正是 R892 那个错的另一面：R892 因为判据太严高报缺口（40 vs 32），
这一轮因为判据太松可能低报缺口（17 可能是 14）。**
"""

if "按宿主的覆盖：**17 / 45**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R894 appended")

BLOCKER = """

---

## 318. 按宿主覆盖 **17 / 45**：Nike 齐、Vans 全缺、Turnstile 缺

> R894。未改产品代码。

### 一、总数与分布

| | |
|---|---|
| 有宿主的族 | **45** |
| 复刻件有 | **17**（**上界，见下**） |
| 复刻件无 | **28** |

| 宿主 | 有/共 |
|---|---|
| **`api.nike.com`** | **11/11** |
| `checkout.johnlewis.com` | 1/4 |
| `checkoutshopper-live.adyen.com` | 1/2 |
| `id.asics.com` · `www.goat.com` · `www.nike.com` · `inbox-api.aycd.io` | 各 1/1 |
| **`www.vans.com`** | **0/3** |
| **`challenges.cloudflare.com`** | **0/1** |
| **`prod-hk-actapi.popmart.com`** | **0/1** |
| 其余 18 个 | 各 0/1 |

### 二、三条具体结论

1. **Nike 11/11** —— 第一个能说「端点层齐了」的站。
2. **Vans 0/3** —— 而 R762 说复刻件有 62 个店模块。**所以 Vans 的模块在、端点不在。**
   **这是一处「模块存在但无端点」的具体证据，比「32 个族完全没有」精确。**
3. **`www.ibm.com` + `/dtd/v11/` 也在 0 里** —— R893 就怀疑它是误收的字符串。

### 三、17 是上界，不是精确值

**判据是「族段（`api/v1`、`bff/v2`）在源码里出现」，而这些段太泛，可能命中不相关的代码。**

**所以真实值可能低于 17。要精确得按宿主逐条对比约 100 次 —— 这一轮没做。**

> **R892 的判据太严，高报缺口（40 vs 32）；这一轮的判据太松，可能低报缺口。**
> **两个方向同一个来源：判据里的松紧度数没有标定。**

### 四、验证

```
famhost2.py（IDA 侧）       -> 45 族带宿主
cov.py                      -> 45 有宿主 / 17 有 / 28 无
按 HOST 分组                -> 见上表
本轮未改产品代码；套件沿用 1783
```

### 五、仍然 Unknown

- **17 里有多少是泛段误命中**：**Unknown** —— 需要逐条对比，约 100 次。
- **Vans 为什么 3 个族全缺**：**Unknown** ——
  **模块在（`www.vans.com` 是 Demandware 系），而 `cart/v1`、`cart/v2`、`products/v2` 一个都没有。
  可能是 Vans 走的是别的路径族，也可能真的缺。**
- **18 个支付商宿主该不该在表里**：**Unknown** ——
  **`api.braintreegateway.com`、`flex.cybersource.com` 这些不是站，是支付环节。
  它们缺不代表站点缺，而这张表混着算。**

### 六、教训

**这一轮我把「族名出现过」当成「实现了」，而那是松判据。**

**同一件事，R892 我用了严判据（整条字面量）并因此高报。
两次都不是判据本身错，而是**我没写清它是上界还是下界**。**

**所以规矩要补一条：报覆盖数时必须同时写「这个数是上界/下界/精确」，以及它为什么。
没有这句的数，读的人会当成精确值 —— 而我自己下一轮也会。**
"""

VERDICT = """

---

## 第 894 轮：按宿主覆盖 17 / 45 —— Nike 齐、Vans 全缺、Turnstile 缺

### 总数

| | |
|---|---|
| 有宿主的族 | **45** |
| 复刻件有 | **17（上界）** |
| 复刻件无 | **28** |

### 分布才有信息

| 宿主 | 有/共 |
|---|---|
| **`api.nike.com`** | **11/11** |
| `checkout.johnlewis.com` | 1/4 |
| `checkoutshopper-live.adyen.com` | 1/2 |
| `id.asics.com` · `www.goat.com` · `www.nike.com` · `inbox-api.aycd.io` | 各 1/1 |
| **`www.vans.com`** | **0/3** |
| **`challenges.cloudflare.com`** | **0/1** |
| **`prod-hk-actapi.popmart.com`** | **0/1** |
| 其余 18 个（支付商与基础设施） | 各 0/1 |

### 三条具体结论

1. **Nike 11/11** —— 第一个能说「端点层齐了」的站
2. **Vans 0/3** —— 而 R762 说复刻件有 62 个店模块。**模块在、端点不在** —— 这比「32 个族完全没有」精确
3. **`www.ibm.com` + `/dtd/v11/` 也在 0 里** —— R893 就怀疑是误收的字符串

### 17 是上界，必须这么说

**判据是「族段（`api/v1`、`bff/v2`）在源码里出现」，段太泛可能误命中。真实值可能低于 17。**

> **R892 判据太严高报（40 vs 32）；这一轮太松可能低报。两个方向同一个来源：判据的松紧没标定。**

### 仍然 Unknown

**17 里多少是泛段误命中**（需逐条约 100 次对比）· **Vans 为何 3 族全缺**（模块在，可能走别的族）·
**18 个支付商宿主该不该算进覆盖率**（它们缺不代表站点缺，表里混着算）

### 教训

> **同一件事，R892 用严判据高报，这一轮用松判据可能低报。两次都不是判据错，而是**我没写清它是上界还是下界**。**
> **规矩要补一条：报覆盖数时必须同时写「上界/下界/精确」以及为什么 —— 没有这句的数，读的人会当成精确值，而我自己下一轮也会。**
"""

BACKLOG_ADD = """

## 判据 — 按宿主覆盖 **17 / 45**（R894）

### 总数与分布

| | |
|---|---|
| 有宿主的族 | **45** |
| 复刻件有 | **17（上界）** |
| 复刻件无 | **28** |

| 宿主 | 有/共 |
|---|---|
| **`api.nike.com`** | **11/11** |
| `checkout.johnlewis.com` | 1/4 |
| `checkoutshopper-live.adyen.com` | 1/2 |
| `id.asics.com` · `www.goat.com` · `www.nike.com` · `inbox-api.aycd.io` | 各 1/1 |
| **`www.vans.com`** | **0/3** |
| **`challenges.cloudflare.com`** | **0/1** |
| **`prod-hk-actapi.popmart.com`** | **0/1** |
| 其余 18 个（支付商/基础设施） | 各 0/1 |

### 三条结论

**① Nike 11/11 = 首个端点层齐的站**
**② Vans 0/3，而模块在（62 个店模块）→ 「模块在、端点不在」，比「32 族完全没有」精确**
**③ `www.ibm.com` + `/dtd/v11/` 也在 0 里 → R893 的误收怀疑**

### 17 是**上界**

**判据「族段（`api/v1`、`bff/v2`）出现过」太松，可能误命中。真实值可能 < 17。**

> **R892 太严高报（40 vs 32）；本轮太松可能低报。同一来源：松紧未标定。**
> **新规矩：报覆盖数必须写「上界/下界/精确」+ 理由。**

| 仍 Unknown | |
|---|---|
| 17 里多少是泛段误命中 | 需逐条约 100 次 |
| Vans 为何 3 族全缺 | 模块在，可能走别的族 |
| 18 个支付商宿主该不该算 | 缺不代表站点缺，混着算了 |

**纪律**：**报覆盖数必须带「上界/下界/精确」，否则读的人（包括下一轮的我）会当精确值。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R894", BLOCKER)
    ensure(RSTATUS, "R894", BLOCKER)
    ensure(RVERDICT, "第 894 轮", VERDICT)
    ensure(BACKLOG, "R894", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R894" not in h:
        h += ("\n## R894 补充 — 按宿主覆盖 **17 / 45**（**未改产品代码**）\n\n"
              "**分布**：`api.nike.com` **11/11（首个端点层齐的站）** · `checkout.johnlewis.com` 1/4 · adyen 1/2 · "
              "asics/goat/www.nike/aycd 各 1/1 · **`www.vans.com` 0/3** · **`challenges.cloudflare.com` 0/1** · **`prod-hk-actapi.popmart.com` 0/1** · 其余 18 个支付商各 0/1。\n"
              "**Vans 0/3 而模块在（62 个店模块）→ 「模块在、端点不在」**，比「32 族完全没有」精确。\n"
              "**17 是上界**：判据「族段出现过」太松可能误命中。**R892 太严高报 40 vs 32；本轮太松可能低报 —— 同一来源：松紧未标定。**\n"
              "**新规矩：报覆盖数必须写「上界/下界/精确」+ 理由。**\n"
              "**下一轮**：17 里有多少是泛段误命中（逐条约 100 次对比）；Vans 走的是哪一族。\n")
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
             for p, k in ((RBLOCK, "R894"), (RSTATUS, "R894"), (RVERDICT, "第 894 轮"), (BACKLOG, "R894")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R894: per-host coverage is seventeen of forty-five, and the distribution says more than the total\n\n"
         "R893 mapped families to hosts. This round adds the column that makes the table answer something: whether the\n"
         " replica mentions each family.\n\n"
         "Seventeen of the forty-five host-attributed families appear in the replica and twenty-eight do not. The\n"
         " distribution is where the information is. Nike's api host is eleven of eleven, the first store whose\n"
         " endpoint layer can be called complete. John Lewis is one of four, with only bff/v2 present. Vans is zero of\n"
         " three, and that is the round's most useful single fact: R762 recorded sixty-two store modules in the\n"
         " replica, so Vans has a module and no endpoints. Eighteen further hosts are payment providers and\n"
         " infrastructure, each zero of one, and those absences do not mean a store is missing anything.\n\n"
         "Two of the zeroes bear on the anti-bot priority and on R835. challenges.cloudflare.com holds turnstile/v0\n"
         " and the family is absent, so Turnstile has an endpoint the replica never names. prod-hk-actapi.popmart.com\n"
         " holds activity/v1 and is likewise absent, which is consistent with R893's finding that Pop Mart has two\n"
         " hosts and the replica works only on the other one's prefixes.\n\n"
         "The number needs a qualifier and the qualifier is the round's real lesson. Presence here means the family\n"
         " segment -- api/v1, bff/v2 -- occurs somewhere in the source, and those segments are generic enough to match\n"
         " unrelated code. So seventeen is an upper bound. R892's criterion was too strict and over-reported absence\n"
         " at forty where the truth was thirty-two; this one is too loose and may under-report the gap. Neither\n"
         " criterion was wrong in itself. What was missing both times is a statement of whether the figure is an upper\n"
         " bound, a lower bound, or exact, and why -- so a rule follows: any coverage figure must carry that word, or\n"
         " the next reader, including me next round, will treat it as precise.\n\n"
         "Unknown: how many of the seventeen are generic-segment false positives, which needs about a hundred\n"
         " path-by-path comparisons; why Vans is zero of three given that its module exists, where it may use a\n"
         " different family or may genuinely lack endpoints; and whether the eighteen payment and infrastructure hosts\n"
         " belong in a coverage denominator at all, since their absence says nothing about a store.\n\n"
         "No product code changed; suite carries at 1783."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
