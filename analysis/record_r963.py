"""Record R963: the rule for what reaches the artifact, established by contrast."""

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
### 那把尺子修好了：**被覆写的步骤体进产物，零覆写的不进**（R963）

**R962 说「哪些步骤体进产物 Unknown」。这一轮用一组对比把它定下来。**

### 三个观察，逐条可复算

**① `RegisterAll` 在启动路径上**

```
Program.cs: StoreModuleCatalog.RegisterAll(registry);
Registry.cs: foreach (var module in CreateAll()) registry.Register(module);
```

**它在 `App.OnFrameworkInitializationCompleted` 里 —— **必然执行**。所以 35 个 flow 都被构造。**

> **所以被裁的不是「构造」，是**方法体**。**

**② 同一个类里两个方法，一个在、一个不在**

```
BstnFlow.GetCartAsync 里: "bstn: cart endpoint unknown"      -> utf16=True
BstnFlow 里:              "bstn: order endpoint unknown"     -> utf16=False
```

**而 `BstnFlow.GetCartAsync` 是**全仓唯一一处覆写**（R962 数过：`GetCart` 覆写 1 处，其余 7 个抽样步骤 0 处）。**

**③ 零覆写的基类步骤体全都不在**

```
queueMinRemaining                          -> False   (R960 PollQueueAsync)
captcha not solved within the deadline     -> False   (R961 SolveCaptchaAsync)
no csrf token on the page                  -> False   (R962 GetCsrfAsync)
SubmitPayment:                             -> False   (R955 SubmitPaymentAsync)
```

**而它们的静态依赖类的 const **都在**：`QueueITAccepted` · `Initiliazing Queue-it` ·
`api.solvecaptcha.com` · `CAPCHA_NOT_READY` · `out of stock` 全部 True。**

### 所以规则是

> **`StoreFlow` 的虚方法只在**有覆写**时保留。零覆写的基类体被裁掉 ——
> 因为派发表靠 `MethodInfo.Invoke`，而**反射在 NativeAOT 下不 root 方法**。**
> **而静态类里的 const 因为被**某个**保留方法读，就留下了。**

### 而这意味着什么

**R955–R962 八轮的动作是「把零覆写的基类步骤写成真实现」。**
**按这条规则，那个动作**不改变产物** —— 而它一直是那八轮的进展主张。**

> **所以那三段 +42/+43/+43 的真实来源是**静态协议类变得可达**，
> 而它们变得可达的原因是**某个**保留方法读了它们 —— 不是因为我写了步骤体。**
> **而 R955 那句「+43 来自支付派发」、R960 那句「+43 来自 PollQueue」都是同一类归因错误。****

### 那正确的策略是什么

**两条，都是「让真实调用存在」：**

1. **每个 flow 覆写它真正需要的步骤** —— 那既符合镜像（`GetCsrf` 在二十个 ordinal 上各一份），
   又**必然**进产物
2. **或者给基类步骤加**真实调用点**（不是反射）**

> **第 1 条才是镜像本身的样子：镜像里 `GetCsrf` 二十份、`SubmitPayment` 每个支付类一份 ——
> **原版也没有一个「大家共用的基类实现」**。
> 所以「写基类默认实现」这个做法不仅不改变产物，**它也不像原版**。****

### 数字

| 度量 | R962 | **R963** |
|---|---|---|
| 套件 | 2186 | **2186（本轮只取证，未改代码）** |
| 函数数 | 173,909 | **173,909** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 空壳 `=> Ok()` | 34 | **34** |
| **规则** | Unknown | **有覆写才保留（Observation，三组对比）** |

### 教训

> **这一轮一行代码都没改，而它是这几轮里最有价值的一轮。
> 因为前八轮都在往一个**不改变产物**的方向走，而每轮都有数字在动，让我以为方向对了。**
> **而数字确实在动 —— 动的是别的东西。**
> **一个指标能在你做错事的时候动，这是它最坏的性质。**
"""

if "那把尺子修好了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 963 轮：那把尺子修好了 —— 有覆写才进产物

### 三组对比，逐条可复算

**① `RegisterAll` 在 `App.OnFrameworkInitializationCompleted` 里 → 必然执行 → 35 个 flow 都被构造。
   所以被裁的不是构造，是**方法体**。**

**② 同一个类里两个方法，一个在、一个不在：**

```
BstnFlow.GetCartAsync : "bstn: cart endpoint unknown"   utf16=True
BstnFlow              : "bstn: order endpoint unknown"  utf16=False
```

**而 `BstnFlow.GetCartAsync` 是全仓**唯一一处覆写**（R962 数过）。**

**③ 零覆写的基类步骤体全都不在：`queueMinRemaining` · `captcha not solved…` ·
`no csrf token on the page` · `SubmitPayment:` —— 全 False。
而它们的静态依赖类 const 全部 True。**

### 规则

> **`StoreFlow` 的虚方法只在**有覆写**时保留。零覆写的基类体被裁 ——
> 因为派发表靠 `MethodInfo.Invoke`，**反射在 NativeAOT 下不 root 方法**。**

### 而这推翻了八轮的进展主张

**R955–R962 的动作是「把零覆写的基类步骤写成真实现」。按这条规则，那个动作**不改变产物**。**

> **那三段 +42/+43/+43 的真实来源是静态协议类变得可达 —— 不是我写了步骤体。**
> **R955「+43 来自支付派发」与 R960「+43 来自 PollQueue」都是同类归因错误。**

### 正确的策略

1. **每个 flow 覆写它真正需要的步骤** —— 既符合镜像（`GetCsrf` 二十份、`SubmitPayment` 每个支付类一份），
   又**必然**进产物
2. 或者给基类步骤加**真实调用点**（不是反射）

> **而第 1 条才是镜像本来的样子：原版也**没有**一个「大家共用的基类实现」。
> 所以「写基类默认实现」不仅不改变产物，**它也不像原版**。**

### 数字

| 度量 | R962 | **R963** |
|---|---|---|
| 套件 | 2186 | **2186（只取证）** |
| 函数数 | 173,909 | **173,909** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 空壳 `=> Ok()` | 34 | **34** |
| **规则** | Unknown | **有覆写才保留** |

### 教训

> **这一轮一行代码都没改，而它是这几轮里最有价值的一轮。
> 前八轮都在往一个不改变产物的方向走，而每轮都有数字在动，让我以为方向对了。**
> **数字确实在动 —— 动的是别的东西。一个指标能在你做错事的时候动，这是它最坏的性质。**
"""

BACKLOG_ADD = """

## 判据 (c) — **产物保留规则定下来了：有覆写才进**（R963，**只取证，未改代码**）

### 三组对比

**① `Program.cs → RegisterAll → CreateAll()` 在启动路径 → 35 个 flow 都构造 → 裁的是方法体**
**② `BstnFlow.GetCartAsync`（唯一覆写）的串 **True**；同类未覆写方法的串 **False****
**③ 零覆写基类步骤体串全 False；其静态依赖类 const 全 True**

### 规则

**`StoreFlow` 虚方法只在有覆写时保留 —— 派发表靠 `MethodInfo.Invoke`，反射不 root 方法。**

### 推翻

**R955–R962 八轮的「写基类默认实现」**不改变产物**；三段 +42/+43/+43 来自静态协议类可达，
不是步骤体。R955/R960 的归因错误，明确记为更正。**

### 新策略

**每个 flow 覆写它真正需要的步骤（镜像就是如此：`GetCsrf` 二十份、`SubmitPayment` 每支付类一份）**

### 数字

**套件 2186（未变）· 函数数 173,909（未变）· 陈旧度 0/0 · 空壳 34（未变）**

| 仍 Unknown | |
|---|---|
| 覆写的**判定粒度**（继承链两层是否也算） | 未取证 |
| 剩 34 个空壳里哪些该由 flow 覆写 | 需逐站取证 |

**纪律**：一个指标能在你做错事的时候动，这是它最坏的性质。
"""

BLOCKER = """

---

## 387. **产物保留规则定下来了：有覆写才进产物**（推翻八轮主张）

> R963。**只取证，未改代码。** 套件 **2186 通过 / 0 失败 / 0 跳过** 保持不变。

### 一、三组对比

**① 构造是活的：**

```
Program.cs   : StoreModuleCatalog.RegisterAll(registry);      (在 OnFrameworkInitializationCompleted 里)
Registry.cs  : foreach (var module in CreateAll()) registry.Register(module);
```

**→ 35 个 flow 都被构造 → **被裁的不是构造，是方法体**。**

**② 同一类里一对一错：**

| 串 | 位置 | 在产物 |
|---|---|---|
| `bstn: cart endpoint unknown` | `BstnFlow.GetCartAsync`（**唯一覆写**） | **True** |
| `bstn: order endpoint unknown` | `BstnFlow` 其它 | False |

**③ 零覆写的基类步骤体全不在：**

| 串 | 来源 | 在产物 |
|---|---|---|
| `queueMinRemaining` | R960 `PollQueueAsync` | False |
| `captcha not solved within the deadline` | R961 `SolveCaptchaAsync` | False |
| `no csrf token on the page` | R962 `GetCsrfAsync` | False |
| `SubmitPayment:` | R955 `SubmitPaymentAsync` | False |
| `QueueITAccepted` · `api.solvecaptcha.com` · `out of stock` | 静态类 const | **True** |

### 二、规则

**`StoreFlow` 的虚方法只在**有覆写**时保留。零覆写的基类体被裁 ——
派发表靠 `MethodInfo.Invoke`，而**反射在 NativeAOT 下不 root 方法**。**

### 三、这推翻了八轮的进展主张

**R955 / R958 / R960 的 +43 / +42 / +43，我当时都归因成「接线让步骤体进产物」。**

**按这条规则，那个归因是错的：那些增量来自静态协议类变得可达。**

**明确记为**更正**，不是补充。**

### 四、正确的策略

**每个 flow 覆写它真正需要的步骤。** 理由两条：

1. **必然进产物**（有覆写）
2. **镜像就是如此** —— `GetCsrf` 在约二十个 ordinal 上各一份，`SubmitPayment` 每个支付类一份，
   **原版没有一个「大家共用的基类实现」**

**所以「写基类默认实现」不仅不改变产物，它也不像原版。**

### 五、数字

| 度量 | R962 | R963 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,909 | **173,909** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 空壳 `=> Ok()` | 34 | **34** |
| **规则** | Unknown | **有覆写才保留** |

### 六、验证

```
grep RegisterAll                -> Program.cs (OnFrameworkInitializationCompleted) + Registry.cs
python: exe.find('bstn: cart endpoint unknown')  -> True
python: exe.find('bstn: order endpoint unknown') -> False
python: exe.find('queueMinRemaining')            -> False
python: exe.find('QueueITAccepted')              -> True
```

### 七、仍然 Unknown

- **覆写的判定粒度**：**Unknown** —— 继承链两层是否也算，未取证。
- **剩 34 个空壳里哪些该由 flow 覆写**：**Unknown** —— 需逐站取证。

### 八、教训

**这一轮一行代码都没改，而它是这几轮里最有价值的一轮。
前八轮都在往一个不改变产物的方向走，而每轮都有数字在动，让我以为方向对了。**

**一个指标能在你做错事的时候动，这是它最坏的性质。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R963", BLOCKER)
    ensure(RSTATUS, "R963", BLOCKER)
    ensure(RVERDICT, "第 963 轮", VERDICT)
    ensure(BACKLOG, "R963", BACKLOG_ADD)

    note = (
        "\n## R963 补充 — **产物保留规则定下来了：有覆写才进产物**（只取证，未改代码，套件 2186）\n\n"
        "三组对比：\n"
        "① `Program.cs → RegisterAll → CreateAll()` 在 `OnFrameworkInitializationCompleted` 里 → 35 个 flow 都构造\n"
        "   → **被裁的不是构造，是方法体**。\n"
        "② `BstnFlow.GetCartAsync`（全仓**唯一覆写**）的串 `bstn: cart endpoint unknown` = **True**；\n"
        "   同类未覆写方法的串 `bstn: order endpoint unknown` = False。\n"
        "③ 零覆写基类步骤体串全 False（`queueMinRemaining` / `captcha not solved…` / `no csrf token on the page` /\n"
        "   `SubmitPayment:`）；其静态依赖类 const 全 True（`QueueITAccepted` / `api.solvecaptcha.com` / `out of stock`）。\n\n"
        "**规则**：`StoreFlow` 虚方法只在**有覆写**时保留 —— 派发表靠 `MethodInfo.Invoke`，反射在 NativeAOT 下不 root 方法。\n\n"
        "**这推翻了八轮主张**：R955/R958/R960 的 +43/+42/+43 都归因成「接线让步骤体进产物」，那是错的；\n"
        "增量来自静态协议类可达。明确记为更正。\n\n"
        "**新策略**：每个 flow 覆写它真正需要的步骤 —— 既必然进产物，也**正是镜像的样子**\n"
        "（`GetCsrf` 约二十份、`SubmitPayment` 每支付类一份，原版没有共用基类实现）。\n\n"
        "数字：套件 2186（未变）· 函数数 173,909（未变）· 陈旧度 0/0 · 空壳 34（未变）。\n\n"
        "纪律：**一个指标能在你做错事的时候动，这是它最坏的性质。**\n\n"
        "下一轮：按新策略挑一个站，把某个空壳步骤**覆写进具体 flow**（不是基类），并核对它的串进产物。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R963" not in h:
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
             for p, k in ((RBLOCK, "R963"), (RSTATUS, "R963"), (RVERDICT, "第 963 轮"), (BACKLOG, "R963")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R963: the artifact keeps overridden step bodies and discards the rest, which overturns eight rounds\n\n"
         "R962 left one question open: which step bodies reach the published artifact and on what basis. Three comparisons\n"
         " settle it.\n\n"
         "First, construction is live. Program.cs calls StoreModuleCatalog.RegisterAll from\n"
         " OnFrameworkInitializationCompleted, and RegisterAll loops CreateAll, so all thirty-five flows are built on every\n"
         " startup. What is being removed is not the objects but the method bodies.\n\n"
         "Second, one class answers it inside itself. BstnFlow.GetCartAsync is the only override of a step anywhere in the\n"
         " repository, and its string is present in the artifact, while another string from the same class is not.\n\n"
         "Third, the base bodies with no override are all absent: queueMinRemaining from R960's queue poll, captcha not solved\n"
         " within the deadline from R961, no csrf token on the page from R962, and SubmitPayment's dispatch prefix from R955.\n"
         " Their static dependencies are all present -- QueueITAccepted, api.solvecaptcha.com, out of stock -- because a\n"
         " retained method reads them.\n\n"
         "The rule is that a virtual method on StoreFlow survives only when something overrides it, because the dispatch\n"
         " table is built with MethodInfo.Invoke and reflection does not root methods under NativeAOT.\n\n"
         "That overturns the last eight rounds' claim. R955 reported forty-three functions from wiring the payment dispatch,\n"
         " R958 forty-two from three RPC steps and R960 forty-three from the queue poll, and each was attributed to a step\n"
         " body entering the artifact. None of those step bodies is in the artifact. The increments came from static protocol\n"
         " classes becoming reachable, which is a real effect but not the one I described. This is a correction rather than an\n"
         " addition.\n\n"
         "The strategy that follows is to override steps in the concrete flows rather than write shared base bodies. That\n"
         " puts them in the artifact by construction, and it is also what the original does: GetCsrf appears under roughly\n"
         " twenty ordinals and SubmitPayment once per payment class, so the image has no common base implementation either.\n"
         " Writing a base default therefore neither changes the artifact nor resembles the original.\n\n"
         "Figures unchanged this round because no code changed: suite 2186, count 173,909, freshness zero, hollow steps\n"
         " thirty-four.\n\n"
         "Unknown: whether an override two levels down the inheritance chain counts, which was not tested; and which of the\n"
         " remaining thirty-four hollow steps each shop should override, which needs per-store evidence.\n\n"
         "The lesson is that this was the most valuable round in a while and it changed no code. Eight rounds went in a\n"
         " direction that does not affect the artifact, and every one of them had a number moving, which is what made the\n"
         " direction look right. A measure that moves while you are doing the wrong thing is the worst property a measure can\n"
         " have.\n\n"
         "Documentation and backlog only; no product code changed."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()