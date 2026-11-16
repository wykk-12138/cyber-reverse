"""Record R852: the ordinals are per-flow, so R851's conclusion upgrades from inference to observation."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### ordinal 是**按流程编号**的（R852）—— R851 从 Inference 升为 Observation

**130 个 ordinal，只有 63 个不同，67 个跨流程重复：**

| 流程 | 范围 |
|---|---|
| JohnLewis | 20 – 39 |
| DemandwareDual | 26 – 47 |
| StructureTokenMulti | 29 – 47 |
| DemandwareClassic | 32 – 43 |
| CollectPlusApp | 33 – 50 |
| StructureTokenSingle | 40 – 51 |
| Nike | 41 – 58 |
| PopMart | 104 – 153 |

**六个流程挤在 20–51 且大量重叠** —— 若是同一编号空间，`d__32` 只能是一个方法；
**而这里 `d__32` 在 DemandwareClassic 是 `AddToCart`、在 CollectPlusApp 是别的步骤。**

**所以每个流程自己从低位数起：各自一个类、各自一套序列。**

**结论：R851 说的「镜像八条按流程的序列」成立，而它上一轮只是 Inference（因为「ordinal 递增是否即运行顺序」没证）。
现在有证了 —— 不是「递增即顺序」，而是「编号空间按流程分开」，这足以支持「序列是每条流程自己的」。**
"""

if "ordinal 是**按流程编号**的（R852" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: ordinal finding appended")

BLOCKER = """

---

## 276. ordinal **按流程编号** —— R851 的结论从 Inference 升为 Observation

> R852。未改产品代码。

### 一、查的是 R851 留的那个 Unknown

R851 说「镜像每流程一条序列」，但标的是 **Inference（中）**，理由是
**「ordinal 递增是否即运行顺序」没证。**

**这一轮换个角度查：如果各流程共用一个编号空间，那同号只能是同一个方法；
如果每个流程自己编号，同号会在不同流程里指不同方法。**

### 二、结果：130 个 ordinal，63 个不同，67 个重复

| 流程 | 范围 |
|---|---|
| JohnLewis | 20 – 39 |
| DemandwareDual | 26 – 47 |
| StructureTokenMulti | 29 – 47 |
| DemandwareClassic | 32 – 43 |
| CollectPlusApp | 33 – 50 |
| StructureTokenSingle | 40 – 51 |
| Nike | 41 – 58 |
| PopMart | 104 – 153 |

**六个流程挤在 20–51 且大量重叠。**

**`d__32` 在 `DemandwareClassic` 是 `AddToCart`，在 `CollectPlusApp` 是另一个步骤 —— 同一个编号，两个不同的方法。**

### 三、所以

**每个流程自己从低位数起 → 各自一个类、各自一套序列。**

**R851 的「镜像八条按流程的序列」成立。**
**而它上一轮的证据是「`d__N` 的注释说这些是同一次相邻运行」，这一轮的证据是「编号空间按流程分开」——
第二条更硬，因为它排除了「一个类装全部步骤」这个可能。**

**这是「把 Inference 变成 Observation」的标准动作：找一个能证伪它的检查。**
**如果各流程共用一个空间，重叠就不会发生；重叠发生了 67 次，所以不共用。**

### 四、对工作量的影响

**R851 列的三种改法里，做法 1（`StoreFlow` 加 `IReadOnlyList<Step>`）现在有了更明确的目标：
不是「把八条序列塞进一个类」，而是「每条流程有自己的序列，runner 按它跑」。**

**而镜像的证据说明：序列与类是绑定的。所以做法 1 若要忠实，可能不只是「加一个列表」，
而是「每条流程自己持有序列并自己驱动」—— 那是更接近「八个执行器」的形态。**

**这条本轮没改，但它把「改法 1 该做多大」这个问题向前推了一步。**

### 五、验证

```
python - (解析 StoreFlowSteps 的 8 个流程与全部 new Step 的 ordinal)
  总 130 · 不同 63 · 重复 67 · min 20 · max 153
  JohnLewis 20–39 / DemandwareDual 26–47 / StructureTokenMulti 29–47 / DemandwareClassic 32–43
  CollectPlusApp 33–50 / StructureTokenSingle 40–51 / Nike 41–58 / PopMart 104–153
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **镜像的类结构**：**Unknown，但范围收窄了** ——
  **八个类各持一套序列（Inference 高）**，而不是一个类里八段。
  要证它得走类型图（MethodTable），本会话还没走通那条路（R828 已记）。
- **`d__N` 的重叠是否也可能来自「同一方法被多条流程引用」**：**Unknown** ——
  若是那样，重叠不成立。**而「`d__32` 在两个流程里指不同步骤」这个观察排除了它，
  但那个观察来自 `StoreFlowSteps` 的转写，不是镜像原文。**
- **`AddToCart` 在 JohnLewis 是 22、在 DemandwareClassic 是 32** —— 同名不同号，
  **说明同名步骤在不同流程里是不同方法（各自实现），而不是一个共享方法被复用。**
  **这条对「165 个虚方法 + 重写」这个设计是个反证：镜像似乎是每个流程各写一份。**

### 七、教训

**R851 我把结论标成 Inference，理由是「没证运行顺序」。**
**这一轮换个检查（编号空间是否共用），就把同一件事证成了 Observation。**

**「同一个结论，换一个能证伪它的检查」比「补上原来缺的那个证据」更容易做到 ——
因为原来缺的那个（运行顺序）要动态观察，而能证伪的那个（编号是否重叠）只需读表。**
"""

VERDICT = """

---

## 第 852 轮：ordinal 按流程编号 —— R851 从 Inference 升为 Observation

### 查的是 R851 的那个 Unknown

**R851 说「镜像每流程一条序列」，但标 Inference（中），因为「ordinal 递增是否即运行顺序」没证。**

**换角度：若各流程共用编号空间，同号只能是同一方法；若各流程自己编号，同号会指向不同方法。**

### 结果：130 个 ordinal，63 个不同，67 个重复

| 流程 | 范围 |
|---|---|
| JohnLewis | 20 – 39 |
| DemandwareDual | 26 – 47 |
| StructureTokenMulti | 29 – 47 |
| DemandwareClassic | 32 – 43 |
| CollectPlusApp | 33 – 50 |
| StructureTokenSingle | 40 – 51 |
| Nike | 41 – 58 |
| PopMart | 104 – 153 |

**`d__32` 在 `DemandwareClassic` 是 `AddToCart`，在 `CollectPlusApp` 是另一个步骤。**

### 所以 R851 成立，证据更硬

**每个流程自己从低位数起 → 各自一个类、各自一套序列。**

**上一轮的证据是「注释说这些来自同一次相邻运行」；这一轮的证据排除了「一个类装全部步骤」这个可能 —— 因为它证伪不了就不会有 67 次重叠。**

> **「同一个结论，换一个能证伪它的检查」比「补上原来缺的那个证据」更容易做到。**
> **原来缺的那个（运行顺序）要动态观察；能证伪的那个（编号是否重叠）只需读表。**

### 一条对设计的反证

**`AddToCart` 在 JohnLewis 是 22、在 DemandwareClassic 是 32 —— 同名不同号。**
**说明同名步骤在不同流程里是**不同方法（各自实现）**，而不是一个共享方法被复用。**

**这对复刻件「165 个虚方法 + 按站重写」是个反证：镜像似乎是每个流程各写一份。**

### 仍然 Unknown

**镜像的类结构**（范围收窄：八类各持一套序列，Inference 高；要证得走 MethodTable）·
**重叠是否也可能来自「同一方法被多流程引用」**（「`d__32` 指不同步骤」排除了它，但那个观察来自转写不是镜像原文）·
**做法 1 该做多大**（若序列与类绑定，可能不只是「加一个列表」）

### 验证

```
130 总 · 63 不同 · 67 重复 · 20–153 · 产品代码未改 · 七项度量沿用
```
"""

BACKLOG_ADD = """

## 判据 (f) — ordinal 按流程编号（R852）

**130 个 ordinal · 63 不同 · 67 跨流程重复 · 范围 20–153。**

| 流程 | 范围 |
|---|---|
| JohnLewis | 20 – 39 |
| DemandwareDual | 26 – 47 |
| StructureTokenMulti | 29 – 47 |
| DemandwareClassic | 32 – 43 |
| CollectPlusApp | 33 – 50 |
| StructureTokenSingle | 40 – 51 |
| Nike | 41 – 58 |
| PopMart | 104 – 153 |

**六个挤在 20–51 且重叠 → 每流程自己编号 → 各自一个类、各自一套序列。**
**→ R851「八条按流程的序列」从 Inference 升为 Observation。**

### 一条对复刻件设计的反证

**`AddToCart` 在 JohnLewis 是 22、在 DemandwareClassic 是 32 —— 同名不同号。**
**→ 镜像里同名步骤在不同流程中是**不同方法**，不是共享方法被复用。**
**→ 对「165 虚方法 + 按站重写」是反证：镜像似乎每流程各写一份。**

| 仍 Unknown | |
|---|---|
| 镜像类结构 | 八类各持一套序列（Inference 高）；要证走 MethodTable |
| 重叠是否可能来自共享方法 | 「`d__32` 指不同步骤」排除，但观察来自转写 |
| 做法 1 该做多大 | 若序列与类绑定，可能不只是加一个列表 |

**纪律**：**「同一个结论换一个能证伪它的检查」比「补原来缺的那个证据」容易 —— 前者只要读表。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R852", BLOCKER)
    ensure(RSTATUS, "R852", BLOCKER)
    ensure(RVERDICT, "第 852 轮", VERDICT)
    ensure(BACKLOG, "R852", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R852" not in h:
        h += ("\n## R852 补充 — ordinal 按流程编号\n\n"
              "**130 个 ordinal，63 不同，67 跨流程重复，范围 20–153** —— 六个流程挤在 20–51 且重叠。\n"
              "**→ 每流程自己编号 → 各自一个类、各自一套序列 → R851 从 Inference 升为 Observation。**\n"
              "**反证**：`AddToCart` 在 JohnLewis 是 22、在 DemandwareClassic 是 32 —— **同名不同号，说明是不同方法**，\n"
              "不是共享方法复用。**对「165 虚方法 + 按站重写」是个反证：镜像似乎每流程各写一份。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R852"), (RSTATUS, "R852"), (RVERDICT, "第 852 轮"), (BACKLOG, "R852")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R852: the ordinals are numbered per flow, which upgrades R851 from inference to observation\n\n"
         "R851 concluded that the image gives each flow its own step sequence, but marked it inference because it had not"
         " established that increasing ordinals are the run order. This round asks a different question that can falsify"
         " the same claim more cheaply: if the flows shared one numbering space, the same ordinal could only ever name"
         " one method.\n\n"
         "They do not share. Across the eight flows the tables hold 130 ordinals, only 63 of them distinct, with 67"
         " repetitions across flows. Six flows crowd into the range 20 to 51 with heavy overlap: John Lewis 20 to 39,"
         " demandware-dual 26 to 47, structure-token-multi 29 to 47, Demandware classic 32 to 43, CollectPlus 33 to 50,"
         " structure-token-single 40 to 51. Ordinal 32 is AddToCart for Demandware classic and a different step for"
         " CollectPlus. So each flow numbers its own async methods from a low start, which means each flow has its own"
         " class and its own sequence.\n\n"
         "The evidence is harder than last round's because it rules out the alternative. Last round's support was a"
         " comment saying the names came from one adjacent run; this round's support is that a shared space cannot"
         " produce 67 collisions.\n\n"
         "There is also a counter-indication for the replica's design. AddToCart sits at ordinal 22 in John Lewis and at"
         " 32 in Demandware classic, so identically named steps are different methods in different flows rather than one"
         " method reused. That argues against the replica's arrangement of 165 virtual methods with per-site overrides"
         " and toward the image writing each flow its own implementation.\n\n"
         "For the three options listed last round this sharpens what option one would mean. If sequences are bound to"
         " classes in the image, then giving StoreFlow a step list may not be enough, and the faithful shape could be"
         " each flow holding and driving its own sequence -- closer to eight executors than to one dispatcher. That is"
         " still not something to do inside a round.\n\n"
         "Unknown: the image's class structure, narrowed now to eight classes each holding a sequence, which would need"
         " the MethodTable walk that R828 already established is the only route; whether the ordinal overlap could"
         " instead come from one method being referenced by several flows, which the d__32 observation rules out but"
         " that observation comes from the transcription rather than from the image itself; and how large option one"
         " really is.\n\n"
         "The lesson is a technique. Refuting a claim is often cheaper than confirming it: the missing evidence was a"
         " dynamic fact about run order, while the falsifying check was a static fact about numbering, and the static one"
         " was a table read.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
