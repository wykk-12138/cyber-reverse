"""Record R736: the two account confirmations differ in argument type and guard -- the family's counter-example."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 165. 家族里的**反例**：两个账户确认，占位符类型不同、闸门也不同

> R736。新增 `replica/src/Cybersole.Core/Reporting/AccountDeletePrompts.cs`、对应 6 条探针。

### 一、两个长得一样、实际不一样的函数

| | `sub_14065EBF0`（accounts） | `sub_1407A8450`（account group） |
|---|---|---|
| 代入值 | `*(_DWORD*)(box+8) = v2` → **装箱 int32** | 传 `*(QWORD*)(model[8]+24)` → **对象引用，不装箱** |
| 闸门 | 计数为零 → 整段跳过 | `v14 = model[16]; if (v14) show(...)` → **宿主存在才显示** |
| 文案 | `Delete {0} accounts?` | `Delete {0}?` |
| 消息 | `…delete {0} accounts?…` | `…delete **the** {0} account group?…` |
| 按钮 | `Delete ({0}) accounts` | `Delete {0}` |

### 二、两处差异都是**行为**差异，不是写法差异

1. **同一个占位符承载两种类型**：一个是账户数量，一个是组名。传错类型不会崩，会产出一句读得通但错的话。
2. **闸门不同**：accounts 测计数，group 测**宿主窗口是否存在**。所以
   **group 的文案是无条件构造的**，只是没有宿主时不显示；accounts 的文案在零计数时**根本不构造**。

**第 2 条决定了两个函数的 contract 不同**：`Accounts()` 返回 `null`，`AccountGroup()` **从不返回 null**。
**一个给两者相同 contract 的共享助手，对其中一个必然是错的。**

### 三、这正是 R735 拒绝按形状接家族的理由，现在有了实例

R735 我只接了读过 body 的 Tasks，当时给的理由是「R731 有单复数规则、R735 没有，不能套通例」。
**这一轮给出了更硬的实例**：不是文案风格不同，是**参数类型和闸门都不同**。

### 四、探针里两条专门钉这个

- `TheAccountGroupBuildsTextsEvenForAnEmptyName`：空名仍产出 `Delete ?` ——
  因为闸门是宿主不是名字。**一个"更合理"的实现在这里会返回 null，与原版不同。**
- `TheTwoScreensUseDifferentActionShapes`：`Delete (3) accounts` 对 `Delete Main` ——
  一个带括号一个不带。**统一格式就会改掉一处按钮文字。**

### 五、验证

```
AccountDeletePromptsTests   6 / 6 通过
完整套件                    1696 通过 / 0 失败（1690 + 6）
四项度量                    4 / 0 / 17 / 78 / 0（未变）
已审候选                    10 / 129（7 实现 + 3 不可探）
```

### 六、仍然 Unknown

- group 版在**组名为空**时是否真的走到 show：**Inference（高）**，依据闸门只看宿主；未实测。
- accounts 那两个多余函数（`0x1406686f0`、`0x140686230`，键集完全相同）各自服务哪个栅格：**Unknown**。
- 六个槽位的实际内容：**Inference（高）**，依据对话框构造器的实参顺序。
"""

VERDICT = """

---

## 第 736 轮：家族里的反例 —— 占位符类型不同、闸门也不同

### 两个长得一样、实际不一样

| | accounts | account group |
|---|---|---|
| 代入值 | **装箱 int32** | **对象引用**（组名），不装箱 |
| 闸门 | 计数为零 → 整段跳过 | **宿主存在**才显示 |
| 按钮 | `Delete ({0}) accounts` | `Delete {0}` |

### 两处差异都是行为差异

1. **同一占位符承载两种类型** —— 传错不崩，会产出一句读得通但错的话
2. **闸门不同** —— group 的文案**无条件构造**，只是没宿主不显示；accounts 零计数时**根本不构造**

**所以 contract 不同**：`Accounts()` 返回 null，`AccountGroup()` 从不返回 null。
**一个给两者相同 contract 的共享助手，对其中一个必然错。**

### 这正是 R735 拒绝按形状接家族的理由，现在有了实例

不是文案风格不同，是**参数类型和闸门都不同**。

### 两条探针专门钉这个

- 空组名仍产出 `Delete ?` —— **一个"更合理"的实现在这里会返回 null，与原版不同**
- `Delete (3) accounts` 对 `Delete Main` —— **统一格式就会改掉一处按钮文字**

### 一句话

> R735 我说"不能按通例套家族"，理由是文案风格不同。
> **这一轮证明理由比那更硬：连参数类型和闸门都不一样。**

### 验证

```
AccountDeletePromptsTests   6 / 6
完整套件                    1696 通过 / 0 失败
四项度量                    4 / 0 / 17 / 78 / 0（未变）
已审候选                    10 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R736", BLOCKER), (P3, "R736", BLOCKER), (P2, "第 736 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    anchor = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if anchor in body:
        add = ("| `0x14065ebf0` | `Accounts.DeleteConfirm.*` | **已实现**（R736，6 条探针） | "
               "装箱 int32 + 计数为零不构造 |\n"
               "| `0x1407a8450` | `Accounts.Group.DeleteConfirm.*` | **已实现**（R736） | "
               "传对象引用（组名）+ 闸门是**宿主**不是值，**从不返回 null** |\n")
        body = body.replace(anchor, add + anchor, 1)
        body = body.replace("## 已审：6 个实现 + 3 个不可探，共 9 个\n\n剩下的 **120 个待审**。",
                            "## 已审：8 个实现 + 3 个不可探，共 11 个\n\n剩下的 **118 个待审**。"
                            "\n\n**家族反例（R736）**：`Accounts` 与 `Accounts.Group` 同形但**参数类型与闸门都不同** —— "
                            "`Accounts()` 零计数返回 null，`AccountGroup()` 从不返回 null。**共享助手会对其中一个错。**")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R736: the two account confirmations differ in argument type and guard -- the family's counter-example\n\n"
         "sub_14065EBF0 boxes an int32 and skips everything when the count is zero. sub_1407A8450 passes an\n"
         "object reference and guards only the show call on whether a host window exists, so it builds its\n"
         "texts unconditionally.\n\n"
         "Two behavioural differences, not stylistic ones:\n"
         "  - the same placeholder carries a count in one screen and a group name in the other\n"
         "  - Accounts() returns null for a zero count; AccountGroup() never returns null\n\n"
         "That second difference is why a shared helper with one contract would be wrong for one of the two,\n"
         "and it is a harder instance of the reason R735 gave for not wiring the family on a shared shape.\n\n"
         "Two probes pin the cases a tidier implementation would 'fix': an empty group name still yields\n"
         "'Delete ?' because the guard is the host and not the value, and the two screens disagree about\n"
         "parenthesising the value in the action label.\n\n"
         "6 probes, suite 1696 pass / 0 fail, four metrics unchanged, 11 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
