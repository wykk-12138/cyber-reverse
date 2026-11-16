"""Record R900: 27 of 154 paths had a prefix the earlier scans dropped."""

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
### R892–R896 的覆盖数**低报最多 27 条** —— 前缀被扫描模式截掉了（R900）

**R899 留下的问题：`/api` 这层是不是别的站也有？**

### 答案：不止 `/api`，共 **27 / 154 条（17.5%）**在族前面还有前缀

**那 27 条正是 R893–R896 会截断的 —— 那些轮把「去掉前缀的路径」拿去与复刻件比，
所以即便复刻件有完整形式也会算成缺。**

| 前缀 | 路径数 |
|---|---|
| **`/api`** | **8** |
| `/payment` | 4 |
| `/payment-authentication` | 4 |
| `/web2` | 3 |
| `/merchants` | 2 |
| `/prod` | 2 |
| `/epayment` · `/forms` · `/data` · `/gs` 等 | 各 1 |

**样例（宿主 / 完整路径）：**

```
api.braintreegateway.com   /merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_me…
api.nike.com               /payment/deferred_payment_forms/v1/jobs
api.vipps.no               /epayment/internal/v1/card-page/Payments
payments.bigcommerce.com   /api/public/v1/orders/payments
payments.dickssporting…    /prod/api/paygate/v2/authorization
auth.casio-intl.com        /api/connect/v1/login
```

### 所以 R895 的 55/171 低报

**低报量最多 27 —— 而这 27 条里有多少是复刻件其实有的，还没算。
要算它得用完整路径重新对一遍。**

**而 Vans 那 6 条正是这 27 里的一部分 —— R899 修的只是它们，其余 21 条还没修。**

### 两个人口不同，不能直接比

| 扫描 | 路径数 | 代价 |
|---|---|---|
| R895（族内匹配） | 171 | **27 条被截断** |
| R900（全路径匹配） | 154 | **人口更小，因为去重方式不同** |

**所以 55/171 与 49/154 不是同一个度量在两个时点，而是两个不同的度量。
要一个可比的数，得先用**同一个**提取法跑一遍，而那还没做。**

### 一条要写完的教训

**同一个扫描模式在四轮里给出了四个数（40 族缺失、32 族缺失、17/45、55/171），
而它每一轮都在做同一件事：在 `/x/vN/` 这个地标处开始匹配。**

**地标匹配方便、好读、看起来对准了 API 的形状 —— 而它**默认前缀不存在**。
这个默认在 `/shop/v1/` 和 `/activity/v1/` 那些站上恰好成立，在 `/api/cart/v2/` 上不成立。**
"""

if "R892–R896 的覆盖数**低报最多 27 条**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R900 appended")

BLOCKER = """

---

## 324. 27 / 154 条路径有族前缀，被 R892–R896 截掉 —— 覆盖数低报

> R900。未改产品代码。

### 一、答案

**R899 问「`/api` 这层是不是别的站也有」。答：不止 `/api`，共 **27 条（17.5%）**在族前面还有前缀。**

| 前缀 | 条数 |
|---|---|
| **`/api`** | **8** |
| `/payment` | 4 |
| `/payment-authentication` | 4 |
| `/web2` | 3 |
| `/merchants` · `/prod` | 各 2 |
| `/epayment` · `/forms` · `/data` · `/gs` 等 | 各 1 |

### 二、所以 R895 的 55/171 低报最多 27

**那 27 条被截成「无前缀路径」后与复刻件比，即便复刻件有完整形式也算缺。**

**Vans 那 6 条是其中一部分 —— R899 修了它们，其余 21 条还没修。**

### 三、而两个人口不同，不能直接比

| 扫描 | 路径数 | 代价 |
|---|---|---|
| R895（族内匹配） | 171 | 27 条截断 |
| R900（全路径匹配） | 154 | 人口更小，去重方式不同 |

**55/171 与 49/154 不是同一个度量在两个时点，是两个不同的度量。
要可比的数得用**同一个**提取法重跑 —— 还没做。**

### 四、一个模式，四轮四个数

**R892 的 40 族缺失 · R893 的 32 族缺失 · R894 的 17/45 · R895 的 55/171 ——
四轮都在 `/x/vN/` 这个地标处开始匹配。**

**地标匹配方便、好读、看起来对准了 API 形状 —— 而它**默认前缀不存在**。
这个默认在 `/shop/v1/`、`/activity/v1/` 上成立，在 `/api/cart/v2/` 上不成立。**

### 五、验证

```
全路径匹配（fullpaths.py）            -> 154 条 / 29 宿主
排除宿主段后第一段分布                -> /shop 41 · /api 38 · /bff 11 …
族前有前缀的路径                      -> 27（/api 8 · /payment 4 · /payment-authentication 4 · …）
逐字命中复刻件                        -> 49 / 154
本轮未改产品代码；套件沿用 1790
```

### 六、仍然 Unknown

- **那 27 条里复刻件其实有完整形式的有几条**：**Unknown** —— 要用同一提取法重跑。
- **两个扫描为什么人口不同（154 vs 171）**：**Unknown** ——
  **去重粒度不同：族内扫描按族+路径去重，全路径扫描按宿主+路径去重。哪一个才是「正确」的人口，取决于要回答什么问题。**
- **还有没有别的截断类型**：**Unknown** —— **这轮只查了「族前缀」，可能还有后缀（`.html`、`?query`）被截。**

### 七、教训

**同一件事我用一个模式量了四轮，得到四个数：40、32、17/45、55/171。**

**四次我都写下了「这是第 N 轮的准确值」。而那个模式有一个默认前提 —— 路径从 `/x/vN/` 开始 ——
我从没检查过它。**

**R764 立的规矩是「扫之前先问：这个东西有几种写法」。这一轮的版本更基本：
**扫之前先问：我的模式假设了什么结构，而那个假设能不能被证伪？**

**能证伪的问法是：找一条**有前缀**的路径。找不到才说明假设成立。
而 `grep 'vans.com.*cart/v2'` 一条就推翻了它。**
"""

VERDICT = """

---

## 第 900 轮：27 / 154 条路径有族前缀，被 R892–R896 截掉

### 答案

**R899 问「`/api` 这层是不是别的站也有」。答：不止 `/api`，共 **27 条（17.5%）**在族前还有前缀。**

| 前缀 | 条数 |
|---|---|
| **`/api`** | **8** |
| `/payment` | 4 |
| `/payment-authentication` | 4 |
| `/web2` | 3 |
| `/merchants` · `/prod` | 各 2 |
| `/epayment` · `/forms` · `/data` · `/gs` 等 | 各 1 |

### 所以 R895 的 55/171 低报最多 27

**Vans 那 6 条是其中一部分 —— R899 修了它们，其余 21 条还没修。**

### 两个人口不同，不能直接比

| 扫描 | 路径数 | 代价 |
|---|---|---|
| R895（族内匹配） | 171 | **27 条截断** |
| R900（全路径匹配） | 154 | 人口更小，去重方式不同 |

> **55/171 与 49/154 不是同一个度量在两个时点，是两个不同的度量。要可比的数得用**同一个**提取法重跑。**

### 一个模式，四轮四个数

**R892 的 40 族缺失 · R893 的 32 族缺失 · R894 的 17/45 · R895 的 55/171 ——
四轮都在 `/x/vN/` 这个地标处开始匹配。**

> **地标匹配方便、好读、看起来对准了 API 形状 —— 而它**默认前缀不存在**。
> 这个默认在 `/shop/v1/`、`/activity/v1/` 上成立，在 `/api/cart/v2/` 上不成立。**

### 仍然 Unknown

**那 27 条里复刻件其实有完整形式的有几条**（要用同一提取法重跑）·
**两个扫描为什么人口不同**（去重粒度：族+路径 vs 宿主+路径）· **还有没有别的截断类型**（**只查了前缀，后缀未查**）

### 教训

> **同一件事我用一个模式量了四轮，得到四个数。四次我都写下了「这是第 N 轮的准确值」。
> 而那个模式有一个默认前提 —— 路径从 `/x/vN/` 开始 —— 我从没检查过它。**
> **R764 立的规矩是「扫之前先问：这个东西有几种写法」。这一轮的版本更基本：
> **扫之前先问：我的模式假设了什么结构，而那个假设能不能被证伪？**
> 能证伪的问法是：找一条**有前缀**的路径。找不到才说明假设成立。
> 而 `grep 'vans.com.*cart/v2'` 一条就推翻了它。**
"""

BACKLOG_ADD = """

## 判据 — **27 / 154** 条路径有族前缀，R892–R896 低报（R900）

### 前缀分布

**`/api` 8 · `/payment` 4 · `/payment-authentication` 4 · `/web2` 3 · `/merchants` 2 · `/prod` 2 · 其余 5 个各 1**

**→ 那 27 条被截成无前缀路径后与复刻件比，即便有完整形式也算缺 → R895 的 55/171 **低报最多 27**。**
**Vans 那 6 条是其一，**其余 21 条未修**。**

### 两个人口不同

| 扫描 | 路径数 | 代价 |
|---|---|---|
| R895（族内） | 171 | **27 条截断** |
| R900（全路径） | 154 | 人口更小 |

**55/171 与 49/154 是两个不同度量，不是同一测度两时点。**

### 一个模式四轮四个数

**40 族缺失（R892）· 32（R893）· 17/45（R894）· 55/171（R895）—— 都在 `/x/vN/` 地标处匹配。**
**→ 地标匹配**默认前缀不存在**；在 `/shop/v1/` 成立，在 `/api/cart/v2/` 不成立。**

| 仍 Unknown | |
|---|---|
| 27 条里复刻件已有完整形式几条 | 需同一提取法重跑 |
| 两扫描人口为何不同 | 去重粒度：族+路径 vs 宿主+路径 |
| 还有别的截断类型吗 | **后缀（.html / ?query）未查** |

**纪律**：**扫之前问「我的模式假设了什么结构，那个假设能否被证伪」—— 找一条反例就够，`grep 'vans.com.*cart/v2'` 一条即推翻。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R900", BLOCKER)
    ensure(RSTATUS, "R900", BLOCKER)
    ensure(RVERDICT, "第 900 轮", VERDICT)
    ensure(BACKLOG, "R900", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R900" not in h:
        h += ("\n## R900 补充 — **27 / 154** 条路径有族前缀，R892–R896 低报（**未改产品代码**）\n\n"
              "**前缀分布**：`/api` 8 · `/payment` 4 · `/payment-authentication` 4 · `/web2` 3 · `/merchants` 2 · `/prod` 2 · 其余各 1。\n"
              "**→ R895 的 55/171 低报最多 27**；**Vans 那 6 条只是其一，其余 21 条未修**。\n"
              "**两个人口不同**（171 vs 154，去重粒度不同）→ **不能用同一测度两时点来读**。\n"
              "**一个模式四轮四个数**（40 / 32 / 17-45 / 55-171）—— 都在 `/x/vN/` 地标处匹配，**而地标匹配默认前缀不存在**。\n"
              "**纪律：扫之前问「我的模式假设了什么结构，那个假设能否被证伪」；找一条反例就够。**\n"
              "**下一轮**：用同一提取法重跑覆盖率，得到可比的数；查后缀截断。\n")
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
             for p, k in ((RBLOCK, "R900"), (RSTATUS, "R900"), (RVERDICT, "第 900 轮"), (BACKLOG, "R900")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R900: twenty-seven of a hundred and fifty-four paths had a prefix the earlier scans dropped\n\n"
         "R899 asked whether the api layer exists on other stores' paths too, and whether that means the coverage\n"
         " figures from R892 through R896 under-report. It does, and this round bounds the effect at twenty-seven paths\n"
         " out of a hundred and fifty-four, seventeen and a half percent.\n\n"
         "The prefixes are api with eight, payment and payment-authentication with four each, web2 with three,\n"
         " merchants and prod with two each, and five singletons. Those twenty-seven are exactly the paths whose family\n"
         " segments the earlier scans anchored on, so the comparison ran a prefix-less path against the replica and\n"
         " counted it missing even where the replica holds the full form. Vans's six were part of that twenty-seven;\n"
         " R899 fixed them and twenty-one remain.\n\n"
         "The two scans also produce different populations, a hundred and seventy-one against a hundred and fifty-four,\n"
         " because they deduplicate differently -- by family and path in one, by host and path in the other. So\n"
         " fifty-five of a hundred and seventy-one and forty-nine of a hundred and fifty-four are not the same measure\n"
         " at two times; they are two measures. A comparable figure needs one canonical extraction, which has not been\n"
         " done.\n\n"
         "What makes this worth recording at length is that one scanning decision produced four numbers across four\n"
         " rounds -- forty families absent, thirty-two absent, seventeen of forty-five, fifty-five of a hundred and\n"
         " seventy-one -- and each round presented its figure as the accurate one. The decision was to match at the\n"
         " /segment/vN/ landmark. That is convenient, readable, and looks like it targets API shapes, and it silently\n"
         " assumes no prefix exists. The assumption happens to hold for shop/v1 and activity/v1 and fails for\n"
         " api/cart/v2.\n\n"
         "Unknown: how many of the twenty-seven the replica in fact holds in full form, which needs the canonical\n"
         " extraction; why the two scans' populations differ, beyond the deduplication guess; and whether other kinds\n"
         " of truncation exist, since this round checked prefixes and not suffixes such as an .html tail or a query\n"
         " string.\n\n"
         "The lesson sharpens R764's rule. That one said to ask how many shapes a thing takes before scanning. This\n"
         " round's version is more basic: ask what structure the pattern assumes, and whether that assumption can be\n"
         " falsified. The falsifying test here is to look for a single path that carries a prefix -- one grep for a\n"
         " vans host followed by a cart path would have overturned it.\n\n"
         "No product code changed; suite carries at 1790."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
