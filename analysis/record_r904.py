"""Record R904: the third state, which surfaced thirteen false negatives."""

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
### 加了个「第三种状态」，浮出 **13 条假阴性**（R904）

**目标：取 `store` 那 52 条缺失清单。**

### 取出来一看，最大的可疑是 John Lewis

**清单里 `checkout.johnlewis.com` 占 11 条。而 `JohnLewisBff` 里它们是 `Base = ".../bff/"` + 相对路径
（`"v2/orders"`）—— **我的逐字匹配看不到。****

**所以这 11 条不是缺，是我的规则看不见。**

### 而 R894 已经因为这个吃过一次

**R894 的教训是「整条字面量」判据太严，高报出 40 族缺失。**

**这次同一个坑**在同一个工具里**又出现一次，因为我把它写成了「verbatim only」并自称那是诚实的默认。**

### 所以加了第三态，而没有放宽规则

| 状态 | 判据 | 含义 |
|---|---|---|
| **verbatim** | 整条路径是字面量 | 复刻件确实有这条 |
| **base-tail** | 去掉族前缀的尾部是字面量 | 复刻件知道这个端点，但它藏在某个 Base 后面 |
| **missing** | 两者都不是 | 真缺 |

**两者都不并入：算成 covered 会高报，算成 missing 会低报，而前面几轮轮流犯过这两种。**

### 数字

| 桶 | verbatim | base-tail | 合计 | 百分比（verbatim） |
|---|---|---|---|---|
| **store** | 3 | **8** | **11 / 55** | 5.5% |
| **vendor** | 0 | **5** | 5 / 32 | 0.0% |
| **hostless** | **67** | 0 | **67 / 67** | **100.0%** |
| **missing** | — | — | **71**（原 84） | — |

**13 条假阴性浮出来：store 8 条 + vendor 5 条。**

### 而 store 的真实覆盖是 11/55 = 20%，不是 5.5%

**verbatim 那 3 条我只敢报 5.5%；加上 base-tail 的 8 条是 20%。**

**而 20% 里有多少是「真的实现」还不确定 —— base-tail 匹配只证明「复刻件里有一段同样的字面量」，
不证明它挂在同一个 Base 下。所以这一列标注为「知道这个端点，形式我确认不了」。**
"""

if "加了个「第三种状态」，浮出 **13 条假阴性**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R904 appended")

VERDICT = """

---

## 第 904 轮：加第三态，浮出 13 条假阴性

### 取清单时发现的问题

**`store` 缺失清单里 `checkout.johnlewis.com` 占 11 条。而 `JohnLewisBff` 里它们是 `Base + "v2/orders"` ——
**我的逐字匹配看不到。**

**所以这 11 条不是缺，是我的规则看不见。而 R894 已经因为同一个坑高报过 40 族缺失。**

### 加第三态，不放宽规则

| 状态 | 判据 | 含义 |
|---|---|---|
| **verbatim** | 整条路径是字面量 | 确实有 |
| **base-tail** | 去掉族前缀的尾部是字面量 | **知道这个端点，但藏在某个 Base 后面** |
| **missing** | 两者都不是 | 真缺 |

> **算成 covered 会高报，算成 missing 会低报 —— 而前面几轮轮流犯过这两种，所以我把它单列。**

### 数字

| 桶 | verbatim | base-tail | 合计 |
|---|---|---|---|
| **store** | 3 | **8** | **11 / 55（20%）** |
| **vendor** | 0 | **5** | 5 / 32（15.6%） |
| **hostless** | **67** | 0 | **67 / 67（100%）** |
| **missing** | — | — | **71**（原 84） |

### 仍然 Unknown

**base-tail 那 13 条是否真的挂在同一个 Base 下**（**尾部匹配只证明「有一段同样的字面量」**）·
**`/shield/v1/verify_otp` 校验什么**（优先级 ②）· **`store` 那 44 条真缺失的清单**

### 教训

> **R894 我学到「整条字面量判据太严」；这一轮在**同一个工具**里又犯一次，因为我把它写成 verbatim only
> 并自称那是诚实的默认。**
> **而「诚实的默认」这个词本身就是信号 —— 它意味着我知道有代价，却把代价藏进了规则而不是报表。**
> **第三种状态才是那个代价该待的地方。**
"""

BACKLOG_ADD = """

## 判据 — 加第三态 `base-tail`，浮出 13 条假阴性（R904，**改工具**）

### 起因

**`store` 缺失清单里 `checkout.johnlewis.com` 占 11 条，而 `JohnLewisBff` 用 `Base + "v2/orders"` 存 —— 逐字匹配看不到。**
**→ 与 R894 同一个坑，在同一个工具里第二次。**

### 三态

| 状态 | 判据 |
|---|---|
| verbatim | 整条路径是字面量 |
| **base-tail** | **去掉族前缀的尾部是字面量**（知道端点，藏在 Base 后面） |
| missing | 两者都不是 |

### 数字

| 桶 | verbatim | base-tail | 合计 |
|---|---|---|---|
| store | 3 | **8** | **11/55 = 20%**（原报 5.5%） |
| vendor | 0 | **5** | 5/32 = 15.6% |
| hostless | **67** | 0 | **67/67 = 100%** |
| **missing** | — | — | **71**（原 84） |

| 仍 Unknown | |
|---|---|
| base-tail 13 条是否同 Base | 尾部匹配只证明「有同样字面量」 |
| `/shield/v1/verify_otp` 校验什么 | 优先级 ② |
| store 44 条真缺失清单 | 下一步 |

**纪律**：**「诚实的默认」这个词是信号 —— 它意味着知道有代价，却把代价藏进规则而非报表。第三种状态才是它该待的地方。**
"""

BLOCKER = """

---

## 328. 加第三态 `base-tail`：store 真实覆盖 **11/55 = 20%**，missing 84 → 71

> R904。**改工具，未改产品代码。** 套件沿用 **1802 通过 / 0 失败**。

### 一、取清单时发现的问题

**`store` 缺失清单里 `checkout.johnlewis.com` 占 11 条。而 `JohnLewisBff` 里它们是
`Base = ".../bff/"` + 相对路径 —— **逐字匹配看不到。****

**所以那些不是缺，是规则看不见。而 R894 已因同一个坑高报过 40 族缺失。**

### 二、三态

| 状态 | 判据 | 含义 |
|---|---|---|
| **verbatim** | 整条路径是字面量 | 确实有 |
| **base-tail** | 去掉族前缀的尾部是字面量 | 知道端点，藏在 Base 后 |
| **missing** | 两者都不是 | 真缺 |

### 三、数字

| 桶 | verbatim | base-tail | 合计 |
|---|---|---|---|
| **store** | 3 | **8** | **11 / 55（20%）** |
| **vendor** | 0 | **5** | 5 / 32（15.6%） |
| **hostless** | **67** | 0 | **67 / 67（100%）** |
| **missing** | — | — | **71**（原 84） |

**13 条假阴性浮出：store 8 + vendor 5。**

### 四、为什么单列而不并入

**算成 covered 会高报，算成 missing 会低报 —— 而前面几轮轮流犯过这两种。
第三种状态是那个代价该待的地方：报表里看得见，两边都不污染。**

### 五、验证

```
endpoint_coverage.py  -> store 3 verbatim + 8 base-tail = 11/55；vendor 0+5；hostless 67；missing 71
本轮未改产品代码；套件 1802
```

### 六、仍然 Unknown

- **base-tail 那 13 条是否真挂在同一个 Base 下**：**Unknown** ——
  **尾部匹配只证明「复刻件里有一段同样的字面量」，不证明它与镜像的那条同属一个基址。**
- **`/shield/v1/verify_otp`**：**Unknown，优先级 ②。**
- **`store` 那 44 条真缺失**：**Unknown 清单** —— 下一步。

### 七、教训

**R894 我学到「整条字面量判据太严」。这一轮在**同一个工具**里又犯了一次 ——
因为我把它写成 verbatim only 并自称那是「诚实的默认」。**

**而「诚实的默认」这个词本身是信号：它意味着我知道有代价，却把代价藏进了规则而不是报表。**

**第三种状态才是那个代价该待的地方。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R904", BLOCKER)
    ensure(RSTATUS, "R904", BLOCKER)
    ensure(RVERDICT, "第 904 轮", VERDICT)
    ensure(BACKLOG, "R904", BACKLOG_ADD)

    note = (
        "\n## R904 补充 — 加第三态 base-tail，浮出 13 条假阴性（改工具）\n\n"
        "起因：store 缺失清单里 checkout.johnlewis.com 占 11 条，而 JohnLewisBff 用 Base + 相对路径存，逐字匹配看不到。"
        "与 R894 同一个坑，同一个工具里第二次。\n\n"
        "三态：verbatim（整条字面量）· base-tail（去族前缀的尾部字面量）· missing。\n\n"
        "数字：store 3+8 = 11/55（20%，原报 5.5%）· vendor 0+5 · hostless 67/67（100%）· missing 84 → 71。\n\n"
        "不并入的理由：算 covered 会高报、算 missing 会低报，两种前面都犯过；第三种状态是代价该待的地方。\n\n"
        "下一轮：/shield/v1/verify_otp（优先级 ②）；store 那 44 条真缺失清单。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R904" not in h:
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
             for p, k in ((RBLOCK, "R904"), (RSTATUS, "R904"), (RVERDICT, "第 904 轮"), (BACKLOG, "R904")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R904: a third state in the coverage tool, which surfaces thirteen false negatives\n\n"
         "The round set out to list the missing store paths and the list was immediately suspicious: eleven of them\n"
         " belonged to checkout.johnlewis.com, and JohnLewisBff stores those as a base plus a relative tail, which a\n"
         " verbatim search cannot see. So they were not missing; the rule could not see them. R894 had already paid for\n"
         " this exact mistake by over-reporting forty absent families, and here it was again inside the tool that was\n"
         " written to stop that kind of drift.\n\n"
         "The fix is a third state rather than a looser rule. A path is verbatim when the whole string appears, base-tail\n"
         " when the portion after its family segment appears, and missing otherwise. Base-tail is reported in its own\n"
         " column because counting it as covered would overstate and counting it as missing would understate, and earlier\n"
         " rounds did each of those in turn.\n\n"
         "Under the new column the store bucket reads three verbatim plus eight base-tail, eleven of fifty-five or\n"
         " twenty percent against the five point five previously reported. Vendors gain five base-tail. Total missing\n"
         " falls from eighty-four to seventy-one, so thirteen rows were false negatives all along.\n\n"
         "Unknown: whether those thirteen really hang under the same base, since a tail match shows the replica contains\n"
         " the same literal somewhere and not that it belongs to the same base; what shield/v1/verify_otp verifies, which\n"
         " is the anti-bot priority's first concrete endpoint; and the list of the forty-four store paths that are\n"
         " genuinely absent.\n\n"
         "The lesson is about a phrase I used. I called verbatim-only matching the honest default, and that phrase was\n"
         " the tell: it meant I knew there was a cost and put the cost inside the rule instead of inside the report. A\n"
         " third state is where that cost belongs, because then it is visible and it contaminates neither side.\n\n"
         "Tool changed; no product code changed; suite carries at 1802."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
