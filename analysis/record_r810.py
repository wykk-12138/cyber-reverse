"""Record R810: retract R809's diagnosis -- the triage was consistent, I compared two different fields."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 234. **撤回 R809 的诊断**：triage 没有自相矛盾，是我拿两个不同字段在比

> R810。未改产品代码。这一轮的工作是把上一轮的错误诊断收回。

### 一、R809 我说了什么

> 「同一份数据、同一个正则、相反的结论 → 说明我扫的『类体』和它的 `bodies()` 收集器不是一个东西」

**这个推断是错的。**

### 二、这一轮做了什么

按上一轮自己写的结论（「该去读收集器，不是改正则」），我做了两件事：

1. **读 `bodies()`**：它用 `DECL` 找声明，然后**花括号配对取整类体（含嵌套类型）**，存成 `found[name] = [(file, body, doc)]`
2. **import 工具自己的 `bodies()` 和它自己的正则**，对 `SettingsShell` 跑一遍

**结果还是 1 存在 / 18 缺失 —— 和 R809 一致。**

**如果类体不同，用它的收集器就该得到 18。得到了 1，说明类体不是分歧点。**

### 三、真正的分歧：我在比两个不同的字段

判定代码里有**两个量**：

```python
named = sum(1 for m in members if re.search(r"\\b%s\\b" % re.escape(m), body))   # 裸名字出现
hit   = sum(1 for p in pats if p.search(body))                                  # 声明模式命中
```

- **`named` = 18** —— 用于 `STRUCTURAL` 判定
- **`hit` = 1** —— 用于 `RENAMED` / `PARTIAL` 判定

**而报告里的 `18/19` 是 `named`，我量的是 `hit`。**

**代码注释把这件事写得很清楚**（R682/R683 那条）：

> 「if the member NAMES appear anywhere in the source but not as declarations, the verdict is STRUCTURAL,
> not UNIMPLEMENTED. **Nothing about the measurement changes.**」

**所以 `STRUCTURAL` 的定义就是「名字出现过、但没作为声明出现」。**
**`SettingsView` 的 18/19 精确地是它声称的那个意思 —— 18 个名字在 `SettingsShell` 里出现过。**

**从来没有矛盾。** 我看了一个字段，报了另一个字段的数，然后说两者冲突。

### 四、`LogOut` 那个例子值得记

注释里还举了一个具体例子：

> `LogOut` 在 `SettingsShell.cs` 里出现过，而 `LogOut` 这个成员住在 `UserView` 上。

**这正是 shell 的合理结构**：一个外壳列着十九个视图/命令的名字，成员各自住在自己的视图里。
**十八个名字出现、一个在这里声明 —— 这不是缺陷，这是外壳该有的样子。**

**所以 `STRUCTURAL` 这个判定的名字选得比它读起来更准：它说的是结构，不是缺失。**

### 五、这是本会话第四次同一类错误，而这次最糟

| 轮 | 我的判断 | 真相 |
|---|---|---|
| R806 | 读取器读错位置 | **显示截断在 22 字符** |
| R807 | 18 个厂商缺口 | **拿 token 键当清单** |
| R809 | 类体口径不同 | **拿 `named` 和 `hit` 比** |
| **R810** | —— | **R809 的诊断本身要撤回** |

**前三次是「用错了一个工具的输出」。这一次是「用错了一个工具的一个字段」，而错完还写了诊断。**

**共同点不是粗心，是**：**我看到两个数字不一样，就直接推断"两边在量不同的东西"，但没有先问"这两个数字各自叫什么、由哪一行产生"。**

### 六、验证

```
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
TYPE_PRESENCE_TRIAGE.md 未改 —— 它本来就是对的
```

### 七、对判据 (a) 的意义

**17 条类型缺失的分类不变，而且现在更可信**：

- `OUT_OF_SCOPE` 2（YG R702）
- `RENAMED` 7
- **`STRUCTURAL` 1 —— 18/19 是"名字出现"，不是"成员声明"，这是它的准确定义**
- `UNKNOWN` 7（契约成员太少）

**判据 (a) 允许「不可得写 Unknown+缺什么」。这 17 条都写了。**

### 八、仍然 Unknown

- **`SettingsView` 的十九个成员里，哪一个在 `SettingsShell` 里也没出现过**：**Unknown** ——
  `named` 是 18/19，**但那一条是谁，我没单独列出**。**这一轮没查，因为查它不影响任何判定。**
- **`LogOut` 住在 `UserView` 上这件事**：来自工具注释，**我没独立验证**（Observation 转述）。

### 九、教训

**两个数字不一样，先问它们各自叫什么。**
**「两边在量不同的东西」是个结论，不是个起点 —— 而它听起来像起点。**
"""

VERDICT = """

---

## 第 810 轮：撤回上一轮的诊断

### R809 我说了什么

> 「同一份数据、同一个正则、相反的结论 → 说明我扫的『类体』和它的 `bodies()` 收集器不是一个东西」

**这个推断是错的。**

### 这一轮的做法

按上一轮自己写的结论，**去读收集器**：`bodies()` 用花括号配对取整类体（含嵌套类型）。
**然后 import 它的 `bodies()` 和它的正则，对 `SettingsShell` 再跑一遍 —— 结果还是 1/18。**

**如果类体不同，用它的收集器就该得到 18。得到 1，说明类体不是分歧点。**

### 真正的分歧：我在比两个不同的字段

```python
named = ...  # 裸名字出现        -> 18   （STRUCTURAL 判定用）
hit   = ...  # 声明模式命中      ->  1   （RENAMED / PARTIAL 判定用）
```

**报告的 `18/19` 是 `named`，我量的是 `hit`。**
**而代码注释写得很清楚：「名字出现过但没作为声明出现 → STRUCTURAL。Nothing about the measurement changes.」**

> **从来没有矛盾。我看了一个字段，报了另一个字段的数，然后说两者冲突。**

### `LogOut` 那个例子

注释里说：`LogOut` 在 `SettingsShell.cs` 里出现过，**而这个成员住在 `UserView` 上。**

**这正是 shell 的合理结构** —— 一个外壳列着十九个视图/命令的名字，成员各自住在自己的视图里。
**十八个名字出现、一个在这里声明，不是缺陷，是外壳该有的样子。**

### 这是第四次同一类错误，而这次最糟

| 轮 | 判断 | 真相 |
|---|---|---|
| R806 | 读取器读错位置 | 显示截断 22 字符 |
| R807 | 18 个厂商缺口 | token 键当清单 |
| R809 | 类体口径不同 | **`named` 比 `hit`** |

**前三次是用错了一个工具的输出；这一次是用错了一个工具的一个字段，而错完还写了诊断。**

### 验证

```
产品代码未改 · 整套 1766 / 0 · 度量未变 · TYPE_PRESENCE_TRIAGE.md 本来就对
```

### 教训

**两个数字不一样，先问它们各自叫什么。**
**「两边在量不同的东西」是个结论，不是个起点 —— 而它听起来像起点。**
"""

BACKLOG_ADD = """

## 全局 — R809 的诊断撤回（R810）

**triage 没有自相矛盾。它有两个量，我用错了那个。**

```python
named = 裸名字出现   = 18  -> STRUCTURAL 判定
hit   = 声明模式命中 =  1  -> RENAMED / PARTIAL 判定
```

**报告里的 `18/19` 是 `named`；我量的是 `hit`。**

**`STRUCTURAL` 的定义就是「名字出现过、但没作为声明出现」**（R682/R683 注释）。
**`SettingsView` 的 18/19 精确地是它声称的意思。**

**`LogOut` 的例子说明这是外壳的合理结构**：十九个视图名在外壳里出现，成员各自住在自己的视图上。

| 17 条分类 | 状态 |
|---|---|
| OUT_OF_SCOPE 2 · RENAMED 7 · STRUCTURAL 1 · UNKNOWN 7 | **不变，且现在更可信** |

**纪律**：**两个数字不一样，先问它们各自叫什么。**
**「两边在量不同的东西」是结论，不是起点 —— 而它听起来像起点。**

**本会话第四次同类错误（R806 / R807 / R809），这次错在诊断本身。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R810", BLOCKER)
    ensure(RSTATUS, "R810", BLOCKER)
    ensure(RVERDICT, "第 810 轮", VERDICT)
    ensure(BACKLOG, "R810", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R810"), (RSTATUS, "R810"), (RVERDICT, "第 810 轮"), (BACKLOG, "R810")):
        body = io.open(path, encoding="utf-8").read()
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R810: retracting R809 -- the triage was consistent and I compared two different fields\n\n"
         "R809 concluded that the type-presence triage contradicted itself over SettingsView because its 18/19 and my\n"
         "1/18 could not both be right, and guessed the bodies() collector was reading a different span.\n\n"
         "Doing what that conclusion recommended -- reading the collector rather than rewriting the pattern -- settles\n"
         "it. bodies() finds declarations with DECL and then brace-matches the whole class body including nested types;\n"
         "importing it and applying the triage's own pattern to SettingsShell still gives one present and eighteen\n"
         "absent. If the body had differed, the triage's own collector would have produced eighteen.\n\n"
         "The real split is two fields, not two bodies. The triage computes named, a bare-name co-occurrence count, and\n"
         "hit, a declaration-pattern count. named is eighteen and drives the STRUCTURAL verdict; hit is one and drives\n"
         "RENAMED and PARTIAL. The report prints named. I measured hit, compared the two, and diagnosed a conflict\n"
         "between a tool and itself.\n\n"
         "The code says so in as many words: if the member names appear anywhere in the source but not as declarations,\n"
         "the verdict is STRUCTURAL, and nothing about the measurement changes. SettingsView's 18/19 means exactly what\n"
         "it claims. Its own comment gives the illustrative case, that LogOut appears in SettingsShell.cs while the\n"
         "member lives on UserView -- which is what a shell is supposed to look like, listing nineteen view and command\n"
         "names while the members live in the views they belong to.\n\n"
         "This is the fourth time in this session that a scratch reading lost to the project's tooling, and the worst of\n"
         "the four, because the first three misread an output while this one misread a field and then wrote a diagnosis\n"
         "on top of it. The common failure is not carelessness: two numbers disagreed and I inferred on the spot that\n"
         "they measured different things, without first asking what each number is called and which line produces it.\n\n"
         "Unknown: which of the nineteen names appears in neither place, since named counts eighteen and I did not list\n"
         "the odd one out; and whether LogOut genuinely lives on UserView, which I have only from the tool's comment\n"
         "and did not verify independently.\n\n"
         "No product code changed; suite 1766 pass / 0 fail; four metrics unchanged; TYPE_PRESENCE_TRIAGE.md was right\n"
         "as written."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
