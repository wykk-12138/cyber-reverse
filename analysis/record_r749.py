"""Record R749: a different shape -- a label that returns nothing for a malformed record."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
LEDGER = r"D:\projects\cyber-reverse\docs\WITNESS_LEDGER.md"

BLOCKER = """

---

## 178. 换一类形状：智能动作的运行标签，**畸形记录不产出标签**

> R749。新增 `replica/src/Cybersole.Core/Reporting/SmartActionLastRun.cs`、对应 8 条探针。
> 换了目标区域（不是删除确认家族），因为连续两轮在同一处磨收益见底。

### 一、反编译

`sub_14061E0E0`（68 行）：

```c
v4 = property(0);
if ( !v4 ) return 0;
if ( *(_UNKNOWN **)v4 != &unk_144DB80B0 ) return 0;      // 必须是字符串
v5 = *(_QWORD *)(v4 + 8);                                // ← {0}
v6 = property(1);
if ( !v6 || *(_UNKNOWN **)v6 != &unk_144C87DE0 ) return 0; // 必须是 int32
v7 = *(_DWORD *)(v6 + 8);                                // ← {1}
v9 = localise(&off_146E90808);                           // "Triggered {0} ({1})"
```

### 二、值得记的是**两条守卫都返回 0**

**字段缺失或类型不符 → 整个标签不产出**，而不是产出 `Triggered  (0)` 这种半截东西。

**这是可断言的行为**，而且与前面几轮那类「类型不符降级为某个值」的行为**相反**：

| 函数 | 类型不符时 |
|---|---|
| `sub_1405C52E0`（Pin/Unpin，R740） | **降级为「未钉」**，照样出标签 |
| `sub_14061E0E0`（本轮的 Triggered） | **返回 0，不出标签** |

**同一份代码里两种处理方式。** 所以不能按一个通例去套 —— 与 R736 那个家族反例同类。

### 三、Inference 与不可镜像

**Observation**：两条类型守卫、两处早退、字符串与 int32 的读取、一个 locale 槽。

**Inference（高）**：字符串填 `{0}`、整数填 `{1}` —— 依据文案读作 `Triggered <动作> (<次数>)`。
格式化调用本身在探查范围之外，没读到。

**不可镜像**：类型标签的比较。在复刻件的类型化模型里不会出现"字段存在但类型错"，
**能镜像的只有 null 那一半，而那一半已镜像。**

### 四、一条我自己写错的探针

`BracesInTheNameAreLiteral` 我第一版写成期望 `Triggered {1} ({1})`（以为实参会被二次扫描）。
**`string.Format` 把实参原样插入、不二次扫描**，正确期望是 `Triggered {0} (1)`。已改。

**这类错误值得记**：我对着自己刚写的、明显有问题的期望值愣了一秒 ——
**探针的期望值也是要推敲的，不是把心里想的那句照抄上去。**

### 五、验证

```
SmartActionLastRunTests   8 / 8 通过
完整套件                  1716 通过 / 0 失败（1708 + 8）
四项度量                  4 / 0 / 17 / 78 / 0（未变）
已审候选                  26 / 129
```

### 六、仍然 Unknown

- 格式化调用的实参顺序（`{0}`/`{1}` 谁是谁）：**Inference（高）**，未读到调用点。
- 这个标签在什么 UI 位置显示：**Unknown**（只知它由智能动作的记录产生）。
- `unk_144DB80B0` 与 `unk_144C87DE0` 的具体类型名：**Unknown**（AOT 元数据，见 §八）。
"""

VERDICT = """

---

## 第 749 轮：换一类形状 —— 畸形记录不产出标签

### 反编译

```c
if (!v4 || *v4 != &unk_144DB80B0) return 0;    // 必须是字符串
v5 = *(v4 + 8);                                  // {0}
if (!v6 || *v6 != &unk_144C87DE0) return 0;    // 必须是 int32
v7 = *(_DWORD*)(v6 + 8);                         // {1}
text = localise(&off_146E90808);                 // "Triggered {0} ({1})"
```

### 值得记的是**两条守卫都返回 0**

**字段缺失或类型不符 → 整个标签不产出**，而不是 `Triggered  (0)` 这种半截东西。

**而它与前几轮的行为相反**：

| 函数 | 类型不符时 |
|---|---|
| Pin/Unpin（R740） | **降级为「未钉」**，照样出标签 |
| Triggered（本轮） | **返回 0，不出标签** |

> **同一份代码里两种处理方式。不能按通例套 —— 与 R736 那个家族反例同类。**

### 一条我自己写错的探针

第一版期望写成 `Triggered {1} ({1})`（以为实参会被二次扫描）。**`string.Format` 不二次扫描**，正确是 `Triggered {0} (1)`。

**探针的期望值也是要推敲的，不是把心里想的那句照抄上去。**

### 验证

```
SmartActionLastRunTests   8 / 8
完整套件                  1716 通过 / 0 失败
四项度量                  4 / 0 / 17 / 78 / 0（未变）
已审候选                  26 / 129
```
"""


def main():
    for p, marker, text in ((P1, "R749", BLOCKER), (P3, "R749", BLOCKER), (P2, "第 749 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(LEDGER, encoding="utf-8").read()
    anchor = "| `0x1407b8ac0` | `Update.Downloading*` |"
    if anchor in body:
        add = ("| `0x14061e0e0` | `SmartActions.LastRun.Format` | **已实现**（R749，8 条探针） | "
               "两条类型守卫**都 return 0** → 畸形记录不产出标签；**与 R740 的降级行为相反** |\n")
        body = body.replace(anchor, add + anchor, 1)
        body = body.replace("## 已审：25 / 129", "## 已审：26 / 129")
        io.open(LEDGER, "w", encoding="utf-8").write(body)
        print("  WITNESS_LEDGER.md updated")
    else:
        print("  WITNESS_LEDGER.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R749: a different shape -- a label that produces nothing for a malformed record\n\n"
         "After two rounds on the same Imported gap with nothing moving, this reads a candidate from outside\n"
         "the delete-confirmation family: sub_14061E0E0, the smart-action last-run label.\n\n"
         "Both of its type guards return zero. A field that is absent or of the wrong type produces no label at\n"
         "all, rather than 'Triggered  (0)' with a blank in it. That is expressible as null-in-null-out and is\n"
         "now implemented, with eight probes covering names, counts, zero, and both missing fields.\n\n"
         "It matters because it is the opposite of R740: the pin label degrades to 'not pinned' on a type\n"
         "mismatch and still renders, while this one refuses. Two treatments in one binary, so neither can be\n"
         "the general rule.\n\n"
         "One probe I wrote was wrong and I caught it before running: I expected string.Format to re-scan an\n"
         "argument containing braces. It does not, so the correct expectation is the literal '{0}' in the text.\n"
         "Expected values in probes need the same scrutiny as the code under test.\n\n"
         "Suite 1716 pass / 0 fail; four metrics unchanged; 26 of 129 candidates adjudicated."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
