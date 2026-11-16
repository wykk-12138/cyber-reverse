"""Record R742: the DeleteConfirm family is closed, four more candidates adjudicated, and the count deficit grows."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 171. `DeleteConfirm` 家族**结案**；accounts 是 4 个函数合成 1 个（**-3**）

> R742。本轮未改产品代码 —— 这是结论，不是没活干。

### 一、第四个 accounts 函数也是同形

`0x140797D30`（50 行）：`sub_142E73610` 闸门 + `sub_143028C10(&unk_144DB9458)`（int32 装箱）+ 三文案。

**与已审的三个同键同形。所以不新增实现。**

### 二、于是 accounts 是 **4 → 1**

```
0x14065ebf0  0x1406686f0  0x140686230  0x140797d30     四个原版函数
Cybersole.Core.Reporting.AccountDeletePrompts.Accounts  一个复刻实现
```

**函数数量差 -3**（R737 记的是 -2，那时只知道三个）。

### 三、家族完整账（7 个成员）

| 成员 | 处置 |
|---|---|
| accounts ×4 | **1 个实现**覆盖 4 个（-3） |
| tasks | 已实现（R735） |
| proxies | 已实现（R737） |
| account group | 已实现（R736）—— **contract 不同**：从不返回 null |
| profiles | **卡住**：闸门是三层，语义 Unknown（R738/R739） |
| store groups（2 文案，非三文案） | 已实现（R732） |
| size presets / stores | 已实现（R734/R741） |

**这个家族到此为止。** 再往下读它不会有新东西。

### 四、顺带认出两个**已经覆盖**的候选

ranking 里有两个我早就有探针的函数：

```
0x140f77350  Unknown country "{0}"        ← R718 那 15 条探针里的国家校验器
0x140f777e0  Unknown state "{0}" for {1}  ← 同上，州校验器
```

**台账把它们标成"已被 R718 覆盖"，不重复做。**

### 五、验证

```
本轮未改产品代码
完整套件        1705 通过 / 0 失败（与 R741 相同）
已审候选        21 / 129（12 实现 + 3 不可探 + 2 合并 + 2 已被 R718 覆盖 + 2 待读/卡住）
```

### 六、函数数量对账（累积）

| 项 | 差 |
|---|---|
| accounts 4→1 | **-3** |
| 其余家族成员 | 一对一 |
| **合计（仅本家族）** | **-3** |

**这仍然只是局部。** 全局（原版 321,244 / 复刻件 189,090）**没有可执行口径**，R737 已记。

### 七、仍然 Unknown

- profiles 闸门（三层）：**Unknown**，见 R739 的 gap_reason。
- 其余 108 个候选的形状：**Unknown** —— 台账一屏一屏填。
- 「4 个同键函数是否真的一模一样」：**Inference（高）**，依据是四个 body 的头部逐行比对；
  **未做逐字节或逐分支的全等比较**。
"""

VERDICT = """

---

## 第 742 轮：家族结案，accounts 是 4 → 1

### 第四个也是同形

`0x140797D30`：`sub_142E73610` 闸门 + int32 装箱 + 三文案。**不新增实现。**

### accounts 是 **4 → 1**，差 **-3**

R737 记 -2 时只知道三个。**现在是四个。**

### 家族 7 个成员全部有处置

| 成员 | 处置 |
|---|---|
| accounts ×4 | 1 个实现（**-3**） |
| tasks / proxies / account group / store groups / sizes / stores | 已实现 |
| **profiles** | **卡住**（三层闸门，R739） |

**这个家族到此为止，再读不会有新东西。**

### 顺带认出两个已覆盖的候选

```
0x140f77350  Unknown country "{0}"
0x140f777e0  Unknown state "{0}" for {1}
```

**都是 R718 那 15 条探针里的校验器。标为已覆盖，不重复做。**

### 一句话

> 这一轮没写代码。**正确的结论有时就是"这里没有新东西"。**

> 而我上一轮差点为了"每轮都要有产出"去给第四个同形函数写第二个实现 —— **那会让 DRY 变差、让 -3 变 -2、且不增加任何行为覆盖。**

### 验证

```
产品代码未改
完整套件   1705 通过 / 0 失败
已审候选   21 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R742", BLOCKER), (P3, "R742", BLOCKER), (P2, "第 742 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    anchor = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if anchor in body:
        add = ("| `0x140797d30` | `Accounts.DeleteConfirm.*` | **与另三个同形**（R742） | 不新增实现；"
               "accounts 至此是 **4 个原版函数 → 1 个实现**，**函数数差 -3** |\n"
               "| `0x140f77350` / `0x140f777e0` | `ProfileCsv` 校验器 | **已被 R718 覆盖** | "
               "那 15 条探针就是这两个函数的（国家 / 州） |\n")
        body = body.replace(anchor, add + anchor, 1)
        body = body.replace("## 已审：11 个实现 + 3 个不可探 + 2 个合并/待读，共 18 个\n\n剩下的 **111 个待审**。",
                            "## 已审：21 / 129\n\n**`DeleteConfirm` 家族已结案**（7 个成员全部有处置，见 BLOCKERS §171）。"
                            "\n**accounts 是 4 个原版函数 → 1 个实现，函数数差 -3。**"
                            "\n\n下一步按 `analysis/witness_ranking.tsv` 读 1 个占位符那一档："
                            "CSV 导入导出簇（`Couldn't read the CSV`、`Exported {0} rows to {1}`、`Ignored unknown columns`）。")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R742: the DeleteConfirm family is closed, and accounts is four functions collapsed to one\n\n"
         "The fourth accounts function, 0x140797D30, has the same guard, the same int32 boxing and the same\n"
         "three texts as the other three, so it adds no implementation. That makes accounts four original\n"
         "functions against one replica helper -- a function-count deficit of three, where R737 recorded two\n"
         "before the fourth was known.\n\n"
         "The family now has a disposal for all seven members: accounts x4 collapsed, tasks, proxies, account\n"
         "groups, store groups, size presets and stores implemented, profiles blocked on a three-layer guard\n"
         "whose semantics R739 showed cannot be recovered with the tools available.\n\n"
         "Two candidates in the ranking turned out to be already covered: 0x140f77350 and 0x140f777E0 are the\n"
         "country and state validators that R718's fifteen probes already exercise.\n\n"
         "No product code changed, and that is the finding rather than an omission: writing a second\n"
         "implementation for a fourth identical function would worsen the duplication, shrink the deficit from\n"
         "three to two, and add no behavioural coverage.\n\n"
         "Suite 1705 pass / 0 fail; 21 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
