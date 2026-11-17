"""Record R966: the step names are absent from the artifact, which means the reflection table is empty there."""

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
### 179 个步骤名**一个都不在产物里** —— 派发表在 AOT 里是空的（R966）

**R965 说下一轮查「那些覆写进产物了吗」。而字符串核对已经被 R964 否掉了
（`www.bstn.com` 在、而同一方法里带协议的完整串不在）。所以换一个不依赖 body 串的检查：**
**查**步骤方法名**。**

### 为什么方法名是个干净的问法

**`StepActionRunner.Build()` 走 `typeof(StoreFlow).GetMethods(...)`。
要让那句反射返回东西，裁剪工具**必须**保留 `StoreFlow` 的方法元数据 —— **名字在内**。
所以方法名在不在产物里，直接回答「反射表在 AOT 里能不能建起来」，而与任何字面量无关。**

### 结果

```
StoreFlow 声明的步骤:                    179
方法名在产物里:                            0
方法名不在:                              179
阴性对照 NoSuchStepNameAtAll / ZzzQqqWww:  都不在（对照正确）
```

> **0 / 179。而阴性对照也是不在 —— 所以这不是「搜错编码」的假阴性，是**真的没有**。**
> **而 `StepActionTests` 在 Debug 构建里通过 —— 那里有 metadata。AOT 产物里没有。****

### 所以 AOT 产物里 `StepActionRunner.Invokers` 是**空的**

**`Knows(step)` 恒为 false，`StepDispatch` 恒为空字典。
而那意味着：**在产物里，任何「按名字跑一个步骤」的路径都跑不起来。**

> **而这给 62.77% 的缺口提供了一个具体的主因候选：
> 不是「步骤没写」（R965 已证 34 个全有覆写），也不是「写了被裁」，
> 而是**整个派发机制在 AOT 下失效，于是所有只经它可达的代码都被裁掉**。**

### 而 `StepMap` 大概不是同一条路

**R882 的 `*StepMap` 是**编译期字面量**（`ordinal → 步骤名`），不是反射。
所以如果派发真在跑，走的是那张表，不是 `Invokers`。**

> **而这两条路里哪条是活的、以及原版走哪条 —— 我没取证。标 Unknown。**

### 数字

| 度量 | R965 | **R966** |
|---|---|---|
| 套件 | 2186 | **2186（本轮只取证）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **产物里的步骤名** | 未查 | **0 / 179** |
| 有覆写的空壳 | 0 | **0** |

### 教训

> **我用了十几轮「写实现」当进展，而**实现早就在**（R965），
> 而**派发它的那张表在产物里是空的**（R966）。
> 两句合起来说明：我一直在一个**跑不起来的分支**上加内容，然后看着旁边的数字动。**
> **而找出这件事的不是一个新工具，是**换一个不依赖字符串的问法** ——
> 因为我上一轮刚证明原来那个问法的反向不成立。**
"""

if "179 个步骤名**一个都不在产物里**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 966 轮：179 个步骤名一个都不在产物里 —— 派发表在 AOT 里是空的

### 为什么换个问法

**R964 否掉了字符串核对（`www.bstn.com` 在、同一方法里带协议的完整串不在）。
所以这一轮查**步骤方法名** —— `StepActionRunner.Build()` 走 `GetMethods()`，
要让那句反射返回东西，裁剪工具必须保留 `StoreFlow` 的方法元数据，名字在内。
所以方法名在不在，直接回答「反射表能不能建起来」，与字面量无关。**

### 结果

```
StoreFlow 声明的步骤:                     179
方法名在产物里:                             0
方法名不在:                               179
阴性对照 NoSuchStepNameAtAll / ZzzQqqWww:   都不在（对照正确）
```

> **0 / 179，而阴性对照也不在 —— 不是编码搜错，是真的没有。**
> **而 `StepActionTests` 在 Debug 构建里通过 —— 那里有 metadata；AOT 产物里没有。**

### 所以 AOT 产物里 `StepActionRunner.Invokers` 是空字典

**`Knows(step)` 恒 false，`StepDispatch` 恒空。
→ **在产物里，任何「按名字跑一个步骤」的路径都跑不起来。****

> **这给 62.77% 的缺口一个具体的主因候选：
> 不是「步骤没写」（R965：34 个全有覆写），也不是「写了被裁」，
> 而是**整个派发机制在 AOT 下失效，于是所有只经它可达的代码都被裁掉**。**

### 而 `StepMap` 大概不是同一条路

**`*StepMap` 是编译期字面量（`ordinal → 步骤名`），不是反射。
所以如果派发真在跑，走的是那张表，不是 `Invokers`。**

**哪条路是活的、原版走哪条 —— 未取证，标 Unknown。**

### 数字

| 度量 | R965 | **R966** |
|---|---|---|
| 套件 | 2186 | **2186（只取证）** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **产物里的步骤名** | 未查 | **0 / 179** |

### 教训

> **十几轮用「写实现」当进展，而实现早就在（R965），而派发它的表在产物里是空的（R966）。
> 两句合起来：我一直在一个**跑不起来的分支**上加内容，然后看着旁边的数字动。**
> **找出这件事的不是新工具，是**换一个不依赖字符串的问法** —— 因为上一轮刚证明原来那个问法的反向不成立。**
"""

BACKLOG_ADD = """

## 判据 (c) — **179 个步骤名 0 个在产物；派发表在 AOT 里是空的**（R966，**只取证**）

### 新问法（不依赖 body 串）

**查步骤**方法名**：`StepActionRunner.Build()` 走 `GetMethods()`，要让反射返回东西，
裁剪工具必须保留 `StoreFlow` 的方法元数据（名字在内）。**

### 结果

**179 个步骤 → 方法名在产物里 **0** 个；阴性对照 `NoSuchStepNameAtAll` / `ZzzQqqWww` 也不在（对照正确）**

### 推论

**AOT 产物里 `StepActionRunner.Invokers` 是空字典 → `Knows()` 恒 false → 按名字跑步骤在产物里跑不起来。**

**→ 62.77% 缺口的主因候选：不是「没写」，是**派发在 AOT 下失效，只经它可达的代码全被裁**。**

### 而 `*StepMap` 是另一条路

**编译期字面量，不是反射。哪条路活的未取证 → Unknown。**

### 数字

**套件 2186（未变）· 函数数 173,952（未变）· 陈旧度 0/0 · 产物步骤名 0/179**

| 仍 Unknown | |
|---|---|
| `StepMap` 路线在产物里是否还活着 | 未取证 |
| 原版怎么派发步骤 | 未取证（按名字反编译不可行，R958） |
| `Invokers` 空是不是缺口的全部原因 | 未证明 |

**纪律**：找出这件事的不是新工具，是换一个不依赖字符串的问法。
"""

BLOCKER = """

---

## 390. **179 个步骤名 0 个在产物；AOT 里派发表是空的**

> R966。**只取证，未改代码。** 套件 **2186 通过 / 0 失败 / 0 跳过** 保持不变。

### 一、为什么要换问法

**R964 否掉了字符串核对：`www.bstn.com` 在产物、而同一方法里带协议的完整串不在。
所以这一轮查**步骤方法名**。**

**为什么方法名干净：`StepActionRunner.Build()` 走 `typeof(StoreFlow).GetMethods(...)`。
要让那句反射返回东西，裁剪工具**必须**保留 `StoreFlow` 的方法元数据 —— 名字在内。
所以方法名在不在，直接回答「反射表能不能建起来」，与任何字面量无关。**

### 二、结果

```
StoreFlow 声明的步骤:                       179
方法名在产物里:                               0
方法名不在:                                 179
阴性对照 NoSuchStepNameAtAll / ZzzQqqWww:     都不在（对照正确）
```

**0 / 179，而阴性对照也不在 —— 不是编码搜错。**

### 三、推论

**AOT 产物里 `StepActionRunner.Invokers` 是空字典：**

**`Knows(step)` 恒 false · `StepDispatch` 恒空 →
**任何「按名字跑一个步骤」的路径在产物里都跑不起来。****

**给 62.77% 缺口一个具体的主因候选：**
- **不是「步骤没写」**（R965：34 个全有覆写）
- **不是「写了被裁」**
- **而是**派发机制在 AOT 下失效，只经它可达的代码全被裁****

### 四、而 `*StepMap` 是另一条路

**它是编译期字面量（`ordinal → 步骤名`），不是反射。
如果派发真在跑，走的是那张表。哪条活、原版走哪条 —— **未取证**。**

### 五、数字

| 度量 | R965 | R966 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **产物里的步骤名** | 未查 | **0 / 179** |

### 六、验证

```
python analysis/step_name_presence.py
  -> steps declared on StoreFlow: 179
  -> step method name present in artifact: 0
  -> control NoSuchStepNameAtAll present=False
```

### 七、仍然 Unknown

- **`StepMap` 路线在产物里是否还活着**：**Unknown** —— 未取证。
- **原版怎么派发步骤**：**Unknown** —— 按名字反编译不可行（R958）。
- **`Invokers` 空是不是缺口的全部原因**：**未证明**。

### 八、教训

**十几轮用「写实现」当进展，而实现早就在（R965），而派发它的表在产物里是空的（R966）。

两句合起来：我一直在一个**跑不起来的分支**上加内容，然后看着旁边的数字动。

找出这件事的不是一个新工具，是换一个不依赖字符串的问法 —— 因为上一轮刚证明原来那个问法的反向不成立。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R966", BLOCKER)
    ensure(RSTATUS, "R966", BLOCKER)
    ensure(RVERDICT, "第 966 轮", VERDICT)
    ensure(BACKLOG, "R966", BACKLOG_ADD)

    note = (
        "\n## R966 补充 — **179 个步骤名 0 个在产物；AOT 里派发表是空的**（只取证，套件 2186）\n\n"
        "换了个不依赖 body 串的问法：查步骤**方法名**。理由：`StepActionRunner.Build()` 走 `GetMethods()`，\n"
        "要让反射返回东西，裁剪工具必须保留 `StoreFlow` 的方法元数据（名字在内）。\n\n"
        "结果：**179 个步骤 → 方法名在产物里 0 个**；阴性对照 `NoSuchStepNameAtAll` / `ZzzQqqWww` 也不在（对照正确）。\n\n"
        "→ **AOT 产物里 `StepActionRunner.Invokers` 是空字典** → `Knows()` 恒 false → 按名字跑步骤在产物里跑不起来。\n\n"
        "→ 62.77% 缺口的主因候选：**不是「没写」（R965：34 个全有覆写），是派发在 AOT 下失效，\n"
        "   只经它可达的代码全被裁掉。**\n\n"
        "而 `*StepMap` 是编译期字面量、不是反射 —— 哪条路活的未取证，标 Unknown。\n\n"
        "数字：套件 2186（未变）· 函数数 173,952（未变）· 陈旧度 0/0 · 产物步骤名 0/179。\n\n"
        "纪律：找出这件事的不是新工具，是换一个不依赖字符串的问法。\n\n"
        "下一轮：让派发**不依赖反射**（把 Invokers 改成编译期字面量表，或给 StoreFlow 加 "
        "[DynamicallyAccessedMembers]），然后看函数数是否跳。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R966" not in h:
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
             for p, k in ((RBLOCK, "R966"), (RSTATUS, "R966"), (RVERDICT, "第 966 轮"), (BACKLOG, "R966")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R966: none of the 179 step names reach the artifact, so the dispatch table is empty there\n\n"
         "R965 left one question open: do the overrides reach the artifact. The body-string check cannot answer it, because\n"
         " R964 showed a retained method keeps some literals and drops others -- www.bstn.com is present while the full URL\n"
         " string in the same method is not. So this round asked a different question, one that does not depend on literals\n"
         " at all.\n\n"
         "StepActionRunner.Build walks typeof(StoreFlow).GetMethods. For that reflection to return anything, the trimming\n"
         " tool must keep StoreFlow's method metadata, names included. So whether the names are in the image answers directly\n"
         " whether the table can be built there, with no string involved on the body side.\n\n"
         "The answer is that none of the 179 declared steps has its name in the artifact, and the negative controls behave\n"
         " correctly, so this is not a search that missed its encoding. StepActionTests passes under a Debug build, where the\n"
         " metadata exists; the published image has none of it.\n\n"
         "That means Invokers is an empty dictionary in the artifact: Knows always returns false and StepDispatch is always\n"
         " empty, so no path that runs a step by name can work there. It also gives the missing thirty-seven percent a\n"
         " concrete candidate cause, and it is neither of the two I had been working from. The steps are written, as R965\n"
         " showed, and they are not written-and-then-trimmed for being unreachable in the ordinary sense; the dispatcher that\n"
         " would make them reachable does not exist in the image, so everything reachable only through it is removed.\n\n"
         "The *StepMap tables are a different mechanism: they are compile-time literals mapping an ordinal to a step name\n"
         " rather than reflection, so if dispatch does run in the artifact it runs through those. Which path is live, and\n"
         " which the original uses, was not examined and stays Unknown.\n\n"
         "Figures unchanged because no code changed: suite 2186, count 173,952, freshness zero, and step names in the\n"
         " artifact zero out of 179.\n\n"
         "Unknown: whether the StepMap route still works in the artifact; how the original dispatches steps, since\n"
         " decompiling by name is unavailable per R958; and whether the empty table accounts for the whole gap, which is not\n"
         " proven.\n\n"
         "The lesson is that for many rounds I treated writing implementations as progress while the implementations were\n"
         " already there, and the table that dispatches them was empty in the artifact. Together those two say I was adding\n"
         " content to a branch that cannot run, and watching a number move beside it. What found this was not a new tool but\n"
         " a different question, asked because the previous round had just shown the old one does not work in reverse.\n\n"
         "Documentation and one probe script only; no product code changed."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()