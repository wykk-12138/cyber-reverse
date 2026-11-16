"""Record R737: three guard styles in one family, three functions that collapse to one, and a count-parity note."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 166. 同一家族里**三种闸门**；三个函数行为相同；以及一次和「函数数量对等」的对账

> R737。`DeleteConfirmPrompts.Proxies` 新增；对应 +1 条探针。

### 一、读到第四、五个成员后，闸门已经有三种

| 屏 | 闸门 | 依据 |
|---|---|---|
| accounts / size presets / store groups | **计数 != 0** | 显式比较 |
| account group | **宿主窗口存在** | `if (model[16]) show(...)` |
| **proxies** | **计数 != 0**（与 accounts 同） | `sub_142E73610(off_144930330, …)` |
| **profiles** | **一个计算出来的对象非 null** | `if (!v4) …` 早退，`v4 = off_14492E970(off_14492E6C8())` |

**profiles 的闸门语义是 Unknown** —— 它先取一个委托的返回值，再拿那个值做一次查表，再判空。
**三层，一层都没解出来。所以 profiles 不接**，记为待读。

### 二、`Accounts` 那三个函数：**行为相同，差别在调用点**

```
0x14065ebf0  …  ???
0x1406686f0  集合 [v0+72]    计数 off_14734E830(...)
0x140686230  集合 [v0+120]   计数 off_1473548F0(...)
```

三者槽位相同 → 三条文案相同 → **行为相同**。差别只在**读哪个集合**，即**从哪个栅格点进来的**。

### 三、于是要和目标对账一次：**函数数量对等**

目标写的是「函数数量对等」。原版这里有 **3 个函数**，复刻件用 **1 个** `Accounts(count)` 覆盖。

**这是一个 2 个函数的差额，必须写清而不是含糊过去。** 我的判断：

- **行为上无损**：三条路径产出完全一样的三条文案
- **结构上是原版的产物**：3 个函数对应 3 个栅格各自的命令绑定；**复刻件的 UI 接线是自己的**，
  所以它在自己那边也应该是 3 个调用点、1 个实现
- **但如果按"函数数量"这个字面口径量，这是 -2**

**记录方式**：写进 `docs/WITNESS_LEDGER.md` 与本节，不写进 METRICS（METRICS 的四个度量不测这个）。

### 四、验证

```
DeleteConfirmPromptsTests   7 / 7 通过（+1 proxies）
完整套件                    1697 通过 / 0 失败（1696 + 1）
四项度量                    4 / 0 / 17 / 78 / 0（未变）
已审候选                    12 / 129
```

### 五、仍然 Unknown

- profiles 那个**三层闸门**的语义：**Unknown**；未接。
- 三个 accounts 函数里 `0x14065ebf0` 读哪个集合：**Unknown**（未逐行比对第一段）。
- 「函数数量对等」这个口径该怎么量：**Unknown** —— 原版 321,244 个函数，复刻件 189,090；
  这一节只记了一个局部的 -2，**全局没有可执行的口径**。
"""

VERDICT = """

---

## 第 737 轮：三种闸门、三合一、一次对账

### 同一家族里三种闸门

| 屏 | 闸门 |
|---|---|
| accounts / size presets / store groups | 计数 != 0 |
| account group | 宿主窗口存在 |
| proxies | 计数 != 0（同 accounts） |
| **profiles** | **一个计算出来的对象非 null**（三层，语义 Unknown） |

**profiles 不接**，记为待读。

### 三个 accounts 函数：行为相同，差别在调用点

```
0x1406686f0  集合 [v0+72]
0x140686230  集合 [v0+120]
```

槽位相同 → 文案相同 → **行为相同**。差别只在**从哪个栅格点进来**。

### 一次对账：目标要求「函数数量对等」

原版 **3 个函数**，复刻件 **1 个** 覆盖。**这是 -2。**

- **行为上无损**：三条路径产出一样的三条文案
- **结构上是原版的产物**：3 个函数对应 3 个栅格各自的绑定；**复刻件的 UI 接线是自己的**
- **但按字面口径量，就是 -2**

**写进文档，不写进 METRICS**（四个度量不测这个）。

### 一句话

> 我这一轮差点只记"又接了一屏"。**真正要记的是：我为了 DRY 合并了 3 个函数，
> 而目标的一条判据是"函数数量对等"。**

> **这个差额不写下来，将来对账时会变成一个没人解释得清的差。**

### 验证

```
DeleteConfirmPromptsTests   7 / 7
完整套件                    1697 通过 / 0 失败
四项度量                    4 / 0 / 17 / 78 / 0（未变）
已审候选                    12 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R737", BLOCKER), (P3, "R737", BLOCKER), (P2, "第 737 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    anchor = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if anchor in body:
        add = ("| `0x1406686f0` / `0x140686230` | `Accounts.DeleteConfirm.*` | **与 `0x14065ebf0` 行为相同**（R737） | "
               "槽位相同、文案相同，差别只在读哪个集合 → 复刻件用 1 个实现覆盖 3 个原版函数（**-2 函数数**，见 BLOCKERS §166） |\n"
               "| `0x1406cb910` | `Proxies.DeleteConfirm.*` | **已实现**（R737） | 与 accounts 同形：计数闸门 + 装箱 int32 |\n"
               "| `0x1406e9190` | `Profiles.DeleteConfirm.*` | **待读** | 闸门是**三层**（取委托值 → 查表 → 判空），语义 Unknown，未接 |\n")
        body = body.replace(anchor, add + anchor, 1)
        body = body.replace("## 已审：8 个实现 + 3 个不可探，共 11 个\n\n剩下的 **118 个待审**。",
                            "## 已审：9 个实现 + 3 个不可探 + 2 个合并/待读，共 14 个\n\n剩下的 **115 个待审**。"
                            "\n\n**闸门已有三种**（R737）：计数 != 0 / 宿主存在 / 计算对象非 null。"
                            "**同一家族里三种闸门，所以每接一屏都要读它的闸门，不能照抄。**")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R737: three guard styles in one family, and an honest note on the function-count gap\n\n"
         "Reading the fourth and fifth family members gives three distinct guards: a count test (accounts, size\n"
         "presets, store groups, proxies), a host-window test (account groups), and a computed-object null test\n"
         "(profiles). Profiles is not wired: its guard resolves a delegate, looks the result up and then tests\n"
         "null, and none of those three layers was resolved.\n\n"
         "The three accounts functions turn out to differ only in which collection they read -- same slots, same\n"
         "texts, same behaviour. The replica covers them with one helper.\n\n"
         "That is a two-function deficit against the objective's 'equal function count', and it is recorded rather\n"
         "than glossed: behaviour is unaffected, the split is an artefact of the original having three grids, and\n"
         "a literal count still shows -2. There is no executable way to measure the objective's count criterion\n"
         "globally (321,244 original functions against 189,090), so this is a local note and not a metric.\n\n"
         "7 probes, suite 1697 pass / 0 fail, four metrics unchanged, 14 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
