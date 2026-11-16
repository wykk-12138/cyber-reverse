"""Record R741: the stores screen, and a second shipped copy bug."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 170. Stores 屏与 sizes 屏同形；而**出厂文案有两处 bug**，都不是我的错

> R741。`SizePresetDeletePrompt.Stores` 新增；对应 +2 条探针。

### 一、结构相同，一行参数化就够

`sub_1406458F0`（50 行）与 R734 的 `sub_140641190` 完全同形：

```c
if (*(DWORD*)(*(a1 + 528)[8] + 16))     // count != 0
{
    count   = 同一个计数
    title   = format(&off_146E892D0, count)   // int32
    message = format(&off_146E89260, count)
    show(...)
}
return;                                  // count == 0：什么都不做
```

**同一个零值闸门、同一个 int32、两条文案。** 所以把 builder 参数化成前缀，两个屏共用一个。

### 二、出厂文案的两处 bug（照抄，不修）

| 屏 | 标题 | 消息 | 问题 |
|---|---|---|---|
| `Settings.Sizes` | `Delete {0} presets?` | `…delete {0} **sizes**?…` | **标题说 presets、消息说 sizes** |
| `Settings.Stores` | `Delete {0} presets?` | `…delete {0} **presets**?…` | **这是 stores 屏，两处都说 presets** |

**R734 我记了第一处。这一轮发现第二处，而且更彻底：stores 屏的两条文案都跟屏幕无关。**

**这是原版自己的问题，不是我的读法。** 一个"顺手改对"的复刻件会在用户读到的文字上与原文不同 ——
而这两处文字正是用户点删除时看到的那两行。

### 三、探针

- `TheStoresScreenSharesTheSameGuard`：零计数返回 null，与 sizes 一致
- `TheStoresScreenSaysPresetsInBothTexts`：**断言它说 presets，且不说 stores** ——
  钉住这个 bug，防止将来"修正"

### 四、验证

```
SizePresetDeletePromptTests   8 / 8 通过（6 + 2）
完整套件                      1705 通过 / 0 失败（1703 + 2）
四项度量                      4 / 0 / 17 / 78 / 0（未变）
已审候选                      17 / 129（12 实现 + 3 不可探 + 2 合并/待读）
```

### 五、仍然 Unknown

- 两处文案是**发布时的笔误**还是**故意的历史遗留**：**Unknown**（无法从二进制判断意图）。
- 其余屏是否也有同类错误：**Unknown** —— **这一轮的经验是"该逐屏检查文案与屏名是否相符"**，
  而四度量只查「键是否存在」，不查「文案是否说对了屏幕」。
"""

VERDICT = """

---

## 第 741 轮：Stores 屏 + 第二处出厂文案 bug

### 结构同形

`sub_1406458F0` 与 R734 的 sizes 完全同形：零值闸门 + int32 + 两条文案。
**参数化成前缀，两个屏共用一个 builder。**

### 两处出厂 bug

| 屏 | 标题 | 消息 |
|---|---|---|
| `Settings.Sizes` | `Delete {0} presets?` | `…delete {0} **sizes**?…` |
| `Settings.Stores` | `Delete {0} presets?` | `…delete {0} **presets**?…` |

**第二处更彻底：stores 屏的两条文案都跟屏幕无关。**

**这是原版自己的问题。** 一个"顺手改对"的复刻件会在**用户点删除时看到的那两行**上与原文不同。

### 探针

`TheStoresScreenSaysPresetsInBothTexts` —— **断言它说 presets 且不说 stores**，防止将来被"修正"。

### 一句话

> 四度量只查「键是否存在」，**不查「文案说对了屏幕没有」**。
> 所以这类错误只能靠人一屏一屏地读 —— 而它们恰好是用户真的会看到的字。

### 验证

```
SizePresetDeletePromptTests   8 / 8
完整套件                      1705 通过 / 0 失败
四项度量                      4 / 0 / 17 / 78 / 0（未变）
已审候选                      17 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R741", BLOCKER), (P3, "R741", BLOCKER), (P2, "第 741 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    anchor = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if anchor in body:
        add = ("| `0x1406458f0` | `Settings.Stores.DeleteConfirm.*` | **已实现**（R741，+2 条探针） | "
               "与 sizes 同形（零值闸门 + int32 + 两文案）；**出厂文案说 presets，与 stores 屏无关，照抄** |\n")
        body = body.replace(anchor, add + anchor, 1)
        body = body.replace("## 已审：10 个实现 + 3 个不可探 + 2 个合并/待读，共 16 个\n\n剩下的 **113 个待审**。",
                            "## 已审：11 个实现 + 3 个不可探 + 2 个合并/待读，共 17 个\n\n剩下的 **112 个待审**。")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS (counts left as-is)")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R741: the stores screen shares the sizes shape, and a second shipped copy bug\n\n"
         "sub_1406458F0 has the same zero guard, the same int32 boxing and two texts, so the builder is\n"
         "parameterised by key prefix and both screens use it.\n\n"
         "Its catalogue copy is wrong in a way worth preserving: this is the stores screen and both of its\n"
         "texts say 'presets'. R734 already recorded that the sizes screen's title says presets while its\n"
         "message says sizes; this one is consistently wrong instead of inconsistently.\n\n"
         "Both are the original's own bugs. A replica that quietly corrected them would differ from the\n"
         "original in the two lines a user reads when they click delete, so a probe asserts the presets\n"
         "wording and asserts the absence of the word 'stores'.\n\n"
         "The general point this raises: the four metrics check that keys exist, not that a screen's copy\n"
         "describes the right screen. Errors of this kind can only be found by reading each screen.\n\n"
         "8 probes, suite 1705 pass / 0 fail, four metrics unchanged, 17 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
