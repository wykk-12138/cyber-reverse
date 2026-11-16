"""Record R735: the delete-confirm family, one screen read and wired."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 164. `DeleteConfirm` 家族：**只接了我读过的那一屏**，其余五屏记为待读

> R735。新增 `replica/src/Cybersole.Core/Reporting/DeleteConfirmPrompts.cs`、对应 6 条探针。

### 一、先纠正我自己的旧判断

R721 我把 `0x1405aaa60` 读成「UI 接线」——那是 **55 行的草率一瞥**，而且当时那个分类器是坏的（R730 已证）。
**正经读一遍，它是同族里信息最多的一条**：三条文案全部代入计数，且整段有闸门。

```
if (predicate(...))                       // 不成立 → 整段跳过
{
    count   = model[8][16]
    title   = format(&off_146EBA8A0, count)   // "Delete {0} tasks?"
    message = format(&off_146EBA848, count)   // "Are you sure… {0} tasks?\\nYou cannot undo…"
    dialog(title, message, 1)
    dlg[528]= format(&off_146EBA7F0, count)   // "Delete ({0}) tasks"
}
```

### 二、一个与 R732/R734 的**真实差别**，写清而不是抹平

R732（store groups）的闸门是 `if (count)`、R734（size presets）是 `if (count != 0)` —— **都是显式的零测试**。
**这里是一个 helper 调用**（`sub_142E73610`），**它的语义我没解出来**。

所以：

- **Observation**：三个槽位、同一计数、闸门不成立时整段跳过
- **Inference（中）**：那个闸门是零测试 —— **由同族推来的，不是这一条读出来的**

**这条差别很重要**：如果我把它写成"Observation: 零值不弹框"，就是把推断记成了观测。

### 三、只接一屏

家族有 7 个成员（Tasks / Accounts ×2 / Proxies / Profiles / Groups / store-groups）。
**只有 Tasks 的 body 读过**，所以 `Tasks()` 是唯一接上的入口。
其余五屏的键存在、文案形状一致（都是三条），**但 body 没读** —— 记为待读，不冒充已读。

`Build(prefix, count, copy)` 是内部通用实现，**留着给下一轮读一屏接一屏**。

### 四、两条探针值得单说

- `TheActionLabelParenthesisesTheCount`：动作按钮是 `Delete (9) tasks` —— **计数在括号里**，
  而标题与消息里没有括号。一个"顺手统一三种措辞"的改写会改掉按钮上的字。
- `ASingleTaskIsStillPhrasedInThePlural`：`count=1` 给出 **"Delete 1 tasks?"** ——
  **目录里每屏只有一种形式，不做单复数**。丑但忠实；与 R731 那个**有**单复数规则的功能形成对照。

### 五、验证

```
DeleteConfirmPromptsTests   6 / 6 通过
完整套件                    1690 通过 / 0 失败（1684 + 6）
四项度量                    4 / 0 / 17 / 78 / 0（未变）
已审候选                    8 / 129（6 实现 + 2 不可探）
```

### 六、仍然 Unknown

- `sub_142E73610`（Tasks 的闸门）的语义：**Unknown**；零值规则是推断。
- 其余五屏的闸门与文案条数：**Unknown**（body 未读）。
- 三个槽位的实际内容：**Inference（高）**，依据 `sub_140740120` 的实参顺序（R732 确立）。
"""

VERDICT = """

---

## 第 735 轮：`DeleteConfirm` 家族 —— 只接读过的那一屏

### 先纠正旧判断

R721 我把 `0x1405aaa60` 读成「UI 接线」—— **55 行的草率一瞥 + 当时坏掉的分类器**。正经读一遍，它是同族里信息最多的。

```
if (predicate(...)) {
    title   = format(TitleFormat,   count)   // "Delete {0} tasks?"
    message = format(MessageFormat, count)
    dlg[528]= format(ActionFormat,  count)   // "Delete ({0}) tasks"
}
```

### 一个与同族的真实差别

R732 是 `if (count)`、R734 是 `if (count != 0)` —— **都是显式零测试**。**这里是 helper 调用，语义没解出来。**

- **Observation**：三槽位、同计数、闸门不成立整段跳过
- **Inference（中）**：闸门是零测试 —— **同族推来的**

**写成"Observation: 零值不弹框"就是把推断记成观测。**

### 只接一屏

家族 7 个成员，**只有 Tasks 的 body 读过**。其余五屏键存在、形状一致，**但 body 没读 —— 记待读，不冒充已读。**

### 两条探针

- 动作按钮是 `Delete (9) tasks` —— **计数在括号里**，标题与消息没有。"统一措辞"会改掉按钮上的字。
- `count=1` → **"Delete 1 tasks?"** —— **这屏不做单复数**。丑但忠实，
  与 R731 那个**有**单复数规则的功能形成对照。

### 一句话

> 同一轮里既有"不做单复数"的，也有"有单复数规则"的。
> **所以不能按一个通例去套整个家族 —— 每一屏都得读。**

### 验证

```
DeleteConfirmPromptsTests   6 / 6
完整套件                    1690 通过 / 0 失败
四项度量                    4 / 0 / 17 / 78 / 0（未变）
已审候选                    8 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R735", BLOCKER), (P3, "R735", BLOCKER), (P2, "第 735 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    old = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if old in body:
        add = ("| `0x1405aaa60` | `Tasks.DeleteConfirm.*` | **已实现**（R735，6 条探针） | "
               "三条文案全部代入计数；闸门是 helper 调用（**语义未解，零值规则属推断**）；"
               "`count=1` 给 \"Delete 1 tasks?\" —— **这屏不做单复数** |\n")
        body = body.replace(old, add + old, 1)
        body = body.replace("## 已审：5 个实现 + 3 个不可探，共 8 个\n\n剩下的 **121 个待审**。",
                            "## 已审：6 个实现 + 3 个不可探，共 9 个\n\n剩下的 **120 个待审**。"
                            "\n\n`DeleteConfirm` 家族还有 5 个成员（Accounts ×2 / Proxies / Profiles / Groups / store-groups）"
                            "**body 未读**，形状一致但不能按通例套 —— R735 与 R731 一个不做单复数、一个有单复数规则。")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R735: the DeleteConfirm family -- only the screen whose body was read is wired\n\n"
         "R721 dismissed 0x1405aaa60 as UI wiring from a glance at 55 lines, back when the classifier I was\n"
         "using had already been shown broken. Read properly it is the most informative member of the family:\n"
         "three texts, all carrying the selection count, behind a guard that skips the whole body.\n\n"
         "One real difference from its siblings is recorded rather than smoothed over: R732 tests `if (count)`\n"
         "and R734 tests `if (count != 0)`, both explicit, while this one calls a helper whose semantics were\n"
         "not resolved. The zero rule here is therefore an inference from the family, not an observation --\n"
         "writing it as an observation would be exactly the substitution the evidence rules forbid.\n\n"
         "Only the tasks screen is wired. The other five have keys and matching text shapes but unread bodies,\n"
         "and this round produced a concrete reason not to generalise: this screen does not pluralise, so\n"
         "count=1 yields 'Delete 1 tasks?', while TaskButtonLabel in R731 does have a plural rule.\n\n"
         "6 probes, suite 1690 pass / 0 fail, four metrics unchanged, 9 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
