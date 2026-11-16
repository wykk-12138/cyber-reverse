"""Record R722: test provenance -- 5.3% direct, 27.0% including class-level inheritance."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 151. 1639 条测试里，**5.3% 的断言直接引了二进制**；含类级继承 27.0%

> R722。新增 `analysis/test_provenance.py`；生成 `docs/TEST_PROVENANCE.md`。

### 一、为什么要量这个

C7c（每个函数功能相等）是 `unknown`。R719–R721 证明「从原版挑见证函数」卡在元数据归属上。
那么 C7c 实际能拿出的证据是**另一个量**：**有多少条断言陈述的是二进制说过的事**，而不是把实现复述一遍。

**1649 条全绿不等于 1649 条证据。**

### 二、判据（先定，保守）

一条测试算 `binary-sourced`，当且仅当方法体或紧邻文档注释里出现其一：

```
0x14xxxxxx 或 sub_14XXXXXX   原版镜像地址/反编译函数名
decompil                     反编译 / Hex-Rays / 伪代码
descriptor                   编译期 XAML 描述符表
the image                    关于原版二进制的主张
```

**其余一律记 `implementation-derived`**，包含从文案或 UI 设计推出的测试 —— 那些也不是从二进制推的。

### 三、结果（方法数，不是用例数）

```
测试方法总数     1553   （分布在 329 个文件）
direct           83    (5.3%)   方法体/自身注释里有引用
inherited        419   (27.0%)  含"类级文档声明对该类全体的覆盖"
neither          1134  (73.0%)
```

**口径差别必须说清**：1553 是**方法数**；METRICS 里的 1639 是**用例数**（`[Theory]` 会展开）。
两个数不是一回事，**不能互相印证**。

### 四、我在这轮里修了三个自己的 bug，每个都让数字变

| # | bug | 症状 | 修法 | 数字 |
|---|---|---|---|---|
| 1 | 地址正则只认 `0x14XXXXXX` | R718 那 15 条探针用的是 `sub_141CFA390`，**一条都没数到** | 加 `sub_14XXXXXX` | 50 → 50 |
| 2 | 向上找 `///` 时遇到 `[InlineData]` 就停 | `[Theory]` 的文档块被属性行隔开，**整块丢失** | 跳过属性行与空行 | 50 → 83 |
| 3 | 只看方法级，不看类级 | R718 的地址写在**类注释**里，7 个方法全判 False | 类级声明继承给该类方法 | 83 → 419 |

**第 1 个最值得记**：审计脚本漏掉了它本来要审计的那批证据，**而且漏得毫无提示**。
如果我只报 50，就等于说"我自己上一轮做的 15 条不算证据"。

### 五、两个数都报，不合并

**83（5.3%）** = 断言本身带引用，证据强。
**419（27.0%）** = 加上「类注释说了、方法没细说」的那 336 条，证据弱一档。
**1134（73.0%）** = 两者都没有。

合并成一个数会掩盖"强弱之分"，而这张表存在的理由就是分清强弱。

### 六、仍然 Unknown

- `inherited` 那 336 条里，有多少**真的**依赖类级声明里的地址：**Unknown**（未逐条核）。
- 73% 里有多少**间接**依赖反编译（例如被测函数是照反编译写的）：**Unknown** ——
  **所以 83 是下界，不是真值**。
- 方法数 1553 与用例数 1639 的差怎么分布在文件间：**Unknown**（未展开 `[Theory]`）。

### 七、这一轮的判断

> **绿色是"没坏"，不是"对"。** 一条测试断言"实现输出等于实现输出"，它永远是绿的，也永远不证明任何事。

R722 量的是**这个区别**，而它只有 5.3%。
"""

VERDICT = """

---

## 第 722 轮：1639 条测试，5.3% 的断言直接引了二进制

### 为什么要量

C7c 需要"二进制说过的行为"。**1649 条全绿不等于 1649 条证据。**

### 判据

方法体或紧邻注释里有 `0x14XXXXXX`/`sub_14XXXXXX`、`decompil`、`descriptor`、`the image` 之一。

### 结果（方法数，非用例数）

```
1553 个测试方法
  direct      83   ( 5.3%)   自身带引用
  inherited  419   (27.0%)   含类级注释的覆盖
  neither   1134   (73.0%)
```

1553 是**方法数**，METRICS 的 1639 是**用例数**（Theory 展开）—— **两个数不能互相印证**。

### 我这轮修了自己三个 bug，每个都改数字

| bug | 症状 | 修法 | 数字 |
|---|---|---|---|
| 只认 `0x14` | R718 探针写的是 `sub_141…`，**一条没数到** | 加 `sub_14` | 50→50 |
| 遇 `[InlineData]` 就停 | Theory 的文档块整块丢失 | 跳过属性行 | 50→83 |
| 只看方法级 | R718 地址写在类注释里，7 条全 False | 类级继承 | 83→419 |

**第 1 个最值得记**：审计脚本漏掉了它本来要审计的证据，**且毫无提示**。

### 两个数都报

**83 强 / 419 弱（含 336 条只有类级声明）/ 1134 无。** 合并成一个数会掩盖强弱之分，
而这张表存在的理由就是分清强弱。

### 一句话

> **绿色是「没坏」，不是「对」。** 一条测试断言「实现输出等于实现输出」，它永远绿，也永远不证明任何事。

> R722 量的是这个区别——**它只有 5.3%。**

### 下一轮

**73% 是最大的池子。** 挑几个文件逐条看：它们的期望值到底是"从文案抄的"、"从 UX 约定推的"，
还是"照着实现写的"——**三种都算 implementation-derived，但修的成本完全不同**。
"""


def main():
    for p, marker, text in ((P1, "R722", BLOCKER), (P3, "R722", BLOCKER), (P2, "第 722 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R722: 5.3% of test methods cite the binary directly; 27.0% counting class-level statements\n\n"
         "C7c needs assertions that state what the binary says, and 1639 green cases are not 1639 pieces\n"
         "of evidence. Marker-based audit over 1553 test methods in 329 files:\n\n"
         "  direct      83   (5.3%)   the assertion or its own doc cites an address / decompilation\n"
         "  inherited  419   (27.0%)  also counts a class-level statement covering the class\n"
         "  neither   1134   (73.0%)\n\n"
         "1553 is methods; METRICS' 1639 is cases, because Theories expand -- the two do not corroborate\n"
         "each other and both numbers are needed.\n\n"
         "Three bugs of my own fixed during the round, each of which moved the number: the address regex\n"
         "did not accept sub_14XXXXXX, so R718's own fifteen probes were invisible; the doc-block walk\n"
         "stopped at the first [InlineData], losing every Theory's comment; and method-only scope missed\n"
         "provenance stated once per class. The first is the one to remember -- the audit silently\n"
         "excluded the evidence it was written to find."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
