"""Record R1027: the relay and the third-party API are two different arrangements."""

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
### `RemoteApi` 盖了两件事：**自建中继**与**调第三方**（R1027）

**R1026 说下一轮找 kasada/akamai 的远端服务。找了，而**找到的东西否掉了 R1026 的判据**。**

### ① 镜像里原版**自己跑**几个服务

```
solver.cybersole     n=3
  0x1434563e6  SolverUrl<https://cf-solver.cybersole.io      ← 字段名与常量值粘连
  0x14705c6fc  https://cf-solver.cybersole.io
  0x14705c754  https://cf-solver.cybersole.io/v1/warm        ← 预热端点

cybersole.workers.dev  n=4
  https://cloudflare-jsd-gen.cybersole.workers.dev/api      ← JSD = JS Detection
  https://forter.cybersole.workers.dev/
  https://hcaptcha-cache.cybersole.workers.dev/
  https://proxy-data.cybersole.workers.dev/

datadome.cybersole    n=2
  https://datadome.cybersole.io/  ·  /sensor
```

**→ 所以 cloudflare 与 datadome 是**经原版自建的服务**解的 —— 而 R1026 把它们标成 `How.Local`。
→ **R1026 的判据（「失败词汇里有 `API down`」）错了**：它是**充分不必要**条件。**

### ② 而两个信号**从不共现**

| vendor | 有中继 host | 有 `API down` |
|---|---|---|
| cloudflare | **是**（`cf-solver` · `jsd-gen`） | 否 |
| datadome | **是**（`/sensor`） | 否 |
| kasada | 否 | **是** |
| akamai | 否 | **是** |

**→ 一个 `RemoteApi` 值盖住了两组**互斥**的事实。
→ 而那正是 R1020 那次（`Inferred` 盖两件事）的同一形状 ——**只是这次我上上轮刚修过它。**

### ③ 所以拆成五个值

```csharp
public enum How { None, Local, Relay, ThirdPartyApi, Unknown }
```

| vendor | How | 依据 |
|---|---|---|
| **cloudflare** | **`Relay`** | `cf-solver.cybersole.io` + `/v1/warm` · `cloudflare-jsd-gen…workers.dev/api` |
| **datadome** | **`Relay`** | `datadome.cybersole.io/sensor` |
| **kasada** | **`ThirdPartyApi`** | `API down (Contact staff)`，无中继 host |
| **akamai** | **`ThirdPartyApi`** | `API down (Contact Staff)`，无中继 host |
| perimeterx | `Local` | `Solving PerimeterX`，无中继无 outage |
| queue-it | `Local` | `Error Solving Queue-it (Softblock)`，同 |
| imperva | `None` | 无解 |

**→ `API down, contact staff` 只在**别人的** API 会挂时才有意义 —— 那是这个值存在的理由。**

### ④ 6 条守卫，其中一条是那次观察本身

| 守卫 | 断言 |
|---|---|
| `OnlyTheTwoWithAnOutageLineCallAThirdParty` | `ThirdPartyApi` = `{kasada, akamai}` |
| `TheTwoWithARelayHostUseIt` | `Relay` = `{cloudflare, datadome}` |
| `TheRestAreLocalOrNone` | `Local` = `{perimeterx, queue-it}` · `None` = `{imperva}` |
| **`RelayAndThirdPartyAreDisjoint`** | **无行同时满足「Relay」与「Note 含 API down」** |
| `NoRowClaimsUnknownYet` | 无行用 `Unknown` |
| `TheColumnDistinguishesTheCases` | 至少四种取值在用（列有信息） |

**→ 第 4 条是**那个观察的可执行形式**：两个信号从不共现，所以一个列不能诚实地同时装它们。**

### ⑤ 而这一轮有一个 `-99` 没解开

**`ida.py str "cybersole.io"` 转义后仍 `-99`，而手动跑 `"cybersole"` 成功（`n=40`，4629 字节）。
→ 所以 `-99` 有**第二个成因**，而这次我没定论。
→ 按 R1026 的纪律：标 **Unknown**，不写成「没有」。**

### ⑥ 数字

| 度量 | R1026 | **R1027** |
|---|---|---|
| 套件 | 2241 / 0 | **2243 / 0 / 0（+2）** |
| 产物陈旧度 | 4 / 3,859 | **4 / 3,869** |
| 函数数 | 174,336 | **174,336** |
| **`How` 取值数** | 4 | **5（+`Relay` / `ThirdPartyApi` 拆分）** |
| **`Relay` 厂商** | — | **2（cloudflare · datadome）** |
| **`ThirdPartyApi` 厂商** | — | **2（kasada · akamai）** |
| **原版自建服务 host** | 未知 | **7（cf-solver · 4 个 workers.dev · datadome · api）** |
| **`cybersole.io` 的 `-99`** | — | **Unknown（第二成因未定）** |

### 教训

> **R1026 的判据是从一条**症状**（`API down`）反推一个**机制**（远端解），而那条症状只覆盖一种机制。
> → 而更刺眼的是：**R1020 我刚为 `Inferred` 拆过一次列，R1026 又在 `RemoteApi` 上重犯。**
> **→ 所以那个教训不是「一个词别盖两件事」，而是：**每次新加一个枚举值，先问它能不能被两个
> 互斥的事实同时满足**。**
"""

if "`RemoteApi` 盖了两件事" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1027 轮：`RemoteApi` 盖了两件事 —— 自建中继与调第三方

### ① 镜像里原版自己跑几个服务

```
cf-solver.cybersole.io  ·  /v1/warm              ← cloudflare 的 solver
cloudflare-jsd-gen.cybersole.workers.dev/api     ← JSD = JS Detection
datadome.cybersole.io/  ·  /sensor
forter.cybersole.workers.dev/ · hcaptcha-cache… · proxy-data…
api.cybersole.io  ·  /connect/app
```

**→ cloudflare 与 datadome 是**经原版自建的服务**解的 —— R1026 标成 `How.Local`，**错**。
→ **R1026 的判据（「失败词汇有 `API down`」）是充分不必要条件。**

### ② 而两个信号**从不共现**

| vendor | 中继 host | `API down` |
|---|---|---|
| cloudflare · datadome | **是** | 否 |
| kasada · akamai | 否 | **是** |

**→ 一个 `RemoteApi` 值盖住两组**互斥**的事实 —— 与 R1020 那次同形，
而那次我**上上轮刚修过。****

### ③ 拆成五个值

```csharp
public enum How { None, Local, Relay, ThirdPartyApi, Unknown }
```

**cloudflare · datadome = `Relay`（自建）· kasada · akamai = `ThirdPartyApi`（会 down 的别人的 API）·
perimeterx · queue-it = `Local` · imperva = `None`。**

**→ `API down, contact staff` 只在**别人的** API 会挂时才有意义 —— 那是这个值存在的理由。**

### ④ 6 条守卫，其中一条是那次观察本身

`OnlyTheTwoWithAnOutageLineCallAThirdParty` · `TheTwoWithARelayHostUseIt` · `TheRestAreLocalOrNone` ·
**`RelayAndThirdPartyAreDisjoint`** · `NoRowClaimsUnknownYet` · `TheColumnDistinguishesTheCases`

**→ 第 4 条是观察的可执行形式：两个信号从不共现，一个列不能诚实地同时装它们。**

### ⑤ 而这一轮有一个 `-99` 没解开

**`ida.py str "cybersole.io"` 转义后仍 `-99`，而手动跑 `"cybersole"` 成功（`n=40`，4629 字节）。
→ `-99` 有**第二个成因**，这次没定论 ⇒ 标 **Unknown**。**

### ⑥ 数字

| 度量 | R1026 | **R1027** |
|---|---|---|
| 套件 | 2241 / 0 | **2243 / 0 / 0（+2）** |
| 产物陈旧度 | 4 / 3,859 | **4 / 3,869** |
| 函数数 | 174,336 | **174,336** |
| **`How` 取值数** | 4 | **5** |
| **`Relay` · `ThirdPartyApi`** | — | **2 · 2** |
| **原版自建服务 host** | 未知 | **7** |
| **`cybersole.io` 的 `-99`** | — | **Unknown** |

### 教训

> **R1026 的判据是从一条**症状**（`API down`）反推一个**机制**（远端解），而那条症状只覆盖一种机制。
> → 更刺眼的是：**R1020 我刚为 `Inferred` 拆过一次列，R1026 又在 `RemoteApi` 上重犯。**
> → 所以那个教训不是「一个词别盖两件事」，而是：**每次新加一个枚举值，先问它能不能被两个
> 互斥的事实同时满足**。**
"""

BACKLOG_ADD = """

## 优先级 ② — **`RemoteApi` 拆成 `Relay` 与 `ThirdPartyApi`；原版自建 7 个服务 host**（R1027）

### 证据：原版自己跑服务

```
cf-solver.cybersole.io  ·  /v1/warm        ← SolverUrl 字段 · cloudflare solver
cloudflare-jsd-gen.cybersole.workers.dev/api
datadome.cybersole.io/  ·  /sensor
forter.cybersole.workers.dev/ · hcaptcha-cache… · proxy-data…
api.cybersole.io  ·  /connect/app
```

### 两个信号互斥

| vendor | 中继 host | `API down` |
|---|---|---|
| cloudflare · datadome | **是** | 否 |
| kasada · akamai | 否 | **是** |

**→ 一个 `RemoteApi` 盖住两组互斥事实（R1020 同形，而那次刚修过）。**

### 拆

```csharp
public enum How { None, Local, Relay, ThirdPartyApi, Unknown }
```

`cloudflare` `datadome` = `Relay` · `kasada` `akamai` = `ThirdPartyApi` ·
`perimeterx` `queue-it` = `Local` · `imperva` = `None`。

### 6 条守卫

含 **`RelayAndThirdPartyAreDisjoint`**（观察的可执行形式）与 `TheColumnDistinguishesTheCases`。

### 数字

**套件 2243（+2）· 陈旧度 4 / 3,869 · 函数数 174,336 · How 4 → 5 值 · 自建 host 7 个**

| 仍 Unknown | |
|---|---|
| `ida.py str "cybersole.io"` 的 `-99` 第二成因 | 未定 |
| relay 的协议（`/v1/warm` 之后是什么） | 未取证 |

**纪律**：每次新加枚举值，先问它能不能被两个互斥的事实同时满足。
"""

BLOCKER = """

---

## 451. **`RemoteApi` 盖了两件事：自建中继与调第三方**

> R1027。**改 1 个源文件 + 1 个测试文件。** 套件 **2243 通过 / 0 失败 / 0 跳过**。

### 一、镜像里原版**自己跑**几个服务

```
solver.cybersole     n=3
  0x1434563e6  SolverUrl<https://cf-solver.cybersole.io      ← 字段名与常量值粘连
  0x14705c6fc  https://cf-solver.cybersole.io
  0x14705c754  https://cf-solver.cybersole.io/v1/warm        ← 预热端点

cybersole.workers.dev  n=4
  cloudflare-jsd-gen · forter · hcaptcha-cache · proxy-data
datadome.cybersole    n=2
  datadome.cybersole.io/  ·  /sensor
api.cybersole         n=2
  https://api.cybersole.io  ·  /connect/app
```

**→ 所以 cloudflare 与 datadome 是**经原版自建的服务**解的 —— R1026 把它们标成 `How.Local`，
  而 **R1026 的判据（「失败词汇里有 `API down`」）是充分不必要条件**。**

### 二、两个信号**从不共现**

| vendor | 有中继 host | 有 `API down` |
|---|---|---|
| cloudflare | **是**（`cf-solver` · `jsd-gen`） | 否 |
| datadome | **是**（`/sensor`） | 否 |
| kasada | 否 | **是** |
| akamai | 否 | **是** |

**→ 一个 `RemoteApi` 值盖住了两组**互斥**的事实。
→ 而那正是 R1020 那次（`Inferred` 盖两件事）的同一形状 —— **只是那次我上上轮刚修过它。****

### 三、所以拆成五个值

```csharp
public enum How { None, Local, Relay, ThirdPartyApi, Unknown }
```

| vendor | How | 依据 |
|---|---|---|
| **cloudflare** | **`Relay`** | `cf-solver.cybersole.io` + `/v1/warm` · `cloudflare-jsd-gen…workers.dev/api` |
| **datadome** | **`Relay`** | `datadome.cybersole.io/sensor` |
| **kasada** | **`ThirdPartyApi`** | `API down (Contact staff)`，无中继 host |
| **akamai** | **`ThirdPartyApi`** | `API down (Contact Staff)`，无中继 host |
| perimeterx | `Local` | `Solving PerimeterX`，无中继无 outage |
| queue-it | `Local` | `Error Solving Queue-it (Softblock)`，同 |
| imperva | `None` | 无解 |

**→ `API down, contact staff` 只在**别人的** API 会挂时才有意义 —— 那是这个值存在的理由。**

### 四、6 条守卫

| 守卫 | 断言 |
|---|---|
| `OnlyTheTwoWithAnOutageLineCallAThirdParty` | `ThirdPartyApi` = `{kasada, akamai}` |
| `TheTwoWithARelayHostUseIt` | `Relay` = `{cloudflare, datadome}` |
| `TheRestAreLocalOrNone` | `Local` = `{perimeterx, queue-it}` · `None` = `{imperva}` |
| **`RelayAndThirdPartyAreDisjoint`** | **无行同时满足「Relay」与「Note 含 API down」** |
| `NoRowClaimsUnknownYet` | 无行用 `Unknown` |
| `TheColumnDistinguishesTheCases` | 至少四种取值在用 |

**→ 第 4 条是**那个观察的可执行形式**：两个信号从不共现，所以一个列不能诚实地同时装它们。**

### 五、而这一轮有一个 `-99` 没解开

**`ida.py str "cybersole.io"` 转义后仍 `-99`，而手动跑 `"cybersole"` 成功（`n=40`，4629 字节）。
→ 所以 `-99` 有**第二个成因**，而这次我没定论。
→ 按 R1026 的纪律：标 **Unknown**，不写成「没有」。**

### 六、数字

| 度量 | R1026 | R1027 |
|---|---|---|
| 套件 | 2241 / 0 | **2243 / 0 / 0（+2）** |
| 产物陈旧度 | 4 / 3,859 | **4 / 3,869** |
| 函数数 | 174,336 | **174,336** |
| **`How` 取值数** | 4 | **5** |
| **`Relay` 厂商** | — | **2（cloudflare · datadome）** |
| **`ThirdPartyApi` 厂商** | — | **2（kasada · akamai）** |
| **原版自建服务 host** | 未知 | **7** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "cf-solver"            -> {"n":3}
python analysis/ida.py str "jsd-gen"              -> {"n":1}
python analysis/ida.py str "datadome.cybersole"   -> {"n":2}
python analysis/ida.py str "cybersole.workers.dev" -> {"n":4}
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~VendorSolvingMode" -m:1   -> 6 通过
python tools/metrics_report.py -> 完整套件 exit 0  2243 / 0 / 0
```

### 八、仍然 Unknown

- **`cybersole.io` 查询的 `-99` 第二成因**：**未定**。
- **relay 的协议（`/v1/warm` 之后是什么）**：**未取证**。

### 九、教训

**R1026 的判据是从一条**症状**（`API down`）反推一个**机制**（远端解），而那条症状只覆盖一种机制。**

**→ 而更刺眼的是：**R1020 我刚为 `Inferred` 拆过一次列，R1026 又在 `RemoteApi` 上重犯。**
**→ 所以那个教训不是「一个词别盖两件事」，而是：**每次新加一个枚举值，先问它能不能被两个
  互斥的事实同时满足**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1027", BLOCKER)
    ensure(RSTATUS, "R1027", BLOCKER)
    ensure(RVERDICT, "第 1027 轮", VERDICT)
    ensure(BACKLOG, "R1027", BACKLOG_ADD)

    note = (
        "\n## R1027 补充 — **`RemoteApi` 拆成 `Relay` 与 `ThirdPartyApi`；原版自建 7 个服务 host**（套件 2243）\n\n"
        "**证据**：`cf-solver.cybersole.io` + `/v1/warm`（`SolverUrl` 字段）· `cloudflare-jsd-gen.cybersole.workers.dev/api` ·\n"
        "`datadome.cybersole.io/sensor` · `forter`/`hcaptcha-cache`/`proxy-data` workers · `api.cybersole.io`。\n"
        "→ **cloudflare 与 datadome 走**自建中继**，而 R1026 标成 `How.Local` —— 错。**\n\n"
        "**两个信号互斥**：cloudflare/datadome 有中继 host 无 `API down`；kasada/akamai 反之。\n"
        "→ **一个 `RemoteApi` 盖住两组互斥事实 —— R1020 同形，而那次我上上轮刚修过。**\n\n"
        "**拆**：`How { None, Local, Relay, ThirdPartyApi, Unknown }`。\n"
        "cloudflare/datadome = `Relay` · kasada/akamai = `ThirdPartyApi` · perimeterx/queue-it = `Local` · imperva = `None`。\n"
        "**6 条守卫**，含 **`RelayAndThirdPartyAreDisjoint`**（观察的可执行形式）。\n\n"
        "**一个 `-99` 没解开**：`str \"cybersole.io\"` 转义后仍 -99，而 `str \"cybersole\"` 成功（n=40）⇒ 第二成因未定 ⇒ **Unknown**。\n\n"
        "数字：套件 2243（+2）· 陈旧度 4 / 3,869 · 函数数 174,336 · How 4 → **5** 值 · 自建 host **7** 个。\n\n"
        "纪律：**每次新加枚举值，先问它能不能被两个互斥的事实同时满足。**\n\n"
        "下一轮：relay 的协议（`cf-solver.cybersole.io/v1/warm` 之后是什么）—— 那是 cloudflare 求解的核心。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1027" not in h:
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
             for p, k in ((RBLOCK, "R1027"), (RSTATUS, "R1027"), (RVERDICT, "第 1027 轮"), (BACKLOG, "R1027")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1027: RemoteApi was covering a self-run relay and a third party at once\n\n"
         "R1026 ended by asking which remote service Kasada and Akamai use. Looking for it turned up services the\n"
         " original runs itself, and that finding retracts R1026's criterion rather than answering its question.\n\n"
         "cf-solver.cybersole.io carries a /v1/warm endpoint and a SolverUrl field; cloudflare-jsd-gen sits on the\n"
         " original's own Worker; datadome.cybersole.io/sensor was already known. So Cloudflare and DataDome are solved\n"
         " through infrastructure the original owns, and R1026 had them down as local, because its test was whether the\n"
         " failure vocabulary contains API down (Contact staff). That line only makes sense for somebody else's API, so it\n"
         " marks one way of solving remotely and not the only one.\n\n"
         "The two signals never co-occur. Cloudflare and DataDome have a relay host and no outage line; Kasada and Akamai\n"
         " have the outage line and no relay host. One enum value was holding both, which is exactly what R1020 fixed for\n"
         " the Inferred column two rounds ago.\n\n"
         "So How becomes None, Local, Relay and ThirdPartyApi, plus Unknown for a row that later cannot tell. Relay means\n"
         " the original routes through a service of its own; ThirdPartyApi means it calls one that can be down.\n\n"
         "Six guards pin the split. The load-bearing one asserts that no row is both a relay and an outage-line row,\n"
         " which is the observation that made one column untenable, expressed as an assertion instead of a paragraph.\n\n"
         "One query did not resolve: cybersole.io still returns -99 after escaping, while cybersole returns forty matches\n"
         " in under five kilobytes. So the sentinel has a second cause and this round did not find it. Following R1026's\n"
         " rule, that is unknown rather than absent.\n\n"
         "Figures: suite 2241 to 2243, freshness four files and 3,869 lines, count 174,336, How at five values, two\n"
         " vendors on the relay and two on a third party, and seven service hosts the original runs itself.\n\n"
         "Unknown: the protocol behind /v1/warm, and the second cause of the -99.\n\n"
         "The lesson is not that one word should not cover two things, since I wrote that down two rounds ago and then\n"
         " did it again -- it is that every time I add an enum value I should ask whether two facts that cannot both be\n"
         " true could both select it.\n\n"
         "One source file and one test file changed; suite green at 2243."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()