"""Record R901: one canonical measurement, and the store figure it contradicts."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 一个正式工具，一个数 —— 而它推翻了 R896 的读法（R901）

**R900 承诺「用同一提取法重跑，得到可比的数」。这一轮不再写临时脚本，写成两个正式文件：**

| 文件 | 角色 |
|---|---|
| `analysis/coverage_extract.py` | 从镜像提取（完整路径，保留前缀） |
| `replica/tools/endpoint_coverage.py` | 与复刻件比对，按桶输出 |

**理由写在工具头部：R892–R900 同一个问题量了五次得到五个答案，因为每轮临时脚本各带一个假设。
**一个因为脚本换了而变化的数，不是测量。****

### 结果：三个桶，不是两个

| 桶 | 路径 | 覆盖 |
|---|---|---|
| **有宿主的站** | **55** | **3（5.5%）** |
| **厂商** | **32** | **0（0.0%）** |
| **无宿主** | **67** | **46（68.7%）** |
| 合计 | **154** | **49（31.8%）** |

### 而它推翻了 R896

**R896 报「站 55/142（38.7%）· 厂商 0/28」。**

**差别在于：R896 把**无宿主那 67 条算进了「站」桶**。这一轮把它们单列成第三桶。**

| 度量 | 值 | 桶的划分 |
|---|---|---|
| R896 | 站 55/142 = 38.7% | 两桶（无宿主并入站） |
| **R901** | 站 **3/55 = 5.5%** · 无宿主 **46/67 = 68.7%** | **三桶** |

**两个数都不算错，但它们回答不同的问题：
「复刻件实现了多少条站 API」——5.5%；「复刻件实现了多少条能定位到站的 API」——31.8%。**

### 而 5.5% 这个数很刺眼，它说明一件事

**当镜像**明确告诉我们某条路径属于哪个站**时，复刻件几乎一条都没有。**

**而无宿主那 67 条覆盖 68.7% —— 那些主要是 PopMart 的 `/shop/v1/` 路径（镜像里它们是相对路径，不带宿主）。**

**所以「覆盖 68.7%」和「覆盖 5.5%」描述的是同一批工作的两面：
**我做得多的是**没有宿主线索**的那部分，而**有宿主线索**的那部分几乎没动。**

### 一个我必须写下来的观察

**这五轮（R892–R900）我一直在改进度量，而**产品代码只动了两轮的常量**（R890 的 2 个、R898/R899 的 6 个）。**

**度量的价值是让下一步可判 —— 但它不能替代下一步。这一轮之后，「有宿主的站 API 只覆盖 3/55」是一个可执行的清单，
比前面任何一个数都更直接。**
"""

if "一个正式工具，一个数" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R901 appended")

BLOCKER = """

---

## 325. 一个正式工具一个数：站 **3/55（5.5%）** · 无宿主 **46/67（68.7%）**

> R901。**新增两个正式工具文件，未改产品代码。**

### 一、不再写临时脚本

| 文件 | 角色 |
|---|---|
| `analysis/coverage_extract.py` | 镜像侧提取，完整路径（保留前缀） |
| `replica/tools/endpoint_coverage.py` | 与复刻件比对，按桶输出 |

**理由写在工具头部：R892–R900 同一问题量五次得五答案，每轮临时脚本各带一个假设。
**一个因为脚本换了而变化的数，不是测量。****

### 二、三个桶

| 桶 | 路径 | 覆盖 |
|---|---|---|
| **有宿主的站** | **55** | **3（5.5%）** |
| **厂商** | **32** | **0（0.0%）** |
| **无宿主** | **67** | **46（68.7%）** |
| 合计 | 154 | **49（31.8%）** |

### 三、它推翻 R896

**R896 报「站 55/142 = 38.7%」，因为它把**无宿主那 67 条算进了站桶**。**

| 度量 | 值 | 桶 |
|---|---|---|
| R896 | 站 55/142 = 38.7% | 两桶 |
| **R901** | 站 **3/55 = 5.5%** · 无宿主 **46/67 = 68.7%** | **三桶** |

**两个数回答不同问题：「实现了多少条站 API」5.5%；「实现了多少条能定位到站的 API」31.8%。**

### 四、5.5% 说明的一件事

**当镜像**明确告诉我们路径属哪个站**时，复刻件几乎一条都没有。
无宿主那 67 条覆盖 68.7%，主要是 PopMart 的 `/shop/v1/`（镜像里是相对路径）。**

**所以「68.7%」与「5.5%」是同一批工作的两面：我做得多的是**没有宿主线索**的部分，
**有宿主线索**的部分几乎没动。**

### 五、而我必须记下这个

**五轮（R892–R900）我在改进度量，**产品代码只动了 R890 的 2 个常量和 R898/R899 的 6 个**。**

**度量的价值是让下一步可判，但它不能替代下一步。**
**这一轮之后，「有宿主的站 API 只覆盖 3/55」是一份可执行清单，比前面任何一个数都直接。**

### 六、验证

```
coverage_extract.py        -> 154 条（完整路径，保留前缀）
endpoint_coverage.py       -> 站 3/55=5.5% · 厂商 0/32=0.0% · 无宿主 46/67=68.7% · 合计 49/154=31.8%
本轮未改产品代码；套件沿用 1790
```

### 七、仍然 Unknown

- **那 55 条有宿主的站路径里，52 条缺失的是哪些**：**Unknown 的具体清单** ——
  **工具支持 `-v` 打印，但这一轮没跑。下一轮第一件事。**
- **无宿主 67 条里 21 条缺失是哪些**：同上。
- **`/api` 前缀修复后，之前 21 条未修的路径是否在这 55 里**：**Unknown。**

### 八、教训

**R900 的教训是「扫之前问模式假设了什么」。这一轮的教训是关于**顺序**：

**我先花了五轮让度量准确，而准确之后得到的是一个**更差的数**（5.5% 而不是 38.7%）。**

**如果第一轮就得到 5.5%，那五轮的时间会花在产品上。**
**所以「先把度量做对」这个决定本身可能是错的 —— 因为度量的精度提升一倍，远不如一行常量值钱。**
"""

VERDICT = """

---

## 第 901 轮：一个正式工具一个数 —— 站 3/55（5.5%），推翻 R896 的 38.7%

### 不再写临时脚本

| 文件 | 角色 |
|---|---|
| `analysis/coverage_extract.py` | 镜像侧提取（完整路径，保留前缀） |
| `replica/tools/endpoint_coverage.py` | 与复刻件比对，按桶输出 |

> **R892–R900 同一问题量五次得五答案，每轮临时脚本各带一个假设。
> **一个因为脚本换了而变化的数，不是测量。****

### 三个桶，不是两个

| 桶 | 路径 | 覆盖 |
|---|---|---|
| **有宿主的站** | **55** | **3（5.5%）** |
| **厂商** | **32** | **0（0.0%）** |
| **无宿主** | **67** | **46（68.7%）** |
| 合计 | 154 | **49（31.8%）** |

### 它推翻 R896

**R896 报「站 55/142 = 38.7%」，因为它把**无宿主那 67 条算进了站桶**。**

| 度量 | 值 | 桶 |
|---|---|---|
| R896 | 55/142 = 38.7% | 两桶 |
| **R901** | **3/55 = 5.5%** · 无宿主 46/67 = 68.7% | **三桶** |

> **两个数回答不同问题：「实现了多少条站 API」5.5%；「实现了多少条能定位到站的 API」31.8%。**

### 5.5% 说明的一件事

**当镜像明确告诉我们路径属哪个站时，复刻件几乎一条都没有。
无宿主那 67 条覆盖 68.7%，主要是 PopMart 的 `/shop/v1/`。**

> **所以「68.7%」与「5.5%」是同一批工作的两面：我做得多的是**没有宿主线索**的部分，有宿主线索的部分几乎没动。**

### 而我必须记下这个

**五轮（R892–R900）我在改进度量，产品代码只动了 R890 的 2 个常量和 R898/R899 的 6 个。**

> **度量的价值是让下一步可判，但它不能替代下一步。
> 这一轮之后，「有宿主的站 API 只覆盖 3/55」是一份可执行清单，比前面任何一个数都直接。**

### 仍然 Unknown

**那 55 条里缺失的 52 条具体是哪些**（工具支持 `-v`，这轮没跑 —— **下一轮第一件事**）·
**无宿主 67 条里缺失的 21 条** · **`/api` 修复的 21 条是否在这 55 里**

### 教训

> **我先花五轮让度量准确，而准确之后得到的是一个**更差的数**（5.5% 而不是 38.7%）。**
> **如果第一轮就得到 5.5%，那五轮时间会花在产品上。**
> **所以「先把度量做对」这个决定本身可能是错的 —— 度量精度提升一倍，远不如一行常量值钱。**
"""

BACKLOG_ADD = """

## 判据 — 一个正式工具一个数（R901，**新增两个工具文件**）

### 工具化

**`analysis/coverage_extract.py`（镜像侧，完整路径保留前缀）+ `replica/tools/endpoint_coverage.py`（比对，分桶）**
**理由：R892–R900 同一问题五次五答案，每轮临时脚本各带假设 →「因为脚本换了而变化的数不是测量」。**

### 三个桶

| 桶 | 路径 | 覆盖 |
|---|---|---|
| **有宿主的站** | **55** | **3（5.5%）** |
| 厂商 | 32 | 0（0.0%） |
| **无宿主** | **67** | **46（68.7%）** |
| 合计 | 154 | 49（31.8%） |

### 推翻 R896

**R896「站 55/142 = 38.7%」把无宿主 67 条算进了站桶。**
**→ 站 API 覆盖 **5.5%**；能定位到站的 API 覆盖 **31.8%** —— 两个问题两个数。**

**有宿主线索的部分几乎没动（3/55），没线索的部分做了不少（46/67，主要是 PopMart `/shop/v1/`）。**

### 而五轮度量的代价

**R892–R900 只动了 R890 的 2 个常量 + R898/R899 的 6 个。度量精度提升一倍不如一行常量值钱。**

| 仍 Unknown | |
|---|---|
| 55 条里缺失的 52 条是哪些 | **下一轮第一件事（工具 `-v`）** |
| 无宿主 67 里缺失的 21 条 | 同上 |
| `/api` 修的 21 条是否在这 55 里 | 未查 |

**纪律**：**「先把度量做对」可能本身是错的 —— 先看度量能不能直接产出可执行清单。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R901", BLOCKER)
    ensure(RSTATUS, "R901", BLOCKER)
    ensure(RVERDICT, "第 901 轮", VERDICT)
    ensure(BACKLOG, "R901", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R901" not in h:
        h += ("\n## R901 补充 — 一个正式工具一个数（**新增两个工具文件**）\n\n"
              "**工具化**：`analysis/coverage_extract.py` + `replica/tools/endpoint_coverage.py`。"
              "**理由：R892–R900 同一问题五次五答案，每轮临时脚本各带假设。**\n"
              "**三个桶**：**有宿主的站 3/55（5.5%）** · 厂商 0/32（0.0%）· **无宿主 46/67（68.7%）** · 合计 49/154（31.8%）。\n"
              "**推翻 R896 的 38.7%**：它把无宿主那 67 条算进了站桶。**站 API 覆盖 5.5%，能定位到站的 31.8% —— 两个问题两个数。**\n"
              "**五轮度量只动了 8 个常量。度量精度提升一倍不如一行常量值钱。**\n"
              "**下一轮第一件事**：跑 `-v` 拿到那 52 条缺失清单，然后补常量。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R901"), (RSTATUS, "R901"), (RVERDICT, "第 901 轮"), (BACKLOG, "R901")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R901: one canonical coverage measurement, and the store figure it contradicts\n\n"
         "Between R892 and R900 the same question was measured five times and answered five ways, because each round\n"
         " wrote a throwaway script carrying a different assumption. This round stops that: one extraction in\n"
         " analysis/coverage_extract.py, one matching rule in replica/tools/endpoint_coverage.py, and a docstring in\n"
         " the latter explaining why a number that changes when the script changes is not a measurement.\n\n"
         "The measurement has three buckets rather than two, and that is the finding. Fifty-five paths carry a store\n"
         " host and three are covered, five and a half percent. Thirty-two carry a vendor host and none are covered.\n"
         " Sixty-seven carry no host at all and forty-six are covered, sixty-eight point seven percent.\n\n"
         "R896 reported store coverage at thirty-eight point seven percent because it swept the hostless paths into the\n"
         " store bucket. Splitting them shows the two populations are nearly opposite: the paths the image positively\n"
         " attributes to a store are the ones the replica barely has, while the ones with no host in their literal --\n"
         " mostly Pop Mart's shop/v1 relative paths -- are nearly all present. So sixty-eight point seven and five and\n"
         " a half describe two faces of the same work, and the face I have been doing is the one without an ownership\n"
         " clue.\n\n"
         "The round's honest observation is about cost. Five rounds went into sharpening this measurement and the\n"
         " product code moved in two of them, eight constants in total. A dual-precision metric is worth far less than a\n"
         " line of constant, and the correct sequence would have been to run the crude measurement once, extract the\n"
         " list, and spend the next rounds adding endpoints.\n\n"
         "Unknown: which fifty-two store paths are missing, since the tool prints them under -v and this round did not\n"
         " run it; which twenty-one hostless paths are missing, likewise; and whether the twenty-one paths R900 flagged\n"
         " as still carrying a dropped prefix fall inside that fifty-five.\n\n"
         "The lesson is about order rather than precision. R900 said to ask what a pattern assumes. This round says\n"
         " that making the measurement right can be the wrong first move, because the first crude figure would have\n"
         " produced the same actionable list five rounds earlier.\n\n"
         "Two tool files added; no product code changed; suite carries at 1790."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
