"""Record R964: the first override written to test the rule, and the rule needs narrowing."""

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
### 第一个「按新策略写」的覆写：**+43 函数**，而规则要收窄（R964）

**R963 定的策略是：覆写进具体 flow，不写共用基类。这一轮照做了一次，并且**用产物核对，不靠相信**。**

### 改了什么

**`BstnFlow.GetCsrfAsync` —— 第一个真正做事的覆写（不是 `StepOutcome.Fail` 占位）：
拉 `https://www.bstn.com/` → `FindCsrfToken` → 回退到 `csrftoken` cookie → 找不到判不可重试。**

### 而产物说了两件事

**① 覆写确实让方法进产物：**

```
pdata-replica: 173,909 -> 173,952     +43
pdata-ratio:   62.76%  -> 62.77%
```

**② 而方法体里的**报错串**没进：**

| 串 | 在产物 |
|---|---|
| `www.bstn.com`（同方法里的 URL 字面量） | **True** |
| `bstn: csrf page ` | False |
| `bstn: no csrf token on the landing page` | False |
| `bstn: cart endpoint unknown`（`GetCart` 覆写，同步） | **True** |
| `bstn: checkout endpoint unknown (Adyen)`（`GetCheckout` 覆写） | False |

### 所以 R963 的规则要收窄

> **「有覆写才保留」—— 方向对（+43 证明）。
> 但「覆写体完整保留」是错的：同一个 async 方法里，URL 字面量在、`StepOutcome.Fail` 的参数串不在。**
> **而 `GetCheckoutAsync` 也是覆写，它的串也不在 —— 所以「覆写」不是充分条件，只是必要条件。**

**新规则（Observation，两条）：**

1. **零覆写 → 基类体必被裁（R963 三组对比）**
2. **有覆写 → 方法进产物，但体内字符串**按需保留**，判据 Unknown**

> **而第 2 条对「用串核对产物」这个做法有直接影响：
> 串在场可以证明「在」，串不在**不能**证明「不在」——
> 这又是 §2.7b 那条反向不可用，而这次是在**产物**上踩的。****

### 而一个守卫红了，而它钉的正是我想去掉的东西

**`StepActionTests.RunnerExecutesAnActionAndRecordsEveryStep` 用 `TinyServer(_ => (200, "{}"))` 跑 `CSRF-Generate`，
期望 3 步全 OK。**

**而 `GetCsrf` 现在找不到 token 会**正确失败** —— 所以那个测例红在了**假成功消失**上。**

> **处置：把 fixture 换成带 token 的页面（`<input type="hidden" name="csrf_token" value="testtoken123456">`），
> 测例仍在测它名字说的那件事（每步都跑、都被记录），而不再顺手钉住一个假成功。**
> **而这不是「改数字」——是**行为变了，所以改夹具**，两者都是正当的，但要说清是哪一种。**

### 数字

| 度量 | R963 | **R964** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,909 | **173,952（+43）** |
| **函数比** | 62.76% | **62.77%** |
| 产物大小 | 54,724 KB | **54,741 KB** |
| 覆写总数（GetCsrf） | 0 | **1** |

### 教训

> **这一轮同时验证了一条规则和收窄了它 —— 而收窄的部分比验证的部分重要。
> 「有覆写 → 进产物」让我高兴了十分钟；「但体内字符串按需保留」让我明白
> **我刚才用来高兴的那个核对方法，在反方向上不成立**。**
> **而这条规则 R963 就写过（§2.7b），我这一轮差点又用它反向下了结论。**
"""

if "第一个「按新策略写」的覆写" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 964 轮：第一个按新策略写的覆写 —— +43，而规则要收窄

### 改了什么

**`BstnFlow.GetCsrfAsync`：拉页面 → `FindCsrfToken` → 回退 `csrftoken` cookie → 找不到判不可重试。
第一个真正做事的覆写（不是 `Fail` 占位）。**

### 产物说了两件事

**① 覆写确实让方法进产物：173,909 → **173,952（+43）**，比 62.77%。**

**② 而方法体里的报错串**没进**：**

| 串 | 在产物 |
|---|---|
| `www.bstn.com`（同方法 URL 字面量） | **True** |
| `bstn: csrf page ` · `bstn: no csrf token on the landing page` | False |
| `bstn: cart endpoint unknown`（同步覆写） | **True** |
| `bstn: checkout endpoint unknown (Adyen)`（另一覆写） | False |

### R963 的规则要收窄

> **「有覆写才保留」方向对（+43 证明）；但「覆写体完整保留」错 ——
> 同一个 async 方法里 URL 在、`Fail` 的参数串不在；而 `GetCheckoutAsync` 也是覆写、串也不在。
> 所以「覆写」是**必要条件不是充分条件**。**

**新规则两条：**
1. **零覆写 → 基类体必被裁**（R963 三组对比）
2. **有覆写 → 方法进产物，但体内字符串按需保留，判据 Unknown**

> **第 2 条直接影响「用串核对产物」：串在场能证明「在」，串不在**不能**证明「不在」——
> 又是 §2.7b 反向不可用，这次踩在**产物**上。**

### 一个守卫红了，而它钉的正是我想去掉的东西

**`RunnerExecutesAnActionAndRecordsEveryStep` 用 `(200, "{}")` 跑 `CSRF-Generate` 期望 3 步全 OK。
而 `GetCsrf` 现在找不到 token 会**正确失败** → 那个测例红在**假成功消失**上。**

> **处置：fixture 换成带 token 的页面。测例仍在测它名字说的那件事（每步都跑、都被记录），
> 而不再顺手钉住一个假成功。这是「行为变了 → 改夹具」，不是「形状变了 → 改数字」。**

### 数字

| 度量 | R963 | **R964** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,909 | **173,952（+43）** |
| **函数比** | 62.76% | **62.77%** |
| 产物大小 | 54,724 KB | **54,741 KB** |
| `GetCsrf` 覆写数 | 0 | **1** |

### 教训

> **这一轮同时验证了一条规则和收窄了它，而收窄的部分比验证的部分重要。
> 「有覆写 → 进产物」让我高兴了十分钟；「但体内字符串按需保留」让我明白
> 我刚才用来高兴的那个核对方法，在反方向上不成立。**
> **而这条规则 R963 就写过，我这一轮差点又用它反向下了结论。**
"""

BACKLOG_ADD = """

## 判据 (c) — 第一个按新策略写的覆写：+43，而规则收窄（R964，**+0 用例**）

### 改动

**`BstnFlow.GetCsrfAsync` 覆写：拉 `https://www.bstn.com/` → `FindCsrfToken` → 回退 `csrftoken` cookie**

### 产物核对

**`pdata-replica` 173,909 → **173,952（+43）** · 比 62.77% · 产物 54,741 KB**

**串核对：`www.bstn.com` **True**；`bstn: csrf page` / `bstn: no csrf token on the landing page` False；
`bstn: cart endpoint unknown`（同步覆写）True；`bstn: checkout endpoint unknown (Adyen)` False**

### 规则收窄

**① 零覆写 → 基类体必被裁（R963）**
**② 有覆写 → 方法进产物，但**体内字符串按需保留，判据 Unknown****

**→ 串在场证明「在」；串不在**不能**证明「不在」（§2.7b，踩在产物上）**

### 修了一个钉住假成功的测例

**`RunnerExecutesAnActionAndRecordsEveryStep` 的 fixture 从 `{}` 换成带 token 的页面
—— 行为变了改夹具，不是形状变了改数字。**

### 数字

**套件 2186 / 0 / 0 · 陈旧度 0/0 · 函数数 173,952 · 比 62.77%**

| 仍 Unknown | |
|---|---|
| 体内字符串按需保留的判据 | 未取证 |
| 覆写两层的继承链是否算 | 未取证 |
| 剩 34 个空壳里各站该覆写哪些 | 需逐站取证 |

**纪律**：串不在不能证明不在 —— 这次踩在产物上。
"""

BLOCKER = """

---

## 388. 第一个按新策略写的覆写：+43，而规则要收窄

> R964。**改产品代码 + 修一个测例夹具。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、改动

**`BstnFlow.GetCsrfAsync` —— 第一个真正做事的覆写：
拉 `https://www.bstn.com/` → `FindCsrfToken` → 回退 `csrftoken` cookie → 找不到判不可重试。**

### 二、产物核对（两件事）

**① 覆写确实让方法进产物：`173,909 → 173,952（+43）`，比 62.77%。**

**② 而方法体里的报错串没进：**

| 串 | 在产物 |
|---|---|
| `www.bstn.com` | **True** |
| `bstn: csrf page ` | False |
| `bstn: no csrf token on the landing page` | False |
| `bstn: cart endpoint unknown`（同步覆写） | **True** |
| `bstn: checkout endpoint unknown (Adyen)`（另一覆写） | False |

### 三、R963 的规则收窄

**① 零覆写 → 基类体必被裁（R963 三组对比）**
**② 有覆写 → 方法进产物，但体内字符串**按需保留**，判据 Unknown**

**所以「覆写」是**必要条件不是充分条件**（`GetCheckoutAsync` 也是覆写、串也不在）。**

**→ 直接影响核对方法：串在场证明「在」；串不在**不能**证明「不在」（§2.7b，这次在产物上）。**

### 四、修了一个钉住假成功的测例

**`StepActionTests.RunnerExecutesAnActionAndRecordsEveryStep` 用 `TinyServer(_ => (200, "{}"))`
跑 `CSRF-Generate` 期望 3 步全 OK；`GetCsrf` 现在找不到 token 会正确失败 → 它红在假成功消失上。**

**处置：fixture 换成 `<input type="hidden" name="csrf_token" value="testtoken123456">`。
测例仍在测「每步都跑、都被记录」，而不再顺手钉住一个假成功。**

**这是「行为变了 → 改夹具」，不是「形状变了 → 改数字」。**

### 五、数字

| 度量 | R963 | R964 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,909 | **173,952（+43）** |
| **函数比** | 62.76% | **62.77%** |
| 产物大小 | 54,724 KB | **54,741 KB** |
| `GetCsrf` 覆写数 | 0 | **1** |

### 六、验证

```
dotnet build Stores -c Debug                -> 0 error
dotnet publish                              -> 54,741 KB
func_count.py                               -> 173,952 (+43)
probe_artifact.py: 'www.bstn.com'           -> utf16=True
probe_artifact.py: 'bstn: csrf page '       -> utf16=False
test --filter StepActionTests               -> 7 通过
metrics_report.py                           -> 2186 通过 / 0 失败
```

### 七、仍然 Unknown

- **体内字符串按需保留的判据**：**Unknown** —— 未取证。
- **覆写两层的继承链是否算**：**Unknown** —— 未取证。
- **剩 34 个空壳里各站该覆写哪些**：**Unknown** —— 需逐站取证。

### 八、教训

**「有覆写 → 进产物」让我高兴了十分钟；「但体内字符串按需保留」让我明白
我刚才用来高兴的那个核对方法，在反方向上不成立。**

**而这条规则 R963 就写过，我这一轮差点又用它反向下了结论。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R964", BLOCKER)
    ensure(RSTATUS, "R964", BLOCKER)
    ensure(RVERDICT, "第 964 轮", VERDICT)
    ensure(BACKLOG, "R964", BACKLOG_ADD)

    note = (
        "\n## R964 补充 — 第一个按新策略写的覆写：+43，而规则收窄（套件 2186）\n\n"
        "照 R963 的策略做了第一个真覆写：`BstnFlow.GetCsrfAsync`（拉 www.bstn.com → FindCsrfToken → 回退 csrftoken cookie）。\n\n"
        "**产物核对两件事**：\n"
        "① 覆写确实让方法进产物：173,909 → **173,952（+43）**，比 62.77%，产物 54,741 KB。\n"
        "② 而方法体里的报错串**没进**：`www.bstn.com` True；`bstn: csrf page ` False；\n"
        "   `bstn: no csrf token on the landing page` False；`bstn: cart endpoint unknown`（同步覆写）True；\n"
        "   `bstn: checkout endpoint unknown (Adyen)`（另一覆写）False。\n\n"
        "**规则收窄两条**：① 零覆写 → 基类体必被裁；② 有覆写 → 方法进产物，但体内字符串**按需保留**，判据 Unknown。\n"
        "**→ 覆写是必要条件不是充分条件；串不在**不能**证明不在（§2.7b，这次踩在产物上）。**\n\n"
        "修了一个钉住假成功的测例：`RunnerExecutesAnActionAndRecordsEveryStep` 的 fixture 从 `{}` 换成带 token 的页面\n"
        "（行为变了改夹具，不是形状变了改数字）。\n\n"
        "数字：套件 2186 / 0 / 0 · 陈旧度 0/0 · 函数数 173,952 · 比 62.77% · GetCsrf 覆写数 0 → 1。\n\n"
        "纪律：串不在不能证明不在。\n\n"
        "下一轮：给第二个站写覆写（挑一个有真实端点证据的站），并核对 +43 这个量是否稳定。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R964" not in h:
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
             for p, k in ((RBLOCK, "R964"), (RSTATUS, "R964"), (RVERDICT, "第 964 轮"), (BACKLOG, "R964")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R964: the first override written to test R963's rule, which the artifact both confirms and narrows\n\n"
         "R963 concluded that a virtual method on StoreFlow reaches the artifact only when a concrete flow overrides it, and\n"
         " that shared base bodies therefore change nothing. This round acted on it once and checked the artifact rather\n"
         " than trusting the conclusion.\n\n"
         "BstnFlow.GetCsrfAsync is the first override that does work rather than returning a Fail placeholder: it fetches the\n"
         " shop's landing page, finds a token, falls back to the csrftoken cookie, and fails when neither is there.\n\n"
         "The artifact said two things. The rule holds in its direction: the count went from 173,909 to 173,952, so an\n"
         " override does bring the method in. But the strings inside that method did not all arrive. The URL literal is\n"
         " present while both failure messages are absent, and another override entirely, GetCheckoutAsync, also has its\n"
         " string absent, while the synchronous GetCartAsync override keeps its own. So an override is necessary and not\n"
         " sufficient, and which strings a retained method keeps needs its own explanation.\n\n"
         "That matters for method: a string being present proves it is in the artifact, and a string being absent does not\n"
         " prove it is out. This is the reverse-unavailable rule from AGENTS.md and this time it applied to the artifact\n"
         " rather than to a source listing, and I nearly used the weaker direction to draw a conclusion an hour after the\n"
         " round that wrote the rule.\n\n"
         "One guard went red and it was pinning the very thing being removed. RunnerExecutesAnActionAndRecordsEveryStep\n"
         " served a body of two braces and expected all three steps to pass, which only worked because GetCsrf returned\n"
         " success without reading anything. The fixture now serves a page with a real token, so the test still checks what\n"
         " its name says -- that every step runs and is recorded -- without also pinning a false success. That is changing a\n"
         " fixture because behaviour changed, not changing a number because a shape did.\n\n"
         "Figures: suite 2186 green, freshness zero, count 173,952, ratio 62.77 percent, artifact 54,741 kilobytes, and one\n"
         " GetCsrf override where there were none.\n\n"
         "Unknown: what decides which strings a retained method keeps; whether an override two levels down the inheritance\n"
         " chain counts; and which of the remaining thirty-four hollow steps each shop should override.\n\n"
         "The lesson is that this round both confirmed a rule and narrowed it, and the narrowing is the more useful half. The\n"
         " confirmation bought ten minutes of satisfaction; the narrowing showed that the check I was satisfied by does not\n"
         " work in the other direction.\n\n"
         "Product code and one test fixture changed; suite green at 2186."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()