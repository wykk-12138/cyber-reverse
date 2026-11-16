"""Record R926: KeyGesture implemented, and the duplicate tool I wrote before checking."""

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
### 判据 (a)：17 个类型缺失分类结案，并补了 `KeyGesture`（R926）

**(f) 闭合后转向 (a)。METRICS 里 (a) 的现状：类型级缺口 **0**、文案缺口 **0**、**类型缺失 17**。**

### 而 17 个里 10 个是 UI

**4 个 `Localize*Extension` + 6 个 View/Window —— 按优先级 ④ 本来就延后。
所以真正要查的是另外 7 个。**

### 查那 7 个时，我先犯了一个错

**我写了一个 100 行的分类工具放在 `replica/tools/type_presence_triage.py`。**

**而 `analysis/type_presence_triage.py` **早就存在** —— R619 的 298 行版本，
还会数成员覆盖率（不只判「有没有声明」）。**
**而且有一个测试 `TypePresenceTriageTests` 一直在守它。**

> **§2.7c 又一次：写之前没跑 `where_is type_presence`。
> 我写的那 100 行是更差的重复品，而它存在的证据是一个我没读的测试。**

**所以删掉了重复品，改用真的那个。**

### 真的那个为什么红了

**它的 `ABSENT` 表是**从 bind_diff 拷的快照**，硬编码 17 个名字。
我补了 `KeyGesture` 之后 bind_diff 报 16，而快照还有 17 → 工具自检失败、exit 1。**

**修法：加一个 `RESOLVED` 分支 —— 已经有同名声明的类型**退出缺失计数**并单独报出。
**因为一个已经补上的缺口不该继续被数。**

### 而分类结果

| 判定 | 数 | 含义 |
|---|---|---|
| **OUT_OF_SCOPE** | 2 | 授权/许可见 `DECISION_LICENSE_OUT_OF_SCOPE.md` |
| **RENAMED** | 6 | 改名了，映射已记 |
| **STRUCTURAL** | 1 | 结构不同 |
| **UNKNOWN（非区分匹配）** | 1 | 多个候选分不开 |
| **UNKNOWN（非区分）** | 6 | 同上 |

**共 16 行 = bind_diff 的 16 = `ABSENT` 17 减 1 个 RESOLVED。**

### 写了 `KeyGesture`

| 成员 | |
|---|---|
| `Key` · `Modifiers` | **bindings 声明的两个名字** |
| `IsEmpty` | 未绑定是一种要显示、要处理的状态 |
| `Equals` / `==` | **忽略大小写** —— `d` 与 `D` 是一个绑定 |
| `ToString` / `TryParse` | **往返**是这类值存在的理由 |

**而 `Modifiers` 是 flags 而不是字符串：**文本形式要在读取时解析、显示时格式化，两边会分歧；
**而一次大小写滑动就把一个能用的绑定变成死的。**

### 而测试抓到一件真事

**`shift+ctrl+d` 第一次解析出的 `ToString` 是 `Ctrl+Shift+d` 而不是 `Ctrl+Shift+D` ——
单字符键没规范化。**

**修在构造函数里而不是 `ToString` 里，**让值与其文本一致**。
**而那正是这个类型存在要防的那类滑动。****

### 数字

| 度量 | R925 | **R926** |
|---|---|---|
| 套件 | 1896 | **1911** |
| **类型缺失** | 17 | **16** |
| 分类结案 | 无 | **16 行全部带判定** |

### 教训

> **这一轮我做了两件相反的事：补了 `KeyGesture`（真的进展），同时写了一个早已存在的工具的重复品（真的退步）。**
> **而发现重复品的方式是**一个测试红了** —— 不是因为我查了。**
> **§2.7c 写在那里，而我在它存在的第六次上又犯了一次，唯一不同的是这次它有一道防线。**
"""

if "判据 (a)：17 个类型缺失分类结案" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R926 appended")

VERDICT = """

---

## 第 926 轮：(a) 的 17 个类型缺失分类结案，并补了 `KeyGesture`

### 17 个里 10 个是 UI

**4 个 `Localize*Extension` + 6 个 View/Window → 按优先级 ④ 延后。真正要查的是另外 7 个。**

### 而查那 7 个时我先犯了一个错

**我写了一个 100 行的分类工具放在 `replica/tools/`。而 `analysis/type_presence_triage.py`
**早就存在** —— R619 的 298 行版本，会数成员覆盖率，**而且有一个测试一直在守它。****

> **§2.7c 又一次：写之前没跑 `where_is`。我写的那 100 行是更差的重复品，
> 而它存在的证据是一个我没读的测试。**

**删掉了重复品。**

### 真的那个为什么红了

**`ABSENT` 表是从 bind_diff 拷的**快照**，硬编码 17 个名字。我补了 `KeyGesture` 后 bind_diff 报 16，
快照还有 17 → 工具自检失败。**

**修法：加 `RESOLVED` 分支 —— 已有同名声明的类型**退出缺失计数**并单独报出。一个已补上的缺口不该继续被数。**

### 分类结果（16 行 = 17 减 1 个 RESOLVED）

| 判定 | 数 |
|---|---|
| OUT_OF_SCOPE（授权/许可决定） | 2 |
| **RENAMED（映射已记）** | **6** |
| STRUCTURAL | 1 |
| UNKNOWN（非区分匹配 / 非区分） | 1 + 6 |

### `KeyGesture`

**`Key` · `Modifiers`（bindings 的两个名字）· `IsEmpty` · `Equals`（**忽略大小写**）· `ToString`/`TryParse`（**往返**）**

> **`Modifiers` 用 flags 不用字符串：文本要在读取时解析、显示时格式化，两边会分歧；
> 而一次大小写滑动就把一个能用的绑定变成死的。**

### 而测试抓到一件真事

**`shift+ctrl+d` 第一次 `ToString` 出 `Ctrl+Shift+d` —— 单字符键没规范化。
修在构造函数里而不是 `ToString` 里，让值与其文本一致 —— 那正是这个类型存在要防的那类滑动。**

### 数字

| 度量 | R925 | **R926** |
|---|---|---|
| 套件 | 1896 | **1911** |
| 类型缺失 | 17 | **16** |
| 分类结案 | 无 | **16 行全部带判定** |

### 教训

> **这一轮我做了两件相反的事：补了 `KeyGesture`（真进展），同时写了一个早已存在的工具的重复品（真退步）。**
> **而发现重复品的方式是**一个测试红了** —— 不是因为我查了。**
"""

BACKLOG_ADD = """

## 判据 (a) — 类型缺失 **17 → 16**，16 行分类结案（R926，**改产品代码 + 改 analysis 工具 +15 用例**）

### 分类

| 判定 | 数 | 含义 |
|---|---|---|
| OUT_OF_SCOPE | 2 | 授权/许可，见 `DECISION_LICENSE_OUT_OF_SCOPE.md` |
| **RENAMED** | **6** | 改名，映射已记 |
| STRUCTURAL | 1 | 结构不同 |
| UNKNOWN | 7 | 非区分匹配 1 + 非区分 6 |

**10 个 UI 类型（4 Localize + 6 View/Window）按优先级 ④ 延后。**

### `Cybersole.Core/KeyInput/KeyGesture.cs`

**`Key` · `Modifiers` · `IsEmpty` · `Equals`（忽略大小写）· `ToString`/`TryParse`（往返）**

### 两个修

**① 删掉我写的重复工具（`replica/tools/type_presence_triage.py`）—— `analysis/` 下 R619 的 298 行版本早就存在。**
**② `analysis/type_presence_triage.py` 加 `RESOLVED` 分支 —— 快照里已实现的类型退出缺失计数。**

### 一次真发现

**`shift+ctrl+d` 的 `ToString` 出 `Ctrl+Shift+d` → 单字符键未规范化 → 修在构造函数里，让值与其文本一致。**

### 数字

**套件 1896 → 1911 · 类型缺失 17 → **16** · 分类结案 16 行**

| 仍 Unknown | |
|---|---|
| 7 个 UNKNOWN 判定 | 非区分匹配 / 候选分不开 |
| 2 个 OUT_OF_SCOPE | 已有裁决文件 |
| 剩 6 个 RENAMED 的成员是否齐 | 覆盖率是下界 |

**纪律**：**§2.7c 我犯到第六次，唯一不同的是这次有一道防线（一个我没读的测试）把它抓住了。**
"""

BLOCKER = """

---

## 350. 类型缺失 17 → 16；16 行分类结案；而我写了一个早已存在的工具的重复品

> R926。**改产品代码 + 改 analysis 工具 +15 用例。** 套件 **1911 通过 / 0 失败 / 0 跳过**。

### 一、17 个里 10 个是 UI

**4 个 `Localize*Extension` + 6 个 View/Window → 优先级 ④ 延后。真正要查的是另外 7 个。**

### 二、而我先犯了一个错

**我写了 100 行的分类工具放 `replica/tools/`。而 `analysis/type_presence_triage.py` **早就存在** ——
R619 的 298 行版本，会数成员覆盖率，**而且有测试 `TypePresenceTriageTests` 一直在守它。**

**→ §2.7c 又一次。删掉重复品。**

### 三、真的那个为什么红了

**`ABSENT` 表是从 bind_diff 拷的快照，硬编码 17 个名字。补了 `KeyGesture` 后 bind_diff 报 16 → 自检失败 exit 1。**

**修：加 `RESOLVED` 分支 —— 已有同名声明的类型退出缺失计数并单独报出。**

### 四、分类结果

| 判定 | 数 |
|---|---|
| OUT_OF_SCOPE | 2 |
| **RENAMED** | **6** |
| STRUCTURAL | 1 |
| UNKNOWN（非区分匹配 / 非区分） | 1 + 6 |

**16 行 = bind_diff 的 16 = 快照 17 − 1 个 RESOLVED。**

### 五、`Cybersole.Core/KeyInput/KeyGesture.cs`

**`Key` · `Modifiers`（bindings 的两个名字）· `IsEmpty` · `Equals`（忽略大小写）· `ToString`/`TryParse`（往返）**

**`Modifiers` 用 flags：文本要在读取时解析、显示时格式化，两边会分歧；一次大小写滑动就把能用的绑定变成死的。**

### 六、一次真发现

**`shift+ctrl+d` 第一次 `ToString` 出 `Ctrl+Shift+d` —— 单字符键未规范化。
修在构造函数里而不是 `ToString` 里：**让值与其文本一致**。**

### 七、数字

| 度量 | R925 | R926 |
|---|---|---|
| 套件 | 1896 | **1911** |
| **类型缺失** | 17 | **16** |
| 分类结案 | 无 | **16 行** |

### 八、验证

```
analysis/type_presence_triage.py -> resolved: KeyGesture · triage rows: 16 · exit 0
test --filter KeyGestureTests    -> 15 通过
test --filter TypePresenceTriageTests -> 通过
metrics_report.py                -> 1911 通过 / 0 失败；类型缺失 16
```

### 九、仍然 Unknown

- **7 个 UNKNOWN 判定**：**Unknown** —— 非区分匹配或候选分不开。
- **2 个 OUT_OF_SCOPE**：**已有裁决文件**，非本轮判断。
- **剩 6 个 RENAMED 的成员是否齐**：**Unknown** —— 覆盖率是下界。

### 十、教训

**这一轮我做了两件相反的事：补了 `KeyGesture`（真进展），同时写了一个早已存在的工具的重复品（真退步）。**

**而发现重复品的方式是**一个测试红了** —— 不是因为我查了。**

**§2.7c 写在那里，而我在它存在的第六次上又犯了一次，唯一不同的是这次它有一道防线。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R926", BLOCKER)
    ensure(RSTATUS, "R926", BLOCKER)
    ensure(RVERDICT, "第 926 轮", VERDICT)
    ensure(BACKLOG, "R926", BACKLOG_ADD)

    note = (
        "\n## R926 补充 — 类型缺失 17→16，16 行分类结案（改产品代码 + 改 analysis 工具 +15 用例，套件 1911）\n\n"
        "17 个里 10 个是 UI（优先级 ④ 延后）。剩余 7 个查了。\n\n"
        "而我先犯了一个错：写了 100 行分类工具放 replica/tools/，而 analysis/type_presence_triage.py 早就存在"
        "（R619 的 298 行，会数成员覆盖率，且有 TypePresenceTriageTests 在守）→ §2.7c 又一次，删掉重复品。\n\n"
        "真的那个红的原因：ABSENT 表是硬编码快照 17 个名字，补了 KeyGesture 后 bind_diff 报 16 → 自检失败。"
        "修：加 RESOLVED 分支，已实现的类型退出缺失计数。\n\n"
        "分类：OUT_OF_SCOPE 2 · RENAMED 6 · STRUCTURAL 1 · UNKNOWN 7 —— 16 行 = 快照 17 − 1 RESOLVED。\n\n"
        "新增 Cybersole.Core/KeyInput/KeyGesture.cs：Key · Modifiers（flags）· IsEmpty · Equals（忽略大小写）· ToString/TryParse（往返）。\n"
        "测试抓到：单字符键未规范化 → shift+ctrl+d 出 Ctrl+Shift+d → 修在构造函数里让值与其文本一致。\n\n"
        "数字：套件 1896 → 1911 · 类型缺失 17 → 16。\n\n"
        "下一轮：剩 7 个 UNKNOWN 判定里的非区分匹配那一个；或 6 个 RENAMED 的成员补齐（覆盖率是下界）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R926" not in h:
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
             for p, k in ((RBLOCK, "R926"), (RSTATUS, "R926"), (RVERDICT, "第 926 轮"), (BACKLOG, "R926")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R926: KeyGesture implemented, and a duplicate of a tool that already existed\n\n"
         "Criterion (a) after (f) closed. Of the seventeen types bind_diff reports absent, ten are Ui and deferred by the\n"
         " priority order, so seven needed looking at -- and looking at them I first wrote a hundred-line triage tool in\n"
         " replica/tools, when analysis/type_presence_triage.py has existed since R619 at 298 lines, scores member\n"
         " coverage as well as declarations, and has a test guarding it. That is section 2.7c for the sixth time, and\n"
         " the only difference this time is that a test I had not read caught it.\n\n"
         "With the duplicate deleted, the real tool failed for a reason worth keeping: its ABSENT table is a snapshot\n"
         " copied from bind_diff, so once KeyGesture had a declaration the snapshot still held seventeen while bind_diff\n"
         " reported sixteen, and the tool's own check refused to run. A type that has acquired a declaration is now\n"
         " RESOLVED -- reported separately and removed from the absent count, because a gap that has closed should not\n"
         " keep being counted.\n\n"
         "The classification is complete: two out of scope by an existing decision, six renamed with the mapping\n"
         " recorded, one structural, seven unknown because the candidates cannot be told apart. Sixteen rows against\n"
         " bind_diff's sixteen.\n\n"
         "KeyGesture is the type added: the two members the bindings declare, an explicit empty state, case-insensitive\n"
         " equality and a text round trip. Modifiers are flags rather than text because a string has to be parsed where\n"
         " it is read and formatted where it is shown, and the two can disagree -- one case slip turns a working binding\n"
         " into a dead one. The tests found exactly that: shift+ctrl+d first produced Ctrl+Shift+d because a\n"
         " single-character key was not normalised, and the fix went into the constructor so that the value and its\n"
         " text agree.\n\n"
         "Figures: suite 1896 to 1911, absent types seventeen to sixteen, and all sixteen rows now carry a verdict.\n\n"
         "Unknown: the seven unknown verdicts, where candidates cannot be distinguished; the two out-of-scope ones,\n"
         " which rest on a decision rather than on this round; and whether the six renamed types have all their members,\n"
         " since coverage is a lower bound.\n\n"
         "The lesson is that this round did two opposite things at once -- real progress on a type, and a real\n"
         " regression in writing a duplicate -- and the regression was found by a test firing rather than by my\n"
         " checking.\n\n"
         "Product code and an analysis tool changed; suite green at 1911."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()