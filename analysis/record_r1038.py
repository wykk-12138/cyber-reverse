"""Record R1038: the control disproved R1036's premise, and Farfetch is covered rather than absent."""

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
### 对照查询推翻了 R1036 的前提；Farfetch 是**未覆盖**而不是**多余**（R1038）

**R1037 说下一轮做那个对照查询，它决定 R1036 是否要撤回。做了，而答案是**要撤回** —— 但撤的不是我以为的那部分。**

### ① 对照：已知支持的站，名字在不在池里

```
nike.com         40 (AT CAP)   → accounts.nike.com · api.nike.com
footlocker.com    8            → images.footlocker.com · www.footlocker.com
supreme.com       6            → eu/jp/shop.supreme.com
mywarhammer.com   6            → login.mywarhammer.com
mattel.com       10            → creations.mattel.com
```

**→ 域名字面量**通常**在池里 ⇒ R1036 那个前提「域名以字面量出现」**大体成立**。**
**→ 而两个我以为的反例都是**我拼错了**：`zalando.` 带点查不到 `ZalandoAndroidMobile`；`asos.com` 查不到 `ASOS Sample Sale`。**

### ② 而裸词查询把结论翻了过来

```
farfetch        3  → 0x14338eadc "Farfetch" · 0x146d8dfdc "Farfetch" · **0x146d8e004 "Farfetch Checkout"**
farfetch.com    0
ff-products     0
```

**→ `Farfetch` 与 **`Farfetch Checkout` 都在镜像里** ⇒ 原版**确实**有这个站，而且**有结账流程**。
→ 所以 R1036 那句「原版从不提到这个站」**是错的**，而它之所以错，是因为我只查了
**`farfetch.com` 与 `api.farfetch.com`** 两个精确串。**

**→ 那与本轮两次拼写错误是**同一个错**的第三次：
**精确串只能找到它被写成的那种拼写。****

### ③ 所以 Farfetch 的性质变了

| | R1036 说 | R1038 修正 |
|---|---|---|
| 这个站 | **镜像里没有** | **镜像里有（`Farfetch Checkout`）** |
| 缺什么 | 整站 | **transport**（域名与 7 条 API 路由，任何拼写都是 0） |
| 性质 | **多余（addition）** | **未覆盖（gap）** |
| 那 −43 个函数 | 「停止假装」的代价 | **仍然正确** —— 它们服务于编造的请求 |

**→ 而那正是 goal 完成判据 (f) 要的形态：「未覆盖的每条写为什么」。
→ Farfetch 现在有一条合格的记录：**原版有结账流程，我们不知道它怎么说话。****

### ④ 改了什么

**类头从「原版从不提到」改成三段：R1036 的结论被撤回、三条字的地址、以及「域名通常可见而我的反例是拼写错」。
7 条消息从 `the image carries no farfetch.com` 改成 `the original has a Farfetch checkout,
this workspace does not know its transport`。**

**→ 而那让 flow **保留**、步骤**仍然报告**、而那 43 个函数**不恢复** —— 三件事各归其位。**

### ⑤ 而我写的守卫**过严**了一次

**第一版守卫里有两条：禁止文件引用被撤回的那句话（`the original never mentions`）、
禁止出现 `/api/ff-products`。**
**→ 第一条让**撤回无法被写下来** —— 一条守卫不能禁止它保护的那段注释引用它要撤回的话。
→ 收窄成两条正向断言（`Farfetch Checkout` 在 · `does not know its transport` 在）。**

### ⑥ 数字

| 度量 | R1037 | **R1038** |
|---|---|---|
| 套件 | 2252 / 0 | **2254 / 0 / 0（+2）** |
| 产物陈旧度 | 0 / 0 | **1 / 217**（本轮改了 flow） |
| 函数数 | 174,293 | **174,293（不变）** |
| 比例 | 62.89% | **62.89%** |
| **端点门 `unknown`** | 0 | **0** |
| **Farfetch 在镜像里** | 「否」（错） | **是（3 条，含 `Farfetch Checkout`）** |
| **Farfetch 的性质** | 多余 | **未覆盖** |
| **照对照的已知站** | 未做 | **5 个全在** |
| **我的拼写错误** | — | **2 个（zalando / asos），同族第三次** |

### 教训

> **这一轮最有价值的一步不是那个查询，是**先做对照**。
> → 若没有对照，我会停在一个正好相反的结论上，而那个结论**看起来**被一次干净的零支持。**
> **→ 而对照本身也差点骗我：我挑的两个反例都是我拼错的。
> → 所以对照也要问「我用的拼写对吗」—— 而那次我查了变体，才没把 zalando 和 asos 记成缺席。**
"""

if "对照查询推翻了 R1036 的前提" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1038 轮：对照查询推翻了 R1036 的前提；Farfetch 是**未覆盖**不是多余

### ① 对照：已知支持的站，名字在不在池里

```
nike.com 40 · footlocker.com 8 · supreme.com 6 · mywarhammer.com 6 · mattel.com 10
```

**→ 域名字面量**通常**在池里 ⇒ R1036 的前提**大体成立**。
→ 而我以为的两个反例都是**我拼错**：`zalando.` → `ZalandoAndroidMobile`；`asos.com` → `ASOS Sample Sale`。**

### ② 而裸词查询把结论翻了过来

```
farfetch   3  → "Farfetch" ×2 · **"Farfetch Checkout"**
```

**→ 原版**确实**有这个站，且有结账流程 ⇒ R1036 那句「原版从不提到这个站」**是错的**。
→ 它错的原因：我只查了 `farfetch.com` 与 `api.farfetch.com` **两个精确串**。
→ 那是本轮两次拼写错误的**同一个错的第三次**：**精确串只能找到它被写成的那种拼写。****

### ③ 所以性质变了

| | R1036 | **R1038** |
|---|---|---|
| 这个站 | 镜像里没有 | **镜像里有** |
| 缺什么 | 整站 | **transport**（域名 + 7 条路由，任何拼写 0） |
| 性质 | **多余** | **未覆盖** |
| 那 −43 函数 | 「停止假装」的代价 | **仍正确**（服务于编造的请求） |

### ④ 改动

**类头三段（撤回 + 三条地址 + 「域名通常可见而我的反例是拼写错」）；
7 条消息 → `the original has a Farfetch checkout, this workspace does not know its transport`。
→ flow **保留**、步骤**仍报告**、43 个函数**不恢复** —— 三件事各归其位。**

### ⑤ 而我写的守卫**过严**了一次

**第一版禁止文件**引用**被撤回的那句话 ⇒ **撤回本身无法被写下来**。
→ 收窄成两条正向断言（`Farfetch Checkout` 在 · `does not know its transport` 在）。**

### ⑥ 数字

| 度量 | R1037 | **R1038** |
|---|---|---|
| 套件 | 2252 / 0 | **2254 / 0 / 0（+2）** |
| 产物陈旧度 | 0 / 0 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **端点门 `unknown`** | 0 | **0** |
| **Farfetch 在镜像里** | 「否」（错） | **是（3 条）** |
| **Farfetch 的性质** | 多余 | **未覆盖** |

### 教训

> **最有价值的一步不是那个查询，是**先做对照**。
> → 没有对照，我会停在一个正好相反的结论上，而它**看起来**被一次干净的零支持。
> → 而对照本身也差点骗我：两个反例都是我拼错的 ⇒ **对照也要问「我用的拼写对吗」。****
"""

BACKLOG_ADD = """

## 判据 (f) — **对照推翻 R1036：Farfetch 在镜像里（`Farfetch Checkout`）⇒ 未覆盖不是多余**（R1038）

### 对照

```
nike.com 40 · footlocker.com 8 · supreme.com 6 · mywarhammer.com 6 · mattel.com 10   ← 域名通常可见
zalando → ZalandoAndroidMobile · asos → ASOS Sample Sale                            ← 我的两个"反例"是拼写错
```

### 裸词查询翻转结论

```
farfetch 3  → "Farfetch" ×2 · **"Farfetch Checkout"**       farfetch.com 0
```

**→ 原版**确实**有此站且有结账流程 ⇒ R1036 的「原版从不提到」是错的。
→ 错因：只查 `farfetch.com` + `api.farfetch.com` 两个**精确串**。

### 性质修正

| | R1036 | R1038 |
|---|---|---|
| 站 | 没有 | **有** |
| 缺 | 整站 | **transport** |
| 性质 | 多余 | **未覆盖** |
| −43 函数 | 代价 | **仍正确** |

**flow 保留 · 步骤仍报告 · 43 函数不恢复。**

### 而我的守卫过严一次

**禁止引用被撤回的话 ⇒ 撤回无法被写下。收窄成两条正向断言。**

### 数字

**套件 2254（+2）· 陈旧度 1 / 217 · 函数数 174,293 · 比例 62.89% · 门 unknown 0 · Farfetch 3 条证据**

| 仍 Unknown | |
|---|---|
| Farfetch 的 transport 是什么 | 需配置或运行时证据 |
| 产物需重 publish（1 文件陈旧） | 待收尾 |

**纪律**：对照也要问「我用的拼写对吗」；精确串只能找到它被写成的那种拼写。
"""

BLOCKER = """

---

## 462. **对照查询推翻 R1036；Farfetch 是「未覆盖」而不是「多余」**

> R1038。**改 1 个 flow + 1 个测试文件。** 套件 **2254 通过 / 0 失败 / 0 跳过**。
> 端点门 `unknown` 0 · exit 0。

### 一、对照：已知支持的站，名字在不在池里

```
nike.com         40 (AT CAP)   → accounts.nike.com · api.nike.com
footlocker.com    8            → images.footlocker.com · www.footlocker.com
supreme.com       6            → eu/jp/shop.supreme.com
mywarhammer.com   6            → login.mywarhammer.com
mattel.com       10            → creations.mattel.com
```

**→ 域名字面量**通常**在池里 ⇒ R1036 那个前提「域名以字面量出现」**大体成立**。**
**→ 而两个我以为的反例都是**我拼错了**：`zalando.` 带点查不到 `ZalandoAndroidMobile`；
  `asos.com` 查不到 `ASOS Sample Sale`。**

### 二、而裸词查询把结论翻了过来

```
farfetch        3  → 0x14338eadc "Farfetch" · 0x146d8dfdc "Farfetch" · **0x146d8e004 "Farfetch Checkout"**
farfetch.com    0
ff-products     0
```

**→ `Farfetch` 与 **`Farfetch Checkout` 都在镜像里** ⇒ 原版**确实**有这个站，而且**有结账流程**。
→ 所以 R1036 那句「原版从不提到这个站」**是错的**，而它之所以错，是因为我只查了
  **`farfetch.com` 与 `api.farfetch.com`** 两个精确串。**

**→ 那与本轮两次拼写错误是**同一个错的第三次**：
  **精确串只能找到它被写成的那种拼写。****

### 三、所以 Farfetch 的性质变了

| | R1036 说 | R1038 修正 |
|---|---|---|
| 这个站 | **镜像里没有** | **镜像里有（`Farfetch Checkout`）** |
| 缺什么 | 整站 | **transport**（域名与 7 条 API 路由，任何拼写都是 0） |
| 性质 | **多余（addition）** | **未覆盖（gap）** |
| 那 −43 个函数 | 「停止假装」的代价 | **仍然正确** —— 它们服务于编造的请求 |

**→ 而那正是 goal 完成判据 (f) 要的形态：「未覆盖的每条写为什么」。
→ Farfetch 现在有一条合格的记录：**原版有结账流程，我们不知道它怎么说话。****

### 四、改了什么

**类头从「原版从不提到」改成三段：R1036 的结论被撤回、三条字的地址、
  以及「域名通常可见而我的反例是拼写错」。
7 条消息从 `the image carries no farfetch.com` 改成
  `the original has a Farfetch checkout, this workspace does not know its transport`。**

**→ 而那让 flow **保留**、步骤**仍然报告**、而那 43 个函数**不恢复** —— 三件事各归其位。**

### 五、而我写的守卫**过严**了一次

**第一版守卫里有两条：禁止文件引用被撤回的那句话（`the original never mentions`）、
  禁止出现 `/api/ff-products`。**

**→ 第一条让**撤回无法被写下来** —— 一条守卫不能禁止它保护的那段注释引用它要撤回的话。
→ 收窄成两条正向断言（`Farfetch Checkout` 在 · `does not know its transport` 在）。**

### 六、数字

| 度量 | R1037 | R1038 |
|---|---|---|
| 套件 | 2252 / 0 | **2254 / 0 / 0（+2）** |
| 产物陈旧度 | 0 / 0 | **1 / 217**（本轮改了 flow） |
| 函数数 | 174,293 | **174,293（不变）** |
| 比例 | 62.89% | **62.89%** |
| **端点门 `unknown`** | 0 | **0** |
| **Farfetch 在镜像里** | 「否」（错） | **是（3 条，含 `Farfetch Checkout`）** |
| **Farfetch 的性质** | 多余 | **未覆盖** |
| **对照的已知站** | 未做 | **5 个全在** |
| **我的拼写错误** | — | **2 个（zalando / asos），同族第三次** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "farfetch"          -> {"n":3}（含 "Farfetch Checkout"）
python analysis/ida.py str "farfetch\\.com"     -> {"n":0}
python analysis/ida.py str "nike\\.com"         -> {"n":40}（对照：域名可见）
python analysis/ida.py str "zalando"           -> {"n":4}（我的旧反例是拼写错）
cd replica
python tools/endpoint-provenance.py            -> unknown 0 · exit 0
python tools/metrics_report.py -> 完整套件 exit 0  2254 / 0 / 0
```

### 八、仍然 Unknown

- **Farfetch 的 transport 是什么**：**需配置或运行时证据**。
- **产物需重新 publish**（1 文件陈旧）：待收尾。

### 九、教训

**这一轮最有价值的一步不是那个查询，是**先做对照**。**

**→ 若没有对照，我会停在一个正好相反的结论上，而那个结论**看起来**被一次干净的零支持。**

**→ 而对照本身也差点骗我：我挑的两个反例都是我拼错的。
→ 所以对照也要问「我用的拼写对吗」—— 而那次我查了变体，才没把 zalando 和 asos 记成缺席。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1038", BLOCKER)
    ensure(RSTATUS, "R1038", BLOCKER)
    ensure(RVERDICT, "第 1038 轮", VERDICT)
    ensure(BACKLOG, "R1038", BACKLOG_ADD)

    note = (
        "\n## R1038 补充 — **对照推翻 R1036：Farfetch 在镜像里（`Farfetch Checkout`）⇒ 未覆盖不是多余**（套件 2254）\n\n"
        "**对照**：`nike.com` 40 · `footlocker.com` 8 · `supreme.com` 6 · `mywarhammer.com` 6 · `mattel.com` 10\n"
        "⇒ 域名**通常**可见。而我以为的两个反例都是**我拼错**：`zalando.` → `ZalandoAndroidMobile`；\n"
        "`asos.com` → `ASOS Sample Sale`。\n\n"
        "**裸词查询翻转结论**：`farfetch` **3** 条 —— `\"Farfetch\"` ×2 · **`\"Farfetch Checkout\"`**；`farfetch.com` 仍 0。\n"
        "⇒ 原版**确实**有此站且有结账流程 ⇒ R1036 的「原版从不提到」**错**，错因是只查两个**精确串**。\n\n"
        "**性质修正**：站**有** · 缺的是 **transport** · 性质是**未覆盖**（不是多余）· 那 −43 个函数**仍正确**。\n"
        "**flow 保留 · 步骤仍报告 · 43 函数不恢复。**\n\n"
        "**而我的守卫过严一次**：禁止文件引用被撤回的话 ⇒ **撤回无法被写下**。收窄成两条正向断言。\n\n"
        "数字：套件 2254（+2）· 陈旧度 1 / 217 · 函数数 174,293 · 比例 62.89% · 门 unknown 0 ·\n"
        "Farfetch **3** 条证据 · 我的拼写错 **2** 个（同族第三次）。\n\n"
        "纪律：**对照也要问「我用的拼写对吗」；精确串只能找到它被写成的那种拼写。**\n\n"
        "下一轮：publish 清陈旧度；或找 Farfetch 的 transport（配置/运行时）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1038" not in h:
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
             for p, k in ((RBLOCK, "R1038"), (RSTATUS, "R1038"), (RVERDICT, "第 1038 轮"), (BACKLOG, "R1038")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1038: the control disproves R1036, and Farfetch is a gap rather than an addition\n\n"
         "R1037 ended by asking whether a store's domain has to appear as a literal, since R1036 had turned Farfetch\n"
         " into a reporting stub on the strength of farfetch.com returning zero. A control answers it.\n\n"
         "Known stores are visible: nike.com forty times, footlocker.com eight, supreme.com six, mywarhammer.com six,\n"
         " mattel.com ten. So domains usually are literals and a missing one usually means something. My first two\n"
         " counter-examples were my own misspellings -- zalando appears as ZalandoAndroidMobile and asos as ASOS Sample\n"
         " Sale -- which is the third time this round that a precise string found only the spelling it was written for.\n\n"
         "That sent me back to probe the bare word, which R1036 never did. Farfetch appears three times: twice as the\n"
         " store name and once as Farfetch Checkout. The original does have a checkout flow for this store. What is\n"
         " absent is the transport -- the domain and the seven API routes are zero at every spelling tried -- so R1036's\n"
         " sentence about the original never mentioning the store was simply wrong.\n\n"
         "Farfetch is therefore uncovered rather than additional, and the code says the second thing now: the store is\n"
         " real, the routes are unknown. The flow stays, the steps keep reporting, and R1036's forty-three trimmed\n"
         " functions stay trimmed, because they served requests that were invented. Three separate facts, each in its\n"
         " own place.\n\n"
         "My first guard draft forbade the file from quoting R1036's retracted sentence, which made the retraction\n"
         " impossible to write down. A guard can be too strict in a way that fights the comment it protects, so it was\n"
         " narrowed to two positive facts.\n\n"
         "Figures: suite 2252 to 2254, freshness one file and 217 lines since the flow changed after the publish, count\n"
         " 174,293 unchanged at 62.89 per cent, the provenance gate at zero, and three pieces of evidence where the\n"
         " previous round believed there were none.\n\n"
         "Unknown: what Farfetch's transport actually is, which needs configuration or runtime evidence rather than\n"
         " strings.\n\n"
         "The lesson is that the control was worth more than the query, because without it I would have stopped on a\n"
         " conclusion whose opposite is true -- and it looked well supported by a clean zero. The control also nearly\n"
         " fooled me, since both of my counter-examples were misspellings.\n\n"
         "One flow and one test file changed; suite green at 2254."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()