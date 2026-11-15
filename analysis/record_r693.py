"""Record R693: the artifact is rebuilt; C10's 21/819 was measured against a doubly-stale pair."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
CLAIMS = r"D:\projects\cyber-reverse\docs\PARITY_CLAIMS.md"

BLOCKER = """

---

## 126. 产物已用当前源码重建；而 **C10 的 21/819 是在一对双重过期的输入上算出来的**

> R693。重建 `.publish-aot`；起第二个 IDA 实例（复刻件，13338）在后台分析。

### 一、先查输入时效（判据先定）

> **C10 重算必须基于「当前源码构建的产物」+「从该产物导出的符号表」，任一过期结果即无效。**

查出来**两样都过期**：

| 输入 | 时间 | 说明 |
|---|---|---|
| `.publish-aot\\Cybersole.Ui.exe` | **11-15 14:39** | 旧产物 |
| `analysis/replica_funcs.txt`（符号表） | **11-14 18:03** | **比产物还旧 20 小时** |
| 最新源码 `.cs` | **11-15 21:47** | 比产物新 |

**所以符号表比产物旧、产物比源码旧 —— 三层错位。**

### 二、结论：C10 的 21/819 不是对"当前产物"的测量

这比 R692 里写的「R433 时的一次性测量」更进一步 ——
**它不是"旧但当时有效"，而是"符号表与产物本身就对不上"**：
`replica_funcs.txt` 是 11-14 从当时的产物导出的，而 11-15 的产物已经变过。

**所以 C10 的 21/819 应记为：在一次已失效的输入组合上得到的数，不能代表任何一版产物。**

### 三、本轮做完的

**产物已重建**（当前源码，`mswin` Release + AOT）：

```
exit=0    artifact: 55,080,448 B  21:49:47
free: 14.57 GB -> 13.93 GB
```

**判据 (c) 的资源面在**新产物**上复算通过**：

```
原版: 12 leaves (129,243,216 bytes)
复刻件: 12 leaves (55,080,448 bytes)     ← 新产物
```

12 ↔ 12 与 R609 一致，且这次用的是当前源码的产物。

### 四、C10 的重算已启动，但需要第二次完整分析

`func_compare.py` 需要**两个活着的 IDA 实例**（原版 13337、复刻件 13338，带 PDB）。
第二个实例已启动：

```
启动 ida.exe .publish-aot\\Cybersole.Ui.exe
模态框 1：Database ...i64 already exists -> **Overwrite**（旧库对应旧产物，按判据不能用 Load existing）
模态框 2：Load a new file（PE 加载器已选，Analysis 已启用）-> OK
状态：Please wait...  ws=718 MB（自动分析中）
```

**这一步是项目里最贵的一次分析**（55 MB AOT、约 18.7 万函数），本轮让它后台跑完。

### 五、仍然 Unknown

- C10 的**新值**：**Unknown**（等 13338 分析完 + 重导符号表 + 跑 coverage）。
- 新产物与旧产物的差异：**Unknown**（未做产物级 diff）。
- C6 里 187,328 与 186,732 两个数哪个对应哪版产物：**Unknown**。
"""

VERDICT_TEXT = """

---

## 第 693 轮：产物重建；C10 的 21/819 是在**双重过期**的输入上算的

### 一、判据先定

> C10 重算必须基于「当前源码构建的产物」+「从该产物导出的符号表」，任一过期即无效。

查出**两样都过期**：

```
产物         11-15 14:39
符号表       11-14 18:03   ← 比产物还旧 20 小时
最新源码     11-15 21:47   ← 比产物新
```

**三层错位。**

### 二、所以 C10 的 21/819 要改记

不是"旧但当时有效"，而是**符号表与产物本身就对不上** ——
`replica_funcs.txt` 是 11-14 从当时的产物导出的，11-15 的产物已经变过。

**结论：21/819 是在一次已失效的输入组合上得到的数，不代表任何一版产物。**

### 三、本轮做完的

**产物重建**：`exit=0`，**55,080,448 B @ 21:49:47**（当前源码）。

**判据 (c) 在新产物上复算**：原版 **12** leaves ↔ 复刻件 **12** leaves —— 与 R609 一致，且这次用的是当前源码的产物。

### 四、C10 重算已启动（项目里最贵的一步）

`func_compare.py` 要两个活的 IDA 实例。第二个已起：

```
Overwrite（旧库对应旧产物，按判据不能用 Load existing）
-> Load a new file，PE 加载器 + Analysis 已选 -> OK
-> Please wait...  ws=718 MB
```

### 五、一句话

> 这一轮没算出新数，但发现旧数**连"当时的有效测量"都算不上**。

> **一个数字过期，和这个数字从来没对过，是两种不同的事。
> 前者只需要更新；后者需要先把表里那一行降级，否则它会以"旧值"的身份继续被引用。**

### 六、下一轮

等 13338 分析完 → `python analysis/func_compare.py --export-only` 重导符号表 → `python tools/aot_member_coverage.py` 得 C10 新值。
判据先定：新值必须能对上「符号表 mtime > 产物 mtime」这一条，否则不写进表。
"""


def main():
    for p, marker, text in ((P1, "R693", BLOCKER), (P3, "R693", BLOCKER), (P2, "第 693 轮", VERDICT_TEXT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # downgrade C10's line in the claim table
    body = io.open(CLAIMS, encoding="utf-8").read()
    old = '`python tools\\aot_member_coverage.py` → 21/819 = 2.6%（**R433 时的一次性测量，未随度量重算**；与 `func_compare` 同规则同数）'
    new = ('`python tools\\aot_member_coverage.py` → 21/819 = 2.6% —— '
           '**R693 降级：这个数不算任何一版产物的有效测量**。它的符号表（`analysis/replica_funcs.txt`，11-14 18:03）'
           '比产物（11-15 14:39）还旧 20 小时，而产物又旧于源码（11-15 21:47）。'
           '重算中：产物已重建，第二个 IDA 实例（13338）分析中；新值出来前本行按 Unknown 读')
    if new in body:
        print("  claims: C10 already downgraded")
    elif old in body:
        io.open(CLAIMS, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  claims: C10 downgraded to Unknown")
    else:
        print("  claims: C10 MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R693: rebuild the AOT artifact; C10's 21/819 was measured on doubly-stale inputs\n\n"
         "The symbol export (11-14 18:03) was 20 hours older than the artifact (11-15 14:39), which\n"
         "was itself older than the source (11-15 21:47). So 21/819 is not a valid measurement of any\n"
         "version of the product, not merely an old one -- C10 is downgraded to Unknown until the\n"
         "recompute lands. Artifact rebuilt from current source: 55,080,448 B.\n"
         "Resource face recomputed on the new artifact: 12 leaves <-> 12 leaves."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True,
    )
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
