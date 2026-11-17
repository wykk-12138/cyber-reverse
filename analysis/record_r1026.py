"""Record R1026: the outcome vocabulary has two layers, and only two vendors have an outage line."""

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
### `-99` 不是 0；而转义之后露出一个**两层结构**（R1026）

**R1025 说下一轮做 `BotDeflector` 或 softblock 协议。改成了先做一件更基础的事：
把七个 vendor 的**处置文案**一次问完（按 R1025 的教训，读不走我问题的那几行）。**

### ① 而第一批查询里有六行 `n=-99` —— 那不是「没有」

**`ida.py str` 收**正则**。而 `"Cloudflare Failed ("` 那个未转义的 `(` 让正则非法 ⇒ 查询抛错 ⇒
我的哨兵值 `-99`。**

**→ 而我差点把 `-99` 读成「0 命中」。
→ 那是 R1015/R1016 那条的第三次：**一个「0」可以是假的，而「-99」更是** —— 它连查询都没跑成。**

**→ 修法：`re.escape()`。转义之后六行全部 `n=0`，干净。**

### ② 而转义之后露出一个**两层结构**

```
Failed Solving Cloudflare (   n=3    → no clearance · too many rounds
Solving Cloudflare (          n=12
Akamai Failed (               n=1    → Akamai Failed (Rotating)
其余六家 Failed (             n=0
```

**→ 原版的失败文案分成两层：**

| 层 | 形 | 例 |
|---|---|---|
| **检测层** | `<Vendor> Failed` · `Blocked` · `block` · `(Rotating)` | `Akamai Blocked (IP)` · `PerimeterX block (Rotating proxy)` · `Akamai block (Rotating...)` |
| **求解层** | `Solving <Vendor> (...)` · `Failed Solving <Vendor> (...)` | `Solving Cloudflare (no clearance)` · `Failed solving Kasada (TL)` · `Solving Akamai (SBSD)` · `Error Solving Queue-it (Softblock)` |

### ③ 而关键的那一条：`API down (Contact staff)` **只有两家**

```
Kasada API down (Contact staff)      0x146dda8dc
Akamai API down (Contact Staff)      0x146b4010c
Akamai API down (Contact staff)      0x146b40164
```

**→ 其余四家**没有**这条。
→ 而一个 **API 会挂**，一个**本地例程不会** —— 它只是失败。**

> **→ 所以 kasada 与 akamai 是**经远端服务解**，而 cloudflare / datadome / perimeterx / queue-it 是**本地解**。
> → 那是一个新的、可验证的结构事实 —— 而它从「读了两层的文案」得到，不是从任何一句话推的。**

### ④ 所以加第八列 `How`

```csharp
public enum How { None, Local, RemoteApi, Unknown }
```

| vendor | How | 依据 |
|---|---|---|
| **kasada** | **`RemoteApi`** | `Kasada API down (Contact staff)` 在镜像里 |
| **akamai** | **`RemoteApi`** | `Akamai API down (Contact Staff)` + 两个 solver 模式 |
| cloudflare | `Local` | 词汇是轮次与 clearance，无 outage 行 |
| datadome | `Local` | `Solving DataDome (I)`，无 outage 行 |
| perimeterx | `Local` | `Solving PerimeterX`，无 outage 行 |
| queue-it | `Local` | `Error Solving Queue-it (Softblock)`，无 outage 行 |
| **imperva** | **`None`** | 无解 — 与 R1021 一致 |

**→ `Unknown` 存在但**无使用者** —— 那是给它**将来**用的（一个说不清的行该说 `Unknown` 而不是猜）。**

### ⑤ 4 条守卫

| 守卫 | 断言 |
|---|---|
| `OnlyTheTwoWithAnOutageLineAreRemote` | `RemoteApi` 恰好 = `{kasada, akamai}`（**行序**） |
| `TheOthersSplitBetweenLocalAndNone` | `Local` = 四家 · `None` = `{imperva}` |
| `NoRowClaimsUnknownYet` | 无行用 `Unknown` |
| `TheColumnDistinguishesTheTwo` | `RemoteApi` 与 `Local` 都非空（列**有信息**） |

### ⑥ 而**行序**那个坑我第三次撞上

**`RemoteApi` 的期望值我第一版写 `{ "akamai", "kasada" }`（字母序），红了。
→ 那是 R1009（`Wired` 行序）与 R1024（`Gaps` 行序）之后**第三次**。
→ 所以这次我把「行序不是字母序」写进了断言旁边的注释，而不是只改对。**

### ⑦ 数字

| 度量 | R1025 | **R1026** |
|---|---|---|
| 套件 | 2237 / 0 | **2241 / 0 / 0（+4）** |
| 产物陈旧度 | 4 / 3,835 | **4 / 3,859** |
| 函数数 | 174,336 | **174,336** |
| **`Row` 的列** | 7 | **8（+`How`）** |
| **`RemoteApi` 厂商** | 未知 | **2（kasada · akamai）** |
| **`n=-99` 的含义** | 未注意 | **查询失败（正则非法），不是 0** |
| **行序坑** | 2 次 | **3 次（注释已记）** |

### 教训

> **`-99` 是我自己设的哨兵，而它掩盖的是一次**语法错误** —— 我差点把它读成「没有」。**
> **→ 一个「0」可以是假阴性（R1015/R1016），而一个「-99」更坏：它连问题都没问出去。
> → 而两者在输出里长得一样安静。**
> **→ 所以读到任何非正数，第一个问题不是「所以是多少」，是「这个查询跑成了吗」。**
"""

if "`-99` 不是 0" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1026 轮：`-99` 不是 0；而转义之后露出一个两层结构

### ① 第一批查询有六行 `n=-99` —— 那不是「没有」

**`ida.py str` 收正则，而 `"Cloudflare Failed ("` 里未转义的 `(` 让正则非法 ⇒ 查询抛错 ⇒ 哨兵 `-99`。**

**→ 我差点把 `-99` 读成「0 命中」。那是 R1015/R1016 那条的第三次：
**一个「0」可以是假的，「-99」更是** —— 它连查询都没跑成。
→ 修法 `re.escape()`；转义后六行全部 `n=0`。**

### ② 而转义之后露出一个**两层结构**

| 层 | 形 | 例 |
|---|---|---|
| **检测层** | `<Vendor> Failed` · `Blocked` · `block` · `(Rotating)` | `Akamai Blocked (IP)` · `PerimeterX block (Rotating proxy)` |
| **求解层** | `Solving <Vendor> (...)` · `Failed Solving <Vendor> (...)` | `Solving Cloudflare (no clearance)` · `Failed solving Kasada (TL)` · `Solving Akamai (SBSD)` |

### ③ 而 `API down (Contact staff)` **只有两家**

```
Kasada API down (Contact staff)      0x146dda8dc
Akamai API down (Contact Staff)      0x146b4010c
Akamai API down (Contact staff)      0x146b40164
```

**→ 一个 API 会挂，一个本地例程不会 —— 它只是失败。
→ 所以 kasada 与 akamai 是**经远端服务解**，其余四家是**本地解**。那是一个可验证的结构事实。**

### ④ 加第八列 `How`

```csharp
public enum How { None, Local, RemoteApi, Unknown }
```

**kasada · akamai = `RemoteApi` · cloudflare · datadome · perimeterx · queue-it = `Local` ·
imperva = `None`。`Unknown` 存在但无使用者 —— 给将来「说不清」的行用。**

### ⑤ 4 条守卫

`OnlyTheTwoWithAnOutageLineAreRemote` · `TheOthersSplitBetweenLocalAndNone` ·
`NoRowClaimsUnknownYet` · `TheColumnDistinguishesTheTwo`

### ⑥ 而**行序**那个坑我第三次撞上

**期望值第一版写字母序，红了。R1009（`Wired`）· R1024（`Gaps`）之后第三次。
→ 这次把「行序不是字母序」写进了断言旁的注释，而不是只改对。**

### ⑦ 数字

| 度量 | R1025 | **R1026** |
|---|---|---|
| 套件 | 2237 / 0 | **2241 / 0 / 0（+4）** |
| 产物陈旧度 | 4 / 3,835 | **4 / 3,859** |
| 函数数 | 174,336 | **174,336** |
| **`Row` 的列** | 7 | **8（+`How`）** |
| **`RemoteApi` 厂商** | 未知 | **2** |
| **`n=-99` 的含义** | 未注意 | **查询失败，不是 0** |
| **行序坑** | 2 次 | **3 次** |

### 教训

> **`-99` 是我自己设的哨兵，而它掩盖的是一次**语法错误**。一个「0」可以是假阴性，而一个「-99」更坏：
> 它连问题都没问出去。而两者在输出里长得一样安静。**
> **→ 读到任何非正数，第一个问题不是「所以是多少」，是「这个查询跑成了吗」。**
"""

BACKLOG_ADD = """

## 优先级 ② — **`-99` 不是 0（正则非法）；两层文案结构；加 `How` 列（RemoteApi 只有两家）**（R1026）

### 判据缺陷

**`ida.py str` 收正则 ⇒ `"Cloudflare Failed ("` 未转义 `(` 让正则非法 ⇒ 查询抛错 ⇒ 哨兵 `-99`。
**六行 `-99` 不是「0 命中」**。修法 `re.escape()`；转义后六行全 `n=0`。**

**→ R1015/R1016 那条第三次：一个「0」可以是假的，「-99」更坏 —— 它连查询都没跑成。**

### 两层结构

| 层 | 形 |
|---|---|
| 检测层 | `<Vendor> Failed` · `Blocked` · `block` · `(Rotating)` |
| 求解层 | `Solving <Vendor> (...)` · `Failed Solving <Vendor> (...)`（带原因：no clearance · too many rounds · TL · SBSD · SDS · Softblock） |

### 而 `API down (Contact staff)` 只有两家

`Kasada API down (Contact staff)` · `Akamai API down (Contact Staff)` → **经远端服务解**；
其余四家**本地解**（本地例程不会「挂」，它只是失败）。

### 加 `How` 列（第 8 列）

```csharp
public enum How { None, Local, RemoteApi, Unknown }
```

`kasada` `akamai` = `RemoteApi` · `cloudflare` `datadome` `perimeterx` `queue-it` = `Local` ·
`imperva` = `None`。`Unknown` 无使用者（留给将来）。

### 4 条守卫

`OnlyTheTwoWithAnOutageLineAreRemote`（**行序**）· `TheOthersSplitBetweenLocalAndNone` ·
`NoRowClaimsUnknownYet` · `TheColumnDistinguishesTheTwo`

### 数字

**套件 2241（+4）· 陈旧度 4 / 3,859 · 函数数 174,336 · Row 列 7 → 8 · RemoteApi 2 · 行序坑 3 次**

| 仍 Unknown | |
|---|---|
| kasada/akamai 的远端服务是哪个 | 未取证 |

**纪律**：读到任何非正数，先问「这个查询跑成了吗」。
"""

BLOCKER = """

---

## 450. **`-99` 不是 0；两层文案结构；加 `How` 列**

> R1026。**改 1 个源文件 + 加 1 个测试文件。** 套件 **2241 通过 / 0 失败 / 0 跳过**。

### 一、第一批查询有六行 `n=-99` —— 那不是「没有」

**`ida.py str` 收**正则**。而 `"Cloudflare Failed ("` 那个未转义的 `(` 让正则非法 ⇒ 查询抛错 ⇒
  我的哨兵值 `-99`。**

**→ 而我差点把 `-99` 读成「0 命中」。
→ 那是 R1015/R1016 那条的第三次：**一个「0」可以是假的，而「-99」更是** —— 它连查询都没跑成。
→ 修法：`re.escape()`。转义之后六行全部 `n=0`，干净。**

### 二、转义之后露出一个**两层结构**

```
Failed Solving Cloudflare (   n=3    → no clearance · too many rounds
Solving Cloudflare (          n=12
Akamai Failed (               n=1    → Akamai Failed (Rotating)
其余六家 Failed (             n=0
```

| 层 | 形 | 例 |
|---|---|---|
| **检测层** | `<Vendor> Failed` · `Blocked` · `block` · `(Rotating)` | `Akamai Blocked (IP)` · `PerimeterX block (Rotating proxy)` |
| **求解层** | `Solving <Vendor> (...)` · `Failed Solving <Vendor> (...)` | `Solving Cloudflare (no clearance)` · `Failed solving Kasada (TL)` · `Solving Akamai (SBSD)` |

### 三、而 `API down (Contact staff)` **只有两家**

```
Kasada API down (Contact staff)      0x146dda8dc
Akamai API down (Contact Staff)      0x146b4010c
Akamai API down (Contact staff)      0x146b40164
```

**→ 一个 **API 会挂**，一个**本地例程不会** —— 它只是失败。
→ 所以 kasada 与 akamai 是**经远端服务解**，其余四家是**本地解**。**

### 四、所以加第八列 `How`

```csharp
public enum How { None, Local, RemoteApi, Unknown }
```

| vendor | How | 依据 |
|---|---|---|
| **kasada** | **`RemoteApi`** | `Kasada API down (Contact staff)` |
| **akamai** | **`RemoteApi`** | `Akamai API down (Contact Staff)` + 两个 solver 模式 |
| cloudflare · datadome · perimeterx · queue-it | `Local` | 求解词汇是轮次/原因，无 outage 行 |
| **imperva** | **`None`** | 无解（与 R1021 一致） |

**→ `Unknown` 存在但**无使用者** —— 给将来「说不清」的行用。**

### 五、4 条守卫

| 守卫 | 断言 |
|---|---|
| `OnlyTheTwoWithAnOutageLineAreRemote` | `RemoteApi` 恰好 = `{kasada, akamai}`（**行序**） |
| `TheOthersSplitBetweenLocalAndNone` | `Local` = 四家 · `None` = `{imperva}` |
| `NoRowClaimsUnknownYet` | 无行用 `Unknown` |
| `TheColumnDistinguishesTheTwo` | `RemoteApi` 与 `Local` 都非空 |

### 六、而**行序**那个坑我第三次撞上

**期望值第一版写 `{ "akamai", "kasada" }`（字母序），红了。
→ 那是 R1009（`Wired` 行序）与 R1024（`Gaps` 行序）之后**第三次**。
→ 这次把「行序不是字母序」写进了断言旁的注释，而不是只改对。**

### 七、数字

| 度量 | R1025 | R1026 |
|---|---|---|
| 套件 | 2237 / 0 | **2241 / 0 / 0（+4）** |
| 产物陈旧度 | 4 / 3,835 | **4 / 3,859** |
| 函数数 | 174,336 | **174,336** |
| **`Row` 的列** | 7 | **8（+`How`）** |
| **`RemoteApi` 厂商** | 未知 | **2（kasada · akamai）** |
| **`n=-99` 的含义** | 未注意 | **查询失败（正则非法），不是 0** |

### 八、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "Kasada Failed \\("     -> {"n":0}
python analysis/ida.py str "Akamai Failed \\("     -> {"n":1}（Akamai Failed (Rotating)）
python analysis/ida.py str "Kasada API down"       -> {"n":1}
python analysis/ida.py str "Akamai API down"       -> {"n":2}
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~VendorSolvingMode|~Vendor" -m:1 -> 51 通过
python tools/metrics_report.py -> 完整套件 exit 0  2241 / 0 / 0
```

### 九、仍然 Unknown

- **kasada / akamai 的远端服务是哪个**：**未取证**。

### 十、教训

**`-99` 是我自己设的哨兵，而它掩盖的是一次**语法错误** —— 我差点把它读成「没有」。**

**→ 一个「0」可以是假阴性（R1015/R1016），而一个「-99」更坏：它连问题都没问出去。
→ 而两者在输出里长得一样安静。**
**→ 所以读到任何非正数，第一个问题不是「所以是多少」，是「这个查询跑成了吗」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1026", BLOCKER)
    ensure(RSTATUS, "R1026", BLOCKER)
    ensure(RVERDICT, "第 1026 轮", VERDICT)
    ensure(BACKLOG, "R1026", BACKLOG_ADD)

    note = (
        "\n## R1026 补充 — **`-99` 不是 0（正则非法）；两层文案结构；加 `How` 列（RemoteApi 只有两家）**（套件 2241）\n\n"
        "**判据缺陷**：`ida.py str` 收**正则** ⇒ `\"Cloudflare Failed (\"` 未转义 `(` ⇒ 查询抛错 ⇒ 哨兵 **`-99`**。\n"
        "**六行 `-99` 不是「0 命中」。** 修法 `re.escape()`；转义后六行全 `n=0`。\n"
        "→ **R1015/R1016 那条第三次：一个「0」可以是假的，「-99」更坏 —— 它连查询都没跑成。**\n\n"
        "**两层结构**：检测层 `<Vendor> Failed/Blocked/block/(Rotating)` · 求解层 `Solving <Vendor> (...)` /\n"
        "`Failed Solving <Vendor> (...)`（带原因 no clearance · too many rounds · TL · SBSD · SDS · Softblock）。\n\n"
        "**而 `API down (Contact staff)` 只有 kasada 与 akamai** ⇒ 那两家**经远端服务解**，其余四家**本地解**\n"
        "（本地例程不会「挂」，它只是失败）。\n\n"
        "**加第 8 列 `How { None, Local, RemoteApi, Unknown }`**：kasada/akamai = `RemoteApi` ·\n"
        "cloudflare/datadome/perimeterx/queue-it = `Local` · imperva = `None` · `Unknown` 无使用者（留将来）。\n"
        "**4 条守卫**（`VendorSolvingModeTests`）。\n\n"
        "**而「行序不是字母序」我第三次撞上**（R1009 · R1024 · 本轮）—— 这次写进了断言旁的注释。\n\n"
        "数字：套件 2241（+4）· 陈旧度 4 / 3,859 · 函数数 174,336 · Row 列 7 → **8** · RemoteApi **2**。\n\n"
        "纪律：**读到任何非正数，先问「这个查询跑成了吗」。**\n\n"
        "下一轮：kasada/akamai 的远端服务是哪个（`API down` 说明是第三方 solver，找它的 host）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1026" not in h:
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
             for p, k in ((RBLOCK, "R1026"), (RSTATUS, "R1026"), (RVERDICT, "第 1026 轮"), (BACKLOG, "R1026")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1026: minus ninety-nine is not zero, and escaping it exposes two layers\n\n"
         "R1025's lesson was to read the lines that do not answer my question. So this round asked all seven vendors for\n"
         " their outcome vocabulary, and six probes came back -99.\n\n"
         "That sentinel means the query threw, not that the string is absent. ida.py str takes a regular expression, and\n"
         "\"Cloudflare Failed (\" carries an unescaped parenthesis, so the pattern would not compile. I nearly read those six\n"
         " rows as absences. Escaping them turns all six into a clean zero, and it is the third instalment of R1015's\n"
         " lesson -- a zero can be false -- with a worse variant: a failed query never asks the question at all, and both\n"
         " look equally quiet in the output.\n\n"
         "Escaping also exposes something the audit did not have. The image's failure lines come in two layers: the\n"
         " detection layer says Failed, Blocked, block or Rotating, and the solving layer says Solving X (...) or\n"
         " Failed Solving X (...) with a reason -- no clearance, too many rounds, TL, SBSD, SDS, Softblock. Reading both\n"
         " gives a third fact: only Kasada and Akamai carry API down (Contact staff). An API can be down; a local routine\n"
         " cannot be, it just fails. So those two are solved through a service and the other four in-process.\n\n"
         "That becomes an eighth column, How, with None, Local, RemoteApi and Unknown. Unknown has no users yet and is\n"
         "there so a future row can say it does not know rather than guess.\n\n"
         "Four guards pin the split, and writing them caught me ordering the expected list alphabetically for the third\n"
         " time in this repository. The note beside the assertion now says so, because fixing it silently twice already\n"
         " did not stop the third.\n\n"
         "Figures: suite 2237 to 2241, freshness four files and 3,859 lines, count 174,336, Row at eight columns, two\n"
         " vendors solved remotely, and six probes that had been failing quietly are now real zeros.\n\n"
         "Unknown: which remote service Kasada and Akamai are solved through.\n\n"
         "The lesson is that a non-positive number deserves the question \"did this query run\" before \"what is the\n"
         " value\", and that both a false zero and a failed query present as silence.\n\n"
         "One source file and one test file changed; suite green at 2241."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()