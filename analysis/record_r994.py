"""Record R994: R989's claim about vendor coverage was wrong, and the repo had said so for 850 rounds."""

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
### R989 那句「优先级 ② 的 vendor 覆盖是**完整的**」是**错的** —— 6 个墙里只有 2 个接通（R994）

**R993 说下一轮查 `DetectAsync` 接上没有。查的过程中发现那张表**早就在仓里**，
而它说的事与我在 R989 的结论相反。**

### ① 仓里有一张完整的墙接线审计表

**`src/Cybersole.Stores/Scripts/VendorWiring.cs`（R140/R141 建立）：**

| vendor | marker（检测） | cookie | **state** |
|---|---|---|---|
| cloudflare | `cf-chl` / `server: cloudflare` | `cf_clearance` | **Wired**（R140） |
| kasada | `kpsdk` | `kpsdk` | **Wired**（R141） |
| imperva | `_Incapsula_Resource` | 无 | **DetectedOnly** |
| datadome | `datadome` | `datadome` | **HostWithoutProtocol** |
| perimeterx | `px-captcha` | 无 | **DetectedOnly** |
| queue-it | `queue-it` | `queue-it-set-cookie` | **NotAChallenge** |

**而四个缺口各自有**不同**的原因，不是同一类：**

- **imperva**：镜像里既没有 Imperva 的 cookie，也没有 Imperva 的 host
- **datadome**：host 有（`datadome.cybersole.io`），**协议**没有
- **perimeterx**：注释写「deliberately blank: a token header exists, no `_px` cookie does」
- **queue-it**：**不是墙而是队列** —— 正确处置是**等**，不是求解

### ② 所以我在 R989 的结论错了

**R989 写：「优先级 ②（风控对抗）的 vendor 覆盖是**完整的**：cloudflare · kasada · datadome ·
perimeterx · queue-it · aycd · … 全 matched」。**

> **那个 12/12 来自 `vendor_coverage.py`，它答的是「这个厂商的名字在源码里出现过」。**
> **而 `VendorWiring` 答的是「检测 → 求解 → 存回，链条完整」。**
> **→ 两个问题的答案分别是 12/12 和 **2/6**。**
> **→ 而我把前者的答案写成了后者的结论 —— 这是同一个「名字出现 ≠ 接上」的错误，
> 只是这一层比 R989 修的那层更高：那一轮我修的是「两列用不同分母」，
> 这一轮发现其中一列问的根本不是这个问题。****

### ③ 而这个错误**已经被钉住了**，只是钉在另一个文件里

```
tests/Cybersole.Tests/VendorWiringTests.cs:37   Assert.Equal(6, VendorWiring.Rows.Count);
VendorWiringTests.cs:38                         Assert.Equal(new[] { "cloudflare", "kasada" }, VendorWiring.Wired);
VendorWiringTests.cs:48                         Assert.Equal(new[] { "imperva", "datadome", "perimeterx", "queue-it" }, …);
WallDispatchTests.cs:67-68                      Assert.Equal(new[] { "cloudflare", "kasada" }, …); Assert.Equal(4, Gaps.Count);
```

**→ 2 与 4 这两个数**已经有守卫**。所以「不知道」不是仓库的问题，是我没查。**

### ④ 而最刺的一件事：`VendorWiring.AuditRule` 早就写出了一句总结

```csharp
public const string AuditRule =
    "detection and storage are cheap and were already present; the call between them is the work";
```

**而 R992 的 `GetToken`（步骤存在、没有调用）与 R993 的 `HandleResponseAsync`
（分类表存在、不在执行路径上）—— 正是「检测和存储在、中间那个调用不在」。**

> **仓库在 R140 就把这句话写成了常量，并让测试钉住它。
> 而我在 R992–R993 花了三轮「发现」它。**
> **→ `where_is` 的纪律（R870，五次踩坑后立）在这里失效了三轮：
> 我查的都是**单个名字**（`GetToken` / `HandleResponseAsync` / `Detect`），
> 而没有查「这件事有没有一张表」。**

### ⑤ 所以优先级 ② 的真实剩余是**4 个墙**，而它们不是同一种活

| 墙 | 要做什么 | 缺什么 |
|---|---|---|
| imperva | 先在镜像里找到 cookie 家族或 host | **证据**，不是代码 |
| datadome | 写协议（host 已有） | 协议 —— 同 Cloudflare R140 之前的状态 |
| perimeterx | 先确认有没有 `_px` cookie | **证据** |
| queue-it | **不求解，等** | 一个等待策略，不是 solver |

> **→ 这比「12/12 全 matched」有用得多：它把「4 个缺口」分成「缺证据」与「缺代码」两类。**

### 数字

| 度量 | R993 | **R994** |
|---|---|---|
| 套件 | 2208 | **2208（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **墙的接线** | 未测 | **2 / 6 Wired** |
| **墙的缺口** | 未测 | **4（2 缺证据 · 1 缺协议 · 1 不是墙）** |
| **R989「vendor 覆盖完整」** | 已写 | **撤回** |

### 教训

> **`where_is` 查的是**名字**。而「这件事有没有一张表」是另一种查法，
> 而那张表可能早就把答案、原因分类、以及一句话总结都写好了。**
> **三轮的代价：我以为自己在发现，其实在重新发现。**
"""

if "R989 那句「优先级 ② 的 vendor 覆盖是**完整的**」是**错的**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 994 轮：R989 那句「优先级 ② vendor 覆盖完整」是错的 —— 6 个墙只有 2 个接通

### ① 仓里有一张完整的墙接线表

**`src/Cybersole.Stores/Scripts/VendorWiring.cs`（R140/R141）：**

| vendor | marker | cookie | **state** |
|---|---|---|---|
| cloudflare | `cf-chl` / `server` | `cf_clearance` | **Wired**（R140） |
| kasada | `kpsdk` | `kpsdk` | **Wired**（R141） |
| imperva | `_Incapsula_Resource` | 无 | **DetectedOnly** |
| datadome | `datadome` | `datadome` | **HostWithoutProtocol** |
| perimeterx | `px-captcha` | 无 | **DetectedOnly** |
| queue-it | `queue-it` | `queue-it-set-cookie` | **NotAChallenge** |

**四个缺口各有**不同**原因：imperva 既无 cookie 也无 host · datadome 有 host 无协议 ·
perimeterx「deliberately blank: a token header exists, no `_px` cookie does」·
queue-it **不是墙而是队列，正确处置是等**。**

### ② 所以 R989 的结论错了

**R989：「优先级 ② 的 vendor 覆盖是**完整的**……全 matched」。**
**那个 12/12 来自 `vendor_coverage.py`，它答「名字在源码里出现过」；`VendorWiring` 答「链条完整」。
两个答案是 12/12 和 **2/6**。**

> **这是「名字出现 ≠ 接上」的同一个错误，只是高一层：
> R989 修的是「两列用不同分母」，这一轮发现其中一列问的根本不是这个问题。**

### ③ 而这个错误早已被钉住，只是钉在另一个文件

```
VendorWiringTests.cs:37-48   Assert.Equal(6, Rows.Count); Wired == {cloudflare, kasada}
                             Gaps == {imperva, datadome, perimeterx, queue-it}
WallDispatchTests.cs:67-68   同上 + Assert.Equal(4, Gaps.Count)
```

**→ 2 与 4 已有守卫。「不知道」不是仓库的问题，是我没查。**

### ④ 最刺的一件事

```csharp
public const string AuditRule =
    "detection and storage are cheap and were already present; the call between them is the work";
```

**而 R992 的 `GetToken`、R993 的 `HandleResponseAsync` —— 正是「检测和存储在、中间那个调用不在」。
仓库在 R140 就把这句话写成了常量并让测试钉住，而我在 R992–R993 花了三轮「发现」它。**

> **`where_is` 的纪律（R870）失效了三轮：我查的都是**单个名字**，
> 没查「这件事有没有一张表」。**

### ⑤ 优先级 ② 的真实剩余：4 个墙，不是同一种活

| 墙 | 缺什么 |
|---|---|
| imperva | **证据**（cookie 家族 / host） |
| datadome | **协议**（host 已有） |
| perimeterx | **证据**（有没有 `_px` cookie） |
| queue-it | **等待策略**，不是 solver |

### 数字

| 度量 | R993 | **R994** |
|---|---|---|
| 套件 | 2208 | **2208（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **墙的接线** | 未测 | **2 / 6 Wired** |
| **墙的缺口** | 未测 | **4（2 缺证据 · 1 缺协议 · 1 不是墙）** |

### 教训

> **`where_is` 查的是**名字**。「这件事有没有一张表」是另一种查法 ——
> 而那张表可能早就把答案、原因分类、以及一句话总结都写好了。
> 三轮的代价：我以为自己在发现，其实在重新发现。**
"""

BACKLOG_ADD = """

## 优先级 ② — **墙接线 2/6 Wired；4 个缺口分三类；R989「覆盖完整」撤回**（R994）

### `VendorWiring.cs`（R140/R141）早有一张表

| vendor | state |
|---|---|
| cloudflare · kasada | **Wired**（R140 / R141） |
| imperva | DetectedOnly（镜像无 cookie 无 host） |
| datadome | HostWithoutProtocol（`datadome.cybersole.io` 有，协议无） |
| perimeterx | DetectedOnly（「token header exists, no `_px` cookie」） |
| queue-it | NotAChallenge（**队列不是墙，正确处置是等**） |

**守卫已存在：`VendorWiringTests.cs:37-54` · `WallDispatchTests.cs:67-68`（2 与 4）。**

### 撤回 R989

**R989「优先级 ② vendor 覆盖完整（12/12 matched）」—— `vendor_coverage` 答的是「名字出现过」，
`VendorWiring` 答的是「链条完整」，2/6。撤回。**

### 优先级 ② 的剩余

| 墙 | 缺什么 |
|---|---|
| imperva | 证据 |
| datadome | 协议 |
| perimeterx | 证据 |
| queue-it | 等待策略 |

### 数字

**套件 2208（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 墙 2/6 Wired · 缺口 4（2 证据 / 1 协议 / 1 非墙）**

| 仍 Unknown | |
|---|---|
| imperva / perimeterx 在镜像里的 cookie 家族 | 未取证 |

**纪律**：`where_is` 查名字；「这件事有没有一张表」是另一种查法。
"""

BLOCKER = """

---

## 418. **墙接线 2/6 Wired；R989「优先级 ② 覆盖完整」撤回**

> R994。**只取证，未改代码。** 套件 **2208（R993 的记录仍有效）**。

### 一、仓里早有一张完整的墙接线审计表

**`src/Cybersole.Stores/Scripts/VendorWiring.cs`（R140/R141 建立）：**

| vendor | marker（检测） | cookie | **state** |
|---|---|---|---|
| cloudflare | `cf-chl` / `server: cloudflare` | `cf_clearance` | **Wired**（R140） |
| kasada | `kpsdk` | `kpsdk` | **Wired**（R141） |
| imperva | `_Incapsula_Resource` | 无 | **DetectedOnly** |
| datadome | `datadome` | `datadome` | **HostWithoutProtocol** |
| perimeterx | `px-captcha` | 无 | **DetectedOnly** |
| queue-it | `queue-it` | `queue-it-set-cookie` | **NotAChallenge** |

**四个缺口各有**不同**原因：**

- **imperva**：镜像里既没有 Imperva 的 cookie，也没有 Imperva 的 host
- **datadome**：host 有（`datadome.cybersole.io`），**协议**没有
- **perimeterx**：注释「deliberately blank: a token header exists, no `_px` cookie does」
- **queue-it**：**不是墙而是队列** —— 正确处置是**等**，不是求解

### 二、所以 R989 的结论错了

**R989 写：「优先级 ②（风控对抗）的 vendor 覆盖是**完整的**：cloudflare · kasada · datadome ·
perimeterx · queue-it · aycd · … 全 matched」。**

**→ 那个 12/12 来自 `vendor_coverage.py`，它答的是「这个厂商的名字在源码里出现过」。
→ `VendorWiring` 答的是「检测 → 求解 → 存回，链条完整」。
→ 两个问题的答案是 12/12 与 **2/6**。
→ 我把前者的答案写成了后者的结论 —— 这是「名字出现 ≠ 接上」的同一个错误，
只是比 R989 修的那层更高：那一轮修的是「两列用不同分母」，
这一轮发现其中一列问的根本不是这个问题。**

### 三、而这个错误早已被钉住

```
tests/Cybersole.Tests/VendorWiringTests.cs:37   Assert.Equal(6, VendorWiring.Rows.Count);
VendorWiringTests.cs:38-48                      Wired == {cloudflare, kasada}; Gaps == {imperva, datadome, perimeterx, queue-it}
tests/Cybersole.Tests/WallDispatchTests.cs:67-68 同上 + Assert.Equal(4, Gaps.Count)
```

**→ 2 与 4 这两个数**已经有守卫**。所以「不知道」不是仓库的问题，是我没查。**

### 四、而最刺的一件事

```csharp
public const string AuditRule =
    "detection and storage are cheap and were already present; the call between them is the work";
```

**→ R992 的 `GetToken`（步骤存在、没有调用）与 R993 的 `HandleResponseAsync`
（分类表存在、不在执行路径上）—— 正是这句话描述的形状。
→ 仓库在 R140 就把这句话写成了常量，并让测试钉住它。
→ 而我在 R992–R993 花了三轮「发现」它。
→ **`where_is` 的纪律（R870，五次踩坑后立）在这里失效了三轮：
我查的都是**单个名字**（`GetToken` / `HandleResponseAsync` / `Detect`），
而没有查「这件事有没有一张表」。****

### 五、优先级 ② 的真实剩余：4 个墙，不是同一种活

| 墙 | 要做什么 | 缺什么 |
|---|---|---|
| imperva | 先在镜像里找到 cookie 家族或 host | **证据**，不是代码 |
| datadome | 写协议（host 已有） | 协议 —— 同 Cloudflare R140 之前的状态 |
| perimeterx | 先确认有没有 `_px` cookie | **证据** |
| queue-it | **不求解，等** | 一个等待策略，不是 solver |

**→ 这比「12/12 全 matched」有用：它把 4 个缺口分成「缺证据」与「缺代码」两类。**

### 六、数字

| 度量 | R993 | R994 |
|---|---|---|
| 套件 | 2208 | **2208（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| **墙的接线** | 未测 | **2 / 6 Wired** |
| **墙的缺口** | 未测 | **4（2 缺证据 · 1 缺协议 · 1 不是墙）** |
| **R989「vendor 覆盖完整」** | 已写 | **撤回** |

### 七、验证

```
cd replica
python - 读 src/Cybersole.Stores/Scripts/VendorWiring.cs -> Rows 6 行，State 见上表
python - 扫 tests 找 VendorWiring -> VendorWiringTests.cs:37-54 · WallDispatchTests.cs:67-68
dotnet test --filter "FullyQualifiedName~VendorWiringTests" -m:1  -> 通过
```

### 八、仍然 Unknown

- **imperva / perimeterx 在镜像里的 cookie 家族**：**Unknown** —— 未取证。
- **datadome 的协议**：**Unknown** —— host 有，协议不在镜像里（同 Cloudflare R140 之前）。

### 九、教训

**`where_is` 查的是**名字**。而「这件事有没有一张表」是另一种查法，
而那张表可能早就把答案、原因分类、以及一句话总结都写好了。**

**三轮的代价：我以为自己在发现，其实在重新发现。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R994", BLOCKER)
    ensure(RSTATUS, "R994", BLOCKER)
    ensure(RVERDICT, "第 994 轮", VERDICT)
    ensure(BACKLOG, "R994", BACKLOG_ADD)

    note = (
        "\n## R994 补充 — **墙接线 2/6 Wired；R989「优先级 ② 覆盖完整」撤回**（套件 2208，未改代码）\n\n"
        "`src/Cybersole.Stores/Scripts/VendorWiring.cs`（R140/R141）**早有完整审计表**：\n"
        "cloudflare **Wired** · kasada **Wired** · imperva DetectedOnly · datadome HostWithoutProtocol ·\n"
        "perimeterx DetectedOnly · queue-it NotAChallenge。**2/6 接通，4 个缺口各有不同原因。**\n\n"
        "→ **R989「优先级 ② vendor 覆盖完整（12/12）」撤回**：`vendor_coverage` 答「名字出现过」，\n"
        "`VendorWiring` 答「链条完整」，12/12 与 2/6。这是「名字出现 ≠ 接上」的同一错误，只是高一层。\n\n"
        "而 2 与 4 已被 `VendorWiringTests.cs:37-54` 与 `WallDispatchTests.cs:67-68` 钉住 → 「不知道」不是仓库的问题。\n\n"
        "**最刺的是 `VendorWiring.AuditRule`：**\n"
        "「detection and storage are cheap and were already present; the call between them is the work」\n"
        "—— 正是 R992/R993 花三轮「发现」的形状。仓库 R140 就写成了常量。\n\n"
        "优先级 ② 的剩余：imperva 缺**证据** · datadome 缺**协议** · perimeterx 缺**证据** · queue-it 缺**等待策略**。\n\n"
        "数字：套件 2208（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 墙 2/6 · 缺口 4（2 证据 / 1 协议 / 1 非墙）。\n\n"
        "纪律：**`where_is` 查名字；「这件事有没有一张表」是另一种查法。**\n\n"
        "下一轮：按这张表做 — datadome 的协议（唯一「缺代码」的那一格），或 imperva / perimeterx 的 cookie 取证。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R994" not in h:
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
             for p, k in ((RBLOCK, "R994"), (RSTATUS, "R994"), (RVERDICT, "第 994 轮"), (BACKLOG, "R994")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R994: two of six walls are wired, which retracts what I said about vendor coverage\n\n"
         "R993 left DetectAsync to be checked for wiring. Looking for it turned up something the repository has had since\n"
         " round 140: VendorWiring.cs, a table of all six walls with their markers, their cookies and a state per row.\n\n"
         "Cloudflare and Kasada are wired. Imperva and PerimeterX are detected and nothing more -- the image names no\n"
         " Imperva cookie and no Imperva host, and PerimeterX has a token header but no _px cookie. DataDome has a host and no\n"
         " protocol, the position Cloudflare was in before round 140. Queue-it is not a wall at all; it is a queue, and the\n"
         " correct handling is to wait rather than to solve. So two of six, and the four gaps are of three different kinds,\n"
         " each with its reason recorded.\n\n"
         "That retracts what I wrote two rounds ago. I reported priority two's vendor coverage as complete on the strength of\n"
         " vendor_coverage saying twelve of twelve matched. That tool answers whether a vendor's name appears anywhere in the\n"
         " source. This table answers whether detect, solve and store are connected. Twelve of twelve and two of six are both\n"
         " correct about their own question, and I wrote the first as the second. It is the same defect R989 itself repaired\n"
         " one layer down: that round found two columns measured against different denominators, and this round finds one of\n"
         " those columns was asking a different question altogether.\n\n"
         "The numbers were already held down. VendorWiringTests asserts six rows, the wired pair and the gap quartet, and\n"
         " WallDispatchTests repeats the same two figures. So the repository was not withholding anything; I simply did not\n"
         " look.\n\n"
         "The sharpest part is the constant in that file: detection and storage are cheap and were already present, the call\n"
         " between them is the work. GetToken last round and HandleResponseAsync the round before were both exactly that\n"
         " shape, and I spent three rounds arriving at a sentence the repository had written down at round 140 with a test\n"
         " holding it in place. where_is answers \"where is this name\"; it does not answer \"is there already a table about\n"
         " this\", and that second question is the one I failed to ask.\n\n"
         "So priority two's remaining work is four walls of three kinds: Imperva and PerimeterX need evidence before any\n"
         " code, DataDome needs a protocol, and Queue-it needs a wait policy rather than a solver.\n\n"
         "Figures: suite 2208 unchanged, freshness zero, count 173,952, walls two of six wired, four gaps split as two\n"
         " needing evidence, one needing a protocol and one that is not a challenge.\n\n"
         "Unknown: the Imperva and PerimeterX cookie families, which the image may or may not carry.\n\n"
         "No product code changed; one claim retracted and the real size of priority two recorded."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()