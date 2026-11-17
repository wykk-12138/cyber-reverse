"""Record R1010: the key-name probe has a domain, and most of the 159 fall outside it."""

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
### 那个判据有**适用范围**，而 159 个里大部分在界外（R1010）

**R1009 说下一轮判那 62 个不带点键。判了，而结果是「这个问法对它们不成立」。**

### ① 按 R956 的教训换成三种形态再查

**那 62 个是驼峰内部标识符（`orderProcessed` / `totalMinor`），而原版不用会话变量字典 —— 它用**字段**。
所以裸名可能是错的形状。查四种：**

```
orderProcessed      bare=0  _field=0  get_OrderProcessed=0  content=orderProcessed=0
paymentStarted      bare=0  _field=0  get_PaymentStarted=0  content=paymentStarted=0
totalMinor          bare=0  _field=0  get_TotalMinor=0      content=totalMinor=0
transactionAmount   bare=0  _field=0  get_TransactionAmount=0 content=transactionAmount=0
deviceProfiled      bare=0  _field=0  get_DeviceProfiled=0  content=deviceProfiled=0
sizeLine            bare=0  _field=0  get_SizeLine=0        content=sizeLine=0
selectedRate        bare=0  _field=0  get_SelectedRate=0    content=selectedRate=0
discountApplied     bare=0  _field=0  get_DiscountApplied=0 content=discountApplied=0
```

**→ 全 0。四种形态一个都没有。**

### ② 而全 0 不说明它们错了 —— 它说明这个问法对这一类**不适用**

**原版**没有** `Vars` 这个字典。它把状态放在**字段**里，而字段叫什么**不必与我们的键名相同** ——
我们的 `orderProcessed` 在原版里可能是字段 `_orderDone`、可能是 `_placed`、可能是别的东西，
而「这个名字在镜像里吗」对**任何一个**候选都只会答 0。**

> **→ 所以「键名对镜像」这个判据有一个**定义域**：
> 它只对**协议层**的名字有判定力 —— 那些名字是从镜像里抄来的（`kpsdk` / `datadome` /
> `paymentGatewayName` / URL / cookie 名），所以**这个名字**必须出现在镜像里。
> → 而对**内部状态管理**的名字，它没有判定力，因为原版在那一层用的是另一种机制。**
> **→ 这是 R730「不再写前缀分类器」的同一课：**一个判据在某一层不适用时，用它得出的结论是假的。**

### ③ 所以 159 个的正确读法

| 类 | 数 | 判据适用？ | 说明 |
|---|---|---|---|
| 带点（`adyen.*` 等） | 97 | **否** | 我们发明的命名空间约定，原版没有这套约定 |
| 驼峰内部状态 | ~57 | **否** | 原版用字段，字段名不必相同 |
| **协议层名字** | **5** | **是** | `paymentMethodsUrl` · `sensorKeys` · `lastStatus` · `lastBody` · `antibot.solver` |

**那 5 个里，**只有 `paymentMethodsUrl` 是该判的** —— 它是**端点**，而端点必须来自镜像。
另外 4 个（`lastStatus` / `lastBody` / `sensorKeys` / `antibot.solver`）是**我们自己的通道名**，
原版不需要它们，所以「不在镜像里」**正常**。**

**→ 而 `paymentMethodsUrl` R1008 已经处理过（记为自造、路由不可得）。**

### ④ 而 152 个 present 的含义现在清楚了

**那 152 个是**协议层的名字** —— 从镜像里抄来的（token 键、cookie 名、请求字段）。
→ 所以「152 在 / 159 不在」不是「一半对一半错」，
→ 而是**「抄来的都在，自己起的不在」** —— 而那正是应有的样子。**

### ⑤ 这一轮没有改代码，因为结论是「不需要修」

**R1009 把 159 摆成一个待办清单的形状。而这一轮说：那 159 个里**约 154 个不需要任何人做什么** ——
它们是我们自己的状态管理，而它本来就该有我们自己的名字。**

> **→ 唯一留下的是 `paymentMethodsUrl`（已记）与一个真问题：
> 「原版用什么字段名承载这些状态」。而那需要**类型级**证据（字段表），不是字符串级。
> → 而 vtable/字段表在 NativeAOT 下按名不可得（R958）—— 所以它是 Unknown，不是待办。**

### 数字

| 度量 | R1009 | **R1010** |
|---|---|---|
| 套件 | 2219 | **2219（未改代码）** |
| 产物陈旧度 | 1 / 2,671 | **1 / 2,671** |
| 函数数 | 174,336 | **174,336** |
| 会话键 absent | 159 | **159（但按判据分成 97 不可判 / 57 不可判 / 5 可判）** |
| **其中需要修** | 记为待判 ~50 | **1（`paymentMethodsUrl`，R1008 已记）** |
| **判据的定义域** | 未讨论 | **协议层名字（152 个），不含内部状态** |

### 教训

> **一个判据在某一层不适用时，用它得出的结论是假的 —— 而它的**输出形状**
> （「159 个不在」）看起来和「159 个都是缺陷」一模一样。**
> **→ 上一轮我把一个清单交给了下一轮，而这一轮的第一件事本该是问
> 「这个清单上的东西**该不该**满足这个判据」。**
"""

if "那个判据有**适用范围**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1010 轮：那个判据有适用范围，而 159 个里大部分在界外

### ① 按 R956 的教训换成四种形态再查

```
orderProcessed      bare=0  _field=0  get_OrderProcessed=0  content=orderProcessed=0
paymentStarted      bare=0  _field=0  get_PaymentStarted=0  content=paymentStarted=0
totalMinor          bare=0  _field=0  get_TotalMinor=0      content=totalMinor=0
transactionAmount   bare=0  _field=0  get_TransactionAmount=0 content=transactionAmount=0
（另四个同样全 0）
```

**→ 全 0，四种形态一个都没有。而全 0 **不说明它们错了**。**

### ② 而它说明这个问法对这一类**不适用**

**原版**没有** `Vars` 这个字典 —— 它把状态放在**字段**里，而字段叫什么**不必与我们的键名相同**。
「这个名字在镜像里吗」对**任何一个**候选都只会答 0。**

> **→ 「键名对镜像」这个判据有**定义域**：只对**协议层**的名字有判定力
> （`kpsdk` / `datadome` / `paymentGatewayName` / URL / cookie 名 —— 那些是抄来的，所以必须在）。
> → 对**内部状态管理**的名字没有判定力，因为原版在那一层用另一种机制。
> → 这是 R730「不再写前缀分类器」的同一课：**判据在某一层不适用时，用它得出的结论是假的。**

### ③ 所以 159 个的正确读法

| 类 | 数 | 判据适用？ |
|---|---|---|
| 带点（`adyen.*`） | 97 | **否** — 我们发明的命名空间约定 |
| 驼峰内部状态 | ~57 | **否** — 原版用字段，名字不必相同 |
| **协议层名字** | **5** | **是** |

**那 5 个里只有 `paymentMethodsUrl` 该判（它是**端点**，必须来自镜像）；另外 4 个
（`lastStatus` / `lastBody` / `sensorKeys` / `antibot.solver`）是我们自己的通道名，缺失**正常**。**
**而 `paymentMethodsUrl` R1008 已处理。**

### ④ 152 个 present 的含义现在清楚了

**那 152 个是**协议层的名字**（token 键、cookie 名、请求字段）。
→ 所以「152 在 / 159 不在」不是「一半对一半错」，而是**「抄来的都在，自己起的不在」—— 那正是应有的样子。**

### ⑤ 这一轮没有改代码，因为结论是「不需要修」

**R1009 把 159 摆成一个待办清单的形状。而这一轮说：那 159 个里**约 154 个不需要任何人做什么**。
唯一留下的是 `paymentMethodsUrl`（已记）与一个真问题：「原版用什么字段名承载这些状态」——
而那需要**类型级**证据，在 NativeAOT 下按名不可得（R958）⇒ **Unknown，不是待办**。**

### 数字

| 度量 | R1009 | **R1010** |
|---|---|---|
| 套件 | 2219 | **2219（未改代码）** |
| 产物陈旧度 | 1 / 2,671 | **1 / 2,671** |
| 函数数 | 174,336 | **174,336** |
| 会话键 absent | 159 | **159（97 不可判 / 57 不可判 / 5 可判）** |
| **其中需要修** | 记为待判 ~50 | **1（已记）** |
| **判据的定义域** | 未讨论 | **协议层名字** |

### 教训

> **一个判据在某一层不适用时，用它得出的结论是假的 —— 而它的**输出形状**（「159 个不在」）
> 看起来和「159 个都是缺陷」一模一样。
> → 上一轮我把一个清单交给了下一轮，而这一轮的第一件事本该是问
> 「这个清单上的东西**该不该**满足这个判据」。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — **键名判据有定义域：159 个 absent 里约 154 个不可判且不需修**（R1010）

### 四种形态全 0

```
orderProcessed / paymentStarted / totalMinor / transactionAmount / deviceProfiled / sizeLine
selectedRate / discountApplied      全部 bare=0  _field=0  get_Pascal=0  content==0
```

**→ 全 0 不说明它们错 —— 说明这个问法对这一类**不适用**。**

### 定义域

**原版没有 `Vars` 字典，它用**字段**，字段名不必与我们的键名相同。
→ 判据只对**协议层**名字有判定力（`kpsdk` / `datadome` / `paymentGatewayName` / URL / cookie 名）。
→ 对**内部状态管理**的名字没有判定力。**
**→ 与 R730「不再写前缀分类器」同一课。**

### 159 的读法

| 类 | 数 | 判据适用 |
|---|---|---|
| 带点 `adyen.*` | 97 | **否** |
| 驼峰内部状态 | ~57 | **否** |
| **协议层名字** | **5** | **是** |

**5 个里只有 `paymentMethodsUrl` 该判（端点必须来自镜像，R1008 已记）；另 4 个是我们自己的通道名，缺失正常。**

### 152 present 的含义

**那 152 个是协议层名字（token 键 / cookie 名 / 请求字段）→「抄来的都在，自己起的不在」—— 应有的样子。**

### 数字

**套件 2219 · 陈旧度 1 / 2,671 · 函数数 174,336 · absent 159（154 不可判 / 5 可判 / 1 需修且已记）**

| 仍 Unknown | |
|---|---|
| 原版用什么字段名承载这些状态 | 需类型级证据；NativeAOT 下按名不可得（R958） |

**纪律**：判据在某一层不适用时，它的输出形状和「全都是缺陷」一模一样。
"""

BLOCKER = """

---

## 434. **键名判据有定义域：159 个 absent 里约 154 个不可判且不需修**

> R1010。**未改代码，只判定判据的适用范围。** 套件 **2219 通过 / 0 失败 / 0 跳过**。

### 一、按 R956 的教训换成四种形态再查

```
orderProcessed      bare=0  _field=0  get_OrderProcessed=0  content=orderProcessed=0
paymentStarted      bare=0  _field=0  get_PaymentStarted=0  content=paymentStarted=0
totalMinor          bare=0  _field=0  get_TotalMinor=0      content=totalMinor=0
transactionAmount   bare=0  _field=0  get_TransactionAmount=0 content=transactionAmount=0
deviceProfiled      bare=0  _field=0  get_DeviceProfiled=0  content=deviceProfiled=0
sizeLine            bare=0  _field=0  get_SizeLine=0        content=sizeLine=0
selectedRate        bare=0  _field=0  get_SelectedRate=0    content=selectedRate=0
discountApplied     bare=0  _field=0  get_DiscountApplied=0 content=discountApplied=0
```

**→ 全 0。四种形态一个都没有。
→ 而全 0 **不说明它们错了** —— 它说明这个问法对这一类**不适用**。**

### 二、为什么它不适用

**原版**没有** `Vars` 这个字典。它把状态放在**字段**里，而字段叫什么**不必与我们的键名相同** ——
我们的 `orderProcessed` 在原版里可能是 `_orderDone`、可能是 `_placed`、可能是别的东西，
而「这个名字在镜像里吗」对**任何一个**候选都只会答 0。**

**→ 所以「键名对镜像」这个判据有一个**定义域**：
→ 它只对**协议层**的名字有判定力 —— 那些名字是从镜像里抄来的
  （`kpsdk` / `datadome` / `paymentGatewayName` / URL / cookie 名），所以**这个名字**必须出现在镜像里。
→ 而对**内部状态管理**的名字，它没有判定力，因为原版在那一层用的是另一种机制。**

**→ 这是 R730「不再写前缀分类器」的同一课：
**一个判据在某一层不适用时，用它得出的结论是假的。****

### 三、所以 159 个的正确读法

| 类 | 数 | 判据适用？ | 说明 |
|---|---|---|---|
| 带点（`adyen.*` 等） | 97 | **否** | 我们发明的命名空间约定，原版没有这套约定 |
| 驼峰内部状态 | ~57 | **否** | 原版用字段，字段名不必相同 |
| **协议层名字** | **5** | **是** | `paymentMethodsUrl` · `sensorKeys` · `lastStatus` · `lastBody` · `antibot.solver` |

**那 5 个里，**只有 `paymentMethodsUrl` 是该判的** —— 它是**端点**，而端点必须来自镜像。
另外 4 个是**我们自己的通道名**，原版不需要它们，所以「不在镜像里」**正常**。
→ 而 `paymentMethodsUrl` R1008 已经处理过（记为自造、路由不可得）。**

### 四、152 个 present 的含义现在清楚了

**那 152 个是**协议层的名字** —— 从镜像里抄来的（token 键、cookie 名、请求字段）。
→ 所以「152 在 / 159 不在」不是「一半对一半错」，
→ 而是**「抄来的都在，自己起的不在」** —— 而那正是应有的样子。**

### 五、这一轮没有改代码，因为结论是「不需要修」

**R1009 把 159 摆成一个待办清单的形状。而这一轮说：那 159 个里**约 154 个不需要任何人做什么** ——
它们是我们自己的状态管理，而它本来就该有我们自己的名字。**

**→ 唯一留下的是 `paymentMethodsUrl`（已记）与一个真问题：
  「原版用什么字段名承载这些状态」。而那需要**类型级**证据（字段表），不是字符串级。
→ 而 vtable/字段表在 NativeAOT 下按名不可得（R958）—— 所以它是 Unknown，不是待办。**

### 六、数字

| 度量 | R1009 | R1010 |
|---|---|---|
| 套件 | 2219 | **2219（未改代码）** |
| 产物陈旧度 | 1 / 2,671 | **1 / 2,671** |
| 函数数 | 174,336 | **174,336** |
| 会话键 absent | 159 | **159（97 不可判 / 57 不可判 / 5 可判）** |
| **其中需要修** | 记为待判 ~50 | **1（`paymentMethodsUrl`，R1008 已记）** |
| **判据的定义域** | 未讨论 | **协议层名字（152 个），不含内部状态** |

### 七、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str orderProcessed        -> {"n":0}
python analysis/ida.py str _orderProcessed       -> {"n":0}
python analysis/ida.py str get_OrderProcessed    -> {"n":0}
（paymentStarted / totalMinor / transactionAmount / deviceProfiled / sizeLine / selectedRate /
  discountApplied 同形，全部 0）
cd replica && python tools/metrics_report.py -> 套件 2219 · 陈旧度 1 / 2,671 · 函数数 174,336
```

### 八、仍然 Unknown

- **原版用什么字段名承载这些状态**：**Unknown** —— 需类型级证据；NativeAOT 下按名不可得（R958）。

### 九、教训

**一个判据在某一层不适用时，用它得出的结论是假的 —— 而它的**输出形状**
（「159 个不在」）看起来和「159 个都是缺陷」一模一样。**

**→ 上一轮我把一个清单交给了下一轮，而这一轮的第一件事本该是问
「这个清单上的东西**该不该**满足这个判据」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1010", BLOCKER)
    ensure(RSTATUS, "R1010", BLOCKER)
    ensure(RVERDICT, "第 1010 轮", VERDICT)
    ensure(BACKLOG, "R1010", BACKLOG_ADD)

    note = (
        "\n## R1010 补充 — **键名判据有定义域：159 个 absent 里约 154 个不可判且不需修**（套件 2219，未改代码）\n\n"
        "按 R956 的教训换成四种形态再查（bare / `_field` / `get_Pascal` / `content=`）：\n"
        "`orderProcessed` · `paymentStarted` · `totalMinor` · `transactionAmount` · `deviceProfiled` ·\n"
        "`sizeLine` · `selectedRate` · `discountApplied` —— **全 0，四种形态一个都没有。**\n\n"
        "**而全 0 不说明它们错 —— 说明这个问法对这一类**不适用**：**\n"
        "原版没有 `Vars` 字典，它用**字段**，字段名不必与我们的键名相同。\n"
        "→ **判据的定义域：只对**协议层**名字有判定力（`kpsdk`/`datadome`/`paymentGatewayName`/URL/cookie 名），\n"
        "对**内部状态管理**没有。**\n"
        "→ 与 **R730「不再写前缀分类器」同一课**：判据在某一层不适用时，用它得出的结论是假的。\n\n"
        "**159 的正确读法**：97 带点（不可判，我们发明的命名空间）· ~57 驼峰内部（不可判）· **5 协议层（可判）**。\n"
        "5 个里**只有 `paymentMethodsUrl` 该判**（端点在必须来自镜像，R1008 已记）；另 4 个是我们自己的通道名，缺失正常。\n\n"
        "**152 present 的含义清楚了**：那 152 个是协议层名字 → **「抄来的都在，自己起的不在」—— 应有的样子。**\n\n"
        "数字：套件 2219 · 陈旧度 1 / 2,671 · 函数数 174,336 · absent 159（154 不可判 / 5 可判 / 1 需修且已记）。\n\n"
        "纪律：**判据在某一层不适用时，它的输出形状和「全都是缺陷」一模一样。**\n\n"
        "下一轮：回核心 —— 优先级 ① 的 flow 端点（那条路已有覆写与 ordinal 证据）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1010" not in h:
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
             for p, k in ((RBLOCK, "R1010"), (RSTATUS, "R1010"), (RVERDICT, "第 1010 轮"), (BACKLOG, "R1010")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1010: the key-name probe has a domain, and most of the 159 fall outside it\n\n"
         "R1009 left a list of 159 session keys absent from the image and framed the next step as judging around fifty of\n"
         " them. Judging them first meant asking whether they should be judged at all.\n\n"
         "Taking R956's lesson, I checked four shapes rather than the bare name: the name itself, an underscore field, a\n"
         " get_ accessor, and a content= form. Eight of the unprefixed keys return zero in all four. That looks like more\n"
         " evidence of invention and is not evidence at all.\n\n"
         "The original has no session-variable dictionary. It holds state in fields, and a field need not be named what\n"
         " our key is named -- orderProcessed could be _orderDone or _placed -- so the question \"is this name in the\n"
         " image\" answers zero for every candidate regardless of whether the state exists there in some other form.\n\n"
         "So the probe has a domain. It settles protocol-level names, which are copied from the artifact and therefore\n"
         " must appear in it: kpsdk, datadome, paymentGatewayName, request fields, cookie names. It does not settle names\n"
         " for internal state management, because at that layer the original uses a different mechanism entirely. This is\n"
         " the same lesson as R730's ruling against prefix classifiers -- a criterion applied outside its layer produces\n"
         " conclusions that are simply false.\n\n"
         "That reshapes the 159. Ninety-seven carry a module prefix and are this workspace's own naming convention. About\n"
         " fifty-seven are camel-case internal state. Five are protocol-level, and of those only paymentMethodsUrl needs\n"
         " judging, because an endpoint must come from the image; the other four are our own channel names and are\n"
         " correctly absent. paymentMethodsUrl was already recorded in R1008.\n\n"
         "The 152 that are present now read differently too. They are the protocol names, so the split is not half right\n"
         " and half wrong -- it is copied names present and invented names absent, which is exactly the shape it should\n"
         " have.\n\n"
         "No code changed, because the finding is that roughly 154 of the 159 need nothing done. What remains is one real\n"
         " question -- which field names the original uses for this state -- and that needs type-level evidence, which\n"
         " NativeAOT does not give up by name (R958), so it is unknown rather than pending.\n\n"
         "Figures: suite 2219 unchanged, freshness one file and 2,671 lines, count 174,336, absent keys 159 of which 154\n"
         " are outside the probe's domain, 5 inside it, 1 needing work and already recorded.\n\n"
         "Unknown: the original's field names for this state.\n\n"
         "The lesson is that when a criterion does not apply at a layer, its output still looks identical to \"everything\n"
         " here is broken\", and the first thing to do with a list handed over by the previous round is ask whether its\n"
         " items should satisfy that criterion at all.\n\n"
         "No product code changed; one criterion given its domain; suite green at 2219."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()