"""Record R967: the attribute changed nothing, and R966's conclusion falls to a wrong encoding."""

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
### `[DynamicallyAccessedMembers]` 没效果 —— 而我查错了编码（R967）

**R966 说「179 个步骤名 0 个在产物 → `Invokers` 是空的」。这一轮做了两件事，两件都不按预期。**

### ① 加属性，无效果

**给 `StoreFlow` 加了 `[DynamicallyAccessedMembers(PublicMethods)]`（反射点名它、让裁剪工具留着）。**

```
pdata-replica: 173,952 -> 173,952     （不变）
size:          54,724 KB -> 54,728 KB
GetCsrfAsync 在产物里:  utf16=False   （还是 False）
```

> **所以那个属性对这个产物没有可见影响 —— 或者更可能，**我用的检查看不见它**。**

### ② 而检查本身是坏的 —— 反射元数据是 **UTF-8**，字符串字面量是 **UTF-16**

**补了阳性对照 —— 一个**必然**在产物里的名字：**

```
Main                        utf16=True   utf8=True
Initialize                  utf16=True   utf8=True
StoreFlow                   utf16=False  utf8=True    ← 决定性
StepActionRunner            utf16=False  utf8=True
GetCsrfAsync                utf16=False  utf8=True
'bstn: cart endpoint unknown' utf16=True  utf8=False   ← 字面量是 UTF-16
NoSuchTypeAtAll             utf16=False  utf8=False   （对照正确）
```

**而用 UTF-8 重查那 179 个名字：**

```
UTF-16LE   名字在场: 0 / 179
UTF-8      名字在场: 179 / 179
```

### 所以 R966 的结论**倒掉**

> **`Invokers` **不是**空的。179 个方法名全部在场，反射表在产物里能建起来。
> 而「派发在 AOT 下失效」这个主因候选 —— **是假的**。**

**而它假的原因：我搜了 UTF-16，而反射元数据存 UTF-8。**
**而我上一轮**有阴性对照**（`NoSuchStepNameAtAll` 不在）—— 那一项验证的是「搜索能工作」，
**不是「被搜索的东西存在」**。而这两件事在编码不同的情况下会分开。**

> **这是同一形状错的第二十三次，而这次的具体形态是：
> **阴性对照通过了，所以我以为检查是好的。而阴性对照只能证明「搜不到不存在的东西」，
> 不能证明「搜得到存在的东西」。****

### 数字

| 度量 | R966 | **R967** |
|---|---|---|
| 套件 | 2186 | **2186（属性不改行为）** |
| 函数数 | 173,952 | **173,952（属性无影响）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物大小 | 54,724 KB | **54,728 KB** |
| **步骤名（UTF-8）** | 未查 | **179 / 179** |
| **步骤名（UTF-16）** | 0 / 179（错） | 0 / 179（编码不对） |

### 教训

> **阴性对照通过，是这一轮最危险的地方。
> 它让我对一个**看不见阳性结果**的检查产生了信任。**
> **而检查的正确做法是两向都要有对照：一个已知在、一个已知不在。
> 我上一轮只做了后者，于是「全都不在」被读成了结论，而不是被读成警报。**
"""

if "`[DynamicallyAccessedMembers]` 没效果" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 967 轮：`[DynamicallyAccessedMembers]` 没效果 —— 而我查错了编码

### ① 加属性，无效果

**给 `StoreFlow` 加 `[DynamicallyAccessedMembers(PublicMethods)]`：函数数 173,952 不变，产物 +4 KB，`GetCsrfAsync` 仍报 utf16=False。**

### ② 而检查本身是坏的 —— 反射元数据是 UTF-8

**补阳性对照（一个**必然**在产物里的名字）：**

```
Main                  utf16=True   utf8=True
Initialize            utf16=True   utf8=True
StoreFlow             utf16=False  utf8=True    ← 决定性
StepActionRunner      utf16=False  utf8=True
GetCsrfAsync          utf16=False  utf8=True
'bstn: cart endpoint unknown'  utf16=True  utf8=False   ← 字面量是 UTF-16
NoSuchTypeAtAll       utf16=False  utf8=False   （对照正确）
```

**用 UTF-8 重查 179 个名字：**

```
UTF-16LE  0 / 179
UTF-8     179 / 179
```

### 所以 R966 的结论倒掉

> **`Invokers` **不是**空的。179 个方法名全部在场，反射表在产物里能建起来。
> 「派发在 AOT 下失效」这个主因候选 —— **是假的**。**

**假的原因：我搜 UTF-16，而反射元数据存 UTF-8。**

### 而阴性对照通过是这一轮最危险的地方

> **上一轮我做了阴性对照（`NoSuchStepNameAtAll` 不在），于是以为检查是好的。
> 而阴性对照只能证明「搜不到不存在的东西」，**不能**证明「搜得到存在的东西」。
> 两者在编码不同时会分开 —— 于是「全都不在」被读成了结论，而不是被读成警报。**

### 数字

| 度量 | R966 | **R967** |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952（属性无影响）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物大小 | 54,724 KB | **54,728 KB** |
| **步骤名（UTF-8）** | 未查 | **179 / 179** |

### 教训

> **检查的正确做法是两向都要有对照：一个已知在、一个已知不在。
> 我上一轮只做了后者。**
"""

BACKLOG_ADD = """

## 判据 (c) — **步骤名 179/179 在场（UTF-8）；R966 倒掉；属性无效果**（R967）

### 编码

**反射元数据（类型名、方法名）= **UTF-8**；字符串字面量 = **UTF-16**。**
**阳性对照：`Main`/`Initialize` 两编码都在；`StoreFlow`/`StepActionRunner`/`GetCsrfAsync` 只 UTF-8；
`'bstn: cart endpoint unknown'` 只 UTF-16；`NoSuchTypeAtAll` 两编码都不在。**

### 结论

**UTF-8 下 179 / 179 步骤名在场 → `Invokers` **不是**空的 → R966「派发在 AOT 下失效」**倒掉**。**

### 属性

**`[DynamicallyAccessedMembers(PublicMethods)]` 加到 `StoreFlow`：函数数不变、产物 +4 KB。
**属性是否真的没效果 — Unknown**（检查曾经看不见它，现在看得见了但仍报 False，因方法名本来就在）。**

### 数字

**套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 产物 54,728 KB · 步骤名 UTF-8 179/179**

| 仍 Unknown | |
|---|---|
| 62.77% 缺口的真实位置 | R966 的候选倒了，**未找到新候选** |
| 那 34 个覆写的 body 是否真的在产物里 | body 串是 UTF-16，需重新核对 |

**纪律**：阴性对照通过只证明搜不到不存在的东西，不证明搜得到存在的东西。
"""

BLOCKER = """

---

## 391. **步骤名 179/179 在场（UTF-8）；R966 倒掉；属性无效果**

> R967。**改产品代码（加属性）+ 更正上一轮结论。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、加了什么

**`StoreFlow` 上 `[DynamicallyAccessedMembers(PublicMethods)]` —— 反射点名它，让裁剪工具留着。**

**结果：`pdata-replica` 173,952 **不变**；产物 54,724 → 54,728 KB；`GetCsrfAsync` 仍报 utf16=False。**

### 二、而检查本身是坏的

**补阳性对照：**

| 名字 | utf16 | utf8 |
|---|---|---|
| `Main` | True | True |
| `Initialize` | True | True |
| **`StoreFlow`** | **False** | **True** |
| **`StepActionRunner`** | **False** | **True** |
| **`GetCsrfAsync`** | False | **True** |
| `'bstn: cart endpoint unknown'` | **True** | False |
| `NoSuchTypeAtAll` | False | False |

**→ 反射元数据（类型名/方法名）存 **UTF-8**；字符串字面量存 **UTF-16**。**

**用 UTF-8 重查 179 个步骤名：**

```
UTF-16LE  0 / 179
UTF-8     179 / 179
```

### 三、所以 R966 倒掉

**`Invokers` **不是**空的。179 个方法名全在，反射表在产物里能建起来。
「派发在 AOT 下失效」这个主因候选 **是假的**。**

**假因：我搜 UTF-16，而反射元数据存 UTF-8。**

### 四、而阴性对照通过是最危险的地方

**上一轮做了阴性对照（`NoSuchStepNameAtAll` 不在），于是以为检查是好的。
而阴性对照只证明「搜不到不存在的东西」，**不证明**「搜得到存在的东西」。
两者在编码不同时会分开 —— 于是「全都不在」被读成结论，而不是警报。**

### 五、数字

| 度量 | R966 | R967 |
|---|---|---|
| 套件 | 2186 | **2186** |
| 函数数 | 173,952 | **173,952** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 产物大小 | 54,724 KB | **54,728 KB** |
| **步骤名 UTF-8** | 未查 | **179 / 179** |

### 六、验证

```
python analysis/positive_control.py  -> StoreFlow utf16=False utf8=True
python analysis/step_name_utf8.py    -> UTF-16LE 0/179，UTF-8 179/179
metrics_report.py                    -> 2186 通过 / 0 失败
```

### 七、仍然 Unknown

- **62.77% 缺口的真实位置**：**Unknown** —— R966 的候选倒了，新候选未找到。
- **那 34 个覆写的 body 是否真在产物里**：**Unknown** —— body 串是 UTF-16，需重新核对。

### 八、教训

**阴性对照通过只证明搜不到不存在的东西，不证明搜得到存在的东西。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R967", BLOCKER)
    ensure(RSTATUS, "R967", BLOCKER)
    ensure(RVERDICT, "第 967 轮", VERDICT)
    ensure(BACKLOG, "R967", BACKLOG_ADD)

    note = (
        "\n## R967 补充 — **步骤名 179/179 在场（UTF-8）；R966 倒掉；属性无效果**（套件 2186）\n\n"
        "① 给 `StoreFlow` 加 `[DynamicallyAccessedMembers(PublicMethods)]`：函数数 173,952 **不变**，产物 +4 KB。\n\n"
        "② **而检查本身是坏的**：补阳性对照发现 —— 反射元数据（类型名/方法名）存 **UTF-8**，\n"
        "   字符串字面量存 **UTF-16**。`StoreFlow`/`StepActionRunner`/`GetCsrfAsync` 只 UTF-8；\n"
        "   `'bstn: cart endpoint unknown'` 只 UTF-16；`Main`/`Initialize` 两编码都在；`NoSuchTypeAtAll` 都不在。\n\n"
        "→ 用 UTF-8 重查 179 个步骤名：**179 / 179 全在**（UTF-16 下 0）。\n\n"
        "→ **R966 倒掉**：`Invokers` 不是空的，「派发在 AOT 下失效」是假的。假因是我搜了 UTF-16。\n\n"
        "→ 而**阴性对照通过是最危险的地方**：它只证明「搜不到不存在的东西」，不证明「搜得到存在的东西」。\n"
        "   两者在编码不同时会分开，于是「全都不在」被读成结论而非警报。\n\n"
        "数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 产物 54,728 KB · 步骤名 UTF-8 179/179。\n\n"
        "纪律：检查要两向对照 —— 一个已知在、一个已知不在。\n\n"
        "下一轮：用 UTF-16 重新核对那 34 个覆写的 body 串（这次编码是对的），然后找 62.77% 缺口的新候选。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R967" not in h:
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
             for p, k in ((RBLOCK, "R967"), (RSTATUS, "R967"), (RVERDICT, "第 967 轮"), (BACKLOG, "R967")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R967: the attribute changed nothing, and R966 fell to an encoding I searched wrong\n\n"
         "R966 concluded that Invokers is empty in the artifact because none of the 179 step names appeared. Two things this\n"
         " round, neither as expected.\n\n"
         "First, StoreFlow now carries DynamicallyAccessedMembers for PublicMethods, which is the instruction to keep this\n"
         " type's public instance methods through trimming. The count did not move, the artifact grew four kilobytes, and the\n"
         " name still did not appear under the encoding I was searching.\n\n"
         "Second, and this is the real finding, the check itself was broken. A positive control -- a name that must certainly\n"
         " survive -- showed that Main and Initialize appear as UTF-16, while StoreFlow, StepActionRunner and GetCsrfAsync\n"
         " appear only as UTF-8, and a string literal from a flow appears only as UTF-16. Reflection metadata is stored as\n"
         " UTF-8 in this image and string literals as UTF-16. Rerunning the 179 names against UTF-8 finds all 179.\n\n"
         "So R966 falls. Invokers is not empty, the names are all there, and the table can be built in the artifact. The\n"
         " candidate cause I offered for the missing thirty-seven percent -- dispatch failing under NativeAOT -- is false.\n\n"
         "The dangerous part is that last round had a negative control and it passed, which is what made me trust the check.\n"
         " A negative control only shows that the search cannot find something that is not there; it says nothing about\n"
         " whether the search can find something that is. Those two come apart exactly when the encoding differs, and so\n"
         " 'none of them are present' got read as a conclusion rather than as an alarm.\n\n"
         "Figures: suite 2186, count 173,952 unchanged by the attribute, freshness zero, artifact 54,728 kilobytes, and step\n"
         " names 179 of 179 under UTF-8.\n\n"
         "Unknown: where the thirty-seven percent actually sits, since the R966 candidate is gone and nothing has replaced\n"
         " it; and whether those thirty-four override bodies truly reach the artifact, which needs the same recheck now that\n"
         " the encodings are known.\n\n"
         "The lesson is that a check needs controls in both directions, one known present and one known absent. I had only\n"
         " the second, and it was enough to make 'all absent' look like a result.\n\n"
         "Product code gained one attribute; conclusions in two documents corrected."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()