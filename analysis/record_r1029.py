"""Record R1029: two axes, and the honest Unknown for the pair that only knows it calls somebody."""

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
### 一个列换成两个轴；而 kasada/akamai 标 `Unknown` 是**刻意的**（R1029）

**R1028 诊断说「`How` 想同时答两件事，下一轮换成两个轴」。换了。**

### ① 两个轴

```csharp
public enum Solver { None, Local, SelfHosted, UserThirdParty, Unknown }
public sealed record Row(..., Solver Solver, bool Relayed);
```

| vendor | `Solver` | `Relayed` | 依据 |
|---|---|---|---|
| cloudflare | **`UserThirdParty`** | **true** | `ApiKey` + `Balance` + `BalanceSupported` + `IsFetchingBalance` · `/v1/warm` |
| datadome | **`SelfHosted`** | **true** | `datadome.cybersole.io/sensor` |
| kasada | **`Unknown`** | false | `API down (Contact staff)`，无 solver 类，无中继 |
| akamai | **`Unknown`** | false | 同 |
| perimeterx | `Local` | false | `Solving PerimeterX`，无 host 无 key |
| queue-it | `Local` | false | `Error Solving Queue-it (Softblock)` |
| imperva | `None` | false | 无解 |

**→ 而 cloudflare 与 datadome **都** `Relayed = true` 而 `Solver` 不同，
kasada 与 akamai **都** `Unknown` 而 `Relayed = false` —— **两个轴确实独立**。**

### ② 而 `Unknown` 用在这里是**刻意的**

**kasada/akamai 的词汇说 `API down (Contact staff)` —— 那只证明**别人**在解，不证明是谁。
→ 而没有 solver 类（`DataDomeSolver` 那类 0 命中）也没有中继 host。**

**→ 所以给它们 `UserThirdParty` 会是一次**同形的推断** —— 用一条症状反推机制，而这已经错了两次。**
**→ 所以那两行说 `Unknown`，而那正是这个值被加进来的理由。**

### ③ 而这次改动里我的脚本错了**四次**

| 次 | 错 | 补 |
|---|---|---|
| 1 | 替换时吞掉行尾的 `)` | 补 `)` |
| 2 | 补 `)` 的匹配形不对（行尾是 `,`） | 匹配 `Relayed = X,` |
| 3 | 补成 `)` 而集合初始化器需要 `),` | 补 `,` |
| 4 | 写成命名实参 `Relayed = true`，而 `Row` 是**位置**构造 | 改位置实参 |

**→ 四次都是**同一个动作（改七行构造调用）的四个不同细节**，而每一次我都以为改完了。
→ 而那与 R1029 之前那些轮的区别在于：这次是**机械错误**，不是判断错误 ——
但代价一样（四次构建）。**

**→ 教训不是「小心点」，是：改七处同形调用时，**先改一处并构建**，再批量。**

### ④ 6 条守卫，其中一条钉「两轴独立」

| 守卫 | 断言 |
|---|---|
| `CloudflareIsSolvedByAUserSuppliedService` | `UserThirdParty` + `Relayed` |
| `DataDomeIsSolvedByTheOriginalsOwnService` | `SelfHosted` + `Relayed` |
| `TheOutageLineVendorsSayTheyDoNotKnowWhoSolves` | kasada/akamai = `Unknown` 且不中转 |
| `TheRestAreLocalOrNone` | `Local` = 两家 · `None` = imperva |
| **`TheTwoAxesAreIndependent`** | **中转跨多种 solver** 且 **`Local` 且不中转 = 2** |
| `UnknownIsUsedByExactlyTheOutagePair` | `Unknown` 恰好是那两家 |

**→ 第 5 条是这次拆分的**意义**：如果两个轴总是一起变，拆分就只是把一个值换成两个值。**

### ⑤ 数字

| 度量 | R1028 | **R1029** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0** |
| 产物陈旧度 | 4 / 3,869 | **4 / 3,879** |
| 函数数 | 174,336 | **174,336** |
| **`How`** | 1 列（改过 2 次） | **拆成 2 列** |
| **`Solver` 取值在用** | — | **5（None · Local · SelfHosted · UserThirdParty · Unknown）** |
| **`Relayed` 为真的厂商** | — | **2** |
| **两轴独立的守卫** | 0 | **1** |
| **本轮脚本错误** | — | **4（同一动作四个细节）** |

### 教训

> **拆一个列之后要问的是：这两个新列会不会总是一起动。**
> **→ 若会，那拆分只是把一个值换成两个值，问题还在。**
> **→ 而 `Relayed` 跨 `UserThirdParty` 与 `SelfHosted` 两种 solver，`Local` 两家都不中转 ——
> 那就是独立性，而它恰好也是**为什么必须拆**的理由。**
"""

if "一个列换成两个轴" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1029 轮：一个列换成两个轴；而 kasada/akamai 标 `Unknown` 是刻意的

### ① 两个轴

```csharp
public enum Solver { None, Local, SelfHosted, UserThirdParty, Unknown }
public sealed record Row(..., Solver Solver, bool Relayed);
```

| vendor | `Solver` | `Relayed` |
|---|---|---|
| cloudflare | **`UserThirdParty`** | **true** |
| datadome | **`SelfHosted`** | **true** |
| kasada · akamai | **`Unknown`** | false |
| perimeterx · queue-it | `Local` | false |
| imperva | `None` | false |

**→ cloudflare 与 datadome 都中转而 solver 不同；kasada 与 akamai 都 `Unknown` 而不中转 ⇒ **两轴独立**。**

### ② 而 `Unknown` 用在这里是**刻意的**

**kasada/akamai 的 `API down (Contact staff)` 只证明**别人**在解，不证明是谁 ——
无 solver 类、无中继 host。给它们 `UserThirdParty` 会是一次**同形的推断**，而那已经错了两次。**

### ③ 而这次改动里我的脚本错了**四次**

| 次 | 错 |
|---|---|
| 1 | 替换时吞掉行尾 `)` |
| 2 | 补 `)` 的匹配形不对（行尾是 `,`） |
| 3 | 补成 `)` 而集合初始化器需要 `),` |
| 4 | 写成命名实参，而 `Row` 是**位置**构造 |

**→ 四次都是**同一个动作的四个不同细节**，每次我都以为改完了。代价：四次构建。
→ 教训不是「小心点」，是：改七处同形调用时，**先改一处并构建，再批量。****

### ④ 6 条守卫，第 5 条是拆分的**意义**

`CloudflareIsSolvedByAUserSuppliedService` · `DataDomeIsSolvedByTheOriginalsOwnService` ·
`TheOutageLineVendorsSayTheyDoNotKnowWhoSolves` · `TheRestAreLocalOrNone` ·
**`TheTwoAxesAreIndependent`** · `UnknownIsUsedByExactlyTheOutagePair`

**→ 如果两轴总是一起变，拆分只是把一个值换成两个值。**

### ⑤ 数字

| 度量 | R1028 | **R1029** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0** |
| 产物陈旧度 | 4 / 3,869 | **4 / 3,879** |
| 函数数 | 174,336 | **174,336** |
| **`How`** | 1 列（改 2 次） | **拆成 2 列** |
| **`Solver` 在用取值** | — | **5** |
| **`Relayed` 为真** | — | **2** |
| **本轮脚本错误** | — | **4** |

### 教训

> **拆一个列之后要问：这两个新列会不会总是一起动。若会，拆分只是把一个值换成两个值。
> → 而 `Relayed` 跨 `UserThirdParty` 与 `SelfHosted`，`Local` 两家都不中转 ——
> 那就是独立性，而它恰好也是**为什么必须拆**的理由。**
"""

BACKLOG_ADD = """

## 优先级 ② — **`How` 拆成 `Solver` + `Relayed` 两轴；kasada/akamai 刻意标 `Unknown`**（R1029）

### 两个轴

```csharp
public enum Solver { None, Local, SelfHosted, UserThirdParty, Unknown }
public sealed record Row(..., Solver Solver, bool Relayed);
```

| vendor | Solver | Relayed | 依据 |
|---|---|---|---|
| cloudflare | `UserThirdParty` | true | `ApiKey`+`Balance`+`BalanceSupported`+`IsFetchingBalance` · `/v1/warm` |
| datadome | `SelfHosted` | true | `datadome.cybersole.io/sensor` |
| kasada · akamai | `Unknown` | false | `API down`，无 solver 类，无中继 |
| perimeterx · queue-it | `Local` | false | 有 Solving 文案，无 host 无 key |
| imperva | `None` | false | 无解 |

### 而 `Unknown` 是刻意的

**`API down` 只证明**别人**在解，不证明是谁。给 `UserThirdParty` 会是同形的推断（已错两次）。**

### 6 条守卫

含 **`TheTwoAxesAreIndependent`**（若两轴总是一起动，拆分无意义）。

### 而这次我的脚本错了 4 次

吞 `)` → 匹配形错 → 缺 `,` → 命名实参 vs 位置构造。
**教训：改七处同形调用时，先改一处并构建，再批量。**

### 数字

**套件 2243/0/0 · 陈旧度 4 / 3,879 · 函数数 174,336 · How 1 列 → 2 列 · Solver 5 值 · Relayed 2 家**

| 仍 Unknown | |
|---|---|
| kasada/akamai 具体是哪个第三方 | 未取证 |
| `Type` 有哪些 solver 取值 | 未取证 |

**纪律**：拆分后要问两个新列会不会总是一起动。
"""

BLOCKER = """

---

## 453. **`How` 拆成 `Solver` + `Relayed` 两轴；kasada/akamai 刻意标 `Unknown`**

> R1029。**改 1 个源文件 + 1 个测试文件。** 套件 **2243 通过 / 0 失败 / 0 跳过**。

### 一、两个轴

```csharp
public enum Solver { None, Local, SelfHosted, UserThirdParty, Unknown }
public sealed record Row(..., Solver Solver, bool Relayed);
```

| vendor | `Solver` | `Relayed` | 依据 |
|---|---|---|---|
| cloudflare | **`UserThirdParty`** | **true** | `ApiKey` + `Balance` + `BalanceSupported` + `IsFetchingBalance` · `/v1/warm` |
| datadome | **`SelfHosted`** | **true** | `datadome.cybersole.io/sensor` |
| kasada | **`Unknown`** | false | `API down (Contact staff)`，无 solver 类，无中继 |
| akamai | **`Unknown`** | false | 同 |
| perimeterx | `Local` | false | `Solving PerimeterX`，无 host 无 key |
| queue-it | `Local` | false | `Error Solving Queue-it (Softblock)` |
| imperva | `None` | false | 无解 |

**→ cloudflare 与 datadome **都** `Relayed = true` 而 `Solver` 不同；
  kasada 与 akamai **都** `Unknown` 而 `Relayed = false` —— **两个轴确实独立**。**

### 二、而 `Unknown` 用在这里是**刻意的**

**kasada/akamai 的词汇说 `API down (Contact staff)` —— 那只证明**别人**在解，不证明是谁。
→ 而没有 solver 类也没有中继 host。
→ 所以给它们 `UserThirdParty` 会是一次**同形的推断** —— 用一条症状反推机制，而这已经错了两次。
→ 所以那两行说 `Unknown`，而那正是这个值被加进来的理由。**

### 三、而这次改动里我的脚本错了**四次**

| 次 | 错 | 补 |
|---|---|---|
| 1 | 替换时吞掉行尾的 `)` | 补 `)` |
| 2 | 补 `)` 的匹配形不对（行尾是 `,`） | 匹配 `Relayed = X,` |
| 3 | 补成 `)` 而集合初始化器需要 `),` | 补 `,` |
| 4 | 写成命名实参 `Relayed = true`，而 `Row` 是**位置**构造 | 改位置实参 |

**→ 四次都是**同一个动作（改七行构造调用）的四个不同细节**，而每一次我都以为改完了。
→ 代价：四次构建。**

**→ 教训不是「小心点」，是：改七处同形调用时，**先改一处并构建**，再批量。**

### 四、6 条守卫

| 守卫 | 断言 |
|---|---|
| `CloudflareIsSolvedByAUserSuppliedService` | `UserThirdParty` + `Relayed` |
| `DataDomeIsSolvedByTheOriginalsOwnService` | `SelfHosted` + `Relayed` |
| `TheOutageLineVendorsSayTheyDoNotKnowWhoSolves` | kasada/akamai = `Unknown` 且不中转 |
| `TheRestAreLocalOrNone` | `Local` = 两家 · `None` = imperva |
| **`TheTwoAxesAreIndependent`** | **中转跨多种 solver** 且 **`Local` 且不中转 = 2** |
| `UnknownIsUsedByExactlyTheOutagePair` | `Unknown` 恰好是那两家 |

**→ 第 5 条是这次拆分的**意义**：如果两个轴总是一起变，拆分就只是把一个值换成两个值。**

### 五、数字

| 度量 | R1028 | R1029 |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0** |
| 产物陈旧度 | 4 / 3,869 | **4 / 3,879** |
| 函数数 | 174,336 | **174,336** |
| **`How`** | 1 列（改过 2 次） | **拆成 2 列** |
| **`Solver` 取值在用** | — | **5** |
| **`Relayed` 为真的厂商** | — | **2** |
| **两轴独立的守卫** | 0 | **1** |
| **本轮脚本错误** | — | **4（同一动作四个细节）** |

### 六、验证

```
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~Vendor" -m:1               -> 53 通过
python tools/metrics_report.py -> 完整套件 exit 0  2243 / 0 / 0
```

### 七、仍然 Unknown

- **kasada / akamai 具体是哪个第三方**：**未取证**。
- **`Type` 有哪些 solver 取值**：**未取证**。

### 八、教训

**拆一个列之后要问的是：这两个新列会不会总是一起动。**

**→ 若会，那拆分只是把一个值换成两个值，问题还在。
→ 而 `Relayed` 跨 `UserThirdParty` 与 `SelfHosted` 两种 solver，`Local` 两家都不中转 ——
  那就是独立性，而它恰好也是**为什么必须拆**的理由。**

**→ 另一条：改七处同形调用时先改一处并构建，再批量 —— 本轮我的脚本在同一动作上错了四次。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1029", BLOCKER)
    ensure(RSTATUS, "R1029", BLOCKER)
    ensure(RVERDICT, "第 1029 轮", VERDICT)
    ensure(BACKLOG, "R1029", BACKLOG_ADD)

    note = (
        "\n## R1029 补充 — **`How` 拆成 `Solver` + `Relayed` 两轴；kasada/akamai 刻意标 `Unknown`**（套件 2243）\n\n"
        "**两个轴**：`Solver { None, Local, SelfHosted, UserThirdParty, Unknown }` + `bool Relayed`。\n"
        "cloudflare = `UserThirdParty`/true · datadome = `SelfHosted`/true · kasada·akamai = `Unknown`/false ·\n"
        "perimeterx·queue-it = `Local`/false · imperva = `None`/false。\n"
        "→ cloudflare 与 datadome 都中转而 solver 不同；kasada/akamai 都 Unknown 而不中转 ⇒ **两轴独立**。\n\n"
        "**`Unknown` 是刻意的**：`API down (Contact staff)` 只证明**别人**在解，不证明是谁。\n"
        "给它们 `UserThirdParty` 会是同形的推断（已错两次）⇒ 两行说 `Unknown`，那正是这个值存在的理由。\n\n"
        "**而这次我的脚本在同一动作上错了 4 次**：吞 `)` → 匹配形错 → 缺 `,` → 命名实参 vs 位置构造。\n"
        "→ 教训：改七处同形调用时，**先改一处并构建，再批量**。\n\n"
        "**6 条守卫**，含 **`TheTwoAxesAreIndependent`**（若两轴总是一起动，拆分无意义）。\n\n"
        "数字：套件 2243/0/0 · 陈旧度 4 / 3,879 · 函数数 174,336 · How 1 列 → **2 列** · Solver **5** 值 · Relayed **2** 家。\n\n"
        "纪律：**拆分后要问两个新列会不会总是一起动。**\n\n"
        "下一轮：kasada/akamai 的具体第三方（`Type` 枚举可能是线索）；或换回优先级 ①。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1029" not in h:
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
             for p, k in ((RBLOCK, "R1029"), (RSTATUS, "R1029"), (RVERDICT, "第 1029 轮"), (BACKLOG, "R1029")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1029: the How column becomes two axes, and two vendors are deliberately Unknown\n\n"
         "R1028 diagnosed the column rather than editing it a third time: one value was answering who solves and whether\n"
         " the original relays, and Cloudflare satisfies both. This round splits it.\n\n"
         "Solver is None, Local, SelfHosted, UserThirdParty or Unknown, and Relayed is a separate bool. Cloudflare is\n"
         " UserThirdParty because its property set is a paid service the user configures -- ApiKey, Balance,\n"
         " BalanceSupported, IsFetchingBalance beside a Type -- and Relayed because cf-solver.cybersole.io warms it.\n"
         " DataDome is SelfHosted and Relayed, since datadome.cybersole.io/sensor is the original's own service.\n\n"
         "Kasada and Akamai are Unknown on purpose. Their vocabulary says API down (Contact staff), which establishes that\n"
         " somebody else solves and not who, and there is neither a solver class nor a relay host to name. Calling them\n"
         " UserThirdParty would be the same inference from a symptom to a mechanism that has now been wrong twice, so the\n"
         " column says it does not know -- which is what that value was added for two rounds ago.\n\n"
         "Six guards pin it. The one that matters asks whether the axes are independent, because a split where both\n"
         " columns always move together is just one column with extra steps: relaying spans two solver kinds, and the two\n"
         " Local vendors do not relay.\n\n"
         "The scripted edit itself was wrong four times in one action -- a dropped paren, a pattern that did not match the\n"
         " trailing comma, a comma missing where the collection initialiser needed it, and named arguments against a\n"
         " positional record. Four builds to land seven identical lines. The lesson is not care, it is to change one and\n"
         " build before changing the rest.\n\n"
         "Figures: suite 2243 unchanged, freshness four files and 3,879 lines, count 174,336, one column becoming two,\n"
         " five solver values in use, two vendors relaying, and one guard asserting the split is real.\n\n"
         "Unknown: which service Kasada and Akamai call, and what Type can be set to.\n\n"
         "The lesson is that after splitting a column the question to ask is whether the new ones always move together,\n"
         " because if they do nothing has been gained.\n\n"
         "One source file and one test file changed; suite green at 2243."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()