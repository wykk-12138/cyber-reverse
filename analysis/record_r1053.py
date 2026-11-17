"""Record R1053: the payment layer's two gaps, sized, and a correction to R1048's stage count."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 「归支付层」是真的，而那也是**一个没被记下来的缺口**（R1053）

**R1052 把真厂商缺口降到 0，剩 5 个「不属于风控台账」的。其中 2 个是支付挑战，R1048 说「归支付层」。
这一轮去查那一层 —— 而 `where_is` 说两个都**不在**复刻件里。**

### ① 而「归支付层」这句话的漏洞

**R1048 的处置是**正确的**：`Stripe challenge` 与 `PayPal 3DS` 确实不该进 `VendorWiring`。
→ 而那不等于它们被记在别处 —— `where_is PayPal3DS` 与 `where_is StripeChallenge` 都返回 **no hit**。**

**→ 所以「不属于这张表」当时**掩盖**了一个事实：它属于另一张表，而**那张表不存在**。
→ 那正是 (f) 要抓的形状：**未覆盖的项不是消失了，是换了一个看不见的位置。****

### ② 而取证给出了两条的**可实现规格**

```
PayPal 3DS   Solving PayPal 3DS (1) (2) **(2.1)** (3) (4) (5) (6) (7) (8)      ← 9 条
3DS 状态机    Submit3DS · Process3DS · Waiting3DS · Complete3DS               ← 4 态
PayPal solver <SolvePayPal3DS>d__38 · <SolvePayPalHosted3DS>d__39              ← 两个（含 Hosted）
Stripe        SubmitOrderStripe · ProcessOrderStripe · GetStripePaymentIntent
              CreateStripePaymentMethod · SubmitStripeOrder · ValidateStripeIntent
              SetStripePayment · StripeFallbackHandler · StripeTimestamp
              StripeVersion "2025-08-27.basil"
```

**→ 而 `(2.1)` 让 R1048 的一个数字**错了**：它说「9 条分期 ⇒ **8 个可观察阶段**」，
→ 而 `(2.1)` 是阶段 2 之后的**子阶段** ⇒ **可观察阶段是 9 个，不是 8 个**。
→ 那条错法很典型：**把「条数」映射成「阶段数」时假设了一一对应，而 2.1 打破了这个假设。**

### ③ 而「名字出现」≠「实现」—— 这一轮又踩了一次

**第一版生成器只报「复刻件里有没有」，结果 `2/4` 是「有」。而那两个「有」的性质完全不同：**

| 标记 | 出现在 | 性质 |
|---|---|---|
| `PayPal3DS` | `WallSolving.cs:20` | **风控侧提到这个名字** |
| `CreateStripePaymentMethod` | `DemandwareStepMap.cs:32` · `RetailFlows.cs:1214` | **步骤映射表里的名字引用** |
| `StripeChallenge` | — | **完全缺失** |
| `Submit3DS` | — | **完全缺失** |

**→ 所以第一版文档里那句「本工作里一条都没有」是**错的** —— 两条**连名字都没有**，另两条**只在别处被引用**。
→ 而那与 R1042 那条「有文案不等于有 solver」同族，也与 R1048 的「不属于这张表」同族：
**"找得到" 与 "实现了" 之间隔着一次分类。**

**→ 改法：生成器现在报**位置 + 性质**，不报布尔值。**

### ④ 而产物是第四份生成的覆盖文档

`replica/tools/payment_challenges.py` → `replica/docs/PAYMENT_CHALLENGES.md`（3,497 字节），
每次运行重探 12 个串（含 `kpsdk` 对照）并重扫 `src/` 的标记。

**→ 而四份文档现在各答一个问题：**

| 文档 | 答什么 |
|---|---|
| `CORE_COVERAGE.md` | 复刻件有多少 flow / 端点有没有据 / 原版站清单（Unknown） |
| `VENDOR_COVERAGE.md` | 原版点名哪些求解对象 ↔ `VendorWiring` 逐条对 |
| `FINGERPRINT_VOCAB.md` | 指纹层的名字哪些有据、哪些是本地约定 |
| **`PAYMENT_CHALLENGES.md`** | **两条支付挑战的规模与复刻件侧缺口** |

### ⑤ 数字

| 度量 | R1052 | **R1053** |
|---|---|---|
| **套件** | 2257 / 1（网络 flaky） | **2258 / 0 / 0（绿 —— 那个 flaky 这次也过了）** |
| 产物陈旧度 | 3 / 650 | **3 / 650** |
| 函数数 | 174,293 | **174,293** |
| **`PayPal 3DS` 分期文案** | 「9 条」 | **9（含 `(2.1)`）** |
| **3DS 可观察阶段** | 「8 个」（错） | **9 个** |
| **3DS 状态机** | 未知 | **4 态** |
| **PayPal solver 体** | 未知 | **2（普通 + Hosted）** |
| **Stripe 方法名** | 未知 | **9 个 + API 版本常量** |
| **复刻件里实现它们的** | 未查 | **0 处**（2 个名字被引用，2 个完全缺失） |
| **`PAYMENT_CHALLENGES.md`** | 不存在 | **3,497 字节（生成）** |

### 教训

> **「归到另一张表」不是「记下来了」。R1048 的分类是对的，而它把一个缺口移出了视野 ——
> 而**移出视野与解决，在台账里长得一样**。**
> **→ 而这一轮的第二个教训：`(2.1)` 说明「N 条文案 ⇒ N 个阶段」是一个**假设**。
> → 与 R1048 那条「撞到就算缺」是同一个错的另一面：**用计数代替结构。****
"""

if "「归支付层」是真的，而那也是" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1053 —— **「归支付层」是没被记下来的缺口；两条支付挑战已量化；套件 2258 绿**

### ① 而「归支付层」的漏洞

`where_is PayPal3DS` 与 `where_is StripeChallenge` 都 **no hit** ⇒ R1048 说「归支付层」是**对的**，
而那一层**不存在** ⇒ **「不属于这张表」当时掩盖了「属于另一张不存在的表」。**
**→ 移出视野与解决，在台账里长得一样。**

### ② 取证：两条的规格

```
PayPal 3DS   (1) (2) **(2.1)** (3) (4) (5) (6) (7) (8)   ← 9 条；**(2.1) 是 2 之后的子阶段**
3DS 状态机    Submit3DS · Process3DS · Waiting3DS · Complete3DS     ← 4 态
PayPal solver <SolvePayPal3DS> · <SolvePayPalHosted3DS>              ← 2（普通 + Hosted）
Stripe        9 个方法 + StripeFallbackHandler + StripeVersion "2025-08-27.basil"
```

**⇒ R1048 的「8 个可观察阶段」**错了**：`(2.1)` 打破「N 条 = N 阶段」这个假设 ⇒ **9 个阶段**。**

### ③ 而「名字出现」≠「实现」—— 又踩一次

| 标记 | 出现在 | 性质 |
|---|---|---|
| `PayPal3DS` | `WallSolving.cs:20` | 风控侧提到名字 |
| `CreateStripePaymentMethod` | `DemandwareStepMap.cs:32` · `RetailFlows.cs:1214` | 步骤映射表引用 |
| `StripeChallenge` / `Submit3DS` | — | **完全缺失** |

**⇒ 第一版文档那句「一条都没有」是错的；现在生成器报**位置 + 性质**，不报布尔值。**

### ④ 四份覆盖文档各答一问

`CORE_COVERAGE`（flow/端点/站清单）· `VENDOR_COVERAGE`（风控逐条对）·
`FINGERPRINT_VOCAB`（指纹名字有据否）· **`PAYMENT_CHALLENGES`（支付挑战规模与缺口）**。

### 数字

| 度量 | R1052 | **R1053** |
|---|---|---|
| 套件 | 2257 / 1（flaky） | **2258 / 0 / 0 绿** |
| 陈旧度 | 3 / 650 | **3 / 650** |
| 函数数 | 174,293 | **174,293** |
| 3DS 阶段 | 「8」（错） | **9** |
| 复刻件实现 | 未查 | **0 处** |
| `PAYMENT_CHALLENGES.md` | — | **3,497 字节** |

**纪律**：「归到另一张表」不是「记下来了」；「N 条文案 = N 个阶段」是一个会被 `(2.1)` 打破的假设。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1053", NOTE)
append(RBLOCK, "R1053", "\n---\n\n## 477. **「归支付层」是没被记下来的缺口；两条支付挑战已量化**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1053: belonging to another table is not the same as being recorded\n\n"
     "R1052 brought genuine vendor gaps to zero and left five items the ledger classifies as not belonging to it. Two\n"
     " are payment challenges, and R1048's ruling that they belong to the payment layer is correct. where_is then\n"
     " returns nothing for either, which makes the ruling a way of moving a gap out of sight rather than closing it --\n"
     " the same outcome in a ledger as solving it would produce.\n\n"
     "Taking the image's text for both gives them a size. PayPal 3DS carries nine staged strings including a 2.1,\n"
     " which corrects R1048's reading of eight observable stages: the extra one is a sub-stage of the second, and nine\n"
     " strings are nine stages, not eight. The 3DS state machine is four names, submit, process, wait and complete, and\n"
     " PayPal has two solver bodies, the ordinary and the hosted variant. Stripe has a full chain -- config, intent,\n"
     " method, submit, validate -- with a fallback handler and an API version constant.\n\n"
     "My first version of the document answered whether the replica contains each marker, and reported two of four as\n"
     " yes. Those two turned out to be a mention in a risk file and a name referenced from a step map. Neither is the\n"
     " challenge being implemented, so the sentence I had written -- that this workspace has none of it -- was wrong in\n"
     " a way that mattered: two markers have no name here at all, and the other two are only spoken of elsewhere. The\n"
     " generator now reports where a marker appears and what kind of appearance it is, rather than a boolean.\n\n"
     "That is R1042's text-versus-solver point again, and R1048's classification point again: between found and\n"
     " implemented there is always a classification step, and skipping it produces a confident wrong answer.\n\n"
     "Figures: suite green at 2258 with the network flake from last round passing, which is what makes it a flake;\n"
     " freshness three files and 650 lines; count 174,293; nine 3DS stages where the previous round said eight; nine\n"
     " Stripe method names; zero places implementing either challenge; and a fourth generated coverage document at\n"
     " 3,497 bytes.\n\n"
     "Unknown: the wire protocol inside those Stripe and PayPal bodies, which needs decompilation rather than string\n"
     " search, and is the next step for this layer.\n\n"
     "The lesson is that classification can be correct and still hide a gap, and that counting strings into stages\n"
     " assumes a one-to-one mapping which a single sub-stage is enough to break."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
