"""Record R880: the task-kind axis, and the doc guard catching the same error a fourth time."""

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
### 任务种类这一层建起来了：**14 + 2**，6 个测试；而文档守卫又一次抓到我（R880）

**R879 说最大的结构缺口是「任务种类这一层在复刻件里几乎没有对应物」。这一轮把它建起来。**

### 新增 `TaskKinds.cs`

| 类型 | 内容 |
|---|---|
| `FlowKind` | **14 个**：Normal · Clear · Signup · AccountRegistration · PopNow · InStore · Draw · DrawCheck · DrawEvent · Exhibit · Raffle · Reservation · Rpc · Tasks |
| `TaskKind` | **2 个**：DailyCheckIn · PopNowView |
| `TaskKindCatalog` | 每个成员 ↔ 镜像名（`StartNormalFlow` …）· `Resolve(imageName)` 往返 |

**每个成员都有基线出处（`recovered_async_methods.txt` 的 `Start*Flow` / `Start*Task` 行）。
没有一个是为了对称而加的 —— 这是 R876/R878 那两轮的直接后果：那里的错，是把相邻当成归属。**

**而 `FlowKind` 与 `TaskKind` 分开，是因为镜像自己的名字就分开：
flow 跑一条结账形状的序列，task 按计划做一件事。合并就重犯 R877 那个
「`storeOfflineDraw` 与 `drawScratch` 看着像一家」的错误 —— 而它们服务不同的东西。**

### 6 个测试

| 用例 | 钉住什么 |
|---|---|
| `ThereAreFourteenFlowKinds` | **14，不是 5** |
| `ThereAreTwoTaskKinds` | 2，且与 flow 分开 |
| `EveryMemberHasAnImageNameAndResolvesBackToItself` | 每个成员都有出处名，且往返一致 |
| `TheImageNamesAreDistinct` | 16 个名字互不重复 |
| `AnUnclaimedNameResolvesToNothing` | **不认得的名字返回 null，不返回「最像的那个」** |
| `TheKindAxisIsNotYetWiredToAnyFlow` | **还没接进任何流程，断言这个缺席** |

**最后一条是刻意的：如果我只写前五条，这个目录看起来像个已完成的功能。
第六条说清它现在只是一张清单 —— 而这正是 R850 「空壳方法」那条教训的形态：
宁可报缺席，不报看起来完整。**

### 而文档守卫第四次抓到我

**`DocsConsistencyTests.TheModuleCountInVerdictMatchesTheCatalogue` 红了。**

**我在 R879 写了「`Registry.cs` 的 **64** 个模块」，而目录实际是 **63**。**

**这个守卫的历史（VERDICT 里自己记着）：R457 · R464 · R813 · **现在**。**
**四次同一个模式：引用旧轮次的数字时顺手写成「N 个模块」。**

**修法不是改那个 64 —— 是承认这个句式本身就是陷阱。
守卫扫的是 `(\\d+)\\s*(?:个模块|modules)` 且 `n >= 20`，它分不清
「目录有 N 个模块」这个断言和「某一轮处理了 N 个模块」这个事实陈述。**

**所以正确做法是：**在 VERDICT 里不写「N 个模块」，写「模块」或直接引 `METRICS.md`。****

**这一轮我只把 64 改成 63（四处文档）。下次该改成不带数字的说法。**
"""

if "任务种类这一层建起来了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R880 appended")

BLOCKER = """

---

## 304. 任务种类这一层建起来了：**14 + 2**；而文档守卫第四次抓到我

> R880。**改产品代码。** 套件 **1779 通过 / 0 失败 / 0 跳过**（原 1773 + 新 6）。

### 一、`TaskKinds.cs`

| 类型 | 内容 |
|---|---|
| `FlowKind` | **14**：Normal · Clear · Signup · AccountRegistration · PopNow · InStore · Draw · DrawCheck · DrawEvent · Exhibit · Raffle · Reservation · Rpc · Tasks |
| `TaskKind` | **2**：DailyCheckIn · PopNowView |
| `TaskKindCatalog` | 成员 ↔ 镜像名 · `Resolve(imageName)` 往返 |

**每个成员都有基线出处。没有一个是为对称而加的。**

**`FlowKind` 与 `TaskKind` 分开，因为镜像自己的名字分开：flow 跑一条结账形状的序列，
task 按计划做一件事。合并就重犯 R877 那个「`storeOfflineDraw` 与 `drawScratch` 看着像一家」——
而它们服务不同的东西。**

### 二、六个测试里最要紧的是第六条

| 用例 | 钉住 |
|---|---|
| `ThereAreFourteenFlowKinds` | **14 不是 5** |
| `ThereAreTwoTaskKinds` | 2，与 flow 分开 |
| `EveryMemberHasAnImageNameAndResolvesBackToItself` | 每个都有出处名且往返一致 |
| `TheImageNamesAreDistinct` | 16 个名字互不重复 |
| `AnUnclaimedNameResolvesToNothing` | **不认得的返回 null，不返回「最像的」** |
| **`TheKindAxisIsNotYetWiredToAnyFlow`** | **还没接进任何流程，断言这个缺席** |

**只写前五条，这个目录看起来像个已完成的功能。第六条说清它现在只是一张清单 ——
R850「空壳方法」那条教训的形态：宁可报缺席，不报看起来完整。**

### 三、文档守卫第四次抓到我 —— 而这次该改的是句式不是数字

**`TheModuleCountInVerdictMatchesTheCatalogue` 红：我写了「`Registry.cs` 的 **64** 个模块」，实际 **63**。**

**守卫历史（VERDICT 自己记着）：R457 · R464 · R813 · R880。四次同一模式。**

**它扫 `(\\d+)\\s*(?:个模块|modules)` 且 `n >= 20`，**分不清**
**「目录有 N 个模块」（断言）** 与 **「某一轮处理了 N 个模块」（事实陈述）**。**

**所以真正的修法不是把 64 改 63 —— 是**在 VERDICT 里不写「N 个模块」这个句式**，
改成「模块」或直接引 `METRICS.md`。**

**本轮只做了前半（64→63，四处文档）。后半是下一轮该做的。**

### 四、这一层建起来之后，优先级 ① 的图景变了

**之前：`StepSequence` 3 条（Nike / PopMart / JohnLewis），没有任务种类概念。
之后：14 个种类有名有出处，但**没有任何一个接到流程上**（第六条测试钉着）。**

**所以下一步是那张映射表：`FlowKind × Store → 哪个 StoreFlow`。
而它需要的证据是「某个站的某个 `Start*Flow` 存在」——
那正是 R857 那 5 条 `Start*Flow` 在 `0x14337bdc4` 的形态。**

### 五、验证

```
python tools\\snapshot.py                     -> 20261116-222059, 292 files
D:\\tools\\dotnet8\\dotnet.exe build ...        -> 0 错误
test --filter TaskKindTests                  -> 6 通过 / 0 失败
test 全量（首跑）                             -> 1778 通过 / 1 失败
  失败: TheModuleCountInVerdictMatchesTheCatalogue（catalogue: 63, claims: 63 和 64）
修 4 处「64 个模块」-> 63
python tools\\metrics_report.py               -> 1779 通过 / 0 失败 / 0 跳过
```

### 六、仍然 Unknown

- **`FlowKind` 怎么接到 `StoreFlow`**：**Unknown** ——
  **需要「某个站有哪些 `Start*Flow`」的证据，而目前只有 R857 那 5 条（一个代码区）。**
- **14 个种类是否都能被某个站支持**：**Unknown** ——
  **有的种类可能只有一个站有（如 `PopNow` 之于 PopMart）。**
- **`Rpc` 这个种类是什么**：**Unknown** —— 名字是全部证据；`_rpc*` 字段（R876）暗示与支付/运费有关，
  **但那是 Inference。**

### 七、教训

**这一轮做了两件事：建了一层，以及被自己的守卫抓住一次。**

**建层这件事我能掌控：名字全有出处、划分有镜像依据、缺席有测试钉着。**

**而被抓那件事说明：我写文档时仍在用「N 个模块」这个句式，而它是守卫的陷阱。
第四次了，而我前三次的修法都是「把数字改对」。**

**改数字只能撑到下一次；改句式才能让它不再红。
这是「修症状」与「修成因」的区别 —— 而我在 R764 那轮就写过这条，
当时说的是「诊断文案要写对因」。这次轮到我自己。**
"""

VERDICT = """

---

## 第 880 轮：任务种类这一层建起来了 —— 14 + 2，六个测试

### `TaskKinds.cs`

| 类型 | 内容 |
|---|---|
| `FlowKind` | **14**：Normal · Clear · Signup · AccountRegistration · PopNow · InStore · Draw · DrawCheck · DrawEvent · Exhibit · Raffle · Reservation · Rpc · Tasks |
| `TaskKind` | **2**：DailyCheckIn · PopNowView |
| `TaskKindCatalog` | 成员 ↔ 镜像名 · `Resolve()` 往返 |

**每个成员都有基线出处（`recovered_async_methods.txt` 的 `Start*Flow` / `Start*Task` 行）。没有为对称而加的。**

**`FlowKind` 与 `TaskKind` 分开，因为镜像自己的名字分开 —— 合并会重犯 R877 那个
「`storeOfflineDraw` 与 `drawScratch` 看着像一家」的错误。**

### 六个测试里最要紧的是第六条

| 用例 | 钉住 |
|---|---|
| `ThereAreFourteenFlowKinds` | **14 不是 5** |
| `ThereAreTwoTaskKinds` | 2，与 flow 分开 |
| `EveryMemberHasAnImageNameAndResolvesBackToItself` | 出处名 + 往返一致 |
| `TheImageNamesAreDistinct` | 16 个名字互不重复 |
| `AnUnclaimedNameResolvesToNothing` | **不认得的返回 null，不返回「最像的」** |
| **`TheKindAxisIsNotYetWiredToAnyFlow`** | **还没接进任何流程，断言这个缺席** |

> **只写前五条，这个目录看起来像个已完成的功能。第六条说清它现在只是一张清单 —— 宁可报缺席，不报看起来完整。**

### 文档守卫第四次抓到我

**`TheModuleCountInVerdictMatchesTheCatalogue` 红：我写「**64** 个模块」，实际 **63**。**

**历史：R457 · R464 · R813 · R880。四次同一模式。**

**它分不清「目录有 N 个模块」（断言）与「某轮处理了 N 个模块」（事实）。
所以真正的修法不是改数字 —— 是**不写「N 个模块」这个句式**。**

**本轮只做了前半（64→63，四处）。后半是下一轮该做的。**

### 优先级 ① 的图景变了

**之前：3 条 `StepSequence`，无任务种类概念。之后：14 个种类有名有出处，但**一个都没接到流程上**（第六条钉着）。**

**下一步是映射表 `FlowKind × Store → StoreFlow`，需要的证据是「某站的某 `Start*Flow` 存在」。**

### 验证

```
snapshot 20261116-222059 · build 0 错误 · TaskKindTests 6 通过
全量首跑 1778/1 失败（catalogue: 63, claims: 63 和 64）→ 修 4 处 → 1779 通过 / 0 失败
```

### 仍然 Unknown

**`FlowKind` 怎么接到 `StoreFlow`**（需「某站有哪些 `Start*Flow`」的证据，目前只有 R857 那 5 条）·
**14 个种类是否都有站支持** · **`Rpc` 是什么**（名字是全部证据）

### 教训

> **改数字只能撑到下一次；改句式才能让它不再红。**
> **这是「修症状」与「修成因」的区别 —— 而我在 R764 那轮就写过这条，当时说的是「诊断文案要写对因」。这次轮到我自己。**
"""

BACKLOG_ADD = """

## 优先级 ① — 任务种类这一层建起来了（R880，**已改产品代码**）

### `TaskKinds.cs`：14 + 2

| 类型 | 内容 |
|---|---|
| `FlowKind` | **14**：Normal · Clear · Signup · AccountRegistration · PopNow · InStore · Draw · DrawCheck · DrawEvent · Exhibit · Raffle · Reservation · Rpc · Tasks |
| `TaskKind` | **2**：DailyCheckIn · PopNowView |
| `TaskKindCatalog` | 成员 ↔ `Start*Flow`/`Start*Task` 名 · `Resolve()` 往返 |

**每个成员都有基线出处；`FlowKind`/`TaskKind` 分开（镜像名字分开，合并会重犯 R877 的错误）。**

### 六测试

**14 / 2 / 出处名+往返 / 16 名互斥 / 不认识返回 null / **`TheKindAxisIsNotYetWiredToAnyFlow`**（断言它还没接进流程）。**

**套件 1779 通过 / 0 失败（原 1773 + 6）。**

### 文档守卫第四次抓到我

**`TheModuleCountInVerdictMatchesTheCatalogue`：写「64 个模块」，实际 63。历史 R457 · R464 · R813 · R880。**
**它分不清「目录有 N 个模块」（断言）与「某轮处理 N 个模块」（事实）→ **真正的修法是别写这个句式**。**
**本轮只把 64→63（四处），**下一轮该改成不带数字的说法**。**

### 下一步

**`FlowKind × Store → StoreFlow` 映射表**；需要「某站的某 `Start*Flow` 存在」的证据（R857 只有 5 条，一个代码区）。

| 仍 Unknown | |
|---|---|
| `FlowKind` 怎么接 `StoreFlow` | 缺「某站有哪些 Start*Flow」证据 |
| 14 种是否都有站支持 | 有的可能只一个站有 |
| `Rpc` 是什么 | 名字是全部证据 |

**纪律**：**改数字撑到下一次，改句式才不再红 —— R764 写过这条，这次轮到自己。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R880", BLOCKER)
    ensure(RSTATUS, "R880", BLOCKER)
    ensure(RVERDICT, "第 880 轮", VERDICT)
    ensure(BACKLOG, "R880", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R880" not in h:
        h += ("\n## R880 补充 — 任务种类这一层建起来了（**已改产品代码**）：14 + 2\n\n"
              "**新增 `src/Cybersole.Stores/Flows/TaskKinds.cs`**：`FlowKind` 14 个 · `TaskKind` 2 个 · `TaskKindCatalog`（成员↔`Start*Flow` 名 + `Resolve()` 往返）。"
              "**每个成员都有基线出处，没有为对称而加的。**\n"
              "**六测试**：14 / 2 / 出处名+往返 / 16 名互斥 / 不认识返回 null / **`TheKindAxisIsNotYetWiredToAnyFlow`（断言还没接进流程）**。\n"
              "**套件 1779 通过 / 0 失败（原 1773 + 6）。**\n"
              "**文档守卫第四次抓到我**：写「64 个模块」实际 63（历史 R457·R464·R813·R880）。**已修四处 → 63；下一轮改成不带数字的说法。**\n"
              "**下一步：`FlowKind × Store → StoreFlow` 映射表**，需「某站的某 `Start*Flow` 存在」的证据。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R880"), (RSTATUS, "R880"), (RVERDICT, "第 880 轮"), (BACKLOG, "R880")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R880: the task-kind axis exists, fourteen and two, every member with a baseline line\n\n"
         "R879 named the largest structural gap: the replica has sixty-odd store modules and nothing corresponding to\n"
         " the task-kind axis the image's top layer is built on. This round builds it as data rather than behaviour.\n\n"
         "TaskKinds.cs holds FlowKind with fourteen members, TaskKind with two, and a catalog mapping each to the image\n"
         " name it came from plus a Resolve that goes the other way. Every member traces to a line in\n"
         " recovered_async_methods.txt; none was added for symmetry. That constraint is a direct consequence of R876,\n"
         " which attributed a sequence to the nearest capitalised string, and R878, which refuted it with arithmetic.\n"
         " The rule now is that a member exists only if a baseline line names it.\n\n"
         "FlowKind and TaskKind stay separate because the image's own names separate them: a flow runs a checkout-shaped\n"
         " sequence, a task does one thing on a schedule. Merging would repeat the error R877 resolved, where\n"
         " storeOfflineDraw and drawScratch looked like one endpoint family and turned out to serve different things.\n\n"
         "Six tests. The last one matters most: it asserts that no FlowKind is wired to any StoreFlow yet. With only the\n"
         " first five, the catalog would look like an integrated feature rather than a list; the sixth says plainly that\n"
         " it is a list. That is R850's lesson about shell methods, applied before the shell is mistaken for something.\n\n"
         "The docs guard caught me a fourth time. TheModuleCountInVerdictMatchesTheCatalogue went red because I wrote\n"
         " that Registry has sixty-four modules and the catalogue says sixty-three. The guard's own history in\n"
         " VERDICT.md records R457, R464 and R813 before this one, all the same shape: quoting an earlier round's\n"
         " number in the form 'N modules'. It scans for the pattern and cannot tell a claim about the catalogue's size\n"
         " from a statement that some round handled that many modules.\n\n"
         "So the fix is not the digit. Changing sixty-four to sixty-three holds until the next module lands; the phrase\n"
         " itself is the trap, and the durable repair is to stop writing 'N modules' in the verdict at all. This round\n"
         " only did the digit, in four documents, and the phrase change is next round's work. Repairing a symptom and\n"
         " repairing a cause differ, which is a thing I wrote down at R764 about diagnostic messages and have now had\n"
         " applied to me.\n\n"
         "Unknown: how FlowKind attaches to StoreFlow, which needs evidence of which Start-prefixed flows a given store\n"
         " has and currently rests on the five R857 found in one code region; whether all fourteen kinds are supported by\n"
         " any store, since some may belong to exactly one, as PopNow appears to belong to Pop Mart; and what Rpc denotes,\n"
         " where the name is the whole of the evidence and the _rpc fields R876 found suggest payment or freight without\n"
         " proving it.\n\n"
         "Suite green at 1779, the previous 1773 plus six."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
