"""Record R941: Dummy is cart priming, not a dry run -- the third misfiled name in three rounds."""

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
### `Dummy` 不是 dry run，是**购物车预热**（R941）

**R940 把 `AddToCartDummy` 记成「五个里唯一不依赖端点证据的」，理由是「它的名字说它不和店说话」。
而它的邻居说不是。**

### 四条连号

```
<GetProduct>d__45 · <AddToCartDummy>d__46 · <AddToCartMulti>d__47 · <RemoveDummy>d__48
```

**一个 add 紧跟着它的 remove。**

> **那不是 dry run，也不是 test —— 那是**预热**：
> 一个「首次加车才建车」的店，会把一次往返和一次会话变更花在最糟的时刻。
> 所以提前加一个便宜的占位商品、稍后移除，就让真正的加车**复用一辆已经存在的车**。**
> **而 `Dummy` 说的是**那件商品**是占位，不是**那次调用**是假的。**

### 而它的邻居把这家店也描出来了

```
Login · LoginVerify2FA · EnableTwoFactor · Register
FetchBalance · CheckFanRewardStat · EnterSweepStakesRaffle
```

**余额 · 粉丝奖励统计 · 抽奖 —— 那是一家**有会员体系**的店的表面。
而这也解释了为什么占位商品便宜：那家店有。**

> **而这是 Inference（从名字推的），标注了 —— 它缩小了「这是哪家店」，但没指认它。**

### 所以「唯一不依赖端点证据」这句也错了

**它需要的是**一个占位商品**，不是一个恢复到的 car地址。
而那是**按店不同的数据**，不是按框架不同的代码。**

> **所以它不是「不依赖证据」，而是「依赖另一种证据」。**
> **而 R940 把它记成独立的那个，是因为「dummy」听起来像「空的」——
> 而它实际是「占位的」。词根一样，意思相反。**

### 而这一轮又抓到两处旧断言

**① 我自己的 `DoesNotContain("dry run")` —— 而注释写的是「not a dry run」，当然含那两个词。**
**② R940 那个 `TheDummyPathIsTheIndependentOne` 断言注释含「no endpoint evidence」——
而那正是 R941 纠正掉的说法。**

**两处都改成断言**纠正后**的说法，并改名为 `TheDummyPathIsPrimingNotADryRun`。**

### 数字

| 度量 | R940 | **R941** |
|---|---|---|
| 套件 | 2012 | **2023** |
| 产物陈旧度 | 7 文件 / 752 行 | **8 文件 / 832 行** |
| 三个轮次里被纠正的名字 | 2（Frontend · Box） | **3（+ Dummy）** |

### 教训

> **三轮，三个名字被纠正：`Frontend`（伞）· `Box`（PopMart 一步）· `Dummy`（占位不是空）。**
> **而三个都是**同一个判据**能抓的：**看它旁边是谁**（连号的 state machine、有没有配套的 ScrapeProduct*、
> 后面是否紧跟一个反操作）。**
> **而三个都靠「名字听起来像什么」骗过了我一次。**
> **所以那条判据不是「别相信名字」，而是**名字只能提出假设，连号才能确认**。**
"""

if "`Dummy` 不是 dry run" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R941 appended")

VERDICT = """

---

## 第 941 轮：`Dummy` 是购物车预热，不是 dry run

### 四条连号

```
<GetProduct>d__45 · <AddToCartDummy>d__46 · <AddToCartMulti>d__47 · <RemoveDummy>d__48
```

**一个 add 紧跟它的 remove —— 不是 dry run 也不是 test，是**预热**：
提前加一个便宜的占位商品、稍后移除，让真正的加车**复用一辆已存在的车**。**

> **`Dummy` 说的是**那件商品**是占位，不是**那次调用**是假的。**

### 邻居把店也描出来了

```
Login · LoginVerify2FA · EnableTwoFactor · Register · FetchBalance
CheckFanRewardStat · EnterSweepStakesRaffle
```

**余额 · 粉丝奖励 · 抽奖 → 一家**有会员体系**的店（Inference，标注了）。
也解释了为什么占位商品便宜。**

### 「唯一不依赖端点证据」也错了

**它需要的是**一个占位商品**，不是 car地址 —— 那是**按店不同的数据**，不是按框架不同的代码。**
**所以不是「不依赖证据」，是「依赖另一种证据」。**

### 而这一轮抓到两处旧断言

**① 我自己的 `DoesNotContain("dry run")` —— 而注释写的是「not a dry run」。
② R940 的 `TheDummyPathIsTheIndependentOne` 断言「no endpoint evidence」—— 正是被纠正掉的说法。**

**两处都改成断言纠正后的说法，并改名为 `TheDummyPathIsPrimingNotADryRun`。**

### 数字

| 度量 | R940 | **R941** |
|---|---|---|
| 套件 | 2012 | **2023** |
| 产物陈旧度 | 7 / 752 | **8 / 832** |
| 三轮里被纠正的名字 | 2 | **3（+ Dummy）** |

### 教训

> **三轮，三个名字被纠正：`Frontend`（伞）· `Box`（PopMart 一步）· `Dummy`（占位不是空）。
> 三个都是**同一个判据**能抓的：**看它旁边是谁**。**
> **所以那条判据不是「别相信名字」，而是**名字只能提出假设，连号才能确认**。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — `Dummy` 是购物车预热（R941，**+11 用例 + 修 2 处旧断言**）

### 证据

```
d__45 GetProduct · d__46 AddToCartDummy · d__47 AddToCartMulti · d__48 RemoveDummy
```

**add 紧跟 remove → 预热，不是 dry run。**

**邻居：Login/2FA/Register/FetchBalance/CheckFanRewardStat/EnterSweepStakesRaffle → 有会员体系的店（Inference）。**

### `Scripts/CartPriming.cs`

**`PrimingSequence`(4) · `LoyaltySurface`(7) · `UnknownForPriming` · `Meaning` · `IsPriming` · `CallsFor`**

### 两处旧断言被修

**① 我的 `DoesNotContain("dry run")`（注释含「not a dry run」）。
② R940 的 `TheDummyPathIsTheIndependentOne` → 改名 `TheDummyPathIsPrimingNotADryRun`。**

### 数字

**套件 2012 → 2023 · 陈旧度 7/752 → 8/832**

| 仍 Unknown | |
|---|---|
| 哪件商品可当占位 | 按店数据 |
| `Dummy` 的真实接口形态 | 只有名字 |
| 是否还有第 4 个被误读的名字 | 未扫完 |

**纪律**：名字只能提出假设，连号才能确认。三轮三个名字被纠正，三个都靠这个判据。
"""

BLOCKER = """

---

## 365. `Dummy` 是购物车预热；三轮第三个被纠正的名字

> R941。**改产品代码 +11 用例 + 修 2 处旧断言。** 套件 **2023 通过 / 0 失败 / 0 跳过**。

### 一、四条连号

```
<GetProduct>d__45 · <AddToCartDummy>d__46 · <AddToCartMulti>d__47 · <RemoveDummy>d__48
```

**add 紧跟 remove → **预热**：提前加便宜的占位商品、稍后移除，让真正的加车复用已存在的车。**

**`Dummy` 说的是**商品**是占位，不是**调用**是假的。**

### 二、邻居说明店的性质

```
Login · LoginVerify2FA · EnableTwoFactor · Register
FetchBalance · CheckFanRewardStat · EnterSweepStakesRaffle
```

**有会员体系的店（Inference）→ 解释了为什么占位商品便宜。**

### 三、R940 那句「唯一不依赖端点证据」也错了

**它需要**一个占位商品** —— 按店数据，不是按框架代码。所以是「依赖另一种证据」。**

### 四、两处旧断言被修

1. **我自己的 `DoesNotContain("dry run")` —— 注释写的是「not a dry run」，当然含那两个词。**
2. **R940 的 `TheDummyPathIsTheIndependentOne` → 改名 `TheDummyPathIsPrimingNotADryRun`。**

### 五、数字

| 度量 | R940 | R941 |
|---|---|---|
| 套件 | 2012 | **2023** |
| 产物陈旧度 | 7 / 752 | **8 / 832** |
| **三轮里被纠正的名字** | 2 | **3** |

### 六、验证

```
analysis/ida.py str "AddToCartDummy"  -> 4 命中，d__45/46/47/48 连号
test --filter CartPrimingTests        -> 11 通过
test --filter AddToCartCoverageTests  -> 11 通过
metrics_report.py                     -> 2023 通过 / 0 失败
```

### 七、仍然 Unknown

- **哪件商品可当占位**：**Unknown** —— 按店数据。
- **`Dummy` 的真实接口形态**：**Unknown** —— 只有名字。
- **是否还有第 4 个被误读的名字**：**Unknown** —— 未扫完。

### 八、教训

**三轮，三个名字被纠正：`Frontend`（伞）· `Box`（PopMart 一步）· `Dummy`（占位不是空）。**

**三个都是同一个判据能抓的：**看它旁边是谁**。三个都靠「名字听起来像什么」骗过我一次。**

**所以那条判据不是「别相信名字」，而是**名字只能提出假设，连号才能确认**。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R941", BLOCKER)
    ensure(RSTATUS, "R941", BLOCKER)
    ensure(RVERDICT, "第 941 轮", VERDICT)
    ensure(BACKLOG, "R941", BACKLOG_ADD)

    note = (
        "\n## R941 补充 — Dummy 是购物车预热，不是 dry run（+11 用例 + 修 2 处旧断言，套件 2023）\n\n"
        "四条连号 d__45 GetProduct · d__46 AddToCartDummy · d__47 AddToCartMulti · d__48 RemoveDummy → "
        "add 紧跟 remove = 预热（提前加占位商品、稍后移除，让真正加车复用已存在的车）。\n\n"
        "邻居 Login/2FA/Register/FetchBalance/CheckFanRewardStat/EnterSweepStakesRaffle → 有会员体系的店（Inference）。\n\n"
        "R940 那句「唯一不依赖端点证据」也错了：它需要一个占位商品（按店数据），不是 car地址。\n\n"
        "两处旧断言被修：我的 DoesNotContain(\"dry run\")；R940 的 TheDummyPathIsTheIndependentOne → 改名 "
        "TheDummyPathIsPrimingNotADryRun。\n\n"
        "数字：套件 2012 → 2023 · 陈旧度 7/752 → 8/832 · 三轮里被纠正的名字 2 → 3。\n\n"
        "纪律：名字只能提出假设，连号才能确认。\n\n"
        "下一轮：扫是否还有第 4 个被误读的名字（用连号判据）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R941" not in h:
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
             for p, k in ((RBLOCK, "R941"), (RSTATUS, "R941"), (RVERDICT, "第 941 轮"), (BACKLOG, "R941")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R941: Dummy is cart priming, the third name in three rounds that meant something else\n\n"
         "R940 called AddToCartDummy the one gap that need not wait on endpoint evidence, on the reasoning that its name\n"
         " says it does not talk to a shop. Its neighbours say otherwise: four consecutive state machines run GetProduct,\n"
         " AddToCartDummy, AddToCartMulti, RemoveDummy -- an add followed immediately by its remove. That is not a dry run\n"
         " and not a test. A shop that creates a cart on first add costs a round trip and a session mutation at the worst\n"
         " possible moment, so adding a cheap placeholder early and removing it later leaves a cart for the real add to\n"
         " reuse. Dummy describes the item as a placeholder, not the call as fake.\n\n"
         "The same file's other descriptors -- Login, LoginVerify2FA, EnableTwoFactor, Register, FetchBalance,\n"
         " CheckFanRewardStat, EnterSweepStakesRaffle -- describe a store with a loyalty programme, which is why a cheap\n"
         " placeholder is available at all. That narrowing is inference from names and is labelled as such.\n\n"
         "So the claim that this gap needs no endpoint evidence was wrong too, in a subtler way: what it needs is a\n"
         " placeholder item rather than a recovered cart address, which is per-shop data rather than per-framework code.\n"
         " Not independent of evidence, but dependent on a different kind.\n\n"
         "Two older assertions had to be corrected. My own DoesNotContain(\"dry run\") failed against a note that reads not\n"
         " a dry run, and R940's test asserted the very claim this round overturned; it is renamed to say priming rather\n"
         " than independent.\n\n"
         "Figures: suite 2012 to 2023, freshness from seven files to eight and seven hundred and fifty-two lines to eight\n"
         " hundred and thirty-two, and three names corrected across three rounds.\n\n"
         "Unknown: which item a given shop tolerates as a placeholder; the step's real interface, of which only the name\n"
         " survives; and whether a fourth name is also misfiled, since the scan is unfinished.\n\n"
         "The lesson is that all three corrections were catchable by one test -- look at what stands beside the name --\n"
         " and all three got past me by sounding right. So the rule is not to distrust names; it is that a name only\n"
         " proposes a hypothesis and consecutive ordinals confirm one.\n\n"
         "Product code and two tests changed; suite green at 2023."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()