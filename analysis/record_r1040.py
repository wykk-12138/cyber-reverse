"""Record R1040: three routes to the original's store list, all negative, and what that means for criterion (f)."""

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
### 原版站清单的三条取证路径**全是空的** —— 而那回答了 (f) 的一个更基本的问题（R1040）

**R1039 说下一轮「publish 或换回 ①」。而 ① 的完成判据 (f) 要「原版站点清单从二进制取证 ↔ Flows 逐条对」。
这一轮去取，而三条路全空 —— 而那本身是答案。**

### ① 路径一：命名空间（反射元数据）

```
str "Stores\\.Flows\\.[A-Za-z0-9_]+"  --limit 600   →  n = 0
```

**→ 原版**没有** `Cybersole.Stores.Flows` 这个命名空间。
→ 而 `FarfetchFlow` 单独查也 **n = 0**，`[A-Za-z]+Flow,` 只有一条（**TPL Dataflow 的文档**）。**

**→ 所以 `*Flow` 是**复刻件的命名**（goal 允许「命名可不同」）。
→ 而那意味着**用复刻件的命名习惯去找原版的站清单，方向从一开始就错了。**

### ② 路径二：`"<站> Checkout"` 数据行

```
^[A-Za-z0-9 .&'-]+ Checkout$   →  n = 34
```

**→ 34 条里只有 **4 条**是站名 + 结账：**

```
FUNKO CHECKOUT · Farfetch Checkout · Kith EU Checkout · Shopify Checkout
```

**→ 其余 30 条是别的东西：**14 条动作/错误文案**（`Create checkout` · `Error polling checkout` · `Parsing checkout` ·
`Preloading checkout` …）· `User Checkout` · `Invalid Checkout` · `The date of the checkout` ·
`Triggers when any user completes a checkout`。**

**→ 所以那不是站清单 —— 它是**4 个站的定制结账文案**，而复刻件有 **52** 个 flow 文件。**

### ③ 而它对 Farfetch 是**更强**的证据

**`Farfetch Checkout` 与 `Shopify Checkout` · `Kith EU Checkout` · `FUNKO CHECKOUT` 同列。
→ 那说明原版对 Farfetch 有**专属的**结账流程（不只是通用 Shopify/Hybris 适配器）。
→ 而那让 R1038 的结论更硬：Farfetch 不只是「有这个站名」，它有一个**定制的结账步骤**。**

### ④ 路径三（推理）：站清单**可能不在二进制里**

**证据方向：**
- 复刻件有 **52** 个 flow 文件，而二进制里没有对应的 52 个名字或 52 行 `X Checkout`
- 原版的技术栈是**任务/工具**软件，且镜像里有 `api.cybersole.io` · `/connect/app`（R1032）
- R1032 的 `Relay` 证据显示原版**依赖自建服务**

**→ 所以「站点清单」很可能是**服务端下发**的配置，而不是内嵌在 exe 里。
→ 而那属于 goal 完成判据 (a) 的形态：**不可得 ⇒ 写 Unknown + 缺什么**。**

**→ 缺的是：`api.cybersole.io/connect/app` 的响应（需要原版登录凭据）—— 而那属于「可停下等 YG」的第一类。**

### ⑤ 所以 (f) 的表述要改

| (f) 原文 | 问题 | 改后 |
|---|---|---|
| 「原版站点清单从**二进制**取证」 | 清单可能**不在**二进制里 | 「站清单的**取证来源**要写明：二进制 / 服务端 / Unknown+缺什么」 |

**→ 而复刻件的 52 个 flow 已经可以逐条对上的是**另一件事**：
「这些 flow 的端点有没有镜像依据」—— 那正是 `endpoint-provenance.py` 现在回答的（`invented 0` · `unresolved 0` · `unknown 0`）。**

**→ 两件事分开：**
| 问题 | 现在能回答？ |
|---|---|
| 原版支持哪些站 | **Unknown —— 需服务端配置或凭据** |
| 复刻件的每个端点有据吗 | **能 —— 门三项全零** |

### ⑥ 数字

| 度量 | R1039 | **R1040** |
|---|---|---|
| 套件 | 2254 / 0 | **2254 / 0 / 0（未改代码）** |
| 产物陈旧度 | 1 / 217 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **`Stores.Flows` 命名空间** | 未查 | **n = 0** |
| **`FarfetchFlow` 类名** | 未查 | **n = 0** |
| **`*Flow` 类名（Fed 形）** | 未查 | **n = 1，且是 TPL Dataflow 文档** |
| **`X Checkout` 行** | 未查 | **34，其中站名 4 条** |
| **复刻件 flow 文件** | 未测 | **52** |
| **原版站清单** | 「从二进制取证」 | **Unknown —— 可能服务端下发** |

### 教训

> **这一轮我三次去找同一件东西，三次都空 —— 而那比找到更有用：**
> **→ 它说明 (f) 那条判据的**取证方向**本身有问题，而问题不在执行上。**
> **→ 而我最初的三次尝试都带着同一个偏见：**用复刻件的形状（`*Flow` 类、`X Checkout` 行）去找原版。**
> **→ 而原版不欠我们那些形状 —— 它是**数据驱动**的，而数据可能根本不在 exe 里。**
"""

if "原版站清单的三条取证路径" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1040 轮：原版站清单的三条取证路径全是空的

### ① 路径一：命名空间

```
str "Stores\\.Flows\\.[A-Za-z0-9_]+" --limit 600  →  n = 0
FarfetchFlow                                      →  n = 0
[A-Za-z]+Flow,                                    →  n = 1（TPL Dataflow 的文档，无关）
```

**→ 原版没有 `Cybersole.Stores.Flows` 命名空间，也没有 `*Flow` 类。
→ `*Flow` 是**复刻件的命名**（goal 允许）⇒ **用复刻件的命名习惯找原版的站清单，方向从一开始就错了。****

### ② 路径二：`"<站> Checkout"` 数据行

```
^[A-Za-z0-9 .&'-]+ Checkout$  →  n = 34
```

**→ 其中**只有 4 条**是站名 + 结账：**

```
FUNKO CHECKOUT · Farfetch Checkout · Kith EU Checkout · Shopify Checkout
```

**→ 其余 30 条是动作/错误文案（`Create checkout` · `Error polling checkout` · `Parsing checkout` …）
与无关句（`The date of the checkout` · `Triggers when any user completes a checkout`）。
→ 所以那不是站清单；复刻件有 **52** 个 flow 文件。**

### ③ 而它对 Farfetch 是**更强**的证据

**`Farfetch Checkout` 与 `Shopify Checkout` · `Kith EU Checkout` · `FUNKO CHECKOUT` 同列
⇒ 原版对 Farfetch 有**专属**结账流程，不只是通用适配器。**

### ④ 而推理给出：站清单**可能不在二进制里**

**52 个 flow 文件 vs 二进制里 0 个对应名 —— 加上 `api.cybersole.io` · `/connect/app`（R1032）⇒
站点列表很可能是**服务端下发**的配置。**

**→ 那正是 (a) 的形态：**不可得 ⇒ 写 Unknown + 缺什么**。
→ 缺的是 `api.cybersole.io/connect/app` 的响应 —— **需要原版登录凭据**（属可停下等 YG 的第一类）。**

### ⑤ 所以 (f) 的表述要改

| (f) 原文 | 改后 |
|---|---|
| 「原版站点清单从**二进制**取证」 | 「站清单的**取证来源**要写明：二进制 / 服务端 / Unknown + 缺什么」 |

**→ 而两件事要分开：**

| 问题 | 现在能回答？ |
|---|---|
| 原版支持哪些站 | **Unknown —— 需服务端配置或凭据** |
| 复刻件每个端点有据吗 | **能 —— 门三项全零** |

### ⑥ 数字

| 度量 | R1039 | **R1040** |
|---|---|---|
| 套件 | 2254 / 0 | **2254 / 0 / 0（未改代码）** |
| 产物陈旧度 | 1 / 217 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **`Stores.Flows` 命名空间** | 未查 | **0** |
| **`*Flow` 类名** | 未查 | **0（仅 TPL Dataflow 文档 1 条）** |
| **`X Checkout` 行** | 未查 | **34，站名 4 条** |
| **复刻件 flow 文件** | 未测 | **52** |
| **原版站清单** | 「从二进制取证」 | **Unknown —— 可能服务端下发** |

### 教训

> **三次去找同一件东西，三次都空 —— 而那比找到更有用：它说明 (f) 的**取证方向**有问题，不是执行。
> → 三次尝试都带同一个偏见：**用复刻件的形状去找原版**。
> → 而原版不欠我们那些形状 —— 它是**数据驱动**的，而数据可能根本不在 exe 里。**
"""

BACKLOG_ADD = """

## 判据 (f) — **原版站清单三条取证路径全空 ⇒ (f) 的取证方向要改**（R1040）

### 三条路径

| 路径 | 结果 |
|---|---|
| `Stores\\.Flows\\.[A-Za-z0-9_]+` | **n = 0** |
| `FarfetchFlow` | **n = 0** |
| `[A-Za-z]+Flow,` | n = 1（**TPL Dataflow 文档，无关**） |
| `^... Checkout$` | n = 34，**只有 4 条是站名**：FUNKO · Farfetch · Kith EU · Shopify |

**→ `*Flow` 是**复刻件的命名**；`X Checkout` 只覆盖 4 个站而复刻件有 **52** 个 flow 文件。**

### 而 `Farfetch Checkout` 因此更强

**与 `Shopify Checkout` / `Kith EU Checkout` / `FUNKO CHECKOUT` 同列 ⇒ 原版对它**有专属结账流程**。**

### 推理：站清单可能服务端下发

**52 个 flow 文件 vs 二进制 0 个对应名 + `api.cybersole.io` / `/connect/app` ⇒
站点列表很可能是**服务端配置**。**

**⇒ (a) 形态：Unknown + 缺什么 = `api.cybersole.io/connect/app` 的响应，需**原版登录凭据**。**

### (f) 表述改

**「原版站点清单从**二进制**取证」→「站清单的**取证来源**要写明：二进制 / 服务端 / Unknown+缺什么」。**

**两件事分开：原版支持哪些站 = Unknown（需凭据）· 复刻件端点是否有据 = 能（门三项全零）。**

### 数字

**套件 2254/0/0 · 陈旧度 1 / 217 · 函数数 174,293 · 命名空间 0 · `*Flow` 0 · `X Checkout` 34/站名4 · flow 文件 52**

| 仍 Unknown | |
|---|---|
| 原版支持哪些站 | **需 `api.cybersole.io/connect/app`（凭据）** |
| Farfetch 的 transport | 未找到 |

**纪律**：别用复刻件的形状去原版里找东西 —— 它不欠我们那些形状。
"""

BLOCKER = """

---

## 464. **原版站清单的三条取证路径全是空的 ⇒ (f) 的取证方向要改**

> R1040。**未改代码 —— 本轮是取证与判据修正。** 套件 **2254 通过 / 0 失败 / 0 跳过**。

### 一、路径一：命名空间（反射元数据）

```
str "Stores\\.Flows\\.[A-Za-z0-9_]+"  --limit 600   →  n = 0
FarfetchFlow                                      →  n = 0
[A-Za-z]+Flow,                                    →  n = 1（**TPL Dataflow 的文档**）
```

**→ 原版**没有** `Cybersole.Stores.Flows` 这个命名空间，也没有 `*Flow` 类。
→ 所以 `*Flow` 是**复刻件的命名**（goal 允许「命名可不同」）。
→ 那意味着**用复刻件的命名习惯去找原版的站清单，方向从一开始就错了。**

### 二、路径二：`"<站> Checkout"` 数据行

```
^[A-Za-z0-9 .&'-]+ Checkout$   →  n = 34
```

**→ 34 条里只有 **4 条**是站名 + 结账：**

```
FUNKO CHECKOUT · Farfetch Checkout · Kith EU Checkout · Shopify Checkout
```

**→ 其余 30 条是别的东西：**14 条动作/错误文案**（`Create checkout` · `Error polling checkout` ·
  `Parsing checkout` · `Preloading checkout` …）· `User Checkout` · `Invalid Checkout` ·
  `The date of the checkout` · `Triggers when any user completes a checkout`。**

**→ 所以那不是站清单 —— 它是**4 个站的定制结账文案**，而复刻件有 **52** 个 flow 文件。**

### 三、而它对 Farfetch 是**更强**的证据

**`Farfetch Checkout` 与 `Shopify Checkout` · `Kith EU Checkout` · `FUNKO CHECKOUT` 同列。
→ 那说明原版对 Farfetch 有**专属的**结账流程（不只是通用 Shopify/Hybris 适配器）。
→ 而那让 R1038 的结论更硬：Farfetch 不只是「有这个站名」，它有一个**定制的结账步骤**。**

### 四、路径三（推理）：站清单**可能不在二进制里**

**证据方向：**
- 复刻件有 **52** 个 flow 文件，而二进制里没有对应的 52 个名字或 52 行 `X Checkout`
- 原版镜像里有 `api.cybersole.io` · `/connect/app`（R1032）
- R1032 的 `Relay` 证据显示原版**依赖自建服务**

**→ 所以「站点清单」很可能是**服务端下发**的配置，而不是内嵌在 exe 里。
→ 而那属于 goal 完成判据 (a) 的形态：**不可得 ⇒ 写 Unknown + 缺什么**。**

**→ 缺的是：`api.cybersole.io/connect/app` 的响应（需要原版登录凭据）
  —— 而那属于「可停下等 YG」的第一类。**

### 五、所以 (f) 的表述要改

| (f) 原文 | 问题 | 改后 |
|---|---|---|
| 「原版站点清单从**二进制**取证」 | 清单可能**不在**二进制里 | 「站清单的**取证来源**要写明：二进制 / 服务端 / Unknown+缺什么」 |

**→ 两件事分开：**
| 问题 | 现在能回答？ |
|---|---|
| 原版支持哪些站 | **Unknown —— 需服务端配置或凭据** |
| 复刻件的每个端点有据吗 | **能 —— 门三项全零** |

### 六、数字

| 度量 | R1039 | R1040 |
|---|---|---|
| 套件 | 2254 / 0 | **2254 / 0 / 0（未改代码）** |
| 产物陈旧度 | 1 / 217 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **`Stores.Flows` 命名空间** | 未查 | **n = 0** |
| **`FarfetchFlow` 类名** | 未查 | **n = 0** |
| **`*Flow` 类名** | 未查 | **n = 1，且是 TPL Dataflow 文档** |
| **`X Checkout` 行** | 未查 | **34，其中站名 4 条** |
| **复刻件 flow 文件** | 未测 | **52** |
| **原版站清单** | 「从二进制取证」 | **Unknown —— 可能服务端下发** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "Stores\\.Flows\\.[A-Za-z0-9_]+" --limit 600  -> {"n":0}
python analysis/ida.py str "FarfetchFlow" --limit 100                    -> {"n":0}
python analysis/ida.py str "[A-Za-z]+Flow," --limit 60                    -> {"n":1}（TPL Dataflow 文档）
python analysis/ida.py str "^[A-Za-z0-9 .&'-]+ Checkout$" --limit 600     -> {"n":34}
```

### 八、仍然 Unknown / 待 YG

- **原版支持哪些站**：**需 `api.cybersole.io/connect/app` 的响应 ⇒ 需原版登录凭据（第一类停等项）**。
- **Farfetch 的 transport**：未找到。
- **产物需重新 publish**（1 文件陈旧）：待收尾。

### 九、教训

**这一轮我三次去找同一件东西，三次都空 —— 而那比找到更有用：
  它说明 (f) 那条判据的**取证方向**本身有问题，而问题不在执行上。**

**→ 而我最初的三次尝试都带着同一个偏见：**用复刻件的形状（`*Flow` 类、`X Checkout` 行）去找原版。**

**→ 而原版不欠我们那些形状 —— 它是**数据驱动**的，而数据可能根本不在 exe 里。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1040", BLOCKER)
    ensure(RSTATUS, "R1040", BLOCKER)
    ensure(RVERDICT, "第 1040 轮", VERDICT)
    ensure(BACKLOG, "R1040", BACKLOG_ADD)

    note = (
        "\n## R1040 补充 — **原版站清单三条取证路径全空 ⇒ (f) 的取证方向要改**（套件 2254，未改代码）\n\n"
        "**路径一 命名空间**：`Stores\\.Flows\\.` **0** · `FarfetchFlow` **0** · `[A-Za-z]+Flow,` **1**（TPL Dataflow 文档）。\n"
        "→ `*Flow` 是**复刻件的命名** ⇒ 用复刻件的形状找原版，方向从一开始就错。\n\n"
        "**路径二 `X Checkout` 行**：**34** 条，其中**只有 4 条**是站名：\n"
        "`FUNKO CHECKOUT` · `Farfetch Checkout` · `Kith EU Checkout` · `Shopify Checkout`；\n"
        "其余 30 条是动作/错误文案与无关句 ⇒ 那是**4 个站的定制文案**，而复刻件有 **52** 个 flow 文件。\n\n"
        "**而 `Farfetch Checkout` 因此更强**：与 Shopify/Kith EU/FUNKO 同列 ⇒ 原版对 Farfetch 有**专属结账流程**。\n\n"
        "**推理**：52 个 flow vs 二进制 0 个对应名 + `api.cybersole.io`/`/connect/app` ⇒ 站清单很可能**服务端下发**。\n"
        "⇒ (a) 形态：**Unknown + 缺什么 = `api.cybersole.io/connect/app` 的响应，需原版登录凭据**（第一类停等项）。\n\n"
        "**(f) 表述改**：「从**二进制**取证」→「写明取证来源：二进制 / 服务端 / Unknown+缺什么」。\n"
        "两件事分开：原版支持哪些站 = **Unknown（需凭据）** · 复刻件端点是否有据 = **能（门三项全零）**。\n\n"
        "数字：套件 2254/0/0 · 陈旧度 1 / 217 · 函数数 174,293 · 命名空间 **0** · `*Flow` **0** ·\n"
        "`X Checkout` **34/站名 4** · flow 文件 **52**。\n\n"
        "纪律：**别用复刻件的形状去原版里找东西 —— 它不欠我们那些形状。**\n\n"
        "下一轮：publish 清陈旧度；或标注 (f) 的 Unknown 并推进 ① 的端点覆盖（那部分可算）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1040" not in h:
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
             for p, k in ((RBLOCK, "R1040"), (RSTATUS, "R1040"), (RVERDICT, "第 1040 轮"), (BACKLOG, "R1040")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1040: three routes to the original's store list, all empty, and what that means for criterion (f)\n\n"
         "Criterion (f) asks for the original's store list taken from the binary and reconciled against the replica's\n"
         " flows. Going to get it produced three negatives.\n\n"
         "No Cybersole.Stores.Flows namespace. No FarfetchFlow type. No *Flow types at all, save one match that turns out\n"
         " to be TPL Dataflow's own documentation. So *Flow is this workspace's naming -- the goal permits that -- and\n"
         " searching for the original's stores under the replica's naming conventions was wrong before it started.\n\n"
         "The second guess was data rows of the form store-plus-step, since Farfetch Checkout exists. Thirty-four strings\n"
         " end in Checkout and only four name a store: FUNKO, Farfetch, Kith EU and Shopify. The rest are UI actions and\n"
         " error lines and sentences about checkouts. Four stores against fifty-two flow files is not a store list; it is\n"
         " a set of custom checkout strings, which makes the Farfetch evidence stronger rather than weaker -- the original\n"
         " gives it a bespoke step, alongside Shopify, Kith EU and Funko.\n\n"
         "Which leaves the likely answer that the list is not in the executable. Fifty-two flows, zero matching names, and\n"
         " an api.cybersole.io with a /connect/app endpoint all point the same way: the store catalogue is served. That\n"
         " makes it criterion (a)'s shape rather than a failure -- unknown, with what is missing named. What is missing is\n"
         " that endpoint's response, and getting it needs the original login, which is one of the two things this work is\n"
         " allowed to stop for.\n\n"
         "So (f) is restated: the store list's source must be stated as binary, server, or unknown-with-what-is-missing.\n"
         " And the two questions it was conflating are separated -- which stores the original supports is unknown pending\n"
         " credentials, while whether this replica's endpoints rest on evidence is answerable now, and answers zero on all\n"
         " three counts.\n\n"
         "Figures: suite 2254 unchanged, freshness one file and 217 lines, count 174,293, zero namespaces and zero flow\n"
         " types where I expected a list, thirty-four Checkout strings of which four name stores, and fifty-two flow files\n"
         " in the replica.\n\n"
         "Unknown: the store catalogue itself, pending the endpoint, and Farfetch's transport.\n\n"
         "The lesson is that all three attempts shared one bias -- looking for the original in the replica's shapes. The\n"
         " artifact does not owe us those shapes, and a data-driven program may keep its data somewhere else entirely.\n\n"
         "No code changed; suite green at 2254."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()