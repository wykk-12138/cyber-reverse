"""Record R725: the evidence taxonomy, and the discovery of a second build on disk."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 154. 先枚举，再数：证据种类总表 + 盘上还有**第二个版本**（5.18.35）

> R725。新增 `docs/EVIDENCE_CLASSES.md`（本次交付的核心）。

### 一、上一轮欠的那一步做了

R724 的结论是「我的测量方法缺少一步『先枚举来源』」。这一轮补上：**把原版能提供的证据列全**，
十类，每类写载体、可得性、是否在用、是否红线。

| # | 证据类 | 在用？ |
|---|---|---|
| 1 | 二进制字节 | 是 |
| 2 | 反编译伪代码 | 是（主参照） |
| 3 | 字符串池 | 是 |
| 4 | 编译期 XAML 描述符（1,457 条） | 是 |
| 5 | locale 目录（1,142 条） | 是 |
| 6 | **原版磁盘数据**（5500 + 12 个文件） | **部分**（只用过 settings.json 键码） |
| 7 | **第二版本 5.18.35** | **从未用于本任务** |
| 8 | 网络抓包 | 无既有文件 |
| 9 | 运行期观察 | 不可得（需凭据） |
| 10 | 调用图/入度 | 试过，**判据被证否**（R719） |

### 二、盘上还有第二个版本 —— 这是本轮的实际发现

盘点 `%LOCALAPPDATA%\\Cybersole` 时看到 `current\\Cybersole.exe`，尺寸和我锁定的靶子不同。实测：

```
target\\Cybersole.exe                          5.18.32.0  129,243,216  md5 f81070a1…
%LOCALAPPDATA%\\Cybersole\\current\\Cybersole.exe 5.18.35.0  129,306,192  md5 30eef212…
差值                                                       +62,976
```

旁边还有 `packages\\Cybersole-5.18.35-win-x64-full.nupkg`（59,732,175 B）。

### 三、为什么这重要（不是"顺便发现"）

本任务要 1:1 的是 **5.18.32**，盘上还有一个 **5.18.35**。**两版差分能回答 C7c 一直答不了的问题**：

- **两版相同的函数** = 一个真实版本增量里都没动过的核心 → **稳定的见证目标**
- **两版不同的函数** = 版本特有逻辑 → 拿它当"功能对等"的证人**不具代表性**
- 差分还给出**一份外部事实**：官方到底改了什么 —— **在没有符号、跑不起来的情况下，这是唯一能拿到的第三方校验**

工具已白名单化（AGENTS.md §1，只读）：`pe_diff.py`。R431 用过一次，结论「六节全重排」——
**当时只当版本分诊，没当复刻证据。**

### 四、这张表和 TEST_PROVENANCE 的关系

`TEST_PROVENANCE.md` 量「复刻件的测试用了哪类证据」；本表量「原版能给哪几类」。
**两者相乘才是 C7c 的真实覆盖。** R721–R724 的问题正是**没先做本表**，所以那个表的分母一直在动。

### 五、仍然 Unknown

- 第 8 类是否真无抓包：**Unknown**（只看了两个数据目录，未全域搜）。
- 第 6 类 5500 个文件里哪些是程序自己写的：**Unknown**（大部分是 Chromium 运行时，未甄别）。
- 第 7 类能覆盖多少函数：**Unknown**（差分未跑）。

### 六、下一轮

跑 `pe_diff.py` 5.18.32 ↔ 5.18.35，**用差分结果去选探针目标**——
不再问「哪个函数重要」，改问「哪个函数在真实版本增量里没变」。
"""

VERDICT = """

---

## 第 725 轮：先枚举，再数 —— 并且发现盘上还有第二个版本

### 补上欠的那一步

新增 `docs/EVIDENCE_CLASSES.md`：十类证据，每类写载体、可得性、是否在用、红线。
R721–R724 四轮都在「数完发现漏了一类」，根因是**量之前没枚举**。这张表就是那一步。

### 实际发现：5.18.35 也在盘上

```
target\\Cybersole.exe                          5.18.32.0  129,243,216  md5 f81070a1…
%LOCALAPPDATA%\\Cybersole\\current\\Cybersole.exe 5.18.35.0  129,306,192  md5 30eef212…
```

旁边还有 `Cybersole-5.18.35-win-x64-full.nupkg`。

### 为什么重要

**两版相同的函数** = 真实版本增量里没动过的核心 → **稳定的见证目标**。
**两版不同的函数** = 版本特有逻辑 → 当"功能对等"的证人不具代表性。

差分还给出**一份外部事实**：官方到底改了什么。**在没符号、跑不起来的情况下，这是唯一能拿到的第三方校验。**

工具已白名单（`pe_diff.py`），R431 用过一次但**只当版本分诊，没当复刻证据**。

### 一句话

> 我一直在问「哪个函数重要」。**「哪个函数在真实版本增量里没变」是个更好的问题** ——
> 因为它不依赖我的判断，只依赖两次官方发布。

### 下一轮

跑 5.18.32 ↔ 5.18.35 的差分，拿结果选探针目标。
"""


def main():
    for p, marker, text in ((P1, "R725", BLOCKER), (P3, "R725", BLOCKER), (P2, "第 725 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    # link the new doc from the handoff routes so a fresh session finds it
    hb = r"D:\projects\cyber-reverse\docs\HANDOFF_BLOCKERS.md"
    body = io.open(hb, encoding="utf-8").read()
    if "EVIDENCE_CLASSES" not in body:
        io.open(hb, "a", encoding="utf-8").write(
            "\n\n## 证据种类总表\n\n`docs/EVIDENCE_CLASSES.md` —— **量任何东西之前先读它**："
            "原版能提供十类证据，其中第 7 类（盘上的 5.18.35）从未用于本任务。\n")
        print("  HANDOFF_BLOCKERS.md += EVIDENCE_CLASSES pointer")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R725: enumerate the evidence classes first, and a second build is sitting on disk\n\n"
         "Four consecutive rounds (R721-R724) ended with 'the number was higher because I had missed an\n"
         "evidence class'. The root cause was not an incomplete marker set but measuring before listing\n"
         "what the original can offer. docs/EVIDENCE_CLASSES.md is that listing: ten classes with carrier,\n"
         "availability, whether it is in use, and whether it crosses the read-only red line.\n\n"
         "Listing two data directories turned up %LOCALAPPDATA%\\Cybersole\\current\\Cybersole.exe at\n"
         "129,306,192 bytes against the target's 129,243,216:\n\n"
         "  target\\Cybersole.exe   5.18.32.0  md5 f81070a1b90857c0c868336dcd7f0d58\n"
         "  installed              5.18.35.0  md5 30eef212c3a4e96bb0e744743b355bd6\n\n"
         "A second build of the same program, plus its 59 MB nupkg. That is evidence class seven, never\n"
         "used for this task.\n\n"
         "Why it matters for C7c: functions identical across the two releases are the core that a real\n"
         "version delta did not touch, which makes them stable witnesses; functions that differ carry\n"
         "version-specific logic and are poor witnesses for 'functional equivalence'. The diff is also an\n"
         "external fact -- what the publisher actually changed -- which is the only third-party check\n"
         "available with no symbols and no runnable original. pe_diff.py is already whitelisted; R431 ran\n"
         "it once but only for version triage, never as replica evidence."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
