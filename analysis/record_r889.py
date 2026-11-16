"""Record R889: the draw POST bodies are unreachable statically, confirmed at the last route."""

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
### 抽签 POST 的请求体**静态不可得** —— 最后一条路也关上了（R889）

**R873 说 7 个抽签 POST 步骤缺请求体，R876 说字段名可能是候选键但那是 Inference。
这一轮把剩下的三条路都试完了。**

### 三条路，全部关闭

| 路 | 做法 | 结果 |
|---|---|---|
| **属性名** | 在 R883 基线里搜 `Drawid` `DrawGoodsId` `UniqCode` `EventId` `Slots` … 共 13 个 | **0 命中** —— draw 模型的属性从没被物化 |
| **函数名** | `ida.py funcs <名字>` | **`funcs` 不按名前过滤**，三个不同模式返回同样的前 50 个 `sub_` —— 镜像无符号名 |
| **字符串 xref** | `ida.py xrefs 0x14337c7e5` | **`xref_count: 0` —— 「No cross-references to this address」** |

**第三条是决定性的。`<GetOrders>d__104` / `<StartDrawFlow>d__115` 那条字面量**没有任何代码引用它** ——
它是死串，是编译期留下的名字表，而不是被代码指向的数据。**

**这正是 R504 那个结论（描述符无 xref）在**这个具体地址**上的确认。
而之前 R504 说的是「属性写入拿不到」，这一轮把范围扩到「这些状态机名字本身也没有 xref」。**

### 所以 PopMart 的抽签前沿到了静态天花板

**已写 7 步（R871–R873）· 缺 7 个 POST 的体 · 缺 `GetInstoreOrders` 的端点。**

**而这三样都要求**运行期观察** —— 那需要原版登录凭据。**

**按 goal 的纪律，这是「可停下等 YG」的两类事之一。**

### 而优先级 ① 还有别的未结项，不需要凭据

| 项 | 状态 |
|---|---|
| 抽签/展览/预约步骤的体 | **静态不可得，需凭据** |
| `GetInstoreOrders` 用哪个端点 | **常量里没有；可能还有别的名字没搜** |
| 5 条变体序列（demandware-* / collectplus / structure-token-*） | **无流程类；R879 说任务种类这一层才有 14 个名字** |
| 其余 7 个流程的 `StepSequence` | **只做了 3 个** |

**所以「静态天花板」不是「无事可做」，是「这一条路到头了，旁边还有四条」。**
"""

if "抽签 POST 的请求体**静态不可得**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R889 appended")

BLOCKER = """

---

## 313. 抽签 POST 请求体：三条路全关，静态不可得

> R889。未改产品代码。

### 一、三条路

| 路 | 做法 | 结果 |
|---|---|---|
| **属性名** | R883 基线搜 13 个候选（`Drawid` `DrawGoodsId` `UniqCode` `EventId` `Slots` …） | **0 命中** |
| **函数名** | `ida.py funcs <名字>` | **不按名前过滤**（三个模式返回同样前 50 个 `sub_`）；镜像无符号 |
| **字符串 xref** | `ida.py xrefs 0x14337c7e5` | **`xref_count: 0`** |

**第三条决定性：那条状态机名字字面量**没有任何代码引用它** —— 是编译期留下的名字表，不是被代码指向的数据。**

**R504 说的是「属性写入拿不到」。这一轮把它扩到「这些状态机名字本身也没有 xref」。**

### 二、一处我自己的错，值得记

**前两次查询我把 JSON 的键读错了（`functions`/`matches`，实际是 `[{data:[…]}]`），
于是三次都返回「0 functions」，而我差点据此写下「镜像里没有这些函数」。**

**那次是**工具读法的错被读成了对象的缺席** —— 与 §2.7b 那条「池子里没找到 ⇏ 镜像里没有」同族，
只是这次发生在 JSON 解析而不是字符串搜索上。**

**而救回来的动作是：**用已知存在的名字（`MoveNext`）先验工具能不能工作**。

### 三、PopMart 抽签前沿到了静态天花板

**已写 7 步 · 缺 7 个 POST 体 · 缺 `GetInstoreOrders` 端点。三者都要运行期观察 —— 需原版登录凭据。**

**按 goal 纪律，这是「可停下等 YG」的两类事之一。**

### 四、但优先级 ① 还有四条不需要凭据的路

| 项 | 状态 |
|---|---|
| `GetInstoreOrders` 的端点 | **可能还有别的名字没搜**（R873 只搜了 `order` 一族） |
| 5 条变体序列 | 无流程类；R879 的 14 个种类是它们的名字来源 |
| 其余 7 个流程的 `StepSequence` | **只做了 3 个** |
| `EditLine` / `ReplaceProduct` 之类的基础步骤 | R877 说 `method` 形态有 34 条 |

**所以「静态天花板」不是「无事可做」，是「这一条路到头了，旁边还有四条」。**

### 五、验证

```
R883 基线搜 13 个 draw 属性名                  -> 0 命中，types holding any: 0
ida.py funcs EnterDraw / ChooseGoods / MoveNext -> 三者返回相同前 50 个 sub_（不过滤）
ida.py str "EnterDraw>d__"                      -> 1 命中 @ 0x14337c7e5（与 GetOrders 同串）
ida.py xrefs 0x14337c7e5                        -> xref_count: 0，message "No cross-references to this address"
本轮未改产品代码；套件沿用 1780
```

### 六、仍然 Unknown

- **那 7 个 POST 的请求体**：**Unknown，静态不可得** —— 需运行期。
- **`GetInstoreOrders` 的端点**：**Unknown** —— R873 搜的是 `order` 一族，
  **而 draw 端点在 `/shop/v1/drawScratch/*` 下，in-store 的可能在别的族。**
- **`funcs` 是否真的不支持前缀过滤**：**Observation（三个模式同结果）** ——
  **但 `ida.py` 是我们自己的客户端，所以这可能是客户端没实现参数透传，而不是插件不支持。**

### 七、教训

**我差点把「我的 JSON 读法错了」写成「镜像里没有这些函数」。**

**而救回它的是「先用一个已知存在的输入验工具」这个动作 ——
这个动作我这一轮做了一次，而它值三轮的结论。**

**所以：**任何一次「查询返回空」，在写成结论之前，都要先用一个已知非空的输入跑同一条命令。****
"""

VERDICT = """

---

## 第 889 轮：抽签 POST 请求体静态不可得 —— 三条路全关

### 三条路

| 路 | 结果 |
|---|---|
| **属性名**（R883 基线搜 13 个候选） | **0 命中** |
| **函数名**（`ida.py funcs`） | **不按名前过滤**；镜像无符号名 |
| **字符串 xref**（`ida.py xrefs 0x14337c7e5`） | **`xref_count: 0`** |

**第三条决定性：那条状态机名字字面量**没有任何代码引用** —— 是编译期的名字表，不是代码指向的数据。**

**R504 说的是「属性写入拿不到」；这一轮扩到「这些名字本身也没有 xref」。**

### 一处我自己的错

**前两次查询我把 JSON 键读错了（`functions`/`matches`，实际 `[{data:[…]}]`），三次都返回 0，
而我差点据此写下「镜像里没有这些函数」。**

> **那是**工具读法的错被读成对象的缺席** —— 与 §2.7b 同族，只是发生在 JSON 解析而不是字符串搜索上。**
> **救回它的是：用已知存在的名字（`MoveNext`）先验工具能不能工作。**

### PopMart 抽签前沿到了静态天花板

**已写 7 步 · 缺 7 个 POST 体 · 缺 `GetInstoreOrders` 端点 —— 三者都要运行期观察（需原版登录凭据）。**

**按 goal 纪律，这是「可停下等 YG」的两类事之一。**

### 但优先级 ① 还有四条不需要凭据的路

| 项 | 状态 |
|---|---|
| `GetInstoreOrders` 的端点 | **可能还有别的名字没搜**（R873 只搜 `order` 一族） |
| 5 条变体序列 | 无流程类；R879 的 14 个种类是名字来源 |
| 其余 7 个流程的 `StepSequence` | **只做了 3 个** |
| `method` 形态那 34 条 | R877 的分类 |

### 教训

> **任何一次「查询返回空」，在写成结论之前，都要先用一个已知非空的输入跑同一条命令。**
> **这一轮那个动作做了一次，而它值三轮的结论。**
"""

BACKLOG_ADD = """

## 判据 — 抽签 POST 请求体**静态不可得**（R889）

### 三条路全关

| 路 | 结果 |
|---|---|
| 属性名（R883 基线搜 13 个候选） | **0 命中** |
| 函数名（`ida.py funcs`） | **不按名前过滤**，镜像无符号名 |
| **字符串 xref @ `0x14337c7e5`** | **`xref_count: 0`** |

**→ 状态机名字是编译期名字表，无代码引用。R504 的「属性写入拿不到」扩为「这些名字本身也没 xref」。**

### 我的错：差点把工具读法的错写成对象缺席

**JSON 键读错（`functions`/`matches` vs `[{data:[…]}]`）→ 三次 0 结果。
救回：**先用已知存在的名字（`MoveNext`）验工具**。**

> **任何「查询返回空」写成结论前，先用已知非空的输入跑同一条命令。**

### PopMart 前沿 = 静态天花板

**已写 7 步 · 缺 7 个 POST 体 · 缺 `GetInstoreOrders` 端点 —— 都要运行期（**需原版登录凭据**，属可停下等 YG 的两类之一）。**

### 但还有四条不需凭据

**`GetInstoreOrders` 端点（R873 只搜了 `order` 一族）· 5 条变体序列 · 其余 7 个流程的 `StepSequence` · `method` 形态 34 条**

**纪律**：**「静态天花板」≠「无事可做」，是「这一条路到头，旁边还有四条」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R889", BLOCKER)
    ensure(RSTATUS, "R889", BLOCKER)
    ensure(RVERDICT, "第 889 轮", VERDICT)
    ensure(BACKLOG, "R889", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R889" not in h:
        h += ("\n## R889 补充 — 抽签 POST 请求体**静态不可得**（**未改产品代码**）\n\n"
              "**三条路全关**：属性名（基线搜 13 个候选 0 命中）· 函数名（`funcs` 不按名过滤，镜像无符号）· **字符串 xref `0x14337c7e5` = `xref_count: 0`**。\n"
              "**→ 状态机名字是编译期名字表，无代码引用。R504 扩为「这些名字本身也没 xref」。**\n"
              "**我的错**：JSON 键读错（`functions`/`matches` vs `[{data:[…]}]`）→ 三次 0 结果，**差点写成「镜像里没有这些函数」**；"
              "救回的是用已知存在的名字先验工具。**纪律：任何「查询返回空」写成结论前，先用已知非空的输入跑同一条命令。**\n"
              "**PopMart 前沿 = 静态天花板**：缺 7 个 POST 体 + `GetInstoreOrders` 端点，**都要运行期 → 需原版登录凭据（可停下等 YG）。**\n"
              "**还有四条不需凭据**：`GetInstoreOrders` 端点 · 5 条变体序列 · 其余 7 个流程的 `StepSequence` · `method` 形态 34 条。\n")
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
             for p, k in ((RBLOCK, "R889"), (RSTATUS, "R889"), (RVERDICT, "第 889 轮"), (BACKLOG, "R889")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R889: the draw POST bodies are unreachable statically, and all three routes are now closed\n\n"
         "R873 wrote seven of Pop Mart's twenty-four steps and recorded that the other seven are POSTs whose bodies\n"
         " nothing evidences. R876 noted the model's backing fields as candidate keys and refused to use them because\n"
         " that would be inference. This round tried the three routes that remained.\n\n"
         "Reading property names out of the R883 baseline produced zero hits across thirteen candidates, so the draw\n"
         " model's properties were never materialised for binding and are not in that inventory at all. Searching the\n"
         " function list does not filter by name -- three different patterns return the same first fifty sub_ entries,\n"
         " which is consistent with an image carrying no symbol names. And asking for cross-references to the literal\n"
         " that holds the state-machine names returns a count of zero with 'No cross-references to this address'.\n\n"
         "The third is decisive. The names sit in a compile-time table that no code points at, which extends R504's\n"
         " finding: that round established property writes are unreachable, this one establishes that the state-machine\n"
         " names themselves are dead strings. So the request bodies cannot be recovered statically by any route left.\n\n"
         "One error of mine is worth recording because it nearly became a conclusion. My first two queries read the\n"
         " wrong JSON key, so all three patterns appeared to return zero functions, and I was one step from writing that\n"
         " the image does not contain them. What rescued it was running the same command against a name I knew existed,\n"
         " MoveNext, to check the tool worked at all. Reading a tool's misuse as an object's absence is the same family\n"
         " as section 2.7b's warning about sampled sources, except the parsing layer rather than the search layer.\n\n"
         "So Pop Mart's draw frontier sits at its static ceiling: seven steps written, seven POST bodies missing, and\n"
         " GetInstoreOrders' endpoint missing. All three need runtime observation, which needs the original's login\n"
         " credentials -- one of the two conditions under which this goal permits stopping.\n\n"
         "But priority one has four other threads that need no credentials. GetInstoreOrders' endpoint, since R873\n"
         " searched only the order family and the draw endpoints live under a different prefix. The five variant\n"
         " sequences, whose names R879's fourteen kinds supply. The other seven flows' step sequences, of which three are\n"
         " done. And the thirty-four method-shaped rows R877 classified. A static ceiling on one thread is not a\n"
         " static ceiling on the work.\n\n"
         "Unknown: the seven request bodies, unavailable statically and needing runtime; GetInstoreOrders' endpoint,\n"
         " where only the order family has been searched; and whether funcs genuinely cannot filter by prefix, since the\n"
         " client is ours and this may be a missing argument pass-through rather than a limitation of the plugin.\n\n"
         "The lesson is a check to run before any query result becomes a finding: try the same command against an input\n"
         " known to be non-empty. Doing it once this round was worth three rounds of conclusions.\n\n"
         "No product code changed; suite carries at 1780."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
