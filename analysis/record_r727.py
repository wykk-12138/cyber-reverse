"""Record R727: the §1.2 check on both reference repositories, and the viable route it left."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 156. §1.2 检查：两个参考仓库都没有「功能等价」的答案，但留下了可行路线

> R727。读 `seep-reverse-lab/MANUAL/POC-VALIDATION.md`（AGENTS.md 标为"待读"）、
> `rea/docs/native-function-matching.md`；实测 35 的字符串可抽。

### 一、seep-reverse-lab：**不覆盖**

`MANUAL/POC-VALIDATION.md`（171 行）定义的是 **Frida 脚本 / Smali 补丁 / 代理 DLL 的自动化验证 SOP**：
三阶段闭环（静态自检 → 沙箱执行 → 报错自愈），配一张「常见报错 → 自愈映射表」。

**它是"我改的这个补丁能不能跑起来"的验证，不是"我的复刻件和原版功能是否相同"的验证。**
两件事：一个的失败信号是**崩溃**，另一个的失败信号是**行为不同但没有崩溃**。

**所以最高优先级的参考里没有 C7c 的答案。** 这构成了去读 `rea` 的理由，也写清了缺什么。

### 二、rea：工具更强，但字节层撞同一堵墙

`docs/native-function-matching.md`（10,426 B）说得很直接：

> A byte match requires every body byte, equal total size, equal ordered range lengths,
> a unique SHA-256 fingerprint and the same known architecture.
> **Extents are never guessed from the next entry, and relocations are not normalized.**

**`relocations are not normalized`** —— **这正是 R726 撞的那堵墙。** REA 的字节层会给出同样的 25%。

名字层也不行：它「先配唯一精确名字」，而 **NativeAOT 只有 3.13% 的函数有名字**，覆盖率接近零。

**但 REA 还有第三层：`compatible CFG/call/string fingerprints propose unresolved groups`。**
**CFG / 调用 / 字符串指纹是重排不变的东西** —— 这才是它比我那 30 行哈希强的地方。

### 三、用它的成本

`match_native_functions` 要两个 `list_procedures` **Evidence**，即**两个 129 MB 的 NativeAOT 都要开进 provider**。
`docs/providers/ghidra-nativeaot.md` 存在，说明支持；但**一次开两个 129 MB 的镜像不是一轮能做完的事**。

**判断**：不在本轮盲开。**先走一个便宜的、同样重排不变的近似**（见下），如果它够用，就不必付那个成本。

### 四、便宜的近似：**字符串引用签名**（本轮已验证可行性）

思路：一个函数引用了哪些**字符串内容**，是重排不变的（内容不变、地址变了不影响）。

**可行性第一步已测**：35 的字符串能**纯字节**抽出，不需要 IDA：

```
5.18.35  ASCII runs >=6 : 313,119
         UTF-16 runs>=6 :  76,529
         含 "Cybersole." :   1,383
```

与 32 的 324,895 条字符串池同一量级。**所以两侧都能建「地址 → 字符串内容」表。**

### 五、下一轮的具体做法

1. 两侧各自：`地址 → 字符串内容` 表（32 已有 `pe_strings.txt`；35 用同法抽）
2. 两侧各自：`disp32_scan_any.scan` 扫 `.text`，命中点 → 所属函数（`.pdata` 已会解析）
3. 每个函数得到 **引用字符串内容集合**（排序去重）
4. 两侧比这个集合 → **重排不变的相同/不同**

**这不能证明行为相同**（引用同一批字符串的两个函数仍可能逻辑不同），**但它能可靠地把"因为重排而不同"剔掉**，
这正是 R726 缺的那一步。

### 六、仍然 Unknown

- rea 的 CFG/字符串指纹层在这两个镜像上能配到多少：**Unknown**（未跑，成本高）。
- 字符串签名相同的函数里有多少逻辑真相同：**Unknown**（签名是必要条件不是充分条件）。
- `ghidra-nativeaot.md` 描述的 provider 是否支持 129 MB 镜像：**Unknown**（未读该文档，未实测）。
"""

VERDICT = """

---

## 第 727 轮：§1.2 检查 —— 两个参考仓库都没有答案，但留下了路线

### seep-reverse-lab：不覆盖

`POC-VALIDATION.md` 是 **Frida/Smali 补丁的动态验证 SOP**（三阶段闭环 + 报错自愈表）。
**它验证"补丁能不能跑"，不验证"复刻件和原版行为是否相同"。** 一个的失败信号是崩溃，另一个是**行为不同但没崩**。

### rea：工具更强，字节层撞同一堵墙

`native-function-matching.md` 原文：

> **relocations are not normalized**

**这正是 R726 撞的墙。** REA 的字节层会给同样的 25%。名字层也不行（NativeAOT 只有 3.13% 有名字）。

**但它有第三层：CFG/调用/字符串指纹 —— 那是重排不变的。** 这是它比我那 30 行强的地方。
成本：两个 129 MB 镜像都要开进 provider，**不是一轮的事**。

### 便宜的近似（本轮已验证可行）

**字符串引用签名**：一个函数引用了哪些字符串内容，重排不变。

```
5.18.35  ASCII runs 313,119 · UTF-16 76,529 · 含 "Cybersole." 1,383
```

**不用 IDA，纯字节就能抽。** 两侧都能建「地址 → 内容」表，再用已写好的 `disp32_scan_any` 命中 → `.pdata` 归属。

### 一句话

> R726 我撞墙后想自己写归一化差分。**按 §1.2 先查，发现两个仓库都不管这件事** ——
> 但它们让我看清墙在哪：**字节会动，字符串内容不会。**

> **不证明行为相同，但能把「因为重排而不同」剔掉** —— 这正是 R726 缺的那一步。

### 下一轮

建两侧的「地址 → 字符串内容」表，算每函数的引用集合，比集合。
"""


def main():
    for p, marker, text in ((P1, "R727", BLOCKER), (P3, "R727", BLOCKER), (P2, "第 727 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # mark POC-VALIDATION as read in AGENTS.md's table
    ag = r"D:\projects\cyber-reverse\AGENTS.md"
    body = io.open(ag, encoding="utf-8").read()
    old = "| `seep-reverse-lab/MANUAL/POC-VALIDATION.md` | 验证口径（待读） | 待采用 |"
    if old in body:
        new = ("| `seep-reverse-lab/MANUAL/POC-VALIDATION.md` | **R727 已读**：Frida/Smali 补丁的三阶段动态验证 SOP，"
               "**不覆盖复刻件的功能等价** | 已读，不适用 |")
        io.open(ag, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  AGENTS.md: POC-VALIDATION row updated")
    else:
        print("  AGENTS.md: row MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R727: neither reference repo answers functional equivalence, but the check found the route\n\n"
         "seep-reverse-lab's POC-VALIDATION.md (marked 'to read' since it was catalogued) is a three-stage\n"
         "dynamic validation SOP for Frida scripts and Smali patches. Its failure signal is a crash; C7c's is\n"
         "different behaviour without one. It does not cover reimplementation equivalence.\n\n"
         "rea's native-function-matching.md states plainly that 'relocations are not normalized', which is\n"
         "the wall R726 hit: its byte tier would return the same 25%. Its name tier is near-useless here\n"
         "because only 3.13% of the functions carry names. What it has that mine lacks is the third tier --\n"
         "compatible CFG, call and string fingerprints -- and those are relocation invariant. Using it means\n"
         "opening two 129 MB NativeAOT images in a provider, which is not a one-round cost, so this round\n"
         "verifies a cheaper approximation instead.\n\n"
         "String-reference signatures: which string contents a function references is invariant under\n"
         "relayout. Verified that 5.18.35's strings extract by pure bytes without IDA -- 313,119 ASCII runs,\n"
         "76,529 UTF-16, 1,383 carrying the app's namespace, against 324,895 in the target's pool. Both sides\n"
         "can therefore be mapped address-to-content, scanned with the existing disp32_scan_any, and\n"
         "attributed to functions through .pdata."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
