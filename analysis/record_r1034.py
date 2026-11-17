"""Record R1034: the two ledgers now name each other, and the tool can see a templated path."""

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
### 两份台账现在互相点名；而工具此前**看不见**任何含模板的路径（R1034）

**R1033 说下一轮加 `sent` 格并联通两份台账。做了，而做的时候发现了一个比台账更底层的 bug。**

### ① 那个 bug：工具的 `ledger_classes()` 与 `inline_scan()` 格式不同

```python
inline_scan:      invented.append((name, line, prefix + "{...}"))     # 截断形
ledger_classes:   set(re.findall(r"-\\s+`(?:live|fixture|assembled)`\\s+`([^`]+)`", body))   # 完整形
unknown = [row for row in invented if row[2] not in allowed]          # 两边直接比
```

**→ 扫描器报的是 `prefix + "{...}"`，而台账存的是**完整字面量** ⇒ **含模板的路径永远匹配不上，
无论登记得多仔细。****

**→ 所以那 4 条（`/api/ff-products/v1/products/{pid}/` · `/api/basket/v1/` ·
`.../payment` · `api.nike.com/.../{CountryCode}/...`）在旧代码下**不可能**被登记成功。**

**→ 而那解释了 R1033 的一个现象：我把 6 条写进测试台账而工具数不动 —— 一半原因是读错文件，
另一半是**即使读对文件，4 条也匹配不上**。**

### ② 修法：两边形都接受

```python
for lit in literals:
    allowed.add(lit)                      # 完整形
    brace = lit.find("{")
    if brace > 0:
        allowed.add(lit[:brace] + "{...}")   # 截断形
```

**→ 而 `sent` 成为第五个分类。它的含义精确：**这个请求真的会发出去，而镜像里没有这条路由，
也没有活的响应证据可以引用** —— 不是 fixture（保留它不验证任何东西），也不是待定（已经判过）。**

### ③ 而 `ledger_classes()` 的 docstring 原本也错了

**它的正则里**早就有** `assembled`，而 docstring 写着「registers as `live` or `fixture`」。
→ 那是 R1011 那条「注释与代码不一致」的又一个实例 —— 而它是无害的，因为代码对。**

### ④ 结果

```
修前:  registered in ledger: 29   unknown: 12   exit 1
修后:  registered in ledger: 41   unknown:  0   exit 0
```

**→ 41 = 29 + 12（6 条 × 完整/截断两种形）。
→ 而 `unknown: 0` 与 `exit 0` 是**这个门第一次真的变绿** —— 不是靠放宽，是靠让判据能看见。**

### ⑤ 而 4 条守卫钉住「互不引用」这个缺陷本身

| 守卫 | 断言 |
|---|---|
| `TheProvenanceLedgerNamesTheRatchet` | 台账正文含 `EndpointEvidenceRatchetTests` |
| `TheRatchetNamesTheProvenanceLedger` | 测试文件含 `ENDPOINT_PROVENANCE` |
| `TheLedgerHasTheSentClass` | 有 `## sent` 段且 ≥6 条 |
| **`EverySentPathIsKnownToTheRatchet`** | **台账里每条 `sent` 路径也在棘轮里出现** |

**→ 第 4 条是**一致性**：两份台账对「存在什么」不能再有分歧。
→ 而前两条钉的是那个**根因** —— 一份在 `docs/`、一份在 `tests/`，没有一处交叉引用。**

### ⑥ 数字

| 度量 | R1033 | **R1034** |
|---|---|---|
| 套件 | 2243 / 0 | **2247 / 0 / 0（+4）** |
| 产物陈旧度 | 5 / 4,199 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **端点门 `unknown`** | 12 | **0** |
| **端点门 exit** | **1（红）** | **0（绿）** |
| **`registered in ledger`** | 29 | **41** |
| **可被登记的模板路径** | **0（格式不匹配）** | **全部** |
| **台账分类数** | 4 | **5（+`sent`）** |
| **两份台账的交叉引用** | 0 | **2（双向）** |

### 教训

> **那个 bug 的形状是：**生产者截断，消费者不截断，而两者直接比较。**
> **→ 而它不会报错 —— 它只是让「登记」这个动作**永远无效**，而无效的样子和「没登记」一模一样。**
> **→ 而我是通过「我明明登记了为什么数不动」这个矛盾找到它的 ——
> 那个矛盾是这一轮唯一有价值的东西，因为它逼我去看**判据怎么比的**，而不是**我做了什么**。**
"""

if "两份台账现在互相点名" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1034 轮：两份台账互相点名；而工具此前看不见任何含模板的路径

### ① 那个 bug：生产端截断，消费端不截断，两者直接比较

```python
inline_scan:      invented.append((name, line, prefix + "{...}"))   # 截断形
ledger_classes:   re.findall(r"-`(?:live|fixture|assembled)`\\s+`([^`]+)`")   # 完整形
unknown = [row for row in invented if row[2] not in allowed]
```

**→ 含模板的路径**永远匹配不上**，无论登记得多仔细。
→ 所以那 4 条（Farfetch 三条 + Nike 一条）在旧代码下**不可能**登记成功。
→ 那也解释了 R1033：我把 6 条写进测试台账而数不动 —— 一半是读错文件，**另一半是即使读对也匹配不上**。**

### ② 修法：两边形都接受

```python
allowed.add(lit)
if (brace := lit.find("{")) > 0:
    allowed.add(lit[:brace] + "{...}")
```

**而 `sent` 成为第五个分类：**真的会发出去、镜像里没有这条路由、也没有活的响应证据** ——
不是 fixture（保留它不验证任何东西），也不是待定（已经判过）。**

### ③ 而 `ledger_classes()` 的 docstring 也错了

**正则里**早有** `assembled`，而 docstring 写「只认 `live` 或 `fixture`」—— 无害，因为代码对。**

### ④ 结果

```
修前:  registered 29   unknown 12   exit 1
修后:  registered 41   unknown  0   exit 0
```

**→ 41 = 29 + 12（6 条 × 两种形）。而这是**这个门第一次真的变绿** —— 不是放宽，是让判据能看见。**

### ⑤ 4 条守卫钉住「互不引用」这个缺陷本身

`TheProvenanceLedgerNamesTheRatchet` · `TheRatchetNamesTheProvenanceLedger` ·
`TheLedgerHasTheSentClass` · **`EverySentPathIsKnownToTheRatchet`**

**→ 前两条钉根因（一份在 `docs/`、一份在 `tests/`，无交叉引用）；第 4 条钉一致性。**

### ⑥ 数字

| 度量 | R1033 | **R1034** |
|---|---|---|
| 套件 | 2243 / 0 | **2247 / 0 / 0（+4）** |
| 产物陈旧度 | 5 / 4,199 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **端点门 `unknown`** | 12 | **0** |
| **端点门 exit** | **1（红）** | **0（绿）** |
| **`registered in ledger`** | 29 | **41** |
| **可被登记的模板路径** | **0** | **全部** |
| **台账分类数** | 4 | **5（+`sent`）** |
| **交叉引用** | 0 | **2（双向）** |

### 教训

> **那个 bug 的形状：**生产者截断，消费者不截断，而两者直接比较。**
> **→ 它不报错 —— 它只是让「登记」这个动作**永远无效**，而无效的样子和「没登记」一模一样。**
> **→ 我是通过「我明明登记了为什么数不动」这个矛盾找到它的。
> → 那个矛盾是这一轮唯一有价值的东西，因为它逼我去看**判据怎么比的**，而不是**我做了什么**。**
"""

BACKLOG_ADD = """

## 判据 (d) — **端点门第一次真绿：`unknown` 12 → 0；原因是格式不匹配的真 bug**（R1034）

### 那个 bug

```python
inline_scan  → prefix + "{...}"       # 截断形
ledger_classes → 完整字面量            # 完整形
unknown = invented if not in allowed   # 直接比
```

**→ 含模板的路径**永远匹配不上**。那 4 条（Farfetch 三 + Nike 一）旧代码下不可能登记成功。**

### 修

**两边形都接受；`sent` 成为第五类**（真的发、镜像无此路由、无活响应证据 —— 非 fixture 非待定）。**

### 结果

```
registered 29 → 41      unknown 12 → 0      exit 1 → 0
```

**→ 这个门第一次真绿：不是放宽，是让判据能看见。**

### 4 条守卫

`TheProvenanceLedgerNamesTheRatchet` · `TheRatchetNamesTheProvenanceLedger` ·
`TheLedgerHasTheSentClass` · **`EverySentPathIsKnownToTheRatchet`**

### 数字

**套件 2247（+4）· 陈旧度 5 / 4,199 · 函数数 174,336 · unknown 12 → 0 · registered 29 → 41 ·
台账分类 4 → 5 · 交叉引用 0 → 2**

| 仍 Unknown | |
|---|---|
| 那 6 条该继续发还是改报告 | 现在有 `sent` 格，可判了 |
| `endpoint constants: unresolved 4`（Warhammer IdentityHost 模板） | 未处理 |

**纪律**：生产端截断 + 消费端不截断 = 登记永远无效，而无效与没登记同形。
"""

BLOCKER = """

---

## 458. **两份台账互相点名；而工具此前看不见任何含模板的路径**

> R1034。**改工具 1、台账 1、测试 1 新 + 1 旧。** 套件 **2247 通过 / 0 失败 / 0 跳过**。
> **端点门 `unknown` 12 → 0，exit 1 → 0。**

### 一、那个 bug：生产端截断，消费端不截断，两者直接比较

```python
inline_scan:      invented.append((name, line, prefix + "{...}"))     # 截断形
ledger_classes:   set(re.findall(r"-\\s+`(?:live|fixture|assembled)`\\s+`([^`]+)`", body))   # 完整形
unknown = [row for row in invented if row[2] not in allowed]          # 两边直接比
```

**→ 扫描器报的是 `prefix + "{...}"`，而台账存的是**完整字面量** ⇒ **含模板的路径永远匹配不上，
  无论登记得多仔细。**

**→ 所以那 4 条（`/api/ff-products/v1/products/{pid}/` · `/api/basket/v1/` ·
  `.../payment` · `api.nike.com/.../{CountryCode}/...`）在旧代码下**不可能**被登记成功。**

**→ 而那解释了 R1033 的一个现象：我把 6 条写进测试台账而工具数不动 —— 一半原因是读错文件，
  另一半是**即使读对文件，4 条也匹配不上**。**

### 二、修法：两边形都接受

```python
for lit in literals:
    allowed.add(lit)                      # 完整形
    brace = lit.find("{")
    if brace > 0:
        allowed.add(lit[:brace] + "{...}")   # 截断形
```

**→ 而 `sent` 成为第五个分类。它的含义精确：**这个请求真的会发出去，而镜像里没有这条路由，
  也没有活的响应证据可以引用** —— 不是 fixture（保留它不验证任何东西），也不是待定（已经判过）。**

### 三、而 `ledger_classes()` 的 docstring 原本也错了

**它的正则里**早就有** `assembled`，而 docstring 写着「registers as `live` or `fixture`」。
→ 那是 R1011 那条「注释与代码不一致」的又一个实例 —— 而它是无害的，因为代码对。**

### 四、结果

```
修前:  registered in ledger: 29   unknown: 12   exit 1
修后:  registered in ledger: 41   unknown:  0   exit 0
```

**→ 41 = 29 + 12（6 条 × 完整/截断两种形）。
→ 而 `unknown: 0` 与 `exit 0` 是**这个门第一次真的变绿** —— 不是靠放宽，是靠让判据能看见。**

### 五、4 条守卫钉住「互不引用」这个缺陷本身

| 守卫 | 断言 |
|---|---|
| `TheProvenanceLedgerNamesTheRatchet` | 台账正文含 `EndpointEvidenceRatchetTests` |
| `TheRatchetNamesTheProvenanceLedger` | 测试文件含 `ENDPOINT_PROVENANCE` |
| `TheLedgerHasTheSentClass` | 有 `## sent` 段且 ≥6 条 |
| **`EverySentPathIsKnownToTheRatchet`** | **台账里每条 `sent` 路径也在棘轮里出现** |

### 六、数字

| 度量 | R1033 | R1034 |
|---|---|---|
| 套件 | 2243 / 0 | **2247 / 0 / 0（+4）** |
| 产物陈旧度 | 5 / 4,199 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **端点门 `unknown`** | 12 | **0** |
| **端点门 exit** | **1（红）** | **0（绿）** |
| **`registered in ledger`** | 29 | **41** |
| **可被登记的模板路径** | **0（格式不匹配）** | **全部** |
| **台账分类数** | 4 | **5（+`sent`）** |
| **两份台账的交叉引用** | 0 | **2（双向）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse\\replica
python tools/endpoint-provenance.py   -> registered 41 · unknown 0 · exit 0
dotnet test --filter "FullyQualifiedName~EndpointLedgerLink|~EndpointEvidenceRatchet" -m:1 -> 7 通过
python tools/metrics_report.py -> 完整套件 exit 0  2247 / 0 / 0
```

### 八、仍然 Unknown

- **那 6 条该继续发还是改报告**：**现在有 `sent` 格，可判了**。
- **`endpoint constants: unresolved 4`**（Warhammer 的 `IdentityHost` 模板）：**未处理**。

### 九、教训

**那个 bug 的形状是：**生产者截断，消费者不截断，而两者直接比较。**

**→ 而它不会报错 —— 它只是让「登记」这个动作**永远无效**，而无效的样子和「没登记」一模一样。**

**→ 而我是通过「我明明登记了为什么数不动」这个矛盾找到它的 ——
  那个矛盾是这一轮唯一有价值的东西，因为它逼我去看**判据怎么比的**，而不是**我做了什么**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1034", BLOCKER)
    ensure(RSTATUS, "R1034", BLOCKER)
    ensure(RVERDICT, "第 1034 轮", VERDICT)
    ensure(BACKLOG, "R1034", BACKLOG_ADD)

    note = (
        "\n## R1034 补充 — **端点门第一次真绿：`unknown` 12 → 0，原因是格式不匹配的真 bug**（套件 2247）\n\n"
        "**那个 bug**：`inline_scan` 报 `prefix + \"{...}\"`（截断形），而 `ledger_classes()` 比的是**完整字面量**，\n"
        "两者直接比 ⇒ **含模板的路径永远匹配不上**。那 4 条（Farfetch 三 + Nike 一）旧代码下**不可能**登记成功。\n"
        "→ 也解释了 R1033：一半是读错文件，**另一半是即使读对也匹配不上**。\n\n"
        "**修**：两边形都接受；`sent` 成为第五类（真的发、镜像无此路由、无活响应证据 —— 非 fixture 非待定）。\n\n"
        "```\nregistered 29 → 41      unknown 12 → 0      exit 1 → 0\n```\n"
        "**→ 这是这个门**第一次真的变绿** —— 不是放宽，是靠让判据能看见。**\n\n"
        "**4 条守卫**：两份台账**双向点名** + `sent` 段 ≥6 条 + **`EverySentPathIsKnownToTheRatchet`**（一致性）。\n\n"
        "数字：套件 2247（+4）· 陈旧度 5 / 4,199 · 函数数 174,336 · unknown **12 → 0** · registered **29 → 41** ·\n"
        "台账分类 **4 → 5** · 交叉引用 **0 → 2**。\n\n"
        "纪律：**生产端截断 + 消费端不截断 = 登记永远无效，而无效与没登记同形。**\n\n"
        "下一轮：`endpoint constants: unresolved 4`（Warhammer 的 `IdentityHost` 模板）；或判那 6 条该发还是改报告。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1034" not in h:
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
             for p, k in ((RBLOCK, "R1034"), (RSTATUS, "R1034"), (RVERDICT, "第 1034 轮"), (BACKLOG, "R1034")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1034: the two ledgers now name each other, and the tool could not see a templated path at all\n\n"
         "R1033 ended with six new ledger rows and the tool still reporting twelve, and blamed the round for writing\n"
         " into the ledger nobody reads. That was half of it. The other half was in the tool.\n\n"
         "inline_scan records a templated path as its prefix plus a brace ellipsis. ledger_classes returns the literals\n"
         " written in the markdown, in full. The gate compares those two sets directly, so any path containing a\n"
         " template could never match, however carefully it was registered. Four of the six were of that shape, which\n"
         " means no amount of bookkeeping would have moved the count.\n\n"
         "Both spellings are accepted now, and sent becomes the fifth class: the replica really makes this request, the\n"
         " image names no such route, and there is no live response to cite. Not a fixture, since keeping it tests\n"
         " nothing, and not pending, since it has been judged.\n\n"
         "The gate went from twenty-nine registered and twelve unknown with a non-zero exit, to forty-one registered,\n"
         " zero unknown, and exit zero. That is the first time it has passed, and it passed by letting the criterion see\n"
         " rather than by relaxing it.\n\n"
         "Four guards keep the two ledgers from drifting apart again: each names the other in prose, the sent section\n"
         " exists with at least six rows, and every path filed as sent also appears in the ratchet's own table.\n\n"
         "Figures: suite 2243 to 2247, freshness five files and 4,199 lines, count 174,336, registered up from\n"
         " twenty-nine to forty-one, unknown down from twelve to zero, and two cross-references where there were none.\n\n"
         "Unknown: whether those six should keep being sent or become reports, which the new category now makes\n"
         " answerable, and the four unresolved constants in Warhammer's identity host template.\n\n"
         "The lesson is that when a producer truncates and a consumer does not, registering something is permanently\n"
         " ineffective, and ineffective looks exactly like unregistered. I found it because the count refused to move\n"
         " after I had done the work, and that contradiction forced me to read how the criterion compared rather than\n"
         " what I had done.\n\n"
         "One tool, one ledger, one new test file and one old; suite green at 2247."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()