"""Record R996: DataDome is wired, 2/6 becomes 3/6."""

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
### DataDome 接上了 —— 墙从 **2/6** 到 **3/6**，而这一轮写了真代码（R996）

**R995 说下一轮写 DataDome 的存回调用。写了：新建 `Scripts/DataDomeClearance.cs`（125 行），
并在 `SolveDetectedWallAsync` 里加了一条分支。**

### ① 先看已 `Wired` 的两个是怎么接的

**`SolveDetectedWallAsync`（`StoreFlow.cs:406`）是**唯一的派发点**，而它只放行两个：**

```csharp
if (vendor is not ("cloudflare" or "kasada")) return StepOutcome.Success();   // datadome 走不到任何 solver
...
if (vendor == "cloudflare") { … CloudflareClearance.ApplyAsync … }
var kasada = KasadaStrategyRunner.Default();
return await KasadaClearance.ApplyAsync(…);
```

> **所以「有协议」还不够 —— 派发点的白名单里没有 datadome。
> 那正是 `Wired` 的意思：检测 → 求解 → 存回，**而三样都要有人调用**。**

### ② 写了什么

**`src/Cybersole.Stores/Scripts/DataDomeClearance.cs`，形状与 `CloudflareClearance.cs` 对称：**

| 元素 | 依据 |
|---|---|
| `SensorUrl = "https://" + AntiBotVendors.DataDomeSensor` | 镜像 `https://datadome.cybersole.io/sensor` |
| `SdkUrl = "https://" + AntiBotVendors.DataDomeSdk` | 镜像 `https://api-sdk.datadome.co/sdk/` |
| `ClearanceCookie = "datadome"` | `AntiBotProtocol.CookiesFor("DataDome")` 已记 |
| `Stages` 四条 | 镜像四句日志：Getting / Initialising / Solving / Submitting DataDome |
| `ApplyAsync` 存回 | `Vars[ClearanceVar] = token` **且** `Cookies["datadome"] = token` |
| 未配置时 | 返回**状态**而非错误（与 `ServiceCloudflareSolver` 同一决定） |

**而派发点加了一条：**

```csharp
if (vendor is not ("cloudflare" or "kasada" or "datadome")) return StepOutcome.Success();
...
if (vendor == "datadome")
{
    var sensor = InjectedDataDomeSensor.Default();
    return await DataDomeClearance.ApplyAsync(c, sensor, c.Url ?? string.Empty, ct);
}
```

### ③ 而「一个都没配」这件事被写成事实而不是失败

**`InjectedDataDomeSensor` 无 call 时返回：**

> 「DataDome relay not configured: the image names datadome.cybersole.io/sensor but this workspace has no credentials for it」

**→ 与 `cf-solver.cybersole.io` 探到 401 时 Cloudflare 那条路一样：host 是真的、要凭据，而凭据我们没有。
→ 所以**不假装成功**，也不当失败，而是把状态记下来让流程继续 —— 下一个请求再试。**

### ④ 而这一轮没有发明第二条路

**镜像只命名**一个 relay + 一个 SDK**。所以 DataDome 这边**没有** service→in-bot 的阶梯，
只有一条 `IDataDomeSensor`。**

> **`CloudflareClearance` 的注释写着 Cloudflare 有两条路（service 在前、本地在后），
> 而 DataDome 的镜像证据里没有第二条 —— 造一条会是镜像没有的策略。**

### ⑤ 改了 5 处断言，其中两处是「钉住 2/6」的

| 文件 | 改了什么 |
|---|---|
| `VendorWiring.cs` | datadome 行 → `State.Wired` + 新 note（引用 R141 的更正与派发点） |
| `VendorWiringTests.cs` | `Wired` 加 datadome；`Gaps` 去掉它；用例名 `TwoOfSixAreWired` → `ThreeOfSixAreWired` |
| `WallDispatchTests.cs` | 派发白名单串加 `datadome`；`Wired` 加它；`Gaps.Count` 4 → 3；注释「two wired, four gaps」→「three wired, three gaps」 |
| `WallSolvingTests.cs` | datadome → `Wired`；删掉 R995 那条 `Assert.NotEqual(Wired, …)`（它现在该等于） |

> **而 `VendorWiring.Wired` 的顺序是**行序**不是字母序**：`["cloudflare", "kasada", "datadome"]`。
> 第一次改成了字母序，测试立刻报 `Collections differ` —— **一个陈列顺序的假设，一次就露。**

### ⑥ 一个仍然诚实的边界

**`Wired` 现在说「三样都在」，而「求解」那一样在默认配置下**返回未配置**。
所以 3/6 的意思是：**调用链存在、派发到它、存回写对了**，而不是「这个墙在本机能过**。

> **这与 Cloudflare / Kasada 的 2/6 是**同一口径** —— 那两个的 service 路也需要凭据。
> 所以 3/6 没有虚高。**

### 数字

| 度量 | R995 | **R996** |
|---|---|---|
| 套件 | 2209 | **2209** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| **墙 Wired** | 2 / 6 | **3 / 6** |
| **墙的缺口** | 4 | **3（imperva 证据 · perimeterx 证据 · queue-it 等待）** |
| 新增源文件 | 0 | **1（`DataDomeClearance.cs`）** |

### 教训

> **`Wired` 这个词在这里不是「协议已知」，是「三样都有人调」。
> 而当我把 ProtocolUnrecorded 那种状态写出来之后，它看起来已经很像做完了 —— 一个更准确的名字
> 会让缺口显得更小。**
> **→ 一个标签的改善不等于工作的进展。R995 那个 state 是对的，而它一个字都没让墙过去。**
"""

if "DataDome 接上了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 996 轮：DataDome 接上了 —— 墙 2/6 → 3/6，这一轮写了真代码

### ① 先看已 Wired 的两个怎么接的

**`SolveDetectedWallAsync`（`StoreFlow.cs:406`）是唯一派发点，而它只放行两个：**

```csharp
if (vendor is not ("cloudflare" or "kasada")) return StepOutcome.Success();   // datadome 走不到任何 solver
```

> **所以「有协议」不够 —— 派发白名单里没有 datadome。**`Wired` 的意思是三样都有人调。**

### ② 写了 `DataDomeClearance.cs`（125 行），与 `CloudflareClearance.cs` 对称

| 元素 | 依据 |
|---|---|
| `SensorUrl` | 镜像 `https://datadome.cybersole.io/sensor` |
| `SdkUrl` | 镜像 `https://api-sdk.datadome.co/sdk/` |
| `ClearanceCookie = "datadome"` | `AntiBotProtocol.CookiesFor("DataDome")` |
| `Stages` 四条 | 镜像四句日志 Getting / Initialising / Solving / Submitting |
| 存回 | `Vars[ClearanceVar]` **且** `Cookies["datadome"]` |

**派发点加分支：`if (vendor is not (… or "datadome"))` + `if (vendor == "datadome") { … }`。**

### ③ 没配时写成事实而非失败

> 「DataDome relay not configured: the image names datadome.cybersole.io/sensor but this workspace has no
> credentials for it」

**与 `cf-solver.cybersole.io` 的 401 同一条路：不假装成功，也不当失败。**

### ④ 这一轮没发明第二条路

**镜像只命名一个 relay + 一个 SDK。所以 DataDome **没有** service→in-bot 阶梯，
只有一条 `IDataDomeSensor`。造第二条会是镜像没有的策略。**

### ⑤ 改了 5 处断言，其中两处是「钉住 2/6」的

| 文件 | 改了什么 |
|---|---|
| `VendorWiring.cs` | datadome → `Wired` + 新 note |
| `VendorWiringTests.cs` | `Wired` 加它 · `Gaps` 去它 · 用例名 → `ThreeOfSixAreWired` |
| `WallDispatchTests.cs` | 白名单串 · `Wired` · `Gaps.Count` 4→3 · 注释 |
| `WallSolvingTests.cs` | datadome → `Wired`；删 R995 那条 `NotEqual(Wired, …)` |

> **`Wired` 的顺序是**行序**不是字母序**：`["cloudflare", "kasada", "datadome"]`。
> 第一次改成字母序，测试立刻报 `Collections differ` —— **一个陈列顺序的假设，一次就露。**

### ⑥ 诚实的边界

**`Wired` 说「三样都在」，而「求解」默认返回未配置。
所以 3/6 的意思是：**调用链存在、派发到它、存回写对**，不是「本机能过」。
这与 Cloudflare / Kasada 的 2/6 **同一口径**，所以没有虚高。**

### 数字

| 度量 | R995 | **R996** |
|---|---|---|
| 套件 | 2209 | **2209** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| **墙 Wired** | 2 / 6 | **3 / 6** |
| **墙的缺口** | 4 | **3** |
| 新增源文件 | 0 | **1** |

### 教训

> **一个标签的改善不等于工作的进展。R995 那个 state 是对的，而它一个字都没让墙过去。
> 更准确的名字会让缺口显得更小 —— 这正是名字与工作之间最容易混的一步。**
"""

BACKLOG_ADD = """

## 优先级 ② — **DataDome 接线完成：墙 2/6 → 3/6；新建 `DataDomeClearance.cs`**（R996）

### 改了什么

| 文件 | 改了什么 |
|---|---|
| **`Scripts/DataDomeClearance.cs`（新，125 行）** | SensorUrl / SdkUrl / `datadome` cookie / 四阶段 / `ApplyAsync` 存回 / `IDataDomeSensor` + 未配置时返回状态串 |
| `Flows/StoreFlow.cs` | `SolveDetectedWallAsync` 白名单加 `datadome`；新增 datadome 分支 |
| `Scripts/VendorWiring.cs` | datadome 行 → `State.Wired` |
| `VendorWiringTests.cs` / `WallDispatchTests.cs` / `WallSolvingTests.cs` | 5 处断言（含两处钉住 2/6 的） |

### 边界（诚实）

**`Wired` = 检测 → 求解 → 存回三样都有人调，**不是**「本机能过」。
求解默认返回「relay not configured」，与 Cloudflare 的 401 同口径。**

### 数字

**套件 2209 · 陈旧度 0/0 · 函数数 173,952 · 墙 3/6 · 缺口 3（imperva 证据 · perimeterx 证据 · queue-it 等待）**

| 仍 Unknown | |
|---|---|
| imperva / perimeterx 的 cookie 家族 | 未取证 |
| DataDome relay 的凭据与字段顺序 | 无凭据 |

**纪律**：一个标签的改善不等于工作的进展。
"""

BLOCKER = """

---

## 420. **DataDome 接线完成：墙 2/6 → 3/6（新建 `DataDomeClearance.cs`）**

> R996。**新建 1 个源文件 + 改 2 个源 + 5 处断言。** 套件 **2209 通过 / 0 失败 / 0 跳过**。

### 一、先看已 Wired 的两个怎么接的

**`SolveDetectedWallAsync`（`StoreFlow.cs:406`）是**唯一的派发点**，而它只放行两个：**

```csharp
if (vendor is not ("cloudflare" or "kasada")) return StepOutcome.Success();   // datadome 走不到任何 solver
if (vendor == "cloudflare") { … CloudflareClearance.ApplyAsync … }
var kasada = KasadaStrategyRunner.Default();
return await KasadaClearance.ApplyAsync(…);
```

**→ 所以「有协议」还不够：派发白名单里没有 datadome。
→ `Wired` 的意思是「检测 → 求解 → 存回，三样都有人调」。**

### 二、写了 `src/Cybersole.Stores/Scripts/DataDomeClearance.cs`（125 行）

**形状与 `CloudflareClearance.cs` 对称：**

| 元素 | 依据 |
|---|---|
| `SensorUrl = "https://" + AntiBotVendors.DataDomeSensor` | 镜像 `https://datadome.cybersole.io/sensor` |
| `SdkUrl = "https://" + AntiBotVendors.DataDomeSdk` | 镜像 `https://api-sdk.datadome.co/sdk/` |
| `ClearanceCookie = "datadome"` | `AntiBotProtocol.CookiesFor("DataDome")` 已记 |
| `Stages` 四条 | 镜像四句日志：Getting / Initialising / Solving / Submitting DataDome |
| `ApplyAsync` 存回 | `Vars[ClearanceVar] = token` **且** `Cookies["datadome"] = token` |
| 未配置 | 返回**状态**而非错误 |

**派发点加了一条分支：**

```csharp
if (vendor is not ("cloudflare" or "kasada" or "datadome")) return StepOutcome.Success();
...
if (vendor == "datadome")
{
    var sensor = Cybersole.Stores.Scripts.InjectedDataDomeSensor.Default();
    return await Cybersole.Stores.Scripts.DataDomeClearance
        .ApplyAsync(c, sensor, c.Url ?? string.Empty, ct).ConfigureAwait(false);
}
```

### 三、「一个都没配」被写成事实而不是失败

**`InjectedDataDomeSensor` 无 call 时返回：**

> 「DataDome relay not configured: the image names datadome.cybersole.io/sensor but this workspace has no credentials for it」

**→ 与 `cf-solver.cybersole.io` 探到 401 时 Cloudflare 那条路一致：host 是真的、要凭据，而凭据我们没有。
→ 不假装成功，也不当失败，而是记状态让流程继续。**

### 四、这一轮没有发明第二条路

**镜像只命名**一个 relay + 一个 SDK**。所以 DataDome 这边**没有** service→in-bot 的阶梯，
只有一条 `IDataDomeSensor`。造第二条会是镜像没有的策略。**

### 五、改了 5 处断言，其中两处是「钉住 2/6」的

| 文件 | 改了什么 |
|---|---|
| `Scripts/VendorWiring.cs` | datadome 行 → `State.Wired` + 新 note（引用 R141 的更正与派发点） |
| `VendorWiringTests.cs` | `Wired` 加 datadome · `Gaps` 去掉它 · 用例名 `TwoOfSixAreWired` → `ThreeOfSixAreWired` |
| `WallDispatchTests.cs` | 派发白名单串加 `datadome` · `Wired` 加它 · `Gaps.Count` 4 → 3 · 注释 |
| `WallSolvingTests.cs` | datadome → `Wired`；删掉 R995 那条 `Assert.NotEqual(Wired, …)` |

**→ 一个踩到的细节：`VendorWiring.Wired` 的顺序是**行序**不是字母序**
（`["cloudflare", "kasada", "datadome"]`）。第一次改成字母序，测试立刻报 `Collections differ`。
**一个陈列顺序的假设，一次就露。****

### 六、诚实的边界

**`Wired` 现在说「三样都在」，而「求解」那一样在默认配置下**返回未配置**。
→ 所以 3/6 的意思是：**调用链存在、派发到它、存回写对了**，而不是「这个墙在本机能过」。
→ 这与 Cloudflare / Kasada 的 2/6 是**同一口径** —— 那两个的 service 路也需要凭据。
→ 所以 3/6 没有虚高。**

### 七、数字

| 度量 | R995 | R996 |
|---|---|---|
| 套件 | 2209 | **2209** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952（未 publish）** |
| **墙 Wired** | 2 / 6 | **3 / 6** |
| **墙的缺口** | 4 | **3（imperva 证据 · perimeterx 证据 · queue-it 等待）** |
| 新增源文件 | 0 | **1** |

### 八、验证

```
cd replica
python tools/snapshot.py
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug     -> 已成功生成
dotnet test --filter "FullyQualifiedName~VendorWiringTests|FullyQualifiedName~WallDispatchTests|FullyQualifiedName~WallSolvingTests|FullyQualifiedName~CloudflareClearanceTests" -m:1  -> 23 通过
python tools/metrics_report.py                                          -> 完整套件 exit 0  2209 通过 / 0 失败 / 0 跳过
```

### 九、仍然 Unknown

- **imperva / perimeterx 在镜像里的 cookie 家族**：**Unknown** —— 未取证。
- **DataDome relay 的凭据与字段顺序**：**Unknown** —— 无凭据，未探到。

### 十、教训

**`Wired` 这个词在这里不是「协议已知」，是「三样都有人调」。

而当我上一轮把 `OriginalSolvesProtocolUnrecorded` 那种状态写出来之后，它看起来已经很像做完了 ——
一个更准确的名字会让缺口显得更小。**

**→ 一个标签的改善不等于工作的进展。R995 那个 state 是对的，而它一个字都没让墙过去。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R996", BLOCKER)
    ensure(RSTATUS, "R996", BLOCKER)
    ensure(RVERDICT, "第 996 轮", VERDICT)
    ensure(BACKLOG, "R996", BACKLOG_ADD)

    note = (
        "\n## R996 补充 — **DataDome 接线完成：墙 2/6 → 3/6**（套件 2209）\n\n"
        "**新建 `src/Cybersole.Stores/Scripts/DataDomeClearance.cs`（125 行）**，与 `CloudflareClearance.cs` 对称：\n"
        "SensorUrl = `datadome.cybersole.io/sensor` · SdkUrl = `api-sdk.datadome.co/sdk/` · cookie `datadome` ·\n"
        "四阶段 Getting/Initialising/Solving/Submitting · `ApplyAsync` 存回 `Vars` **且** `Cookies` ·\n"
        "未配置时返回**状态**而非错误。\n\n"
        "**`SolveDetectedWallAsync` 白名单加 `datadome` + 新增分支** —— 之前它只放行 cloudflare/kasada，\n"
        "datadome 走不到任何 solver。**`Wired` 的意思是「检测→求解→存回三样都有人调」。**\n\n"
        "这一轮**没有**发明第二条路：镜像只命名一个 relay + 一个 SDK，所以没有 service→in-bot 阶梯。\n\n"
        "改了 5 处断言，其中两处是钉住 2/6 的（`VendorWiringTests` 用例名 → `ThreeOfSixAreWired`；\n"
        "`WallDispatchTests` 的 `Gaps.Count` 4→3）。**踩到一个细节：`Wired` 顺序是行序不是字母序** ——\n"
        "改成字母序立刻报 `Collections differ`。\n\n"
        "**边界**：3/6 是「调用链存在、派发到它、存回写对」，不是「本机能过」（求解默认返回未配置，\n"
        "与 Cloudflare 的 401 同口径）。\n\n"
        "数字：套件 2209 · 陈旧度 0/0 · 函数数 173,952（未 publish）· 墙 3/6 · 缺口 3。\n\n"
        "纪律：**一个标签的改善不等于工作的进展** —— R995 那个 state 是对的，而它一个字都没让墙过去。\n\n"
        "下一轮：imperva 或 perimeterx 的 cookie 取证（剩下两个缺口都是「缺证据」）；或 publish 一次把函数数刷新。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R996" not in h:
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
             for p, k in ((RBLOCK, "R996"), (RSTATUS, "R996"), (RVERDICT, "第 996 轮"), (BACKLOG, "R996")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R996: DataDome is wired, three walls of six\n\n"
         "R995 left DataDome labelled honestly and still unwired. This round writes the call.\n\n"
         "The dispatch point was the reason it could not work. SolveDetectedWallAsync is the only place that knows which\n"
         " wall is in the way, and its guard admitted cloudflare and kasada only, so a DataDome store detected the wall and\n"
         " never reached a solver. Having the protocol was never the whole of Wired.\n\n"
         "So DataDomeClearance now mirrors CloudflareClearance: the sensor URL the image names, the SDK host it also names,\n"
         " the datadome cookie the protocol table already recorded, and the four stages the image narrates -- Getting,\n"
         " Initialising, Solving, Submitting. ApplyAsync writes the token both as a session variable and into the cookie jar,\n"
         " which is the store step that was missing. An unconfigured sensor reports that it is unconfigured and returns the\n"
         " refusal as a status rather than an error, the same choice Cloudflare made when cf-solver answered 401.\n\n"
         "No second road was invented. The image names one relay and one SDK, so there is no service-then-in-bot ladder\n"
         " here; building one would be a strategy the original does not have.\n\n"
         "Five assertions moved, two of which existed to hold the old two-of-six. A detail worth recording: Wired lists in\n"
         " row order, not alphabetical, so the alphabetical expectation failed immediately with Collections differ. One\n"
         " mistaken assumption about ordering, caught in one run.\n\n"
         "The boundary is worth stating because the number looks better than the state. Wired means detect, solve and store\n"
         " are all called. It does not mean the wall falls on this machine: the solve step returns not-configured by\n"
         " default, exactly as Cloudflare's service road needs credentials this workspace lacks. Three of six is the same\n"
         " measure as the two that came before it, so it is not inflated.\n\n"
         "Figures: suite 2209, freshness zero, count 173,952 unpublished, walls three of six, gaps three, one source file\n"
         " added.\n\n"
         "Unknown: the Imperva and PerimeterX cookie families, and the DataDome relay's credentials and field order.\n\n"
         "The lesson is that improving a label feels like progress and is not. R995's state was the right label and it moved\n"
         " no wall; a better name makes the gap look smaller, which is the trap.\n\n"
         "One source file added, two sources and five assertions changed; suite green at 2209."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()