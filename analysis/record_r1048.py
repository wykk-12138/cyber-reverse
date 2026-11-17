"""Record R1048: R1047 closed (suite green), and the seven gaps are two kinds."""

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
### R1047 收尾；而那 7 个缺口只有 **2 个**真该补（R1048）

**R1047 留下的只有一件事：套件没跑。这一轮先补它 —— 绿，所以 R1047 的结论成立。
然后做 (f) 的实质：给 7 条缺口逐条写「为什么未覆盖 + 该不该补」。**

### ① R1047 收尾

```
完整套件  exit 0  2258 通过 / 0 失败 / 0 跳过
产物陈旧度  exit 0  0 / 0
函数数       277,120 / 174,293 / 62.89%
```

**→ 所以 R1047 记的「未跑」现在补成「跑了，绿」。而那条纪律仍然成立：
未跑要写未跑，补跑之后才写绿。**

### ② 而 7 条缺口分成**两类**，而那把上一轮的判断修正了

**上一轮我按「撞到就算缺」数出 **4 个**真缺口。这一轮给每条定了**类别**与**处置**，结果只有 **2 个**：**

| 缺口 | 命中 | 类别 | 处置 |
|---|---|---|---|
| **`BotDeflector`** | 2 | **vendor** | 真该补行。原版有**两条**文案（`icons` · `proof of work`）⇒ 它是**两种挑战**。补行要先定 `Solver` —— 镜像里没有第三方指向，但那不等于自建（R1029 的 `Relayed` 两轴就是为这种情形留的）。 |
| **`Vercel`** | 2 | **vendor** | 真该补行。只有一条文案、无分期 ⇒ 最小诚实形态是 `State.DetectedOnly` + `Solver.Unknown`。 |
| `Stripe challenge` | 1 | **payment** | **不该进这张表** —— 那是支付侧挑战，属 `AdyenGateway` 那一族。 |
| `PayPal 3DS` | 9 | **payment** | **不该进这张表** —— 9 条分期（`(1)`…`(8)` 加无条件）是 3DS 的阶段。**分期数本身是有用证据：3DS 有 8 个可观察阶段。** |
| `captcha` | 1 | challenge | 通用验证码，不是厂商 ⇒ 台账形状不建模，**且不该建模**。 |
| `proof of work` | 1 | challenge | 同上。**注意镜像原文拼作 `challange` —— 保留拼写，不修正。** |
| `checkpoint` | 1 | challenge | 同上。 |

**→ 所以：真厂商缺口 **2** 个（`BotDeflector` · `Vercel`）· 不属于这张表的 **5** 个。**

**→ 而那次修正值得记：上一轮我把「原版点名 + 台账没有」当成一个判据，
而它把**三种不同的东西**混成一个数 —— 厂商、支付挑战、通用挑战类型。
→ 与 R1042 那次「14 个未知压成一个数字」是**同一个形状**：计数掩盖类别。**

### ③ 而生成物现在带类别与处置

**`replica/docs/VENDOR_COVERAGE.md`：2,059 → **4,466 字节**，7 条缺口每条一行「类别 + 为什么 + 处置」。**

**→ 而生成器里那张 `DISPOSITION` 表是**手写的判断**，所以它有一条自保：
`DISPOSITION.get(name, ("?", "（未分类 —— 这是生成器的缺口，不是结论）"))` ——
→ 若镜像里出现一个我没分类的名字，表会**明说那是生成器的缺口**，而不是默默把它当「不属于这张表」。**

### ④ 数字

| 度量 | R1047 | **R1048** |
|---|---|---|
| **完整套件** | **未跑** | **2258 / 0 / 0（绿）** |
| 产物陈旧度 | 未重测 | **0 / 0** |
| 函数数 | 未重测 | **174,293** |
| 比例 | — | **62.89%** |
| **`Solving` 族命中** | 36 | **36（未变）** |
| **原版点名的求解对象** | 13 | **13** |
| **`VendorWiring` 行数** | 7 | **7** |
| **缺口（总数）** | 7 | **7** |
| **其中真该补的厂商行** | 「4」 | **2（BotDeflector · Vercel）** |
| **不属于这张表的** | — | **5（2 支付 · 3 挑战类型）** |
| **`VENDOR_COVERAGE.md`** | 已生成 | **4,466 字节（含分类与处置）** |

### 教训

> **「撞到就算缺」是一个**太松**的判据，而它给我的数字**偏大一倍**（4 对 2）。
> → 而错的不是取证，是**分类**：支付挑战和通用挑战类型**不属于**站点风控台账，
> 而它们在「原版点名了、台账没有」这个判据下长得和真厂商缺口一模一样。**
> **→ 所以 (f) 那句「未覆盖的每条写为什么」不是形式要求 ——
> 它要求的是**每条先定类别**，因为「为什么未覆盖」的答案随类别完全不同。****
"""

if "R1047 收尾；而那 7 个缺口只有" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1048 轮：R1047 收尾；7 个缺口只有 2 个真该补

### ① R1047 收尾 —— 套件补跑，绿

```
完整套件 exit 0  2258 / 0 / 0        产物陈旧度 0 / 0        函数数 174,293（62.89%）
```

**→ 未跑要写未跑，补跑之后才写绿。**

### ② 而 7 条缺口分成两类，把上一轮的判断修正了

| 缺口 | 命中 | 类别 | 处置 |
|---|---|---|---|
| **`BotDeflector`** | 2 | **vendor** | 真该补。两条文案（`icons` · `proof of work`）⇒ **两种挑战**。补行要先定 `Solver`。 |
| **`Vercel`** | 2 | **vendor** | 真该补。最小诚实形态 `State.DetectedOnly` + `Solver.Unknown`。 |
| `Stripe challenge` | 1 | **payment** | **不该进这张表** —— 属支付层。 |
| `PayPal 3DS` | 9 | **payment** | **不该进这张表** —— 9 条分期，而**分期数本身是证据：3DS 有 8 个可观察阶段**。 |
| `captcha` · `proof of work` · `checkpoint` | 1 / 1 / 1 | challenge | 通用挑战，**不该建模**。注意原文拼作 `challange`，**保留拼写**。 |

**→ 真厂商缺口 **2** 个 · 不属于这张表的 **5** 个。**

**→ 而上一轮我报「4 个真缺口」：错的不在取证，在**分类**。
→ 与 R1042「14 个未知压成一个数字」同一个形状：计数掩盖类别。**

### ③ 而生成物带类别与处置

**`VENDOR_COVERAGE.md`：2,059 → **4,466 字节**，7 条各一行「类别 + 为什么 + 处置」。**
**→ `DISPOSITION` 是手写判断，所以有自保：未分类的名字会**明说「这是生成器的缺口，不是结论」**。**

### ④ 数字

| 度量 | R1047 | **R1048** |
|---|---|---|
| **完整套件** | **未跑** | **2258 / 0 / 0（绿）** |
| 产物陈旧度 | 未重测 | **0 / 0** |
| 函数数 | 未重测 | **174,293** |
| **缺口总数** | 7 | **7** |
| **真该补的厂商行** | 「4」 | **2** |
| **不属于这张表的** | — | **5（2 支付 · 3 挑战）** |
| **`VENDOR_COVERAGE.md`** | 已生成 | **4,466 字节** |

### 教训

> **「撞到就算缺」太松，数字偏大一倍（4 对 2）。
> → 错的不是取证，是**分类**：支付挑战与通用挑战类型不属于站点风控台账，
> 而它们在那个判据下长得和真厂商缺口一模一样。**
> **→ (f) 的「未覆盖的每条写为什么」不是形式要求 —— 它要求**每条先定类别**，
> 因为「为什么未覆盖」的答案随类别完全不同。**
"""

BACKLOG_ADD = """

## 判据 (f) — **R1047 收尾（套件绿）；7 个缺口只有 2 个真该补**（R1048）

### R1047 收尾

```
完整套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · 62.89%
```

### 7 条缺口分两类

| 缺口 | 类别 | 处置 |
|---|---|---|
| `BotDeflector` | **vendor** | 真该补。两条文案 ⇒ 两种挑战（icons · PoW）。补行要先定 `Solver`。 |
| `Vercel` | **vendor** | 真该补。最小诚实形态 `DetectedOnly` + `Solver.Unknown`。 |
| `Stripe challenge` | payment | **不该进这张表**（属支付层） |
| `PayPal 3DS` | payment | **不该进**（9 条分期 ⇒ **3DS 有 8 个可观察阶段**） |
| `captcha` · `proof of work` · `checkpoint` | challenge | **不该建模**（原文 `challange` 拼写保留） |

**⇒ 真厂商缺口 2 · 不属于这张表 5。**

### 生成物

**`VENDOR_COVERAGE.md` 2,059 → **4,466** 字节；`DISPOSITION` 有自保：未分类名字会明说「生成器的缺口」。**

### 数字

**套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · 求解对象 13 · 台账 7 行 · 缺口 7（真厂商 2）**

| 待做 | |
|---|---|
| `BotDeflector` 补行（先定 Solver） | 下一步 |
| `Vercel` 补行（DetectedOnly + Unknown） | 下一步 |

**纪律**：「未覆盖的每条写为什么」要求**每条先定类别** —— 答案随类别完全不同。
"""

BLOCKER = """

---

## 472. **R1047 收尾（套件绿）；7 个缺口只有 2 个真该补**

> R1048。**改 1 个生成器（未改业务代码）。** 套件 **2258 通过 / 0 失败 / 0 跳过**。

### 一、R1047 收尾

```
完整套件  exit 0  2258 通过 / 0 失败 / 0 跳过
产物陈旧度  exit 0  0 / 0
函数数       277,120 / 174,293 / 62.89%
```

**→ R1047 记的「未跑」现在补成「跑了，绿」。而那条纪律仍然成立：
  未跑要写未跑，补跑之后才写绿。**

### 二、而 7 条缺口分成**两类**，而那把上一轮的判断修正了

**上一轮我按「撞到就算缺」数出 **4 个**真缺口。这一轮给每条定了**类别**与**处置**，结果只有 **2 个**：**

| 缺口 | 命中 | 类别 | 处置 |
|---|---|---|---|
| **`BotDeflector`** | 2 | **vendor** | 真该补行。原版有**两条**文案（`icons` · `proof of work`）⇒ 它是**两种挑战**。补行要先定 `Solver` —— 镜像里没有第三方指向，但那不等于自建（R1029 的 `Relayed` 两轴就是为这种情形留的）。 |
| **`Vercel`** | 2 | **vendor** | 真该补行。只有一条文案、无分期 ⇒ 最小诚实形态是 `State.DetectedOnly` + `Solver.Unknown`。 |
| `Stripe challenge` | 1 | **payment** | **不该进这张表** —— 那是支付侧挑战，属 `AdyenGateway` 那一族。 |
| `PayPal 3DS` | 9 | **payment** | **不该进这张表** —— 9 条分期（`(1)`…`(8)` 加无条件）是 3DS 的阶段。**分期数本身是有用证据：3DS 有 8 个可观察阶段。** |
| `captcha` | 1 | challenge | 通用验证码，不是厂商 ⇒ 台账形状不建模，**且不该建模**。 |
| `proof of work` | 1 | challenge | 同上。**注意镜像原文拼作 `challange` —— 保留拼写，不修正。** |
| `checkpoint` | 1 | challenge | 同上。 |

**→ 所以：真厂商缺口 **2** 个（`BotDeflector` · `Vercel`）· 不属于这张表的 **5** 个。**

**→ 而那次修正值得记：上一轮我把「原版点名 + 台账没有」当成一个判据，
  而它把**三种不同的东西**混成一个数 —— 厂商、支付挑战、通用挑战类型。
→ 与 R1042 那次「14 个未知压成一个数字」是**同一个形状**：计数掩盖类别。**

### 三、而生成物现在带类别与处置

**`replica/docs/VENDOR_COVERAGE.md`：2,059 → **4,466 字节**，7 条缺口每条一行「类别 + 为什么 + 处置」。**

**→ 而生成器里那张 `DISPOSITION` 表是**手写的判断**，所以它有一条自保：
  `DISPOSITION.get(name, ("?", "（未分类 —— 这是生成器的缺口，不是结论）"))` ——
  若镜像里出现一个我没分类的名字，表会**明说那是生成器的缺口**，而不是默默把它当「不属于这张表」。**

### 四、数字

| 度量 | R1047 | R1048 |
|---|---|---|
| **完整套件** | **未跑** | **2258 / 0 / 0（绿）** |
| 产物陈旧度 | 未重测 | **0 / 0** |
| 函数数 | 未重测 | **174,293** |
| 比例 | — | **62.89%** |
| **`Solving` 族命中** | 36 | **36（未变）** |
| **原版点名的求解对象** | 13 | **13** |
| **缺口（总数）** | 7 | **7** |
| **其中真该补的厂商行** | 「4」 | **2（BotDeflector · Vercel）** |
| **不属于这张表的** | — | **5（2 支付 · 3 挑战类型）** |
| **`VENDOR_COVERAGE.md`** | 已生成 | **4,466 字节（含分类与处置）** |

### 五、验证

```
cd D:\\projects\\cyber-reverse\\replica
python tools/vendor_coverage.py
  -> controls ok=True  vendors named=13  wiring rows=7  missing=7
  -> docs/VENDOR_COVERAGE.md 4,466 字节
python tools/metrics_report.py -> 完整套件 exit 0  2258 / 0 / 0 · 陈旧度 0 / 0
```

### 六、待做

- **`BotDeflector` 补行**：先定 `Solver`（镜像无第三方指向 ⇒ 按 R1029 的 `Relayed` 两轴处理）。
- **`Vercel` 补行**：`State.DetectedOnly` + `Solver.Unknown`。

### 七、教训

**「撞到就算缺」是一个**太松**的判据，而它给我的数字**偏大一倍**（4 对 2）。**

**→ 而错的不是取证，是**分类**：支付挑战和通用挑战类型**不属于**站点风控台账，
  而它们在「原版点名了、台账没有」这个判据下长得和真厂商缺口一模一样。**

**→ 所以 (f) 那句「未覆盖的每条写为什么」不是形式要求 ——
  它要求的是**每条先定类别**，因为「为什么未覆盖」的答案随类别完全不同。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1048", BLOCKER)
    ensure(RSTATUS, "R1048", BLOCKER)
    ensure(RVERDICT, "第 1048 轮", VERDICT)
    ensure(BACKLOG, "R1048", BACKLOG_ADD)

    note = (
        "\n## R1048 补充 — **R1047 收尾（套件绿）；7 个缺口只有 2 个真该补**（套件 2258）\n\n"
        "**R1047 收尾**：套件补跑 **2258/0/0 绿** · 陈旧度 **0/0** · 函数数 **174,293** · 62.89%。\n"
        "→ 未跑要写未跑，补跑之后才写绿。\n\n"
        "**7 条缺口分两类**（修正上一轮的「4 个」）：\n"
        "| 缺口 | 类别 | 处置 |\n|---|---|---|\n"
        "| `BotDeflector` | **vendor** | 真该补。两条文案 ⇒ **两种挑战**（icons · PoW）。补行要先定 `Solver`。 |\n"
        "| `Vercel` | **vendor** | 真该补。`State.DetectedOnly` + `Solver.Unknown`。 |\n"
        "| `Stripe challenge` | payment | **不该进这张表**（属 `AdyenGateway` 那一族） |\n"
        "| `PayPal 3DS` | payment | **不该进**（9 条分期 ⇒ **3DS 有 8 个可观察阶段**） |\n"
        "| `captcha` · `proof of work` · `checkpoint` | challenge | **不该建模**（原文 `challange` 拼写保留） |\n\n"
        "**⇒ 真厂商缺口 2 · 不属于这张表 5。**\n"
        "→ 与 R1042「14 个未知压成一个数字」同一个形状：**计数掩盖类别**。\n\n"
        "**生成物**：`VENDOR_COVERAGE.md` 2,059 → **4,466** 字节；`DISPOSITION` 有自保 ——\n"
        "未分类的名字会明说「这是生成器的缺口，不是结论」。\n\n"
        "数字：套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · 求解对象 13 · 台账 7 行 · 缺口 7（真厂商 **2**）。\n\n"
        "纪律：**(f) 要求每条先定类别** —— 「为什么未覆盖」的答案随类别完全不同。\n\n"
        "下一轮：给 `BotDeflector` 与 `Vercel` 各补一行（先定 `Solver`），然后跑全量。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1048" not in h:
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
             for p, k in ((RBLOCK, "R1048"), (RSTATUS, "R1048"), (RVERDICT, "第 1048 轮"), (BACKLOG, "R1048")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1048: R1047 closes green, and only two of the seven gaps are gaps\n\n"
         "R1047 was left unrun when memory ran out. The suite ran first this round and is green -- 2258 passing, zero\n"
         " failing -- with freshness at zero and the count unchanged, so R1047's conclusion stands and the discipline\n"
         " holds: unrun is written as unrun, and only a rerun makes it green.\n\n"
         "Then the substance of criterion (f), which asks every uncovered item to say why. Last round I counted four\n"
         " real gaps by the test 'the image names it and the ledger has no row'. Classifying each one says two.\n\n"
         "BotDeflector and Vercel are genuine missing rows. Stripe challenge and PayPal 3DS are not: they are payment\n"
         " challenges belonging to the payment layer, and PayPal's nine staged strings are evidence in their own right\n"
         " that 3DS has eight observable stages. captcha, proof of work and checkpoint are challenge types the row shape\n"
         " should not model at all -- and the image spells one of them 'challange', which the table keeps rather than\n"
         " correcting.\n\n"
         "So the test was too loose and its number twice too large. What was wrong was not the evidence but the\n"
         " classification: a payment challenge and a generic challenge type look exactly like a missing vendor under a\n"
         " test that only asks whether the ledger has a row. That is R1042's shape again, where fourteen unknowns turned\n"
         " out to be three different states and the count hid the difference.\n\n"
         "The dispositions are hand-written judgements, so the generator has a guard against its own staleness: a name\n"
         " it has no entry for renders as 'unclassified, which is the generator's gap and not a conclusion', rather than\n"
         " quietly joining the not-this-table group.\n\n"
         "Figures: suite 2258 green, freshness zero, count 174,293 at 62.89 per cent, thirty-six Solving strings naming\n"
         " thirteen solvers, seven ledger rows, seven gaps of which two are real, and the coverage document growing\n"
         " from 2,059 to 4,466 bytes to carry the classification.\n\n"
         "Next: add the two rows, deciding Solver for BotDeflector first, since having no third-party pointer does not\n"
         " make it self-hosted.\n\n"
         "The lesson is that criterion (f)'s instruction to say why each item is uncovered is not a formality -- the\n"
         " answer differs completely by kind, and the kind has to be decided before the why can be true."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d" % r.returncode)
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
                   cwd=ROOT, capture_output=True, text=True)
    log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
    print("  " + log.stdout.strip().replace("\n", "\n  "))
    st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
    print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))


if __name__ == "__main__":
    main()