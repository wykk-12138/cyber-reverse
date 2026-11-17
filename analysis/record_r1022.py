"""Record R1022: PerimeterX is Imperva's mirror image, and the inventory entry is the second witness."""

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
### PerimeterX 是 Imperva 的**镜像情形**；而第二个证人在台账里（R1022）

**R1021 说下一轮做另一个 `Gap` 分支：perimeterx。做了，而它的证据结构与 imperva 正好相反。**

### ① 两个 `Gap` 的对照现在都有第二个证人

| | **imperva**（`VendorAbsent`） | **perimeterx**（`NoPageMarker`） |
|---|---|---|
| 第一个证人 | 六种拼写全 **0** | `px-captcha` **0**（而 cookie 名有 4 条） |
| **第二个证人** | **`AntiBotVendors.All` 不含它** | **`AntiBotVendors` 的 PerimeterX 条目有 4 条** |
| 含义 | 厂商**不在**产物里 | 厂商**在**，而没有页面级串 |

**→ 同一份台账，一个用于证明**缺席**，一个用于证明**在场但缺某类字面量**。
→ 两者都以「每条都带证据」为前提。**

### ② 而 PerimeterX 那四条，逐条都不是页面级串

```
new Vendor("PerimeterX", new[] { "PerimeterX", "PerimeterX-Token", "PerimeterXHandler", "_pxHandler" })
```

| 字面量 | 命中 | 性质 |
|---|---|---|
| `PerimeterX` | 5 | **复刻件自己的文案** —— `"PerimeterX block (Rotating proxy)"` 是 Cybersole **弹给用户**的，不是商店页面 |
| `PerimeterX-Token` | 1 | cookie / header 名 |
| `PerimeterXHandler` | 1 | **类名**（反射元数据，UTF-8） |
| `_pxHandler` | 1 | 字段 / 方法名 |

**→ 四条里**没有一条**会在一个商店的**响应体**里出现。**
**→ 那正是 `Gap.NoPageMarker` 的精确含义，而现在它有两个来源支持（查询 + 台账条目）。**

### ③ 而 `"PerimeterX block (Rotating proxy)"` 那条值得一提

**它是本次会话里**唯一**一条带厂商名的用户可见文案。而它说的是「换代理」——
**那说明原版遇到过 PerimeterX 的封禁，而它的应对是**换代理**，不是解挑战。**

**→ 那是一个**行为证据**：原版不解决 PerimeterX，它绕过。
→ 而 `State.DetectedOnly`（检测到但不处理）与那条文案**一致** —— 那是巧合，还是当初就这么定的？**
**→ 未查，标 Unknown。而它值得查：若原版真的只是换代理，那复刻件也不该给 perimeterx 写 solver。**

### ④ 4 条守卫

| 守卫 | 断言 |
|---|---|
| `TheInventoryEntryIsTheFourClassifiedLiterals` | 台账条目就是那四条 |
| **`NoneOfTheFourIsAPageLevelLiteral`** | 四条都不含 `px-captcha` / `captcha-delivery` / `/interstitial/` / `block` |
| `TheRowRecordsTheGapAsAMissingPageMarker` | `Gap` / `MarkerFrom` / `Marker` 三者一致 |
| `BothGapKindsHaveALiveExample` | 两种 `Gap` 各有一个活例子 |

**→ 第 2 条是这次分类的可执行形式：它断言那四条**不是**页面级串，
→ 而那正是「缺页面级 marker」这个论断的内容。**

### ⑤ 数字

| 度量 | R1021 | **R1022** |
|---|---|---|
| 套件 | 2229 / 0 | **2233 / 0 / 0（+4）** |
| 产物陈旧度 | 3 / 3,563 | **4 / 3,788** |
| 函数数 | 174,336 | **174,336** |
| **有第二个证人的 `Gap` 分支** | **1**（imperva） | **2**（+ perimeterx） |
| **PerimeterX 的页面级 marker** | 未知 | **确认无（4 条逐一分类）** |
| **`"PerimeterX block (Rotating proxy)"` 的含义** | 未注意 | **记为行为证据，待查** |

### 教训

> **同一份台账能做两件相反的事：证明一个厂商**不在**（看它没列谁），和证明一个厂商**在而缺某样东西**
> （看它列了什么）。第二种用法我上一轮没想到。**
> **→ 而第二种更少见：它需要把列出的条目**逐条分类**，而不是只数个数。
> → 而分类的结果正好是那个论断的内容。**
"""

if "PerimeterX 是 Imperva 的**镜像情形**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1022 轮：PerimeterX 是 Imperva 的镜像情形；而第二个证人在台账里

### ① 两个 `Gap` 的对照现在都有第二个证人

| | **imperva**（`VendorAbsent`） | **perimeterx**（`NoPageMarker`） |
|---|---|---|
| 第一个证人 | 六种拼写全 **0** | `px-captcha` **0**（cookie 名 4 条有） |
| **第二个证人** | **台账不含它** | **台账的 PerimeterX 条目有 4 条** |
| 含义 | 厂商**不在**产物里 | 厂商**在**，无页面级串 |

**→ 同一份台账，一个用于证明**缺席**，一个用于证明**在场但缺一类字面量**。两者都以「每条都带证据」为前提。**

### ② 而 PerimeterX 那四条，逐条都不是页面级串

| 字面量 | 命中 | 性质 |
|---|---|---|
| `PerimeterX` | 5 | **复刻件自己的文案** —— `"PerimeterX block (Rotating proxy)"` 是弹给用户的 |
| `PerimeterX-Token` | 1 | cookie / header 名 |
| `PerimeterXHandler` | 1 | **类名**（反射元数据） |
| `_pxHandler` | 1 | 字段 / 方法名 |

**→ 四条里没有一条会在商店的**响应体**里出现 ⇒ `Gap.NoPageMarker` 的精确含义，两源支持。**

### ③ 而那条文案是**行为证据**

**`"PerimeterX block (Rotating proxy)"` —— 它说的是「换代理」。
→ 说明原版遇到过 PerimeterX 封禁，而**它的应对是换代理，不是解挑战**。
→ 那与 `State.DetectedOnly`（检测到但不处理）一致 —— 巧合还是当初就这么定，**未查，标 Unknown**。
→ 而它值得查：若原版真的只换代理，复刻件也不该给 perimeterx 写 solver。**

### ④ 4 条守卫

`TheInventoryEntryIsTheFourClassifiedLiterals` · **`NoneOfTheFourIsAPageLevelLiteral`** ·
`TheRowRecordsTheGapAsAMissingPageMarker` · `BothGapKindsHaveALiveExample`

**→ 第 2 条是分类的可执行形式：它断言那四条**不是**页面级串，而那正是那个论断的内容。**

### ⑤ 数字

| 度量 | R1021 | **R1022** |
|---|---|---|
| 套件 | 2229 / 0 | **2233 / 0 / 0（+4）** |
| 产物陈旧度 | 3 / 3,563 | **4 / 3,788** |
| 函数数 | 174,336 | **174,336** |
| **有两个证人的 `Gap` 分支** | **1** | **2** |
| **PerimeterX 页面级 marker** | 未知 | **确认无（4 条逐一分类）** |
| **那条文案的含义** | 未注意 | **记为行为证据，待查** |

### 教训

> **同一份台账能做两件相反的事：看它**没列谁**证明缺席，看它**列了什么**证明在场而缺某样东西。
> 第二种用法我上一轮没想到。**
> **→ 而第二种更少见：它需要把列出的条目**逐条分类**，而不是只数个数。
> → 而分类的结果正好是那个论断的内容。**
"""

BACKLOG_ADD = """

## 优先级 ② — **PerimeterX 是 Imperva 的镜像情形；台账条目是第二个证人**（R1022）

### 两个 Gap 各有两个证人

| | imperva（`VendorAbsent`） | perimeterx（`NoPageMarker`） |
|---|---|---|
| 证据 1 | 六拼写全 **0** | `px-captcha` **0**（cookie 名 4 条有） |
| 证据 2 | **台账不含它** | **台账条目有 4 条** |

**→ 同一份台账：看它**没列谁**证明缺席；看它**列了什么**证明在场而缺一类字面量。**

### 四条逐条分类（无一是页面级串）

| 字面量 | 命中 | 性质 |
|---|---|---|
| `PerimeterX` | 5 | 复刻件自己的文案（`"PerimeterX block (Rotating proxy)"`） |
| `PerimeterX-Token` | 1 | cookie / header 名 |
| `PerimeterXHandler` | 1 | 类名（反射元数据） |
| `_pxHandler` | 1 | 字段 / 方法名 |

### 而那条文案是**行为证据**

**`"PerimeterX block (Rotating proxy)"` 说的是**换代理** ⇒ 原版遇到过 PerimeterX 封禁，
而应对是**绕过**不是**解挑战**。与 `State.DetectedOnly` 一致。**

**→ 待查：若原版真的只换代理，复刻件不该给 perimeterx 写 solver。**

### 4 条守卫

`TheInventoryEntryIsTheFourClassifiedLiterals` · **`NoneOfTheFourIsAPageLevelLiteral`** ·
`TheRowRecordsTheGapAsAMissingPageMarker` · `BothGapKindsHaveALiveExample`

### 数字

**套件 2233（+4）· 陈旧度 4 / 3,788 · 函数数 174,336 · 双证人 Gap 分支 1 → 2 · 页面级 marker 确认无**

| 仍 Unknown | |
|---|---|
| 那条文案是否就是原版对 PerimeterX 的**全部**处置 | 待查 |

**纪律**：同一个清单，数「缺谁」与分类「有什么」是两个不同的问题。
"""

BLOCKER = """

---

## 446. **PerimeterX 是 Imperva 的镜像情形；台账条目是第二个证人**

> R1022。**改 2 个源文件 + 加 1 个测试文件。** 套件 **2233 通过 / 0 失败 / 0 跳过**。

### 一、两个 `Gap` 的对照现在都有第二个证人

| | **imperva**（`VendorAbsent`） | **perimeterx**（`NoPageMarker`） |
|---|---|---|
| 第一个证人 | 六种拼写全 **0** | `px-captcha` **0**（cookie 名 4 条有） |
| **第二个证人** | **`AntiBotVendors.All` 不含它** | **`AntiBotVendors` 的 PerimeterX 条目有 4 条** |
| 含义 | 厂商**不在**产物里 | 厂商**在**，而没有页面级串 |

**→ 同一份台账，一个用于证明**缺席**，一个用于证明**在场但缺某类字面量**。
→ 两者都以「每条都带证据」为前提。**

### 二、而 PerimeterX 那四条，逐条都不是页面级串

| 字面量 | 命中 | 性质 |
|---|---|---|
| `PerimeterX` | 5 | **复刻件自己的文案** —— `"PerimeterX block (Rotating proxy)"` 是 Cybersole **弹给用户**的 |
| `PerimeterX-Token` | 1 | cookie / header 名 |
| `PerimeterXHandler` | 1 | **类名**（反射元数据，UTF-8） |
| `_pxHandler` | 1 | 字段 / 方法名 |

**→ 四条里**没有一条**会在一个商店的**响应体**里出现。
→ 那正是 `Gap.NoPageMarker` 的精确含义，而现在它有两个来源支持。**

### 三、而 `"PerimeterX block (Rotating proxy)"` 是**行为证据**

**它是本次会话里**唯一**一条带厂商名的用户可见文案。而它说的是「换代理」——
**那说明原版遇到过 PerimeterX 的封禁，而它的应对是**换代理**，不是解挑战。**

**→ 那与 `State.DetectedOnly`（检测到但不处理）**一致**。
→ 而「那是巧合还是当初就这么定的」**未查，标 Unknown**。
→ 而它值得查：若原版真的只是换代理，那复刻件也不该给 perimeterx 写 solver。**

### 四、4 条守卫

| 守卫 | 断言 |
|---|---|
| `TheInventoryEntryIsTheFourClassifiedLiterals` | 台账条目就是那四条 |
| **`NoneOfTheFourIsAPageLevelLiteral`** | 四条都不含 `px-captcha` / `captcha-delivery` / `/interstitial/` / `block` |
| `TheRowRecordsTheGapAsAMissingPageMarker` | `Gap` / `MarkerFrom` / `Marker` 三者一致 |
| `BothGapKindsHaveALiveExample` | 两种 `Gap` 各有一个活例子 |

**→ 第 2 条是这次分类的可执行形式：它断言那四条**不是**页面级串，
  而那正是「缺页面级 marker」这个论断的内容。**

### 五、数字

| 度量 | R1021 | R1022 |
|---|---|---|
| 套件 | 2229 / 0 | **2233 / 0 / 0（+4）** |
| 产物陈旧度 | 3 / 3,563 | **4 / 3,788** |
| 函数数 | 174,336 | **174,336** |
| **有第二个证人的 `Gap` 分支** | **1**（imperva） | **2（+ perimeterx）** |
| **PerimeterX 的页面级 marker** | 未知 | **确认无（4 条逐一分类）** |
| **`"PerimeterX block (Rotating proxy)"` 的含义** | 未注意 | **记为行为证据，待查** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "px-captcha"          -> {"n":0}
python analysis/ida.py str "PerimeterX"          -> {"n":5}（含 "PerimeterX block (Rotating proxy)"）
python analysis/ida.py str "PerimeterXHandler"   -> {"n":1}
python analysis/ida.py str "_pxHandler"          -> {"n":1}
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~PerimeterXMarker" -m:1      -> 4 通过
python tools/metrics_report.py -> 完整套件 exit 0  2233 / 0 / 0
```

### 七、仍然 Unknown

- **那条文案是否就是原版对 PerimeterX 的全部处置**：**待查** —— 若是，复刻件不该给它写 solver。

### 八、教训

**同一份台账能做两件相反的事：证明一个厂商**不在**（看它没列谁），
和证明一个厂商**在而缺某样东西**（看它列了什么）。第二种用法我上一轮没想到。**

**→ 而第二种更少见：它需要把列出的条目**逐条分类**，而不是只数个数。
→ 而分类的结果正好是那个论断的内容。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1022", BLOCKER)
    ensure(RSTATUS, "R1022", BLOCKER)
    ensure(RVERDICT, "第 1022 轮", VERDICT)
    ensure(BACKLOG, "R1022", BACKLOG_ADD)

    note = (
        "\n## R1022 补充 — **PerimeterX 是 Imperva 的镜像情形；台账条目是第二个证人**（套件 2233）\n\n"
        "**两个 Gap 各有两个证人**：\n"
        "- imperva `VendorAbsent`：六拼写全 0 + **台账不含它**\n"
        "- perimeterx `NoPageMarker`：`px-captcha` 0（cookie 名 4 条有）+ **台账条目有 4 条**\n"
        "→ **同一份台账：看它没列谁证明缺席；看它列了什么证明在场而缺一类字面量。**\n\n"
        "**四条逐条分类（无一是页面级串）**：`PerimeterX` 5 命中（复刻件自己的文案）· `PerimeterX-Token` 1（cookie 名）·\n"
        "`PerimeterXHandler` 1（类名）· `_pxHandler` 1（字段名）。\n"
        "→ 没有一条会在商店的**响应体**里出现 ⇒ `NoPageMarker` 两源支持。\n\n"
        "**而那条文案是行为证据**：`\"PerimeterX block (Rotating proxy)\"` 说的是**换代理** ⇒\n"
        "原版遇到过 PerimeterX 封禁，应对是**绕过**不是**解挑战**，与 `DetectedOnly` 一致。\n"
        "→ **待查**：若原版真的只换代理，复刻件不该给 perimeterx 写 solver。\n\n"
        "**4 条守卫**（`PerimeterXMarkerTests`）：条目就是那四条 · **`NoneOfTheFourIsAPageLevelLiteral`（分类的可执行形式）** ·\n"
        "三列一致 · 两种 Gap 各一活例子。\n\n"
        "数字：套件 2233（+4）· 陈旧度 4 / 3,788 · 函数数 174,336 · 双证人 Gap 分支 1 → **2**。\n\n"
        "纪律：**同一个清单，数「缺谁」与分类「有什么」是两个不同的问题。**\n\n"
        "下一轮：查那条文案是否就是原版对 PerimeterX 的全部处置（若是，perimeterx 不该有 solver）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1022" not in h:
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
             for p, k in ((RBLOCK, "R1022"), (RSTATUS, "R1022"), (RVERDICT, "第 1022 轮"), (BACKLOG, "R1022")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1022: PerimeterX is Imperva's mirror image, and the inventory entry is the second witness\n\n"
         "R1021 proved Imperva absent from two directions and left the other gap kind for this round. PerimeterX turns\n"
         " out to be its mirror, and the same inventory answers the opposite question about it.\n\n"
         "Imperva's absence rests on the list not naming it. PerimeterX's state rests on the list naming it with four\n"
         " literals, and none of those four is a string a store's page would contain: five hits of PerimeterX are this\n"
         " workspace's own narration, the token is a cookie name, the handler is a class name out of reflection metadata,\n"
         " and _pxHandler is a field. So the vendor is handled and there is nothing to grep a response body for, which is\n"
         " exactly what NoPageMarker means and why it is not VendorAbsent.\n\n"
         "That per-item classification is the work. Counting four literals would have said the vendor is evidenced and\n"
         " stopped there; classifying them is what turns the count into the claim.\n\n"
         "One of the four is worth more than the rest. \"PerimeterX block (Rotating proxy)\" is the only user-facing\n"
         " string in this session that names a vendor, and what it says is: switch proxies. So the original met\n"
         " PerimeterX blocks and responded by routing around them rather than solving them, which agrees with the row's\n"
         " DetectedOnly state -- though I cannot yet say whether that agreement is a decision or a coincidence, and it\n"
         " matters: if routing around is the original's whole response, this replica should not be growing a PerimeterX\n"
         " solver.\n\n"
         "Four guards pin the finding, and the load-bearing one asserts that none of the four literals is page-level.\n"
         "That is the executable form of the classification, so a later edit that quietly added an HTML marker to the\n"
         " inventory would break the claim rather than silently upgrade it.\n\n"
         "Figures: suite 2229 to 2233, freshness four files and 3,788 lines, count 174,336, gap kinds with two witnesses\n"
         " up from one to two, and no page-level marker for PerimeterX confirmed rather than assumed.\n\n"
         "Unknown: whether that narration is the original's entire response to PerimeterX.\n\n"
         "The lesson is that one inventory answers two opposite questions -- who is missing, and who is present but\n"
         " lacking a particular kind of literal -- and that the second needs per-item classification rather than a count,\n"
         " because the classification is the claim.\n\n"
         "Two source files and one test file changed; suite green at 2233."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()