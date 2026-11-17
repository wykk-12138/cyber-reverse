"""Record R1033: two ledgers that never met, and six paths with no category to file under."""

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
### 两份台账互不知道对方；而那 6 条**没有类可归**（R1033）

**R1032 说下一轮按两个前置条件补账。补了 —— 用整行锚点、用真实字面量 —— 而工具的 12 **一点没动**。**

### ① 工具读的是**另一份**台账

```
endpoint-provenance.py:250
LEDGER = os.path.join(os.path.dirname(ROOT), "replica", "docs", "ENDPOINT_PROVENANCE.md")
LEDGER_CLASSES = 只认 `live` 与 `fixture`
```

**→ 仓里有**两份**端点台账：**

| 台账 | 谁读它 | 条目数 | 我的改动 |
|---|---|---|---|
| `tests/Cybersole.Tests/EndpointEvidenceRatchetTests.cs` | 那三个棘轮守卫 | `Sent` 10 + `DocumentedOnly` 7 = **17** | **已加 6 条，绿** |
| `replica/docs/ENDPOINT_PROVENANCE.md` | `endpoint-provenance.py` | `live` 1 · `fixture` 3 · `待定` 24 · `assembled` 21 | **未动** |

**→ 所以我改了一份台账，而工具读另一份 ⇒ `registered in ledger: 29` 不变，`unknown` 仍是 12。
→ 而两份台账**都不知道对方存在** —— 没有一处代码或文档交叉引用它们。**

### ② 而工具的台账只有四种分类，那 6 条**哪一种都不是**

| 分类 | 定义 | 那 6 条 |
|---|---|---|
| `live` | 有真实响应证据 | **没有**（从未对真站发过） |
| `fixture` | 故意保留的不存在路径，用测试禁止 | **不是**（它们在真的结账链里） |
| `待定` | 既不在镜像也无数响应证据 | 24 条，**那 6 条不在其中** |
| `assembled` | 用流程自己的 origin 拼出来的 | **部分是**（`/discount/` · `/api/payments/` 用 `Origin(c.Url)`） |

**→ 而 `ledger_classes()` 只把 `live` 与 `fixture` 算作「已登记」。
→ 所以即使我把那 6 条放进 `assembled`，工具**仍然**会报它们。**

**→ 而 `BASELINE = 0` 的注释写着「R201: all 24 judged and registered」——
那句话对**当时那 24 条**是真的，而那 6 条**从来没进过那 24 条**。**

### ③ 所以本轮做完的是**第一份台账**，而它确实做完了

**5 处标注 + 6 条账 + ceiling 10 → 16，而棘轮 3/3 绿、全量 2243 / 0 / 0。**

**→ 而我用的是 R1032 那两条前置条件：
① 整行锚点替换（不找 `//` 边界）—— 5 处全部一次成功，**没有再劈开 URL**。
② 真实字面量（`https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified`）
—— `StillInItsFile` 直接绿。**
**→ 所以两条前置条件是**有效**的，而它们省下的正好是上一轮的三次回滚。**

### ④ 而真正的结论是：**那 6 条没有归宿，不是因为没人记，而是因为没有地方记**

**→ 它们是真的在用、真的无据、也不是故意保留的负例。
→ 而台账的分类里没有「真的在用但无据」这一格 —— `待定` 的意思是「还没判」，不是「判过了就这样」。**

**→ 所以下一步不是把它们塞进现有分类（那是把「没归宿」伪装成「有归宿」），
而是**加一格**（例如 `sent`），并让 `ledger_classes()` 认它。
→ 而那一格的含义是精确的：**这个请求真的会发出去，而镜像里没有它**。**

### ⑤ 数字

| 度量 | R1032 | **R1033** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0** |
| 产物陈旧度 | 5 / 4,199 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **棘轮 `Sent`** | 10 | **16** |
| **棘轮守卫** | 3 绿（回滚后） | **3 绿（带 6 条新账）** |
| **补标注** | 0（两次改坏） | **5 处，一次成功** |
| **工具的 `unknown`** | 12 | **12（未变）** |
| **端点台账份数** | 未注意 | **2（互不引用）** |
| **工具的台账分类** | 未注意 | **4，且那 6 条无类可归** |

### 教训

> **我上一轮把「补账」理解成「把条目写进台账」。而仓里有两份台账，我写进了没人读的那份。**
> **→ 而那不全是疏忽：`ENDPOINT_PROVENANCE.md` 在 `docs/`，测试在 `tests/` —— 两个地方，
> 两个名字，没有一处交叉引用。**
> **→ 所以「查一下有没有现成的」（AGENTS §2.7c）在这里该有个变体：
> **查一下这个东西有没有**两个**现成的，而我要改的是哪一个。****
"""

if "两份台账互不知道对方" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1033 轮：两份台账互不知道对方；而那 6 条没有类可归

### ① 工具读的是**另一份**台账

```python
endpoint-provenance.py:250
LEDGER = .../replica/docs/ENDPOINT_PROVENANCE.md     ← 只认 `live` 与 `fixture`
```

| 台账 | 谁读它 | 条目 | 本轮改动 |
|---|---|---|---|
| `tests/.../EndpointEvidenceRatchetTests.cs` | 三个棘轮守卫 | **17** | **加 6 条，绿** |
| `replica/docs/ENDPOINT_PROVENANCE.md` | `endpoint-provenance.py` | live 1 · fixture 3 · 待定 24 · assembled 21 | **未动** |

**→ 我改了没人读的那份 ⇒ `registered in ledger: 29` 不变，`unknown` 仍 12。
→ 两份台账**互不引用**。**

### ② 而工具的台账只有四种分类，那 6 条**哪一种都不是**

| 分类 | 那 6 条 |
|---|---|
| `live`（有响应证据） | **没有** |
| `fixture`（故意的不存在路径） | **不是**（在真的结账链里） |
| `待定`（24 条，还没判） | **那 6 条不在其中** |
| `assembled`（用流程自己的 origin 拼） | **部分**（`/discount/` · `/api/payments/`） |

**→ 而 `ledger_classes()` 只把 `live`/`fixture` 算作已登记 ⇒ 塞进 `assembled` 也仍会报。
→ `BASELINE = 0` 的注释说「all 24 judged and registered」—— 对**那 24 条**是真的，而那 6 条**从未进过**。**

### ③ 而第一份台账确实做完了

**5 处标注 + 6 条账 + `SentCeiling` 10 → 16，棘轮 3/3 绿、全量 2243/0/0。
→ 用的是 R1032 那两条前置条件：**整行锚点替换**（5 处一次成功，没再劈 URL）+
**真实字面量**（Nike 那条用完整的 `{CountryCode}/Nike/SNKRS?format=simplified`）。
→ 两条前置条件**有效** —— 省下的正好是上一轮的三次回滚。**

### ④ 而真正的结论：那 6 条**不是因为没人记，而是因为没有地方记**

**→ 真的在用、真的无据、也不是故意的负例 —— 而台账分类里没有「真的在用但无据」这一格。
→ `待定` 的意思是「还没判」，不是「判过了就这样」。**

**→ 所以下一步不是塞进现有分类（那是把「没归宿」伪装成「有归宿」），而是**加一格** `sent`，
并让 `ledger_classes()` 认它 —— 那一格的含义精确：**这个请求真的会发出去，而镜像里没有它。**

### ⑤ 数字

| 度量 | R1032 | **R1033** |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0** |
| 产物陈旧度 | 5 / 4,199 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **棘轮 `Sent`** | 10 | **16** |
| **补标注** | 0（两次改坏） | **5 处，一次成功** |
| **工具的 `unknown`** | 12 | **12（未变）** |
| **端点台账份数** | 未注意 | **2（互不引用）** |
| **工具台账分类** | 未注意 | **4，那 6 条无类可归** |

### 教训

> **我上一轮把「补账」理解成「写进台账」，而仓里有两份，我写进了没人读的那份。
> → 那不全是疏忽：一份在 `docs/`，一份在 `tests/`，两个名字，没有一处交叉引用。**
> **→ 所以 AGENTS §2.7c「先查有没有现成的」在这里有个变体：
> **查一下这个东西有没有**两个**现成的，而我要改的是哪一个。****
"""

BACKLOG_ADD = """

## 判据 (d)(f) — **两份端点台账互不引用；那 6 条在工具的分类里无类可归**（R1033）

### 两份台账

| 台账 | 谁读 | 条目 | 本轮 |
|---|---|---|---|
| `tests/.../EndpointEvidenceRatchetTests.cs` | 三个棘轮守卫 | 17 | **加 6，绿** |
| `replica/docs/ENDPOINT_PROVENANCE.md` | `endpoint-provenance.py` | live 1 · fixture 3 · 待定 24 · assembled 21 | 未动 |

**工具只把 `live`/`fixture` 算作已登记 ⇒ 改测试那份不动工具的数（仍 12）。**

### 那 6 条无类可归

**`live` 无响应证据 · `fixture` 不是负例 · `待定` 那 24 条不含它们 · `assembled` 只部分吻合。
→ `BASELINE = 0` 的「all 24 judged」对那 24 条真，对这 6 条从未适用。**

### 下一步（不是塞进现有分类，是加一格）

**加 `sent`：**真的会发出去，而镜像里没有它**。让 `ledger_classes()` 认它。**

### 而 R1032 的两条前置条件**有效**

**整行锚点替换（5 处一次成功，未劈 URL）+ 真实字面量（Nike 用完整模板串）⇒ 省下三次回滚。**

### 数字

**套件 2243/0/0 · 陈旧度 5 / 4,199 · 函数数 174,336 · Sent 10→16 · 标注 5 处 · 工具 unknown 12 不变 · 台账 2 份**

| 仍 Unknown | |
|---|---|
| 那 6 条该继续发还是改报告 | 需先有 `sent` 格 |

**纪律**：查一下这个东西有没有**两个**现成的，而我要改的是哪一个。
"""

BLOCKER = """

---

## 457. **两份端点台账互不引用；那 6 条在工具的分类里无类可归**

> R1033。**改 1 个测试文件 + 3 个源文件（5 处标注）。** 套件 **2243 通过 / 0 失败 / 0 跳过**。

### 一、工具读的是**另一份**台账

```
endpoint-provenance.py:250
LEDGER = os.path.join(os.path.dirname(ROOT), "replica", "docs", "ENDPOINT_PROVENANCE.md")
LEDGER_CLASSES = 只认 `live` 与 `fixture`
```

| 台账 | 谁读它 | 条目数 | 本轮改动 |
|---|---|---|---|
| `tests/Cybersole.Tests/EndpointEvidenceRatchetTests.cs` | 那三个棘轮守卫 | `Sent` 10 + `DocumentedOnly` 7 = **17** | **加 6 条，绿** |
| `replica/docs/ENDPOINT_PROVENANCE.md` | `endpoint-provenance.py` | `live` 1 · `fixture` 3 · `待定` 24 · `assembled` 21 | **未动** |

**→ 我改了一份台账，而工具读另一份 ⇒ `registered in ledger: 29` 不变，`unknown` 仍是 12。
→ 两份台账**互不引用** —— 没有一处代码或文档交叉引用它们。**

### 二、而工具的台账只有四种分类，那 6 条**哪一种都不是**

| 分类 | 定义 | 那 6 条 |
|---|---|---|
| `live` | 有真实响应证据 | **没有** |
| `fixture` | 故意保留的不存在路径 | **不是**（在真的结账链里） |
| `待定` | 既不在镜像也无响应证据 | 24 条，**不含那 6 条** |
| `assembled` | 用流程自己的 origin 拼出来 | **部分**（`/discount/` · `/api/payments/`） |

**→ 而 `ledger_classes()` 只把 `live` 与 `fixture` 算作已登记。
→ 所以即使放进 `assembled`，工具**仍然**会报。
→ 而 `BASELINE = 0` 的注释写着「R201: all 24 judged and registered」——
  那句话对**当时那 24 条**是真的，而那 6 条**从来没进过那 24 条**。**

### 三、而第一份台账确实做完了

**5 处标注 + 6 条账 + `SentCeiling` 10 → 16，棘轮 3/3 绿、全量 2243 / 0 / 0。**

**→ 用的是 R1032 那两条前置条件：
  ① 整行锚点替换（不找 `//` 边界）—— 5 处一次成功，**没有再劈开 URL**。
  ② 真实字面量（`https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified`）
     —— `StillInItsFile` 直接绿。
→ 所以两条前置条件是**有效**的，而它们省下的正好是上一轮的三次回滚。**

### 四、真正的结论：**那 6 条没有归宿，不是因为没人记，而是因为没有地方记**

**→ 真的在用、真的无据、也不是故意保留的负例。
→ 而台账的分类里没有「真的在用但无据」这一格 —— `待定` 的意思是「还没判」，不是「判过了就这样」。**

**→ 所以下一步不是把它们塞进现有分类（那是把「没归宿」伪装成「有归宿」），
  而是**加一格**（例如 `sent`），并让 `ledger_classes()` 认它。
→ 而那一格的含义是精确的：**这个请求真的会发出去，而镜像里没有它**。**

### 五、数字

| 度量 | R1032 | R1033 |
|---|---|---|
| 套件 | 2243 / 0 | **2243 / 0 / 0** |
| 产物陈旧度 | 5 / 4,199 | **5 / 4,199** |
| 函数数 | 174,336 | **174,336** |
| **棘轮 `Sent`** | 10 | **16** |
| **棘轮守卫** | 3 绿（回滚后） | **3 绿（带 6 条新账）** |
| **补标注** | 0（两次改坏） | **5 处，一次成功** |
| **工具的 `unknown`** | 12 | **12（未变）** |
| **端点台账份数** | 未注意 | **2（互不引用）** |
| **工具的台账分类** | 未注意 | **4，且那 6 条无类可归** |

### 六、验证

```
cd D:\\projects\\cyber-reverse\\replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~EndpointEvidenceRatchet" -m:1 -> 3 通过
python tools/endpoint-provenance.py                                 -> unknown 仍 12（读另一份台账）
python tools/metrics_report.py -> 完整套件 exit 0  2243 / 0 / 0
```

### 七、仍然 Unknown

- **那 6 条该继续发还是改成报告**：**需先有 `sent` 格**。

### 八、教训

**我上一轮把「补账」理解成「把条目写进台账」。而仓里有两份台账，我写进了没人读的那份。**

**→ 而那不全是疏忽：`ENDPOINT_PROVENANCE.md` 在 `docs/`，测试在 `tests/` —— 两个地方，
  两个名字，没有一处交叉引用。**

**→ 所以「查一下有没有现成的」（AGENTS §2.7c）在这里该有个变体：
  **查一下这个东西有没有**两个**现成的，而我要改的是哪一个。****
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1033", BLOCKER)
    ensure(RSTATUS, "R1033", BLOCKER)
    ensure(RVERDICT, "第 1033 轮", VERDICT)
    ensure(BACKLOG, "R1033", BACKLOG_ADD)

    note = (
        "\n## R1033 补充 — **两份端点台账互不引用；那 6 条在工具的分类里无类可归**（套件 2243）\n\n"
        "**工具读的是另一份台账**：`endpoint-provenance.py:250` → `docs/ENDPOINT_PROVENANCE.md`，只认 `live`/`fixture`。\n"
        "| 台账 | 谁读 | 条目 | 本轮 |\n|---|---|---|---|\n"
        "| `tests/.../EndpointEvidenceRatchetTests.cs` | 三个棘轮守卫 | **17** | **加 6，绿** |\n"
        "| `docs/ENDPOINT_PROVENANCE.md` | 工具 | live 1 · fixture 3 · 待定 24 · assembled 21 | 未动 |\n"
        "→ **我改了没人读的那份 ⇒ `unknown` 仍 12。两份台账互不引用。**\n\n"
        "**而那 6 条无类可归**：`live` 无响应证据 · `fixture` 不是负例 · `待定` 那 24 条不含它们 ·\n"
        "`assembled` 只部分吻合 ⇒ `BASELINE = 0` 的「all 24 judged」对这 6 条从未适用。\n\n"
        "**第一份台账确实做完了**：5 处标注 + 6 条账 + `SentCeiling` 10 → 16，棘轮 3/3 绿。\n"
        "→ 用的是 R1032 两条前置条件（整行锚点替换 + 真实字面量），**一次成功，省下上一轮的三次回滚**。\n\n"
        "**下一步**：给工具台账加一格 `sent`（真的会发出去而镜像里没有），让 `ledger_classes()` 认它 ——\n"
        "而不是把那 6 条塞进现有分类（那是把「没归宿」伪装成「有归宿」）。\n\n"
        "数字：套件 2243/0/0 · 陈旧度 5 / 4,199 · 函数数 174,336 · Sent 10 → **16** · 标注 **5** 处 ·\n"
        "工具 unknown **12 不变** · 台账 **2** 份 · 工具分类 **4**。\n\n"
        "纪律：**查一下这个东西有没有两个现成的，而我要改的是哪一个。**\n\n"
        "下一轮：加 `sent` 格并联通两份台账。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1033" not in h:
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
             for p, k in ((RBLOCK, "R1033"), (RSTATUS, "R1033"), (RVERDICT, "第 1033 轮"), (BACKLOG, "R1033")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1033: two endpoint ledgers that never met, and six paths with nowhere to be filed\n\n"
         "R1032 left two mechanical preconditions for reconciling the ledger, and this round applied them. Both held:\n"
         " whole-line anchors instead of hunting for a comment marker kept every URL intact, and copying literals from\n"
         " the source instead of the tool's truncated display kept StillInItsFile green first time. Five markers, six\n"
         " entries, the ceiling from ten to sixteen, ratchet at three of three, suite at 2243.\n\n"
         "And the provenance tool still reports twelve.\n\n"
         "Because it reads a different ledger. endpoint-provenance.py points at docs/ENDPOINT_PROVENANCE.md, while the\n"
         " ratchet guards read a table inside the test class. Seventeen entries there, twenty-nine plus a pending table\n"
         " and an assembled list here, and not one cross-reference in either direction. I spent the round writing into\n"
         " the one nobody reads.\n\n"
         "That is only half a mistake. The tool's ledger recognises live and fixture, and its baseline note claims all\n"
         " twenty-four were judged. Those six paths are none of the four categories it has: no live response, not a\n"
         " deliberate fixture, absent from the pending twenty-four, and only partly assembled from the flow's own\n"
         " origin. So they are not unrecorded. There is no slot that means what they are -- sent, and unbacked.\n\n"
         "Which makes the next step a new category rather than six more rows. Filing them under an existing label would\n"
         " dress a gap as a resolution, and the label would then be the thing that hides it.\n\n"
         "Figures: suite 2243 unchanged, freshness five files and 4,199 lines, count 174,336, ratchet Sent from ten to\n"
         " sixteen, five markers added on the first attempt, and the tool's count unmoved at twelve for a reason worth\n"
         " writing down rather than working around.\n\n"
         "Unknown: whether those six should keep being sent or become reports, which needs the category first.\n\n"
         "The lesson is a variant on checking whether something already exists: check whether it exists twice, and which\n"
         " copy is the one being read.\n\n"
         "One test file and three source files changed; suite green at 2243."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()