"""Record R1020: the two Inferred rows said two different things, and the column now says which."""

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
### 一个值装了两件相反的事 —— 现在分成一列（R1020）

**R1019 收尾说「两个 `Inferred` 的性质不同，而那个区别只在注释里，下一轮该变成结构」。做了。**

### ① 那两行说的是两件不同的事

| vendor | marker | 镜像 | 真实含义 |
|---|---|---|---|
| **imperva** | `_Incapsula_Resource` | **0**（六种拼写全 0） | **这个厂商在产物里完全不存在** |
| **perimeterx** | `px-captcha` | **0**（而 cookie 名 4 条有） | **这个厂商在，但它没有页面级字面量** |

**→ 两者都是 `Inferred`，而它们**要做的下一件事相反**：**
- imperva：**查原版到底有没有处理它**（六种拼写全 0 是个强信号，而它不等于「没处理」）
- perimeterx：**给一个确实被处理的东西找一个能在响应体里查的 marker**

**→ 而一个读者扫那张表只看到 `Inferred` 一个词。**

### ② 所以加了一列，而不是改那个枚举

**`MarkerSource` 保持两个值（`ImageLiteral` / `Inferred`）—— 它回答「这个串是不是镜像的」。
新加 `Gap` 回答另一个问题：「如果不是，为什么」：**

```csharp
public enum Gap { None, VendorAbsent, NoPageMarker }
```

**→ 六行填值：cloudflare · kasada · datadome · queue-it 是 `None`；imperva 是 `VendorAbsent`；
perimeterx 是 `NoPageMarker`。**

**→ 为什么不把两者塞进 `MarkerSource`：那一个枚举已经在回答一个封闭的问题（是/不是镜像的），
把「为什么不是」并进去会让每个 `MarkerFrom == ImageLiteral` 的判断都得想一下它是不是也开始编码原因。**

### ③ 而守卫钉住两列的一致性（4 条）

| 守卫 | 断言 |
|---|---|
| `TheTwoInferredRowsSayWhyTheyAreInferred` | imperva=`VendorAbsent` · perimeterx=`NoPageMarker` · 其余全 `None` |
| `NoGapImpliesAnImageLiteral` | `Gap.None` ⇒ `ImageLiteral`（两列不能自相矛盾） |
| `AGapImpliesAnInferredMarker` | 反方向同一条 |
| `TheAuditCanBeGroupedByReason` | 能在一处按原因分组取出两个集合 |

**→ 第 2、3 条是双向的：一列说「没缺口」而另一列说「我编的」是不可能同时成立的。
→ 而第 4 条保证那一列**有用** —— 一列只能在注释里被读到，就还是注释。**

### ④ 数字

| 度量 | R1019 | **R1020** |
|---|---|---|
| 套件 | 2222 / 0 | **2226 / 0 / 0（+4 缺口守卫）** |
| 产物陈旧度 | 3 / 3,531 | **3 / 3,552** |
| 函数数 | 174,336 | **174,336** |
| **`Row` 的列** | 6 | **7（+`Gap`）** |
| **`Inferred` 的可分辨原因** | 0（一个词盖两件事） | **2（`VendorAbsent` · `NoPageMarker`）** |
| **两列一致性守卫** | 0 | **4（双向）** |

### 教训

> **一张表里一个词盖住两件事，读表的人就没法据它行动 —— 而写表的人（我）会以为自己已经记录了区别，
> 因为区别在注释里。**
> **→ 而把区别变成列的成本是**一个枚举加六个填值**，收益是下一轮不需要重新推一遍那两个 vendor
> 到底差在哪。**
> **→ 而守卫里那两条**双向**的最要紧：一列说「没缺口」而另一列说「我编的」是自相矛盾，
> 而加列的时候最容易只写一个方向的检查。**
"""

if "一个值装了两件相反的事" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1020 轮：一个值装了两件相反的事 —— 现在分成一列

### ① 那两行说的是两件不同的事

| vendor | marker | 镜像 | 真实含义 |
|---|---|---|---|
| **imperva** | `_Incapsula_Resource` | **0**（六种拼写全 0） | **这个厂商在产物里完全不存在** |
| **perimeterx** | `px-captcha` | **0**（cookie 名 4 条有） | **这个厂商在，但没有页面级字面量** |

**→ 两者都是 `Inferred`，而要做的下一件事**相反**：
imperva 要查原版是否处理它；perimeterx 要给一个确实被处理的东西找页面级 marker。
→ 而一个读者扫那张表只看到 `Inferred` 一个词。**

### ② 所以加了一列，而不是改那个枚举

```csharp
public enum Gap { None, VendorAbsent, NoPageMarker }
```

**→ `MarkerSource` 保持两个值（它回答「这个串是不是镜像的」）；`Gap` 回答「如果不是，为什么」。**
**→ 六行：cloudflare · kasada · datadome · queue-it = `None`；imperva = `VendorAbsent`；
perimeterx = `NoPageMarker`。**

**→ 不并进 `MarkerSource` 的理由：那枚举已在回答一个封闭问题，把「为什么不是」并进去会让每个
`MarkerFrom == ImageLiteral` 的判断都得想一下它是否也开始编码原因。**

### ③ 4 条守卫钉住两列一致

| 守卫 | 断言 |
|---|---|
| `TheTwoInferredRowsSayWhyTheyAreInferred` | imperva=`VendorAbsent` · perimeterx=`NoPageMarker` · 其余 `None` |
| `NoGapImpliesAnImageLiteral` | `Gap.None` ⇒ `ImageLiteral` |
| `AGapImpliesAnInferredMarker` | 反方向 |
| `TheAuditCanBeGroupedByReason` | 能在一处按原因分组 |

**→ 第 2、3 条是**双向**的：一列说「没缺口」而另一列说「我编的」不可能同时成立。
→ 第 4 条保证那一列**有用** —— 只能在注释里读到的列还是注释。**

### ④ 数字

| 度量 | R1019 | **R1020** |
|---|---|---|
| 套件 | 2222 / 0 | **2226 / 0 / 0（+4）** |
| 产物陈旧度 | 3 / 3,531 | **3 / 3,552** |
| 函数数 | 174,336 | **174,336** |
| **`Row` 的列** | 6 | **7（+`Gap`）** |
| **`Inferred` 的可分辨原因** | 0 | **2** |
| **两列一致性守卫** | 0 | **4（双向）** |

### 教训

> **一张表里一个词盖住两件事，读表的人就没法据它行动 —— 而写表的人会以为自己已经记录了区别，
> 因为区别在注释里。**
> **→ 加列成本是一个枚举加六个填值，收益是下一轮不必重推那两个 vendor 差在哪。**
> **→ 而双向守卫最要紧：加列时最容易只写一个方向的检查。**
"""

BACKLOG_ADD = """

## 优先级 ② — **`Gap` 列：把两个 `Inferred` 的相反原因变成结构**（R1020）

### 问题

**imperva 与 perimeterx 都标 `Inferred`，而含义相反：**

| vendor | 镜像 | 含义 | 下一步 |
|---|---|---|---|
| imperva | 六拼写全 **0** | **厂商不在产物里** | 查原版是否处理它 |
| perimeterx | `px-captcha` 0，cookie 名 4 条有 | **厂商在，无页面级字面量** | 找一个响应体里能查的 marker |

**→ 一个词盖两件事，读者无法据表行动。**

### 解

```csharp
public enum Gap { None, VendorAbsent, NoPageMarker }
```

**`Row` 第 7 列。cloudflare/kasada/datadome/queue-it = `None`；imperva = `VendorAbsent`；
perimeterx = `NoPageMarker`。**

**不并进 `MarkerSource`**：那枚举回答封闭问题（是/不是镜像的），并入「为什么不是」会污染所有
`MarkerFrom == ImageLiteral` 的判断。

### 4 条守卫（`VendorGapTests`）

`TheTwoInferredRowsSayWhyTheyAreInferred` · **`NoGapImpliesAnImageLiteral`（双向之一）** ·
**`AGapImpliesAnInferredMarker`（双向之二）** · `TheAuditCanBeGroupedByReason`

### 数字

**套件 2226（+4）· 陈旧度 3 / 3,552 · 函数数 174,336 · Row 列 6 → 7 · Inferred 可分辨原因 0 → 2**

| 仍 Unknown | |
|---|---|
| imperva 是否被原版处理 | 六拼写全 0，是强信号不等于否定 |
| perimeterx 的页面级 marker | 镜像无 |

**纪律**：一个词盖两件事，写表的人会以为已经记录了区别。
"""

BLOCKER = """

---

## 444. **一个值装了两件相反的事 —— 现在分成一列（`Gap`）**

> R1020。**改 1 个源文件 + 加 1 个测试文件。** 套件 **2226 通过 / 0 失败 / 0 跳过**。

### 一、那两行说的是两件不同的事

| vendor | marker | 镜像 | 真实含义 |
|---|---|---|---|
| **imperva** | `_Incapsula_Resource` | **0**（六种拼写全 0） | **这个厂商在产物里完全不存在** |
| **perimeterx** | `px-captcha` | **0**（而 cookie 名 4 条有） | **这个厂商在，但它没有页面级字面量** |

**→ 两者都是 `Inferred`，而它们**要做的下一件事相反**：**

- imperva：**查原版到底有没有处理它**（六种拼写全 0 是个强信号，而它不等于「没处理」）
- perimeterx：**给一个确实被处理的东西找一个能在响应体里查的 marker**

**→ 而一个读者扫那张表只看到 `Inferred` 一个词。**

### 二、所以加了一列，而不是改那个枚举

**`MarkerSource` 保持两个值（`ImageLiteral` / `Inferred`）—— 它回答「这个串是不是镜像的」。
新加 `Gap` 回答另一个问题：「如果不是，为什么」：**

```csharp
public enum Gap { None, VendorAbsent, NoPageMarker }
```

**→ 六行填值：cloudflare · kasada · datadome · queue-it 是 `None`；imperva 是 `VendorAbsent`；
  perimeterx 是 `NoPageMarker`。**

**→ 为什么不把两者塞进 `MarkerSource`：那一个枚举已经在回答一个封闭的问题（是/不是镜像的），
  把「为什么不是」并进去会让每个 `MarkerFrom == ImageLiteral` 的判断都得想一下它是不是也开始编码原因。**

### 三、4 条守卫钉住两列的一致性

| 守卫 | 断言 |
|---|---|
| `TheTwoInferredRowsSayWhyTheyAreInferred` | imperva=`VendorAbsent` · perimeterx=`NoPageMarker` · 其余全 `None` |
| `NoGapImpliesAnImageLiteral` | `Gap.None` ⇒ `ImageLiteral` |
| `AGapImpliesAnInferredMarker` | 反方向同上 |
| `TheAuditCanBeGroupedByReason` | 能在一处按原因分组取出两个集合 |

**→ 第 2、3 条是双向的：一列说「没缺口」而另一列说「我编的」是不可能同时成立的。
→ 而第 4 条保证那一列**有用** —— 一列只能在注释里被读到，就还是注释。**

### 四、数字

| 度量 | R1019 | R1020 |
|---|---|---|
| 套件 | 2222 / 0 | **2226 / 0 / 0（+4 缺口守卫）** |
| 产物陈旧度 | 3 / 3,531 | **3 / 3,552** |
| 函数数 | 174,336 | **174,336** |
| **`Row` 的列** | 6 | **7（+`Gap`）** |
| **`Inferred` 的可分辨原因** | 0（一个词盖两件事） | **2（`VendorAbsent` · `NoPageMarker`）** |
| **两列一致性守卫** | 0 | **4（双向）** |

### 五、验证

```
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~VendorGap|~VendorWiring|~CaptchaDelivery" -m:1 -> 16 通过
python tools/metrics_report.py -> 完整套件 exit 0  2226 / 0 / 0
```

### 六、仍然 Unknown

- **imperva 是否被原版处理**：**六种拼写全 0** —— 强信号，但不等于否定。
- **perimeterx 的页面级 marker**：**镜像无**。

### 七、教训

**一张表里一个词盖住两件事，读表的人就没法据它行动 —— 而写表的人（我）会以为自己已经记录了区别，
因为区别在注释里。**

**→ 而把区别变成列的成本是**一个枚举加六个填值**，收益是下一轮不需要重新推一遍那两个 vendor
  到底差在哪。**
**→ 而守卫里那两条**双向**的最要紧：一列说「没缺口」而另一列说「我编的」是自相矛盾，
  而加列的时候最容易只写一个方向的检查。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1020", BLOCKER)
    ensure(RSTATUS, "R1020", BLOCKER)
    ensure(RVERDICT, "第 1020 轮", VERDICT)
    ensure(BACKLOG, "R1020", BACKLOG_ADD)

    note = (
        "\n## R1020 补充 — **`Gap` 列：把两个 `Inferred` 的相反原因变成结构**（套件 2226）\n\n"
        "**问题**：imperva 与 perimeterx 都标 `Inferred`，而含义相反 ——\n"
        "imperva **厂商不在产物里**（六拼写全 0），perimeterx **厂商在但无页面级字面量**（cookie 名 4 条有）。\n"
        "→ 下一步动作相反，而读者扫表只看到一个词。\n\n"
        "**解**：`public enum Gap { None, VendorAbsent, NoPageMarker }`，`Row` 第 7 列。\n"
        "cloudflare/kasada/datadome/queue-it = `None` · imperva = `VendorAbsent` · perimeterx = `NoPageMarker`。\n"
        "**不并进 `MarkerSource`**：那枚举回答封闭问题，并入「为什么不是」会污染所有 `MarkerFrom == ImageLiteral` 的判断。\n\n"
        "**4 条守卫**（`VendorGapTests`）：两行原因 · **`NoGapImpliesAnImageLiteral`（双向一）** ·\n"
        "**`AGapImpliesAnInferredMarker`（双向二）** · 能按原因分组。\n\n"
        "数字：套件 2226（+4）· 陈旧度 3 / 3,552 · 函数数 174,336 · Row 列 6 → **7** · Inferred 可分辨原因 0 → **2**。\n\n"
        "纪律：**一个词盖两件事，写表的人会以为已经记录了区别（因为区别在注释里）。**\n\n"
        "下一轮：按 `Gap` 分流 —— imperva 查原版是否处理它（六拼写全 0 的强信号需要第二个证据）；\n"
        "perimeterx 找一个页面级 marker。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1020" not in h:
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
             for p, k in ((RBLOCK, "R1020"), (RSTATUS, "R1020"), (RVERDICT, "第 1020 轮"), (BACKLOG, "R1020")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1020: one word was covering two opposite things, so the audit gets a column\n\n"
         "R1019 ended by noting that two rows read Inferred for opposite reasons and that the difference only existed in\n"
         " prose. This round makes it a column.\n\n"
         "Imperva appears in the artifact under none of its six spellings, so the next question is whether the original\n"
         " handles it at all. PerimeterX is present with four cookie-side literals and simply has nothing page-level to\n"
         " grep for, so the next question is what marker to use for a vendor it demonstrably handles. Those are different\n"
         " moves, and a reader scanning the table saw one word.\n\n"
         "MarkerSource keeps its two values, because it answers a closed question -- is this string the image's. A second\n"
         " column answers the follow-up: if not, why. Gap has None, VendorAbsent and NoPageMarker, filled across the six\n"
         " rows. Folding the reason into MarkerSource would have been smaller and worse: every existing comparison\n"
         " against ImageLiteral would then have to consider whether it was also encoding a reason.\n\n"
         "Four guards pin it, and the pair that matters is the bidirectional one. NoGapImpliesAnImageLiteral and\n"
         "AGapImpliesAnInferredMarker say the two columns cannot contradict each other in either direction -- a row\n"
         " claiming no gap while its marker is invented is not a state that can exist. The fourth guard checks the column\n"
         " can actually be used to group the audit, because a column readable only in a comment is still a comment.\n\n"
         "Figures: suite 2222 to 2226, freshness three files and 3,552 lines, count 174,336, Row grows from six columns\n"
         " to seven, and the inferred rows go from one indistinguishable reason to two named ones.\n\n"
         "Unknown: whether the original handles Imperva, for which six absent spellings are a strong signal and not a\n"
         " proof, and a page-level marker for PerimeterX.\n\n"
         "The lesson is that when one word covers two things a reader cannot act on the table, while the person who wrote\n"
         " it believes the distinction is recorded because it is in the prose beside it -- and that when adding a column,\n"
         " the tempting guard checks only one direction.\n\n"
         "One source file and one test file changed; suite green at 2226."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()