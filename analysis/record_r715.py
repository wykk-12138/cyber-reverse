"""Record R715: accessor names exist but are not type-qualified; the guard is the deliverable."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 144. 访问器名字是**新证据源**，但它不带类型 —— 42 条里只有 3 条可归因，仍缺类型

> R715。新增 `analysis/accessor_names.py`（含归因守卫）。

### 一、这一轮找到的新证据

反编译找 `EditValue\\`1` 的类型时，字符串池里露出一组**新的、独立于描述符**的证据 —— **CLR 访问器名本身**：

```
0x1432ffff9  'get_HasMultiple'
0x143300009  'set_HasMultiple'
0x143300069  '<HasMultiple>k__BackingField'
0x143300087  'HasMultiple'
```

**`set_X` 的存在说明类型声明了 setter** —— 而 `ICommand` 属性通常只有 getter。
**这比 R714 那个方向字段强**（那个 78% 都是 G/S，等于背景）。

全池规模：`get_` **4892** / `set_` **2145** / `k__BackingField` **1049**。

### 二、然后它失败在同一个地方

第一版跑出来：`get+set+field` 15 条、`get+set` 3 条 —— 看起来很有用。
**但这些名字不带类型。** 而绑定表里同名成员遍布多个类型：

```
Name    37 个类型      Close  29      Delete 23      Save 17      Running 4
```

**所以 `get_Save` 可能属于 17 个类型中的任何一个。** 这正是 R708 第一版「只匹配成员名」得到 378/819 的那个错，
**同一个错，隔了七轮，换了一个数据源。**

### 三、修法：把归因条件写进工具

> **只有名字在全表唯一的成员，访问器证据才可归因。**

加了守卫后：

```
get+set+field   2   TaskGroupView.Link, PayPalAccountCreatorView.Model
get only        1   CheckoutView.Checkout
none           13   12 个 EditValue 数字名 + ExpressionView.Expressions
unattributable 26   Name / Save / View / Delete 这些共享名字
```

**42 条里只剩 3 条可归因。**

### 四、而这 3 条仍然没有类型

| 成员 | 访问器证据 | 还缺什么 |
|---|---|---|
| `TaskGroupView.Link` | get+set+field → 有 setter 的自动属性 | **类型 Unknown** |
| `PayPalAccountCreatorView.Model` | 同上 | **类型 Unknown** |
| `CheckoutView.Checkout` | get only | 可能是 `ICommand`，也可能是只读数据 —— **Unknown** |

**知道"有 setter"不等于知道"setter 收什么"。** 写一个 `object Link { get; set; }` 能过编译、能让名字出现，
**但那是发明，不是复刻。**

**所以本轮仍然零实现。** 这是结论，不是没时间。

### 五、反编译这条路的结论

七个探针：

```
xrefs 0x143300069  0      (backing field 名)
xrefs 0x143300087  0      (属性名字面量)
xrefs 0x1432ffff9  0      (get_ 名)
xrefs 0x143300009  0      (set_ 名)
xrefs 0x143300068  0      (长度前缀字节)
xrefs 0x143300086  0
xrefs 0x143220dbd  0      (描述符 blob)
```

**全 0。** 这些是元数据里的名字表，代码通过**数据表查名字**访问，没有地址引用。
**所以"顺着名字找代码、再从代码读类型"这条路线，对这个二进制不成立** —— 与 R703 修好的字符串引用问题是**不同**的：
那个是 `lea` 的 disp32 没被 xref 收录；**这里是根本没有代码引用这个名字**。

**AOT 元数据的字段类型，用现有能力取不到。** 这是 Unknown 的**具体缺什么**：
需要一个 AOT `EEType`/`FieldDesc` 解析器，或者运行期探针（需登录凭据，属 YG 那一类）。

### 六、这一轮的判断

> 我找到了一种更好的证据，然后在用它之前先问了"它能不能归因" —— 答案是不能，除了 3 条。

**这一轮的价值不是新增 15 个实现，是拦住 15 个伪造。**

### 七、仍然 Unknown

- `EditValue\\`1` 那 12 个名字的类型与语义：**Unknown**，且用现有能力**不可得**（写清缺什么）。
- 26 条共享名字成员的访问器形态：**Unknown**（不可归因）。
- 3 条可归因成员的类型：**Unknown**。
"""

VERDICT = """

---

## 第 715 轮：新证据源，但它不带类型

### 找到的

字符串池里有 **CLR 访问器名本身**：

```
get_HasMultiple  /  set_HasMultiple  /  <HasMultiple>k__BackingField
```

`set_X` 说明类型声明了 setter，而 `ICommand` 通常只有 getter —— **比 R714 那个方向字段强**。
全池：`get_` 4892 / `set_` 2145 / `k__BackingField` 1049。

### 失败在同一个地方

名字**不带类型**，而绑定表里同名成员遍布多个类型：

```
Name 37 个类型 · Close 29 · Delete 23 · Save 17
```

`get_Save` 可能属于 17 个中的任何一个。**这正是 R708 第一版得到 378/819 的那个错，隔了七轮换了个数据源。**

### 修法：把归因条件写进工具

> 只有名字**全表唯一**的成员，访问器证据才可归因。

```
get+set+field 2 · get only 1 · none 13 · unattributable 26
```

**42 条只剩 3 条可归因，而这 3 条仍然缺类型。**
**知道「有 setter」不等于知道「setter 收什么」。**

### 反编译这条路也关了

七个探针（backing field 名、名字字面量、get_/set_、长度前缀、描述符 blob）**xref 全 0**。
这些是元数据名字表，代码按数据表查名 —— **没有地址引用**。
与 R703 修的 disp32 问题是**不同**的：那个是 xref 没收录，**这里是根本没有代码引用**。

### 本轮零实现

> **价值不是新增 15 个实现，是拦住 15 个伪造。**

### 下一轮

12 个 `EditValue` 名字的类型用现有能力**不可得**，明确写进 Unknown 的「缺什么」。
转去做能做的：42 条里唯一有双证据的 `AccountGroupView.Save`（描述符 + 源码 lambda），
但先要解释它为什么带 Setter 而 `Close` 不带。
"""


def main():
    for p, marker, text in ((P1, "R715", BLOCKER), (P3, "R715", BLOCKER), (P2, "第 715 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R715: accessor names are a new evidence source, but not type-qualified\n\n"
         "The string pool carries get_/set_/k__BackingField names (4892/2145/1049). A set_X string means\n"
         "a setter exists, which ICommand properties normally lack -- stronger than R714's direction field.\n\n"
         "The first run classified 15 members as 'get+set+field' and 3 as 'get+set'. It cannot: these names\n"
         "carry no type, and Name appears on 37 binding types, Close on 29, Save on 17. That is the same\n"
         "error as c10_split's first version (378/819), seven rounds later with a different source.\n\n"
         "Guard added: a member is only attributable when its name is unique across the binding table. That\n"
         "leaves 3 of 42, and all three still lack a type -- knowing a setter exists does not say what it\n"
         "accepts. Nothing implemented; writing `object Link { get; set; }` would compile and would be\n"
         "invention, not replication.\n\n"
         "Decompilation is closed too: seven probes on the backing-field name, the literal, get_/set_, the\n"
         "length prefix and the descriptor blob all return zero xrefs. These are metadata name tables that\n"
         "code reaches by data lookup, not by address -- different from R703's disp32 problem, where the\n"
         "reference existed and the xref database simply did not record it."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
