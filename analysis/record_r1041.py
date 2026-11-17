"""Record R1041: (f)'s table is now generated, and the generator is guarded."""

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
### (f) 的表现在是**生成物**，而生成物也要守卫（R1041）

**R1040 证明「原版站清单」不可得（需凭据）。所以 (f) 的可交付形态是两半：
**复刻件侧可算**，**原版侧写 Unknown + 缺什么**。这一轮把它做成一份**生成的**表。**

### ① 为什么生成而不手写

**R1030 的教训是**只追加的清单会变成化石**；而手写的表会**与产生它的工具漂移**。
→ 所以 `replica/tools/core_coverage.py` 每次运行都从源码树与 `endpoint-provenance.py` **读**，然后写 `docs/CORE_COVERAGE.md`。**

```
flows=18  steps=356  placeholders=14  provenance exit=0
→ docs/CORE_COVERAGE.md：3,275 字节 / 72 行 / 有效 UTF-8
```

### ② 表的两半

| 半 | 内容 | 可复算？ |
|---|---|---|
| **复刻件侧** | 18 个含覆写的 flow · 356 个覆写步骤 · 14 处报告 Unknown · 端点门 214/214 · invented 0 · unresolved 0 · inline 323/33 · 已登记 33 · 未登记 **0** · exit **0** | **是**（跑工具即得） |
| **原版侧** | 站清单 = **Unknown**，缺 `api.cybersole.io/connect/app` 的响应（需原版登录凭据） | **不可得，已写明缺什么** |

**→ 而那正是 (a) 与 (f) 要求的形态：**可得的给出数，不可得的写 Unknown + 缺什么**。**

### ③ 而表里也记了那三条空路径

**`Stores.Flows.` 0 · `FarfetchFlow` 0 · `[A-Za-z]+Flow,` 1（TPL Dataflow 文档）· `X Checkout` 34（站名 4）。
→ 而那三条**写进生成物**的理由是：**下一个人不该再走一遍**。**

### ④ 4 条守卫 —— 而它们防的是「生成物过时」

| 守卫 | 断言 |
|---|---|
| `TheFlowCountMatchesTheTree` | 表里的 flow 数 == 磁盘上含覆写的 `.cs` 文件数 |
| `TheOriginalStoreListIsStillUnknown` | 原版侧仍写 Unknown 且点名 `connect/app` |
| `TheEmptyProbesAreRecorded` | 三条空路径仍在（`FarfetchFlow` · `TPL Dataflow`） |
| `TheDocumentSaysItIsGenerated` | 正文点名 `core_coverage.py`（防手改） |

**→ 第 1 条是「生成物过时」的可执行判据：源码变了而没重新生成 ⇒ 红。
→ 第 2 条防的是**悄悄漂移成断言** —— 若有人把 Unknown 改成「已知」，守卫红。**

### ⑤ 数字

| 度量 | R1040 | **R1041** |
|---|---|---|
| 套件 | 2254 / 0 | **2258 / 0 / 0（+4）** |
| 产物陈旧度 | 1 / 217 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **`docs/CORE_COVERAGE.md`** | 不存在 | **3,275 字节 / 72 行（生成）** |
| **flow 数（含覆写）** | 未测 | **18** |
| **覆写步骤总数** | 未测 | **356** |
| **报告 Unknown 的步骤** | 未测 | **14（在 3 个 flow 里）** |
| **(f) 的原版侧** | Unknown（口头） | **Unknown（写进生成物 + 守卫）** |

### 教训

> **「可复算」不是形容词 —— 它要求**文档与产生它的东西**之间有活连接。
> → 一份手写的表在写下的那一刻就开始了漂移，而它**不会报错**。
> → 所以 (f) 这一项真正的交付不是那张表，是**那个脚本加那 4 条守卫**。**
> **→ 而它们让「表是新的」这件事可被机器检查，而不是靠我记得重跑。**
"""

if "(f) 的表现在是**生成物**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1041 轮：(f) 的表现在是生成物，而生成物也要守卫

### ① 为什么生成而不手写

**`replica/tools/core_coverage.py` 每次运行从源码树与 `endpoint-provenance.py` **读**，然后写
`docs/CORE_COVERAGE.md`。**

```
flows=18  steps=356  placeholders=14  provenance exit=0
→ 3,275 字节 / 72 行 / 有效 UTF-8
```

**→ R1030 说只追加的清单会变成化石；手写的表会**与产生它的工具漂移**。生成 + 守卫是两者的解。**

### ② 表的两半

| 半 | 内容 | 可复算？ |
|---|---|---|
| **复刻件侧** | 18 flow · 356 步骤 · 14 处 Unknown · 门 214/214 · invented 0 · unresolved 0 · inline 323/33 · 已登记 33 · 未登记 **0** · exit **0** | **是** |
| **原版侧** | 站清单 **Unknown**，缺 `api.cybersole.io/connect/app`（需凭据） | **不可得，已写明缺什么** |

**→ 那正是 (a)+(f) 的形态：可得的给数，不可得的写 Unknown + 缺什么。**

### ③ 而那三条空路径也写进生成物

**`Stores.Flows.` 0 · `FarfetchFlow` 0 · `[A-Za-z]+Flow,` 1（TPL Dataflow）· `X Checkout` 34（站名 4）
—— 理由是**下一个人不该再走一遍**。**

### ④ 4 条守卫防「生成物过时」

`TheFlowCountMatchesTheTree`（表里的数 == 磁盘实际）· `TheOriginalStoreListIsStillUnknown`（防漂移成断言）·
`TheEmptyProbesAreRecorded` · `TheDocumentSaysItIsGenerated`（防手改）

### ⑤ 数字

| 度量 | R1040 | **R1041** |
|---|---|---|
| 套件 | 2254 / 0 | **2258 / 0 / 0（+4）** |
| 产物陈旧度 | 1 / 217 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **`docs/CORE_COVERAGE.md`** | 不存在 | **3,275 字节 / 72 行** |
| **flow 数（含覆写）** | 未测 | **18** |
| **覆写步骤总数** | 未测 | **356** |
| **报告的 Unknown 步骤** | 未测 | **14（3 个 flow）** |
| **(f) 原版侧** | Unknown（口头） | **Unknown（写进生成物 + 守卫）** |

### 教训

> **「可复算」不是形容词 —— 它要求**文档与产生它的东西**之间有活连接。
> → 一份手写的表在写下那一刻就开始漂移，而它**不会报错**。
> → 所以 (f) 真正的交付不是那张表，是**那个脚本加那 4 条守卫** ——
> 它们让「表是新的」可被机器检查，而不靠我记得重跑。**
"""

BACKLOG_ADD = """

## 判据 (f) — **(f) 的表是生成物 `docs/CORE_COVERAGE.md`，4 条守卫防过时**（R1041）

### 生成器

`replica/tools/core_coverage.py` → 读源码树 + `endpoint-provenance.py` → 写 `docs/CORE_COVERAGE.md`。

```
flows=18  steps=356  placeholders=14  provenance exit=0      → 3,275 字节 / 72 行 / UTF-8 有效
```

### 两半

| 半 | 内容 |
|---|---|
| 复刻件侧（**可复算**） | 18 flow · 356 步骤 · 14 Unknown · 门 214/214 · invented 0 · unresolved 0 · inline 323/33 · 已登记 33 · 未登记 **0** · exit 0 |
| 原版侧（**Unknown+缺什么**） | 站清单 Unknown，缺 `api.cybersole.io/connect/app`（需原版凭据） |

### 三条空路径也写进生成物

`Stores.Flows.` 0 · `FarfetchFlow` 0 · `[A-Za-z]+Flow,` 1（TPL Dataflow）· `X Checkout` 34（站名 4）
—— **下一个人不该再走一遍。**

### 4 条守卫

`TheFlowCountMatchesTheTree` · `TheOriginalStoreListIsStillUnknown` ·
`TheEmptyProbesAreRecorded` · `TheDocumentSaysItIsGenerated`

### 数字

**套件 2258（+4）· 陈旧度 1 / 217 · 函数数 174,293 · flow 18 · 步骤 356 · Unknown 14 · 表 3,275 字节**

| 仍待 | |
|---|---|
| 原版站清单 | 需凭据（第一类停等项） |
| 产物重 publish | 1 文件陈旧 |

**纪律**：「可复算」要求文档与产生它的东西之间有活连接。
"""

BLOCKER = """

---

## 465. **(f) 的表是生成物，而生成物也要守卫**

> R1041。**加 1 个工具 + 1 个生成文档 + 1 个测试文件。** 套件 **2258 通过 / 0 失败 / 0 跳过**。

### 一、为什么生成而不手写

**R1030 的教训是**只追加的清单会变成化石**；而手写的表会**与产生它的工具漂移**。
→ 所以 `replica/tools/core_coverage.py` 每次运行都从源码树与 `endpoint-provenance.py` **读**，
  然后写 `docs/CORE_COVERAGE.md`。**

```
flows=18  steps=356  placeholders=14  provenance exit=0
→ docs/CORE_COVERAGE.md：3,275 字节 / 72 行 / 有效 UTF-8
```

### 二、表的两半

| 半 | 内容 | 可复算？ |
|---|---|---|
| **复刻件侧** | 18 个含覆写的 flow · 356 个覆写步骤 · 14 处报告 Unknown · 端点门 214/214 · invented 0 · unresolved 0 · inline 323/33 · 已登记 33 · 未登记 **0** · exit **0** | **是**（跑工具即得） |
| **原版侧** | 站清单 = **Unknown**，缺 `api.cybersole.io/connect/app` 的响应（需原版登录凭据） | **不可得，已写明缺什么** |

**→ 而那正是 (a) 与 (f) 要求的形态：**可得的给出数，不可得的写 Unknown + 缺什么**。**

### 三、而表里也记了那三条空路径

**`Stores.Flows.` 0 · `FarfetchFlow` 0 · `[A-Za-z]+Flow,` 1（TPL Dataflow 文档）· `X Checkout` 34（站名 4）。
→ 而那三条**写进生成物**的理由是：**下一个人不该再走一遍**。**

### 四、4 条守卫 —— 而它们防的是「生成物过时」

| 守卫 | 断言 |
|---|---|
| `TheFlowCountMatchesTheTree` | 表里的 flow 数 == 磁盘上含覆写的 `.cs` 文件数 |
| `TheOriginalStoreListIsStillUnknown` | 原版侧仍写 Unknown 且点名 `connect/app` |
| `TheEmptyProbesAreRecorded` | 三条空路径仍在（`FarfetchFlow` · `TPL Dataflow`） |
| `TheDocumentSaysItIsGenerated` | 正文点名 `core_coverage.py`（防手改） |

**→ 第 1 条是「生成物过时」的可执行判据：源码变了而没重新生成 ⇒ 红。
→ 第 2 条防的是**悄悄漂移成断言** —— 若有人把 Unknown 改成「已知」，守卫红。**

### 五、数字

| 度量 | R1040 | R1041 |
|---|---|---|
| 套件 | 2254 / 0 | **2258 / 0 / 0（+4）** |
| 产物陈旧度 | 1 / 217 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **`docs/CORE_COVERAGE.md`** | 不存在 | **3,275 字节 / 72 行（生成）** |
| **flow 数（含覆写）** | 未测 | **18** |
| **覆写步骤总数** | 未测 | **356** |
| **报告 Unknown 的步骤** | 未测 | **14（在 3 个 flow 里）** |
| **(f) 的原版侧** | Unknown（口头） | **Unknown（写进生成物 + 守卫）** |

### 六、验证

```
cd D:\\projects\\cyber-reverse\\replica
python tools/core_coverage.py
  -> wrote docs/CORE_COVERAGE.md
  -> flows=18 steps=356 placeholders=14 provenance exit=0
dotnet test --filter "FullyQualifiedName~CoreCoverageDocument" -m:1 -> 4 通过
python tools/metrics_report.py -> 完整套件 exit 0  2258 / 0 / 0
```

### 七、仍然待

- **原版站清单**：需凭据（第一类停等项）。
- **产物需重新 publish**（1 文件陈旧）：待收尾。

### 八、教训

**「可复算」不是形容词 —— 它要求**文档与产生它的东西**之间有活连接。**

**→ 一份手写的表在写下的那一刻就开始了漂移，而它**不会报错**。**

**→ 所以 (f) 这一项真正的交付不是那张表，是**那个脚本加那 4 条守卫**。
→ 而它们让「表是新的」这件事可被机器检查，而不是靠我记得重跑。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1041", BLOCKER)
    ensure(RSTATUS, "R1041", BLOCKER)
    ensure(RVERDICT, "第 1041 轮", VERDICT)
    ensure(BACKLOG, "R1041", BACKLOG_ADD)

    note = (
        "\n## R1041 补充 — **(f) 的表是生成物 `docs/CORE_COVERAGE.md`，4 条守卫防过时**（套件 2258）\n\n"
        "**生成器**：`replica/tools/core_coverage.py` 读源码树 + `endpoint-provenance.py` → 写 `docs/CORE_COVERAGE.md`。\n"
        "```\nflows=18  steps=356  placeholders=14  provenance exit=0   → 3,275 字节 / 72 行 / UTF-8 有效\n```\n\n"
        "**两半**：复刻件侧**可复算**（18 flow · 356 步骤 · 14 Unknown · 门 214/214 · invented 0 · unresolved 0 ·\n"
        "inline 323/33 · 已登记 33 · 未登记 **0** · exit 0）· 原版侧 **Unknown + 缺什么**\n"
        "（站清单需 `api.cybersole.io/connect/app`，即需原版登录凭据）。\n\n"
        "**三条空路径也写进生成物**（`Stores.Flows.` 0 · `FarfetchFlow` 0 · `[A-Za-z]+Flow,` 1 TPL Dataflow ·\n"
        "`X Checkout` 34/站名 4）—— 理由是**下一个人不该再走一遍**。\n\n"
        "**4 条守卫**：`TheFlowCountMatchesTheTree`（防生成物过时）· `TheOriginalStoreListIsStillUnknown`\n"
        "（防悄悄漂移成断言）· `TheEmptyProbesAreRecorded` · `TheDocumentSaysItIsGenerated`（防手改）。\n\n"
        "数字：套件 2258（+4）· 陈旧度 1 / 217 · 函数数 174,293 · flow 18 · 步骤 356 · Unknown 14 · 表 3,275 字节。\n\n"
        "纪律：**「可复算」要求文档与产生它的东西之间有活连接。**\n\n"
        "下一轮：publish 清陈旧度；随后回到 ① 的实质工作（端点基或风控求解协议）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1041" not in h:
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
             for p, k in ((RBLOCK, "R1041"), (RSTATUS, "R1041"), (RVERDICT, "第 1041 轮"), (BACKLOG, "R1041")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1041: criterion (f)'s table is generated, and the generator is guarded\n\n"
         "R1040 showed the original's store list cannot be had from the binary -- three shapes probed, all empty, and\n"
         " the evidence pointing at a served catalogue. So criterion (f) has to be delivered in the shape criterion (a)\n"
         " prescribes: what is computable is computed, what is not is recorded as unknown with the missing artefact\n"
         " named.\n\n"
         "The replica side is computable, so it is generated rather than written. tools/core_coverage.py reads the flow\n"
         " tree and runs the provenance tool, then writes docs/CORE_COVERAGE.md: eighteen flows with at least one\n"
         " override, three hundred and fifty-six overrides, fourteen of them reporting an unknown endpoint in three\n"
         " flows, and an endpoint gate that is all zeros -- two hundred and fourteen constants all verbatim, nothing\n"
         " invented, nothing unresolved, nothing unregistered.\n\n"
         "The original side says Unknown and names what is missing: the response from api.cybersole.io/connect/app,\n"
         " which needs the original login. It also records the three shapes that came back empty, so the next reader\n"
         " does not spend a round rediscovering them.\n\n"
         "Four guards keep the document alive rather than merely present. The flow count must equal the number of files\n"
         " that declare an override, so a stale document fails. The unknown section must still say unknown and still\n"
         " name the endpoint, so it cannot quietly drift into a claim. The empty probes must still be listed, and the\n"
         " document must name its generator so nobody edits it by hand.\n\n"
         "Figures: suite 2254 to 2258, freshness one file and 217 lines, count 174,293, eighteen flows and three\n"
         " hundred and fifty-six override steps now stated in a file rather than estimated in prose.\n\n"
         "Pending: the store catalogue itself, which needs credentials, and a publish to clear freshness.\n\n"
         "The lesson is that recomputable is not an adjective: it requires a live connection between a document and the\n"
         " thing that produces it, and a hand-written table starts drifting the moment it is written without ever\n"
         " raising an error.\n\n"
         "One tool, one generated document and one test file added; suite green at 2258."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()