"""Record R1071: decompilation works, and it shows what decompilation cannot do here."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 反编译通了 —— 而它证明了**反编译不足以给出语义**（R1071）

**R1070 把 IDA 拉回来了，那是几轮以来第一次真正打开「反编译」这条主参照路径。
而这一轮做的第一件事就是反编译，而结果同时是**成功**和**一个边界**。**

### ① 而「最大的函数」这个排序，第一次试就错了

```
.pdata 直接给出 RUNTIME_FUNCTION（begin/end/unwind 三个 dword）⇒ 大小不用 IDA 就能算
最大 5 个：687,318 · 527,392 · 227,186 · 83,620 · 70,719 字节
decompile 0x14117c4e0 → **Decompilation failed**
```

**→ 687 KB 不是「一个函数」**：那是多个函数压在一个 `RUNTIME_FUNCTION` 下，或一个跳转表区域。
→ 而 `.pdata` 有 **277,094** 条，IDA 分析出 **321,244** 个函数 —— **差 44,150 ⇒ 两者不是同一份清单。**
→ 所以「最大」被巨型 blob 污染。收到 **4k–30k** 区间：**669 个**，且第一个能反编译。**

**→ 而那 277,094 与 R1066 独立算出的函数数**完全一致** —— 那是一次干净的交叉验证。**

### ② 而成功反编译的那个函数，给出了本轮最重要的观察

```
sub_14067E260(__int64 a1, __int64 a2)     29,867 字节
伪代码前 56 行：__int64 v4; _QWORD *v5; __int64 v6; … v54;
```

**→ 它有 **54+ 个局部变量**，全是 `__int64` / `_QWORD *`。
→ 而**没有一个是带类型的**，没有一个字段名。**

**→ 所以：反编译**给得出控制流**，**给不出字段名与类型**。**

### ③ 而这不是我做错，是产物本身

| 层 | 反编译能给 | 反编译给不了 |
|---|---|---|
| 控制流 | ✓ 分支、循环、调用 | — |
| 调用关系 | ✓ 谁调谁（`xrefs` 可用） | 间接调用目标 |
| **数据语义** | — | **字段名、类型、枚举取值** |
| **协议** | 部分（字符串常量） | 帧结构、签名字段 |

**→ 因为 NativeAOT 剥离了元数据，而**类型信息不在代码里**。
→ 恢复它需要**从数据流反推类型**（R1045 说的那件工程），而那与本轮做的**不是同一件事**。**

### ④ 所以「反编译是主参照」这句话要补一半

**AGENTS §0 写着「反编译优先（主参照）」。而对这个产物，正确的读法是：**
**→ 反编译是**控制流**的主参照；
**→ 而**语义**的主参照是 `analysis/pe_strings.txt` 与反射元数据（那正是 R1068 用来数类型的）。**

**→ 两者不能互相替代，而我一直偏在前者之外（几轮全是元数据），这一轮又偏回后者。
→ 正确的位置是**两者并用**：元数据给名字与类型，反编译给顺序与分支。**

### ⑤ 而下一步因此是明确的

**669 个 4k–30k 的函数是可反编译的集合。而那 669 个里，业务 core（flow 步骤、风控 solver）
应该是最大的那些 —— 所以「按大小取前 N 个，逐个反编译，把控制流与元数据里的名字对上」是 (a)/(f) 的下一条路。**

**→ 而那需要一件事：把函数地址映射到类型/方法名。而那是 NativeAOT 的 `ReflectionMethod` 表 —— 尚未取证。**

### ⑥ 数字

| 度量 | R1070 | **R1071** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,258 / 277,094 | **同（`.pdata` 独立算得 277,094，一致）** |
| **`.pdata` 条目** | 未读 | **277,094** |
| **IDA 分析函数** | 321,244 | **321,244（差 44,150）** |
| **4k–30k 可反编译段** | — | **669 个** |
| **最大可反编译函数** | — | **29,867 字节** |
| **反编译是否可用** | 未试 | **可用（但 687 KB blob 会失败）** |
| **反编译给出了什么** | — | **控制流，不是语义** |

### 教训

> **「主参照」不是「唯一的参照」。反编译能给出**顺序与分支**，而给不出**字段名**，
> 因为那些不在代码里而在被剥离的元数据里。**
> **→ 而这一轮的错法也值得记：我按「最大」排，而前五全是**不是函数的东西**。
> → 而那不是工具错 —— `.pdata` 的条目**本来就不等于函数**（277,094 vs 321,244）。
> → 两个数字都真，而我把一个当成了另一个的清单。**
"""

if "反编译通了 —— 而它证明了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1071 —— **反编译通了；而它证明了反编译不足以给出语义**

### 「最大函数」这个排序第一次就错了

```
.pdata 三 dword = begin/end/unwind ⇒ 大小不用 IDA 算
最大：687,318 · 527,392 · 227,186 …  → decompile 687KB → **failed**
```

**687 KB 不是「一个函数」**（多函数合并 / 跳转表区域）。
**而 `.pdata` 277,094 条 vs IDA 321,244 个函数 —— 差 44,150 ⇒ 两者不是同一份清单。**
收到 4k–30k：**669 个**，第一个能反编译。

**而 277,094 与 R1066 独立算出的函数数**完全一致** —— 一次干净的交叉验证。**

### 而成功反编译的那个函数给出最重要的观察

```
sub_14067E260(__int64 a1, __int64 a2)   29,867 字节
前 56 行：__int64 v4; _QWORD *v5; … v54;      ← **54+ 个局部变量，无一个带类型或字段名**
```

**⇒ 反编译**给得出控制流**，**给不出字段名与类型**（NativeAOT 剥离了元数据）。**

### 所以「反编译是主参照」要补一半

| 层 | 能给 | 给不了 |
|---|---|---|
| 控制流 | ✓ 分支/循环/调用 | — |
| **数据语义** | — | **字段名、类型、枚举取值** |
| **协议** | 部分（字符串常量） | 帧结构、签名字段 |

**⇒ 反编译是**控制流**的主参照；**语义**的主参照是字符串池与反射元数据（R1068 用的那个）——
两者不能互相替代。**

### 下一步

669 个 4k–30k 函数是可反编译集合；业务 core 应是其中最大的那些。
**缺一件东西：把函数地址映射到类型/方法名 —— NativeAOT 的 `ReflectionMethod` 表，尚未取证。**

### 数字

| 度量 | R1070 | **R1071** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同（独立算得一致）** |
| `.pdata` 条目 / IDA 函数 | — / 321,244 | **277,094 / 321,244（差 44,150）** |
| 4k–30k 可反编译 | — | **669 个** |
| 最大可反编译函数 | — | **29,867 字节** |
| 反编译给出了什么 | — | **控制流，不是语义** |

**纪律**：「主参照」不是「唯一参照」；而两个数字都真，不等于一个是另一个的清单。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1071", NOTE)
append(RBLOCK, "R1071", "\n---\n\n## 495. **反编译通了；而它不足以给出语义**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1071: decompilation works, and shows what it cannot supply here\n\n"
     "IDA came back last round, which reopened the route the project calls its main reference. The first thing done\n"
     " with it was to decompile, and the result is both a success and a boundary.\n\n"
     "The first attempt was wrong on the ordering. A RUNTIME_FUNCTION in .pdata carries begin and end, so the size of\n"
     " every function is computable without any analysis at all; sorting by it put a 687-kilobyte entry on top, and\n"
     " Hex-Rays refused it. That entry is not a function -- several are folded under one record, or it is a jump-table\n"
     " region -- and the counts say so independently: .pdata holds 277,094 records where IDA analyses 321,244\n"
     " functions. Two true numbers, and I had treated one as the inventory of the other. Restricting to four to thirty\n"
     " kilobytes leaves 669 entries and the largest of those decompiles.\n\n"
     "That 277,094 also matches the figure R1066 derived by dividing .pdata by twelve from a different direction, which\n"
     " is a clean cross-check on a number that has now been used for several rounds.\n\n"
     "The decompiled function is 29,867 bytes and declares more than fifty locals, every one of them a plain __int64 or\n"
     "_QWORD pointer. There is no type and no field name anywhere in it. So decompilation yields control flow --\n"
     " branches, loops, calls -- and does not yield data semantics, because NativeAOT stripped the metadata and the\n"
     " types are not in the code. Recovering them means inferring from data flow, which is a different undertaking from\n"
     " this one.\n\n"
     "That corrects how the instruction should be read. Decompilation is the main reference for control flow;\n"
     " the string pool and the reflection metadata are the main reference for meaning, and R1068 leaned on those to\n"
     " count types. Neither substitutes for the other, and I have been on one side or the other for several rounds\n"
     " rather than using both.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, count unchanged at 174,258 against 277,094,\n"
     " 277,094 .pdata records against 321,244 analysed functions, 669 entries in the decompilable range, a largest\n"
     " decompilable function of 29,867 bytes, and fifty untyped locals standing for everything the code no longer\n"
     " says.\n\n"
     "Unknown: which address corresponds to which type and method, which is the NativeAOT reflection-method table and\n"
     " has not been examined yet.\n\n"
     "The lesson is that no single reference is the reference, and that two numbers being true does not make one of\n"
     " them the other's list."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
