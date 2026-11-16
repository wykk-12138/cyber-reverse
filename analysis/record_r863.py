"""Record R863: the ceiling blocks UI member behaviour; the core's behaviour is reachable another way."""

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
### R504 的天花板**只挡 UI**；核心的行为有另一条路（R863）

**42 条里点名的类，全部是 UI：**

```
AccountGrid · AccountGroupView · ActionsModal · CreateGroupModal · DesktopNotification
GoogleLogin · InputModal · MessageBoxDialog · PublishTemplateModal · StoreGroupModal
```

**成员是 `Add` · `Clear` · `Close` · `Delete` · `Edit` · `OpenUrl` · `Save` · `Start` · `StartAll` ——
都是 UI 上的按钮动作。**

### 所以

| 层 | R504 的天花板挡不挡 |
|---|---|
| **UI 成员行为** | **挡 —— 而 YG 2026-11-16 明令「ui先不急着复刻」** |
| **核心流程行为** | **不挡 —— 走的是另一条路（见下）** |

### 核心为什么不受影响

**R504 的断点有三条：描述符无 xref、setter 内联、`ICommand` 委托点无类型信息。
这三条都是**UI 属性**的问题 —— 一个按钮的 `Save` 属性做什么，没有独立函数体可读。**

**而核心步骤不是属性，是**方法发一个请求**。它的行为可以从三处证：**

1. **端点串**（`/shop/v1/drawScratch/draw` 这类，R849 已核 39 个全在）
2. **步骤序列与 ordinal**（R851–R856：哪几步、什么顺序、归哪一层）
3. **请求参数记号**（R850：`_uniqCode` / `storeUniqCode` / `Drawno`）

**所以核心的行为证据是「它发什么请求」，而 UI 的行为证据是「它改什么状态」。
前者在字符串池与 `.pdata` 里，后者被内联吃掉了。**

### 这对「每个函数功能相等」意味着

**这条判据在核心层**部分可达**（能证发什么请求），在 UI 层**不可达**（除非运行期差分）。**

**而 YG 的优先级已经把 UI 排在第 4 位。所以核心做到底时，
「功能相等」在核心层是有证据的；剩下的行为 Unknown 集中在被暂缓的 UI 层。**
"""

if "R504 的天花板**只挡 UI**；核心的行为有另一条路（R863" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: UI-only ceiling appended")

BLOCKER = """

---

## 287. 那个天花板**只挡 UI** —— 核心的行为有另一条路

> R863。未改产品代码。**R862 的结论要收窄一半。**

### 一、先核一件事：那 42 条在哪些类上

`BINDING_BACKLOG.md` L25–78 那段点名的类：

```
AccountGrid · AccountGroupView · ActionsModal · CreateGroupModal · DesktopNotification
GoogleLogin · InputModal · MessageBoxDialog · PublishTemplateModal · StoreGroupModal
```

**全是 UI。成员是 `Add` `Clear` `Close` `Delete` `Edit` `OpenUrl` `Save` `Start` `StartAll` ——
UI 上的按钮动作。**

### 二、所以天花板的作用域

| 层 | 挡不挡 |
|---|---|
| **UI 成员行为** | **挡** —— 而 YG 2026-11-16 明令「ui先不急着复刻」，排在第 4 位 |
| **核心流程行为** | **不挡** |

### 三、核心为什么走另一条路

**R504 的三条断点 —— 描述符无 xref、setter 内联、`ICommand` 委托点无类型信息 ——
全是**UI 属性**的性质。一个按钮的 `Save` 做什么，没有独立函数体可读。**

**而核心的一步不是属性，是**方法发一个请求**。它的行为可以从三处证：**

| 证据 | 例子 | 已到哪一步 |
|---|---|---|
| 端点串 | `/shop/v1/drawScratch/draw` | R849 核过 39 个全在 |
| 步骤序列 + ordinal | 哪几步、什么顺序、归哪层 | R851–R856 |
| 请求参数记号 | `_uniqCode` · `storeUniqCode` · `Drawno` | R850 |

**所以：核心的行为证据是「它发什么请求」，UI 的行为证据是「它改什么状态」。
前者在字符串池与 `.pdata` 里活着，后者被内联吃掉了。**

### 四、这对判据的影响

**「每个函数功能相等」在核心层**部分可达**（能证发什么请求），在 UI 层**不可达**（除非运行期差分）。**

**而 YG 的优先级把 UI 排在第 4 位，且明令「不急着复刻」。**

**所以：核心做到底时，「功能相等」在核心层是有证据的；
剩下的行为 Unknown 集中在被暂缓的 UI 层。**
**这比 R862 那句「这条路到头了」准确得多 —— 是**UI 那条路**到头了。**

### 五、R862 那个问题还要不要问 YG

**要，但它的分量变了。**

**原来问「不给凭据就没法做 1:1」。现在的准确问法是：**

> **核心层的功能相等我能靠请求证据推到较高程度；UI 层的行为（按钮 Save/Clear/Delete 到底改什么）
> 静态拿不到，而那是你已明令暂缓的部分。
> 所以我按现在的优先级做核心，UI 行为一律记 Unknown —— 这条路你认可吗？
> 或者你想先把凭据给我，让 UI 那层也能验。**

**这不再是「通不过的关卡」，是一个优先级确认。**

### 六、验证

```
replica\\docs\\BINDING_BACKLOG.md L25–L86
  点名的类 11 个，全部 UI 形状（View/Modal/Dialog/Grid/Notification/Login）
  成员集合 {Add, Clear, Close, Delete, Edit, OpenUrl, Save, Start, StartAll}
R504 三条断点：描述符无 xref · setter 内联 · ICommand 委托点无类型信息 —— 全部关于属性
R849: 39 个 /shop/v1 端点全在 · R850: 参数记号 5 个 · R851–R856: 序列与层级
本轮未改产品代码
七项度量沿用
```

### 七、仍然 Unknown

- **核心类里有没有「属性式」成员踩同一条断点**：**Unknown** ——
  **42 条是全量吗？backlog 说「`shape_audit` 把它们标成…」暗示是筛出来的全量，但它筛的是「既无方法也无属性」，**
  **所以核心类里那些「有方法但行为不明」的成员不在这 42 条里，而它们的可达性没查。**
- **`TaskGroup` 那套 solver 配置（R860）的行为**：**Unknown** —— 那是属性还是方法，没查。
- **UI 层不做的前提下，「1:1」怎么表述**：**要 YG 定** —— 这是第五节那个问题。

### 八、教训

**R862 我写「这条路到头了」，而它只对了一半 —— 我读的是 backlog 里那份列表，没问「这列表覆盖哪些类」。**

**一个天花板的作用域，和天花板本身一样重要。
「静态拿不到行为证据」这句话，如果不说**哪些**行为，就等于说「全都拿不到」。**
"""

VERDICT = """

---

## 第 863 轮：那个天花板只挡 UI；核心的行为有另一条路

### 那 42 条点名的类，全部是 UI

```
AccountGrid · AccountGroupView · ActionsModal · CreateGroupModal · DesktopNotification
GoogleLogin · InputModal · MessageBoxDialog · PublishTemplateModal · StoreGroupModal
```

**成员：`Add` `Clear` `Close` `Delete` `Edit` `OpenUrl` `Save` `Start` `StartAll` —— UI 按钮动作。**

### 所以天花板的作用域

| 层 | 挡不挡 |
|---|---|
| **UI 成员行为** | **挡** —— 而 YG 明令「ui先不急着复刻」，排第 4 位 |
| **核心流程行为** | **不挡** |

### 核心为什么走另一条路

**R504 的三条断点（描述符无 xref · setter 内联 · `ICommand` 委托点无类型信息）全是**UI 属性**的性质 ——
一个按钮的 `Save` 做什么，没有独立函数体可读。**

**而核心的一步是**方法发一个请求**，它的行为可以从三处证：**

| 证据 | 已到哪一步 |
|---|---|
| 端点串（`/shop/v1/drawScratch/draw`） | R849 核过 39 个全在 |
| 步骤序列 + ordinal | R851–R856 |
| 请求参数记号（`_uniqCode` / `storeUniqCode` / `Drawno`） | R850 |

> **核心的行为证据是「它发什么请求」，UI 的行为证据是「它改什么状态」。
> 前者在字符串池与 `.pdata` 里活着，后者被内联吃掉了。**

### 那个问题要重问，但分量变了

> **核心层的功能相等我能靠请求证据推到较高程度；UI 层的行为（按钮 Save/Clear/Delete 改什么）静态拿不到，
> 而那是你已明令暂缓的部分。所以我按现在的优先级做核心，UI 行为一律记 Unknown —— 这条路你认可吗？
> 或者你想先把凭据给我，让 UI 那层也能验。**

**这不再是「通不过的关卡」，是一个优先级确认。**

### 仍然 Unknown

**核心类里有没有「属性式」成员踩同一条断点**（42 条筛的是「既无方法也无属性」，**核心类里「有方法但行为不明」的成员可达性没查**）·
**`TaskGroup` 那套 solver 配置是属性还是方法** · **UI 不做时「1:1」怎么表述**（要 YG 定）

### 教训

> **一个天花板的作用域，和天花板本身一样重要。**
> **「静态拿不到行为证据」这句话，如果不说**哪些**行为，就等于说「全都拿不到」。**
"""

BACKLOG_ADD = """

## 判据 — 天花板只挡 UI（R863）

**42 条点名的类全部 UI**：`AccountGrid` `AccountGroupView` `ActionsModal` `CreateGroupModal` `DesktopNotification`
`GoogleLogin` `InputModal` `MessageBoxDialog` `PublishTemplateModal` `StoreGroupModal`
**成员：`Add` `Clear` `Close` `Delete` `Edit` `OpenUrl` `Save` `Start` `StartAll`**

| 层 | R504 天花板 |
|---|---|
| **UI 成员行为** | **挡**（YG 已明令暂缓） |
| **核心流程行为** | **不挡** |

### 核心走另一条路

**核心一步 = 方法发一个请求 → 行为证据在三处：端点串（R849 39 个全在）· 序列与 ordinal（R851–R856）· 参数记号（R850）。**

> **核心的行为证据是「发什么请求」，UI 的是「改什么状态」。前者在字符串池与 `.pdata` 里活着，后者被内联吃掉。**

### 待 YG 的确认（分量已变）

> 核心层功能相等可靠请求证据推进；UI 层行为静态拿不到，而那是暂缓部分。
> **按现优先级做核心、UI 行为记 Unknown —— 这条路认可吗？或先给凭据让 UI 层也能验。**

| 仍 Unknown | |
|---|---|
| 核心类里「有方法但行为不明」的成员 | 42 条筛的是「既无方法也无属性」，这批未查 |
| `TaskGroup` solver 配置是属性还是方法 | 未查 |
| UI 不做时「1:1」怎么表述 | **要 YG 定** |

**纪律**：**天花板的作用域和天花板本身一样重要 —— 不说「哪些行为」，就等于说「全都拿不到」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R863", BLOCKER)
    ensure(RSTATUS, "R863", BLOCKER)
    ensure(RVERDICT, "第 863 轮", VERDICT)
    ensure(BACKLOG, "R863", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R863" not in h:
        h += ("\n## R863 补充 — 天花板只挡 UI\n\n"
              "**42 条点名的类全部是 UI**（`AccountGrid` `ActionsModal` `GoogleLogin` `MessageBoxDialog` …），"
              "成员是 `Add`/`Clear`/`Close`/`Delete`/`Save`/`StartAll` 等按钮动作。\n"
              "**→ R504 天花板只挡 UI 成员行为（YG 已暂缓），不挡核心。**\n"
              "**核心一步 = 方法发请求 → 行为证据在三处：端点串（R849 39 个）· 序列与 ordinal（R851–R856）· 参数记号（R850）。**\n"
              "**待 YG 确认（分量已变）：按现优先级做核心、UI 行为记 Unknown，这条路认可吗？**\n"
              "**教训：天花板的作用域和天花板本身一样重要。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R863"), (RSTATUS, "R863"), (RVERDICT, "第 863 轮"), (BACKLOG, "R863")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R863: the ceiling covers UI members only, and the core's behaviour has another route\n\n"
         "R862 said the static route to behaviour was finished. Checking which classes the forty-two members sit on"
         " narrows that considerably. Every class named in that section is a UI type -- AccountGrid, AccountGroupView,"
         " ActionsModal, CreateGroupModal, DesktopNotification, GoogleLogin, InputModal, MessageBoxDialog,"
         " PublishTemplateModal, StoreGroupModal -- and the members are Add, Clear, Close, Delete, Edit, OpenUrl, Save,"
         " Start and StartAll, which are button actions.\n\n"
         "R504's three dead ends are all properties of UI properties. A descriptor with no cross-references, a setter"
         " inlined so it has no body of its own, and ICommand behaviour hidden in a delegate initialisation point located"
         " through type information that also has no cross-references. None of that says anything about a flow step,\n"
         " because a flow step is not a property. It is a method that issues a request, and its behaviour is evidenced\n"
         " from three places that are alive in the binary: the endpoint string, which R849 checked thirty-nine of; the"
         " step sequence and its ordinal, which R851 through R856 worked out; and the request parameter markers, which\n"
         " R850 found as _uniqCode, storeUniqCode and Drawno.\n\n"
         "So core behaviour is evidenced by what request it sends while UI behaviour would be evidenced by what state it"
         " changes, and the former survives in the string pool and .pdata where the latter was inlined away. Since YG"
         " put UI fourth and said not to hurry it, the ceiling lands almost entirely on work already deferred.\n\n"
         "That changes the question from a gate to a confirmation. The core can be taken a long way on request evidence;"
         " UI behaviour cannot be had statically and is deferred; so the proposal is to keep the current priorities and"
         " record UI behaviour as Unknown, and to ask YG whether that is the shape they want, or whether they would"
         " rather supply credentials so the UI layer can be verified too.\n\n"
         "Unknown: whether core classes have property-shaped members hitting the same dead ends, since the forty-two were"
         " selected as having neither method nor property and a core member that has a method but unclear behaviour was"
         " never in that list and is unchecked; whether TaskGroup's solver configuration is property or method; and how"
         " one-to-one should be phrased when UI is out of scope, which is YG's call.\n\n"
         "The lesson is that a ceiling's scope matters as much as the ceiling. Saying behaviour cannot be had statically,"
         " without saying which behaviour, amounts to saying none of it can.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
