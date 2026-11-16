"""Record R777: the off_ reader works, and it was the layout I had wrong."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 203. `off_` 读取器做出来了；**错的是我对布局的模型，不是工具**

> R777。新增 `analysis/off_slot_reader.py`、`analysis/peek_off_slot.py`。未改产品代码。

### 一、先看字节，不再猜结构

R776 试了三条路都读回乱码。这一轮**先把那个槽的真实字节打出来**：

```
slot 0x1471151d0 (file 0x7113dd0):
  40 6a db 44 01 00 00 00 | 0a 00 00 00 | 70 00 6f 00 71 00 2d 00 61 00 70 00 …
  └─ 方法表指针 ──────────┘ └─ 长度=10 ─┘ └─ 'p','o','q','-','a','p','…' ─────┘
```

**NativeAOT 字符串对象布局（Observation）：**

```
+0   method table pointer   (8 字节)
+8   length                 (DWORD)
+12  UTF-16 characters
```

**所以 `off_x` 就是字符串对象本身，字符在 `+12`，长度在 `+8`。不需要任何解引用。**

### 二、我错在哪（连续三轮）

| 轮 | 我的模型 | 实际 |
|---|---|---|
| R715/R731 | 把槽内容当长度 | 那是方法表 |
| R776 | 把槽当对象头，读 +12 | **方向对，但我把"槽内容"当成了对象指针** |
| R777 | 打出字节才看见 | 槽就是对象 |

**我一直在建模，而不是看。** 三次都栽在同一处：**先假设布局，再去验它。**
`AGENTS.md` §2.7 说的是"有几种写法"，这一层其实是"**先看字节，再谈结构**"。

### 三、校准与结果

用已知的 `off_1471151D0`（应为 `poq-app-id`）校准，**规则 `object+12` 一次命中，且长度 10 == 字符数 10**。
然后跑那 12 个槽位（每个都带长度校验）：

```
0x147115240  poq-country-identifier   len=22
0x1471151d0  poq-app-id               len=10
0x146f6c400  accept                   len=6
0x147115200  poq-app-identifier       len=18
0x146f7cb78  authorization            len=13
0x147115288  poq-currency-identifier  len=23
0x14717e5b8  version-code             len=12
0x146f6c498  accept-language          len=15
0x147113f48  platform                 len=8
0x147115310  poq-user-id              len=11
0x146f6c460  accept-encoding          len=15
0x1471795d0  user-agent               len=10
```

**R776 说的"六项 Unknown"现在全部解出。**

### 四、Poq App 请求头的完整集合

```
user-agent       Poq-Native-iOS-App
accept · accept-language · accept-encoding
authorization · version-code · platform
poq-app-id · poq-app-identifier
poq-country-identifier · poq-currency-identifier · poq-user-id
```

**`poq-slot-conditions` 不在这个构造器里** —— 它在另一个函数，R774 提到过。**未定位，记 Unknown。**

### 五、工具已可复用

```
python analysis/off_slot_reader.py              # 校准 + 读那 12 个
python analysis/off_slot_reader.py 0x1471151d0  # 读指定槽
```

**先校准再批量**，校准不过就停 —— **这条是它自己的守护**：
没有可复现的已知答案，剩下的读数就是猜。

### 六、验证

```
本轮未改产品代码
完整套件保持 1752 通过 / 0 失败
两个新脚本：off_slot_reader.py（可复用）、peek_off_slot.py（一次性的字节诊断，保留作布局证据）
```

### 七、仍然 Unknown

- **各头部的取值**：**Unknown** —— 名字有了，值来自 `sub_141CF6230(&off_146B5C780, a1[29])`、
  `sub_140B399B0(a1)`、`a1[24]` 等，语义未读。
- `poq-slot-conditions` 在哪个构造器：**Unknown**。
- **触发 App 面的任务类型**：**Unknown**（R775）。
- 四个头部构造器为何是四个：**Unknown**。
"""

VERDICT = """

---

## 第 777 轮：工具做出来了，错的是我的模型

### 先看字节

```
slot 0x1471151d0:
  40 6a db 44 01 00 00 00 | 0a 00 00 00 | 70 00 6f 00 71 00 2d 00 …
  └─ 方法表指针 ──────────┘ └─ 长度=10 ─┘ └─ 'p','o','q','-','a','p'… ┘
```

**NativeAOT 字符串：`+0` 方法表、`+8` 长度 DWORD、`+12` UTF-16 字符。**
**`off_x` 就是字符串对象本身 —— 不需要解引用。**

### 我错在哪（连续三轮）

| 轮 | 我的模型 | 实际 |
|---|---|---|
| R715/R731 | 槽内容当长度 | 那是方法表 |
| R776 | 槽当对象头读 +12 | 方向对，但把槽内容当成了对象指针 |
| R777 | **打出字节才看见** | 槽就是对象 |

**我一直在建模，而不是看。三次都栽在同一处：先假设布局，再去验它。**

### 校准 + 结果

`off_1471151D0` 应为 `poq-app-id`，**规则一次命中，长度 10 == 字符数 10**。12 个槽位全部解出：

```
user-agent · accept · accept-language · accept-encoding
authorization · version-code · platform
poq-app-id · poq-app-identifier
poq-country-identifier · poq-currency-identifier · poq-user-id
```

**R776 说的"六项 Unknown"全部解出。** `poq-slot-conditions` 在另一个构造器，未定位。

### 工具

```
python analysis/off_slot_reader.py [slot…]
```
**先校准再批量；校准不过就停** —— 没有可复现的已知答案，剩下的读数就是猜。

### 验证

```
产品代码未改；套件 1752 / 0
```
"""

BACKLOG_ADD = """

## 工具债已还 — `off_` 读取器（R777 完成）

```
python analysis/off_slot_reader.py [slot…]
```

**NativeAOT 字符串布局**：`+0` 方法表 · `+8` 长度 DWORD · `+12` UTF-16 字符 —— **`off_x` 就是对象本身**。
校准用 `off_1471151D0 → 'poq-app-id'`，长度与字符数必须一致；**校准不过就停**。

**Poq App 请求头（12 个，全部解出）**：

```
user-agent Poq-Native-iOS-App · accept · accept-language · accept-encoding
authorization · version-code · platform
poq-app-id · poq-app-identifier · poq-country-identifier · poq-currency-identifier · poq-user-id
```

**余下**：

| 项 | 状态 |
|---|---|
| 各头的取值 | Unknown（`sub_141CF6230`、`sub_140B399B0`、`a1[24]` 未读） |
| `poq-slot-conditions` 所在构造器 | Unknown |
| 触发 App 面的任务类型 | Unknown |

**构建单位不变**：App 面一个 flow（身份 + 四步 + 注册项）。**身份的头名现在齐了，值还差。**
"""


def main():
    for p, marker, text in ((P1, "R777", BLOCKER), (P3, "R777", BLOCKER), (P2, "第 777 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R777 完成" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += 工具债已还")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R777: the off_ reader works -- what was wrong was my model of the layout, not the tool\n\n"
         "Three rounds of failed reads came down to never looking at the bytes. This round printed them, and the\n"
         "layout is plain: at the slot, a method-table pointer in the first eight bytes, a DWORD length at plus eight,\n"
         "and UTF-16 characters from plus twelve. So an off_ symbol names the string object itself and needs no\n"
         "dereference at all.\n\n"
         "Three rounds went wrong on the same assumption, taken in different directions. R715 and R731 read the\n"
         "slot's content as a length when it was a method table. R776 read past the slot as if it were an object\n"
         "header, which was the right direction, but obtained the object from the slot's content when the slot was the\n"
         "object. Each time I built a model first and tested it after. Printing the bytes settled it in one call.\n\n"
         "The reader calibrates before it trusts itself: it reads the slot known to hold poq-app-id and requires the\n"
         "string to match and the length field to equal the character count. Only then does it batch. Without a\n"
         "reproducible known answer the rest would be guesses, so failing calibration stops it.\n\n"
         "All twelve slots in that request builder resolve, with length checks passing on every row: user-agent,\n"
         "accept, accept-language, accept-encoding, authorization, version-code, platform, poq-app-id,\n"
         "poq-app-identifier, poq-country-identifier, poq-currency-identifier and poq-user-id. The six that R776 had\n"
         "to record as unknown are now known. poq-slot-conditions is not among them -- it lives in a different builder\n"
         "and remains unlocated.\n\n"
         "So the identity's header names are complete and its values are not: they come from sub_141CF6230,\n"
         "sub_140B399B0 and a1[24], whose semantics are unread. The unit of work is still an app-surface flow rather\n"
         "than a set of constants.\n\n"
         "No product code changed; suite remains 1752 pass / 0 fail. Two scripts added: the reader, and a small\n"
         "one-off byte peek kept as the evidence for the layout."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
