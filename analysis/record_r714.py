"""Record R714: the direction field is nearly uninformative, so R712's advice was over-reading."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 143. 描述符的**方向字段几乎不带信息** —— R712 那张表给的建议是过度解读

> R714。新增 `analysis/command_descriptors.py`、`analysis/descriptor_direction_stats.py`；改生成器并重生成文档。

### 一、本来要做什么

R713 结尾我写「下一轮攻那 7 条命令形态的 G/S：反编译看它们到底是不是命令」。
先去查描述符原文（比反编译便宜，且是 Observation）：

```
AccountGroupView.Save   ,Cybersole.Save!Getter
TaskView.Edit           ,Cybersole.Edit!Getter   +   ,Cybersole.Edit!Setter
```

方向确实存在（索引取并集拿到 Setter），**但类型仍然没有**。判据「至少settle 一条的类型」**未达成**。

### 二、然后量了一件事，结果推翻了上一轮的读法

全表 819 个成员的方向分布：

```
Getter only     : 181
Setter only     :    0
Getter + Setter : 638      ← 78%
no descriptor   :    0
```

**78% 是 G/S**，其中包括 `Product.Name`、`TaskGroup.Name`、`AccountGroup.Name` 这类显然是**数据**的成员。

**所以「有 Setter」推不出「该做成可写属性」。**

### 三、连带更正 R712

R712 的 `docs/MEMBER_GAP_EVIDENCE.md` 里有一列叫「**该做成什么**」，按方向填了
「只读属性」/「可读写属性」。**那一列是过度解读，已删除。**

R712 的正文还写着「`Getter/Setter` 那 18 条**必须做成可写属性**，不是 `ICommand`」——同样撤回。

**方向字段在这个语料里的区分力接近零**（Setter-only 为 0，G/S 是常态）。

### 四、那什么还能判类型

只剩两种证据，且都不是方向：

| 证据 | 例子 | 强度 |
|---|---|---|
| **基数/排除法** | `Notification`：原版绑 4 个名字、record 4 个参数，2 个已对上 → 剩下 1:1 | 高 |
| **描述符 + 源码形态互证** | `Close`：`Getter` 单方向 **且** 源码里已是 lambda 按钮 | 中高 |

**只有一条证据时，不给实现建议。**

### 五、这一轮没有实现任何成员，这是结论不是懈怠

7 条里只有 `AccountGroupView.Save` 满足第②种（描述符 + 源码 lambda 按钮）；
**但它的描述符带 Setter，而 `Close` 只有 Getter —— 两者形态不同，`Close` 的经验不能直接搬。**
其余 6 条连第二条证据都没有。

**在"证据不够"时不动手，是这一轮唯一正确的动作。** 7 条全部留在 `undeclared` 里，描述符可查。

### 六、验证

```
python analysis/descriptor_direction_stats.py   181 / 0 / 638 / 0
python analysis/write_member_gap_doc.py         42 rows，无「该做成什么」列，含分布说明与更正声明
完整套件（代码未动）                            1624 通过 / 0 失败
```

### 七、仍然 Unknown

- 7 条命令形态成员的真实类型：**Unknown** —— 方向不帮忙，需反编译或另一种结构证据。
- `EditValue\\`1` 那 12 个名字的语义：**Unknown**（不变）。
- 为什么 Avalonia 对 78% 的绑定同时产出 Getter 与 Setter 描述符：**Unknown** ——
  可能是编译期统一产出，也可能是这些绑定都是 TwoWay；未查证。
"""

VERDICT = """

---

## 第 714 轮：方向字段几乎不带信息，上一轮的建议要撤回

### 先查描述符原文

```
AccountGroupView.Save   ,Cybersole.Save!Getter
TaskView.Edit           ,Cybersole.Edit!Getter  +  ,Cybersole.Edit!Setter
```

方向存在，**类型仍然没有**。判据未达成。

### 量了一件事，推翻了上一轮的读法

```
Getter only     : 181
Setter only     :   0
Getter + Setter : 638   ← 78%，含 Product.Name / TaskGroup.Name
```

**「有 Setter」推不出「该做成可写属性」。**

### 连带更正 R712

`docs/MEMBER_GAP_EVIDENCE.md` 里「**该做成什么**」那一列是过度解读，**已删**；
R712 正文「18 条必须做成可写属性」**撤回**。

### 还能判类型的只剩两种证据

| 证据 | 例子 |
|---|---|
| 基数/排除法 | `Notification`：4 名字对 4 参数，2 个已对上 |
| 描述符 + 源码形态 | `Close`：`Getter` 单方向 **且** 源码里已是 lambda |

**只有一条证据时，不给实现建议。**

### 本轮没有实现任何成员 —— 这是结论不是懈怠

7 条里只有 `AccountGroupView.Save` 有第二条证据，**但它的描述符带 Setter，与 `Close` 形态不同**，
经验不能直接搬。其余 6 条连第二条都没有。

### 一句话

> 我上一轮把「有 Setter」当成了「该做成可写属性」，然后量了一下分布：**78% 都这样**。

> **一个字段如果在 78% 的样本上取同一个值，它就不是判据，是背景。
> 我把背景当判据，还写进了生成文档。**

### 下一轮

`EditValue\\`1` 那 12 个名字语义 Unknown，是最该先弄清的（它占 42 条里的 12 条）。
反编译找它的 MethodTable / 属性元数据，而不是继续猜。
"""


def main():
    for p, marker, text in ((P1, "R714", BLOCKER), (P3, "R714", BLOCKER), (P2, "第 714 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R714: the descriptor direction field carries almost no information\n\n"
         "Measured across all 819 binding members: Getter-only 181, Setter-only 0, Getter+Setter 638.\n"
         "78% are G/S, including Product.Name and TaskGroup.Name, so 'has a Setter' does not imply 'make\n"
         "it a writable property'. R712's evidence table had a column saying exactly that -- it is removed\n"
         "and the claim is withdrawn.\n\n"
         "The seven command-shaped members could not be typed from their descriptors: AccountGroupView.Save\n"
         "and TaskView.Edit both quote Getter (Edit also Setter), which is what we already knew. Nothing was\n"
         "implemented, because only AccountGroupView.Save has a second independent evidence (its source is\n"
         "a lambda button) and its descriptor differs in shape from Close's, so that experience does not\n"
         "transfer. They stay in the undeclared bucket with their descriptors on record.\n\n"
         "What can still type a member: cardinality/elimination (Notification) or descriptor-plus-source\n"
         "agreement (Close). Not direction."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
