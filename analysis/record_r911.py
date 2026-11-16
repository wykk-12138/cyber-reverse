"""Record R911: the Async-suffix undercount, and the damage this round did on the way to finding it."""

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
### 覆盖率从 20.4% 修到 **24.0%** —— 因为我的匹配漏了 `Async` 后缀（R911）

**R910 排出的榜首是 `ScrapeProduct` 7 · `ScrapeJson` 7，我按那个去补 —— 结果编译报 CS0111「重复定义」。**

### 根因

**镜像的名字从状态机类型（`d__NN`）恢复，所以它们是 `ScrapeProduct`（**无 `Async`**）。
而 C# 方法是 `ScrapeProductAsync`。**

**我的判据是 `\\bScrapeProduct\\b` —— 而 `\\b` 在 `t` 与 `A` 之间**不成立**，因为 `Async` 让标识符继续。
**所以 `ScrapeProductAsync` 不算命中 `ScrapeProduct`。****

### 影响范围

| 判据 | 命中 | 覆盖率 |
|---|---|---|
| 严格整词（旧） | 317 | 20.5% |
| **允许 `Async` 后缀（新）** | **371** | **24.0%** |

**54 个名字被误判为缺失。而 R906/R910 的所有排序都建立在这个误判上。**

### 而这一轮我先做坏了一次

**发现 CS0111 后我加了个删重复定义的动作，结果删掉 6,876 字符，**连 `GetHomeAsync` 一起删了** ——
虚步骤从 175 掉到 165，四个店编译失败（CS0115「没有找到适合的方法来重写」）。**

**而 `tools/.snapshot-backup` 不存在**（`snapshot.py` 写的是 `tools/.snapshots/`），所以我按错的路径找恢复源，找不到。**

**最后用 `git checkout -- src/Cybersole.Stores/Flows/StoreFlow.cs` 恢复 —— 175 恢复，编译干净。**

### 而第 462 轮那部分工作其实是对的

**`PopMartFlow` 在 HEAD 里**没有** `ScrapeProductAsync` / `ScrapeJsonAsync` 的 override。
所以我加的两个 override 是有效的、真实的。**

**这一轮保留了它们：`StoreFlow` 已有虚方法（所以不能重复声明），`PopMartFlow` 加 override（正确）。**

| 度量 | 改后 |
|---|---|
| `StoreFlow` 虚步骤 | **175** |
| 异步覆盖 | **371 / 1547 = 24.0%** |
| 缺失名承载出现次数 | **1303**（原 1523） |
| 套件 | **1815 通过 / 0 失败** |

### 新的缺失榜首（都真缺）

`WriteToAsync` 7 · `WriteRawAsync` 6 · `LoadAsync` 5 · `WriteStartNamespaceDeclarationAsync` 4 ·
`WriteAsyncInternal` 4 · `OverrideAsyncMethod` 4 · `OnLoadedAsync` 4 · `Enumerate` 4 · `DownloadAsync` 4

**`ScrapeProduct` 与 `ScrapeJson` 已从榜首消失 —— 因为它们现在真的在。**
"""

if "覆盖率从 20.4% 修到 **24.0%**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R911 appended")

VERDICT = """

---

## 第 911 轮：覆盖率 20.4% → 24.0%，因为匹配漏了 `Async` 后缀

### 根因

**镜像名从状态机类型恢复，是 `ScrapeProduct`（无 `Async`）；C# 方法是 `ScrapeProductAsync`。
而我的判据 `\\bScrapeProduct\\b` 里，`\\b` 在 `t` 与 `A` 之间不成立 —— **`Async` 让标识符继续。****

| 判据 | 命中 | 覆盖率 |
|---|---|---|
| 严格整词（旧） | 317 | 20.5% |
| **允许 `Async` 后缀（新）** | **371** | **24.0%** |

**54 个名字被误判为缺失。R906/R910 的所有排序都建立在这个误判上。**

### 而这一轮我先做坏了一次

**发现 CS0111 后我加了个删重复定义的动作 —— 删掉 6,876 字符，**连 `GetHomeAsync` 一起删了**。
虚步骤 175 → 165，四个店 CS0115 编译失败。**

**而 `tools/.snapshot-backup` 不存在（`snapshot.py` 写的是 `tools/.snapshots/`）——
我按错的路径找恢复源，找不到。最后 `git checkout --` 恢复。**

### 而第 462 轮那部分工作是对的

**HEAD 的 `PopMartFlow` 里没有这两个 override。我加的是有效的。
这一轮保留：`StoreFlow` 已有虚方法（不能重复声明），`PopMartFlow` 加 override（正确）。**

### 数字

| 度量 | 改后 |
|---|---|
| `StoreFlow` 虚步骤 | **175** |
| 异步覆盖 | **371 / 1547 = 24.0%** |
| 缺失名承载出现次数 | **1303**（原 1523） |
| 套件 | **1815 通过 / 0 失败** |

### 新的缺失榜首（都真缺）

`WriteToAsync` 7 · `WriteRawAsync` 6 · `LoadAsync` 5 · `WriteStartNamespaceDeclarationAsync` 4 ·
`WriteAsyncInternal` 4 · `OverrideAsyncMethod` 4 · `OnLoadedAsync` 4 · `Enumerate` 4 · `DownloadAsync` 4

### 教训

> **这一轮有两个错，而它们方向相反：**
> **① 判据太严（`Async` 后缀）→ **低报**覆盖率。**
> **② 删除动作太宽（锚点延伸到下一个 `/// <summary>`）→ **删坏产品代码**。**
> **两个都不是「想不到」的错 —— 是我在同一个文件上同时用一个过严的判据和一个过宽的锚点。
> 严的判据让我去找不存在的东西；宽的锚点让我删掉了存在的东西。**
"""

BACKLOG_ADD = """

## 判据 — 覆盖率 **20.4% → 24.0%**：匹配漏了 `Async` 后缀（R911，**改两个工具 + 修产品**）

### 根因

**镜像名来自状态机（`d__NN`）→ `ScrapeProduct`（无 `Async`）；C# 方法 → `ScrapeProductAsync`。
`\\bScrapeProduct\\b` 里 `\\b` 在 `t`/`A` 间不成立 → 不命中。**

| 判据 | 命中 | 覆盖率 |
|---|---|---|
| 严格（旧） | 317 | 20.5% |
| **允许 `Async`（新）** | **371** | **24.0%** |

**54 个名字被误判 → R906/R910 的所有排序都虚高。**

### 这一轮做坏的一次

**删重复定义时锚点过宽 → 删掉 6,876 字符含 `GetHomeAsync` → 虚步骤 175→165、四店 CS0115。
`tools/.snapshot-backup` 不存在（真实路径 `tools/.snapshots/`）→ 用 `git checkout --` 恢复。**

### 而第 462 轮的 override 是对的

**HEAD 的 `PopMartFlow` 无这两个 override → 保留。`StoreFlow` 已有虚方法故不重复。**

### 最终数字

**虚步骤 175 · 异步覆盖 371/1547 = 24.0% · 缺失承载 1303（原 1523）· 套件 1815 通过**

**新榜首：`WriteToAsync` 7 · `WriteRawAsync` 6 · `LoadAsync` 5 · `WriteStartNamespaceDeclarationAsync` 4 · `WriteAsyncInternal` 4 · `OverrideAsyncMethod` 4 · `OnLoadedAsync` 4 · `Enumerate` 4 · `DownloadAsync` 4**

| 仍 Unknown | |
|---|---|
| 54 个名字里还有几个真缺 | 需按新判据重排 |
| `Write*` 一族属哪层 | IO/序列化 |

**纪律**：**同一轮里判据过严（低报）与锚点过宽（删坏）可以同时发生 —— 严的让人找不存在的东西，宽的让人删掉存在的东西。**
"""

BLOCKER = """

---

## 335. 覆盖率修到 **24.0%**；以及这一轮删坏文件又恢复的过程

> R911。**改两个工具 + 保留产品改动。** 套件 **1815 通过 / 0 失败 / 0 跳过**。

### 一、根因：`Async` 后缀

**镜像名来自状态机（`d__NN`）→ `ScrapeProduct`（无 `Async`）；C# 是 `ScrapeProductAsync`。
`\\bScrapeProduct\\b` 的 `\\b` 在 `t` 与 `A` 之间不成立 → 不命中。**

| 判据 | 命中 | 覆盖率 |
|---|---|---|
| 严格（旧） | 317 | 20.5% |
| **允许 `Async`（新）** | **371** | **24.0%** |

**54 个名字被误判为缺失 —— R906/R910 的全部排序都因此虚高。**

### 二、这一轮我先做坏了一次

**发现 CS0111 后删重复定义，锚点延伸到下一个 `/// <summary>` → **删掉 6,876 字符，含 `GetHomeAsync`**。
虚步骤 175 → 165，四店 CS0115。**

**而 `tools/.snapshot-backup` 不存在（`snapshot.py` 实际写 `tools/.snapshots/`），按错路径找不到恢复源。
最后 `git checkout -- src/Cybersole.Stores/Flows/StoreFlow.cs` 恢复。**

### 三、而第 462 轮的 override 是对的

**HEAD 的 `PopMartFlow` 里没有这两个 override，所以我加的是真实的。
`StoreFlow` 已有虚方法（不能重复声明），`PopMartFlow` 加 override（正确）—— 保留。**

### 四、最终数字

| 度量 | 值 |
|---|---|
| `StoreFlow` 虚步骤 | **175** |
| 异步覆盖 | **371 / 1547 = 24.0%** |
| 缺失名承载出现次数 | **1303**（原 1523） |
| 套件 | **1815 通过 / 0 失败** |

### 五、新的缺失榜首（都真缺）

`WriteToAsync` 7 · `WriteRawAsync` 6 · `LoadAsync` 5 · `WriteStartNamespaceDeclarationAsync` 4 ·
`WriteAsyncInternal` 4 · `OverrideAsyncMethod` 4 · `OnLoadedAsync` 4 · `Enumerate` 4 · `DownloadAsync` 4

### 六、仍然 Unknown

- **54 个被误判的名字里还有几个真缺**：**Unknown** —— 需按新判据重排后逐个看。
- **`Write*` 一族属哪层**：**Unknown** —— 名字像 IO/序列化。
- **`tools/.snapshots/` 的实际内容**：**Unknown** —— 我一直按 `.snapshot-backup` 找。

### 七、教训

**这一轮有两个错，方向相反：**

**① 判据太严（`Async` 后缀）→ **低报**覆盖率 3.5 个百分点。**
**② 删除锚点太宽（延伸到下一个 `/// <summary>`）→ **删坏产品代码**，丢了 10 个虚方法。**

**两个都不是「想不到」—— 是我在同一个文件上同时用一个过严的判据和一个过宽的锚点。
严的判据让我去找不存在的东西；宽的锚点让我删掉了存在的东西。**

**而恢复靠的是 `git checkout`，不是快照 —— 因为我把快照目录名记错了。
记错一个目录名，就等于没有快照。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R911", BLOCKER)
    ensure(RSTATUS, "R911", BLOCKER)
    ensure(RVERDICT, "第 911 轮", VERDICT)
    ensure(BACKLOG, "R911", BACKLOG_ADD)

    note = (
        "\n## R911 补充 — 覆盖率 20.4% → 24.0%（匹配漏了 Async 后缀）\n\n"
        "根因：镜像名来自状态机 d__NN → ScrapeProduct（无 Async）；C# 是 ScrapeProductAsync；\\bScrapeProduct\\b 不命中。\n"
        "严格 317（20.5%）→ 允许 Async 371（24.0%）。54 个名字被误判 → R906/R910 排序全虚高。\n\n"
        "而这一轮先做坏了一次：删重复定义锚点过宽 → 删 6876 字符含 GetHomeAsync → 虚步骤 175→165、四店 CS0115。"
        "tools/.snapshot-backup 不存在（真实是 tools/.snapshots/）→ 用 git checkout 恢复。\n\n"
        "第 462 轮的 PopMartFlow override 是对的（HEAD 里没有）→ 保留。\n\n"
        "最终：虚步骤 175 · 异步覆盖 371/1547 = 24.0% · 缺失承载 1303（原 1523）· 套件 1815 通过。\n\n"
        "新榜首：WriteToAsync 7 · WriteRawAsync 6 · LoadAsync 5 · WriteStartNamespaceDeclarationAsync 4 · WriteAsyncInternal 4 · OverrideAsyncMethod 4 · OnLoadedAsync 4 · Enumerate 4 · DownloadAsync 4。\n\n"
        "纪律：同一轮里判据过严（低报）与锚点过宽（删坏）可以同时发生。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R911" not in h:
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h + note)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R911"), (RSTATUS, "R911"), (RVERDICT, "第 911 轮"), (BACKLOG, "R911")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R911: coverage is twenty-four percent, because the matcher ignored the Async suffix\n\n"
         "R910 ranked absent names by leverage and put ScrapeProduct at the top, so this round went to add it and got\n"
         " CS0111 for a duplicate definition. The cause is systematic: the image's names come from state-machine types\n"
         " and carry no Async suffix, while C# methods do, so a whole-word test for ScrapeProduct does not match\n"
         " ScrapeProductAsync -- the word boundary falls between the t and the A.\n\n"
         "Allowing the suffix moves coverage from 317 names to 371, twenty point five percent to twenty-four, and\n"
         " fifty-four names had been counted as missing when they were present. Every ranking produced by R906 and R910\n"
         " was inflated by that error.\n\n"
         "This round also broke something on the way. The duplicate definitions had to go, and the anchor I used ran to\n"
         " the next summary comment, which took 6876 characters including GetHomeAsync; the virtual count fell from 175\n"
         " to 165 and four flows failed to compile with CS0115. The snapshot directory I reached for does not exist --\n"
         " snapshot.py writes tools/.snapshots and I looked in tools/.snapshot-backup -- so recovery came from git\n"
         " checkout instead, which restored the file and the count.\n\n"
         "The part of the previous round that was right is kept: PopMartFlow had no override of either method at HEAD,\n"
         " so the two overrides added there are real work, while the duplicate virtuals in StoreFlow were the mistake.\n\n"
         "Final state: 175 virtuals, 371 of 1547 async names, twenty-four percent, absent names carrying 1303\n"
         " occurrences down from 1523, suite green at 1815.\n\n"
         "The new top of the missing list is all genuinely absent: WriteToAsync seven, WriteRawAsync six, LoadAsync\n"
         " five, then four each for WriteStartNamespaceDeclarationAsync, WriteAsyncInternal, OverrideAsyncMethod,\n"
         " OnLoadedAsync, Enumerate and DownloadAsync.\n\n"
         "Unknown: how many of the fifty-four misjudged names are still genuinely absent once the corrected matcher is\n"
         " applied; what layer the Write family belongs to, the names suggesting IO or serialisation; and what\n"
         " tools/.snapshots actually contains, since I had been looking elsewhere.\n\n"
         "The lesson is that two opposite errors can happen in one round on one file: a criterion too strict, which\n"
         " reports absent things that are present, and an anchor too wide, which deletes present things. And recovery\n"
         " depended on git rather than the snapshot, because I had the snapshot directory's name wrong -- misremembering\n"
         " one directory name is the same as having no snapshot.\n\n"
         "Tools and product changed; suite green at 1815."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()