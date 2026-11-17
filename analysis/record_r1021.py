"""Record R1021: Imperva is absent on two independent counts, and the branch is recorded as an extension."""

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
### Imperva 的双重缺席证据；而那个分支留作**扩展**（R1021）

**R1020 说按 `Gap` 分流：imperva 查原版是否处理它。查了，而第二个证据来自**原版自己的风控台账**。**

### ① 第一个证据（R1019 已取）：六种拼写全 0

```
_Incapsula_Resource  0
incap_ses            0
visid_incap          0
incapsula            0
imperva              0
nlbi_                0
```

### ② 而第二个证据：`AntiBotVendors` 的台账里**没有它**

**`AntiBotVendors.Vendor(name, Evidence)` 是一个**带证据清单**的厂商记录。
`All` 里八条，`NamedButNotHandled` 里一条：**

```
All:                 DataDome · PerimeterX · Akamai · Kasada · TrustDecision · Cloudflare · Forter · Signifyd
NamedButNotHandled:  Riskified
imperva 出现次数:     0
```

**→ Imperva 连「被点名但未处理」都不算。**
**→ 而那些条目**每条都带镜像 Evidence** —— 所以「Imperva 不在其中」意味着
  **当初从镜像里提取厂商清单时它就没出现**。**

**→ 两个来源（一次逐串查询、一份早先提取的清单）在不同时间独立地给出同一个答案。
→ 而那正是 AGENTS §2.7 第三条配套要的东西：**两个独立来源报同一个结论才算数。****

### ③ 所以 `Gap.VendorAbsent` 有**双重支持**，可以比「我没找到」更强

**→ 而它与 R1019 那个 `cf-chl` 的差别在于处置：**
- **`cf-chl`：镜像里有一个**更好的替代**（`challenge-platform`）⇒ **换掉**
- **`_Incapsula_Resource`：镜像里**没有替代**，而那个厂商根本不在 ⇒ **留作扩展**

### ④ 而留的理由是**防御性**，不是惰性

**一个 Imperva 墙如果出现在原版从未覆盖的站上，`DetectAsync` 会把它判成 `"none"`，
于是 flow 会把**封禁页当商品页**处理 —— 那比多一条永不触发的分支坏得多。**

**→ 而那条分支只在页面**真的写了** `_Incapsula_Resource` 时才触发，所以厂商缺席时它的成本是零。
→ 而注释现在写明：`this branch is an extension, not the image's behaviour`。**

### ⑤ 3 条守卫

| 守卫 | 断言 |
|---|---|
| `TheVendorInventoryDoesNotListImperva` | `All` 与 `NamedButNotHandled` 都不含 imperva |
| `EveryListedVendorCarriesEvidence` | 台账里每个厂商都有非空 Evidence —— **那正是「缺席有意义」的前提** |
| `TheBranchIsRecordedAsAnExtension` | 分支在、注释写明「extension」、`Gap == VendorAbsent`、Note 含「two independent sources」 |

**→ 第 2 条是那个论证的支点：一个**不带证据**的清单，缺席什么都说明不了。**

### ⑥ 数字

| 度量 | R1020 | **R1021** |
|---|---|---|
| 套件 | 2226 / 0 | **2229 / 0 / 0（+3）** |
| 产物陈旧度 | 3 / 3,552 | **3 / 3,563** |
| 函数数 | 174,336 | **174,336** |
| **imperva 的独立证据数** | 1（六拼写全 0） | **2（+ 台账不含它）** |
| **imperva 分支的处置** | 未说明 | **留作扩展，注释写明** |
| **台账里带证据的厂商** | 8（未验证） | **8（守卫验证）** |

### 教训

> **「我没找到」与「它不在」之间的桥，是一条**第二条独立证据**。而这里它来得意外地便宜：
> 一份早先为别的目的写的清单，恰好能回答这个问题。**
> **→ 而那份清单能回答它，只因为**每条都带证据** —— 一个不带证据的清单，缺席什么都说明不了。
> → 所以「给每个条目留证据」这件事的价值，在于它让**将来的一个否定**变得可用。**
"""

if "Imperva 的双重缺席证据" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1021 轮：Imperva 的双重缺席证据；而那个分支留作扩展

### ① 第一个证据（R1019 已取）：六种拼写全 0

`_Incapsula_Resource` · `incap_ses` · `visid_incap` · `incapsula` · `imperva` · `nlbi_` —— 全 0。

### ② 第二个证据：`AntiBotVendors` 台账里**没有它**

```
All:                 DataDome · PerimeterX · Akamai · Kasada · TrustDecision · Cloudflare · Forter · Signifyd
NamedButNotHandled:  Riskified
imperva 出现次数:     0
```

**→ 连「被点名但未处理」都不算。
→ 而那些条目**每条都带镜像 Evidence** ⇒ 「Imperva 不在其中」意味着**当初提取时它就没出现**。
→ 两个来源在不同时间独立给出同一答案 —— AGENTS §2.7 第三条配套要的正是这个。**

### ③ 所以 `Gap.VendorAbsent` 比「我没找到」更强

**而与 R1019 那个 `cf-chl` 的差别在处置：**
- **`cf-chl`：有更好替代（`challenge-platform`）⇒ 换掉**
- **`_Incapsula_Resource`：无替代，厂商根本不在 ⇒ 留作扩展**

### ④ 留的理由是**防御性**

**一个 Imperva 墙若出现在原版从未覆盖的站上，`DetectAsync` 会判成 `"none"`，
于是 flow 把**封禁页当商品页** —— 那比多一条永不触发的分支坏得多。
→ 分支只在页面真的写了 `_Incapsula_Resource` 时触发，厂商缺席时成本为零。
→ 注释写明 `this branch is an extension, not the image's behaviour`。**

### ⑤ 3 条守卫

`TheVendorInventoryDoesNotListImperva` · **`EveryListedVendorCarriesEvidence`（论证的支点）** ·
`TheBranchIsRecordedAsAnExtension`

**→ 第 2 条是支点：一个**不带证据**的清单，缺席什么都说明不了。**

### ⑥ 数字

| 度量 | R1020 | **R1021** |
|---|---|---|
| 套件 | 2226 / 0 | **2229 / 0 / 0（+3）** |
| 产物陈旧度 | 3 / 3,552 | **3 / 3,563** |
| 函数数 | 174,336 | **174,336** |
| **imperva 的独立证据数** | 1 | **2** |
| **分支处置** | 未说明 | **留作扩展，注释写明** |
| **带证据的厂商** | 8（未验证） | **8（守卫验证）** |

### 教训

> **「我没找到」与「它不在」之间的桥，是一条**第二条独立证据**。而这里它来得意外地便宜：
> 一份早先为别的目的写的清单，恰好能回答这个问题。**
> **→ 那份清单能回答它，只因为**每条都带证据** —— 一个不带证据的清单，缺席什么都说明不了。
> → 所以「给每个条目留证据」的价值，在于它让**将来的一个否定**变得可用。**
"""

BACKLOG_ADD = """

## 优先级 ② — **Imperva 双重缺席证据；`_Incapsula_Resource` 分支留作扩展**（R1021）

### 两个独立证据

1. **六种拼写全 0**（R1019）：`_Incapsula_Resource` · `incap_ses` · `visid_incap` · `incapsula` · `imperva` · `nlbi_`
2. **`AntiBotVendors` 台账不含它**：`All` 八条（DataDome · PerimeterX · Akamai · Kasada · TrustDecision ·
   Cloudflare · Forter · Signifyd）· `NamedButNotHandled` 一条（Riskified）· imperva **0**
   → 那些条目**每条都带镜像 Evidence** ⇒ 缺席有意义

**→ AGENTS §2.7 第三条配套：两个独立来源报同一结论才算数。**

### 处置与 R1019 的差别

| 串 | 替代 | 处置 |
|---|---|---|
| `cf-chl` | `challenge-platform`（2） | **换掉** |
| `_Incapsula_Resource` | 无 | **留作扩展** |

**留的理由（防御性）**：Imperva 墙若出现在原版未覆盖的站上，`DetectAsync` 判 `"none"` ⇒
flow 把**封禁页当商品页**。分支只在页面真写该串时触发 ⇒ 缺席时成本为零。
**注释写明 `this branch is an extension, not the image's behaviour`。**

### 3 条守卫（`ImpervaAbsenceTests`）

`TheVendorInventoryDoesNotListImperva` · **`EveryListedVendorCarriesEvidence`** ·
`TheBranchIsRecordedAsAnExtension`

### 数字

**套件 2229（+3）· 陈旧度 3 / 3,563 · 函数数 174,336 · imperva 独立证据 1 → 2 · 带证据厂商 8（守卫验证）**

| 仍 Unknown | |
|---|---|
| imperva 是否真被原版处理 | 两个来源都说不 —— 但都不构成否定证明 |

**纪律**：给每个条目留证据的价值，在于它让**将来的一个否定**变得可用。
"""

BLOCKER = """

---

## 445. **Imperva 双重缺席证据；`_Incapsula_Resource` 分支留作扩展**

> R1021。**改 2 个源文件 + 加 1 个测试文件。** 套件 **2229 通过 / 0 失败 / 0 跳过**。

### 一、第一个证据（R1019 已取）：六种拼写全 0

```
_Incapsula_Resource  0
incap_ses            0
visid_incap          0
incapsula            0
imperva              0
nlbi_                0
```

### 二、第二个证据：`AntiBotVendors` 的台账里**没有它**

**`AntiBotVendors.Vendor(name, Evidence)` 是一个**带证据清单**的厂商记录。**

```
All:                 DataDome · PerimeterX · Akamai · Kasada · TrustDecision · Cloudflare · Forter · Signifyd
NamedButNotHandled:  Riskified
imperva 出现次数:     0
```

**→ Imperva 连「被点名但未处理」都不算。
→ 而那些条目**每条都带镜像 Evidence** —— 所以「Imperva 不在其中」意味着
  **当初从镜像里提取厂商清单时它就没出现**。
→ 两个来源在不同时间独立给出同一答案 —— AGENTS §2.7 第三条配套要的正是这个。**

### 三、`Gap.VendorAbsent` 有双重支持

**而它与 R1019 那个 `cf-chl` 的差别在**处置**：**

| 串 | 镜像替代 | 处置 |
|---|---|---|
| `cf-chl` | `challenge-platform`（2） | **换掉** |
| `_Incapsula_Resource` | **无** | **留作扩展** |

### 四、而留的理由是**防御性**，不是惰性

**一个 Imperva 墙如果出现在原版从未覆盖的站上，`DetectAsync` 会把它判成 `"none"`，
于是 flow 会把**封禁页当商品页**处理 —— 那比多一条永不触发的分支坏得多。**

**→ 而那条分支只在页面**真的写了** `_Incapsula_Resource` 时才触发，所以厂商缺席时它的成本是零。
→ 而注释现在写明：`this branch is an extension, not the image's behaviour`。**

### 五、3 条守卫

| 守卫 | 断言 |
|---|---|
| `TheVendorInventoryDoesNotListImperva` | `All` 与 `NamedButNotHandled` 都不含 imperva |
| `EveryListedVendorCarriesEvidence` | 台账里每个厂商都有非空 Evidence —— **那正是「缺席有意义」的前提** |
| `TheBranchIsRecordedAsAnExtension` | 分支在、注释写明 extension、`Gap == VendorAbsent`、Note 含 two independent sources |

**→ 第 2 条是那个论证的支点：一个**不带证据**的清单，缺席什么都说明不了。**

### 六、数字

| 度量 | R1020 | R1021 |
|---|---|---|
| 套件 | 2226 / 0 | **2229 / 0 / 0（+3）** |
| 产物陈旧度 | 3 / 3,552 | **3 / 3,563** |
| 函数数 | 174,336 | **174,336** |
| **imperva 的独立证据数** | 1（六拼写全 0） | **2（+ 台账不含它）** |
| **imperva 分支的处置** | 未说明 | **留作扩展，注释写明** |
| **台账里带证据的厂商** | 8（未验证） | **8（守卫验证）** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "_Incapsula_Resource"  -> {"n":0}
python analysis/ida.py str "incap_ses"            -> {"n":0}
python analysis/ida.py str "nlbi_"                -> {"n":0}
cd replica
python - 读 src/Cybersole.Stores/Flows/AntiBotVendors.cs -> All 八条 · NamedButNotHandled 一条 · imperva 0
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~ImpervaAbsence" -m:1        -> 3 通过
python tools/metrics_report.py -> 完整套件 exit 0  2229 / 0 / 0
```

### 八、仍然 Unknown

- **imperva 是否真被原版处理**：**两个来源都说不** —— 但两者都不是否定证明。

### 九、教训

**「我没找到」与「它不在」之间的桥，是一条**第二条独立证据**。而这里它来得意外地便宜：
一份早先为别的目的写的清单，恰好能回答这个问题。**

**→ 而那份清单能回答它，只因为**每条都带证据** —— 一个不带证据的清单，缺席什么都说明不了。
→ 所以「给每个条目留证据」这件事的价值，在于它让**将来的一个否定**变得可用。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1021", BLOCKER)
    ensure(RSTATUS, "R1021", BLOCKER)
    ensure(RVERDICT, "第 1021 轮", VERDICT)
    ensure(BACKLOG, "R1021", BACKLOG_ADD)

    note = (
        "\n## R1021 补充 — **Imperva 双重缺席证据；`_Incapsula_Resource` 分支留作扩展**（套件 2229）\n\n"
        "**两个独立证据**：① 六种拼写全 0（R1019）② **`AntiBotVendors` 台账不含它** ——\n"
        "`All` 八条（DataDome · PerimeterX · Akamai · Kasada · TrustDecision · Cloudflare · Forter · Signifyd）·\n"
        "`NamedButNotHandled` 一条（Riskified）· imperva **0**。而那些条目**每条都带镜像 Evidence** ⇒ 缺席有意义。\n"
        "→ **AGENTS §2.7 第三条配套：两个独立来源报同一结论才算数。**\n\n"
        "**处置与 R1019 的差别**：`cf-chl` 有替代（`challenge-platform`）⇒ **换掉**；\n"
        "`_Incapsula_Resource` **无替代**、厂商根本不在 ⇒ **留作扩展**。\n\n"
        "**留的理由是防御性**：Imperva 墙若出现在原版未覆盖的站上，`DetectAsync` 判 `\"none\"` ⇒\n"
        "flow 把**封禁页当商品页**。分支只在页面真写该串时触发 ⇒ 缺席时成本为零。\n"
        "注释写明 `this branch is an extension, not the image's behaviour`。\n\n"
        "**3 条守卫**（`ImpervaAbsenceTests`）：台账不含它 · **每条都有 Evidence（论证支点）** · 分支记为扩展。\n\n"
        "数字：套件 2229（+3）· 陈旧度 3 / 3,563 · 函数数 174,336 · imperva 独立证据 1 → **2**。\n\n"
        "纪律：**给每个条目留证据的价值，在于它让将来的一个否定变得可用。**\n\n"
        "下一轮：perimeterx 的页面级 marker（另一个 `Gap` 分支：厂商在，缺 marker）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1021" not in h:
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
             for p, k in ((RBLOCK, "R1021"), (RSTATUS, "R1021"), (RVERDICT, "第 1021 轮"), (BACKLOG, "R1021")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1021: Imperva is absent on two independent counts, and its branch stays as an extension\n\n"
         "R1020 split the inferred rows by reason so this round could act differently on each. Imperva's question was\n"
         " whether the original handles it, and six absent spellings are a strong signal that is not a proof.\n\n"
         "The second witness turned out to be cheap. AntiBotVendors.All is a list of eight vendors, each carrying the image\n"
         " literals that justify its membership, and it does not mention Imperva at all -- nor does NamedButNotHandled. Two\n"
         " things built at different times, one by querying strings and one by extracting a vendor inventory, agree.\n\n"
         "That agreement matters because of why the inventory can answer the question: every entry carries evidence. A\n"
         " list of names with no literals behind it would say nothing by omission, and this one is checkable precisely\n"
         " because someone recorded what each name rests on.\n\n"
         "The disposition differs from R1019's cf-chl, and the difference is what the image offers. cf-chl had a better\n"
         " replacement in challenge-platform, so it was swapped. _Incapsula_Resource has no replacement and its vendor is\n"
         " not in the artifact at all, so the branch stays -- as an extension, which the comment now says in those words.\n"
         " The reason is defensive: an Imperva wall on a store the original never covered would classify as \"none\" and\n"
         " the flow would treat a block page as a product page, and that is far worse than a branch that fires only on a\n"
         " page actually naming the resource.\n\n"
         "Three guards pin it, and the load-bearing one asserts that every listed vendor carries evidence -- that is the\n"
         " premise the whole negative rests on, so it deserves a test rather than a comment.\n\n"
         "Figures: suite 2226 to 2229, freshness three files and 3,563 lines, count 174,336, independent witnesses for\n"
         " Imperva up from one to two, and eight vendors now verified to carry evidence rather than assumed to.\n\n"
         "Unknown: whether the original handles Imperva. Both witnesses say no and neither is a disproof.\n\n"
         "The lesson is that the bridge between \"I did not find it\" and \"it is not there\" is a second independent\n"
         " source, that this one arrived free from work done for another purpose, and that it could only answer because\n"
         " someone had written down what each entry rests on -- which is what makes a future negative usable.\n\n"
         "Two source files and one test file changed; suite green at 2229."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()