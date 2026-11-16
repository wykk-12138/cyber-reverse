"""Record R734: the ranked candidate list and SizePresetDeletePrompt."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 163. 候选排序落地，第四个实现：**空选择不弹框**

> R734。新增 `analysis/witness_ranking.py`、`analysis/witness_ranking.tsv`；
> `replica/src/Cybersole.Core/Reporting/SizePresetDeletePrompt.cs`、对应 6 条探针。

### 一、把台账的经验系统化

R733 那条经验（"引用的文案带占位符 → 大概率可探"）现在能算了：
对 129 个候选，数它引用的键里有多少个**对应的文案含 `{0}`/`{1}`**。

```
候选总数                 129
至少引一个占位符文案       38
  其中还没读的            35
```

**顶上是整个 `*DeleteConfirm.ActionFormat/MessageFormat/TitleFormat` 家族**
（Tasks / Accounts / Proxies / Profiles / Groups，7 个），与 R732 的 store-group 同形状。

### 二、先否掉一个：`0x1407b8ac0`（`Update.DownloadingFormat`）

看着像百分比格式化器，读了发现：`*(_DWORD *)(v10 + 8) = 0` —— **参数硬编码为 0**。
它是"下载对话框的初始状态（Downloading 0%）"，不是百分比计算。**不合格。**

**顺带得出**：真正更新百分比的是**另一个函数**，`Update.DownloadingFormat` 的占位符在别处被填。

### 三、实现第四个：`0x140641190`（尺寸预设删除确认）

```c
if (*(DWORD*)(*(a1 + 528)[8] + 16))     // 选择计数
{
    title   = format(&off_146E891F8, count);   // "Delete {0} presets?"
    message = format(&off_146E89188, count);   // "Are you sure you want to delete {0} sizes?\\n…"
    show(...)
}
return;                                  // count == 0：什么都不做
```

**可断言的行为是那个零值闸门**：计数为 0 时**整个函数被跳过**，不弹任何框。
**一个无条件构造对话框的复刻件会在空选择时显示「delete 0 sizes?」——原版从不这样。**

### 四、出厂文案自己不一致，照抄不修

- 标题：`Delete {0} presets?`
- 消息：`Are you sure you want to delete {0} sizes?\\nYou cannot undo this action.`

**标题说 presets，消息说 sizes。** 那是目录里的实际内容。
**一个"顺手统一"成一致措辞的复刻件，会在用户读到的字符串上与原文不同。**
探针 `TheShippedWordingIsKeptEvenWhereItDisagreesWithItself` 钉住这一点。

### 五、验证

```
SizePresetDeletePromptTests   6 / 6 通过
完整套件                      1684 通过 / 0 失败（1678 + 6）
四项度量                      4 / 0 / 17 / 78 / 0（未变）
已审候选                      7 / 129（5 实现 + 2 不可探）
```

### 六、仍然 Unknown

- `off_146E891F8` / `off_146E89188` 的槽位内容：**Inference（高）**，依据是 `sub_140740120` 的实参顺序，
  而该顺序由 R732 的 store-group 案例确立。
- 同一个函数是否同时服务「sizes」和「presets」两个栅格：**Unknown**；文案不一致说明源码里有一条是旧的。
- `0x1407b8ac0` 之外的百分比更新函数在哪：**Unknown**（未找）。
"""

VERDICT = """

---

## 第 734 轮：排序落地，四个实现 —— 空选择不弹框

### 经验变成可算

对 129 个候选数「引用的键里有几个对应含占位符的文案」：

```
至少引一个       38
  还没读        35
```

顶上整个 `*DeleteConfirm.*` 家族（7 个），与 R732 同形状。

### 先否掉一个

`0x1407b8ac0`（`Update.DownloadingFormat`）看着像百分比格式化器，
读了发现**参数硬编码为 0**（`*(_DWORD*)(v10+8) = 0`）—— 那是"下载对话框初始状态"，不是计算。**不合格。**

### 第四个实现：尺寸预设删除确认

```c
if (count != 0) { title = format(TitleFormat, count); message = format(MessageFormat, count); show(); }
return;                       // count == 0：什么都不做
```

**可断言的是那个零值闸门**：空选择时**整个函数被跳过**。
**无条件构造对话框的复刻件会显示「delete 0 sizes?」—— 原版从不这样。**

### 出厂文案自己不一致，照抄不修

标题说 **presets**，消息说 **sizes**。那是目录里的实际内容。
**"顺手统一"成一致措辞的复刻件，会在用户读到的字符串上与原文不同。**

### 一句话

> 这一轮抓到的是两件"实现者会顺手改掉"的事：
> **一个看起来多余的零值闸门，和一处看起来是笔误的文案不一致。**
> **两处都是原版的行为。**

### 验证

```
SizePresetDeletePromptTests   6 / 6
完整套件                      1684 通过 / 0 失败
四项度量                      4 / 0 / 17 / 78 / 0（未变）
已审候选                      7 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R734", BLOCKER), (P3, "R734", BLOCKER), (P2, "第 734 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    old = "| `0x140654480` | `Common.Hour12/Hour24/Disabled` 等 | **不可探** |"
    if old in body:
        add = ("| `0x140641190` | `Settings.Sizes.DeleteConfirm.*` | **已实现**（R734，6 条探针） | "
               "`if (count != 0)` 闸门：零选择不弹框；标题说 presets、消息说 sizes，**照抄** |\n"
               "| `0x1407b8ac0` | `Update.Downloading*` | **不可探** | 构造下载对话框，**百分比参数硬编码为 0**，"
               "没有计算 |\n")
        body = body.replace(old, add + old, 1)
        body = body.replace("## 已审：4 个实现 + 2 个不可探，共 6 个\n\n剩下的 **123 个待审**。",
                            "## 已审：5 个实现 + 3 个不可探，共 8 个\n\n剩下的 **121 个待审**。"
                            "\n\n排序见 `analysis/witness_ranking.tsv`（按引用的占位符文案数），"
                            "**38 个候选引用了带占位符的文案，其中 35 个未读**。")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md: two rows added, counts updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R734: rank candidates by placeholder texts, and SizePresetDeletePrompt shows nothing on an empty selection\n\n"
         "R733's observation is now computable: 38 of the 129 candidates load at least one locale value containing\n"
         "a placeholder, 35 of those unread, and the top of the list is a whole *DeleteConfirm.* family that\n"
         "matches R732's shape.\n\n"
         "Rejected first: 0x1407b8ac0 looked like a download percentage formatter but hardcodes the argument to\n"
         "zero -- it builds the dialog's initial 'Downloading 0%' state. The real percentage updater is elsewhere.\n\n"
         "Implemented the fourth: sub_140641190 guards everything on a non-zero selection count, so an empty\n"
         "selection shows no dialog at all. A replica that builds the dialog unconditionally would display 'delete\n"
         "0 sizes?' where the original says nothing.\n\n"
         "Also preserved rather than tidied: the shipped title says 'presets' and the shipped message says 'sizes'.\n"
         "Harmonising them would differ from the original in a string the user reads, so a probe pins both.\n\n"
         "6 probes, suite 1684 pass / 0 fail, four metrics unchanged, 7 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
