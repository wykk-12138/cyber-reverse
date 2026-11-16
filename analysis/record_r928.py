"""Record R928: the reverse direction of the settings-schema pin, and the four unmatched members."""

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
### 设置 schema 的**反方向**：48 个属性对 44 个键，差 4 个，每个都有理由（R928）

**R927 那条钉只查一个方向：**每个恢复到的键都有属性**。
**而反方向没人查 —— 那里才是 1:1 违规能藏的地方：一个复刻件写出去、原版从不写的键。**

### 限定到 `GlobalSettings` 类体：48 属性 vs 44 键

**差 4 个：`EnableClock` · `ClockFormat` · `MonitorConcurrency` · `StoreGroups`。**

### 而每一个的答案都不同

| 属性 | 结论 | 依据 |
|---|---|---|
| **`EnableClock`** | **原版的，只是备份早于它** | **R198 注记指向 locale 的 `Settings.General.EnableClock`（带 tooltip）** |
| `ClockFormat` | 不在绑定契约里 | 契约没有这个名字 |
| `StoreGroups` | 不在绑定契约里 | 同上 |
| **`MonitorConcurrency`** | **仍然开着的问题** | **契约**有**它，而 `concurrency` 键已被嵌套的 `ConcurrencySettings` 占掉** |

### 所以「差 4 个」不是「4 个 bug」

**而 `EnableClock` 那一条最有价值：它证明**备份早于属性**这件事是真的可能**，不是我为差异找的借口。**

> **判据：一条 locale 键带 tooltip。那是原版自己的字符串，不是我的推断。
> 所以这个属性在原版里，而 44 键备份里没有它 —— **两份证据都真，只是来自不同版本**。**

### 而 `MonitorConcurrency` 是这一轮唯一没有答案的那一个

**契约说 `Settings` 有它（`int`），备份说 `concurrency` 是个对象（`ConcurrencySettings`，契约里 `Models.Concurrency` 的映射）。
**两个都对，而它们不能是同一个成员。**

**所以钉住这个矛盾本身**，让问题不会消失：
**一个测例断言 `MonitorConcurrency` 是 `int`、`Concurrency` 不是、且两者序列化名不同。**
**这样某天有人「顺手统一」它们时，会先红。**

### 新增 4 个测例

| 测例 | 守什么 |
|---|---|
| `TheUnmatchedMembersAreTheExpectedFourAndEachHasAReason` | 恰好这 4 个，顺序无关但集合固定 |
| `EnableClockIsOriginalDespiteHavingNoKey` | 有 locale 键为证 |
| `ClockFormatAndStoreGroupsAreNotInTheContract` | 不在契约里 |
| `MonitorConcurrencyIsAContractMemberWithNoKeyAndConcurrencyIsObject` | **矛盾本身** |

### 数字

| 度量 | R927 | **R928** |
|---|---|---|
| 套件 | 1911 | **1915** |
| 设置属性 / 恢复键 | 48 / 44（未解释） | **48 / 44，4 个每个有理由** |
| 类型缺失 | 16 | 16 |

### 教训

> **一个度量报「48 对 44」，而它不告诉你是 4 个缺失还是 4 个多余 —— 这两个是完全不同的问题，
> 一个要补，一个要删。**
> **而这四个里三个是「多余但合法」，一个是「两边都对而互相冲突」。
> 四种情况，一个数字。**
"""

if "设置 schema 的**反方向**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R928 appended")

VERDICT = """

---

## 第 928 轮：设置 schema 的反方向 —— 48 属性 vs 44 键，差 4 个每个有理由

### 反方向才是 1:1 违规能藏的地方

**R927 那条钉只查「每个键都有属性」。反方向 —— **每个属性都在文件里** —— 没人查。
**而一个复刻件写出去、原版从不写的键，就在那里。****

### 限定到类体：48 vs 44，差 4

| 属性 | 结论 | 依据 |
|---|---|---|
| **`EnableClock`** | **原版的，备份早于它** | **R198：locale 有 `Settings.General.EnableClock`（带 tooltip）** |
| `ClockFormat` | 不在绑定契约 | 契约无此名 |
| `StoreGroups` | 不在绑定契约 | 同上 |
| **`MonitorConcurrency`** | **仍开着** | **契约有它（int），而 `concurrency` 已被 `ConcurrencySettings` 占掉** |

### 「差 4 个」不是「4 个 bug」

**`EnableClock` 那条最有价值：它证明「备份早于属性」是真的可能，不是借口。
**依据是一条 locale 键带 tooltip —— 原版自己的字符串，不是我的推断。
两份证据都真，只是来自不同版本。****

### 而 `MonitorConcurrency` 是唯一没答案的

**契约说它是 `int`，备份说 `concurrency` 是对象。两个都对，而它们不能是同一个成员。**

**所以钉住矛盾本身** —— 某天有人「顺手统一」时，会先红。

### 新增 4 个测例

**集合固定 · `EnableClock` 有 locale 为证 · 两个不在契约里 · **矛盾本身****

### 数字

| 度量 | R927 | **R928** |
|---|---|---|
| 套件 | 1911 | **1915** |
| 设置 48/44 | 未解释 | **4 个每个有理由** |
| 类型缺失 | 16 | 16 |

### 教训

> **「48 对 44」不说你是 4 个缺失还是 4 个多余 —— 一个要补，一个要删，是完全不同的问题。
> 而这四个里三个是「多余但合法」，一个是「两边都对而互相冲突」。四种情况，一个数字。**
"""

BACKLOG_ADD = """

## 判据 (a)/数据契约 — 设置 schema 反方向：48 属性 vs 44 键，差 4 每个有理由（R928，**+4 用例**）

### 反方向此前无人查

**既有钉只查「键 → 属性」。反方向（属性 → 键）才是 1:1 违规能藏处。**

### 4 个差

| 属性 | 结论 |
|---|---|
| **`EnableClock`** | **原版的 —— R198 locale 有 `Settings.General.EnableClock`（带 tooltip）** |
| `ClockFormat` | 不在绑定契约 |
| `StoreGroups` | 不在绑定契约 |
| **`MonitorConcurrency`** | **仍开着：契约有（int），而 `concurrency` 是嵌套对象** |

### `SettingsUnmatchedMembersTests`（4 例）

**集合固定 · `EnableClock` 有 locale 为证 · 两个不在契约 · **钉住 `MonitorConcurrency` 与 `Concurrency` 的矛盾****

### 数字

**套件 1911 → 1915 · 设置 48/44 从「未解释」到「4 个每个有理由」· 类型缺失 16**

| 仍 Unknown | |
|---|---|
| `MonitorConcurrency` 的持久化形态 | 契约有、键被占，两边都对而冲突 |
| `ClockFormat` / `StoreGroups` 是否该持久化 | 不在契约里 |
| 44 键备份的版本 | 至少早于 `EnableClock` |

**纪律**：「48 对 44」不说你是缺 4 个还是多 4 个。四种情况，一个数字。
"""

BLOCKER = """

---

## 352. 设置 schema 反方向：48 属性 vs 44 键，差 4 个每个有理由

> R928。**+4 用例，未改产品代码。** 套件 **1915 通过 / 0 失败 / 0 跳过**。

### 一、反方向此前无人查

**`LiveSchemaPinsTests` 只查「每个恢复键都有属性」。反方向 —— 每个属性是否都在文件里 —— 没人查。
而一个复刻件写出去、原版从不写的键，就在那里。**

### 二、限定到 `GlobalSettings` 类体：48 属性 vs 44 键

| 属性 | 结论 | 依据 |
|---|---|---|
| **`EnableClock`** | **原版的，备份早于它** | **R198：locale 有 `Settings.General.EnableClock`（带 tooltip）** |
| `ClockFormat` | 不在绑定契约 | 契约无此名 |
| `StoreGroups` | 不在绑定契约 | 同上 |
| **`MonitorConcurrency`** | **仍开着** | **契约有（int）；`concurrency` 已被 `ConcurrencySettings` 占** |

### 三、`EnableClock` 那一条为什么最有价值

**它证明「备份早于属性」不是我为差异找的借口 ——
依据是一条 locale 键带 tooltip，那是原版自己的字符串。
两份证据都真，只是来自不同版本。**

### 四、而 `MonitorConcurrency` 钉的是矛盾本身

**契约说 `int`，备份说 `concurrency` 是对象 —— 两个都对，不能是同一成员。
钉住它，某天有人「顺手统一」时先红。**

### 五、`SettingsUnmatchedMembersTests`（4 例）

**集合固定 · `EnableClock` 有 locale 为证 · 两个不在契约 · 矛盾本身**

### 六、数字

| 度量 | R927 | R928 |
|---|---|---|
| 套件 | 1911 | **1915** |
| 设置 48/44 | 未解释 | **4 个每个有理由** |
| 类型缺失 | 16 | 16 |

### 七、验证

```
test --filter SettingsUnmatchedMembersTests -> 4 通过
metrics_report.py                           -> 1915 通过 / 0 失败
```

### 八、仍然 Unknown

- **`MonitorConcurrency` 的持久化形态**：**Unknown** —— 契约有、键被占。
- **`ClockFormat` / `StoreGroups` 是否该持久化**：**Unknown** —— 不在契约里。
- **44 键备份的版本**：**Unknown** —— 至少早于 `EnableClock`。

### 九、教训

**「48 对 44」不说你是缺 4 个还是多 4 个 —— 一个要补，一个要删，完全不同的问题。**

**而这四个里三个是「多余但合法」，一个是「两边都对而互相冲突」。四种情况，一个数字。**

**所以一个差额要逐个问过，才能从「4」变成「3 个已知 + 1 个待解」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R928", BLOCKER)
    ensure(RSTATUS, "R928", BLOCKER)
    ensure(RVERDICT, "第 928 轮", VERDICT)
    ensure(BACKLOG, "R928", BACKLOG_ADD)

    note = (
        "\n## R928 补充 — 设置 schema 反方向：48 属性 vs 44 键，差 4 每个有理由（+4 用例，套件 1915）\n\n"
        "既有钉只查「键→属性」，反方向（属性→键）才是 1:1 违规能藏处。\n\n"
        "差 4：EnableClock（原版的 —— R198 locale 有 Settings.General.EnableClock 带 tooltip，证明备份早于属性）· "
        "ClockFormat / StoreGroups（不在绑定契约）· MonitorConcurrency（仍开着：契约有 int，而 concurrency 已被 "
        "ConcurrencySettings 占）。\n\n"
        "SettingsUnmatchedMembersTests 4 例：集合固定 · EnableClock 有 locale 为证 · 两个不在契约 · 钉住矛盾本身。\n\n"
        "数字：套件 1911 → 1915 · 设置 48/44 从「未解释」到「4 个每个有理由」。\n\n"
        "纪律：「48 对 44」不说你是缺 4 个还是多 4 个 —— 一个要补一个要删。四种情况，一个数字。\n\n"
        "下一轮：MonitorConcurrency 的持久化形态（契约有、键被占）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R928" not in h:
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
             for p, k in ((RBLOCK, "R928"), (RSTATUS, "R928"), (RVERDICT, "第 928 轮"), (BACKLOG, "R928")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R928: the settings schema checked in the other direction, where a 1:1 violation would hide\n\n"
         "The existing pin checks that every key in the recovered backup has a property. Nothing checked the reverse,\n"
         " and that direction is where the interesting failure lives: a property the replica carries that the original\n"
         " does not would write a key the original's own files never hold.\n\n"
         "Scoped to the class body, the file has forty-eight properties against forty-four recovered keys, so four are\n"
         " unmatched -- and each has a different answer. EnableClock is the original's and simply postdates the backup,\n"
         " which R198 establishes from a locale entry named Settings.General.EnableClock carrying a tooltip: that is the\n"
         " original's own string, not an inference, so both pieces of evidence are true and come from different\n"
         " versions. ClockFormat and StoreGroups are in no binding contract at all. MonitorConcurrency stays open, since\n"
         " the contract has it as an int while the backup's concurrency key is an object already owned by\n"
         " ConcurrencySettings.\n\n"
         "So a difference of four is not four bugs. Three are extra but legitimate and one is two true facts that cannot\n"
         " be the same member -- four kinds of situation behind one number, and only asking each in turn turns the four\n"
         " into three knowns and one open question.\n\n"
         "Four tests pin it: the set is fixed, EnableClock carries its locale proof, two are absent from the contract,\n"
         " and the last pins the contradiction itself between MonitorConcurrency and Concurrency so that a later\n"
         " tidying-up that merges them fails first.\n\n"
         "Figures: suite 1911 to 1915, types absent unchanged at sixteen, and the settings pair goes from unexplained to\n"
         " four accounted for.\n\n"
         "Unknown: how MonitorConcurrency is persisted, given the contract has it and the key is taken; whether\n"
         " ClockFormat and StoreGroups should be persisted at all, neither being in the contract; and which version the\n"
         " forty-four-key backup came from, other than that it predates EnableClock.\n\n"
         "The lesson is that 48 against 44 does not say whether four are missing or four are extra. Those need opposite\n"
         " fixes, and the number alone cannot tell you which.\n\n"
         "Tests added; no product code changed; suite green at 1915."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()