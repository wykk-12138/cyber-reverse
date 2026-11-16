"""Record R853: direct evidence for per-flow numbering, and a ninth sequence nobody recorded."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 镜像原文里的两条 blob（R853）

**`<AddToCart>d__32` @ `0x1434acef3`：**

```
AddToCart(32) · InitiateCheckout(33) · GenerateCSRF(34) · GetCheckout(35) · SubmitBillingAddress(36) …
```

**逐字对上 `StoreFlowSteps.DemandwareClassic`（`AddToCart 32 · InitiateCheckout 33 · GenerateCSRF 34 · GetCheckout 35 · SubmitBillingAddress 36`）。**

**`<AddToCart>d__22` @ `0x14338114f`：**

```
GetHome(19) · FindProductMulti(20) · FindProduct(21) · AddToCart(22) · SubmitDiscount(23) …
```

### 第一件事：R852 从「转写来的观察」变成「镜像原文」

**同一个 `AddToCart`，在两条不同的 blob 里是 `d__32` 与 `d__22` —— 同一个名字，两个编号，
分别在两段相邻运行里。所以编号确实是按流程给的，不是全局的。**

**R852 的那条警告（「那个观察来自 `StoreFlowSteps` 的转写，不是镜像原文」）到此解除。**

### 第二件事：还有一条序列没被记录

**`GetHome(19) · FindProductMulti(20) · FindProduct(21) · AddToCart(22) · SubmitDiscount(23)` 不匹配已记录的 8 条：**

| 流程 | `GetHome` | `FindProductMulti` |
|---|---|---|
| CollectPlusApp | 33 | — |
| StructureTokenMulti | — | 29 |
| StructureTokenSingle | — | — |
| **这条未命名序列** | **19** | **20** |

**所以镜像里至少还有第九条流程序列，而 `StoreFlowSteps` 里没有它。**
"""

if "镜像原文里的两条 blob（R853" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: direct evidence + ninth sequence")

BLOCKER = """

---

## 277. R852 的证据升到镜像原文；**而同一批证据带出第九条序列**

> R853。未改产品代码。

### 一、直接证据

**`<AddToCart>d__32` @ `0x1434acef3`：**

```
AddToCart(32) · InitiateCheckout(33) · GenerateCSRF(34) · GetCheckout(35) · SubmitBillingAddress(36) …
```

**这是 `StoreFlowSteps.DemandwareClassic` 逐字。**

**`<AddToCart>d__22` @ `0x14338114f`：**

```
GetHome(19) · FindProductMulti(20) · FindProduct(21) · AddToCart(22) · SubmitDiscount(23) …
```

**同一个 `AddToCart`，两条不同 blob，两个不同编号。**

**所以「编号按流程给」这条现在是 Observation，不是 Inference。
R852 留的那句「那个观察来自转写，不是镜像原文」到此解除。**

### 二、而第二条 blob 不匹配已记录的 8 条

| 流程 | `GetHome` | `FindProductMulti` |
|---|---|---|
| CollectPlusApp | 33 | — |
| StructureTokenMulti | — | 29 |
| StructureTokenSingle | — | — |
| **这条未命名序列** | **19** | **20** |

**`FindProductMulti` + `FindProduct` 同时出现，且 `GetHome` 在 19 —— 8 条里没有一条是这个形状。**

**所以镜像里至少还有第九条流程序列，而 `StoreFlowSteps` 里没有它。**

### 三、这一条对判据 (f) 的意义

**`StoreFlowSteps` 那 8 条我一直当成「镜像的全部流程序列」。**
**现在有一条不属于 8 条里的任何一条 —— 所以 8 不是全部。**

**而它的形状（`FindProductMulti` 与 `FindProduct` 并列）很像 `structure-token` 那两条的亲戚，
但编号不同（`FindProductMulti` 这里 20、struct-token-multi 那里 29）。**

**所以不是「struct-token 那一族被记错」，是**另有一条**。**

### 四、验证

```
ida.py str "AddToCart>d__32"  -> 1 match @0x1434acef3（DemandwareClassic 逐字）
ida.py str "AddToCart>d__22"  -> 1 match @0x14338114f（未命名序列）
ida.py str "d__32"            -> 33 matches（多数是无关类型）
ida.py str "d__22"            -> 34 matches
本轮未改产品代码
七项度量沿用
```

### 五、仍然 Unknown

- **那第九条序列属于哪个流程**：**Unknown** ——
  形状像 struct-token 一族但编号不同，**需要读完整 blob 才能判。**
- **`StoreFlowSteps` 的 8 条是怎么选出来的**：**Unknown** ——
  R112 的注释说「each flow's steps sit in one adjacent run」，**但没说是怎么确定「哪些流程」的。**
  **这条现在很关键：如果选法有偏，那 8 条之外可能还有几条。**
- **总共有多少条序列**：**Unknown** —— **这是判据 (f) 的覆盖率分母，而它现在不可靠。**

### 六、教训

**我在 R844 用 `StoreFlowSteps` 的 8 条算出了 130 步、22 同名、16.9%。**

**而这一轮发现 8 条之外还有一条。**
**如果分母是错的，那个百分比的分母就是错的 —— 而它已经被写进 `ASYNC_OPS.md` 和三轮记录。**

**「8 条是怎么选出来的」这个问题，我从来没问过。**
"""

VERDICT = """

---

## 第 853 轮：证据升到镜像原文；而同一批证据带出第九条序列

### 直接证据

**`<AddToCart>d__32` @ `0x1434acef3`** —— `AddToCart(32) · InitiateCheckout(33) · GenerateCSRF(34) · GetCheckout(35) · SubmitBillingAddress(36)`
**= `StoreFlowSteps.DemandwareClassic` 逐字。**

**`<AddToCart>d__22` @ `0x14338114f`** —— `GetHome(19) · FindProductMulti(20) · FindProduct(21) · AddToCart(22) · SubmitDiscount(23)`

**同一个 `AddToCart`，两条 blob，两个编号 → 「编号按流程给」是 Observation 了。
R852 的警告（「来自转写不是原文」）解除。**

### 而第二条 blob 不匹配已记录的 8 条

`GetHome 19` + `FindProductMulti 20` + `FindProduct 21` —— **8 条里没有一条是这个形状**
（CollectPlus 的 `GetHome` 33；struct-token-multi 的 `FindProductMulti` 29）。

> **镜像里至少还有第九条流程序列，而 `StoreFlowSteps` 里没有它。**

### 这条对 (f) 的意义

**我一直把 `StoreFlowSteps` 的 8 条当成「镜像的全部流程序列」。现在有一条不属于它们。**

**而最要紧的是那个没问过的问题：**

> **「这 8 条是怎么选出来的？」** ——
> **R112 的注释说「each flow's steps sit in one adjacent run」，但没说是怎么确定「哪些流程」的。**

**如果选法有偏，8 条之外可能还有几条；而 8 是 R844 那个 16.9% 的分母。**

### 仍然 Unknown

**第九条属于哪个流程**（形状像 struct-token 一族但编号不同，需读完整 blob）·
**8 条是怎么选出来的**（**现在很关键**）· **总共有多少条序列**（**判据 (f) 的分母，现在不可靠**）

### 教训

**我在 R844 用 8 条算出 130 步 · 22 同名 · 16.9%，而这一轮发现 8 条之外还有一条。**
**分母错了，那个百分比的分母就错了 —— 而它已经写进 `ASYNC_OPS.md` 和三份记录。**
"""

BACKLOG_ADD = """

## 判据 (f) — 第九条序列 + 分母不可靠（R853）

**直接证据（镜像原文）：**
`<AddToCart>d__32` @`0x1434acef3` = DemandwareClassic 逐字 · `<AddToCart>d__22` @`0x14338114f` = 未命名序列
**→ 同名字两个编号 → 编号按流程给 = Observation（R852 的转写警告解除）。**

### 新发现

`GetHome(19) · FindProductMulti(20) · FindProduct(21) · AddToCart(22) · SubmitDiscount(23)` **不匹配 8 条中任何一条**
（CollectPlus `GetHome`=33；struct-token-multi `FindProductMulti`=29）。

**→ 镜像至少还有第九条流程序列，`StoreFlowSteps` 里没有它。**

### 没问过的问题（现在很关键）

> **`StoreFlowSteps` 那 8 条是怎么选出来的？**
> R112 注释说「each flow's steps sit in one adjacent run」，**但没说是怎么确定「哪些流程」的。**

**若选法有偏，8 之外可能还有几条。而 8 是 R844 那个 16.9% 的分母。**

| 仍 Unknown | |
|---|---|
| 第九条属于哪个流程 | 需读完整 blob |
| **8 条怎么选出来的** | **关键** |
| 总共多少条序列 | **(f) 的分母，现不可靠** |

**纪律**：**分母错了，百分比就错了 —— 而它已经写进三份记录。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R853", BLOCKER)
    ensure(RSTATUS, "R853", BLOCKER)
    ensure(RVERDICT, "第 853 轮", VERDICT)
    ensure(BACKLOG, "R853", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R853" not in h:
        h += ("\n## R853 补充 — 第九条序列 + 分母不可靠\n\n"
              "**直接证据**：`<AddToCart>d__32` @`0x1434acef3` = DemandwareClassic 逐字；`<AddToCart>d__22` @`0x14338114f` = 未命名序列。"
              "**同名字两编号 → 编号按流程给 = Observation。**\n"
              "**`GetHome(19)·FindProductMulti(20)·FindProduct(21)·AddToCart(22)·SubmitDiscount(23)` 不匹配 8 条中任何一条 → 镜像至少还有第九条序列。**\n"
              "**没问过的问题：`StoreFlowSteps` 那 8 条是怎么选出来的？** R112 注释只说「相邻一段」，没说怎么定「哪些流程」。\n"
              "**8 是 R844 那个 16.9% 的分母 —— 分母错了，百分比就错了。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R853"), (RSTATUS, "R853"), (RVERDICT, "第 853 轮"), (BACKLOG, "R853")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R853: direct evidence for per-flow numbering, and a ninth sequence the tables do not have\n\n"
         "R852 warned that its key observation came from the transcription rather than from the image. Two blobs settle"
         " it. AddToCart at 0x1434acef3 carries d__32 and continues InitiateCheckout 33, GenerateCSRF 34, GetCheckout 35,"
         " SubmitBillingAddress 36, which is StoreFlowSteps.DemandwareClassic word for word. AddToCart at 0x14338114f"
         " carries d__22 and is followed by SubmitDiscount 23. Same method name, two different ordinals, two different"
         " adjacent runs -- so numbering is per flow, and that is now an observation.\n\n"
         "The second blob carries a second finding. Its run reads GetHome 19, FindProductMulti 20, FindProduct 21,"
         " AddToCart 22, SubmitDiscount 23, which matches none of the eight recorded flows: CollectPlus has GetHome at 33"
         " and structure-token-multi has FindProductMulti at 29. A sequence exists that the tables do not contain.\n\n"
         "That matters out of proportion to one flow. Across R844 and R845 I computed 130 steps, 22 name matches and 16.9"
         " percent on the assumption that StoreFlowSteps held every flow sequence the image has. It holds at least one"
         " fewer than exist. The denominator of that percentage is therefore wrong, and it has already been written into"
         " ASYNC_OPS and three records.\n\n"
         "And the question I never asked is the one that would have caught it: how were those eight chosen? R112's"
         " comment says each flow's steps sit in one adjacent run, which explains how a run is recognised, not how the"
         " set of flows was enumerated. If that enumeration was partial, the true count is larger and every ratio built"
         " on eight is off.\n\n"
         "Unknown: which flow the ninth sequence belongs to, since its shape resembles the structure-token pair while"
         " its ordinals differ; how the eight were selected, which is now the gating question for criterion (f); and how"
         " many sequences there actually are, which is the denominator nobody has established.\n\n"
         "The lesson is that a denominator inherited from an earlier round needs the same scrutiny as a numerator I"
         " compute myself. Eight looked like a fact because it was written down; it was a selection whose rule I never"
         " checked.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
