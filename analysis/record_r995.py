"""Record R995: DataDome's row was mislabelled, R141's intent was right, and two audits now cross-check."""

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
### DataDome 那行的**名字**错了，而 R141 的**判断**是对的（R995）

**R994 说下一轮做 datadome。取完证发现两件事：镜像里的协议比那张表说的多得多，
而「那张表被更正的判断还在被测试保护」这个说法，**只对了一半**。**

### ① 镜像里的 DataDome 是一条完整的链

```
<GenerateSensor>d__11   <SubmitSensor>d__12   <GetSensorData>d__34
sensorData(<datadomeCookie>5__2"<<SubmitCh>b__1>d
https://api-sdk.datadome.co/sdk/      https://datadome.cybersole.io/
https://datadome.cybersole.io/sensor
DataDomeKey  ·  DataDomeChallenge  ·  DatadomeSliderTask  ·  datadome=
Getting DataDome (I)  ·  Initialising DataDome  ·  Solving DataDome (I)  ·  Submitting DataDome (I)
```

> **三个 async 方法 + 一个 sensor 端点 + 四阶段顺序。
> 所以「有 host 无协议」是**错**的：协议就在镜像里。**
> **而这也正是 `WallSolving.DataDomeCorrection`（R141）写的那句：
> 「SolveBotD … the missing protocol is this workspace's gap, not the original's」。**

### ② 而我去看那条「保护错误」的测试，发现它**不是**

```csharp
// WallSolvingTests.cs:66（改前）
// but the audit's state stays as it is: this workspace still lacks the protocol
Assert.Equal(VendorWiring.State.HostWithoutProtocol, VendorWiring.For("datadome")!.State);
```

> **R141 是**有意**让状态停在 `HostWithoutProtocol` 的。
> 因为 `Wired` 的定义是「检测 → 求解 → **存回**」三件齐全，而**存回**我们没写。
> **→ 所以 R141 的判断完全正确：不能因为「原版能解」就把状态升成 Wired。**
> **→ 错的是那个**名字**：`HostWithoutProtocol` 说「协议不存在」，
> 而实际是「协议在原版里、缺在我们的笔记里」。**

**这两件事的差别是**归因方向**，而 `WallSolving.DataDomeCorrection` 已经把正确方向写下来了 ——
只是它没有可供 `VendorWiring` 用的词。**

### ③ 所以新增了一个 state，而不是把状态升成 Wired

```csharp
/// The original solves this vendor and this workspace has not written the call yet.
OriginalSolvesProtocolUnrecorded,
```

**它同时满足两边：**
- **不是 `Wired`** → R141 的意图保留（缺口仍在）
- **不说「协议不存在」** → 名字不再与同一仓库的更正相反

**而 `datadome` 那行的 note 现在写着 `SolveBotD` 与整条链，并指向 `WallSolving.DataDomeCorrection`。**

### ④ 而真正的新东西是一条**跨表**守卫

**`TheTwoAuditsAgree`：任何 `WallSolving.HasSolveFor(v)` 为真的厂商，
在 `VendorWiring` 里不得是 `HostWithoutProtocol` 或 `DetectedOnly`。**

> **理由：两张表都在同一个源码树里，各有各的测试，而**没有一条测试能看见另一张表**。
> 一张表说「无协议」、另一张说「原版能解」，两个断言都绿 ——
> 这正是 R978–R981 那三轮修的形状，只是这次不一致在**两张表之间**，不在一个脚本内部。**

**验过会红：把 datadome 行改回 `HostWithoutProtocol` → **2 条失败**，
其中 `TheTwoAuditsAgree` 是**独立**红的 —— 即使有人改了行却忘了改断言的期望值，它仍会红。**

```
把 datadome 行改回 HostWithoutProtocol
失败!  - 失败: 2，通过: 10，总计: 12
[FAIL] VendorWiringTests.TheGapsAreClassified
[FAIL] VendorWiringTests.TheTwoAuditsAgree
已还原
```

### ⑤ 而这一轮改了三处，全量套件从 2208 变 2209

| 文件 | 改了什么 |
|---|---|
| `Scripts/VendorWiring.cs` | 新增 `State.OriginalSolvesProtocolUnrecorded`；`datadome` 行改用它 + 新 note |
| `tests/.../VendorWiringTests.cs` | 断言改用新 state；新增 `TheTwoAuditsAgree` |
| `tests/.../WallSolvingTests.cs` | 断言改用新 state，并**保留**「不是 Wired」这一条 |

> **第三处是这一轮最要紧的一步：只改前两处会让 R141 的意图**消失**（缺口被读成已修）。
> 加上 `Assert.NotEqual(State.Wired, …)` 才把它钉住。**

### ⑥ 判据 (f) 的 4 个缺口现在只剩 **2 个缺证据**

| 墙 | 之前 | 现在 |
|---|---|---|
| imperva | 缺证据 | 缺证据 |
| **datadome** | **「缺协议」** | **协议在镜像里；缺的是调用** |
| perimeterx | 缺证据 | 缺证据 |
| queue-it | 不是墙 | 不是墙 |

**→ 而 `Wired` 仍是 **2 / 6** —— 这一个没动，因为**存回**那一步确实没写。**

### 数字

| 度量 | R994 | **R995** |
|---|---|---|
| 套件 | 2208 | **2209（+1 跨表守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 墙 Wired | 2 / 6 | **2 / 6（未变）** |
| **墙的四状态** | 4 种 | **5 种** |
| **跨表矛盾** | 1（datadome） | **0（现有守卫）** |

### 教训

> **我上一轮说「一个测试在保护一个已被更正的错误」—— 那句话是错的，而错的方式很有教益：
> 测试保护的**不是**错误结论，是**正确的**约束（缺口仍在），
> 而它用了一个**会误导的名字**去表达那个约束。**
> **→ 所以我差点把一条正确的守卫当成坏的改掉。这与 R980 那次（守卫对象为空）是同一课：
> 一个看起来在阻碍你的守兵，可能正站在正确的位置上。**
"""

if "DataDome 那行的**名字**错了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 995 轮：DataDome 那行的名字错了，而 R141 的判断是对的

### ① 镜像里的 DataDome 是一条完整的链

```
<GenerateSensor>d__11   <SubmitSensor>d__12   <GetSensorData>d__34
sensorData(<datadomeCookie>5__2"<<SubmitCh>b__1>d
https://api-sdk.datadome.co/sdk/   https://datadome.cybersole.io/sensor
DataDomeKey · DataDomeChallenge · DatadomeSliderTask · datadome=
Getting / Initialising / Solving / Submitting DataDome
```

> **所以「有 host 无协议」是错的：协议就在镜像里。而 `WallSolving.DataDomeCorrection`（R141）
> 早就写了这句 —— 只是它没有可供 `VendorWiring` 用的词。**

### ② 而那条测试**不是**在保护错误

```csharp
// but the audit's state stays as it is: this workspace still lacks the protocol
Assert.Equal(VendorWiring.State.HostWithoutProtocol, VendorWiring.For("datadome")!.State);
```

> **R141 是**有意**让状态停在 `HostWithoutProtocol`：`Wired` 要求「检测→求解→**存回**」三件齐全，
> 而存回我们没写。所以它的判断正确。
> 错的是**名字** —— `HostWithoutProtocol` 说「协议不存在」，而实际是「协议在原版里、缺在我们的笔记里」。**

### ③ 新增 state 而不是升成 Wired

```csharp
/// The original solves this vendor and this workspace has not written the call yet.
OriginalSolvesProtocolUnrecorded,
```

**同时满足两边：不是 `Wired`（缺口仍在）· 不说「协议不存在」。**

### ④ 而真正的新东西是一条**跨表**守卫

**`TheTwoAuditsAgree`：`WallSolving.HasSolveFor(v)` 为真的厂商，在 `VendorWiring` 里不得是
`HostWithoutProtocol` 或 `DetectedOnly`。**

> **两张表在同一源码树里，各有测试，而没有一条能看见另一张。
> 一张说「无协议」、另一张说「原版能解」，两个断言都绿 ——
> 这正是 R978–R981 那三轮修的形态，只是这次不一致在**两张表之间**。**
> **验过会红：改回 `HostWithoutProtocol` → 2 条失败，其中 `TheTwoAuditsAgree` **独立**红
> （即使忘了改断言的期望值，它仍会红）。**

### ⑤ 改了三处

| 文件 | 改了什么 |
|---|---|
| `Scripts/VendorWiring.cs` | 新增 state；`datadome` 行改用它 + 新 note |
| `tests/.../VendorWiringTests.cs` | 断言改用新 state；新增 `TheTwoAuditsAgree` |
| `tests/.../WallSolvingTests.cs` | 断言改用新 state，并**保留**「不是 Wired」 |

> **第三处最要紧：只改前两处会让 R141 的意图消失（缺口被读成已修）。**

### ⑥ 判据 (f) 的 4 个缺口现在只剩 2 个缺证据

| 墙 | 之前 | 现在 |
|---|---|---|
| imperva | 缺证据 | 缺证据 |
| **datadome** | **「缺协议」** | **协议在镜像里；缺的是调用** |
| perimeterx | 缺证据 | 缺证据 |
| queue-it | 不是墙 | 不是墙 |

**`Wired` 仍是 2 / 6 —— 这一个没动，因为**存回**那一步确实没写。**

### 数字

| 度量 | R994 | **R995** |
|---|---|---|
| 套件 | 2208 | **2209（+1 跨表守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 墙 Wired | 2 / 6 | **2 / 6（未变）** |
| **墙的四状态** | 4 种 | **5 种** |
| **跨表矛盾** | 1 | **0** |

### 教训

> **我上一轮说「一个测试在保护一个已被更正的错误」—— 那句是错的，而错的方式有教益：
> 测试保护的**不是**错误结论，是**正确的**约束（缺口仍在），而它用了一个**会误导的名字**去表达它。
> → 我差点把一条正确的守卫当成坏的改掉。这与 R980（守卫对象为空）同一课：
> 一个看起来在阻碍你的守兵，可能正站在正确的位置上。**
"""

BACKLOG_ADD = """

## 优先级 ② — **DataDome：协议在镜像里；新增 `OriginalSolvesProtocolUnrecorded`；+1 跨表守卫**（R995）

### 取证

```
<GenerateSensor>d__11  <SubmitSensor>d__12  <GetSensorData>d__34
https://datadome.cybersole.io/sensor   https://api-sdk.datadome.co/sdk/
DataDomeKey · DataDomeChallenge · DatadomeSliderTask
Getting / Initialising / Solving / Submitting DataDome
```

**→ 「有 host 无协议」错：协议在镜像里，缺的是**存回调用**。**

### 改了三处

1. `Scripts/VendorWiring.cs` — 新增 `State.OriginalSolvesProtocolUnrecorded`；`datadome` 行改用它 + 新 note
2. `VendorWiringTests.cs` — 断言改用新 state；新增 **`TheTwoAuditsAgree`**（跨表守卫）
3. `WallSolvingTests.cs` — 断言改用新 state，**保留** `Assert.NotEqual(Wired, …)`

**第三处最要紧：只改前两处会让 R141 的意图消失（缺口被读成已修）。**

### 跨表守卫

**`WallSolving.HasSolveFor(v)` 为真 → `VendorWiring` 里不得是 `HostWithoutProtocol` / `DetectedOnly`。**
**验过会红：改回 → 2 失败，其中跨表那条**独立**红。**

### 判据 (f) 的 4 个缺口

| 墙 | 缺什么 |
|---|---|
| imperva | **证据** |
| **datadome** | **存回调用**（协议已知） |
| perimeterx | **证据** |
| queue-it | 等待策略（不是墙） |

**`Wired` 仍 2/6 —— 未变，因为存回确实没写。**

### 数字

**套件 2209（+1）· 陈旧度 0/0 · 函数数 173,952 · 墙 2/6 · 状态 5 种 · 跨表矛盾 0**

| 仍 Unknown | |
|---|---|
| imperva / perimeterx 在镜像里的 cookie 家族 | 未取证 |

**纪律**：一个看起来在阻碍你的守兵，可能正站在正确的位置上。
"""

BLOCKER = """

---

## 419. **DataDome 协议在镜像里；新增第 5 个 state；+1 跨表守卫（验过会红）**

> R995。**改 1 处源 + 2 处测试。** 套件 **2209 通过 / 0 失败 / 0 跳过**。

### 一、先取证：镜像里的 DataDome 是一条完整的链

```
<GenerateSensor>d__11   <SubmitSensor>d__12   <GetSensorData>d__34
sensorData(<datadomeCookie>5__2"<<SubmitCh>b__1>d
https://api-sdk.datadome.co/sdk/      https://datadome.cybersole.io/
https://datadome.cybersole.io/sensor
DataDomeKey  ·  DataDomeChallenge  ·  DatadomeSliderTask  ·  datadome=
Getting DataDome (I) · Initialising DataDome · Solving DataDome (I) · Submitting DataDome (I)
```

**→ 三个 async 方法 + 一个 sensor 端点 + 四阶段顺序。
→ 「有 host 无协议」是**错**的：协议就在镜像里。
→ 而 `WallSolving.DataDomeCorrection`（R141）早就写了这句 —— 只是它没有可供 `VendorWiring` 用的词。**

### 二、而那条「保护错误」的测试，核查后**不是**

```csharp
// WallSolvingTests.cs:66（改前）
// but the audit's state stays as it is: this workspace still lacks the protocol
Assert.Equal(VendorWiring.State.HostWithoutProtocol, VendorWiring.For("datadome")!.State);
```

**→ R141 是**有意**让状态停在 `HostWithoutProtocol` 的。
→ 因为 `Wired` 的定义是「检测 → 求解 → **存回**」三件齐全，而**存回**我们没写。
→ 所以 R141 的判断完全正确：不能因为「原版能解」就把状态升成 Wired。
→ 错的是那个**名字**：`HostWithoutProtocol` 说「协议不存在」，
而实际是「协议在原版里、缺在我们的笔记里」。**

### 三、所以新增一个 state，而不是升成 Wired

```csharp
/// <summary>
/// The original solves this vendor and this workspace has not written the call yet. R995 added this because the four
/// states above could not say it, and DataDome had been mislabelled as a result.
/// </summary>
OriginalSolvesProtocolUnrecorded,
```

**→ 同时满足两边：不是 `Wired`（R141 的意图保留）· 不说「协议不存在」（不再与更正相反）。
→ `datadome` 行的 note 现在写着 `SolveBotD` 与整条链，并指向 `WallSolving.DataDomeCorrection`。**

### 四、而真正的新东西是一条**跨表**守卫

**`TheTwoAuditsAgree`：任何 `WallSolving.HasSolveFor(v)` 为真的厂商，
在 `VendorWiring` 里不得是 `HostWithoutProtocol` 或 `DetectedOnly`。**

**→ 两张表都在同一个源码树里，各有各的测试，而**没有一条测试能看见另一张表**。
→ 一张表说「无协议」、另一张说「原版能解」，两个断言都绿。
→ 这正是 R978–R981 那三轮修的形态，只是这次不一致在**两张表之间**，不在一个脚本内部。**

**验过会红（把 datadome 行改回 `HostWithoutProtocol`）：**

```
失败!  - 失败: 2，通过: 10，总计: 12
[FAIL] VendorWiringTests.TheGapsAreClassified
[FAIL] VendorWiringTests.TheTwoAuditsAgree
已还原 -> 18 通过
```

**→ `TheTwoAuditsAgree` 是**独立**红的 —— 即使有人改了行却忘了改断言的期望值，它仍会红。**

### 五、改了三处

| 文件 | 改了什么 |
|---|---|
| `src/Cybersole.Stores/Scripts/VendorWiring.cs` | 新增 `State.OriginalSolvesProtocolUnrecorded`；`datadome` 行改用它 + 新 note |
| `tests/Cybersole.Tests/VendorWiringTests.cs` | 断言改用新 state；新增 `TheTwoAuditsAgree` |
| `tests/Cybersole.Tests/WallSolvingTests.cs` | 断言改用新 state，并**保留** `Assert.NotEqual(State.Wired, …)` |

**→ 第三处是这一轮最要紧的一步：只改前两处会让 R141 的意图**消失**（缺口被读成已修）。
→ 加上 `Assert.NotEqual(State.Wired, …)` 才把它钉住。**

### 六、判据 (f) 的 4 个缺口现在只剩 2 个缺证据

| 墙 | 之前 | 现在 |
|---|---|---|
| imperva | 缺证据 | 缺证据 |
| **datadome** | **「缺协议」** | **协议在镜像里；缺的是调用** |
| perimeterx | 缺证据 | 缺证据 |
| queue-it | 不是墙 | 不是墙 |

**→ `Wired` 仍是 **2 / 6** —— 这一个没动，因为**存回**那一步确实没写。**

### 七、数字

| 度量 | R994 | R995 |
|---|---|---|
| 套件 | 2208 | **2209（+1 跨表守卫）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 墙 Wired | 2 / 6 | **2 / 6（未变）** |
| **墙的状态数** | 4 | **5** |
| **跨表矛盾** | 1（datadome） | **0（现有守卫）** |

### 八、验证

```
cd replica
python tools/snapshot.py                                       -> 321 files
dotnet test --filter "FullyQualifiedName~WallSolvingTests|FullyQualifiedName~VendorWiringTests|FullyQualifiedName~WallDispatchTests" -m:1  -> 18 通过
  （把 datadome 行改回 HostWithoutProtocol -> 2 失败 -> 还原 -> 18 通过）
python tools/metrics_report.py                                 -> 完整套件 exit 0  2209 通过 / 0 失败 / 0 跳过
```

### 九、仍然 Unknown

- **imperva / perimeterx 在镜像里的 cookie 家族**：**Unknown** —— 未取证。
- **DataDome 的存回调用长什么样**：协议已知（sensor 端点 + 三方法 + 四阶段），但**抓取-求解-存回**
  那一段的字段名与顺序未取证。

### 十、教训

**我上一轮说「一个测试在保护一个已被更正的错误」—— 那句话是错的，而错的方式很有教益：
测试保护的**不是**错误结论，是**正确的**约束（缺口仍在），而它用了一个**会误导的名字**去表达那个约束。**

**→ 所以我差点把一条正确的守卫当成坏的改掉。这与 R980 那次（守卫对象为空）是同一课：
一个看起来在阻碍你的守兵，可能正站在正确的位置上。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R995", BLOCKER)
    ensure(RSTATUS, "R995", BLOCKER)
    ensure(RVERDICT, "第 995 轮", VERDICT)
    ensure(BACKLOG, "R995", BACKLOG_ADD)

    note = (
        "\n## R995 补充 — **DataDome 协议在镜像里；新增第 5 个 state；+1 跨表守卫（验过会红）**（套件 2209）\n\n"
        "取证：镜像里 DataDome 是完整链 —— `<GenerateSensor>d__11` `<SubmitSensor>d__12` `<GetSensorData>d__34`、\n"
        "`https://datadome.cybersole.io/sensor`、`DataDomeKey`、`DatadomeSliderTask`、四阶段日志。\n"
        "→ **「有 host 无协议」是错的**；协议在镜像里，缺的是**存回调用**。\n\n"
        "**而我上一轮说「测试在保护一个已被更正的错误」—— 核查后只对一半**：`WallSolvingTests.cs:66` 的\n"
        "`HostWithoutProtocol` 是 R141 **有意**保持的（`Wired` 要求检测→求解→**存回**三件齐全，存回没写）。\n"
        "**错的是名字**：它说「协议不存在」，而实际是「协议在原版里、缺在我们的笔记里」。\n\n"
        "改三处：① `VendorWiring.cs` 新增 `State.OriginalSolvesProtocolUnrecorded` + datadome 行改用它\n"
        "② `VendorWiringTests.cs` 断言改用新 state + 新增 **`TheTwoAuditsAgree`**（跨表守卫）\n"
        "③ `WallSolvingTests.cs` 断言改用新 state，**保留** `Assert.NotEqual(Wired, …)` —— 这一条最要紧，\n"
        "只改前两处会让 R141 的意图消失。\n\n"
        "跨表守卫：`WallSolving.HasSolveFor(v)` 为真 → `VendorWiring` 不得是 `HostWithoutProtocol`/`DetectedOnly`。\n"
        "**验过会红**：改回 → 2 失败，其中跨表那条**独立**红。\n\n"
        "判据 (f) 的 4 个缺口：imperva 缺证据 · **datadome 缺存回调用（协议已知）** · perimeterx 缺证据 ·\n"
        "queue-it 等待策略。**`Wired` 仍 2/6 —— 未变。**\n\n"
        "数字：套件 2209（+1）· 陈旧度 0/0 · 函数数 173,952 · 墙 2/6 · 状态 5 种 · 跨表矛盾 0。\n\n"
        "纪律：**一个看起来在阻碍你的守兵，可能正站在正确的位置上。**\n\n"
        "下一轮：写 DataDome 的存回调用（协议已知：sensor 端点 + 三方法 + 四阶段），把它从 2/6 推到 3/6。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R995" not in h:
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
             for p, k in ((RBLOCK, "R995"), (RSTATUS, "R995"), (RVERDICT, "第 995 轮"), (BACKLOG, "R995")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R995: DataDome's row was mislabelled, and the test I called wrong was right\n\n"
         "R994 left DataDome as the one wall needing code rather than evidence. Fetching the evidence first showed the row\n"
         " was wrong about the facts: the image carries the whole chain. GenerateSensor, SubmitSensor and GetSensorData are\n"
         " three state machines, the sensor endpoint is datadome.cybersole.io/sensor beside api-sdk.datadome.co/sdk/, and the\n"
         " four stages read Getting, Initialising, Solving and Submitting DataDome. So there is a protocol; what is missing is\n"
         " the call that stores the result.\n\n"
         "Then I went to the test I had described last round as protecting a corrected error, and it was not. R141 kept the\n"
         " row at HostWithoutProtocol on purpose: Wired means detect, solve and store all exist, and the store side is\n"
         " unwritten. That judgement was right and still is. What was wrong is the state's name, which says the protocol does\n"
         " not exist while the same repository had recorded that the original solves DataDome and only our notes were short.\n\n"
         "So the fix is a fifth state rather than a promotion. OriginalSolvesProtocolUnrecorded says the original solves it\n"
         " and this workspace has not written the call, which keeps R141's weight -- still not Wired -- and stops the row\n"
         " contradicting the correction. Three edits: the enum and the DataDome row, the wiring test's expectation plus a new\n"
         " cross-audit guard, and the wall test, where I deliberately kept the not-equal-to-Wired assertion. Dropping that\n"
         " would have let the correction be read as a fix.\n\n"
         "The cross-audit guard is the part with reach. Two tables sit in one source tree, each with its own tests, and no\n"
         " test could see the other, so a row saying no protocol and a constant saying the original solves it both stayed\n"
         " green. The guard reads both: any vendor WallSolving names a solve method for may not be recorded as\n"
         " HostWithoutProtocol or DetectedOnly. Putting the old value back fails two tests, and the cross-audit one fails\n"
         " independently of the row assertion -- which matters, because forgetting to update an expectation is exactly how\n"
         " this kind of disagreement survives.\n\n"
         "Criterion (f)'s four gaps now split as two needing evidence, one needing the store call with the protocol known,\n"
         " and one that is a queue rather than a challenge. Wired stays at two of six; that figure should not move until the\n"
         " store side exists.\n\n"
         "Figures: suite 2208 to 2209, freshness zero, count 173,952, walls two of six, five states, no cross-audit\n"
         " contradiction.\n\n"
         "Unknown: the Imperva and PerimeterX cookie families, and the field names and order of the DataDome store step.\n\n"
         "The lesson is that I called a correct guard broken because of the word it used. Round 980 taught the same thing\n"
         " from the other side: a guard that looks like it is in your way may be standing exactly where it should.\n\n"
         "One enum value added, one row corrected, one guard added; suite green at 2209."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()