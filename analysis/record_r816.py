"""Record R816: the sampling rule goes into AGENTS.md, and my own record broke a doc guard."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 240. 抽样规则写进 `AGENTS.md`；而**我自己的记录把文档守卫弄红了**

> R816。`AGENTS.md` 新增 §2.7b；`replica/docs/VERDICT.md` 改一句措辞。

### 一、上一轮的结论落成规则

R815 发现 `pe_strings.txt` 是抽样（含 `NIKE`、不含 `NIKE-GS`，而后者在 `0x146e11414`）。
**这一轮把它写成 `AGENTS.md` §2.7b**，与 §2.7 并列：

> **扫之前先问：我这个来源，找得到就等于有吗？**

表里记了四轮：R806（显示截断读成读取错误）· R807（token 键当厂商清单）·
R813（池子搜不到当镜像没有）· R814（用池子数 slug，得到下界）。

**四条判据**：正向可用（找到⇒有）· 反向不可用（没找到⇏没有，要用 `ida.py str`）·
数数要写明下界还是全量 · **动手删除之前先查连带影响**。

### 二、写规则时又踩了一次 —— 这次踩的是我自己写的记录

改完 `AGENTS.md` 跑全量：**1765 通过 / 1 失败。**

失败的是 `DocsConsistencyTests.TheModuleCountInVerdictMatchesTheCatalogue`。它扫 `VERDICT.md` 正文，
把**所有** `N 个模块` / `N modules`（N≥20）当成本文档对「目录有多少模块」的断言，要求全等于 63。

**而我在 R813 的 VERDICT 里写了一个小标题：**

```
### 复刻件 → 镜像：57 个模块逐个查过
```

**那句话是真的** —— `store_catalog.py` 的打印输出确实解析出 57 行。
**但它不是「目录有几个模块」的断言，守卫分不出这两件事。**

**而守卫不该分。要改的是我的措辞，不是守卫。**

### 三、改法

```
### 复刻件 → 镜像：那个目录打印了 57 行，逐行查过
```

**改完用守卫自己的正则复算：**

```
claims the guard will see: [63]
passes against 63: True
```

**全量回到 1766 通过 / 0 失败。**

### 四、顺带查清的一件事：`62 modules` 不是违规

同一份 `VERDICT.md` 里有一行 `total 62 modules`，看着也该红 —— **它在围栏里，守卫的
`Regex.Replace(doc, "```.*?```", …)` 把它排除了。** 我先前的 grep 之所以看到它，是因为我把围栏正则写错了。

**所以违规的只有我那一处。** 这也说明守卫的口径是对的：**围栏内的历史输出不算断言，围栏外的散文算。**

### 五、验证

```
python analysis\\fix_verdict_claim.py      claims=[63]  passes=True
dotnet test --filter DocsConsistencyTests  7 通过 / 0 失败
python tools\\metrics_report.py            1766 通过 / 0 失败
四项度量                                   4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- **`AGENTS.md` 新增的 §2.7b 有没有改变任何既有守卫的期望**：**全量绿，所以没有** ——
  但**我没有单独确认没有守卫会扫 `AGENTS.md`**（`DocsConsistencyTests` 扫的是 `VERDICT.md`）。
- **`62 modules` 那行是哪个年代留下的**：**没查** —— 它在围栏里，不影响守卫。
- **§2.7b 能不能真的防住这类错**：**Unknown** —— 规则写下来只提高下一次注意到的概率，
  **它不会自动生效。**

### 七、教训

**我在写「如何避免误判」的同一轮里，误判了自己的文案该不该算断言。**
**区别在于：这次的守卫是别人（过去的我）设的，它抓住了我** ——
**而 §2.7b 是我这一轮才设的，还没有抓住过任何人。**

**一条规则的价值不在它写得对，在它被触发过一次。**
"""

VERDICT = """

---

## 第 816 轮：抽样规则进 AGENTS.md，而我的记录把文档守卫弄红了

### 规则落地

R815 发现 `pe_strings.txt` 是抽样。**这一轮写成 `AGENTS.md` §2.7b**：

> **扫之前先问：我这个来源，找得到就等于有吗？**

**四条**：正向可用 · 反向不可用（要用 `ida.py str`）· 数数要写明下界还是全量 · **删除前先查连带影响**。

### 写规则时又踩了一次

改完跑全量：**1765 / 1 失败。**
`DocsConsistencyTests.TheModuleCountInVerdictMatchesTheCatalogue` ——
它把正文里所有 `N 个模块`（N≥20）当成本文档的断言，要求全等于 63。

**而我在 R813 的 VERDICT 里写了 `### 复刻件 → 镜像：57 个模块逐个查过`。**

**那句话是真的**（目录确实打印出 57 行），**但它不是「目录有几个模块」的断言 —— 守卫分不出这两件事。**

> **而守卫不该分。要改的是我的措辞，不是守卫。**

**改成**「那个目录打印了 57 行，逐行查过」，守卫只看得到 `[63]`，全量回到 **1766 / 0**。

### 顺带查清：`62 modules` 不是违规

那行在围栏里，守卫的围栏正则已排除它。**我先前的 grep 看到它，是我把围栏正则写错了。**

### 验证

```
fix_verdict_claim.py claims=[63] · DocsConsistencyTests 7/7 · 全套 1766 / 0 · 度量未变
```

### 教训

**我在写「如何避免误判」的同一轮里，误判了自己的文案该不该算断言。**
**区别是：这次的守卫是过去的我设的，它抓住了现在的我 —— 而 §2.7b 是这一轮才设的，还没抓住过任何人。**

> **一条规则的价值不在它写得对，在它被触发过一次。**
"""

BACKLOG_ADD = """

## 纪律 — 抽样规则进 AGENTS.md（R816）

**`AGENTS.md` §2.7b 新增**：

> **扫之前先问：我这个来源，找得到就等于有吗？**

| 判据 | |
|---|---|
| **正向可用** | 池子里找到 ⇒ 镜像里有 |
| **反向不可用** | 没找到 **⇏** 没有 —— 要用 `analysis/ida.py str <pat>` |
| **数数写明** | 下界还是全量 |
| **删除前查连带** | R815 那行地址救了两个模块 |

**踩坑四轮**：R806（显示截断）· R807（token 键当清单）· R813（搜不到当没有）· R814（用池子数 slug）。

### 同轮自伤一次

**改了 `AGENTS.md` 后全量变 1765/1**：`DocsConsistencyTests` 把正文所有 `N 个模块`（N≥20）当断言，
**而我在 R813 的 VERDICT 写了「57 个模块逐个查过」** —— 那句话真，但不是「目录有几个模块」的断言。

**改措辞解决**（不是改守卫）：`claims=[63]` → 全套 1766 / 0。

| 仍 Unknown | |
|---|---|
| 有无守卫扫 `AGENTS.md` | 全量绿，但未单独确认 |
| §2.7b 能否真防住 | **规则只提高注意概率，不自动生效** |

**一条规则的价值不在它写得对，在它被触发过一次。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R816", BLOCKER)
    ensure(RSTATUS, "R816", BLOCKER)
    ensure(RVERDICT, "第 816 轮", VERDICT)
    ensure(BACKLOG, "R816", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R816"), (RSTATUS, "R816"), (RVERDICT, "第 816 轮"), (BACKLOG, "R816")):
        body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R816: the sampling rule goes into AGENTS.md, and my own record broke a doc guard\n\n"
         "R815 found that pe_strings.txt is a sample -- it contains NIKE and not NIKE-GS, while NIKE-GS sits at\n"
         "0x146e11414. Section 2.7b now says so, next to the rule it extends: before scanning, ask whether finding a\n"
         "thing is the same as it being there. Four rounds are tabulated -- the truncated display in R806, the token\n"
         "keys read as a vendor list in R807, absent-from-the-pool read as absent-from-the-image in R813, and the slug\n"
         "count in R814 that is a lower bound rather than a total.\n\n"
         "Four judgements come with it. A pool hit means present. A pool miss does not mean absent, and reverse\n"
         "conclusions belong to ida.py str, which searches the database. Any count should say whether it is a bound or\n"
         "a total. And before deleting on evidence, check the blast radius, since R815 came close to deleting two\n"
         "modules that the image does contain.\n\n"
         "Then I broke a doc guard while writing the rule about misjudging sources. The full suite went to 1765 of 1766\n"
         "because DocsConsistencyTests treats any N 个模块 with N of at least twenty in VERDICT prose as a claim about\n"
         "how many modules the catalogue holds, and my R813 heading said 57 个模块逐个查过. That sentence is true --\n"
         "store_catalog prints 57 rows -- but it is not that claim, and the guard cannot tell the difference.\n\n"
         "The guard should not have to. The wording was mine to fix, so the heading now says the directory printed 57\n"
         "rows and each was checked, and the guard sees only 63 again. A 62 modules line elsewhere in the file looked\n"
         "like a second offender and is not: it sits inside a fence, which the guard excludes, and my earlier grep\n"
         "reported it because my own fence matching was wrong.\n\n"
         "Unknown: whether any guard reads AGENTS.md itself, which the green suite suggests it does not but which I did\n"
         "not verify; and whether 2.7b will prevent anything, since a written rule raises the odds of noticing and does\n"
         "nothing on its own.\n\n"
         "The distinction worth keeping is that the guard that caught me was set by an earlier version of me, while\n"
         "2.7b was written this round and has caught nobody yet. A rule is worth what it has been triggered on, not what\n"
         "it says.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
