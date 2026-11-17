"""Record R1039: the pool is alphabetical, so adjacency means nothing, and ida.py already had what I thought it lacked."""

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
### 字符串池**按字母序排** ⇒ 邻近不代表分组；而 `ida.py` **早有** `--limit`（R1039）

**R1038 说下一轮「publish 清陈旧度，或找 Farfetch 的 transport」。而那条线索（`Farfetch` 与
`Farfetch Checkout` 地址邻近）让我想去枚举那一片 —— 于是发现了两件比 transport 更重要的事。**

### ① 那一片**不是站表**，是按字母序的整个池

```
146d8df3c  FamilyName            ← 字段名
146d8df6c  Fan Rewards Signup    ← 站/活动名
146d8dfac  Fantasy World
146d8dfdc  Farfetch              ← 站名
146d8e004  Farfetch Checkout     ← 站名 + 步骤
146d8e05c  Faroe Islands         ← **国家名**
146d8e08c  Faroese               ← **语言名**
146d8e0b4  Faroese (Faroe Islands)
146d8e0fc  Fashion District (PA) ← **商场名**
```

**→ 八条里有**三种完全不同的东西**：站名、国家名、语言名。
→ 所以 `Farfetch` 与 `Faroe Islands` 相邻是**字母序巧合**（`Far` 开头），不是语义分组。**

**→ 而那否掉了一个很容易犯的推断：**「地址邻近 ⇒ 同一张表」**。
→ 它是 AGENTS §2.7 那条（先假设形状，再把不符合读成别的东西）的**反面**：
→ 这次我先假设了「邻近是一张表」，而事实是池**被排过序**。**

### ② 而 `Farfetch` + `Farfetch Checkout` **仍是真证据**

**它们是池里**两条独立条目** —— 那证明原版有这个站的名字和它的结账步骤，
→ 但**不**证明它们构成一张表，也不提供域名或路由。**

**→ 所以 R1038 的结论不变，而它的**依据**要说清：不是「它们挨着所以是一张表」，
而是「池里有两个条目，一个是站名，一个是站名加结账」。**

### ③ 而 `ida.py` **早就有** `--limit` —— 我 R1024 那轮说「撞上限所以要窄查」是**过时**的

```
analysis/ida.py str <pattern> [--limit N]        ← R817 就是为这个加的
analysis/ida.py call <tool> '<json>'             ← 通用透传
analysis/ida.py py "<IDAPython>" [--timeout N]   ← one-off 脚本
```

**→ 我这一轮用 `py` 枚举了 315 条池条目 —— 那个能力一直可用。
→ 而 R1024 我用 `str "Solv"` 撞上 40 就下结论「工具截断，要把问题问小」，
**而答案是把 `--limit` 传上去**。**

**→ 那与本轮的池排序是同一类错：**我推断工具的局限，而没有读工具的用法。****

### ④ 而 `--limit` 那个发现的更正

| R1024 说 | 实际 |
|---|---|
| 「`ida.py str` 有 40 条上限 ⇒ 要把问题问小」 | **有 `--limit`，R817 加的** |
| 「窄 probe 是解法」 | **窄 probe 有用，但不是唯一解；`--limit 200` 也行** |

**→ 而 R817 的注释里写着「Pass `--limit N` to raise it」—— 那句话就在 82 行的文件里，
而我在七轮里读了那个文件三次。**

### ⑤ 数字

| 度量 | R1038 | **R1039** |
|---|---|---|
| 套件 | 2254 / 0 | **2254 / 0 / 0（未改代码）** |
| 产物陈旧度 | 1 / 217 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **那一片的池条目数** | — | **315** |
| **池是否按字母序** | 未注意 | **是（决定性）** |
| **`Farfetch` / `Farfetch Checkout`** | 2 条证据 | **2 条证据（依据更精确）** |
| **`ida.py --limit`** | 「没有」 | **有（R817 起）** |
| **我读了 ida.py 几次** | — | **3 次，而没看到那句话** |

### 教训

> **这一轮我没找到 transport，而找到了两个**关于我自己**的事实：**
> **① 池是按字母序的，所以「挨着」什么也不意味着；
> ② 我要的那个能力早在工具里，而我三次读同一个 82 行的文件都没看见那行注释。**
> **→ 两条都指向同一件事：**我在推断工具和数据的形状，而不是读它们。****
"""

if "而 `ida.py` **早有** `--limit`" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1039 轮：池按字母序 ⇒ 邻近不代表分组；而 `ida.py` 早有 `--limit`

### ① 那一片不是站表，是按字母序的整个池

```
FamilyName · Fan Rewards Signup · Fantasy World · Farfetch · Farfetch Checkout
Faroe Islands · Faroese · Faroese (Faroe Islands) · Fashion District (PA)
```

**→ 八条里**三种东西**：站名、国家名、语言名 ⇒ `Farfetch` 与 `Faroe Islands` 相邻是**字母序巧合**。
→ 那否掉了「地址邻近 ⇒ 同一张表」这个推断。
→ 它是 AGENTS §2.7 那条的**反面**：我先假设「邻近是一张表」，而事实是池**被排过序**。**

### ② 而 `Farfetch` + `Farfetch Checkout` **仍是真证据**

**它们是池里**两条独立条目** —— 证明原版有这个站的名字和它的结账步骤，
但**不**证明构成一张表，也不提供域名或路由 ⇒ R1038 的结论不变，而**依据**要更精确。**

### ③ 而 `ida.py` 早就有 `--limit` / `call` / `py`

```
str <pattern> [--limit N]      ← R817 就是为这个加的
call <tool> '<json>'           ← 通用透传
py "<IDAPython>" [--timeout N] ← one-off
```

**→ 这一轮我用 `py` 枚举了 315 条池条目 —— 那个能力一直可用。
→ 而 R1024 我撞上 40 就下结论「工具截断，要把问题问小」—— **答案是 `--limit`**。
→ R817 的注释就写着「Pass `--limit N` to raise it」，而在 82 行的文件里，
**我七轮里读了它三次。****

### ④ 数字

| 度量 | R1038 | **R1039** |
|---|---|---|
| 套件 | 2254 / 0 | **2254 / 0 / 0（未改代码）** |
| 产物陈旧度 | 1 / 217 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **那一片池条目数** | — | **315** |
| **池按字母序** | 未注意 | **是（决定性）** |
| **`ida.py --limit`** | 「没有」 | **有（R817 起）** |

### 教训

> **这一轮我没找到 transport，而找到了两个**关于我自己**的事实：
> ① 池按字母序 ⇒「挨着」什么也不意味着；② 我要的能力早在工具里，而我三次读同一个 82 行文件都没看见那行注释。**
> **→ 两条都指向同一件事：**我在推断工具和数据的形状，而不是读它们。****
"""

BACKLOG_ADD = """

## 判据 (f) 的方法学 — **池按字母序（邻近≠分组）；`ida.py` 早有 `--limit`/`call`/`py`**（R1039）

### ① 池按字母序

```
FamilyName · Fan Rewards Signup · Fantasy World · Farfetch · Farfetch Checkout
Faroe Islands · Faroese · Faroese (Faroe Islands) · Fashion District (PA)
```

**→ 站名、国家名、语言名混排 ⇒ `Farfetch` 与 `Faroe Islands` 相邻是**字母巧合**。
→ 否掉「地址邻近 ⇒ 同一张表」。**

### ② `Farfetch` / `Farfetch Checkout` 仍是 2 条独立证据

**证明站名 + 结账步骤存在；不证明是表，不提供域名/路由。**

### ③ 工具能力（一直可用，我漏了）

```
analysis/ida.py str <pattern> [--limit N]      ← R817 加的
analysis/ida.py call <tool> '<json>'           ← 通用透传
analysis/ida.py py "<IDAPython>" [--timeout N] ← one-off（本轮用它枚举 315 条）
```

**→ R1024 的「撞 40 上限 ⇒ 只能窄查」**过时**；答案是 `--limit`。
→ 我在 82 行文件里三次读过那行注释。**

### 数字

**套件 2254/0/0（未改代码）· 陈旧度 1 / 217 · 函数数 174,293 · 池条目 315 · 池字母序 是**

| 仍 Unknown | |
|---|---|
| Farfetch 的 transport | 未找到（需配置/运行时） |
| 产物需重 publish（1 文件） | 待收尾 |

**纪律**：**别推断工具与数据的形状 —— 读它们。**
"""

BLOCKER = """

---

## 463. **池按字母序 ⇒ 邻近不代表分组；而 `ida.py` 早有 `--limit`**

> R1039。**未改代码 —— 本轮纠正两个关于我自己的判断。** 套件 **2254 通过 / 0 失败 / 0 跳过**。

### 一、那一片**不是站表**，是按字母序的整个池

```
146d8df3c  FamilyName            ← 字段名
146d8df6c  Fan Rewards Signup    ← 站/活动名
146d8dfac  Fantasy World
146d8dfdc  Farfetch              ← 站名
146d8e004  Farfetch Checkout     ← 站名 + 步骤
146d8e05c  Faroe Islands         ← **国家名**
146d8e08c  Faroese               ← **语言名**
146d8e0b4  Faroese (Faroe Islands)
146d8e0fc  Fashion District (PA) ← **商场名**
```

**→ 八条里有**三种完全不同的东西**：站名、国家名、语言名。
→ 所以 `Farfetch` 与 `Faroe Islands` 相邻是**字母序巧合**（`Far` 开头），不是语义分组。**

**→ 而那否掉了一个很容易犯的推断：**「地址邻近 ⇒ 同一张表」**。
→ 它是 AGENTS §2.7 那条（先假设形状，再把不符合读成别的东西）的**反面**：
  这次我先假设了「邻近是一张表」，而事实是池**被排过序**。**

### 二、而 `Farfetch` + `Farfetch Checkout` **仍是真证据**

**它们是池里**两条独立条目** —— 那证明原版有这个站的名字和它的结账步骤，
  但**不**证明它们构成一张表，也不提供域名或路由。**

**→ 所以 R1038 的结论不变，而它的**依据**要说清：不是「它们挨着所以是一张表」，
  而是「池里有两个条目，一个是站名，一个是站名加结账」。**

### 三、而 `ida.py` **早就有** `--limit` —— 我 R1024 那轮说「撞上限所以要窄查」是**过时**的

```
analysis/ida.py str <pattern> [--limit N]        ← R817 就是为这个加的
analysis/ida.py call <tool> '<json>'             ← 通用透传
analysis/ida.py py "<IDAPython>" [--timeout N]   ← one-off 脚本
```

**→ 我这一轮用 `py` 枚举了 315 条池条目 —— 那个能力一直可用。
→ 而 R1024 我用 `str "Solv"` 撞上 40 就下结论「工具截断，要把问题问小」，
  **而答案是把 `--limit` 传上去**。**

**→ 那与本轮的池排序是同一类错：**我推断工具的局限，而没有读工具的用法。**

### 四、而那个发现的更正

| R1024 说 | 实际 |
|---|---|
| 「`ida.py str` 有 40 条上限 ⇒ 要把问题问小」 | **有 `--limit`，R817 加的** |
| 「窄 probe 是解法」 | **窄 probe 有用，但不是唯一解** |

**→ 而 R817 的注释里写着「Pass `--limit N` to raise it」—— 那句话就在 82 行的文件里，
  而我在七轮里读了那个文件三次。**

### 五、数字

| 度量 | R1038 | R1039 |
|---|---|---|
| 套件 | 2254 / 0 | **2254 / 0 / 0（未改代码）** |
| 产物陈旧度 | 1 / 217 | **1 / 217** |
| 函数数 | 174,293 | **174,293** |
| **那一片的池条目数** | — | **315** |
| **池是否按字母序** | 未注意 | **是（决定性）** |
| **`Farfetch` / `Farfetch Checkout`** | 2 条证据 | **2 条（依据更精确）** |
| **`ida.py --limit`** | 「没有」 | **有（R817 起）** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "Farfetch" --limit 200        -> 3 条（确认无更多）
python analysis/ida.py py "<枚举 0x146d8d000-0x146d93000>" -> wrote 315
  （结果 analysis/pool_region.txt：FamilyName / Faroe Islands / Faroese 混排 ⇒ 字母序）
```

### 七、仍然 Unknown

- **Farfetch 的 transport**：**未找到**（需配置或运行时证据）。
- **产物需重新 publish**（1 文件陈旧）：待收尾。

### 八、教训

**这一轮我没找到 transport，而找到了两个**关于我自己**的事实：**

**① 池是按字母序的，所以「挨着」什么也不意味着；
② 我要的那个能力早在工具里，而我三次读同一个 82 行的文件都没看见那行注释。**

**→ 两条都指向同一件事：**我在推断工具和数据的形状，而不是读它们。****
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1039", BLOCKER)
    ensure(RSTATUS, "R1039", BLOCKER)
    ensure(RVERDICT, "第 1039 轮", VERDICT)
    ensure(BACKLOG, "R1039", BACKLOG_ADD)

    note = (
        "\n## R1039 补充 — **池按字母序（邻近≠分组）；`ida.py` 早有 `--limit`/`call`/`py`**（套件 2254，未改代码）\n\n"
        "**那一片不是站表**：`FamilyName` · `Fan Rewards Signup` · `Farfetch` · `Farfetch Checkout` ·\n"
        "`Faroe Islands`（国家）· `Faroese`（语言）· `Fashion District (PA)`（商场）混排 ⇒ **字母序**。\n"
        "→ `Farfetch` 与 `Faroe Islands` 相邻是**字母巧合**，不是语义分组。\n"
        "→ 否掉「地址邻近 ⇒ 同一张表」；`Farfetch`/`Farfetch Checkout` 仍是**2 条独立证据**（站名 + 结账步骤），\n"
        "但不证明是表、不给域名或路由。\n\n"
        "**而 `ida.py` 早就有**：`str <p> [--limit N]`（**R817 就是为这个加的**）· `call <tool> '<json>'` ·\n"
        "`py \"<IDAPython>\"`。本轮用 `py` 枚举了 **315** 条池条目。\n"
        "→ **R1024 的「撞 40 上限 ⇒ 只能窄查」过时**；答案是 `--limit`。而那句注释就在 82 行的文件里，\n"
        "**我七轮读了它三次。**\n\n"
        "数字：套件 2254/0/0（未改代码）· 陈旧度 1 / 217 · 函数数 174,293 · 池条目 **315** · 池字母序 **是**。\n\n"
        "纪律：**别推断工具与数据的形状 —— 读它们。**\n\n"
        "下一轮：publish 清陈旧度；或换回优先级 ①（Farfetch 的 transport 需要配置/运行时证据，非字符串可得）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1039" not in h:
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
             for p, k in ((RBLOCK, "R1039"), (RSTATUS, "R1039"), (RVERDICT, "第 1039 轮"), (BACKLOG, "R1039")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1039: the pool is alphabetical, so adjacency means nothing -- and ida.py already had the flag\n\n"
         "R1038 left two Farfetch strings at neighbouring addresses and I read that as a store table worth enumerating.\n"
         "Enumerating it says otherwise.\n\n"
         "The region is the string pool sorted alphabetically, and eight consecutive entries hold three unrelated kinds\n"
         " of thing: a field name, two store names, then Faroe Islands, Faroese and Faroese (Faroe Islands), then a\n"
         " shopping mall. Farfetch sits beside Faroe Islands because both start with Far. So adjacency here carries no\n"
         " semantic weight at all, and the inference I was about to build on it -- that neighbouring addresses mean one\n"
         " table -- is the same error as R764's, only inverted: that time I assumed a shape and read the mismatch as\n"
         " absence, this time I assumed a shape and read alphabetical order as structure.\n\n"
         "The evidence for Farfetch survives, stated more carefully. The pool holds two separate entries, one a store\n"
         " name and one that adds a checkout step, which is enough to say the original supports the store and not enough\n"
         " to say anything about its transport.\n\n"
         "The second finding is about the tool. ida.py has had a limit flag since R817, a generic passthrough, and an\n"
         " IDAPython escape hatch -- the last of which is what enumerated three hundred and fifteen pool entries this\n"
         " round. Seven rounds ago I ran into its forty-match cap, concluded the tool could not answer, and spent the\n"
         " round narrowing questions. The answer was passing a flag. The comment saying so sits in an eighty-two line\n"
         " file I have read three times since.\n\n"
         "Figures: suite 2254 unchanged since no code changed, freshness one file and 217 lines, count 174,293, three\n"
         " hundred and fifteen entries in the region, and two corrections to my own earlier conclusions.\n\n"
         "Unknown: what Farfetch's transport is, which strings cannot supply, and a publish to clear freshness.\n\n"
         "The lesson is not to infer the shape of a tool or a data structure -- read them. Both findings this round came\n"
         " from doing that, and both contradicted something I had already decided.\n\n"
         "No code changed; suite green at 2254."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()