"""Record R726: byte-level version diff cannot separate logic change from relayout."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
EC = r"D:\projects\cyber-reverse\docs\EVIDENCE_CLASSES.md"

BLOCKER = """

---

## 155. 版本差分**不能**用来选稳定见证 —— 字节哈希分不清「逻辑变了」和「重排了」

> R726。新增 `analysis/function_stability.py`；复用 `pdata_unwind.py` 的 PE 解析。

### 一、上一轮的计划，这一轮被自己否掉

R725 说：跑 5.18.32 ↔ 5.18.35 差分，用「两版相同的函数」当稳定见证。
**做出来才发现这个数不能用。**

`pe_diff.py` 是**节级**的（它自己文档里写着「diff shows change, never intent」），没有函数匹配。
于是复用 `analysis/pdata_unwind.py` 的 `parse_pe` / `rva_to_off`，对每个 `RUNTIME_FUNCTION` 范围算 SHA-256。

### 二、结果

```
5.18.32  .pdata 条目   277,094
5.18.35  .pdata 条目   277,265   (+171)
已哈希                 277,094 / 277,265

两版字节相同            69,460   (25.1%)
只在 5.18.32           207,634
只在 5.18.35           207,805
同一 RVA 同索引          1,750   ( 0.6%)
```

**尺寸只差 62,976 字节（0.05%），却有 75% 的函数字节不同，而只有 0.6% 保住原地址。**

### 三、我先怀疑是重定位噪声，于是加了掩码

掩码：把每个 4 字节对齐的字，若其值落在镜像地址区间内，置零。结果：

```
原始      25.1% 相同
掩码后    29.4% 相同   ← 只涨 4.3 个点
```

**掩码不够。** 真正的原因是 **`lea reg, [rip+disp32]`**：整体重排后 disp32 变成别的小数值，
**它们不在我掩的地址范围里**。要盖住就得把所有立即数与位移都掩掉 —— **那是反汇编级归一化**，
不是哈希能做的。

### 四、还有一个独立的证据：差异是**对称**的

```
只在 5.18.32  207,634
只在 5.18.35  207,805
```

**两边几乎相等，都是 20 万量级。** 若只是少数函数被改，这两个数会**都很小**。
现在这个形状说明的是**整片移动**，不是**局部修改**。

### 五、所以结论是什么（不夸大）

**否掉的**：字节哈希（raw 或地址掩码）**不能**在这个二进制上把「逻辑变了」和「重排了」分开。
R725 那条「用版本差分选稳定见证」的计划，**按哈希实现不可行**。

**还站得住的**：`+171` 个 `.pdata` 条目是**真实信号** —— 一个版本增量的净新增非叶函数数，
与重排无关。这是差分能给的、可靠的那一部分。

**要做到我原本想要的**，需要**指令级归一化差分**（把所有立即数/位移抹平后比指令序列），
那是反汇编器 + 匹配算法的工作（diaphora / radare2 那一类），**不是本轮能顺手写的**。
按 §1.2，若真要做，应先读 `seep-reverse-lab` 与 `rea` 里有没有现成的。

### 六、仍然 Unknown

- 那 69,460 个「字节相同」的函数里，有多少是**真没变**、多少是**碰巧没引用地址**：**Unknown**。
- 指令级归一化后能恢复多少稳定函数：**Unknown**（未实施）。
- 那 +171 个新函数是什么：**Unknown**（未定位）。

### 七、这一轮的判断

> **我上一轮把「版本差分」当成 C7c 的救命证据，这一轮量完发现它给的是一个被重排污染的 25%。**

**这不是白跑**：如果不量就按 R725 的计划去挑「稳定函数」，我会挑到一批**因为不含地址引用而稳定**的函数 ——
它们恰好是最不像业务逻辑的那种。
"""

VERDICT = """

---

## 第 726 轮：版本差分不能用来选稳定见证

### 计划被自己否掉

R725 说用「两版相同的函数」当稳定见证。做出来发现这个数不能用。
`pe_diff.py` 是节级的，于是复用 `pdata_unwind.py` 解析 PE，对 277,094 个 `RUNTIME_FUNCTION` 算 SHA-256：

```
两版字节相同     69,460  (25.1%)
只在 5.18.32    207,634
只在 5.18.35    207,805
同一 RVA        1,750  ( 0.6%)
```

**尺寸只差 0.05%，却有 75% 函数字节不同，只有 0.6% 保住地址。**

### 加掩码，只涨 4.3 个点

```
原始    25.1%   掩码后  29.4%
```

**掩码不够**：真正的原因是 `lea [rip+disp32]`——重排后 disp32 变成别的小数值，不在掩码范围内。
要盖住得把所有立即数/位移都抹平，**那是反汇编级归一化**。

### 独立佐证：差异是对称的

```
只在 32  207,634      只在 35  207,805
```

**两边都 20 万量级**。若只是少数函数被改，两个数会都很小。**这个形状说明整片移动，不是局部修改。**

### 结论

**否掉的**：字节哈希分不清「逻辑变了」和「重排了」，R725 那条计划按哈希不可行。
**站得住的**：`+171` 个 `.pdata` 条目是净新增非叶函数数 —— 与重排无关的真实信号。

### 一句话

> **我上一轮把「版本差分」当成 C7c 的救命证据，这一轮量完发现它给的是一个被重排污染的 25%。**

> 不量就按计划挑「稳定函数」，我会挑到一批**因为不含地址引用而稳定**的函数 ——
> **它们恰好是最不像业务逻辑的那种。**

### 下一轮

指令级归一化差分要真做，先按 §1.2 读 `seep-reverse-lab` 与 `rea` 里有没有现成的匹配工具，
**不自己想当然写一个**。
"""


def main():
    for p, marker, text in ((P1, "R726", BLOCKER), (P3, "R726", BLOCKER), (P2, "第 726 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # the taxonomy said class 7 was "never used"; record what using it taught
    body = io.open(EC, encoding="utf-8").read()
    old = "| 7 | **第二版本** | `%LOCALAPPDATA%\\Cybersole\\current\\Cybersole.exe` = **5.18.35.0**，129,306,192 B，md5 `30eef212…` | 可读 | **从未用于本任务** | 只读 |"
    if old in body:
        new = ("| 7 | **第二版本** | `%LOCALAPPDATA%\\Cybersole\\current\\Cybersole.exe` = **5.18.35.0**，129,306,192 B，"
               "md5 `30eef212…` | 可读 | **R726 试过**：字节哈希被重排污染（25.1%，掩码后 29.4%），"
               "**不可用于选稳定函数**；可靠的只有 `+171` 个新增 `.pdata` 条目 | 只读 |")
        io.open(EC, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  EVIDENCE_CLASSES.md: class 7 status updated with the R726 result")
    else:
        print("  EVIDENCE_CLASSES.md: class 7 row MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R726: the version diff cannot select stable witnesses -- byte hashing is dominated by relayout\n\n"
         "R725 planned to pick 'functions identical in both releases' as stable witnesses. Measured:\n\n"
         "  277,094 .pdata entries in 5.18.32, 277,265 in 5.18.35 (+171)\n"
         "  69,460 byte-identical (25.1%)\n"
         "  207,634 only in 32, 207,805 only in 35\n"
         "  1,750 keep the same RVA at the same index (0.6%)\n\n"
         "A 62,976-byte size delta against 75% of functions differing means the image was relaid out.\n"
         "Masking 4-byte words that read as in-image addresses lifts identity only to 29.4%, because the\n"
         "dominant cause is lea [rip+disp32]: after a shift the displacement becomes a different small\n"
         "number, which no address range mask catches. Suppressing those means masking every immediate and\n"
         "displacement, which is instruction-level normalisation -- a disassembler job.\n\n"
         "The two-sided 207k/207.8k counts are independent corroboration: a local edit would make both\n"
         "small, not both 200,000.\n\n"
         "What survives: +171 net new non-leaf functions, which relayout cannot explain. What fails: using\n"
         "hash identity to rank witnesses. Had I not measured, the stable set would have been functions\n"
         "that merely contain no address references -- the least business-logic-like of all."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
