"""Record R862: reading the backlog surfaces a ceiling recorded at R504 and never lifted."""

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
### 读 backlog 读到一个 **R504 就记下、从没被抬走的天花板**（R862）

`replica/docs/BINDING_BACKLOG.md` 第 25–78 行，42 条「复刻件里既无方法也无属性」的成员分三类，
**其中 B 桶 31 条的性质不是「没做」，是「用现有工具拿不到行为证据」：**

| 想拿的东西 | 为什么拿不到 |
|---|---|
| 描述符 → 引用它的注册代码 | **描述符无 xref**（`0x14320c54d` → 0 · `0x1436389fc` → 0） |
| 属性 setter 做什么 | **编译期内联，没有独立函数体** |
| `ICommand` 的行为 | **藏在委托初始化点，该点靠类型信息定位，类型信息也无 xref** |

**R504 的原话：**

> 这与 `PARITY_CLAIMS.md` 的 C7c（每个函数功能相等）一直是 Unknown 是同一件事。
> 要么接受"结构对等、行为 Unknown"，要么换一条完全不同的证据路线（例如运行期差分）——
> **运行期路线需要登录凭据**，那是 goal 允许停下来等 YG 的两件事之一。

### 所以「每个函数功能相等」这条判据的实际状态

| 层 | 能到 | 靠什么 |
|---|---|---|
| 函数数量对等 | **61.96%**（R831，`.pdata` 计数） | 可复算 |
| 结构对等（成员/类型/形状） | **多数已清** | `bind_diff` / `bind_scope` / `shape_audit` |
| **每函数功能相等** | **Unknown** | **静态路线已断（R504）；运行期需凭据** |

**这三层不是同一种完成度。前两层可以靠静态分析推到接近 100%，第三层不行。**

### 这不是新发现，但它是 (f) 与 (a) 之间那个一直没被写清的边界

**判据 (a) 说「类型级缺口、类型缺失 → 0」。这一条**能**做到，因为它问的是存在性。**

**判据的正文另有「每个函数功能相等」。这一条**做不到**，而且不是努力不够 —— 是 NativeAOT
把 setter 内联、把描述符做成无 xref 的数据，静态工具在原理上够不到。**

**所以完成判据里混了两种东西：存在性（可达）与行为（不可达，除非运行期）。**
"""

if "读 backlog 读到一个 **R504 就记下、从没被抬走的天花板**（R862" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: ceiling appended")

BLOCKER = """

---

## 286. backlog 里躺着一个 **R504 的天花板**：行为证据静态拿不到

> R862。未改产品代码。**按 R861 立的规则先读 `BINDING_BACKLOG.md`，读出来的就是这个。**

### 一、B 桶 31 条的性质

`BINDING_BACKLOG.md` L38–78：

| 想拿的东西 | 为什么拿不到 |
|---|---|
| 描述符 → 引用它的注册代码 | **描述符无 xref**（`0x14320c54d` → 0 · `0x1436389fc` → 0） |
| 属性 setter 做什么 | **编译期内联，没有独立函数体** |
| `ICommand` 的行为 | **藏在委托初始化点，靠类型信息定位，而类型信息也无 xref** |

**R504 已把它连到 `PARITY_CLAIMS.md` C7c（每个函数功能相等）一直是 Unknown，
并指出唯一替代路线是**运行期差分**，而那条需要登录凭据。**

### 二、所以那条判据分成了两层

| 目标 | 可达性 | 现状 |
|---|---|---|
| 函数**数量**对等 | **可复算** | `.pdata` 61.96%（R831） |
| 结构对等（成员 / 类型 / 形状） | **可达** | 多数已清，余项在 `docs/METRICS.md` |
| **每个函数**功能相等** | **静态不可达** | **Unknown，R504 起** |

**这不是「还差多少轮」，是「这条路到头了」。**
**NativeAOT 把 setter 内联、把描述符做成无 xref 的数据 —— 静态工具在原理上够不到。**

### 三、这解释了 R827/R828 那两轮的失败

R827 查到 `HandleResponse` 总提及 = 1，R828 记「`0 xrefs` 不是证据」。
**那两轮想走的就是这条路 —— 从名字找代码地址。而 R504 早就记了它为什么断。**

**所以 R824–R828 那五轮是在重试一条已记为断的路。**
**（不过 R854 用另一条路给了 `HandleResponse` 答案：它在 `0x14345abb1` 那条序列里，邻居是 `GetKasada`。
所以「静态不可达」不等于「什么都不知道」—— 是指**行为**拿不到，**位置**可以靠相邻运行推。）**

### 四、这一轮该向 YG 提的问题

**goal 允许停下来等 YG 的两件事之一是**原版登录凭据**。而它正是这条唯一剩余路线的入口。**

**要问的是一句具体的话，不是「要不要凭据」：**

> **「每个函数功能相等」这一条，静态路线 R504 已证断（setter 内联、描述符无 xref）。
> 剩下的路只有运行期差分：让原版跑一次某个动作，看它改了什么。
> 这条路要原版能登录。你愿意给凭据让我走这条路吗？
> 不愿意的话，我按「结构对等 + 行为 Unknown」收尾，并把这条边界写进完成判据的每一处。」

**这不是要授权，是要一个取舍。** 而这个取舍只有 YG 能定。

### 五、验证

```
replica\\docs\\BINDING_BACKLOG.md L25–L78
  A 硬约束 7（平台差异，不是缺口）
  B 需设计 31（实测：静态拿不到行为证据，R504）
  C 已做 4
  R504: xrefs to 0x14320c54d -> 0 · xrefs to 0x1436389fc -> 0
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **运行期差分的具体成本**：**Unknown** —— 需要知道原版登录一次之后，能不能只跑单个动作。
- **凭据之外还有没有第三路线**：**Unknown** ——
  R504 列了两条（静态 / 运行期），**没列第三条**。**而 R854 的「相邻运行」确实是第三种（只能定位，不能取行为）。**
- **`ICommand` 的委托初始化点是否真的完全无 xref**：**Unknown** —— R504 查的是两块描述符，不是全部。

### 七、教训

**R861 我立了规则「查一个成员之前先在 backlog 里搜它的名字」。**
**这一轮照做，读出来的不是一个成员的问题，是整个判据的天花板。**

**而更值得记的是：这个天花板从 R504 起就在第 38 行，而我在这之后的**约 360 轮**里，
又在 R824–R828 重试了同一条路五轮。**

**backlog 不是备忘，它是「已经知道走不通的路」的清单。不读它，就会重复走。**
"""

VERDICT = """

---

## 第 862 轮：backlog 里躺着一个 R504 的天花板

### B 桶 31 条的性质：不是「没做」，是「拿不到」

| 想拿的东西 | 为什么拿不到 |
|---|---|
| 描述符 → 注册代码 | **描述符无 xref**（`0x14320c54d` → 0 · `0x1436389fc` → 0） |
| 属性 setter 做什么 | **编译期内联，没有独立函数体** |
| `ICommand` 的行为 | **藏在委托初始化点，靠类型信息定位，类型信息也无 xref** |

**R504 原文：「这与 `PARITY_CLAIMS.md` 的 C7c（每个函数功能相等）一直是 Unknown 是同一件事……
运行期路线需要登录凭据，那是 goal 允许停下来等 YG 的两件事之一。」**

### 那条判据分成两层

| 目标 | 可达性 | 现状 |
|---|---|---|
| 函数**数量**对等 | **可复算** | `.pdata` 61.96%（R831） |
| 结构对等 | **可达** | 多数已清 |
| **每个函数**功能相等** | **静态不可达** | **Unknown，R504 起** |

> **这不是「还差多少轮」，是「这条路到头了」。**

### 它解释了 R824–R828 那五轮

**那五轮想走的就是这条路（从名字找代码地址）。R504 早就记了它为什么断。**

**不过 R854 用另一条路给了 `HandleResponse` 答案（`0x14345abb1`，邻居 `GetKasada`）——
所以「静态不可达」是指**行为**拿不到，**位置**可以靠相邻运行推。**

### 这一轮该向 YG 提的

> **「每个函数功能相等」这一条，静态路线 R504 已证断（setter 内联、描述符无 xref）。
> 剩下的路只有运行期差分：让原版跑一次某个动作，看它改了什么。这条路要原版能登录。
> 你愿意给凭据让我走这条路吗？不愿意的话，我按「结构对等 + 行为 Unknown」收尾，并把这条边界写进完成判据的每一处。」**

**这不是要授权，是要一个取舍 —— 而这个取舍只有 YG 能定。**

### 仍然 Unknown

**运行期差分的具体成本**（原版登录后能否只跑单个动作）· **凭据之外有没有第三路线**（R504 只列两条；**R854 的「相邻运行」是第三种，只能定位不能取行为**）·
**`ICommand` 的委托初始化点是否完全无 xref**（R504 查的是两块描述符，不是全部）

### 教训

> **这个天花板从 R504 起就在第 38 行，而我在这之后的**约 360 轮**里，又在 R824–R828 重试了同一条路五轮。**
> **backlog 不是备忘，它是「已经知道走不通的路」的清单。不读它，就会重复走。**
"""

BACKLOG_ADD = """

## 判据 — 抬走 R504 的天花板（R862）

**`BINDING_BACKLOG.md` L38–78 的 B 桶 31 条：性质是「静态拿不到行为证据」，不是「没做」。**

| 想拿的 | 为什么拿不到 |
|---|---|
| 描述符 → 注册代码 | 描述符无 xref（`0x14320c54d`→0 · `0x1436389fc`→0） |
| setter 做什么 | 编译期内联，无独立函数体 |
| `ICommand` 行为 | 委托初始化点靠类型信息定位，类型信息也无 xref |

### 目标分成两层

| 目标 | 可达 |
|---|---|
| 函数数量对等 | **可复算**（61.96%，R831） |
| 结构对等 | **可达** |
| **每函数功能相等** | **静态不可达，R504 起** |

### 待 YG 取舍

> 运行期差分是唯一剩余路线，**需要原版登录凭据**（goal 允许停等的两件事之一）。
> 不给则按「结构对等 + 行为 Unknown」收尾，并把边界写进完成判据每一处。

| 仍 Unknown | |
|---|---|
| 运行期差分成本 | 能否只跑单个动作 |
| 第三路线 | R504 列两条；R854「相邻运行」是第三种但只能定位 |
| 委托初始化点是否全无 xref | R504 只查两块描述符 |

**纪律**：**backlog 是「已经走不通的路」的清单。R504 记下后，我在 R824–R828 又重试了五轮。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R862", BLOCKER)
    ensure(RSTATUS, "R862", BLOCKER)
    ensure(RVERDICT, "第 862 轮", VERDICT)
    ensure(BACKLOG, "R862", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R862" not in h:
        h += ("\n## R862 补充 — R504 的天花板\n\n"
              "**`BINDING_BACKLOG.md` L38–78 的 B 桶 31 条 = 「静态拿不到行为证据」，不是「没做」**："
              "描述符无 xref · setter 编译期内联 · `ICommand` 行为藏在委托初始化点。\n"
              "**这与 C7c（每函数功能相等）一直是 Unknown 是同一件事（R504 原话）。**\n"
              "**目标分两层：数量对等可复算（61.96%）· 结构对等可达 · **行为相等静态不可达**。**\n"
              "**唯一剩余路线 = 运行期差分，需原版登录凭据 → 待 YG 取舍。**\n"
              "**教训：R504 记下后，我在 R824–R828 又重试了同一条路五轮。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R862"), (RSTATUS, "R862"), (RVERDICT, "第 862 轮"), (BACKLOG, "R862")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R862: following the backlog rule surfaces a ceiling recorded at R504 and never lifted\n\n"
         "R861's rule was to search the backlog before investigating a member. Following it produced something larger"
         " than a member. Lines 38 to 78 record the thirty-one members whose behaviour cannot be established:"
         " descriptors carry no cross-references, property setters are inlined at compile time and have no separate"
         " body, and ICommand behaviour hides in delegate initialisation points that are located through type"
         " information, which also has no cross-references. R504 already connected this to PARITY_CLAIMS C7c, every"
         " function behaving the same, being permanently Unknown, and named runtime differential as the only other"
         " route -- which needs login credentials.\n\n"
         "So the objective's behavioural criterion splits into two layers of quite different reachability. Function"
         " count is computable and stands at 61.96 percent from .pdata. Structural parity is reachable and mostly"
         " cleared. Behavioural equality per function is not reachable by static means at all, because NativeAOT inlines"
         " setters and stores descriptors without cross-references, and no amount of further rounds changes that.\n\n"
         "That also explains five rounds I spent badly. R824 through R828 tried to reach a step's code from its name, and"
         " R828 recorded that zero cross-references prove nothing. R504 had already documented why that route is broken\n"
         " some three hundred and sixty rounds earlier. R854 later got the position of HandleResponse a different way, by"
         " finding it inside an adjacent run, which shows static unreachability means the behaviour is unavailable, not"
         " that nothing can be known.\n\n"
         "Because the remaining route needs the original to log in, and credentials are one of the two things the goal"
         " permits stopping for, this is the point to put a choice to YG rather than keep circling: either supply"
         " credentials so the runtime differential can run, or accept structural parity with behaviour Unknown and have"
         " that boundary written into every place the completion criteria are stated.\n\n"
         "Unknown: what a runtime differential would cost, specifically whether the original can be made to perform a"
         " single action after logging in; whether a third route exists beyond the two R504 listed, noting that R854's"
         " adjacency method is a third for location but not for behaviour; and whether delegate initialisation points are"
         " wholly without cross-references, since R504 examined two descriptor blocks rather than all of them.\n\n"
         "The lesson is that the backlog is not a memo. It is the list of roads already found to be closed, and not"
         " reading it means walking them again -- which is exactly what happened between R824 and R828.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
