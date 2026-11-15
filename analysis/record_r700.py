"""Record R700, the final audit, and commit. Written as a file to avoid nested-quote damage."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 133. 完成判据终审（R700）：(a)(b) **未满足**，(c)(d)(e) 满足 —— 目标未达成

> R700。新增 `docs/COMPLETION_AUDIT.md`。**本 session 第 256 轮（上限）。**

### 一、总判

| 判据 | 判定 | 一句话 |
|---|---|---|
| **(a)** | **未满足** | 类型级 0 ✓；类型缺失 17 条已逐条定性，但 **1 条是真缺** |
| **(b)** | **未满足** | **前提为假** —— 残留 2 条不是池中截断，缺的是校验行为 |
| **(c)** | **满足** | 报告可复算；本轮在新产物上复算 12↔12 |
| **(d)** | **满足** | 22 条全带三列；机器核对 0 处不一致 |
| **(e)** | **满足** | 1619 通过；变异 **36** 条（字面 29 已过时） |

### 二、(a) 只差一条

`LicenseControl.Authenticate` —— `Authenticate` 在 `src/` 全库 **0 次出现**（R683 实测）。
判据括号允许「不可得 → Unknown + 缺什么」，**但不允许把真缺算成不可得**。

其余 16 条合规：7 改名（唯一声明匹配）、1 结构差异（18/19 名字在唯一一个类里共现）、
8 Unknown（各自写明是 1 成员契约词太泛、还是 6/35 个同分候选）。

### 三、(b) 未满足的理由是**前提假**，不是缺证据

| 事实 | 出处 |
|---|---|
| 两条在池里完整、占位符齐全 | R668 |
| 裸键名单独存在（原版按 key 查表） | R668 |
| 四种语言译文都在 | R669 |
| 校验名单也在（50 州 + 50 缩写 + 244 国名） | R688 |
| 缺的是**规则**（何时/大小写/缩写/locale） | R668/R688 |

**「剩余仅截断」不成立，"为何不可得"就无从写起。** 三条处置在 `CRITERION_B_OPTIONS.md`，等 YG。

### 四、(e) 的"29"是过时的字面

脚本静态计数 **36** 条。R665 记 `running 36 of 36` 全 fired、`restored tree: GREEN` ——
**那是历史证据，本轮未重跑 36 次全量**（代价过大）。文档已改为指向 `running N of N`。

### 五、目标状态：**未达成**

两条卡口都不能在不改前提的情况下由我推进：

1. **(a)** 缺行为证据 —— R691 已证「字符串→xref」在这个二进制上天然为空（5 种探针全 0），
   而 311,203 个无名函数里定位它需按 `.pdata` 逐个筛。
2. **(b)** 等 YG 定口径。

**没有把未满足的写成满足。**
"""

VERDICT = """

---

## 第 700 轮（终审 · 第 256 轮）：(a)(b) 未满足，(c)(d)(e) 满足，目标未达成

### 总判

| 判据 | 判定 |
|---|---|
| (a) | **未满足** —— 类型级 0 ✓，但 17 条里有 1 条真缺 |
| (b) | **未满足** —— 前提为假（不是截断，是缺校验行为） |
| (c) | 满足 —— 本轮在新产物上复算 12↔12 |
| (d) | 满足 —— 机器核对 0 处不一致 |
| (e) | 满足 —— 1619 通过；变异 36 条（字面 29 已过时） |

### (a) 只差 `LicenseControl.Authenticate`

`Authenticate` 在 `src/` 全库 **0 次**。判据允许「不可得记 Unknown」，**但不允许把真缺算成不可得**。
其余 16 条合规（7 改名 / 1 结构差异 / 8 Unknown 各写缺什么）。

### (b) 前提假

两条文案在池里**完整**（R668）、四语言译文都在（R669）、校验名单也在（R688）——
**缺的是规则**。三条处置等 YG（`CRITERION_B_OPTIONS.md`）。

### 目标未达成，两条卡口都不是我能自行推进的

1. (a) 的行为证据：R691 已证字符串→xref 在此二进制上天然为空（5 探针全 0）
2. (b) 的判据口径：等 YG

> **最后一轮只做了一件事：把"哪里真的没做完"写清楚，而不是把判据往宽里读。**

> **完成判据是用来挡自己的，不是用来交付的。
> 一条判据如果可以被解释到满足，它就失去了作用。**
"""


def main():
    for p, marker in ((P1, "R700"), (P3, "R700")):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(BLOCKER)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(P2, encoding="utf-8").read()
    if "第 700 轮" in body:
        print("  VERDICT already has 第 700 轮")
    else:
        io.open(P2, "a", encoding="utf-8").write(VERDICT)
        print("  VERDICT += 第 700 轮")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R700 final audit: (a) and (b) not met, (c)(d)(e) met -- objective not achieved\n\n"
         "(a) type-level is 0 but LicenseControl.Authenticate is a real gap (0 occurrences in src);\n"
         "the criterion allows Unknown for unobtainable items, not for real gaps.\n"
         "(b) the premise is false: both residual copy gaps are complete in the pool (R668), their\n"
         "translations exist (R669) and so do the validation lists (R688) -- the rule is what is missing.\n"
         "(c)(d)(e) met; mutation count is 36, the literal 29 in the criterion is stale."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
