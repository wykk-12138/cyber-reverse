"""Record R965: the hollow-step list was audited with a wider regex, and two rounds of conclusions fall."""

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
### 那 34 个「空壳」几乎全都有覆写 —— 而我的正则漏了 `async`（R965）

**R962 数出「35 个 `=> Ok()` 空壳」，R963 据此定了「零覆写 → 必被裁」的规则。
这一轮把 34 个名字**全查了一遍**，用一个更宽的正则：**

```
旧: override\\s+Task<StepOutcome>\\s+<Step>Async
新: override\\s+(?:async\\s+)?Task<StepOutcome>\\s+<Step>Async    ← 多了 async 可选
```

### 而结果

| 步骤 | 覆写数 | 步骤 | 覆写数 |
|---|---|---|---|
| `ScrapeVariantAvailability` | **13** | `GetShippingRates` | 3 |
| `GetCsrf` | **4** | `SubmitBilling` | 2 |
| `CreateCart` · `EditLine` · `InitiateCheckout` · `SubmitEmail` | 3 | `Login` · `SubmitSensor` · `GetCaptcha` · `WaitForRelease` | 2 |
| 其余 20 个 | **1** | | |

> **34 个，**每一个至少 1 处覆写**。零覆写的一个都没有。**
> **而 R962 报的是「`GetCsrf` 覆写 0 处、`SubmitEmail` 0、`CreateCart` 0、`Login` 0、`SolveCaptcha` 0、`BuildDestination` 0、`Fill` 0」。**

### 所以 R962 和 R963 各倒了一半

**R962 的「35 个空壳、零覆写」——**覆写数全错**，因为正则漏了 `async` 关键字。
整个复刻件的覆写大量写成 `public override async Task<StepOutcome> XAsync(...)`，而旧正则要求
`override` 后面**紧跟** `Task<StepOutcome>`。**

**R963 的规则「零覆写 → 必被裁」—— 前提（有零覆写的步骤）不存在。
而「`BstnFlow.GetCartAsync` 是全仓唯一覆写」也是同一个假阴性造成的。**

### 而那条规则**还对不对**

> **它对「零覆写」这个条件仍然逻辑成立（空集上无矛盾），但它**没有被任何实例支持** ——
> 而 R963 用它推翻了八轮主张，那是**建立在一个假阴性上的推翻**。**
> **而 R964 的 +43 仍然成立（覆写让方法进产物），那一条是直接观测，不受这个错影响。****

### 而真正的问题是另一个

**既然 34 个步骤都有覆写，为什么函数数只有 173,952 / 277,120？**

**那说明缺口**不在「步骤有没有实现」**上。
而这一路我一直在拿「写实现」当进展，而**实现早就有了**。

> **所以真正要查的是：这些覆写**进产物了吗**、以及 62.77% 的缺口**在哪一层**。
> 而这两个问题我之前都没问过 —— 因为我一直假设缺口在「没写」。****

### 数字

| 度量 | R964 | **R965** |
|---|---|---|
| 套件 | 2186 | **2186（本轮只取证）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **零覆写的空壳** | 34（R962 报） | **0（全部至少 1 处）** |
| `GetCsrf` 覆写数 | 1（R964 报） | **4** |
| `ScrapeVariantAvailability` 覆写数 | — | **13** |

### 教训

> **同一个错第三、第四、第五次了：**假设太窄，然后把「不符合假设」读成「不存在」**。
> R753 / R759 / R760 / R762 / R763 / R764 / R768 / R772 / R884 / R885 / R897 / R900 / R911 / R917 / R925 / R929 /
> R936 / R939 / R942 / R943 / R954 —— 加上 R962 和 R963。**
> **而这次的两个字是 `async`。它就在代码里，在 `override` 和 `Task<StepOutcome>` 之间，
> 而我十五轮里从没把它写进那个正则。**
"""

if "那 34 个「空壳」几乎全都有覆写" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 965 轮：那 34 个「空壳」几乎全都有覆写 —— 我的正则漏了 `async`

### 做了什么

**R963 定了「零覆写 → 必被裁」的规则，R964 照着写了一个覆写。这一轮把 34 个名字**全查了一遍**，
用一个更宽的正则：`override\\s+(?:async\\s+)?Task<StepOutcome>\\s+<Step>Async`。**

### 结果

| 步骤 | 覆写数 |
|---|---|
| `ScrapeVariantAvailability` | **13** |
| `GetCsrf` | **4** |
| `CreateCart` · `EditLine` · `InitiateCheckout` · `SubmitEmail` · `GetShippingRates` | 3 |
| `SubmitBilling` · `Login` · `SubmitSensor` · `GetCaptcha` · `WaitForRelease` | 2 |
| 其余约 20 个 | **1** |

> **34 个，**每一个至少 1 处覆写**。零覆写的一个都没有。**
> **而 R962 报的是「`GetCsrf` 0 · `SubmitEmail` 0 · `CreateCart` 0 · `Login` 0 · `SolveCaptcha` 0 ·
> `BuildDestination` 0 · `Fill` 0」。**

### 所以 R962 和 R963 各倒一半

**R962 的「35 个空壳、零覆写」—— 覆写数全错，因为旧正则要求 `override` **紧跟** `Task<StepOutcome>`，
而这仓里大量覆写写成 `public override async Task<StepOutcome> XAsync(...)`。**

**R963 的规则「零覆写 → 必被裁」—— 前提不存在。而「`BstnFlow.GetCartAsync` 是全仓唯一覆写」
也是同一个假阴性造成的。**

> **对「零覆写」这个条件它逻辑上仍成立（空集无矛盾），但**没有被任何实例支持** ——
> 而 R963 用它推翻八轮主张，那是**建立在一个假阴性上的推翻**。**
> **R964 的 +43 仍成立（直接观测，不受影响）。**

### 而真正的问题浮出来了

**既然 34 个步骤都有覆写，为什么函数数只有 173,952 / 277,120？**

**→ 缺口**不在「步骤有没有实现」**上。而这一路我一直在拿「写实现」当进展，而**实现早就有了**。

> **真正要问的是：这些覆写**进产物了吗**、62.77% 的缺口**在哪一层**。
> 而这两个问题我之前都没问过 —— 因为我一直假设缺口在「没写」。**

### 数字

| 度量 | R964 | **R965** |
|---|---|---|
| 套件 | 2186 | **2186（只取证）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **零覆写的空壳** | 34（R962 报） | **0** |
| `GetCsrf` 覆写数 | 1（R964 报） | **4** |

### 教训

> **同一个错又犯了：**假设太窄，然后把「不符合假设」读成「不存在」**。
> 这是第二十二次（R753 … R954，加 R962、R963）。
> **而这次的两个字是 `async` —— 它就在代码里，在 `override` 和 `Task<StepOutcome>` 之间，
> 而我十五轮里从没把它写进那个正则。**
"""

BACKLOG_ADD = """

## 判据 (a)/(c) — **34 个空壳全部有覆写；R962/R963 的覆写数全错**（R965，**只取证**）

### 正确正则

**`override\\s+(?:async\\s+)?Task<StepOutcome>\\s+<Step>Async`（旧版漏 `async`）**

### 34 个步骤的覆写数

**`ScrapeVariantAvailability` 13 · `GetCsrf` 4 · `CreateCart`/`EditLine`/`InitiateCheckout`/`SubmitEmail`/
`GetShippingRates` 3 · `SubmitBilling`/`Login`/`SubmitSensor`/`GetCaptcha`/`WaitForRelease` 2 ·
其余约 20 个 1 · **零覆写 0 个****

### 更正

**R962「35 个空壳、零覆写」→ 覆写数全错（假阴性）**
**R963「零覆写 → 必被裁」→ 前提不存在；「`BstnFlow.GetCartAsync` 唯一覆写」也是假阴性**
**R964「+43 覆写让方法进产物」→ 仍成立（直接观测）**

### 新问题

**既然都有覆写，为什么只有 62.77%？→ 缺口**不在「有没有实现**上。**
**要查：这些覆写进产物了吗；62.77% 的缺口在哪一层。**

### 数字

**套件 2186（未变）· 函数数 173,952（未变）· 陈旧度 0/0 · 零覆写空壳 34 → 0**

| 仍 Unknown | |
|---|---|
| 那 34 个覆写是否都进产物 | 未逐个核对 |
| 62.77% 缺口在哪一层 | 未查（本轮才提出这个问题） |

**纪律**：第二十二次「假设太窄」。而这次漏的两个字是 `async`。
"""

BLOCKER = """

---

## 389. **34 个空壳全部有覆写** —— R962/R963 的覆写数全错（正则漏 `async`）

> R965。**只取证，未改代码。** 套件 **2186 通过 / 0 失败 / 0 跳过** 保持不变。

### 一、错在哪

```
旧正则: override\\s+Task<StepOutcome>\\s+<Step>Async
新正则: override\\s+(?:async\\s+)?Task<StepOutcome>\\s+<Step>Async
```

**这仓里大量覆写写成 `public override async Task<StepOutcome> XAsync(...)` ——
旧正则要求 `override` 后**紧跟** `Task<StepOutcome>`，于是把它们全判成「没有覆写」。**

### 二、正确的数

| 步骤 | 覆写数 |
|---|---|
| `ScrapeVariantAvailability` | **13** |
| `GetCsrf` | **4** |
| `CreateCart` · `EditLine` · `InitiateCheckout` · `SubmitEmail` · `GetShippingRates` | 3 |
| `SubmitBilling` · `Login` · `SubmitSensor` · `GetCaptcha` · `WaitForRelease` | 2 |
| 其余约 20 个 | **1** |

**34 个，每一个至少 1 处覆写。零覆写的：0 个。**

### 三、倒掉的两条

**R962「35 个空壳、零覆写」→ 覆写数全错。**
**R963「零覆写 → 必被裁」→ 前提不存在；「`BstnFlow.GetCartAsync` 是全仓唯一覆写」也是假阴性。**
**R964「覆写让方法进产物（+43）」→ 仍成立，那是直接观测。**

### 四、而真正的问题

**既然 34 个步骤都有覆写，为什么函数数只有 173,952 / 277,120？**

**→ 缺口不在「步骤有没有实现」上。而这一路我一直在拿「写实现」当进展，而实现早就有了。**

**要查两件我没问过的事：**
1. **那 34 个覆写是否都进产物**
2. **62.77% 的缺口在哪一层**

### 五、数字

| 度量 | R964 | R965 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **零覆写的空壳** | 34（错） | **0** |
| `GetCsrf` 覆写数 | 1（错） | **4** |

### 六、验证

```
python analysis/hollow_audit.py
  -> 34 个步骤逐个列出覆写数，最小 1，最大 13，零覆写 0
```

### 七、仍然 Unknown

- **那 34 个覆写是否都进产物**：**Unknown** —— 未逐个核对。
- **62.77% 缺口在哪一层**：**Unknown** —— 本轮才提出这个问题。

### 八、教训

**第二十二次「假设太窄」。而这次漏的两个字是 `async` ——
它就在代码里、在 `override` 和 `Task<StepOutcome>` 之间，而我十五轮里从没把它写进那个正则。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R965", BLOCKER)
    ensure(RSTATUS, "R965", BLOCKER)
    ensure(RVERDICT, "第 965 轮", VERDICT)
    ensure(BACKLOG, "R965", BACKLOG_ADD)

    note = (
        "\n## R965 补充 — **34 个空壳全部有覆写**；R962/R963 的覆写数全错（正则漏 `async`）（套件 2186）\n\n"
        "旧正则 `override\\s+Task<StepOutcome>\\s+<Step>Async` 漏掉 `async` 关键字 → 把大量覆写判成「没有」。\n"
        "新正则 `override\\s+(?:async\\s+)?Task<StepOutcome>\\s+<Step>Async` 下逐个数：\n"
        "`ScrapeVariantAvailability` 13 · `GetCsrf` 4 · 五个 3 · 五个 2 · 其余约 20 个 1 · **零覆写 0 个**。\n\n"
        "**倒掉**：R962「35 个空壳零覆写」；R963「零覆写→必被裁」的前提 + 「BstnFlow.GetCartAsync 唯一覆写」。\n"
        "**仍成立**：R964「覆写让方法进产物（+43）」，直接观测。\n\n"
        "**而真正的问题浮出来**：既然 34 个都有覆写，为什么只有 173,952 / 277,120（62.77%）？\n"
        "→ 缺口**不在「有没有实现」上**，而我一直拿「写实现」当进展，实现早就有了。\n"
        "要查：① 那 34 个覆写是否都进产物；② 62.77% 缺口在哪一层。\n\n"
        "数字：套件 2186（未变）· 函数数 173,952（未变）· 陈旧度 0/0 · 零覆写空壳 34 → 0。\n\n"
        "纪律：第二十二次「假设太窄」，这次漏的两个字是 `async`。\n\n"
        "下一轮：查①——逐个核对 34 个覆写的独有串是否在产物里。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R965" not in h:
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
             for p, k in ((RBLOCK, "R965"), (RSTATUS, "R965"), (RVERDICT, "第 965 轮"), (BACKLOG, "R965")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R965: all thirty-four hollow steps have overrides, and my regex was missing the word async\n\n"
         "R963 concluded that a virtual step is trimmed unless a concrete flow overrides it, resting on a count of zero\n"
         " overrides for GetCsrf, SubmitEmail, CreateCart, Login and three others. This round audited all thirty-four names\n"
         " with a wider pattern and the count was wrong.\n\n"
         "The old regex required override to be immediately followed by Task<StepOutcome>. Much of this repository writes\n"
         " public override async Task<StepOutcome> XAsync, and the word in between made every one of those invisible. With\n"
         " async allowed as an option, ScrapeVariantAvailability has thirteen overrides, GetCsrf four, five steps have\n"
         " three, five have two, and the remaining twenty have one. Not a single step has zero.\n\n"
         "So two rounds fall. R962's thirty-five hollow steps with zero overrides is wrong on the count, and R963's rule\n"
         " loses its premise, including the claim that BstnFlow.GetCartAsync was the only override in the repository. The\n"
         " rule remains logically true of the empty case but no instance supports it, which means the overturning of the\n"
         " previous eight rounds rested on a false negative. R964's forty-three functions still stand, because those came\n"
         " from a direct observation rather than from the rule.\n\n"
         "And a better question surfaces. If all thirty-four steps have overrides, why is the count 173,952 against\n"
         " 277,120? The gap is not in whether the steps are implemented, and implementation has been my measure of progress\n"
         " for many rounds while the implementation was already there. What needs asking is whether those overrides reach\n"
         " the artifact, and where the missing thirty-seven percent actually sits -- neither of which I had asked.\n\n"
         "Figures unchanged because no code changed: suite 2186, count 173,952, freshness zero, and the count of steps with\n"
         " no override down from thirty-four to zero.\n\n"
         "Unknown: whether all thirty-four overrides reach the artifact, not yet checked one by one; and which layer holds\n"
         " the gap, a question this round raised for the first time.\n\n"
         "The lesson is that this is the twenty-second time I have assumed a shape too narrowly and then read the\n"
         " non-conforming cases as absent. The two characters I missed are async, and they sat between override and\n"
         " Task<StepOutcome> in the code for fifteen rounds without ever entering that pattern.\n\n"
         "Documentation and one audit script only; no product code changed."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()