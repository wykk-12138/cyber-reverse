"""Record R868: the sequence mechanism is built, tested, and its first act is to measure the gap at 0/24."""

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
### 序列机制已建成，而它量出的第一个数是 **0 / 24**（R868）

**改了产品代码（R866 之后第一次）。三处：**

| 文件 | 改了什么 |
|---|---|
| `StoreFlow.cs` | `StepSequence` 虚属性（默认空）+ `StepDispatch` 派发表（反射，165 条）+ `RunStepNamedAsync` |
| `PopMartFlow.cs` | `override StepSequence => StoreFlowSteps.PopMart.Names` |
| `tests/.../FlowSequenceTests.cs` | 新建，7 个用例 |

**`StepSequence` 默认空 → 其余 25 个流程行为不变（有测试钉住）。**

### 派发表怎么建的：一个踩坑和一个更正

**第一版按**具体流程类型**绑定（`flowType.GetMethods()`），测试 3 失败：**

> `ArgumentException: Cannot bind to the target method because its signature is not compatible with that of the delegate type.`

**原因：`Func<StoreFlow, …>` 的第一参数是基类，而重写在 `PopMartFlow` 上声明 —— 运行时拒绝。**

**改法：按 `typeof(StoreFlow)` 的声明绑定（`DeclaredOnly`），**虚分派自然走到重写**。
**副作用是正向的：派发表对所有流程**是同一张**，`Lazy` 一次构建，不需要按类型缓存。**

### 机制量出的第一个数

```
map.Count      = 165
sequence.Count =  24
implementable  =   0
```

**Pop Mart 那 24 个镜像步骤名与 `StoreFlow` 的 165 个方法名**零交集**。**

**这个数和 R844 的「22/130」是同一件事的两种量法，而这一次是同一层里的比较：
镜像列出的步骤 ↔ 复刻件真能调的方法。R844 那个是跨层的（步骤名 vs 通用序列名），所以它需要三条免责声明；
这一个不需要。**

### 测试（7 个，全过）

| 用例 | 钉住什么 |
|---|---|
| `AFlowWithoutItsOwnSequenceReportsNone` | 不重写的流程序列为空 → 其余 25 个流程行为不变 |
| `PopMartDeclaresTheImagesTwentyFourSteps` | **断言 24 而非前缀** —— 删条目不能悄悄通过 |
| `PopMartSequenceFollowsTheImagesOrdinals` | `GetOrders`(104) 在 `EnterReservation`(153) 之前 |
| `DispatchReachesBothOverriddenAndInheritedSteps` | 重写（`GetHome`）与继承（`SubmitBillingAddress`/`Init`）都能派发 |
| `DispatchIsNotSilentlyEmpty` | `Count >= 150` —— 反射查询崩了会被抓住 |
| `NoPopMartImageStepIsDispatchableYet` | **`map=165` · `sequence=24` · `implementable=0`** |
| `TheTableIsNotEmptyWhichIsWhyTheZeroAboveMeansDisjoint` | 表非空，所以上面的 0 意味着「两个名字集不相交」而不是「表坏了」 |

**最后两个是一对：一个量缺口，一个证明前一个的 0 不是因为表空。**
"""

if "序列机制已建成，而它量出的第一个数是 **0 / 24**（R868" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: mechanism appended")

BLOCKER = """

---

## 292. **序列机制建成**；它量出的第一个数是 **0 / 24**

> R868。**改了产品代码。** 套件 **1773 通过 / 0 失败 / 0 跳过**（原 1766 + 新 7）。

### 一、改了三处

| 文件 | 改了什么 |
|---|---|
| `StoreFlow.cs` | `StepSequence` 虚属性（默认 `Array.Empty`）+ `StepDispatch` 派发表 + `RunStepNamedAsync` |
| `PopMartFlow.cs` | `override StepSequence => StoreFlowSteps.PopMart.Names` |
| `tests/.../FlowSequenceTests.cs` | 新建，7 个用例 |

**`StepSequence` 默认空 → runner 与其余 25 个流程行为不变。**

### 二、第一版错了，错误值得记

**按**具体流程类型**绑定（`flowType.GetMethods()`）→ 3 个测试失败：**

```
ArgumentException : Cannot bind to the target method because its signature is not compatible
                    with that of the delegate type.
```

**原因：`Func<StoreFlow, FlowContext, CancellationToken, Task<StepOutcome>>` 的第一参数是**基类**，
而 `PopMartFlow` 上的重写方法声明在**派生类**上 —— 运行时拒绝把基类参数绑到派生声明。**

**改法：按 `typeof(StoreFlow)` + `DeclaredOnly` 绑定基类声明，**靠虚分派到达重写**。**

**副作用是正向的：派发表对所有流程是**同一张**，`Lazy` 一次构建。第一版按类型缓存反而是多余的设计。**

### 三、机制量出的数

```
map.Count      = 165
sequence.Count =  24
implementable  =   0
```

**那 24 个镜像步骤名与 165 个方法名**零交集**。Pop Mart 的抽签/展览/预约一个都没实现 —— 这与 R849/R850 一致
（端点全在、3 个证据够、11 个缺请求形状），而现在是**一个可复算的数**，不是一句描述。**

**与 R844 的「22/130」的关系：同一件事的两种量法。R844 那个是跨层的（步骤名 vs 通用序列名），
需要三条免责声明；这一个是同层的（步骤名 ↔ 真能调的方法），不需要。**

### 四、7 个测试里最要紧的两个

| 用例 | 钉住什么 |
|---|---|
| `NoPopMartImageStepIsDispatchableYet` | **`165 / 24 / 0` 三个数一起断言** |
| `TheTableIsNotEmptyWhichIsWhyTheZeroAboveMeansDisjoint` | **表非空 → 上面的 0 意味着「不相交」而不是「表坏了」** |

**这两个是一对：一个量缺口，一个证明前一个的 0 不是假象。**
**单看第一个，表坏了也会得到 0；加上第二个，0 才有意义。**

### 五、还没做的

- **其余 7 个流程的 `StepSequence` 重写** —— 8 处机械，本轮只做了 PopMart（先证明机制）
- **runner 按 `StepSequence` 跑的分支** —— R867 的第 3 项，本轮没动
- **写任何抽签步骤** —— 现在有了位置，但那 11 个仍缺请求形状（R850）

**所以「Pop Mart 的抽签能跑」还没成立。成立的是：位置有了，缺口被量成了 0/24，且这个数会随实现上升。**

### 六、验证

```
cd replica && python tools\\snapshot.py            -> 20261116-214544, 292 files
D:\\tools\\dotnet8\\dotnet.exe build src\\Cybersole.Stores\\...   -> 0 错误
D:\\tools\\dotnet8\\dotnet.exe test ... --filter FlowSequenceTests -> 7 通过 / 0 失败
python tools\\metrics_report.py                     -> 完整套件 exit 0  1773 通过 / 0 失败 / 0 跳过
    wrote docs\\METRICS.md
新用例实测: map=165  sequence=24  implementable=0
```

### 七、仍然 Unknown

- **那 11 个缺请求形状的抽签步骤**：**Unknown**（R850 的边界没变）——
  **但现在它们有位置了，写一个就能把 `implementable` 从 0 变成 1，可复算。**
- **runner 该怎么按序列跑**：**Unknown** ——
  **第 3 项没做。而做的时候要决定：序列里某步失败，是继续还是中止？镜像的行为没查。**
- **其余 7 个流程的 `Flow.Store` 是否都等于流程类的 `Id`**：**只核了 popmart**（是）。

### 八、教训

**R866/R867 我把这件事描述成「结构改造」，听起来像动大手术。实际动手是：
一处虚属性、一张反射表、一个 `override`、七个测试。**

**而其中唯一真正难的地方，是一个我事先没想到的运行时约束（开放实例委托绑不上派生声明）。
那类约束在纸上永远看不出来 —— 只能撞。**

**所以「先估影响面」是对的，但估完就该动手；再估一轮也估不出那个 `ArgumentException`。**
"""

VERDICT = """

---

## 第 868 轮：序列机制建成，它量出的第一个数是 0 / 24

### 改了产品代码（R866 之后第一次）

| 文件 | 改了什么 |
|---|---|
| `StoreFlow.cs` | `StepSequence` 虚属性（默认空）+ `StepDispatch` 派发表（165 条）+ `RunStepNamedAsync` |
| `PopMartFlow.cs` | `override StepSequence => StoreFlowSteps.PopMart.Names` |
| `FlowSequenceTests.cs` | 新建，7 用例 |

**套件 1773 通过 / 0 失败 / 0 跳过**（原 1766 + 新 7）。

### 第一版错了 —— 而错值得记

**按**具体流程类型**绑定 → 3 个测试失败：**

```
ArgumentException : Cannot bind to the target method because its signature is not compatible
                    with that of the delegate type.
```

**`Func<StoreFlow, …>` 第一参数是基类，而重写声明在派生类上 —— 运行时拒绝。**

**改法：按 `typeof(StoreFlow)` + `DeclaredOnly` 绑基类声明，靠**虚分派**到达重写。**
**副作用正向：派发表对所有流程是同一张，`Lazy` 一次构建 —— 第一版按类型缓存是多余设计。**

### 机制量出的数

```
map = 165   sequence = 24   implementable = 0
```

**那 24 个镜像步骤名与 165 个方法名零交集 —— Pop Mart 的抽签/展览/预约一个都没实现，
而现在是**一个可复算的数**，不是一句描述。**

**与 R844 的「22/130」是同一件事的两种量法：R844 是跨层的（要三条免责声明），这一个是同层的（不需要）。**

### 7 个测试里最要紧的一对

| 用例 | 钉住什么 |
|---|---|
| `NoPopMartImageStepIsDispatchableYet` | **165 / 24 / 0 三个数一起断言** |
| `TheTableIsNotEmptyWhichIsWhyTheZeroAboveMeansDisjoint` | **表非空 → 0 意味着「不相交」而非「表坏了」** |

> **单看第一个，表坏了也会得到 0；加上第二个，0 才有意义。**

### 还没做的

**其余 7 个流程的 `StepSequence`**（8 处机械，只做了 PopMart 以先证机制）·
**runner 按序列跑的分支**（R867 第 3 项）· **写任何抽签步骤**（位置有了，11 个仍缺请求形状）

> **「Pop Mart 的抽签能跑」还没成立。成立的是：位置有了，缺口被量成 0/24，且这个数会随实现上升。**

### 仍然 Unknown

**那 11 个的请求形状**（**但写一个就能把 `implementable` 从 0 变 1，可复算**）·
**序列里某步失败该继续还是中止**（镜像行为没查）· **其余 7 个流程的 `Flow.Store` 是否都等于 `Id`**（只核了 popmart）

### 教训

> **R866/R867 我把这件事描述成「结构改造」，听起来像动大手术。实际是一处虚属性、一张反射表、一个 override、七个测试。**
> **而唯一真正难的地方，是一个事先没想到的运行时约束。那类约束在纸上永远看不出来 —— 只能撞。**
> **所以「先估影响面」是对的，但估完就该动手；再估一轮也估不出那个 `ArgumentException`。**
"""

BACKLOG_ADD = """

## 优先级 ① — 序列机制建成（R868，**已改产品代码**）

| 文件 | 改了什么 |
|---|---|
| `StoreFlow.cs` | `StepSequence` 虚属性（默认空）+ `StepDispatch`（反射 165 条）+ `RunStepNamedAsync` |
| `PopMartFlow.cs` | `override StepSequence => StoreFlowSteps.PopMart.Names` |
| `FlowSequenceTests.cs` | 新建 7 用例 |

**套件 1773 通过 / 0 失败 / 0 跳过**（1766 + 7）。

### 踩坑：开放实例委托绑不上派生声明

**第一版按 `flowType.GetMethods()` 绑 → `ArgumentException: Cannot bind … signature is not compatible`。
原因：`Func<StoreFlow,…>` 第一参数是基类，重写声明在派生类。
改法：按 `typeof(StoreFlow)` + `DeclaredOnly` 绑基类声明，靠虚分派到达重写。副作用正向：一张表服务所有流程。**

### 量出的数

```
map = 165   sequence = 24   implementable = 0
```

**24 个镜像步骤名与 165 个方法名零交集。与 R844 的 22/130 是同一件事，但这一次是同层比较，不需要免责声明。**

### 一对测试

`NoPopMartImageStepIsDispatchableYet`（165/24/0）+ `TheTableIsNotEmptyWhichIsWhyTheZeroAboveMeansDisjoint`（表非空）
**→ 单看前者，表坏了也是 0；加上后者，0 才有意义。**

### 还没做

**其余 7 流程的 override** · **runner 按序列跑的分支** · **写抽签步骤**（11 个仍缺请求形状）
**→「Pop Mart 抽签能跑」尚未成立；成立的是位置有了、缺口量成 0/24。**

| 仍 Unknown | |
|---|---|
| 11 个的请求形状 | **写一个即可把 implementable 从 0 变 1** |
| 序列某步失败该继续还是中止 | 镜像行为未查 |
| 其余 7 流程 `Flow.Store` 是否等于 `Id` | 只核 popmart |

**纪律**：**纸上估不出运行时约束 —— 估完就该动手。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R868", BLOCKER)
    ensure(RSTATUS, "R868", BLOCKER)
    ensure(RVERDICT, "第 868 轮", VERDICT)
    ensure(BACKLOG, "R868", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R868" not in h:
        h += ("\n## R868 补充 — 序列机制建成（**已改产品代码**）\n\n"
              "**三处改动**：`StoreFlow` 加 `StepSequence` 虚属性 + `StepDispatch` 反射表（165 条）+ `RunStepNamedAsync`；"
              "`PopMartFlow` override 序列；新建 `FlowSequenceTests`（7 用例）。\n"
              "**套件 1773 通过 / 0 失败 / 0 跳过**（1766 + 7）。\n"
              "**踩坑**：开放实例委托 `Func<StoreFlow,…>` 绑不上派生类声明 → 改按 `typeof(StoreFlow)` + `DeclaredOnly` 绑基类，靠虚分派。\n"
              "**量出：map=165 · sequence=24 · implementable=0** —— 24 个镜像步骤名与 165 个方法名**零交集**。\n"
              "**还没做**：其余 7 流程 override · runner 按序列跑的分支 · 写抽签步骤。**「抽签能跑」尚未成立。**\n"
              "**教训：纸上估不出运行时约束 —— 估完就该动手。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R868"), (RSTATUS, "R868"), (RVERDICT, "第 868 轮"), (BACKLOG, "R868")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R868: the sequence mechanism exists, and its first measurement is zero of twenty-four\n\n"
         "First product change since R866. StoreFlow gains a StepSequence property defaulting to empty, a StepDispatch"
         " table of 165 entries built by reflection, and RunStepNamedAsync to invoke a step by the image's name."
         " PopMartFlow overrides the sequence with StoreFlowSteps.PopMart.Names. Seven tests are new. The suite reads"
         " 1773 passed, 0 failed, 0 skipped -- the previous 1766 plus the seven.\n\n"
         "The first attempt bound delegates against each concrete flow type and three tests failed with 'Cannot bind to"
         " the target method because its signature is not compatible with that of the delegate type'. The cause is that"
         " an open instance delegate whose first parameter is StoreFlow cannot bind a method declared on PopMartFlow,"
         " since the base type is not assignable to the derived one. Binding the base declarations with DeclaredOnly"
         " fixes it, and virtual dispatch reaches the overrides without the table knowing they exist. The side effect "
         "is the better design: one table serves every flow and is built once, whereas the first version's"
         " per-type cache was superfluous.\n\n"
         "With the mechanism in place the first thing it does is measure. The map holds 165 names, Pop Mart's sequence"
         " holds 24, and the overlap is zero. None of the image's draw, exhibit or reservation steps shares a name with"
         " any method the replica can actually invoke. That is consistent with R849 and R850 -- the endpoints all exist"
         " and three steps have enough evidence to write while eleven still lack request shapes -- but it is now a"
         " number that can be recomputed rather than a description.\n\n"
         "It also supersedes R844's 22 of 130, which compared image step names against a generic sequence's names and"
         " therefore needed three separate caveats about layers. This comparison is inside one layer, a step the image"
         " lists against a method the replica can call, and needs none.\n\n"
         "Two of the seven tests matter most and are a pair. One asserts 165, 24 and 0 together. The other asserts the"
         " table is not empty. Alone, the first would pass just as happily on a broken table; with the second, the zero"
         " means the two name sets are disjoint rather than that the reflection query failed.\n\n"
         "Not done: the other seven flows' overrides, which are eight mechanical lines; the runner branch that follows"
         " a sequence when one exists; and any draw step at all. So Pop Mart's draw cannot run yet. What is true is"
         " that the place for those steps now exists, and the gap is measured at zero of twenty-four, a number that"
         " moves the moment one is written.\n\n"
         "Unknown: the request shapes for the eleven blocked steps, unchanged from R850 though writing one now moves"
         " implementable from zero to one and is verifiable; whether a failing step in a sequence should stop the flow"
         " or continue, which is the image's behaviour to establish when the runner branch is written; and whether the"
         " other seven flows' Flow.Store values match their classes' Id, of which only popmart was checked.\n\n"
         "The lesson is about estimating versus doing. R866 and R867 described this as a structural change and made it"
         " sound like surgery; the surgery was one property, one reflection table, one override and seven tests. The"
         " only genuinely hard part was a runtime constraint I could not have predicted on paper -- open instance"
         " delegates do not bind derived declarations -- and that kind of constraint is found by walking into it, not by"
         " estimating again.\n\n"
         "Product code changed; suite green at 1773."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
