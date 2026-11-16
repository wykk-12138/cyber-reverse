"""R703: retract §124 -- the references existed; I probed the wrong address.

`ida.py str` returns the address of a string literal's CHARACTER data. For a .NET frozen string object the layout is
`[MethodTable:8][length:4][chars...]`, so the code references the OBJECT (chars - 12), and an xref query at the chars
address returns zero. R691 ran five probes and all five inherited that wrong address (or the wrong reference class),
then reported "five independent mechanisms agree: no reference".

Verified now:
    xrefs 0x146E4D160 (object)  -> 1, site 0x140F7739B in sub_140F77350
    xrefs 0x146E4D16C (chars)   -> 0
    xrefs 0x146E4D1B8 (object)  -> 1, site 0x140F7784B in sub_140F777E0
    xrefs 0x146E4D1C4 (chars)   -> 0

So §124's conclusion, and everything built on it, needs correcting. This script appends the retraction to BLOCKERS.md,
fixes the handoff's "don't retry this road" entry, and adds `analysis/xref_both.py` so the next probe tries both
addresses by default.
"""

import io
import subprocess

BLOCKERS = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
HANDOFF = r"D:\projects\cyber-reverse\docs\HANDOFF_BLOCKERS.md"
CLOSURE = r"D:\projects\cyber-reverse\docs\TRAP_ENTRY_CLOSURE.md"
XREF_BOTH = r"D:\projects\cyber-reverse\analysis\xref_both.py"

RETRACTION = """

---

## 134. **撤回 §124**：那两条字符串引用一直存在 —— 我探的是字符地址，代码引用的是对象头

> R703。**第二十五次自纠，也是本 session 影响最大的一次。**

### 一、§124 当时写了什么

> 「那片假数据集在 IDB 里与代码没有任何可见连接」「五次独立探测、五种不同机制，结论一致」
> 「字符串 → xref → 函数这条路由在这个二进制上天然为空」

**这句话被用来支撑三件事**：`CRITERION_B_OPTIONS` 的「路径 D 被阻塞」、`HANDOFF_BLOCKERS` 的「别重走的路」、
`TRAP_ENTRY_CLOSURE` 把 §34/§124 列为「结论型，无需门」。

### 二、实测：引用一直在

```
xrefs 0x146E4D160  (对象头)  -> 1 条: 0x140F7739B  in sub_140F77350   ← Country 守卫
xrefs 0x146E4D16C  (字符区)  -> 0                                     ← R691 探的是这个
xrefs 0x146E4D1B8  (对象头)  -> 1 条: 0x140F7784B  in sub_140F777E0   ← State 守卫
xrefs 0x146E4D1C4  (字符区)  -> 0                                     ← R691 探的是这个
```

**差 12 字节** = `[MethodTable:8][length:4]` 头。.NET 冻结字符串对象是
`[mt][len][chars...]`，**代码 `lea` 的是对象头**；`analysis/ida.py str` 返回的是**字符数据地址**。

### 三、所以"五个探针一致"是假的

五个探针**全都继承了同一个错地址**（或同一类错的引用类型）：

| 探针 | 为什么是 0 |
|---|---|
| `xrefs` 字符地址 | 地址错 12 字节 |
| `.rdata`/`.data` 扫 8 字节**绝对指针** | `lea` 用的是 **4 字节 disp32**，且 disp 在 **`.text`** 里 |
| 区域按页 `XrefsTo` | 那片**假数据表**确实可能无引用，但字符串有 —— 两个问题被混成一个 |
| `find_xref_signatures` 字符地址 | 地址错 |
| `trace_data_flow` backward 字符地址 | 地址错 |

**「多种机制独立验证」这句话本身是错的**：机制不同，但它们**共享同一个输入**。
**独立性看的是误差是否独立，不是工具是否不同。**

### 四、独立复验（不经过任何第三方工具）

从**原始 PE 字节**算：

```
0x140F7739E:  48 8d 15 be 5d ed 05      lea rdx, [rip+0x05ed5dbe]
site + 4 + disp32 = 0x146E4D160        ← 与对象头 VA 逐字节相符
```

反编译 `sub_140F77350`（18 行）也直接印证：

```c
if (!*(_DWORD *)(a2+8) || sub_140F752D0(a2)) return 0;   // 空/归一化后放行
v4 = sub_1412626C0(*(qword_1472C7460+8), &off_146E4D160);  // 查表，用该对象
return sub_141CF6EA0(0, v4, &v5);                         // 格式化错误文案
```

### 五、连带失效的结论

| 位置 | 原说法 | 现状 |
|---|---|---|
| `CRITERION_B_OPTIONS.md` 路径 D | 「反编译拿规则：**阻塞**」 | **已达成**（R702 读出四维规则，本轮复验） |
| `HANDOFF_BLOCKERS.md` §3 | 「字符串 → xref → 函数：已否证」 | **错**，已改 |
| `TRAP_ENTRY_CLOSURE.md` §五 | §34/§124 列「结论型」 | **不再成立**，已标注 |
| `APP_LAYER_BOUNDARY.md` | 七条路线全否 | **其中"字符串→函数"这条要重开** |

**注意**：`§35`（导入 thunk → 调用点 → 反编译）**仍然有效且仍然正确** —— 它是**另一条**路，不是这条的替代。

### 六、根因与durable修法

**根因**：`analysis/ida.py str` 返回字符地址，而调用方默认它是"这个字符串的地址"。
在 .NET AOT 里字符串是**对象**，字符只是它的第三个字段。

**修法**：新增 `analysis/xref_both.py` —— 对任何字符串地址，**同时**试 `addr`、`addr-12`
（并把命中的那个连同所在函数一起打出来）。**让下一个人不需要知道这个 12 字节。**

### 七、仍然 Unknown

- 那片**假数据表**（`0x143600000..0x143800000`）是否真的无引用：**Unknown** ——
  本轮只证明了**字符串**有引用；表的探测仍用错类方法（绝对指针 vs `lea`），要重做。
- `§35` 的 thunk 路线与这条的关系（哪些函数只能用一条）：**Unknown**。
- 还有多少过去的"否证"是同类错误（探错地址/错引用类）：**Unknown** —— 这是本轮最该警惕的。
"""


def main():
    body = io.open(BLOCKERS, encoding="utf-8").read()
    if "## 134." in body:
        print("  blockers: already retracted")
    else:
        io.open(BLOCKERS, "a", encoding="utf-8").write(RETRACTION)
        print("  blockers += §134 retraction")

    body = io.open(HANDOFF, encoding="utf-8").read()
    old = "| 字符串 → xref → 函数 | `§32`、`§34`、`§124` |"
    new = ("| ~~字符串 → xref → 函数~~ **（R703 已撤回，这条路是通的）** | ~~`§32`、`§34`、`§124`~~ "
           "—— 见 `§134`：**引用一直在，我探的是字符地址，代码 `lea` 的是对象头（差 12 字节）**。"
           "用 `analysis/xref_both.py` 同时试两个地址 |")
    if new in body:
        print("  handoff: already corrected")
    elif old in body:
        io.open(HANDOFF, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  handoff: corrected the retracted road")
    else:
        print("  handoff: MISS")

    body = io.open(CLOSURE, encoding="utf-8").read()
    marker = "R703 撤回"
    if marker in body:
        print("  closure: already noted")
    else:
        note = ("\n\n---\n\n## 附：R703 撤回\n\n"
                "本文件 §五 把 `§34`/`§124` 列为「结论型，无需门」。**R703 撤回了那个结论**：\n"
                "字符串引用一直存在，当时五个探针共享了同一个错地址（字符区 vs 对象头，差 12 字节）。\n"
                "详见 `BLOCKERS.md §134`。**「多个独立探针一致」在它们共享输入时不构成证据。**\n")
        io.open(CLOSURE, "a", encoding="utf-8").write(note)
        print("  closure: noted the retraction")

    print()
    print("  next: write analysis/xref_both.py")
    print("  target:", XREF_BOTH)

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R703: retract BLOCKERS 124 -- the string references were always there\n\n"
         "ida.py str returns the address of a literal's CHARACTER data; for a .NET frozen string the\n"
         "layout is [MethodTable:8][length:4][chars], so code leas the OBJECT (chars-12) and an xref\n"
         "query at chars returns 0. R691 ran five probes that all inherited that wrong address, then\n"
         "reported 'five independent mechanisms agree: no reference'.\n\n"
         "  xrefs 0x146E4D160 (object) -> 1, site 0x140F7739B in sub_140F77350\n"
         "  xrefs 0x146E4D16C (chars)  -> 0\n\n"
         "Verified independently from raw PE bytes: lea rdx,[rip+0x05ed5dbe] at 0x140F7739E computes\n"
         "exactly 0x146E4D160. Consequences retracted: 'path D is blocked', the handoff's 'do not retry\n"
         "this road', and the trap-closure entry that called 34/124 conclusion-type."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
