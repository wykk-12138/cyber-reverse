"""Record R738: three unresolved slots, one missing capability."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 167. 三处解不开的槽位，**同一个缺失能力**

> R738。新增 `analysis/resolve_guard_slots.py`（保留，作为这条链走到哪为止的记录）。

### 一、本来想解 profiles 的闸门

```c
v3 = off_14492E6C8();        // 无参调用一个槽
v4 = off_14492E970(v3);      // 拿结果再查表
if (!v4) → 早退
```

**三层，一层都没解出来。** 这一轮试着顺着槽往下走：

```
off_14492E6C8 -> 0x14517e5a0   data（不是代码）
off_14492E970 -> 0x14517f978   data
```

再走一层，读对象的前 40 字节：

```
0x14517e5a0:  +0 0x0000003053000000   +8 0x14517e688   +24 0x141cf1410  +32 0x141cf1450
0x14517f978:  +0 0x0000002053440000   +8 0x144db66f8   +24 0x141cf1410  +32 0x141cf1450
```

**两个对象的 `+24` / `+32` 是同一对地址** —— 那是**共享的 MethodTable / 接口分发桩**，不是 delegate 的实际目标。
`+8` 各自不同，像 MethodTable 指针。

**再往下就是猜 delegate / EEType 布局了。停手。**

### 二、三处，同一个缺失

| 轮 | 想解什么 | 卡在哪 |
|---|---|---|
| R715 | `EditValue\\`1` 那 12 个名字的**类型** | AOT 元数据的字段/属性归属 |
| R731 | 四个 `off_` 槽指向哪条**文案** | 读回值不合理，槽里是描述符不是字符串 |
| **R738** | profiles 闸门调的是**哪个 delegate** | 对象里有 MethodTable 和分发桩，**没有可读的目标** |

**三次都撞在同一个缺失能力上：没有 AOT 元数据模型**（`EEType` / `MethodTable` / `FieldDesc` / delegate 布局的解析）。

**这不是三个问题，是一个问题出现三次。**

### 三、这个结论有什么用

**它决定下一轮该做什么、不该做什么**：

- **不该**：再找一个槽位去试读 —— 前三次的形式不同、结局相同
- **该**：要么**建那个解析器**（明确的大工程，需要 EEType 布局知识），
  要么**接受这些成员的类型/目标为 Unknown 并写明缺什么**（当前做法）

**而目标里那条「每条若不可得则写 Unknown + 缺什么」正好覆盖第二种。**
所以现状是**符合判据的**，只是要把它记成一条**收敛的结论**而不是三次零散的失败。

### 四、proxies 那一屏已经接了（R737），profiles 仍不接

**理由不变且更硬了**：不是没时间，是**闸门语义解不出**。

### 五、验证

```
本轮未改产品代码
完整套件        1697 通过 / 0 失败（与 R737 相同）
已审候选        14 / 129
```

### 六、仍然 Unknown（合并成一条）

- **AOT 元数据模型**（`EEType` / `MethodTable` / `FieldDesc` / delegate 布局）：**整体 Unknown**。
  受影响的已知项：`EditValue\\`1` 的 12 个成员类型、R731 的四个文案槽、profiles 闸门的两个 delegate。
- profiles 屏是否接：**取决于上面那条**。
"""

VERDICT = """

---

## 第 738 轮：三处解不开的槽位，同一个缺失能力

### 试了两层，停手

```
off_14492E6C8 -> 0x14517e5a0  (data)
off_14492E970 -> 0x14517f978  (data)
   对象 +24/+32 -> 0x141cf1410 / 0x141cf1450   ← 两个对象给的是同一对
```

**同一对地址 = 共享的 MethodTable / 接口分发桩，不是 delegate 的实际目标。**
`+8` 各自不同，像 MethodTable。

**再往下就是猜布局。停手。**

### 三处，同一个缺失

| 轮 | 想解 | 卡在 |
|---|---|---|
| R715 | `EditValue\\`1` 的名称**类型** | AOT 字段/属性归属 |
| R731 | 四个槽指向哪条**文案** | 槽里是描述符不是字符串 |
| **R738** | profiles 闸门调哪个 **delegate** | 有 MethodTable 和分发桩，无可读目标 |

> **这不是三个问题，是一个问题出现三次。**

### 这个结论决定了下一步做什么

- **不该**：再找一个槽位试读 —— 三次形式不同、结局相同
- **该**：要么建那个解析器（明确的大工程），要么**接受 Unknown 并写明缺什么**

**而目标里「每条若不可得则写 Unknown + 缺什么」正好覆盖后者。
所以现状是符合判据的**，只是要把它记成一条收敛结论，而不是三次零散失败。

### 一句话

> 我一直把每次撞墙当成一次失败来记。**它们是同一个墙的三次截面。**

> **分开记的时候，它看起来像运气不好；合起来记，它是一个明确的工程量决定。**

### 验证

```
产品代码未改
完整套件   1697 通过 / 0 失败
已审候选   14 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R738", BLOCKER), (P3, "R738", BLOCKER), (P2, "第 738 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # one consolidated Unknown in the evidence-class document, replacing three scattered ones
    ec = r"D:\projects\cyber-reverse\docs\EVIDENCE_CLASSES.md"
    body = io.open(ec, encoding="utf-8").read()
    marker = "## 八、" + "AOT 元数据模型：一个缺失，三处症状"
    if marker not in body:
        body += """

## 八、AOT 元数据模型：一个缺失，三处症状

R715 / R731 / R738 三次尝试解开二进制里的某个槽位，形式不同、结局相同：

| 轮 | 想解什么 | 结果 |
|---|---|---|
| R715 | `EditValue\\`1` 那 12 个名字的**类型** | 描述符只给方向；`get_`/`set_` 名字不带类型 |
| R731 | 四个 `off_` 槽指向哪条**文案** | 读回值不合理 —— 槽里是描述符不是字符串指针 |
| R738 | profiles 闸门调的是**哪个 delegate** | 对象里有 MethodTable（`+8`）和共享分发桩（`+24`/`+32`），**没有可读的目标** |

**缺的是同一件东西：`EEType` / `MethodTable` / `FieldDesc` / delegate 布局的解析器。**

**所以这是「一个缺失、三处症状」，不是三次独立失败。**
在它建起来之前，受影响的成员类型与调用目标一律记 Unknown，并写明缺的是这一类能力。

**要建它，先按 §1.2 查 `rea` 的 `docs/providers/ghidra-nativeaot.md` 与 `seep-reverse-lab` 有没有现成的
EEType 解析；两处都没有，才自己写。**
"""
        io.open(ec, "w", encoding="utf-8").write(body)
        print("  EVIDENCE_CLASSES.md += §八 consolidated Unknown")
    else:
        print("  EVIDENCE_CLASSES.md already has §八")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R738: three unresolved slots are one missing capability, not three failures\n\n"
         "The profiles guard calls a delegate, looks up the result and tests null. Chasing the slot two\n"
         "levels: 0x14492E6C8 -> 0x14517e5a0 (data) -> an object whose +8 looks like a MethodTable and whose\n"
         "+24/+32 are the same two code addresses in both objects, i.e. a shared interface dispatch stub and\n"
         "not the delegate's target. Further probing would be guessing at delegate layout.\n\n"
         "That is the third time the same wall appears in a different form:\n"
         "  R715  EditValue`1 member types        -- descriptors give direction, not type\n"
         "  R731  four slots to their texts       -- the slot holds a descriptor, not a string pointer\n"
         "  R738  which delegate the guard calls  -- MethodTable and dispatch stubs, no readable target\n\n"
         "All three need an EEType/MethodTable/FieldDesc/delegate-layout parser. Recorded in EVIDENCE_CLASSES.md\n"
         "as one consolidated Unknown rather than three scattered ones, because that is what it is.\n\n"
         "The practical consequence: stop trying other slots and either build that parser -- after checking\n"
         "rea's ghidra-nativeaot provider and seep-reverse-lab per rule 1.2 -- or keep marking these as Unknown\n"
         "with the missing capability named, which is what the objective's criterion already asks for.\n\n"
         "No product code changed; suite 1697 pass / 0 fail; 14 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
