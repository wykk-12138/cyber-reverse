"""Record R696 (second attempt -- the first embedded a docstring that closed the outer literal)."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = '''

---

## 129. 把那条坑串成三处入口 —— 让下一次在**动手的地方**被拦住

> R696。改 `docs/PARITY_PRODUCT.md`、`docs/IDA_STARTUP_CHECKLIST.md`、`analysis/wait_ready.py`。

### 一、问题不在"没写下来"，在"写的地方不对"

R695 查明：这个坑 R433 就写进了 `PARITY_PRODUCT.md` §8，判据也给了；R613 还用过 `auto_analysis_ready`。
**而 R694 我照样踩了。**

原因很具体：`PARITY_PRODUCT.md` 是**产物对照报告**，读它的时候是"看结论"；
**取数的时候读的是代码和启动步骤**，不是那份报告。
**教训写在"总结"里，而犯错发生在"操作"里 —— 两者之间没有边。**

### 二、三处入口（各自不同的用途）

| 位置 | 用途 | 加了什么 |
|---|---|---|
| `docs/PARITY_PRODUCT.md` §8 | **历史记录**（R433 原文不动） | 下面加一条指向操作手册与工具的指引 |
| `docs/IDA_STARTUP_CHECKLIST.md` | **操作手册** | 指向历史记录，并说明旧判据已被取代 |
| `analysis/wait_ready.py` 文件头 | **就在取数的代码里** | 写明它取代的两个判据、以及为什么"两次一致"不够 |

**第三处是真正的修复**：判据现在住在**取数的那段代码里**，而不是只住在一份报告里。

### 三、`wait_ready.py` 文件头写下的关键理由（转述，不引原文以免混淆引号）

- 它取代 R433 的判据："窗口标题不再带 Loading" + "连续两次取值相同"；
- **后半不成立**，因为中间态是**稳定**的：R433 的错误/正确比值 `136,798/187,328 = 0.730`，
  R694 是 `136,989/187,732 = 0.730`，相隔 260 多轮仍一致。**两次取样可能都对，也可能都错。**
- R613 早已在用 `auto_analysis_ready` —— **好判据本来就存在，只是住在报告里，没住在取数的代码里。**

### 四、验证

```
wait_ready.py parses OK; docstring mentions R433: True, stable: True
完整套件  exit 0  1619 通过 / 0 失败 / 0 跳过
git       32b43f6（三处改动一次提交）
```

### 五、仍然 Unknown

- 这类"教训写在报告里、犯错发生在操作里"的缺口还有多少处：**Unknown** ——
  本轮只处理了这一条，没有系统清点其它坑是否都有操作入口。
- 是否还有第三种"稳定的中间态"（不只 IDA 分析）：**Unknown**。
'''

VERDICT_TEXT = '''

---

## 第 696 轮：把那条坑串成三处入口

### 一、问题不在"没写下来"，在"写的地方不对"

R433 写进了报告、R613 用过正确判据，**而 R694 我照样踩了**。

`PARITY_PRODUCT.md` 是**看结论**时读的；**取数时读的是代码和启动步骤**。
**教训写在"总结"里，犯错发生在"操作"里 —— 两者之间没有边。**

### 二、三处入口

| 位置 | 用途 | 加了什么 |
|---|---|---|
| `PARITY_PRODUCT.md` §8 | 历史（原文不动） | 指向手册与工具的指引 |
| `IDA_STARTUP_CHECKLIST.md` | 操作手册 | 指向历史，说明旧判据被取代 |
| `analysis/wait_ready.py` 头 | **就在取数的代码里** | 它取代哪两个判据、为什么"两次一致"不够 |

**第三处才是修复**：判据现在住在取数的代码里。

### 三、写的理由是定量的

> R433 的错误/正确比值 **0.730**；R694 **0.730**，隔 260 多轮。
> **中间态是稳定的，所以两次一致可能都是错的。**

### 四、一句话

> 这一轮没有新结论，只是把一条已知教训从"读过的人记得"变成"动手的人躲不开"。

> **文档的有效性不看它写得多清楚，看它离那个动作有多近。**

### 五、下一轮

有个模式值得系统查一遍：**`BLOCKERS.md` / `PARITY_PRODUCT.md` 里的坑，有多少条有"操作入口"**
（启动清单 / 脚本头 / 守卫测试），多少条只停在报告里。下一轮做这个清点 —— 比再修一个坑更有价值。
'''


def main():
    for p, marker, text in ((P1, "R696", BLOCKER), (P3, "R696", BLOCKER), (P2, "第 696 轮", VERDICT_TEXT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R696: record the cross-link and why placing the criterion in the code is the fix"],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:150]))


if __name__ == "__main__":
    main()
