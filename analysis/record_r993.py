"""Record R993: two status classifiers, one wired and one not, and they disagree on 409."""

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
### 状态码分类在复刻件里有**两份**，而它们在 **409** 上给出相反结论（R993）

**R992 说下一轮核 `RefreshSessionAsync` / `HandleResponseAsync` 是否同形。核到一半发现更有价值的东西：
R985 说「状态码分类字符串层不可得」的那个分类，**复刻件里就有两份**。**

### ① 这两个**不像** `GetToken`

```csharp
RefreshSessionAsync   → 真 GET origin，写 Vars["lastStatus"]，按 IsSuccess 判
HandleResponseAsync   → 完整状态码表（下面）
```

**没有伪造，有实质内容。而 `Vars["lastStatus"]` 是**活的通道**：5 个写入者、4 个读取者，
`StoreFlowRunner.cs:293` 也在读它。**

### ② 而分类有两份，且**只有一份在执行路径上**

| 位置 | 在步骤序列 | 调用点 |
|---|---|---|
| `HandleResponseAsync`（`StoreFlow.cs:349`） | **无** | **0** |
| `ClassifyCheckoutFailure`（`StoreFlowRunner.cs:262`） | **在用**（`LastStatus(ctx)` 读同一变量） | 有 |

**两份的表：**

| 码 | `HandleResponseAsync` | `ClassifyCheckoutFailure` |
|---|---|---|
| 200/201/204 · 3xx | Success | — |
| 400 | Fail 不可重试 | Error |
| 401 / 403 | Fail **可重试** | Error |
| 404 | Fail 不可重试 | Error |
| **409** | **Fail 可重试** | **Declined（终止）** |
| 422 | Fail 不可重试 | **Declined** |
| 429 | Fail 可重试 | Error |
| 5xx · 其它 | Fail 可重试 | Error |

### ③ 而冲突只有一个码，但是最要紧的那个

**`ClassifyCheckoutFailure` 的注释自己写着：**

> 「A 422 means the store understood the request and rejected it — retrying costs time and
> can burn the account. A 409 (sold out during checkout) is the same story.」

**而 `HandleResponseAsync` 把 409 判成**可重试**。**

> **409 = 结账途中售罄。判可重试会**重试一件已经卖掉的东西** ——
> 而那正是注释说「会烧账号」的那一类。**
> **→ 所以把它接上是**危险**的：接之前必须先把 409 对齐。**
> **这与 R992 的 `GetToken` 相反 —— 那个该接、这个不该直接接。**

### ④ 而这也更正了 R985

**R985 说「原版状态码分类在字符串层不可得」。那句仍然对（原版的看不到）。
但我当时没查**复刻件里有没有**，而答案是：有两份。**

> **而 `HISTORY.md` R12 那条「状态码分类（401/403 可重试 vs 422 不可）」描述的就是
> `HandleResponseAsync` —— 那条记录是对的，只是我一直没找到它在哪个文件。**
> **→ 我说「不可得」的时候，缺的不是原版证据，是**一次 `where_is`**。**

### ⑤ 而这一轮**没有**接上它，理由要写清

**接上 `HandleResponseAsync` 会让 409 从「Declined」变成「可重试」。
那需要先决定哪一份表对 —— 而 `ClassifyCheckoutFailure` 的那份**有注释说明理由**，
`HandleResponseAsync` 的那份**没有**。**

> **→ 所以正确的动作是：把 `HandleResponseAsync` 的 409 改成不可重试（与有理由的那份对齐），
> 然后才谈接线。而「改哪一份」需要证据，不是偏好 —— 这一轮没取到。**
> **→ 记进 BLOCKERS，不自己决定。**

### ⑥ 顺手看到的一件事（未追）

**`HandleResponseAsync` 下面就紧挨着 `DetectAsync`（`StoreFlow.cs:368`），
它从响应 body / headers 里识别 anti-bot vendor：**
`cf-chl` → cloudflare · `kpsdk` → kasada · `_Incapsula_Resource` → imperva ·
`datadome` → datadome · `px-captcha` → perimeterx · `queue-it` → queue-it。

**那是优先级 ② 的实质内容。它接上没有、与 `vendor_coverage` 的 12/12 是什么关系 —— 本轮未查。**

### 数字

| 度量 | R992 | **R993** |
|---|---|---|
| 套件 | 2208 | **2208（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **状态码分类器** | 未测 | **2 份（1 份未接上）** |
| **两份之间的冲突码** | 未测 | **1（409）** |

### 教训

> **「不可得」和「我没找到」是两个不同的结论，而我上一轮把它们写成了同一个。
> R985 的证据（原版字符串里没有状态码分类）是对的，而它的**结论范围**被我扩大了 ——
> 从「原版里看不到」变成了「这里没有」。**
> **而一次 `where_is` 就能把范围收回来。**
"""

if "状态码分类在复刻件里有**两份**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 993 轮：状态码分类有两份，而它们在 409 上给出相反结论

### ① 这两个不像 `GetToken`

```csharp
RefreshSessionAsync → 真 GET origin，写 Vars["lastStatus"]，按 IsSuccess 判
HandleResponseAsync → 完整状态码表
```

**没有伪造，有实质内容。`Vars["lastStatus"]` 是活的：5 写入 / 4 读取，`StoreFlowRunner:293` 也在读。**

### ② 而分类有两份，只有一份在执行路径上

| 位置 | 在步骤序列 | 调用点 |
|---|---|---|
| `HandleResponseAsync`（`StoreFlow.cs:349`） | **无** | **0** |
| `ClassifyCheckoutFailure`（`StoreFlowRunner.cs:262`） | **在用**（读同一变量） | 有 |

### ③ 冲突只有一个码，但是最要紧的那个

**`ClassifyCheckoutFailure` 的注释：**

> 「A 422 means the store understood the request and rejected it — retrying costs time and
> can burn the account. A 409 (sold out during checkout) is the same story.」

**而 `HandleResponseAsync` 把 409 判成**可重试**。**

> **409 = 结账途中售罄。判可重试会重试一件已经卖掉的东西 —— 正是注释说「会烧账号」的那一类。
> → 所以接上它是**危险**的；接之前必须先把 409 对齐。
> → 这与 R992 的 `GetToken` 相反：那个该接，这个不该直接接。**

### ④ 而这更正了 R985

**R985 说「原版状态码分类在字符串层不可得」—— 那句仍对（原版看不到）。
但我当时没查**复刻件里有没有**，答案是两份。**

> **`HISTORY.md` R12 那条「401/403 可重试 vs 422 不可」描述的就是 `HandleResponseAsync`。
> 那条记录是对的，只是我一直没找到它在哪个文件。
> → 我说「不可得」时，缺的不是原版证据，是**一次 `where_is`**。**

### ⑤ 这一轮没有接上它

**接上会让 409 从 Declined 变成可重试。要先决定哪一份表对 ——
而 `ClassifyCheckoutFailure` 那份**有注释说明理由**，`HandleResponseAsync` 那份**没有**。
→ 记 BLOCKERS，不自己决定。**

### ⑥ 顺手看到（未追）

**`HandleResponseAsync` 下面紧挨着 `DetectAsync`（`StoreFlow.cs:368`）——
从 body/headers 识别 anti-bot vendor：`cf-chl`→cloudflare · `kpsdk`→kasada ·
`_Incapsula_Resource`→imperva · `datadome` · `px-captcha`→perimeterx · `queue-it`。
那是优先级 ② 的实质内容。接上没有、与 vendor 12/12 什么关系 —— 未查。**

### 数字

| 度量 | R992 | **R993** |
|---|---|---|
| 套件 | 2208 | **2208（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **状态码分类器** | 未测 | **2 份（1 份未接上）** |
| **冲突码** | 未测 | **1（409）** |

### 教训

> **「不可得」和「我没找到」是两个不同的结论，而我上一轮把它们写成了同一个。
> R985 的证据是对的，而它的**结论范围**被我扩大了 —— 从「原版里看不到」变成「这里没有」。
> 一次 `where_is` 就能把范围收回来。**
"""

BACKLOG_ADD = """

## 优先级 ①/③ — **状态码分类两份并存，409 上冲突；`HandleResponseAsync` 未接上**（R993）

### Observation

| 位置 | 在步骤序列 | 调用点 | 409 |
|---|---|---|---|
| `HandleResponseAsync`（`StoreFlow.cs:349`） | **无** | **0** | **可重试** |
| `ClassifyCheckoutFailure`（`StoreFlowRunner.cs:262`） | **在用** | 有 | **Declined** |

**`ClassifyCheckoutFailure` 有注释说明理由（「A 409 (sold out during checkout) is the same story」），
`HandleResponseAsync` 没有。**

**`Vars["lastStatus"]` 是活通道：5 写入 / 4 读取（含 `StoreFlowRunner:293`）。**

### 处置（本轮未做，需先定哪份表对）

**接上 `HandleResponseAsync` 会让 409 从 Declined 变可重试 = 重试已卖出的东西。
→ 必须先把 409 对齐，再谈接线。**「改哪一份」需要证据，不是偏好。

### 更正 R985

**R985「原版状态码分类字符串层不可得」仍对，但它被我扩大成「这里没有」。
复刻件里有两份；`HISTORY.md` R12 那条描述的就是 `HandleResponseAsync`。
缺的不是原版证据，是一次 `where_is`。**

### 数字

**套件 2208（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 分类器 2 份 · 冲突码 1（409）**

| 仍 Unknown | |
|---|---|
| 两份表哪一份对 | 需证据（镜像侧状态码语义） |
| `DetectAsync` 接上没有 | 未查 —— 优先级 ② 的实质内容 |

**纪律**：「不可得」和「我没找到」是两个结论。
"""

BLOCKER = """

---

## 417. **状态码分类两份并存，409 冲突；`HandleResponseAsync` 未接上**

> R993。**只取证，未改代码。** 套件 **2208（R992 的记录仍有效）**。

### 一、这两个不像 `GetToken`

```csharp
RefreshSessionAsync → 真 GET origin，写 Vars["lastStatus"]，按 IsSuccess 判
HandleResponseAsync → 完整状态码表
```

**→ 没有伪造，有实质内容。
→ `Vars["lastStatus"]` 是**活通道**：5 个写入者 · 4 个读取者，`StoreFlowRunner.cs:293` 也在读它。**

### 二、而分类有两份，只有一份在执行路径上

| 位置 | 在步骤序列 | 调用点 |
|---|---|---|
| `HandleResponseAsync`（`StoreFlow.cs:349`） | **无** | **0** |
| `ClassifyCheckoutFailure`（`StoreFlowRunner.cs:262`） | **在用**（`LastStatus(ctx)` 读同一变量） | 有 |

**两份的表：**

| 码 | `HandleResponseAsync` | `ClassifyCheckoutFailure` |
|---|---|---|
| 200/201/204 · 3xx | Success | — |
| 400 | Fail 不可重试 | Error |
| 401 / 403 | Fail **可重试** | Error |
| 404 | Fail 不可重试 | Error |
| **409** | **Fail 可重试** | **Declined（终止）** |
| 422 | Fail 不可重试 | **Declined** |
| 429 | Fail 可重试 | Error |
| 5xx · 其它 | Fail 可重试 | Error |

### 三、冲突只有一个码，但是最要紧的那个

**`ClassifyCheckoutFailure` 的注释自己写着：**

> 「A 422 means the store understood the request and rejected it — retrying costs time and can burn the account.
>  A 409 (sold out during checkout) is the same story.」

**而 `HandleResponseAsync` 把 409 判成**可重试**。**

**→ 409 = 结账途中售罄。判可重试会**重试一件已经卖掉的东西**，而那正是注释说「会烧账号」的那一类。
→ 所以把它接上是**危险**的：接之前必须先把 409 对齐。
→ **这与 R992 的 `GetToken` 相反 —— 那个该接、这个不该直接接。****

### 四、而这更正了 R985

**R985 说「原版状态码分类在字符串层不可得」。那句仍然对（原版看不到）。
但我当时没查**复刻件里有没有**，而答案是：有两份。**

**→ `HISTORY.md` R12 那条「状态码分类（401/403 可重试 vs 422 不可）」描述的就是 `HandleResponseAsync`。
→ 那条记录是对的，只是我一直没找到它在哪个文件。
→ **我说「不可得」的时候，缺的不是原版证据，是一次 `where_is`。****

### 五、这一轮**没有**接上它

**接上 `HandleResponseAsync` 会让 409 从「Declined」变成「可重试」。
那需要先决定哪一份表对 —— 而 `ClassifyCheckoutFailure` 那份**有注释说明理由**，
`HandleResponseAsync` 那份**没有**。**

**→ 正确的动作是：先把 `HandleResponseAsync` 的 409 改成不可重试（与有理由的那份对齐），然后才谈接线。
→ 「改哪一份」需要证据，不是偏好 —— 本轮没取到，记 BLOCKERS，不自己决定。**

### 六、顺手看到（未追）

**`HandleResponseAsync` 下面就紧挨着 `DetectAsync`（`StoreFlow.cs:368`），
从 body / headers 识别 anti-bot vendor：**

```
cf-chl            → cloudflare      kpsdk              → kasada
_Incapsula_Resource → imperva       datadome           → datadome
px-captcha        → perimeterx      queue-it           → queue-it
```

**→ 那是优先级 ② 的实质内容。它接上没有、与 `vendor_coverage` 的 12/12 是什么关系 —— 本轮未查。**

### 七、数字

| 度量 | R992 | R993 |
|---|---|---|
| 套件 | 2208 | **2208（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **状态码分类器** | 未测 | **2 份（1 份未接上）** |
| **两份之间的冲突码** | 未测 | **1（409）** |

### 八、验证

```
cd replica
python - 扫 src 找 RefreshSessionAsync / HandleResponseAsync 的 DEF 与 CALL -> 各 1 个 DEF，0 个 CALL
python - 扫 StoreFlowSteps.cs -> 两个名字都不在里面
python - 扫 Vars["lastStatus"] -> 5 写入 / 4 读取
python - 读 src/Cybersole.Stores/Flows/StoreFlow.cs:349-367 与 StoreFlowRunner.cs:258-275
```

### 九、仍然 Unknown

- **两份表哪一份对**：**Unknown** —— 需要镜像侧的状态码语义证据。
- **`DetectAsync` 接上没有**：**Unknown** —— 未查；它是优先级 ② 的实质内容。

### 十、教训

**「不可得」和「我没找到」是两个不同的结论，而我上一轮把它们写成了同一个。**

**R985 的证据（原版字符串里没有状态码分类）是对的，而它的**结论范围**被我扩大了 ——
从「原版里看不到」变成了「这里没有」。而一次 `where_is` 就能把范围收回来。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R993", BLOCKER)
    ensure(RSTATUS, "R993", BLOCKER)
    ensure(RVERDICT, "第 993 轮", VERDICT)
    ensure(BACKLOG, "R993", BACKLOG_ADD)

    note = (
        "\n## R993 补充 — **状态码分类两份并存，409 冲突；`HandleResponseAsync` 未接上**（套件 2208，未改代码）\n\n"
        "`HandleResponseAsync`（`StoreFlow.cs:349`）与 `ClassifyCheckoutFailure`（`StoreFlowRunner.cs:262`）\n"
        "读同一个 `Vars[\"lastStatus\"]`，各自有一份状态码表，而**只有后者在执行路径上**\n"
        "（前者不在任何步骤序列、无调用点）。\n\n"
        "**两份只在一个码上冲突，而那是 409：**\n"
        "`ClassifyCheckoutFailure` → **Declined（终止）**，注释写着「A 409 (sold out during checkout) is the same story」；\n"
        "`HandleResponseAsync` → **可重试**。\n"
        "→ 409 = 结账途中售罄，判可重试会重试一件已卖出的东西。**所以接上它是危险的；接之前必须先对齐 409。**\n\n"
        "**而这也更正 R985**：「原版状态码分类字符串层不可得」仍对，但它被我扩大成「这里没有」。\n"
        "复刻件里有两份；`HISTORY.md` R12 那条描述的就是 `HandleResponseAsync`。**缺的不是原版证据，是一次 `where_is`。**\n\n"
        "**未接上的理由**：`ClassifyCheckoutFailure` 那份有注释说明理由，`HandleResponseAsync` 那份没有；\n"
        "「改哪一份」需要证据而非偏好 → 记 BLOCKERS。\n\n"
        "顺手看到未追：`HandleResponseAsync` 下面紧挨 `DetectAsync`（`StoreFlow.cs:368`），从 body/headers 识别\n"
        "cf-chl / kpsdk / _Incapsula_Resource / datadome / px-captcha / queue-it —— **优先级 ② 的实质内容**。\n\n"
        "数字：套件 2208（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 分类器 2 份 · 冲突码 1（409）。\n\n"
        "纪律：**「不可得」和「我没找到」是两个结论。**\n\n"
        "下一轮：查 `DetectAsync` 接上没有 —— 那是优先级 ② 最实质的一块。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R993" not in h:
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
             for p, k in ((RBLOCK, "R993"), (RSTATUS, "R993"), (RVERDICT, "第 993 轮"), (BACKLOG, "R993")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R993: two status classifiers exist and they disagree on 409\n\n"
         "R992 left RefreshSessionAsync and HandleResponseAsync to be checked for the same defect as GetToken. They do not\n"
         " share it: neither fabricates anything and both do real work. What they led to is better.\n\n"
         "Status classification exists twice in the replica. HandleResponseAsync carries a full table and is connected to\n"
         " nothing -- no step sequence, no caller. ClassifyCheckoutFailure reads the same session variable and is on the\n"
         " execution path, through LastStatus in the runner. The variable between them is live, with five writers and four\n"
         " readers.\n\n"
         "The two tables agree almost everywhere and differ on one code, which happens to be the one that matters. For 409\n"
         " HandleResponseAsync says retryable; ClassifyCheckoutFailure says Declined, and its own comment gives the reason:\n"
         " a 409 during checkout is a sold-out, retrying burns time and can burn the account. So wiring the unwired one up\n"
         " would make the replica retry something already sold. That inverts R992's conclusion about the token step: that\n"
         " one should be connected, this one should not be connected until 409 is aligned first.\n\n"
         "It also corrects R985. That round's evidence stands -- the original's classification produces no strings -- but I\n"
         " widened its scope from \"not visible in the original\" to \"not present here\", and the second was never checked.\n"
         " Status classification is here twice, and the line in the replica's own history describing 401 and 403 as\n"
         " retryable against 422 not was describing HandleResponseAsync all along. What was missing was a where_is, not\n"
         " evidence from the binary.\n\n"
         "No code changed. Deciding which table is right needs evidence rather than preference, and only one of the two\n"
         " carries a stated reason, so the disagreement goes to the blocker list.\n\n"
         "Noted and not chased: DetectAsync sits immediately below and identifies anti-bot vendors from response bodies and\n"
         " headers -- cloudflare, kasada, imperva, datadome, perimeterx, queue-it. That is the substance of priority two and\n"
         " whether it is connected has not been looked at.\n\n"
         "Figures: suite 2208 unchanged, freshness zero, count 173,952, two classifiers with one unwired, one conflicting\n"
         " code.\n\n"
         "Unknown: which of the two tables is right, needing the original's status semantics; and whether DetectAsync is\n"
         " wired.\n\n"
         "The lesson is that \"not obtainable\" and \"I did not find it\" are different conclusions, and I wrote the second as\n"
         " the first.\n\n"
         "No product code changed; one conflict recorded and one earlier conclusion narrowed."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()