"""Record R730: the third prefix-based classifier fails; stop building them."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 159. 第三次前缀分类器失败 —— 该停手了

> R730。新增 `analysis/witness_shape.py`（保留，作为判据不可用的记录）。

### 一、本来要做的事

R729 之后下一个候选是 `0x14125fc80`（22 个 `KeyBinds.*` 键）。**手工判断就否掉了**：
60 行伪代码、40+ 个局部变量、只有 4 个属性助手 —— **那是 22 行的大对象初始化器，还是 UI 接线。**

于是不想再一个个猜，写了个分类器：**统计每个候选的被调函数里 `sub_14302xx`（Avalonia 属性助手）的占比**，
占比高=接线、低=逻辑。

### 二、结果：129 个全部 `0.0%`

```
classified           : 129
logic  (< 40% wiring): 129
wiring (>= 40%)      :    0
```

**没有一个候选的被调函数里出现 `sub_14302xx`。** 而 `0x14125fc80` 我手工数出 4 个。

**所以要么分类器错了，要么我手工数错了。** 两种都说明这个判据不能用：
**它在 129 个样本上给出完全一致的答案 —— 一个在 129 个样本上取同一个值的字段不是判据。**

### 三、这是第三次

| 轮 | 前缀法 | 结果 |
|---|---|---|
| R721 | 按被调函数前缀分 wiring/logic | 六个样本全判成 `logic`，因为漏了 `off_14492xxxx` 家族 |
| R730 | 按 `sub_14302xx` 占比 | 129 个全 `0.0%` |
| R714/R717 | 按描述符方向字段 | 78% 同一取值 → 无区分力 |

**三次都是同一个形状**：**我拿"某个符号出现得多不多"当判据，而那个符号的分布恰好是常量或近常量。**

**所以：不再写前缀分类器。** 这条写进约定。

### 四、还有一个独立发现：候选地址里有未对齐值

分类器输出里出现 `0x14065378a`、`0x14065400f` 这样的地址 —— **末尾不是 0**，
而 `.pdata` 的 `RUNTIME_FUNCTION.BeginAddress` 应当是函数起点。**41 字节、未对齐的"函数"**可疑。

**没有查清。** 记在这里而不是藏起来：要么 `.pdata` 里有我理解错的东西，要么
`witness_candidates.txt` 的地址来源在某一环被改过。**下一个用到这个文件的人要先核对这一点。**

### 五、那正确做法是什么

**读伪代码，人工判断。** R729 就是这么做的，一次一个函数，成功。
代价是**每个候选一轮**，129 个候选 = 129 轮。

**接受这个代价**，因为替代方案（前缀法）已经失败三次。

**可以省力的地方**：用**键名**先按职能分组（R729 那一屏已经把 129 个按引用的键名排在了一起），
同一组里做一个就够代表这一类的做法 —— **但这只是减少重复劳动，不能替代读伪代码。**

### 六、仍然 Unknown

- 那批未对齐地址的成因：**Unknown**（未查，见第四节）。
- 129 个里有多少是接线、多少是逻辑：**Unknown** —— **正是这一轮想量而没有量成的**。
- `0x14125fc80` 是否确实只是对象初始化：**Inference（中高）**，依据是 40+ 局部变量 + 4 个属性助手 + 22 个键名，
  未逐行确认。
"""

VERDICT = """

---

## 第 730 轮：第三次前缀分类器失败，停手

### 经过

下一个候选 `0x14125fc80` 手工判断就否掉了：60 行、40+ 局部变量、4 个属性助手 → **22 行对象初始化器，UI 接线。**

不想再一个个猜，写了个分类器统计 `sub_14302xx` 占比。**结果 129 个全是 `0.0%`。**

**一个在 129 个样本上取同一个值的字段不是判据。**

### 这是第三次

| 轮 | 前缀法 | 结果 |
|---|---|---|
| R721 | 被调函数前缀分 wiring/logic | 六个样本全判 `logic`，漏了 `off_14492xxxx` |
| R730 | `sub_14302xx` 占比 | 129 个全 `0.0%` |
| R714/717 | 描述符方向字段 | 78% 同一取值 |

**三次同一个形状：拿"某符号出现得多不多"当判据，而它恰好是常量或近常量。**

### 顺带发现：候选地址里有未对齐值

`0x14065378a`、`0x14065400f` —— 末尾不是 0，而 `.pdata` 的函数起点应当对齐。**没有查清，记下来不藏。**

### 正确做法

**读伪代码，人工判断。** R729 就是这样成功的，代价是每个候选一轮。

> **接受这个代价，因为替代方案已经失败三次。**

可以省力的只是**按键名分组**减少重复，**不能替代读伪代码**。

### 一句话

> 我三次试图用一个廉价指标替代"读代码"，三次都得到一个看起来像结果的东西。

> **不是指标不够好，是"替代读代码"这个念头本身错了。**
"""


def main():
    for p, marker, text in ((P1, "R730", BLOCKER), (P3, "R730", BLOCKER), (P2, "第 730 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # standing rule in AGENTS.md §1: stop building prefix classifiers
    ag = r"D:\projects\cyber-reverse\AGENTS.md"
    body = io.open(ag, encoding="utf-8").read()
    marker = "### 不再写前缀分类器（R730 裁决）"
    if marker not in body:
        anchor = "---\n\n## 2. 证据规则"
        add = """### 不再写前缀分类器（R730 裁决）

三次用「某个符号出现得多不多」当分类判据，三次都给出在全部样本上取同一值的结果：

| 轮 | 判据 | 结果 |
|---|---|---|
| R714/R717 | 描述符方向字段 | 78% 同一取值，无区分力 |
| R721 | 被调函数前缀分 wiring/logic | 六个样本全判 `logic`（漏了 `off_14492xxxx` 家族） |
| R730 | `sub_14302xx` 占比 | 129 个候选全 `0.0%` |

**要判断一个函数是接线还是逻辑，读它的伪代码。** 可以按 locale 键名分组减少重复劳动，
但不能用符号计数替代读代码。

---

## 2. 证据规则"""
        if anchor in body:
            io.open(ag, "w", encoding="utf-8").write(body.replace(anchor, add, 1))
            print("  AGENTS.md += 不再写前缀分类器")
        else:
            print("  AGENTS.md: anchor MISS")
    else:
        print("  AGENTS.md already has the rule")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R730: the third prefix-based classifier fails -- stop building them\n\n"
         "Next candidate 0x14125fc80 was rejected by hand: sixty lines, forty-plus locals, four property\n"
         "helpers, twenty-two KeyBinds keys -- a 22-entry object initialiser, still UI wiring.\n\n"
         "Rather than keep guessing one at a time I wrote a classifier counting sub_14302xx (Avalonia\n"
         "property helper) share among each candidate's callees. All 129 candidates came back at 0.0%.\n"
         "A field that takes the same value across 129 samples is not a discriminator.\n\n"
         "That is the third time: R714/R717 on the descriptor direction field (78% identical), R721 on\n"
         "callee prefixes (all six judged 'logic', missing the off_14492xxxx family), R730 on property-helper\n"
         "share. Same shape each time -- using 'how often does this symbol appear' as a criterion for\n"
         "something whose distribution is constant or near-constant.\n\n"
         "Added to AGENTS.md as a standing rule: to tell wiring from logic, read the pseudocode. Grouping by\n"
         "locale key name is a fair way to avoid repeat work; symbol counting is not a substitute.\n\n"
         "Also noted, unresolved: some candidate addresses are unaligned (0x14065378a), which a .pdata\n"
         "function start should not be. Not investigated; whoever uses witness_candidates.txt next should\n"
         "check it first."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
