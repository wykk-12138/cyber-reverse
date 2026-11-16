"""Record R723: the third bucket, and why it is looser than a citation."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 152. 第三桶：**130 条（8.4%）**测试触到池中文案；仍有 **1004 条（64.6%）**无来源

> R723。新增 `analysis/locale_derived_tests.py`；`docs/TEST_PROVENANCE.md` 追加第三节。

### 一、先纠正一个默认

R722 把「没有地址引用」当作「没有二进制来源」。**那是错的**：

> 一条断言「表头等于 `Unknown country`」——那句话在原版字符串池里**逐字存在**。
> 它来自镜像，不是来自实现。

**所以 73% 那个池子里混着两种东西**：真·实现复述，和**文案溯源**。

### 二、分层结果

```
测试方法总数       1553
  binary (cited)     419  (27.0%)   R722 那两档（83 直接 + 336 类级继承）
  locale-derived     130  ( 8.4%)   触到池中文案
  unaccounted       1004  (64.6%)   两者都没有
```

**有来源的从 27.0% 升到 35.4%**，仍有 **64.6%** 无来源。

### 三、检测器是松的，这必须写在文档里

判据：方法体里出现一段 ≥8 字符、且**逐字**出现在 `Cybersole.Locales.en.json` 的字符串 → 记 locale-derived。

**所以 `TheHeadersActuallySort` 会被算进来**：它确实用了池中的表头文字，**但它断言的是排序，不是文案**。

**所以 locale-derived 的含义是「这条测试触到了池中文字」，不是「整条期望来自池」。**
它比 cited 弱、比 unaccounted 强，**只能这么用**。已写进生成的文档。

### 四、三条证据的强弱排序（这张表现有的全部价值）

| 档 | 条数 | 证明什么 | 不能证明什么 |
|---|---|---|---|
| `cited` | 83 | 断言本身引了原版地址 | 引用不等于读对 |
| `cited`（含类级） | 419 | 类注释覆盖了全类 | 方法本身未必依赖它 |
| `locale-derived` | 130 | 期望值里有池中文字 | 行为是否等同原版 |
| `unaccounted` | 1004 | — | 可能只是复述实现 |

**加起来 549 / 1553 有某种来源（35.4%）。**

### 五、仍然 Unknown

- 1004 条里有多少**间接**依赖反编译（被测函数是照反编译写的）：**Unknown** —— **所以 35.4% 是下界**。
- 130 条里有多少是"整条期望来自池"而非"顺带用到池中文字"：**Unknown**（需逐条看）。
- 549 条里有多少**真的读对了反编译**：**Unknown** —— 这条从 R718 起就记着，没有对拍手段。

### 六、这一轮的判断

> 上一轮我把 73% 说成"没有来源"。**其中 130 条是有来源的，只是来源不是地址而是文字。**

**分桶的价值在这一轮第二次显现**：第一次是把 44 条拆成三种（R709），这次是把"无来源"拆成"无地址来源"和"无来源"。
"""

VERDICT = """

---

## 第 723 轮：第三桶 —— 130 条触到池中文案

### 纠正一个默认

R722 把「没有地址引用」当作「没有二进制来源」。**错**：一条断言「表头等于 `Unknown country`」，
**那句话在池里逐字存在**，它来自镜像不是来自实现。

### 分层

```
1553 个测试方法
  binary (cited)   419  (27.0%)
  locale-derived   130  ( 8.4%)   触到池中文案
  unaccounted     1004  (64.6%)
```

**有来源 35.4%**，仍 **64.6% 无来源**。

### 检测器是松的

≥8 字符、逐字出现在 locale 目录 → 算。**所以 `TheHeadersActuallySort` 会被算进来** ——
它确实用了池中表头，**但断言的是排序**。

> **locale-derived = 「这条测试触到了池中文字」，不是「整条期望来自池」。**

### 四条档次的强弱

| 档 | 条数 | 证明 | 不能证明 |
|---|---|---|---|
| cited | 83 | 引了原版地址 | 引用≠读对 |
| cited 含类级 | 419 | 类注释覆盖全类 | 方法未必依赖 |
| locale-derived | 130 | 期望含池中文字 | 行为是否等同 |
| unaccounted | 1004 | — | 可能只是复述实现 |

### 一句话

> 上一轮我把 73% 说成「没有来源」。**其中 130 条有来源，只是来源不是地址而是文字。**

> **分桶的价值第二次显现：R709 把 44 条拆成三种，这次把「无来源」拆成「无地址来源」和「无来源」。**

### 下一轮

1004 条是最后一个大池子。挑**一个文件**逐条看它们的期望值从哪来 —— 三种可能（文案/UX/照实现写），
**修的成本完全不同**，而只知道比例没用。
"""


def main():
    for p, marker, text in ((P1, "R723", BLOCKER), (P3, "R723", BLOCKER), (P2, "第 723 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R723: 130 more tests are locale-derived, so 35.4% have some binary source and 64.6% have none\n\n"
         "R722 treated 'no address marker' as 'no binary source'. That is wrong: a test asserting a caption\n"
         "equals 'Unknown country' is derived from the image's string pool, because the text is there\n"
         "verbatim and did not come from the implementation.\n\n"
         "  1553 test methods\n"
         "    binary (cited)   419 (27.0%)   the R722 two tiers\n"
         "    locale-derived   130 ( 8.4%)   the body touches pool text\n"
         "    unaccounted     1004 (64.6%)\n\n"
         "The detector is deliberately loose -- any 8+ character literal that appears verbatim in the locale\n"
         "catalogue counts -- so TheHeadersActuallySort is included even though it asserts sorting rather\n"
         "than wording. locale-derived therefore means 'this test touches pool text', not 'this expectation\n"
         "comes from the pool', and the generated document says so.\n\n"
         "35.4% is still a lower bound: 1004 tests may depend on decompilation without saying so."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
