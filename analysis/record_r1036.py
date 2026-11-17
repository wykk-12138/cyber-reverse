"""Record R1036: the image has no farfetch.com, so the flow stops pretending."""

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
### 镜像里**没有 farfetch.com** —— 所以那个 flow 停止假装（R1036）

**R1035 说下一轮判那 6 条 `sent` 该继续发还是改报告。判了，而取证把问题换成了另一个。**

### ① 取证：不是端点无据，是**整个站在镜像里不存在**

```
ff-products          0
/api/basket          0
checkout/v1/basket   0
api/farfetch.com     0
farfetch.com         0      ← 连域名都不在
basketId             5      但都是别的站的字段名
place-order          3      都是别的站（payments/place-order 等）
/api/checkout        1      是 on.com 的
```

**→ `farfetch.com` **零次**。所以 `FarfetchFlow` 的域名、7 个端点、整条结账链**全部无据**。

**→ 那与 Nike 的情况不同：Nike 是**两个步骤**的端点缺据，而 Farfetch 是**整个站**缺据。**
→ 所以「改成报告」这个动作对 Nike 是补丁，对 Farfetch 是**停止假装**。**

### ② 改了什么

**7 个公开步骤全部不再发请求：**

```csharp
return StepOutcome.Fail("farfetch: <step> endpoint unknown -- the image carries no farfetch.com, so there is nothing to call");
```

**→ 类头写明：探域、探 API host、探 product/basket/checkout 前缀，**每一个都是零**。
→ 而去留（这个 flow 该不该存在）留给 YG —— 代码不再假装它能下单。**

### ③ 而两份台账同步

| 台账 | 动作 |
|---|---|
| 棘轮 `Sent` + `DocumentedOnly` | 移出 **7 行** Farfetch 条目 |
| 工具台账 `sent` 段 | 移出 **3 条** Farfetch 的 |

**→ 而 `SentCeiling` 没动（16），因为移出的是条目不是上限。**

### ④ 而 `Counts` 那两个守卫要**改数字而不是回滚**

| 守卫 | 要什么 | 处置 |
|---|---|---|
| `AFlowWithPlaceholdersSaysWhy` | 占位 ≥2 的 flow 正文里要有 `endpoint unknown` | **把 7 条消息改成含这个短语** —— 那本来也是更好的话（说的是缺什么，不是店是什么） |
| `MostOverridesDoWork` | `placeholders <= KnownPlaceholders` | **5 → 12**，并在常量旁写明理由 |

**→ 而那与 R1031 那次不同：那次我**回滚**了，因为改动没据。
→ 这次**有据**（`farfetch.com` 为 0），所以数字**跟着证据走**，而不是让证据迁就数字。**

### ⑤ 而这一轮我又踩了同一个坑两次

**① 类头注释里我写了 `"/api/basket"` 和 `"checkout/v1/basket"` —— 而扫描器把**注释里的路径也算成端点**，
→ 于是 `unknown` 从 0 变 1，而它指的是**我自己写的说明文字**。
→ 改成不引字面量的措辞（「product prefix」「basket and checkout prefixes」）。**

**② 而那是 R1033 我写的报告消息同族：散文里提到路径，工具分不清注释与代码。**
**→ 两次都是**我的文字成了被测对象**。**

### ⑥ 数字

| 度量 | R1035 | **R1036** |
|---|---|---|
| 套件 | 2252 / 0 | **2252 / 0 / 0** |
| 产物陈旧度 | 6 / 5,786 | **6 / 5,669** |
| 函数数 | 174,336 | **174,336** |
| **inline 端点字面量** | 331 | **323（−7 个 Farfetch，−1 注释）** |
| **`not in pool`** | 41 | **33** |
| **端点门 `unknown`** | 0 | **0** |
| **`KnownPlaceholders`** | 5 | **12** |
| **Farfetch 会发的请求** | **7** | **0** |
| **`farfetch.com` 在镜像里** | 未查 | **0（决定性）** |

### 教训

> **R1031 我为同一批端点改过报告，而当时**没有取证**，被守卫拦住只好回滚。
> → 这一轮取证了五分钟，答案（`farfetch.com` 为 0）比任何论证都硬 ——
> 而那五分钟正是上一轮缺的那一步。**
> **→ 所以「守住不动」和「动手」之间没有原则之争：缺一次取证。**
"""

if "镜像里**没有 farfetch.com**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1036 轮：镜像里没有 `farfetch.com` —— 那个 flow 停止假装

### ① 取证：不是端点无据，是**整个站**不在镜像里

```
ff-products 0 · /api/basket 0 · checkout/v1/basket 0
api.farfetch.com 0 · **farfetch.com 0**
```

**→ `FarfetchFlow` 的域名、7 个端点、整条结账链**全部无据**。
→ 与 Nike 不同：Nike 是**两个步骤**缺据，Farfetch 是**整个站**缺据 ⇒
「改成报告」对 Nike 是补丁，对 Farfetch 是**停止假装**。**

### ② 改了什么

**7 个公开步骤全部不再发请求：**
`"farfetch: <step> endpoint unknown -- the image carries no farfetch.com, so there is nothing to call"`

**→ 类头写明四个探针每一个都是零。**去留留给 YG —— 代码不再假装它能下单。**

### ③ 而两份台账同步

**棘轮移出 7 行 · 工具台账移出 3 条。`SentCeiling` 没动（16）—— 移出的是条目不是上限。**

### ④ 那两条守卫要**改数字而不是回滚**

| 守卫 | 处置 |
|---|---|
| `AFlowWithPlaceholdersSaysWhy` | 7 条消息改成含 `endpoint unknown`（那本来也是更好的话） |
| `MostOverridesDoWork` | `KnownPlaceholders` **5 → 12**，常量旁写理由 |

**→ 与 R1031 不同：那次**没据**所以回滚；这次**有据**所以数字跟着证据走。**

### ⑤ 而我又踩了同一个坑

**① 类头注释里写了 `"/api/basket"` —— 扫描器把**注释里的路径也算端点** ⇒ `unknown` 0 → 1，
而它指的是**我自己写的说明文字**。改成不引字面量的措辞。**
**② 与 R1033 我写的报告消息同族：散文里提到路径，工具分不清注释与代码。
→ 两次都是**我的文字成了被测对象**。**

### ⑥ 数字

| 度量 | R1035 | **R1036** |
|---|---|---|
| 套件 | 2252 / 0 | **2252 / 0 / 0** |
| 产物陈旧度 | 6 / 5,786 | **6 / 5,669** |
| 函数数 | 174,336 | **174,336** |
| **inline 字面量** | 331 | **323** |
| **`not in pool`** | 41 | **33** |
| **端点门 `unknown`** | 0 | **0** |
| **`KnownPlaceholders`** | 5 | **12** |
| **Farfetch 会发的请求** | **7** | **0** |
| **`farfetch.com` 在镜像里** | 未查 | **0（决定性）** |

### 教训

> **R1031 我为同一批端点改过报告，而当时**没有取证**，被守卫拦住只好回滚。
> → 这一轮取证五分钟，答案（`farfetch.com` 为 0）比任何论证都硬 —— 而那五分钟正是上一轮缺的那一步。**
> **→ 「守住不动」和「动手」之间没有原则之争：缺一次取证。**
"""

BACKLOG_ADD = """

## 判据 (f) — **镜像里没有 `farfetch.com`；Farfetch 7 个步骤停止发请求**（R1036）

### 取证

```
ff-products 0 · /api/basket 0 · checkout/v1/basket 0 · api.farfetch.com 0 · **farfetch.com 0**
basketId 5（别的站）· place-order 3（别的站）· /api/checkout 1（on.com）
```

**→ 整个站不在镜像里 ⇒ 域名、7 端点、结账链全部无据。
→ 与 Nike 的差别：Nike 两步缺据（补丁），Farfetch 整站缺据（停止假装）。**

### 改动

**7 步骤 → `Fail("farfetch: <step> endpoint unknown -- ...")`；类头列四个零探针。**
**两份台账同步（棘轮 −7 行 · 工具台账 −3 条）；`SentCeiling` 16 不变。**

### 守卫

`AFlowWithPlaceholdersSaysWhy` → 消息含 `endpoint unknown` ·
`MostOverridesDoWork` → **`KnownPlaceholders` 5 → 12**（有据，故改数不回滚）

### 而我又踩了同一个坑

**类头注释里写了 `"/api/basket"` ⇒ 扫描器把注释里的路径也算端点，`unknown` 0 → 1。
→ 与 R1033 同族：**我的文字成了被测对象**。**

### 数字

**套件 2252/0/0 · 陈旧度 6 / 5,669 · 函数数 174,336 · inline 331 → 323 · not-in-pool 41 → 33 ·
unknown 0 · KnownPlaceholders 5 → 12 · Farfetch 会发请求 7 → 0**

| 仍 Unknown / 待 YG | |
|---|---|
| `FarfetchFlow` 该不该存在（多余 vs 未覆盖） | **待 YG 裁决** |
| 产物需重新 publish（6 文件陈旧） | 待收尾 |

**纪律**：「守住不动」与「动手」之间没有原则之争：缺一次取证。
"""

BLOCKER = """

---

## 460. **镜像里没有 `farfetch.com`；Farfetch 的 7 个步骤停止发请求**

> R1036。**改 1 个 flow + 2 个测试 + 2 份台账。** 套件 **2252 通过 / 0 失败 / 0 跳过**。
> **端点门 `unknown` 0 · exit 0。**

### 一、取证：不是端点无据，是**整个站在镜像里不存在**

```
ff-products          0        api/farfetch.com     0
/api/basket          0        farfetch.com         0      ← 连域名都不在
checkout/v1/basket   0
basketId             5        但都是别的站的字段名
place-order          3        都是别的站
/api/checkout        1        是 on.com 的
```

**→ `farfetch.com` **零次**。所以 `FarfetchFlow` 的域名、7 个端点、整条结账链**全部无据**。

**→ 那与 Nike 的情况不同：Nike 是**两个步骤**的端点缺据，而 Farfetch 是**整个站**缺据。
→ 所以「改成报告」对 Nike 是补丁，对 Farfetch 是**停止假装**。**

### 二、改了什么

**7 个公开步骤全部不再发请求：**

```csharp
return StepOutcome.Fail("farfetch: <step> endpoint unknown -- the image carries no farfetch.com, so there is nothing to call");
```

**→ 类头写明：探域、探 API host、探 product/basket/checkout 前缀，**每一个都是零**。
→ 而去留（这个 flow 该不该存在）留给 YG —— 代码不再假装它能下单。**

### 三、而两份台账同步

| 台账 | 动作 |
|---|---|
| 棘轮 `Sent` + `DocumentedOnly` | 移出 **7 行** Farfetch 条目 |
| 工具台账 `sent` 段 | 移出 **3 条** Farfetch 的 |

**→ 而 `SentCeiling` 没动（16），因为移出的是条目不是上限。**

### 四、而 `Counts` 那两个守卫要**改数字而不是回滚**

| 守卫 | 要什么 | 处置 |
|---|---|---|
| `AFlowWithPlaceholdersSaysWhy` | 占位 ≥2 的 flow 正文里要有 `endpoint unknown` | **把 7 条消息改成含这个短语** |
| `MostOverridesDoWork` | `placeholders <= KnownPlaceholders` | **5 → 12**，常量旁写明理由 |

**→ 与 R1031 那次不同：那次我**回滚**了，因为改动没据。
→ 这次**有据**（`farfetch.com` 为 0），所以数字**跟着证据走**。**

### 五、而这一轮我又踩了同一个坑

**类头注释里我写了 `"/api/basket"` 和 `"checkout/v1/basket"` —— 而扫描器把**注释里的路径也算成端点**，
→ 于是 `unknown` 从 0 变 1，而它指的是**我自己写的说明文字**。
→ 改成不引字面量的措辞（「product prefix」「basket and checkout prefixes」）。**

**→ 那是 R1033 我写的报告消息同族：散文里提到路径，工具分不清注释与代码。
→ 两次都是**我的文字成了被测对象**。**

### 六、数字

| 度量 | R1035 | R1036 |
|---|---|---|
| 套件 | 2252 / 0 | **2252 / 0 / 0** |
| 产物陈旧度 | 6 / 5,786 | **6 / 5,669** |
| 函数数 | 174,336 | **174,336** |
| **inline 端点字面量** | 331 | **323** |
| **`not in pool`** | 41 | **33** |
| **端点门 `unknown`** | 0 | **0** |
| **`KnownPlaceholders`** | 5 | **12** |
| **Farfetch 会发的请求** | **7** | **0** |
| **`farfetch.com` 在镜像里** | 未查 | **0（决定性）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "farfetch\\.com"     -> {"n":0}
python analysis/ida.py str "ff-products"        -> {"n":0}
cd replica
python tools/endpoint-provenance.py             -> unknown 0 · exit 0
python tools/metrics_report.py -> 完整套件 exit 0  2252 / 0 / 0
```

### 八、仍然 Unknown / 待 YG

- **`FarfetchFlow` 该不该存在**：**待 YG 裁决**（不是未覆盖，是多余）。
- **产物需重新 publish**（6 文件陈旧）：待收尾。

### 九、教训

**R1031 我为同一批端点改过报告，而当时**没有取证**，被守卫拦住只好回滚。**

**→ 这一轮取证了五分钟，答案（`farfetch.com` 为 0）比任何论证都硬 ——
  而那五分钟正是上一轮缺的那一步。**

**→ 所以「守住不动」和「动手」之间没有原则之争：缺一次取证。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1036", BLOCKER)
    ensure(RSTATUS, "R1036", BLOCKER)
    ensure(RVERDICT, "第 1036 轮", VERDICT)
    ensure(BACKLOG, "R1036", BACKLOG_ADD)

    note = (
        "\n## R1036 补充 — **镜像里没有 `farfetch.com`；Farfetch 7 个步骤停止发请求**（套件 2252）\n\n"
        "**取证**：`farfetch.com` **0** · `api.farfetch.com` 0 · `ff-products` 0 · `/api/basket` 0 · `checkout/v1/basket` 0。\n"
        "→ **整个站不在镜像里** ⇒ 域名、7 端点、结账链全部无据。\n"
        "→ 与 Nike 不同：Nike 两步缺据（补丁），Farfetch 整站缺据（**停止假装**）。\n\n"
        "**改动**：7 步骤 → `Fail(\"farfetch: <step> endpoint unknown -- ...\")`；类头列四个零探针。\n"
        "两份台账同步（棘轮 −7 行 · 工具台账 −3 条）；`SentCeiling` 16 不变。\n\n"
        "**两条守卫改数不回滚**：`AFlowWithPlaceholdersSaysWhy`（消息含 `endpoint unknown`）·\n"
        "`MostOverridesDoWork`（**`KnownPlaceholders` 5 → 12**）。\n"
        "→ 与 R1031 不同：那次没据所以回滚；这次有据所以**数字跟着证据走**。\n\n"
        "**而我又踩了同一个坑**：类头注释里写了 `\"/api/basket\"` ⇒ 扫描器把**注释里的路径也算端点**，\n"
        "`unknown` 0 → 1 —— 指的是我自己的说明文字。改成不引字面量的措辞。\n"
        "→ 与 R1033 同族：**我的文字成了被测对象。**\n\n"
        "数字：套件 2252/0/0 · 陈旧度 6 / 5,669 · 函数数 174,336 · inline **331 → 323** ·\n"
        "not-in-pool **41 → 33** · unknown **0** · KnownPlaceholders **5 → 12** · Farfetch 会发请求 **7 → 0**。\n\n"
        "纪律：**「守住不动」与「动手」之间没有原则之争：缺一次取证。**\n\n"
        "**待 YG**：`FarfetchFlow` 该不该存在（多余 vs 未覆盖）。下一轮：publish 让陈旧度归零，或继续 ①。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1036" not in h:
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
             for p, k in ((RBLOCK, "R1036"), (RSTATUS, "R1036"), (RVERDICT, "第 1036 轮"), (BACKLOG, "R1036")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1036: the image has no farfetch.com, so the flow stops pretending\n\n"
         "R1035 left a judgement to make: whether the six sent endpoints should keep being sent or become reports. The\n"
         " evidence answered a bigger question than the one asked.\n\n"
         "Probing the flow's domain returns zero. So do its API host, its product prefix, and its basket and checkout\n"
         " prefixes. farfetch.com does not appear in the artifact at any spelling, which means the host, all seven\n"
         " endpoints and the entire checkout chain were written without evidence of the store existing. Nike was two\n"
         " steps short of proof; this is a whole store short, so reporting those steps is not patching a gap, it is\n"
         " ending a pretence.\n\n"
         "All seven now return a failure naming the missing endpoint, and the class comment records the four probes that\n"
         " came back empty. Whether the flow should exist at all is the owner's call, and that is now written down rather\n"
         " than implied by dead code.\n\n"
         "Both ledgers lost their Farfetch entries; the ceiling stayed, because entries were removed and the limit was\n"
         " not raised. Two guards needed their numbers moved instead of being reverted -- the placeholder phrase and the\n"
         " ceiling of five, now twelve -- and that is the difference from R1031, where the same change had no evidence\n"
         " behind it and went back.\n\n"
         "I also made the same mistake twice inside this round. The class comment quoted two of the paths it was\n"
         " describing, and the scanner counts a path wherever it appears, so unknown went from zero to one on the\n"
         " strength of my own prose. R1033 was the same shape with a failure message. Twice now my writing has been the\n"
         " thing under test.\n\n"
         "Figures: suite 2252 unchanged, freshness six files and 5,669 lines, count 174,336, inline literals down from\n"
         " 331 to 323, not-in-pool from 41 to 33, the provenance gate still at zero, and Farfetch sending seven requests\n"
         " before this round and none after.\n\n"
         "Unknown: whether the flow should exist, which needs the owner, and a publish to clear freshness.\n\n"
         "The lesson is that five minutes of probing is what separated R1031's revert from this round's change, and that\n"
         " the difference between holding still and acting was never a matter of principle.\n\n"
         "One flow, two tests and two ledgers changed; suite green at 2252."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()