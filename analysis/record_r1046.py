"""Record R1046: priority three's vocabulary, with controls."""

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
### ③ 的词汇分成**有据的**与**自造的**，而那区分可算（R1046）

**R1045 说下一轮换到 ② 或 ③。换到 ③，而第一件事是 `where_is BrowserIdentity` —— 它有实现、21 处测试引用、
两个相关测试。所以 ③ 不缺骨架。缺的是一个**可算的**问题，而它很具体。**

### ① 而 `BrowserIdentity` 写的是三个**内部变量名**，不是指纹字段

```
browser.fingerprintKey · browser.timezoneOffsetMinutes · browser.fingerprintPayload
payload: fingerprint-v1 / fingerprint-v1-sans-ua
```

**→ 那五个名字是**本工作的词汇**（R133/R134 定的）。而它们分两类，而那件事可查 ——
因为 R1045 只证明镜像没有**符号**，没证明没有**字符串数据**。**

### ② 而对照成立，所以零值可信

```
kpsdk      17   ← 对照：Kasada 的 cookie 前缀
datadome   15   ← 对照：DataDome 的 host
```

**→ 同一次运行里两个已知串都大于零 ⇒ 下表里的零可以读成「镜像里没有」。**

### ③ 而结果分成三样

| 类别 | 名字 | 命中 | 地址 | 判定 |
|---|---|---|---|---|
| payload | `fingerprint-v1` | **2** | `0x147034eac` | **有据** |
| payload | `fingerprint-v1-sans-ua` | **2** | `0x147034ee4` | **有据** |
| session key | `browser.fingerprintKey` | **0** | — | **镜像里没有** |
| session key | `browser.fingerprintPayload` | **0** | — | **镜像里没有** |
| session key | `browser.timezoneOffsetMinutes` | **21** | — | **概念有据**（`TimezoneOffset` · `ParseTimeZoneOffset`） |

**→ 所以：**
1. **payload 名**有据** —— 镜像里两条实名，含 `-sans-ua` 变体 ⇒ `FingerprintLayers.PayloadFor` 的分支名**不是猜的**。
2. **时区概念**有据** —— 21 条，含属性与解析函数。
3. **两个 session 变量名是自造的** —— 而**那不矛盾**：session 变量是本工作**内部**的传值约定，
原版用别的方式把同一件事带到支付层。所以它们**不需要**有据，而它们**必须**与携带的值一致。**

**→ 而第 3 条是 (d) 的形态：一个名字**没有** authority 时，要说清**为什么它不需要**。

### ④ 而它是**生成物**

`replica/tools/fingerprint_vocab.py` → `docs/FINGERPRINT_VOCAB.md`（2,059 字节）。
→ 它每次运行都**重新探**那七个串（两个对照 + 五个名字），所以表不会腐化。
→ 而它把「对照是否成立」写在**第一节** —— 因为若对照不成立，下面的零就不可读，而那张表整张作废。**

### ⑤ 数字

| 度量 | R1045 | **R1046** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（未改业务代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **`BrowserIdentity` 实现文件** | 未查 | **1（95 行）** |
| **它的测试引用** | 未查 | **21（+ 两个相关测试文件）** |
| **payload 字面量在镜像里** | 未查 | **2 条实名** |
| **时区概念命中** | 未查 | **21** |
| **自造的 session key** | 未查 | **2** |
| **对照是否成立** | — | **是（17 / 15）** |
| **`docs/FINGERPRINT_VOCAB.md`** | 不存在 | **2,059 字节（生成）** |

### 教训

> **换到 ③ 之后第一件事不是写代码，是**问哪个说法有据**。
> → 而答案把 ③ 分成两半：**从镜像来的**（payload 名 · 时区）与**本地约定**（两个 session 变量）。
> **→ 而那个区分让「为什么这个名字没有 authority」有了答案 —— 它有，只是不需要。
> → 而那与「查不到所以编一个」是完全不同的两件事，而**只有把对照做出来才能分清**。****
"""

if "③ 的词汇分成**有据的**与**自造的**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1046 轮：③ 的词汇分成有据的与自造的

### ① `BrowserIdentity` 写的是三个内部变量名

```
browser.fingerprintKey · browser.timezoneOffsetMinutes · browser.fingerprintPayload
payload: fingerprint-v1 / fingerprint-v1-sans-ua
```

**→ 五个名字分两类，而那可查 —— R1045 只证明镜像没有**符号**，没证明没有**字符串数据**。**

### ② 而对照成立，所以零值可信

```
kpsdk 17 · datadome 15   ← 同一次运行，两个已知串都 > 0
```

### ③ 而结果分成三样

| 类别 | 名字 | 命中 | 地址 | 判定 |
|---|---|---|---|---|
| payload | `fingerprint-v1` | **2** | `0x147034eac` | **有据** |
| payload | `fingerprint-v1-sans-ua` | **2** | `0x147034ee4` | **有据** |
| session key | `browser.fingerprintKey` | **0** | — | **镜像里没有** |
| session key | `browser.fingerprintPayload` | **0** | — | **镜像里没有** |
| session key | `browser.timezoneOffsetMinutes` | **21** | — | **概念有据** |

**→ payload 名**有据**（含 `-sans-ua`）⇒ 分支名**不是猜的**。
→ 时区概念**有据**（`TimezoneOffset` · `ParseTimeZoneOffset`）。
→ 两个 session 变量名**自造** —— 而**那不矛盾**：它们是本工作**内部**的传值约定，
原版用别的方式把同一件事带到支付层 ⇒ **不需要**有据，但**必须**与值一致。**

### ④ 而它是生成物

`replica/tools/fingerprint_vocab.py` → `docs/FINGERPRINT_VOCAB.md`（2,059 字节）。
**→ 每次运行重新探七个串；「对照是否成立」写在**第一节** —— 对照不成立则整张表作废。**

### ⑤ 数字

| 度量 | R1045 | **R1046** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **`BrowserIdentity` 实现** | 未查 | **1（95 行）+ 21 处测试引用** |
| **payload 字面量有据** | 未查 | **2 条实名** |
| **时区概念命中** | 未查 | **21** |
| **自造 session key** | 未查 | **2** |
| **对照** | — | **成立（17 / 15）** |
| **`FINGERPRINT_VOCAB.md`** | 不存在 | **2,059 字节** |

### 教训

> **换到 ③ 后第一件事不是写代码，是**问哪个说法有据**。
> → 答案把 ③ 分成**从镜像来的**与**本地约定**两半。**
> **→ 那个区分让「为什么这个名字没有 authority」有了答案 —— 它有，只是不需要。
> → 而那与「查不到所以编一个」完全不同，只有把对照做出来才能分清。**
"""

BACKLOG_ADD = """

## 判据 (d) — **③ 词汇：payload 名与时区有据，两个 session key 是本地约定**（R1046）

### 对照成立

```
kpsdk 17 · datadome 15      ⇒ 下面的 0 可读成「镜像里没有」
```

### 逐名

| 类别 | 名字 | 命中 | 地址 | 判定 |
|---|---|---|---|---|
| payload | `fingerprint-v1` | **2** | `0x147034eac` | **有据** |
| payload | `fingerprint-v1-sans-ua` | **2** | `0x147034ee4` | **有据** |
| key | `browser.fingerprintKey` | **0** | — | **自造（无需有据）** |
| key | `browser.fingerprintPayload` | **0** | — | **自造（无需有据）** |
| key | `browser.timezoneOffsetMinutes` | **21** | — | **概念有据** |

**⇒ session 变量是本工作内部约定；原版用别的方式把同一件事带到支付层。**

### 生成物

**`replica/tools/fingerprint_vocab.py` → `docs/FINGERPRINT_VOCAB.md`（2,059 字节），
对照写在第一节。**

### 数字

**套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · 实现 95 行/21 测试引用 · payload 2 有据 · 时区 21 · 自造 key 2 · 对照 17/15**

| 仍 Unknown | |
|---|---|
| 两个 session key 对应的原版传值方式 | 待查（若需要） |
| Nike 二选一 / Farfetch transport | 不可得（R1045） |

**纪律**：名字没有 authority 时，要说清**为什么它不需要**，而不只是「查不到」。
"""

BLOCKER = """

---

## 470. **③ 的词汇分成有据的与自造的 —— 而那区分可算**

> R1046。**加 1 个生成器 + 1 个生成文档（未改业务代码）。** 套件 **2258 通过 / 0 失败 / 0 跳过**。

### 一、而 `BrowserIdentity` 写的是三个**内部变量名**

```
browser.fingerprintKey · browser.timezoneOffsetMinutes · browser.fingerprintPayload
payload: fingerprint-v1 / fingerprint-v1-sans-ua
```

**→ 那五个名字是**本工作的词汇**（R133/R134 定的）。而它们分两类，而那件事可查 ——
  因为 R1045 只证明镜像没有**符号**，没证明没有**字符串数据**。**

### 二、而对照成立，所以零值可信

```
kpsdk      17   ← 对照：Kasada 的 cookie 前缀
datadome   15   ← 对照：DataDome 的 host
```

**→ 同一次运行里两个已知串都大于零 ⇒ 下表里的零可以读成「镜像里没有」。**

### 三、而结果分成三样

| 类别 | 名字 | 命中 | 地址 | 判定 |
|---|---|---|---|---|
| payload | `fingerprint-v1` | **2** | `0x147034eac` | **有据** |
| payload | `fingerprint-v1-sans-ua` | **2** | `0x147034ee4` | **有据** |
| session key | `browser.fingerprintKey` | **0** | — | **镜像里没有** |
| session key | `browser.fingerprintPayload` | **0** | — | **镜像里没有** |
| session key | `browser.timezoneOffsetMinutes` | **21** | — | **概念有据**（`TimezoneOffset` · `ParseTimeZoneOffset`） |

**→ 所以：**
1. **payload 名**有据** —— 镜像里两条实名，含 `-sans-ua` 变体 ⇒ `FingerprintLayers.PayloadFor` 的分支名**不是猜的**。
2. **时区概念**有据** —— 21 条，含属性与解析函数。
3. **两个 session 变量名是自造的** —— 而**那不矛盾**：session 变量是本工作**内部**的传值约定，
   原版用别的方式把同一件事带到支付层。所以它们**不需要**有据，而它们**必须**与携带的值一致。**

**→ 而第 3 条是 (d) 的形态：一个名字**没有** authority 时，要说清**为什么它不需要**。**

### 四、而它是**生成物**

`replica/tools/fingerprint_vocab.py` → `docs/FINGERPRINT_VOCAB.md`（2,059 字节）。
→ 它每次运行都**重新探**那七个串（两个对照 + 五个名字），所以表不会腐化。
→ 而它把「对照是否成立」写在**第一节** —— 因为若对照不成立，下面的零就不可读，而那张表整张作废。**

### 五、数字

| 度量 | R1045 | R1046 |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（未改业务代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **`BrowserIdentity` 实现文件** | 未查 | **1（95 行）** |
| **它的测试引用** | 未查 | **21（+ 两个相关测试文件）** |
| **payload 字面量在镜像里** | 未查 | **2 条实名** |
| **时区概念命中** | 未查 | **21** |
| **自造的 session key** | 未查 | **2** |
| **对照是否成立** | — | **是（17 / 15）** |
| **`docs/FINGERPRINT_VOCAB.md`** | 不存在 | **2,059 字节（生成）** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "fingerprint-v1" --limit 600   -> {"n":2}（0x147034eac · 0x147034ee4）
python analysis/ida.py str "fingerprintKey" --limit 600   -> {"n":0}
python analysis/ida.py str "timezoneOffset" --limit 600   -> {"n":21}
python analysis/ida.py str "kpsdk" --limit 600            -> {"n":17}（对照）
cd replica
python tools/fingerprint_vocab.py  -> wrote docs/FINGERPRINT_VOCAB.md（2,059 字节）· controls ok=True
python tools/metrics_report.py     -> 完整套件 exit 0  2258 / 0 / 0 · 陈旧度 0 / 0
```

### 七、仍然 Unknown

- **两个 session key 对应的原版传值方式**：待查（若需要）。
- **Nike 二选一 / Farfetch transport**：**不可得**（R1045 已排除四条路）。

### 八、教训

**换到 ③ 之后第一件事不是写代码，是**问哪个说法有据**。**

**→ 而答案把 ③ 分成两半：**从镜像来的**（payload 名 · 时区）与**本地约定**（两个 session 变量）。**

**→ 而那个区分让「为什么这个名字没有 authority」有了答案 —— 它有，只是不需要。
→ 而那与「查不到所以编一个」是完全不同的两件事，而**只有把对照做出来才能分清**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1046", BLOCKER)
    ensure(RSTATUS, "R1046", BLOCKER)
    ensure(RVERDICT, "第 1046 轮", VERDICT)
    ensure(BACKLOG, "R1046", BACKLOG_ADD)

    note = (
        "\n## R1046 补充 — **③ 词汇：payload 名与时区有据，两个 session key 是本地约定**（套件 2258）\n\n"
        "**对照成立**：`kpsdk` 17 · `datadome` 15 ⇒ 下面的 0 可读成「镜像里没有」。\n\n"
        "| 类别 | 名字 | 命中 | 判定 |\n|---|---|---|---|\n"
        "| payload | `fingerprint-v1` | **2**（`0x147034eac`） | **有据** |\n"
        "| payload | `fingerprint-v1-sans-ua` | **2**（`0x147034ee4`） | **有据** |\n"
        "| key | `browser.fingerprintKey` | **0** | **自造（无需有据）** |\n"
        "| key | `browser.fingerprintPayload` | **0** | **自造（无需有据）** |\n"
        "| key | `browser.timezoneOffsetMinutes` | **21** | **概念有据** |\n\n"
        "**⇒ payload 名有据（含 `-sans-ua`）⇒ `FingerprintLayers.PayloadFor` 的分支名不是猜的。\n"
        "⇒ session 变量是本工作内部约定；原版用别的方式把同一件事带到支付层。**\n\n"
        "**生成物**：`replica/tools/fingerprint_vocab.py` → `docs/FINGERPRINT_VOCAB.md`（2,059 字节），\n"
        "**对照写在第一节** —— 对照不成立则整张表作废。\n\n"
        "数字：套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · 实现 95 行/21 测试引用 · payload 2 有据 ·\n"
        "时区 21 · 自造 key 2 · 对照 17/15。\n\n"
        "纪律：**名字没有 authority 时，要说清为什么它不需要，而不只是「查不到」。**\n\n"
        "下一轮：② 风控 —— `Solving Akamai (SBSD)/(SDS)` 与 queue-it softblock 的求解协议（带对照查文案族）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1046" not in h:
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
             for p, k in ((RBLOCK, "R1046"), (RSTATUS, "R1046"), (RVERDICT, "第 1046 轮"), (BACKLOG, "R1046")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1046: priority three's vocabulary divides into evidenced names and local conventions\n\n"
         "R1045 closed priority one by establishing that the artifact has no business symbols, so this round moved to\n"
         " priority three, where the work is computable. where_is showed BrowserIdentity already has an implementation,\n"
         " ninety-five lines, and twenty-one test references -- so the gap was not a missing skeleton but a missing\n"
         " question. It writes three session variables and two payload literals, and whether the original shares that\n"
         " vocabulary is answerable, because R1045 only proved the pool has no symbols, not that it has no strings.\n\n"
         "Two controls in the same run establish that a zero here is readable: kpsdk returns seventeen and datadome\n"
         " fifteen. Against that, fingerprint-v1 returns two hits -- 0x147034eac and the -sans-ua variant at\n"
         " 0x147034ee4 -- so the payload branch names are not guessed. timezoneOffset returns twenty-one, including a\n"
         " property and a parser. The two session key names return nothing.\n\n"
         "That last result is not a defect. Session variables are this workspace's internal convention from R133 and\n"
         " R134; the original carries the same facts to the payment layer some other way. Those names do not need\n"
         " authority, and they do need to agree with the values they carry, and the values do have authority. Which is\n"
         " the useful shape for this kind of table: a name without evidence has to say why it does not need any, not\n"
         " merely that none was found. Those are very different statements and only a control distinguishes them.\n\n"
         "The table is generated by tools/fingerprint_vocab.py and reads the seven strings fresh each run, with the\n"
         " control result in its first section, because if the control fails the zeros beneath it are unreadable and the\n"
         " whole table is void.\n\n"
         "Figures: suite 2258 unchanged, freshness zero, count 174,293, two payload literals evidenced, twenty-one\n"
         " timezone hits, two self-coined key names, and controls at seventeen and fifteen.\n\n"
         "Unknown: how the original carries those two values, if that ever matters.\n\n"
         "The lesson is that arriving at a new priority, the first thing to ask is which of its claims have evidence --\n"
         " and that the answer split it in half, with the half that has none turning out not to need any.\n\n"
         "One generator and one generated document added; suite green at 2258."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()