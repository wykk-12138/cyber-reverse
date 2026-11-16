"""Record R781: the Casio logic is a JSON path plus one availability flag."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 207. Casio 的判定逻辑读出来了：`data.products.items` + `casio_can_purchase`

> R781。未改产品代码。`off_` 读取器第一次在别的任务上派上用场。

### 一、先查用法，再谈实现

R780 的结论是"Casio 缺整张配置面"。这一轮**先查 `CasioRegion` 怎么被用**：

```
CasioRegion           xrefs=0     —— 配置键，按名字读，没有代码引用
casio_can_purchase    xrefs=1     → sub_140954410 (2,116 B)
casiostore.bhawar     xrefs=1     → sub_14117C4E0 (687 KB，R759 那个 IDA 并片)
casioid               xrefs=2     → sub_14094AF90 (187 B) · sub_140952790 (893 B)
```

**`CasioRegion` 零 xref 是个有用的结果**：它与 store 元数据同类 —— **数据记录里的键，代码按名字读**，
所以"找不到引用"不是"没用到"。

### 二、`sub_140954410` 读的是三个键

函数体里有三次 `sub_141FD2400(对象, &off_xxx, …)` —— 那形状是"按键取值"。三个键用新读取器一读即出：

```
off_146FEA418  ->  'data'      len=4
off_147118348  ->  'products'  len=8
off_1470ABD58  ->  'items'     len=5
```

**所以它走的是 `data → products → items` 这条 JSON 路径。**
再往里（第 170 行之后，`0x140954a20` 处）才引用 `casio_can_purchase`。

**合起来读**：

```
遍历 data.products.items[*]，用每个 item 的 casio_can_purchase 判定可购
```

**这是 Observation**：路径三段是键名，`casio_can_purchase` 的引用点在这个函数体内。

### 三、复刻件缺的正是这两样

`casio_can_purchase` 与另外四个 `casio_*` 字段在 `replica/src` 里**全部 ABSENT**（R780 查过）。
**所以复刻件的 Casio 解析没有走镜像这条路径，也没用那个判定字段。**

**这就把 R780 那句"缺整张配置面"具体成了两件可做的事**：

1. 按 `data.products.items` 解析（而不是现在的形状）
2. 用 `casio_can_purchase` 判定可购（而不是自己推）

### 四、读取器的第一次外部收益

R777 建 `off_slot_reader.py` 时记的是"工具债"，这一轮**三个键一次读全**。
**上一轮 R776 为同样的事烧掉了五次工具尝试。**

另外：`0x144C1E320` 读回 `'\\x01'` 且 `len=1155229432` —— **那不是字符串对象，是类型表。**
**读取器的长度校验（长度必须等于字符数）把它标了出来。**

**这条守护是有用的：没有它，那个 1,155,229,432 会被当成"读到了"，然后写进文档。**

### 五、验证

```
off_slot_reader.py 校准通过（off_1471151D0 -> 'poq-app-id'）
四个槽位读取，三个通过长度校验，一个被标出
本轮未改产品代码；完整套件保持 1752 通过 / 0 失败
```

### 六、仍然 Unknown

- `data.products.items` 里每个 item 的**完整字段集**：**Unknown** —— 只确认了路径与一个判定字段。
- `CasioRegion` 的**取值集合**（AU / SG / US 之外还有没有）：**Unknown**。
- `casiostore.bhawar.com` 的用途：**Unknown** —— 它落在 R759 那个 687 KB 并片里，读不出边界。
- `casioid` 两个函数的语义：**Unknown**。—— 187 B 与 893 B，未读。
"""

VERDICT = """

---

## 第 781 轮：Casio 的判定逻辑是「一条 JSON 路径 + 一个标志」

### 先查用法

```
CasioRegion         xrefs=0   ← 配置键，按名字读（与 store 元数据同类）
casio_can_purchase  xrefs=1   → sub_140954410 (2,116 B)
casiostore.bhawar   xrefs=1   → sub_14117C4E0（R759 那个 687 KB 并片）
casioid             xrefs=2   → sub_14094AF90 · sub_140952790
```

### `sub_140954410` 读三个键，新读取器一次读出

```
'data' · 'products' · 'items'
```

**所以它走 `data → products → items` 这条 JSON 路径**，再往里才引用 `casio_can_purchase`。

**合起来：遍历 `data.products.items[*]`，用每项的 `casio_can_purchase` 判定可购。**

### 于是 R780 那句"缺整张配置面"具体成两件事

1. 按 `data.products.items` 解析
2. 用 `casio_can_purchase` 判定可购

**两者在复刻件里都 ABSENT。**

### 读取器的第一次外部收益

R776 为同样的事烧掉五次尝试；这一轮**三个键一次读全**。

而且：`0x144C1E320` 读回 `'\\x01'` 且 `len=1,155,229,432` —— **那是类型表不是字符串。**
**长度校验把它标了出来。没有它，那个数字会被当成"读到了"写进文档。**

### 验证

```
产品代码未改；套件 1752 / 0
```
"""

BACKLOG_ADD = """

## 核心 — Casio 的具体缺口（R781）

原版判定逻辑（Observation）：

```
遍历 data.products.items[*]
每一项用 casio_can_purchase 判定可购
```

键名已用 `off_slot_reader.py` 读出：`data` / `products` / `items`。

| 要做的 | 现状 |
|---|---|
| 按 `data.products.items` 解析 | 复刻件未走这条路径 |
| 用 `casio_can_purchase` 判定可购 | **ABSENT** |

| 仍 Unknown | |
|---|---|
| item 的完整字段集 | 只确认路径 + 一个判定字段 |
| `CasioRegion` 的取值集合 | AU/SG/US 之外未知 |
| `casiostore.bhawar.com` 用途 | 落在 R759 那个 687 KB 并片里 |
| `casioid` 两个函数语义 | 187 B / 893 B，未读 |

**注意**：`CasioRegion` 零 xref 不等于没用到 —— 它是**数据记录里的键，代码按名字读**。
与 store 元数据同类（R761）。
"""


def main():
    for p, marker, text in ((P1, "R781", BLOCKER), (P3, "R781", BLOCKER), (P2, "第 781 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R781" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += Casio 具体缺口")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R781: Casio's availability logic is one JSON path and one flag -- and the off_ reader earned its keep\n\n"
         "R780 left casio as 'the whole configuration surface is missing', which is true but not actionable. This round\n"
         "asked how the fields are used before adding anything.\n\n"
         "Two results from the xref pass. CasioRegion has no cross-references at all, which is informative rather than\n"
         "discouraging: like the store metadata in R761, it is a key inside a data record that code looks up by name,\n"
         "so absence of references is not absence of use. And casio_can_purchase lands in sub_140954410, a 2,116-byte\n"
         "function.\n\n"
         "That function makes three keyed lookups, and the reader built in R777 resolved all three in one call:\n"
         "data, products, items. So it walks data.products.items, and deeper in the body it consults\n"
         "casio_can_purchase per item. The logic is therefore a path plus a flag, not a set of named configuration\n"
         "fields -- and both are absent from the replica.\n\n"
         "That turns R780's vague conclusion into two concrete pieces of work: parse through data.products.items, and\n"
         "decide availability from casio_can_purchase rather than inferring it.\n\n"
         "The reader also proved its worth a second way. Asked for 0x144C1E320 it returned a single control character\n"
         "with a length of 1,155,229,432 -- that is a method table rather than a string, and the length-equals-\n"
         "character-count check flagged it. Without that guard the number would have been read as a successful\n"
         "lookup and written into a document. R776 spent five tool attempts on what this round did in one call.\n\n"
         "No product code changed; suite remains 1752 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
