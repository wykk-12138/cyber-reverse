"""Record R871: the rule's first real use, the doubt it raised, and the first step written."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### `where_is` 第一次真用：它先逼出一个疑问，再把疑问解掉（R871）

**目标：R850 判为「可写」的 `GetOrders`。按 §2.7c 先跑：**

```
python tools\\where_is.py GetOrders   -> 12 files
    implementation: （无）
    analysis:       CandidateSteps.cs · PopMartStepMap.cs · StoreFlowSteps.cs
    test:           FlowSequenceTests · PopMartStepMapTests · StoreFlowDigestTests
    doc:            VERDICT · BINDING_BACKLOG · ENDPOINT_FAMILIES · docs/baseline/*
```

**implementation 组空 → 确认没人实现，可以写。而 analysis 组里的 `CandidateSteps.cs` 逼出一个疑问。**

### 那个疑问

`CandidateSteps.cs` 写着：

```
104 GetAccessToken / CartApiObjectCreate / GetOrders        (three classes collide)
```

> **ordinals are per class, so a bare ordinal cannot say which class owns a name.**

**如果 104 上三个名字撞号，那「`GetOrders` 是 PopMart 的第 104 步」这个归属就不牢 —— 而整条 PopMart 序列都建立在它上面。**

### 核出来的答案：撞号是真的，但归属不模糊

```
GetAccessToken>d__104    @0x1433737e2  → 同段 CartApiObjectCreate>d__105 · AddToCartGraphQL>d__106
GetOrders>d__104         @0x14337c7e5  → 同段 GetInstoreOrders>d__105 · StartDrawFlow>d__115
```

**ordinal 104 出现两次，在**两条不同的 blob**里 —— 是两个不同类各自的第 104 个方法。**

**所以 `CandidateSteps` 那句警告说的是「裸 ordinal 扫描分不清名字来自哪条 blob」，
而不是「`GetOrders` 归属不明」。`GetOrders` 和 `104` 在**同一个字面量**里，归属是直接的。**

**这条值得记，因为下次再看到「N 个类撞号」时，第一反应不该是「归属不可知」，
而是「它们是同一个字面量还是不同字面量」。**

### 写出来的东西

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | 新增 `virtual GetOrdersAsync` —— **默认显式失败**（不是静默成功） |
| `PopMartFlow.cs` | `override GetOrdersAsync` → `GET Origin + PopMartEndpoints.OrderList`，存进 `Session.Vars["orders"]` |
| `FlowSequenceTests.cs` | `165 → 166`（map）、`0 → 1`（coverage），测试改名 |

**响应体整份存下来，不解析** —— 响应 schema 没有证据，解析就是编一个出来。

### 测试自己红了两次，两次都对

| 次 | 为什么红 | 处理 |
|---|---|---|
| 1 | `implementable` 从 0 变 1 | 按该测试注释里预先写的规则：改成新数字并说明加了什么 |
| 2 | `map.Count` 从 165 变 166（我加了基类虚方法） | 两个数一起钉住：`166` + `24` + `1` |

**第二个失败是个好信号：加一个虚方法会动 map，写一个步骤会动 coverage。
两个数一起断言，就能区分「加了虚方法但没人用」和「写了一步」。**
"""

if "`where_is` 第一次真用：它先逼出一个疑问，再把疑问解掉（R871）" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: first step appended")

BLOCKER = """

---

## 295. 第一步写出来了：`GetOrders`，coverage **0 → 1**

> R871。**改了产品代码。** 套件 **1773 通过 / 0 失败 / 0 跳过**。

### 一、`where_is` 第一次真用

```
python tools\\where_is.py GetOrders -> 12 files
    implementation: （无）              ← 确认没人实现
    analysis:       CandidateSteps.cs · PopMartStepMap.cs · StoreFlowSteps.cs
```

**implementation 组空，所以可以写。而 analysis 组把我推到 `CandidateSteps.cs`，那里有一句让我停下来核的话。**

### 二、它逼出的疑问

```
104 GetAccessToken / CartApiObjectCreate / GetOrders        (three classes collide)
```

> ordinals are per class, so a bare ordinal cannot say which class owns a name.

**如果 104 撞号，那「`GetOrders` 是 PopMart 第 104 步」就不牢 —— 整条 PopMart 序列都靠它。**

### 三、核完：撞号真，归属不模糊

```
GetAccessToken>d__104  @0x1433737e2 → CartApiObjectCreate>d__105 · AddToCartGraphQL>d__106
GetOrders>d__104       @0x14337c7e5 → GetInstoreOrders>d__105 · StartDrawFlow>d__115
```

**104 出现两次，在**两条不同 blob** 里 —— 两个类各自的第 104 个方法。**

**`CandidateSteps` 说的是「裸 ordinal 分不清名字来自哪条 blob」，
不是「`GetOrders` 归属不明」。名字和 ordinal 在同一个字面量里，归属是直接的。**

**可迁移的一条：看到「N 个类撞号」，要问的是「同一个字面量还是不同字面量」，
不是直接判「归属不可知」。**

### 四、写了什么

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | `virtual GetOrdersAsync` —— **默认显式失败** |
| `PopMartFlow.cs` | `override` → `GET Origin + PopMartEndpoints.OrderList` → `Session.Vars["orders"]` |
| `FlowSequenceTests.cs` | map `165→166`、coverage `0→1`、用例改名 |

**响应体整份存下，不解析 —— schema 没证据，解析就是编。**

**基类默认**失败**而不是成功**：一个没有订单端点的店必须说出来。
**静默成功正是 R869 那个假成功的形态，不在新加的步骤里重演。**

### 五、测试红了两次，两次都有信息

| 次 | 原因 | 处理 |
|---|---|---|
| 1 | `implementable` 0 → 1 | 按该测试注释里**预先写好的规则**：改数字并说明加了什么 |
| 2 | `map.Count` 165 → 166（加了基类虚方法） | 三个数一起钉：`166` / `24` / `1` |

**第二次是好信号：加虚方法动 map，写步骤动 coverage。
两个数一起断言就能区分「加了虚方法没人用」与「写了一步」—— 这正是 R858 那个死字段的反面。**

### 六、验证

```
python tools\\where_is.py GetOrders      -> implementation 组为空
ida.py str "GetAccessToken>d__104"      -> 1 match @0x1433737e2（另一条 blob）
ida.py str "GetOrders>d__104"           -> 1 match @0x14337c7e5（PopMart 那条）
D:\\tools\\dotnet8\\dotnet.exe build ...  -> 0 错误
test --filter FlowSequenceTests         -> 7 通过 / 0 失败
python tools\\metrics_report.py          -> 1773 通过 / 0 失败 / 0 跳过
```

### 七、仍然 Unknown

- **`OrderList` 的响应结构**：**Unknown** —— 所以整份存、不解析。
  **要解析它得先有证据（原版怎么用这个响应），否则就是编 schema。**
- **其余 23 步的请求形状**：**Unknown** —— R850 的边界没变（11 个缺形状，3 个可写里现在写了 1 个）。
- **`GetInstoreOrders`（105）能不能同法写**：**likely** —— 它同段、`PopMartEndpoints` 里可能有对应的常量，
  **本轮没查。下一轮第一件事就是 `where_is GetInstoreOrders`。**

### 八、教训

**这一轮的两件事都是规则带来的，不是我想到的：**

**① `where_is` 把 `CandidateSteps.cs` 推到我面前，而那里有一句会让我判错归属的话；
② 我没先写代码，先核了那句话。**

**而核它的成本是两条 `ida.py str`。如果不核，我写出来的 `GetOrders`
会带着一个我没意识到的归属假设 —— 而那个假设是整条序列的地基。**

**所以 §2.7c 的用处不只是「避免重复品」，还有「在读到的文件里发现自己的假设」。**
"""

VERDICT = """

---

## 第 871 轮：第一步写出来了 —— `GetOrders`，coverage 0 → 1

### `where_is` 第一次真用

```
python tools\\where_is.py GetOrders -> 12 files
    implementation: （无）      ← 确认没人实现，可以写
    analysis:       CandidateSteps.cs · PopMartStepMap.cs · StoreFlowSteps.cs
```

**而 analysis 组把我推到 `CandidateSteps.cs`，那里有一句话让我停下来核。**

### 它逼出的疑问，和核出来的答案

```
104 GetAccessToken / CartApiObjectCreate / GetOrders   (three classes collide)
```

**核：**

```
GetAccessToken>d__104  @0x1433737e2 → CartApiObjectCreate>d__105 · AddToCartGraphQL>d__106
GetOrders>d__104       @0x14337c7e5 → GetInstoreOrders>d__105 · StartDrawFlow>d__115
```

**104 出现两次，在**两条不同 blob** 里。撞号是真的，但归属不模糊 ——
名字和 ordinal 在同一个字面量里。**

> **可迁移：看到「N 个类撞号」，要问「同一个字面量还是不同字面量」，不是直接判「归属不可知」。**

### 写了什么

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | `virtual GetOrdersAsync` —— **默认显式失败** |
| `PopMartFlow.cs` | `override` → `GET Origin + OrderList` → `Session.Vars["orders"]` |
| `FlowSequenceTests.cs` | map `165→166`、coverage `0→1`、改名 |

**响应体整份存下不解析（schema 没证据，解析就是编）。**
**基类默认**失败**——静默成功是 R869 假成功的形态，不在新步骤里重演。**

### 测试红两次，两次都有信息

| 次 | 原因 | 处理 |
|---|---|---|
| 1 | coverage 0→1 | 按预先写好的规则改数字并说明 |
| 2 | map 165→166 | 三个数一起钉：`166`/`24`/`1` |

**第二次是好信号：加虚方法动 map，写步骤动 coverage —— 一起断言就能区分「加了没人用」与「写了一步」，正是 R858 死字段的反面。**

### 仍然 Unknown

**`OrderList` 的响应结构**（所以整份存）· **其余 23 步的请求形状**（R850 边界未变）·
**`GetInstoreOrders`(105) 能否同法写** —— 同段、可能有对应常量，**未查；下一轮第一件事就是 `where_is GetInstoreOrders`**

### 教训

> **这一轮两件事都是规则带来的，不是我想到的：`where_is` 把会让我判错归属的文件推到我面前；而我没先写代码，先核了那句话。**
> **核它的成本是两条 `ida.py str`。不核的话，`GetOrders` 会带着一个我没意识到的归属假设 —— 而那是整条序列的地基。**
> **所以 §2.7c 的用处不只是「避免重复品」，还有「在读到的文件里发现自己的假设」。**
"""

BACKLOG_ADD = """

## 优先级 ① — 第一步写出来（R871，**已改产品代码**）：`GetOrders`，coverage 0→1

**`where_is GetOrders` → implementation 组为空（确认没人实现）；analysis 组指向 `CandidateSteps.cs`。**

### 它逼出的疑问与答案

```
104 GetAccessToken / CartApiObjectCreate / GetOrders   (three classes collide)
```
**核：`GetAccessToken>d__104`@`0x1433737e2` 与 `GetOrders>d__104`@`0x14337c7e5` 在**两条不同 blob**。
→ 撞号真，归属不模糊（名字与 ordinal 同字面量）。**

### 改动

| 文件 | 改动 |
|---|---|
| `StoreFlow.cs` | `virtual GetOrdersAsync`，**默认显式失败** |
| `PopMartFlow.cs` | `override` → `GET Origin + OrderList` → `Session.Vars["orders"]` |
| `FlowSequenceTests.cs` | `166`/`24`/`1` 三数一起钉 |

**响应体整份存不解析（无 schema 证据）。套件 1773 通过 / 0 失败。**

### 测试机制验证

**红两次都对：coverage 0→1（按预写规则改数字）· map 165→166（加虚方法）。
两数一起断言可区分「加虚方法没人用」与「写一步」—— R858 死字段的反面。**

| 仍 Unknown | |
|---|---|
| `OrderList` 响应结构 | 所以整份存 |
| 其余 23 步请求形状 | R850 边界未变 |
| `GetInstoreOrders`(105) | 同段、可能有常量 — **下一轮第一件事 `where_is`** |

**纪律**：**§2.7c 不只避免重复品，还能在读到的文件里发现自己没意识到的假设。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R871", BLOCKER)
    ensure(RSTATUS, "R871", BLOCKER)
    ensure(RVERDICT, "第 871 轮", VERDICT)
    ensure(BACKLOG, "R871", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R871" not in h:
        h += ("\n## R871 补充 — 第一步写出来（**已改产品代码**）：`GetOrders`，coverage 0→1\n\n"
              "**`where_is GetOrders` → implementation 组空（确认没人实现）**，analysis 组指向 `CandidateSteps.cs`，"
              "那里写着「ordinal 104 被三个类共用」。**核：`GetAccessToken>d__104`@`0x1433737e2` 与 `GetOrders>d__104`@`0x14337c7e5` "
              "在两条不同 blob → 撞号真，归属不模糊。**\n"
              "**写了**：`StoreFlow.virtual GetOrdersAsync`（默认显式失败）+ `PopMartFlow` override → `GET OrderList` → `Session.Vars[\"orders\"]`。"
              "**响应体整份存不解析（无 schema 证据）。**\n"
              "**测试三数一起钉：`map=166` / `sequence=24` / `implementable=1`。套件 1773 通过 / 0 失败。**\n"
              "**下一轮第一件事：`where_is GetInstoreOrders`（105，同段，可能有常量）。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R871"), (RSTATUS, "R871"), (RVERDICT, "第 871 轮"), (BACKLOG, "R871")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R871: the first step written since the mechanism, and the rule raised a doubt before the code did\n\n"
         "where_is GetOrders reported twelve files with an empty implementation group, confirming nothing implements it,"
         " and an analysis group containing CandidateSteps.cs. That file says ordinal 104 is shared by GetAccessToken,"
         " CartApiObjectCreate and GetOrders across three classes, with the warning that ordinals are per class and a"
         " bare ordinal cannot say which class owns a name.\n\n"
         "If that were so, GetOrders being Pop Mart's hundred-and-fourth step would be uncertain, and the whole of Pop"
         " Mart's sequence rests on it. Checking costs two string reads. GetAccessToken at d__104 sits in one blob with"
         " CartApiObjectCreate at 105 and AddToCartGraphQL at 106, while GetOrders at d__104 sits in a different blob"
         " with GetInstoreOrders at 105 and StartDrawFlow at 115. Ordinal 104 occurs twice in two different blobs, so"
         " the collision is real and the attribution is not ambiguous: the name and its ordinal share one literal.\n\n"
         "So GetOrders is written. StoreFlow gains a virtual GetOrdersAsync whose default fails explicitly rather than"
         " succeeding, because a store with no order endpoint must say so and a silent success is the shape this project"
         " spent R869 removing. PopMartFlow overrides it to fetch PopMartEndpoints.OrderList and store the body whole.\n"
         " It is not parsed, because the response schema has no evidence and parsing it would mean inventing one.\n\n"
         "The tests went red twice and both times informatively. First the coverage assertion failed as the mechanism\n"
         " intended, going from zero to one; the test's own comment had pre-authorised the fix, which is to write the new"
         " number and say what arrived rather than delete the assertion. Then the map count failed, because adding a"
         " virtual to StoreFlow moves it from 165 to 166. Both numbers are now pinned together with the sequence length,\n"
         " so a virtual added and never used moves one and a written step moves the other -- the inverse of R858's dead\n"
         " field, where a name existed with nothing behind it.\n\n"
         "Unknown: what OrderList returns, which is why the body is kept unparsed; the request shapes for the remaining"
         " twenty-three steps, unchanged from R850; and whether GetInstoreOrders at 105 can be written the same way, since"
         " it shares the blob and PopMartEndpoints may already name it -- unchecked, and the first thing next round.\n\n"
         "The lesson is that the rule earned its keep twice over in one round. It surfaced the file that would have made"
         " me judge the attribution wrong, and I read that file before writing rather than after. The cost of checking\n"
         " was two string lookups; the cost of not checking would have been a step carrying an assumption I never"
         " noticed, sitting underneath an entire sequence.\n\n"
         "Product code changed; suite green at 1773."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
