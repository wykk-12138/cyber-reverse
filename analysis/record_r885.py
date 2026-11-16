"""Record R885: the shape audit reads a sampled pool, and my own baseline has a defect."""

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
### 「形状 78」这个数字的证据源是**抽样池**（R885）

**目标：答 R884 的问题 —— `CreateModel` 那 12 个多余属性是 XAML 需要还是我编的。**

**按 §2.7c 先查，三次都是同一个答案：工具已经有了。`tools/shape_audit.py` 做的正是
「镜像的访问器形状 ↔ 复刻件声明」的对比，而 `docs/METRICS.md` 里那个「形状 78」就是它的输出。**

### 但它的证据源是抽样池

```
shape_audit.py:  POOL = analysis/pe_strings.txt     ← 抽样（180,228 行，§2.7b 四次踩坑）
实测:            evidence: string pool (102 types, sampled)
```

**而 R883 的基线（`idautils.Strings()` 全量）有 **211** 个类型。**

**池子里少一半，而且少掉的那个包含了 `Cybersole.Models.CreateModel` —— 所以
「形状 78」这个数从来没包含过 `CreateModel`。**

### 于是我给它加了 `--baseline`

```
shape_audit.py --baseline   -> evidence: baseline (211 types)
```

**但结果暴露了我自己那份基线的缺陷：**

| 证据源 | 类型数 | mismatches |
|---|---|---|
| 抽样池 | 102 | **78** |
| R883 基线 | 211 | **0** |

**0 不是好消息 —— 是**基线把 `Getter`/`Setter` 的区分丢了**。**

**R883 的 `dump_accessors.py` 写成 `<类型> TAB <数量> TAB <属性列表>`，
**访问器种类（Getter/Setter/Property）在格式里就没了**。而 `want_set` 依赖 `'Setter' in kinds`，
所以基线模式下这个检查永不成立。**

**→ 一份丢了字段的数据比没有数据更危险：它让检查从「78 个不匹配」变成「0 个不匹配」，
而两句话在报表上看起来像「修好了」。**

### `CreateModel` 的答案：5 条，不是 12

**用基线跑 `--extra --type CreateModel`：**

```
CreateModel   AccountId          replica=prop+set
CreateModel   ProfileId          replica=prop+set
CreateModel   ProxyGroupId       replica=prop+set
CreateModel   TaskGroupId        replica=prop+set
CreateModel   UseSmartActions    replica=prop+set
total review rows: 5
```

**所以 12 个多余属性里有 **7 个在基线里有证据**，5 个没有。**

**而这 5 个的共同特征：四个是 `*Id`（外键）· 一个是 `UseSmartActions`。
`CreateModel` 在镜像里用 `ProxyGroup`（对象）而不用 `ProxyGroupId`（键）——
**这是一致的：镜像传对象，复刻件传 id。****
"""

if "「形状 78」这个数字的证据源是**抽样池**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R885 appended")

BLOCKER = """

---

## 309. 「形状 78」的证据源是抽样池；而我那份基线丢了字段

> R885。**改工具，未改产品代码。** 套件沿用 **1780 通过 / 0 失败 / 0 跳过**。

### 一、三次查工具，三次都已存在

**R884 学会了 `where_is --sub` 的坑。这一轮按 §2.7c 查「有没有现成的形状对比工具」，
`tools/shape_audit.py` 就是 —— 它做的正是「镜像访问器形状 ↔ 复刻件声明」，而
`docs/METRICS.md` 的「形状 78」是它的输出。**

**所以这一轮没有写新工具（除了给旧的加两个开关）。**

### 二、但它的证据源是抽样池 —— §2.7b 的坑

```
shape_audit.py: POOL = analysis/pe_strings.txt     ← 180,228 行，抽样
evidence: string pool (102 types, sampled)
```

**R883 基线的类型数是 211。池子少一半，而**少掉的那一半包含 `Cybersole.Models.CreateModel`** ——
所以「形状 78」从来没包含过这个类型。**

### 三、加 `--baseline`，而它暴露了我自己那份基线的缺陷

| 证据源 | 类型数 | mismatches |
|---|---|---|
| 抽样池 | 102 | **78** |
| R883 基线 | 211 | **0** |

**0 不是好消息。是**基线把 `Getter`/`Setter` 的区分丢了**。**

**R883 的格式是 `<类型> TAB <数量> TAB <属性列表>` —— 访问器种类在格式里就没了。
而 `want_set` 依赖 `'Setter' in kinds`，所以基线模式下这个检查**永不成立**。**

> **一份丢了字段的数据比没有数据更危险：
> 它把「78 个不匹配」变成「0 个不匹配」，而两句话在报表上看起来像「修好了」。**

**这是本轮唯一的实质缺陷，而且是**我自己上一轮引入的**。

### 四、R884 那个问题的答案

```
CreateModel   AccountId · ProfileId · ProxyGroupId · TaskGroupId · UseSmartActions   (5 条无证据)
```

**12 个多余属性里 **7 个在基线里有证据**，5 个没有。**

**而 5 个里四个是 `*Id` 外键、一个是 `UseSmartActions`。**
**镜像的 `CreateModel` 用 `ProxyGroup`（对象）而不是 `ProxyGroupId`（键）——
**所以这是一处系统性的形态差异，不是五个孤立的多余属性。****

### 五、验证

```
shape_audit.py                    -> evidence: string pool (102 types) · mismatches 78
shape_audit.py --baseline         -> evidence: baseline (211 types)   · mismatches 0（因为丢了 Setter）
shape_audit.py --baseline --extra -> total review rows 63（全类型）/ 5（CreateModel）
本轮未改产品代码；套件 1780 通过
```

### 六、仍然 Unknown

- **基线该不该重生成带访问器种类**：**应该** —— 这是本轮暴露的缺陷，而修它要回 IDA 重跑一次。
  **下一轮第一件事。**
- **那 5 个 `*Id` 属性是不是该改成对象**：**Unknown** ——
  **形态差异是 Observation，而「该改成对象」是设计判断，要看 UI 怎么绑。**
- **`--extra` 那 63 条里有多少是真多余**：**Unknown** —— 报告自称 review list 不是 defect list。

### 七、教训

**这一轮我做了三件对的事：查工具（没写重复的）、给工具加开关、发现问题就报。
以及一件错的事：**上一轮把带字段的数据压成了不带字段的**。**

**而错的那件瞒了一轮 —— 因为它的症状是「0 个不匹配」，看起来像好消息。**

**R881 说「能用可复核工具回答的不该靠手工计数」。这一轮的版本：
**能保留字段的时候，不要为了好看把它压掉** —— 因为下游的检查依赖那些字段，
而它一旦读不到，会安静地返回 0 而不是报错。**
"""

VERDICT = """

---

## 第 885 轮：「形状 78」的证据源是抽样池；而我那份基线丢了字段

### 三次查工具，三次都已存在

**`tools/shape_audit.py` 做的正是「镜像访问器形状 ↔ 复刻件声明」的对比 ——
`docs/METRICS.md` 的「形状 78」是它的输出。这一轮没写新工具，只给它加了两个开关。**

### 但它的证据源是抽样池（§2.7b 的坑）

```
evidence: string pool (102 types, sampled)      ← 180,228 行的抽样
R883 基线: 211 types                            ← idautils.Strings() 全量
```

**池子少一半，而少掉的那一半包含 `Cybersole.Models.CreateModel` ——
所以「形状 78」从来没包含过这个类型。**

### 加 `--baseline` 后暴露了我自己那份基线的缺陷

| 证据源 | 类型数 | mismatches |
|---|---|---|
| 抽样池 | 102 | **78** |
| R883 基线 | 211 | **0** |

**0 不是好消息 —— 是基线把 `Getter`/`Setter` 的区分丢了。**

> **R883 的格式是 `<类型> TAB <数量> TAB <属性列表>`，访问器种类在格式里就没了。
> 而 `want_set` 依赖 `'Setter' in kinds`，所以基线模式下这个检查**永不成立**。**
> **一份丢了字段的数据比没有数据更危险：它把「78 个不匹配」变成「0 个不匹配」，而两句话看起来像「修好了」。**

### R884 那个问题的答案

```
CreateModel: AccountId · ProfileId · ProxyGroupId · TaskGroupId · UseSmartActions   (5 条无证据)
```

**12 个多余属性里 **7 个在基线里有证据**，5 个没有。**

**而 5 个里四个是 `*Id` 外键 —— 镜像用 `ProxyGroup`（对象）而非 `ProxyGroupId`（键）。
**这是一处系统性形态差异，不是五个孤立的多余属性。****

### 仍然 Unknown

**基线该不该重生成带访问器种类**（**应该，下一轮第一件事**）·
**那 5 个 `*Id` 该不该改成对象**（形态差异是 Observation，「该改」是设计判断，要看 UI 怎么绑）·
**`--extra` 那 63 条里有多少真多余**（报告自称 review list）

### 教训

> **这一轮我做了三件对的事：查工具、加开关、发现问题就报。以及一件错的事：上一轮把带字段的数据压成了不带字段的。**
> **而错的那件瞒了一轮 —— 因为它的症状是「0 个不匹配」，看起来像好消息。**
> **能保留字段的时候，不要为了好看把它压掉 —— 下游一旦读不到，会安静返回 0 而不是报错。**
"""

BACKLOG_ADD = """

## 判据 — 「形状 78」的证据源是抽样池（R885）

### 工具早已存在（第三次 §2.7c 生效）

**`tools/shape_audit.py` = 镜像访问器形状 ↔ 复刻件声明，`METRICS.md` 的「形状 78」是它的输出。本轮只加两个开关。**

### 证据源问题

```
抽样池（pe_strings.txt）: 102 types   -> mismatches 78
R883 基线（全量）       : 211 types   -> mismatches 0   ← 不是修好了
```

**池子少一半，且**少掉的那一半含 `Cybersole.Models.CreateModel`** → 「形状 78」从未包含它。**

### 而基线有缺陷（我上一轮引入的）

**格式 `<类型> TAB <数量> TAB <属性列表>` 丢了 `Getter`/`Setter`/`Property` 种类 →
`want_set` 依赖 `'Setter' in kinds` → 基线模式下永不成立 → **安静返回 0**。**

> **丢了字段的数据比没有数据更危险：78→0 看起来像修好了。**

### R884 那问题的答案

**`CreateModel` 12 个多余属性里：7 个有证据，5 个没有**
（`AccountId` `ProfileId` `ProxyGroupId` `TaskGroupId` `UseSmartActions`）
**四个是 `*Id` 外键 —— 镜像用 `ProxyGroup`（对象）而非 `ProxyGroupId`（键）→ 系统性形态差异。**

| 仍 Unknown | |
|---|---|
| **基线要不要重生成带访问器种类** | **下一轮第一件事** |
| 5 个 `*Id` 该不该改成对象 | 形态差异是 Observation；「该改」要看 UI |
| `--extra` 63 条里多少真多余 | 自称 review list |

**纪律**：**能保留字段时不要压掉 —— 下游读不到会安静返回 0，而不是报错。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R885", BLOCKER)
    ensure(RSTATUS, "R885", BLOCKER)
    ensure(RVERDICT, "第 885 轮", VERDICT)
    ensure(BACKLOG, "R885", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R885" not in h:
        h += ("\n## R885 补充 — 「形状 78」的证据源是抽样池（**改工具，未改产品代码**）\n\n"
              "**工具早已存在**：`tools/shape_audit.py`（第三次 §2.7c 生效）。本轮只加 `--baseline` 与 `--extra` 两个开关。\n"
              "**证据源问题**：抽样池 102 types / mismatches 78 vs R883 基线 211 types / **mismatches 0**。"
              "**池子少一半且含 `CreateModel` 缺席 → 「形状 78」从未包含它。**\n"
              "**而基线有缺陷（R883 引入）**：格式丢了 `Getter`/`Setter` 种类 → `want_set` 永不成立 → **安静返回 0**。**下一轮重生成带种类的基线。**\n"
              "**R884 那问题答了**：`CreateModel` 12 个多余属性中 7 个有证据 / 5 个没有（4 个是 `*Id` 外键 → **镜像用对象不用键，系统性差异**）。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R885"), (RSTATUS, "R885"), (RVERDICT, "第 885 轮"), (BACKLOG, "R885")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R885: the shape metric was computed from a sampled pool, and my baseline drops a field it needs\n\n"
         "R884 asked whether CreateModel's twelve extra properties came from XAML binding requirements or from me.\n"
         " Checking first, as section 2.7c says, found the tool already existed: shape_audit.py performs exactly this\n"
         "comparison, and the 'shape 78' figure in METRICS is its output.\n\n"
         "But its evidence comes from analysis/pe_strings.txt, the sampled dump. It reports one hundred and two types\n"
         "where the R883 baseline built from idautils.Strings holds two hundred and eleven. The pool is missing half,\n"
         " and the half it misses contains Cybersole.Models.CreateModel -- so the shape figure has never covered that\n"
         " type at all. Section 2.7b has recorded this trap four times; this is the first time it turned up inside a\n"
         "metric rather than inside a one-off search.\n\n"
         "Adding --baseline to read the full inventory produced a worse result and a more valuable one: mismatches fell\n"
         "from seventy-eight to zero. That is not a repair. The R883 format writes type, count and property list, and\n"
         "drops the accessor kind, so the check looking for Setter evidence can never fire against it. A file that loses\n"
         "a field is more dangerous than a missing file, because the symptom is a clean zero -- and a clean zero in a\n"
         "report reads as fixed. The defect is mine, introduced one round ago.\n\n"
         "The question that started the round has an answer now. Of CreateModel's twelve extra properties, seven have\n"
         "baseline evidence and five do not: AccountId, ProfileId, ProxyGroupId, TaskGroupId and UseSmartActions. Four\n"
         "of the five are foreign-key scalars, which points at a systematic difference rather than five separate slips:\n"
         " the image's CreateModel holds ProxyGroup as an object where the replica holds ProxyGroupId as a key.\n\n"
         "Unknown: whether to regenerate the baseline with accessor kinds, which it should and which means another IDA\n"
         " pass, so that is next round's first move; whether the five key-shaped properties ought to become objects,\n"
         " where the shape difference is an observation and the remedy depends on how the UI binds; and how many of the\n"
         " sixty-three --extra rows are genuinely surplus, since that report calls itself a review list.\n\n"
         "The lesson concerns compression. R883's dump collapsed a four-field record into three, and nothing broke at\n"
         "the time; it broke here, silently, in the direction that looks like success. Keep the field when it is free,\n"
         " because a downstream check that cannot see it returns zero rather than raising.\n\n"
         "Tool changed; no product code changed; suite carries at 1780."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
