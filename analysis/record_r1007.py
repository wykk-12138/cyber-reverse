"""Record R1007: the new probe retracts R1006's self-refutation, and the cause was one encoding."""

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
### 新工具一击推翻了我上一轮的自我否证 —— 原因是我只查了一种编码（R1007）

**R1006 说「`StoreFlowRunner` / `GuardAsync` 现在 absent，而 R1002 记的是 IN，所以其中一次读数错了，
R1002 的可达性结论撤回」。这一轮造了稳定读数工具，第一次跑就把那句话推翻了。**

### ① 工具：`tools/artifact_probe.py`

**它做的事很少，而缺的正是这一点：每次探测都记录**产物身份**（sha256 / 字节数 / mtime），
并把结果追加到 `analysis/ARTIFACT_PROBES.json`。**

**文件头写了为什么现成的够不到（AGENTS.md §1 规则 2）：
`where_is.py` 答复刻件源码，`analysis/ida.py str` 答原版数据库，`pe_triage.py` 答布局 ——
没有一个是「这个字面量在**这个**二进制里吗，是**哪一个**二进制答的」。**

### ② 第一次跑的结果

```
artifact  .publish-aot/Cybersole.Ui.exe
sha256    36c16b3b3fd536d23cf4920603afc7761729a505ed4e0975de38444912891409
bytes     56183808   mtime 2026-11-17T16:26:54

  string              utf-16-le   utf-8   present
  StoreFlowRunner             0       1   yes
  GuardAsync                  0       2   yes
  lastStatus                  0       0   no
  lastBody                    0       0   no
  reservation failed          0       0   no
  decoy                       0       0   no
  antibot                      3       0   yes
```

### ③ 决定性：`StoreFlowRunner` 与 `GuardAsync` **在**产物里，以 **UTF-8** 形式

**→ 我 R1006 只查了 **UTF-16LE**，所以报 absent。
→ 所以「R1002 记 IN、R1006 记 absent」**不是产物变了，也不是 R1002 读错** ——
  是我 R1006 那次只查了一半编码。**

**→ 而 R967 早就立了这条：「反射元数据（类型/方法名）是 **UTF-8**；字符串字面量是 **UTF-16LE**。
  查错一种会给出一个自信的「没有」。」**

> **→ 我在 R1006 违反了它，然后把这个假阴性当成「读数矛盾」，
> 进而写了一条自我否证，还撤回了 R1002 一条本来正确的结论。**
> **→ 而新工具第一次运行就把它纠正了 —— 因为它**同时**查两种编码，而我的手写探测只查一种。**

### ④ 而消息层那四个串两种编码都是 0 —— 那部分是**真的**

| 串 | UTF-16LE | UTF-8 |
|---|---|---|
| `lastStatus` | 0 | 0 |
| `lastBody` | 0 | 0 |
| `reservation failed` | 0 | 0 |
| `decoy` | 0 | 0 |

**→ 所以 R1006 的另一半结论对：消息层**确实**没进产物。
→ 而这一半现在有了带产物身份的读数支撑，不再是我的印象。**

### ⑤ 三个结论的最终状态

| R1006 说的 | 现在 |
|---|---|
| `StoreFlowRunner` / `GuardAsync` absent | **错 —— 在，UTF-8** |
| 「R1002 的可达性结论撤回」 | **撤回该撤回 —— R1002 的 IN 是对的** |
| 消息层没进产物 | **对，且现在有产物身份作证** |
| 「读数为何矛盾」Unknown | **已知：只查一种编码** |

### ⑥ 而同一份产物里两种编码并存

**`GuardAsync` 是 UTF-8（2 次），`antibot` 是 UTF-16LE（3 次）—— 同一个文件。
→ 所以「用哪种编码查」不是可以被默认值替掉的事，它是**每次都要问**的事。
→ 而工具现在强制同时查两种并存两列，那比一条纪律更难违反。**

### 数字

| 度量 | R1006 | **R1007** |
|---|---|---|
| 套件 | 2218 | **2218（未改产品代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **带产物身份的读数** | 0（手写探测） | **全部（新工具）** |
| **R1002 可达性结论** | R1006 撤回 | **恢复（IN 是对的）** |
| **消息层进产物** | 否（一种编码） | **否（两种编码，sha256 背书）** |

### 教训

> **「两次读数矛盾」有第三种解释：**两次问的不是同一个问题**。
> R1006 我把它读成「其中一次错了」，而它其实是「其中一次只查了一半」。
> **→ 一个带身份的读数工具之所以值得写，不是因为它更准 ——
> 是因为它让「问的是不是同一个问题」变成一件**看得见**的事。**
"""

if "新工具一击推翻了我上一轮的自我否证" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1007 轮：新工具一击推翻了我上一轮的自我否证 —— 原因是我只查了一种编码

### ① 工具：`tools/artifact_probe.py`

**每次探测都记录**产物身份**（sha256 / 字节数 / mtime），结果追加到 `analysis/ARTIFACT_PROBES.json`。
文件头写明为什么现成的够不到：`where_is.py` 答源码，`ida.py str` 答原版数据库，`pe_triage.py` 答布局 ——
没有一个是「这个字面量在**这个**二进制里吗，是**哪一个**二进制答的」。**

### ② 第一次跑：`StoreFlowRunner` / `GuardAsync` **在**产物里，以 **UTF-8** 形式

```
StoreFlowRunner  utf-16-le 0   utf-8 1   yes
GuardAsync       utf-16-le 0   utf-8 2   yes
antibot          utf-16-le 3   utf-8 0   yes
```

> **→ R1006 我只查 UTF-16LE 所以报 absent。R1002 的 IN 是**对的**。
> → 而 R967 早已立规：「反射元数据是 UTF-8，字符串字面量是 UTF-16LE，查错一种会给出自信的「没有」。」
> → **我在 R1006 违反了它，把假阴性当成「读数矛盾」，写了一条自我否证，还撤回了 R1002 一条正确的结论。**

### ③ 而消息层那四个串**两种编码都是 0** —— 那部分是**真的**

| 串 | UTF-16LE | UTF-8 |
|---|---|---|
| `lastStatus` · `lastBody` · `reservation failed` · `decoy` | 0 | 0 |

**→ R1006 的另一半结论对：消息层确实没进产物，而现在有 sha256 背书的读数。**

### ④ 三个结论的最终状态

| R1006 说的 | 现在 |
|---|---|
| `StoreFlowRunner` / `GuardAsync` absent | **错 —— 在，UTF-8** |
| 「R1002 可达性撤回」 | **撤回该撤回 —— R1002 的 IN 是对的** |
| 消息层没进产物 | **对，且有产物身份作证** |
| 「读数为何矛盾」Unknown | **已知：只查一种编码** |

### ⑤ 而同一份产物里两种编码并存

**`GuardAsync` 是 UTF-8，`antibot` 是 UTF-16LE —— 同一个文件。
→ 「用哪种编码查」不能被默认值替掉，它每次都要问。
→ 而工具强制同时查两种并存两列，那比一条纪律更难违反。**

### 数字

| 度量 | R1006 | **R1007** |
|---|---|---|
| 套件 | 2218 | **2218（未改产品代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| **带产物身份的读数** | 0 | **全部** |
| **R1002 可达性结论** | 撤回 | **恢复** |
| **消息层进产物** | 否（一种编码） | **否（两种编码，sha256 背书）** |

### 教训

> **「两次读数矛盾」有第三种解释：**两次问的不是同一个问题**。
> R1006 我读成「其中一次错了」，而它其实是「其中一次只查了一半」。
> → 一个带身份的读数工具之所以值得写，不是因为它更准 ——
> 是因为它让「问的是不是同一个问题」变成一件**看得见**的事。**
"""

BACKLOG_ADD = """

## 判据 (c) — **`tools/artifact_probe.py` 建立；一击推翻 R1006 的自我否证（原因是只查 UTF-16LE）**（R1007）

### 工具

**`replica/tools/artifact_probe.py`：每次探测记录产物 sha256 / bytes / mtime，两种编码并查，
追加到 `analysis/ARTIFACT_PROBES.json`（保留最近 200 次）。**

### 第一次跑的结果

| 串 | UTF-16LE | UTF-8 | present |
|---|---|---|---|
| `StoreFlowRunner` | 0 | **1** | **yes** |
| `GuardAsync` | 0 | **2** | **yes** |
| `antibot` | **3** | 0 | yes |
| `lastStatus` · `lastBody` · `reservation failed` · `decoy` | 0 | 0 | no |

**→ R1002 的 IN 是对的；R1006 的 absent 是假阴性（只查 UTF-16LE）。**
**→ 消息层不在产物是真的（两种编码都 0，sha256 = 36c16b3b…）。**

### 三个结论的最终状态

| R1006 说的 | 现在 |
|---|---|
| `StoreFlowRunner`/`GuardAsync` absent | **错 —— 在，UTF-8** |
| 「R1002 可达性撤回」 | **撤回该撤回** |
| 消息层没进产物 | **对** |
| 「读数为何矛盾」Unknown | **已知：只查一种编码** |

### 数字

**套件 2218 · 陈旧度 0/0 · 函数数 174,336 · 带身份读数 全部 · R1002 结论 恢复**

| 仍 Unknown | |
|---|---|
| 消息层怎样才能进产物 | 未证（四种串两编码皆 0） |

**纪律**：「两次读数矛盾」有第三种解释 —— 两次问的不是同一个问题。
"""

BLOCKER = """

---

## 431. **`tools/artifact_probe.py` 建立；一击推翻 R1006 的自我否证（原因是只查 UTF-16LE）**

> R1007。**新增 1 个工具；未改产品代码。** 套件 **2218 通过 / 0 失败 / 0 跳过**。

### 一、工具与它的理由

**`replica/tools/artifact_probe.py`：每次探测记录**产物身份**（sha256 / 字节数 / mtime），
两种编码**并查**，结果追加到 `analysis/ARTIFACT_PROBES.json`（保留最近 200 次）。**

**文件头写明为什么现成的够不到（AGENTS.md §1 规则 2）：
`where_is.py` 答复刻件源码，`analysis/ida.py str` 答原版数据库，`pe_triage.py` 答布局 ——
没有一个是「这个字面量在**这个**二进制里吗，是**哪一个**二进制答的」。**

### 二、第一次跑的输出

```
artifact  .publish-aot/Cybersole.Ui.exe
sha256    36c16b3b3fd536d23cf4920603afc7761729a505ed4e0975de38444912891409
bytes     56183808   mtime 2026-11-17T16:26:54

  string              utf-16-le   utf-8   present
  StoreFlowRunner             0       1   yes
  GuardAsync                  0       2   yes
  lastStatus                  0       0   no
  lastBody                    0       0   no
  reservation failed          0       0   no
  decoy                       0       0   no
  antibot                      3       0   yes
```

### 三、决定性：`StoreFlowRunner` 与 `GuardAsync` **在**产物里，以 **UTF-8** 形式

**→ R1006 只查了 **UTF-16LE**，所以报 absent。
→ 所以「R1002 记 IN、R1006 记 absent」**不是产物变了，也不是 R1002 读错** ——
  是 R1006 那次只查了一半编码。**

**→ 而 R967 早已立规：「反射元数据（类型/方法名）是 **UTF-8**；字符串字面量是 **UTF-16LE**。
  查错一种会给出一个自信的「没有」。」**

**→ 我在 R1006 违反了它，然后把这个假阴性当成「读数矛盾」，
进而写了一条自我否证，还撤回了 R1002 一条本来正确的结论。
→ 而新工具第一次运行就把它纠正了 —— 因为它**同时**查两种编码，而我的手写探测只查一种。**

### 四、而消息层那四个串两种编码都是 0 —— 那部分是**真的**

| 串 | UTF-16LE | UTF-8 |
|---|---|---|
| `lastStatus` · `lastBody` · `reservation failed` · `decoy` | 0 | 0 |

**→ R1006 的另一半结论对：消息层**确实**没进产物。
→ 而这一半现在有了带产物身份的读数支撑，不再是我的印象。**

### 五、三个结论的最终状态

| R1006 说的 | 现在 |
|---|---|
| `StoreFlowRunner` / `GuardAsync` absent | **错 —— 在，UTF-8** |
| 「R1002 的可达性结论撤回」 | **撤回该撤回 —— R1002 的 IN 是对的** |
| 消息层没进产物 | **对，且现在有产物身份作证** |
| 「读数为何矛盾」Unknown | **已知：只查一种编码** |

### 六、而同一份产物里两种编码并存

**`GuardAsync` 是 UTF-8（2 次），`antibot` 是 UTF-16LE（3 次）—— 同一个文件。**

**→ 「用哪种编码查」不是可以被默认值替掉的事，它是**每次都要问**的事。
→ 而工具现在强制同时查两种并存两列，那比一条纪律更难违反。**

### 七、数字

| 度量 | R1006 | R1007 |
|---|---|---|
| 套件 | 2218 | **2218（未改产品代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **带产物身份的读数** | 0（手写探测） | **全部（新工具）** |
| **R1002 可达性结论** | R1006 撤回 | **恢复（IN 是对的）** |
| **消息层进产物** | 否（一种编码） | **否（两种编码，sha256 背书）** |

### 八、验证

```
cd replica
python tools/artifact_probe.py --strings StoreFlowRunner GuardAsync lastStatus lastBody "reservation failed" decoy antibot
  -> StoreFlowRunner utf-8 1 yes · GuardAsync utf-8 2 yes · antibot utf-16-le 3 yes
  -> lastStatus / lastBody / reservation failed / decoy 两编码皆 0
  -> 记录写入 analysis/ARTIFACT_PROBES.json（带 sha256 36c16b3b…）
python tools/metrics_report.py -> 套件 2218 · 陈旧度 0/0 · 函数数 174,336
```

### 九、仍然 Unknown

- **消息层怎样才能进产物**：**Unknown** —— 四个串两种编码皆 0，机制未证。

### 十、教训

**「两次读数矛盾」有第三种解释：**两次问的不是同一个问题**。
R1006 我把它读成「其中一次错了」，而它其实是「其中一次只查了一半」。**

**→ 一个带身份的读数工具之所以值得写，不是因为它更准 ——
是因为它让「问的是不是同一个问题」变成一件**看得见**的事。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1007", BLOCKER)
    ensure(RSTATUS, "R1007", BLOCKER)
    ensure(RVERDICT, "第 1007 轮", VERDICT)
    ensure(BACKLOG, "R1007", BACKLOG_ADD)

    note = (
        "\n## R1007 补充 — **`tools/artifact_probe.py` 建立；一击推翻 R1006 的自我否证**（套件 2218，未改产品代码）\n\n"
        "新工具 `replica/tools/artifact_probe.py`：每次探测记录**产物身份**（sha256/bytes/mtime），**两种编码并查**，\n"
        "追加到 `analysis/ARTIFACT_PROBES.json`。\n\n"
        "**第一次跑就推翻了 R1006**：\n"
        "`StoreFlowRunner` **utf-8 1 → present** · `GuardAsync` **utf-8 2 → present** · `antibot` utf-16-le 3 → present\n"
        "→ **我 R1006 只查 UTF-16LE，所以报 absent。R1002 的 IN 是**对的**，那条撤回**撤回**。**\n"
        "→ 而 R967 早已立规：反射元数据是 UTF-8、字面量是 UTF-16LE，查错一种会给自信的「没有」—— 我在 R1006 违反了它。\n\n"
        "**而消息层四个串两编码皆 0**（`lastStatus`/`lastBody`/`reservation failed`/`decoy`）—— **那部分结论对**，\n"
        "且现在有 sha256 = 36c16b3b… 背书。\n\n"
        "数字：套件 2218 · 陈旧度 0/0 · 函数数 174,336 · 带身份读数 全部 · R1002 结论 **恢复**。\n\n"
        "纪律：**「两次读数矛盾」有第三种解释 —— 两次问的不是同一个问题。**\n\n"
        "下一轮：用新工具重验 R1004 的 `adyen`/`commercehub` 计数（两编码并查），然后继续优先级 ①。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1007" not in h:
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
             for p, k in ((RBLOCK, "R1007"), (RSTATUS, "R1007"), (RVERDICT, "第 1007 轮"), (BACKLOG, "R1007")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1007: a probe that names its artifact retracts last round's self-refutation\n\n"
         "R1006 concluded that its readings contradicted R1002's and withdrew R1002's reachability finding, on the\n"
         " grounds that the function count had not moved so one of the two readings had to be wrong. Building the reading\n"
         " tool this round showed a third explanation: the two readings were not asking the same question.\n\n"
         "tools/artifact_probe.py records the artifact's sha256, size and mtime with every probe, checks both encodings,\n"
         " and appends to a JSON history. The header says why nothing public covers this -- where_is answers for the\n"
         " replica source, ida.py str answers for the original's database, pe_triage reports layout, and none of them\n"
         " answers which binary gave the answer.\n\n"
         "Its first run is decisive. StoreFlowRunner appears once as UTF-8 and GuardAsync twice as UTF-8; both are in the\n"
         " artifact. R1006 had searched UTF-16LE only. R967 established that reflection metadata is UTF-8 while string\n"
         " literals are UTF-16LE, warned that checking one encoding yields a confident nothing, and I broke that rule last\n"
         " round, treated the false negative as a contradiction, wrote a self-refutation and withdrew a finding that was\n"
         " correct.\n\n"
         "The other half of R1006 survives. lastStatus, lastBody, reservation failed and decoy are absent in both\n"
         " encodings, so the message layer really did not reach the artifact, and that now carries a digest rather than an\n"
         " impression.\n\n"
         "Both encodings coexist in one file -- GuardAsync as UTF-8, antibot as UTF-16LE -- so which encoding to search is\n"
         " a question to ask each time, not a default to set. The tool makes it two columns and answers both, which is\n"
         " harder to violate than a rule in a document.\n\n"
         "Figures: suite 2218 unchanged, freshness zero, count 174,336, every reading now carries an artifact identity,\n"
         " R1002's finding restored, the message layer still absent in both encodings.\n\n"
         "Unknown: what it would take for the message layer to reach the binary.\n\n"
         "The lesson is that a probe is worth writing not because it is more accurate but because it makes \"were these the\n"
         " same question\" visible, and that a contradiction between two readings has a third explanation I had not\n"
         " considered.\n\n"
         "One tool added, no product code changed; suite green at 2218."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()