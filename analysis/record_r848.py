"""Record R848: the last four are documented-unresolved, not unknown."""

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
### collectplus-app 4 条：端点族已定位，而流程本身已登记为「未证」（R848）

**`StoreApiFamilies.cs` 里有这个族的端点，只是名字不含 CollectPlus：**

```
/component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores   <- GetCollectPlusLocations
/component/singlepagecheckout/cac/submit                                 <- SubmitCollectPlus
/component/singlepagecheckout/continueToPaymentDetails
/component/singlepagecheckout/setDeliveryCountry
/component/singlepagecheckout/setDeliveryMode
```

**而 `LambdaWitness.cs` 已经把 `collectplus-app` 登记在 `Unwitnessed` 里：**

> Flows with no ownership witness — their gaps stay unresolved.
> `"popmart", "demandware-classic", "demandware-dual", "collectplus-app", "structure-token-multi", "structure-token-single"`

**所以这 4 条的正确状态不是「Unknown」，是「端点族已知、归属未证、仓里已登记」。**

| 步骤 | 端点 | 状态 |
|---|---|---|
| `GetCollectPlusLocations` | `getClickAndCollectOrCollectPlusPoiStores` | **端点已定位** |
| `SubmitCollectPlus` | `cac/submit` | **端点已定位（族内）** |
| `CreateCheckoutApp` | `singlepagecheckout` 族 | **族内，未一一定位** |
| `GetDelivery` | 同上 | **族内，未一一定位** |

**而未证的原因是流程级：没有 ownership witness。**
"""

if "collectplus-app 4 条：端点族已定位（R848" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: collectplus closed as documented-unresolved")

BLOCKER = """

---

## 272. 最后 4 条：**不是 Unknown，是「仓里已登记为未证」**

> R848。未改产品代码。**这条线索收尾。**

### 一、端点族找到了，只是名字不含 CollectPlus

**`StoreApiFamilies.cs`：**

```
/component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores   <- GetCollectPlusLocations
/component/singlepagecheckout/cac/submit                                 <- SubmitCollectPlus
/component/singlepagecheckout/continueToPaymentDetails
/component/singlepagecheckout/setDeliveryCountry
/component/singlepagecheckout/setDeliveryMode
```

**`GetCollectPlusLocations` 那一行甚至把 CollectPlus 写进了路径** —— 而我的探针找的是「名字含 CollectPlus 的标识符」，
**所以探针 0 命中，而端点一直在。**

**这是 R838 那条教训的第四次：探针找的是标识符，真东西可能是路径。**

### 二、而流程本身早就登记为「未证」

**`LambdaWitness.cs`：**

```csharp
/// <summary>Flows with no ownership witness — their gaps stay unresolved.</summary>
public static readonly IReadOnlyList<string> Unwitnessed = new[]
{
    "popmart", "demandware-classic", "demandware-dual", "collectplus-app",
    "structure-token-multi", "structure-token-single",
};
```

**所以 `collectplus-app` 的状态一直是「端点族已知、归属未证」，仓里写着。**

**我把它当成「最后一个未结案项」是错的 —— 它是一个已登记状态，不是一个待办。**

### 三、整条线索的收尾

| 阶段 | 数 | 依据 |
|---|---|---|
| R839 起的名字清单 | 115 | 元数据 `<Name>d__N` |
| 判过一轮后仍不同名 | 71 | 探针三轮 |
| `StoreFlowSteps` 的 8 个流程 | 130 步 · 22 同名 | R844 |
| 减去 `StoreFlow` 基类已有的 | 108 → **59** | R845 |
| 减去 R124 已答的 dual | 59 → **50** | R846 |
| 减去两份 StepMap 已答的 | 50 → **4** | R847 |
| 最后 4 条 | **端点族已知、流程登记为未证** | R848 |

**71 → 0 待办，但「0」不是在 R848 才成立的 —— 它在 R847 就已经是 4，
而这 4 条在 `LambdaWitness` 写下那天就不是待办了。**

### 四、这条线索真正教了什么

**七轮里我做了五次「建清单」，每次都低估或误估：**

| 轮 | 我以为 | 实际 |
|---|---|---|
| R838 | PopMart 抽签是「一块未建模」 | 九方法子系统 + 三个同族 flow |
| R844 | 108 条不同名 | 其中 49 条基类已有 |
| R846 | dual 9 条待判 | R124 已答完 |
| R847 | johnlewis 8 + classic 5 待判 | 两份 StepMap 已答完 |
| R848 | collectplus 4 条最后待办 | 端点族已知 + 已登记未证 |

**共同形态：我总是在**名字层**建清单，而仓里的答案在**语义层**（StepMap / Controllers / ApiFamilies / LambdaWitness）。**

**所以判据 (f) 的正确做法不是「先建清单再裁决」，是「先读 `Flows` 目录里那些分析文件，它们就是清单」。**

### 五、验证

```
Get-ChildItem replica\\src\\Cybersole.Stores\\Flows -Filter *.cs      -> 47 个文件
StoreApiFamilies.cs: getClickAndCollectOrCollectPlusPoiStores · cac/submit
LambdaWitness.cs: Unwitnessed = { popmart, demandware-classic, demandware-dual, collectplus-app, structure-token-*, ... }
grep CollectPlus 全 src -> 13 处，其中 11 处在 StoreFlowSteps（步骤表本身）
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **`collectplus-app` 的 ownership witness**：**Unknown，且这是它被登记为 `Unwitnessed` 的原因。**
- **`CreateCheckoutApp` / `GetDelivery` 在 `singlepagecheckout` 族里的具体端点**：**Unknown** ——
  族已定位，**但没一一对上。**
- **`popmart` / `structure-token-*` 也在 `Unwitnessed` 里**：**这条我上一轮没注意** ——
  **它们在 R835–R838 被判为「没有」，而 `LambdaWitness` 说的是「没有 ownership witness」，两者是不同的话。**

### 七、教训

**最后这 4 条不是待办，是一个已登记的状态。**

**而我在第七轮才读到 `LambdaWitness.cs` —— 它一行就说明了哪些流程「gaps stay unresolved」。
如果我从 R838 就先读它，前面六轮的很多「待判」根本不会进清单。**

**「我不知道它已经存在」和「它不存在」在我脑子里长得一样 —— 这已经是我这个会话里第四次写这句话了。
第四次说明它不是一句感慨，是一个需要工具化的检查。**
"""

VERDICT = """

---

## 第 848 轮：最后 4 条不是 Unknown，是「仓里已登记为未证」

### 端点族一直在这里

```
/component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores   <- GetCollectPlusLocations
/component/singlepagecheckout/cac/submit                                 <- SubmitCollectPlus
```

**`GetCollectPlusLocations` 那一行把 CollectPlus 写进了路径 —— 而我的探针找的是「名字含 CollectPlus 的标识符」，
所以 0 命中，而端点一直在。**

### 而流程本身早登记为未证

```csharp
/// Flows with no ownership witness — their gaps stay unresolved.
Unwitnessed = { "popmart", "demandware-classic", "demandware-dual", "collectplus-app",
                "structure-token-multi", "structure-token-single" };
```

**所以它不是「最后一个待办」，是一个已登记状态。**

### 整条线索收尾

| 阶段 | 数 |
|---|---|
| 名字清单（元数据） | 115 |
| 探针三轮后仍不同名 | 71 |
| 8 个流程 130 步 · 22 同名 | — |
| 减基类已有 | 108 → **59** |
| 减 R124 已答 | → **50** |
| 减两份 StepMap 已答 | → **4** |
| 最后 4 条 | **端点族已知 + 已登记未证** |

### 七轮五次建清单，五次都低估

| 轮 | 我以为 | 实际 |
|---|---|---|
| R838 | 抽签是「一块」 | 九方法子系统 + 三个同族 flow |
| R844 | 108 条不同名 | 49 条基类已有 |
| R846 | dual 9 条待判 | R124 已答完 |
| R847 | johnlewis 8 + classic 5 | 两份 StepMap 已答完 |
| R848 | collectplus 4 条待办 | 端点族已知 + 已登记未证 |

> **我总在**名字层**建清单，而答案在**语义层**（StepMap / Controllers / ApiFamilies / LambdaWitness）。**
> **判据 (f) 的正确做法不是「先建清单再裁决」，是「先读 `Flows` 目录里那些分析文件，它们就是清单」。**

### 仍然 Unknown

**`collectplus-app` 的 ownership witness**（这正是它被登记的原因）· **`CreateCheckoutApp`/`GetDelivery` 在族内的具体端点** ·
**`popmart`/`structure-token-*` 也在 `Unwitnessed` 里 —— 而 R835–R838 说的是「没有」，两者是不同的话**

### 教训

**「我不知道它已经存在」和「它不存在」在我脑子里长得一样 —— 这是第四次写这句，说明它不是感慨，是一个需要工具化的检查。**
"""

BACKLOG_ADD = """

## 判据 (f) — 线索收尾（R848）

| 阶段 | 数 | 依据 |
|---|---|---|
| 名字清单 | 115 | 元数据 `<Name>d__N` |
| 探针三轮后 | 71 | |
| 8 流程 130 步 · 22 同名 | — | `StoreFlowSteps` |
| 减基类已有 | → **59** | `StoreFlow` 165 虚步骤 |
| 减 R124 | → **50** | `ScapiAppPath.cs` |
| 减两份 StepMap | → **4** | `JohnLewisStepMap` · `DemandwareStepMap` |
| 最后 4 条 | **已登记未证** | `LambdaWitness.Unwitnessed` |

### 端点族一直在

```
/component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores   <- GetCollectPlusLocations
/component/singlepagecheckout/cac/submit                                 <- SubmitCollectPlus
```

**探针找的是「标识符含 CollectPlus」，而它写在路径里 → 0 命中。**

### `LambdaWitness.Unwitnessed`

```csharp
{ "popmart", "demandware-classic", "demandware-dual", "collectplus-app",
  "structure-token-multi", "structure-token-single" }
```

**注释：Flows with no ownership witness — their gaps stay unresolved.**

**→ 注意：`popmart` 也在里面。R835–R838 说它「没有」实现，而这里说的是「没有 ownership witness」——
两句话不同，不宜混用。**

| 仍 Unknown | |
|---|---|
| `collectplus-app` 的 ownership witness | 这正是登记原因 |
| `CreateCheckoutApp`/`GetDelivery` 族内具体端点 | 族已定位，未一一对上 |
| `popmart`/`structure-token-*` 的「没有」vs「未证」 | 两种说法要分开 |

### 纪律

**判据 (f) 的正确做法不是「先建清单再裁决」，是「先读 `Flows` 目录里的分析文件，它们就是清单」。**
**七轮五次建清单，五次都低估 —— 这不是疏忽，是方法缺一步。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R848", BLOCKER)
    ensure(RSTATUS, "R848", BLOCKER)
    ensure(RVERDICT, "第 848 轮", VERDICT)
    ensure(BACKLOG, "R848", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R848" not in h:
        h += ("\n## R848 补充 — 线索收尾\n\n"
              "**最后 4 条不是 Unknown，是已登记未证**：`LambdaWitness.Unwitnessed` 里就列着 `collectplus-app`。\n"
              "**端点族一直在**：`StoreApiFamilies.cs` 的 `/component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores`"
              "—— 探针找「标识符含 CollectPlus」，它写在路径里，所以 0 命中。\n"
              "**注意**：`popmart` / `structure-token-*` 也在 `Unwitnessed` 里 —— R835–R838 说「没有」，这里说「未证」，**两句话不同**。\n"
              "**判据 (f) 的正确做法：先读 `Flows` 目录里的分析文件，它们就是清单。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R848"), (RSTATUS, "R848"), (RVERDICT, "第 848 轮"), (BACKLOG, "R848")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R848: the last four are a registered state, not an unknown\n\n"
         "The four remaining CollectPlus names turn out not to be open questions. StoreApiFamilies carries the"
         " endpoint family, and one of its paths says the word outright:"
         " /component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores for GetCollectPlusLocations, with"
         " cac/submit and its siblings alongside. My probes looked for identifiers containing CollectPlus and found"
         " nothing, because the word lives in a URL while the constant is called PickupStores -- which is the fourth"
         " time this session that a probe searched identifiers while the real thing was a path.\n\n"
         "More to the point, LambdaWitness already lists collectplus-app under Unwitnessed, with the comment that flows"
         " without an ownership witness keep their gaps unresolved. So the flow's status has been recorded all along:"
         " endpoint family known, ownership unproven. Treating it as the last pending item was my error, not the"
         " repository's omission.\n\n"
         "The chain closes at zero pending, but zero was already true at the end of the previous round. The four were"
         " never pending; they were documented.\n\n"
         "Across seven rounds I built five inventories and underestimated five times. R838 thought Pop Mart's draw was"
         " one unmodelled surface and it was a nine-method subsystem with three sibling flows. R844 counted 108 unmatched"
         " names and 49 were already in the base class. R846 found the dual flow answered in R124. R847 found two step"
         " maps answering thirteen names. R848 found the last four already registered. The shape is identical every time:"
         " I build a list at the level of names while the repository's answers live at the level of meaning, in step maps,"
         " controller tables, API family files and the witness list.\n\n"
         "So the correct procedure for criterion (f) is not to build a list and then adjudicate it. It is to read the"
         " analysis files under Flows first, because they are the list.\n\n"
         "One thing to keep straight from here: Pop Mart appears in Unwitnessed as well, and that says something"
         " different from R835 through R838's finding that the replica has none of its draw surface. Absent and unproven"
         " are different claims and must not be merged.\n\n"
         "Unknown: the ownership witness for collectplus-app, which is why it is registered; the specific endpoints for"
         " CreateCheckoutApp and GetDelivery within the singlepagecheckout family, located as a family but not paired one"
         " by one; and the distinction between absent and unproven for Pop Mart and the structure-token flows.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
