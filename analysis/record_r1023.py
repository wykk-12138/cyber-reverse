"""Record R1023: the query stopped one match short, and the fifth literal retracts R1022's guess."""

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
### `PerimeterX` 有**五**条，不是四条 —— 而第五条撤回了上一轮的推断（R1023）

**R1022 收尾说下一轮查「那条文案是否就是原版对 PerimeterX 的全部处置」。查了，而答案是**不是** ——
因为我上一轮的回答只看了前四条。**

### ① 第五条

```
PerimeterX  n=5
  0x143336731  "PerimeterXHandler
  0x146e3e6dc  PerimeterX 
  0x146e3e70c  PerimeterX block (Rotating proxy)
  0x146e3e764  PerimeterX-Token
  0x146e9423c  Solving PerimeterX          ← 这一条
```

**→ `"Solving PerimeterX"` 是**进行时** —— 原版**有一个求解动作**。
→ 而它与 `"PerimeterX block (Rotating proxy)"` **并存**：**能解就解，解不了换代理。**

> **→ 所以 R1022 那句「原版不解决 PerimeterX，它绕过；若真是这样，复刻件不该给它写 solver」
> **被推翻了** —— 复刻件**应该**有 solver，而那条文案只是**回退路径**。**
> **→ 而两个表面并存正是 R772 的教训（「镜像有某平台的字符串 ≠ 那是唯一表面」）。**

### ② 而我为什么漏了它

**R1022 我查的是 `ida.py str "PerimeterX"`，而 `n=5`。而我**只读了前四条**（`[:4]` 的截断）。
→ 第五条在 `0x146e9423c`，与那四条相邻但地址差约 0x55 万 —— 打印时排第五。

**→ 这不是工具的问题，是我读输出时截断了自己。**
→ 而 `[:4]` 那个截断是我在临时脚本里随手写的 —— **没有理由的截断**。

### ③ 所以台账补了第五条

**`AntiBotVendors` 的 PerimeterX Evidence：4 → **5**，新增 `"Solving PerimeterX"`。**

**→ 而它不是页面级串（那是复刻件自己的进度输出），所以 `Gap.NoPageMarker` **不变**。
→ 而它settle 的是另一件事：**这个厂商被**处理**，不只是被检测** —— 而 `State.DetectedOnly` 需要重新看。****

### ④ 而那引出一个真问题

**`DetectedOnly` 的意思是「检测到但不处理」。而 `"Solving PerimeterX"` 说明镜像**有**处理。
→ 那 `State.DetectedOnly` **可能是错的**，而它错的方式与 R1018 同族：**从「我们没有实现」推出了「镜像没有」。**

**→ 而求解动作**怎么**做的（走什么协议）仍然 Unknown —— 那是 `SolveDetectedWallAsync` 该补的地方。
→ 但「有没有」这个问题现在有答案了：**有**。**

### ⑤ 数字

| 度量 | R1022 | **R1023** |
|---|---|---|
| 套件 | 2233 / 0 | **2233 / 0 / 0** |
| 产物陈旧度 | 4 / 3,788 | **4 / 3,795** |
| 函数数 | 174,336 | **174,336** |
| **PerimeterX 的字面量** | 4（台账）· 5（镜像，我读了 4） | **5 · 5** |
| **原版是否处理 PerimeterX** | Unknown（猜「只换代理」） | **是（`Solving PerimeterX`）** |
| **`State.DetectedOnly` 是否成立** | 未质疑 | **存疑 —— 待重看** |

### 教训

> **我在临时脚本里写了 `matches[:4]` —— 一个**没有理由的截断**，而它把唯一有行为意义的那条挡在外面。**
> **→ 而更坏的是：我用前四条建立了「原版不解决它」这个结论，而那个结论的形状
> （「只有换代理文案」）恰好与截断后的输入一致，所以它看起来很可靠。**
> **→ 截断自己输出的那一刻，我同时决定了结论。**
"""

if "`PerimeterX` 有**五**条，不是四条" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1023 轮：`PerimeterX` 有五条不是四条 —— 而第五条撤回了上一轮的推断

### ① 第五条

```
PerimeterX  n=5
  0x143336731  "PerimeterXHandler
  0x146e3e6dc  PerimeterX 
  0x146e3e70c  PerimeterX block (Rotating proxy)
  0x146e3e764  PerimeterX-Token
  0x146e9423c  Solving PerimeterX          ← 这一条
```

**→ `"Solving PerimeterX"` 是**进行时** ⇒ 原版**有一个求解动作**。
→ 与 `"PerimeterX block (Rotating proxy)"` **并存**：**能解就解，解不了换代理。**
→ **R1022 那句「原版不解决它、复刻件不该写 solver」**被推翻**。两个表面并存正是 R772 的教训。**

### ② 而我为什么漏了它

**R1022 我查的 `ida.py str "PerimeterX"` 返回 `n=5`，而我在临时脚本里写了 `matches[:4]` ——
**一个没有理由的截断** —— 然后只读了那四条。**

### ③ 台账补第五条

**`AntiBotVendors` PerimeterX Evidence 4 → **5**（`"Solving PerimeterX"`）。
它不是页面级串，所以 `Gap.NoPageMarker` **不变**；而它 settle 的是「被**处理**，不只是被检测」。**

### ④ 而那引出一个真问题

**`DetectedOnly` 意思是「检测到但不处理」。而 `"Solving PerimeterX"` 说明镜像**有**处理
⇒ `State.DetectedOnly` **可能错了**，错法与 R1018 同族：**从「我们没实现」推出了「镜像没有」。**

**→ 求解**怎么**做的仍 Unknown，但「有没有」现在有答案：**有**。**

### ⑤ 数字

| 度量 | R1022 | **R1023** |
|---|---|---|
| 套件 | 2233 / 0 | **2233 / 0 / 0** |
| 产物陈旧度 | 4 / 3,788 | **4 / 3,795** |
| 函数数 | 174,336 | **174,336** |
| **PerimeterX 字面量** | 4（台账）· 5（我读了 4） | **5 · 5** |
| **原版是否处理它** | Unknown（猜「只换代理」） | **是** |
| **`State.DetectedOnly`** | 未质疑 | **存疑 —— 待重看** |

### 教训

> **我在临时脚本里写了 `matches[:4]` —— 一个**没有理由的截断**，而它把唯一有行为意义的那条挡在外面。
> → 更坏的是：我用前四条建立了「原版不解决它」，而那个结论的形状（「只有换代理文案」）
> 恰好与截断后的输入一致，所以它看起来很可靠。**
> **→ 截断自己输出的那一刻，我同时决定了结论。**
"""

BACKLOG_ADD = """

## 优先级 ② — **`PerimeterX` 有 5 条不是 4 条；`"Solving PerimeterX"` 推翻「只换代理」的推断**（R1023）

### 第五条

```
0x146e9423c  Solving PerimeterX     ← 进行时，说明原版有求解动作
0x146e3e70c  PerimeterX block (Rotating proxy)   ← 与它并存
```

**→ 能解就解，解不了换代理（R772「两种表面并存」）。**

### 为什么漏了

**R1022 用的是 `ida.py str "PerimeterX"`（`n=5`），而临时脚本里写了 `matches[:4]` ——
**没有理由的截断**。而用前四条建立的结论，其形状恰好与截断后的输入一致，所以看起来可靠。**

### 改了什么

**`AntiBotVendors` PerimeterX Evidence 4 → 5。`Gap.NoPageMarker` 不变（它不是页面级串）。
守卫 `TheInventoryEntryIsTheFiveClassifiedLiterals` 同步更新。**

### 而它引出一个真问题

**`State.DetectedOnly`（检测到但不处理）与 `"Solving PerimeterX"` 矛盾
⇒ 该状态**可能错了**，错法与 R1018 同族：从「我们没实现」推出「镜像没有」。**
**→ 求解**怎么**做的仍 Unknown，但「有没有」= **有**。**

### 数字

**套件 2233/0/0 · 陈旧度 4 / 3,795 · 函数数 174,336 · 字面量 4→5 · DetectedOnly 存疑**

| 仍 Unknown | |
|---|---|
| PerimeterX 求解走什么协议 | 未取证 |
| `DetectedOnly` 该改成什么 | 待定 |

**纪律**：截断自己输出的那一刻，我同时决定了结论。
"""

BLOCKER = """

---

## 447. **`PerimeterX` 有 5 条不是 4 条；`"Solving PerimeterX"` 推翻「只换代理」的推断**

> R1023。**改 2 个源文件 + 1 个测试文件。** 套件 **2233 通过 / 0 失败 / 0 跳过**。

### 一、第五条

```
PerimeterX  n=5
  0x143336731  "PerimeterXHandler
  0x146e3e6dc  PerimeterX 
  0x146e3e70c  PerimeterX block (Rotating proxy)
  0x146e3e764  PerimeterX-Token
  0x146e9423c  Solving PerimeterX          ← 这一条
```

**→ `"Solving PerimeterX"` 是**进行时** —— 原版**有一个求解动作**。
→ 而它与 `"PerimeterX block (Rotating proxy)"` **并存**：**能解就解，解不了换代理。**

**→ 所以 R1022 那句「原版不解决 PerimeterX，它绕过；若真是这样，复刻件不该给它写 solver」
  **被推翻了** —— 复刻件**应该**有 solver，而那条文案只是**回退路径**。
→ 而两个表面并存正是 R772 的教训。**

### 二、而我为什么漏了它

**R1022 我查的是 `ida.py str "PerimeterX"`，而 `n=5`。而我**只读了前四条**（`[:4]` 的截断）。
→ 第五条在 `0x146e9423c`，与那四条相邻但地址差约 0x55 万 —— 打印时排第五。**

**→ 这不是工具的问题，是我读输出时截断了自己。
→ 而 `[:4]` 那个截断是我在临时脚本里随手写的 —— **没有理由的截断**。**

### 三、所以台账补了第五条

**`AntiBotVendors` 的 PerimeterX Evidence：4 → **5**，新增 `"Solving PerimeterX"`。

→ 而它不是页面级串（那是复刻件自己的进度输出），所以 `Gap.NoPageMarker` **不变**。
→ 而它 settle 的是另一件事：**这个厂商被**处理**，不只是被检测**。**

### 四、而那引出一个真问题

**`DetectedOnly` 的意思是「检测到但不处理」。而 `"Solving PerimeterX"` 说明镜像**有**处理。
→ 那 `State.DetectedOnly` **可能是错的**，而它错的方式与 R1018 同族：
  **从「我们没有实现」推出了「镜像没有」。**

**→ 而求解动作**怎么**做的（走什么协议）仍然 Unknown。
→ 但「有没有」这个问题现在有答案了：**有**。**

### 五、数字

| 度量 | R1022 | R1023 |
|---|---|---|
| 套件 | 2233 / 0 | **2233 / 0 / 0** |
| 产物陈旧度 | 4 / 3,788 | **4 / 3,795** |
| 函数数 | 174,336 | **174,336** |
| **PerimeterX 的字面量** | 4（台账）· 5（镜像，我读了 4） | **5 · 5** |
| **原版是否处理 PerimeterX** | Unknown（猜「只换代理」） | **是（`Solving PerimeterX`）** |
| **`State.DetectedOnly` 是否成立** | 未质疑 | **存疑 —— 待重看** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "PerimeterX"  -> {"n":5}（第五条 0x146e9423c "Solving PerimeterX"）
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~PerimeterXMarker" -m:1      -> 4 通过
python tools/metrics_report.py -> 完整套件 exit 0  2233 / 0 / 0
```

### 七、仍然 Unknown

- **PerimeterX 求解走什么协议**：**未取证**。
- **`State.DetectedOnly` 该改成什么**：**待定**。

### 八、教训

**我在临时脚本里写了 `matches[:4]` —— 一个**没有理由的截断**，而它把唯一有行为意义的那条挡在外面。**

**→ 而更坏的是：我用前四条建立了「原版不解决它」这个结论，而那个结论的形状
  （「只有换代理文案」）恰好与截断后的输入一致，所以它看起来很可靠。**

**→ 截断自己输出的那一刻，我同时决定了结论。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1023", BLOCKER)
    ensure(RSTATUS, "R1023", BLOCKER)
    ensure(RVERDICT, "第 1023 轮", VERDICT)
    ensure(BACKLOG, "R1023", BACKLOG_ADD)

    note = (
        "\n## R1023 补充 — **`PerimeterX` 有 5 条不是 4 条；`\"Solving PerimeterX\"` 推翻「只换代理」**（套件 2233）\n\n"
        "**第五条**：`0x146e9423c  Solving PerimeterX` —— **进行时**，说明原版**有求解动作**。\n"
        "而它与 `0x146e3e70c  PerimeterX block (Rotating proxy)` **并存** ⇒ **能解就解，解不了换代理**（R772 同形）。\n"
        "→ **R1022 那句「原版不解决它、复刻件不该写 solver」被推翻。**\n\n"
        "**为什么漏了**：R1022 的 `ida.py str \"PerimeterX\"` 返回 **n=5**，而我在临时脚本里写了 `matches[:4]` ——\n"
        "**没有理由的截断**。而用前四条建立的结论，其形状（「只有换代理文案」）恰好与截断后的输入一致，看起来可靠。\n\n"
        "**改**：台账 Evidence 4 → **5**。`Gap.NoPageMarker` 不变（它不是页面级串）。\n"
        "守卫改名 `TheInventoryEntryIsTheFiveClassifiedLiterals`。\n\n"
        "**而它引出一个真问题**：`State.DetectedOnly`（检测到但不处理）与 `\"Solving PerimeterX\"` 矛盾\n"
        "⇒ 该状态**可能错了**，错法与 R1018 同族（从「我们没实现」推出「镜像没有」）。\n"
        "→ 求解**怎么**做仍 Unknown，但「有没有」= **有**。\n\n"
        "数字：套件 2233/0/0 · 陈旧度 4 / 3,795 · 函数数 174,336 · 字面量 4 → **5** · `DetectedOnly` 存疑。\n\n"
        "纪律：**截断自己输出的那一刻，我同时决定了结论。**\n\n"
        "下一轮：定 `DetectedOnly` 该改成什么（`Solving PerimeterX` 的存在使它站不住）；或取证求解协议。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1023" not in h:
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
             for p, k in ((RBLOCK, "R1023"), (RSTATUS, "R1023"), (RVERDICT, "第 1023 轮"), (BACKLOG, "R1023")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1023: PerimeterX has five literals not four, and the fifth retracts last round's guess\n\n"
         "R1022 closed by asking whether \"PerimeterX block (Rotating proxy)\" was the whole of the original's response to\n"
         " that vendor -- if it were, this replica should not be growing a solver for it. The answer is no, and the reason\n"
         " I did not have it last round is that my own query output was truncated.\n\n"
         "ida.py str returned five matches. The throwaway script printed matches[:4]. The fifth, at 0x146e9423c, is\n"
         "\"Solving PerimeterX\" -- present progressive, so the original has a solving action. It sits beside the block\n"
         " narration rather than replacing it: solve it when you can, switch proxies when you cannot. Two surfaces, the\n"
         " same shape as R772.\n\n"
         "So the guess is withdrawn. The solver belongs. What the fifth literal does not change is the gap kind: it is a\n"
         " line of the workspace's own progress output, not something a store serves, so there is still no page-level\n"
         " marker to grep and NoPageMarker stands.\n\n"
         "What it does unsettle is the row's state. DetectedOnly means recognised and not handled, and a present-progressive\n"
         " line saying it is being solved says otherwise. That is the same failure as R1018's: concluding the image lacks\n"
         " something because this workspace has not implemented it.\n\n"
         "The inventory entry goes from four literals to five, the guard that pins it is renamed and updated, and both\n"
         " notes now record why four was wrong.\n\n"
         "Figures: suite 2233 unchanged, freshness four files and 3,795 lines, count 174,336, literals four to five in\n"
         " both the inventory and the reading, and the vendor now known to be handled rather than only detected.\n\n"
         "Unknown: the protocol its solver speaks, and what state DetectedOnly should become.\n\n"
         "The lesson is that I truncated my own output with a matches[:4] that had no reason behind it, and that the\n"
         " conclusion I built from the first four had exactly the shape the truncated input would produce -- which is why\n"
         " it looked well-supported. Deciding what to print was deciding what to believe.\n\n"
         "Two source files and one test file changed; suite green at 2233."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()