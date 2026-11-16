"""Record R828: xrefs to step-name blobs are zero even for GetHome, so that check measures nothing."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 252. **`0 xrefs` 不是证据 —— `GetHome` 也是 0**

> R828。未改产品代码。这一轮的价值是打掉自己刚想出来的一个判据。

### 一、我想做什么

R827 确认镜像的元数据里有 `HandleBlock`、复刻件完全没有。
**这一轮想顺着它找到代码：字符串 → xrefs → 所在函数 → 反编译。**

### 二、走不通，而且理由值得记

```
HandleBlock@0x143454ccf        -> xrefs=0
SetRequest@0x143454a52         -> xrefs=0
HandleResponse@0x143454a52     -> xrefs=0
GetHome@0x14336f338            -> xrefs=0
VerifySession@0x1434ac78a      -> xrefs=0
```

**全是 0。而 `GetHome` 是肯定实现了的步骤。**

**所以「0 xrefs」不是「这个步骤不存在代码」，是「这些名字不被代码引用」。**

### 三、这些名字是什么

**它们是 NativeAOT 保留的**方法名元数据** —— 反射与栈回溯要用（`<HandleBlock>d__54` 这种形状就是编译器给 `async` 方法生成的状态机类型名）。**

**代码不比较它们，所以没有任何 xref。** **这与「步骤是否存在」无关。**

**判据用错得干净利落：我拿一个恒为 0 的量当证据。**
**如果我没查 `GetHome` 这个校准项，我会写下「`HandleBlock` 没有代码引用，所以可能只是个残留名字」——
那句话是错的，而且是靠一个自己没验证过的量得出的。**

### 四、要拿到代码，路线不是 xrefs

**NativeAOT 下要从名字走到代码，得走类型图：**

1. **`<HandleBlock>d__54` 是父类里的嵌套状态机类型**
2. **父类型的 `MethodTable` → 方法表 → `MethodDesc` → entry point（代码地址）**
3. **按名字定位就得先找到那个 `MethodTable` 的地址**

**而这需要遍历 MethodTable 结构，不是字符串 xref。** **这件事本轮没做 —— 它是一整轮的活，不是顺手一步。**

**另一条更省的路线**：**反向从代码走到名字** ——
`StoreFlow` 里有 165 个 `public virtual ... Task<StepOutcome> X(` 形式的声明，
**镜像里对应的一批函数有相同的调用形状**，可以从「被谁调用」而非「名字在哪」来定位。

### 五、对 R827 结论的影响

**R827 的三条名字级事实不变**：

| 名字 | 镜像元数据 | 复刻件 |
|---|---|---|
| `RefreshSession` | **无** | 有 |
| `HandleBlock` | **有** | **无** |
| `HandleResponse` / `SetRequest` | 有 | 有、不调用 |

**「镜像元数据里有这个方法名」是确立的。**
**「它在镜像里被实现成一段代码、并被某处调用」是 Inference（高），不是 Observation ——
因为每个有名字的步骤都必然有实现，但本轮没看到那段代码。**

**这个区别要写进文档，否则下一轮会把「元数据有名字」当成「代码已定位」。**

### 六、验证

```
python analysis\\ida.py py ...   五个名字的字符串 xrefs 全为 0（含 GetHome 校准项）
python analysis\\ida.py health   status=ok（IDA 仍在）
本轮未改产品代码
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **`HandleBlock` 的实现与调用点**：**Unknown** —— 需要走 MethodTable，**本轮只确认了「走 xrefs 不行」。**
- **`RefreshSession` 是否也只是一个缺名的步骤而非缺实现**：**Unknown** ——
  **反面：镜像元数据里连名字都没有，所以要么没这个方法，要么被内联/裁剪掉了。裁剪（trimming）是一个真实可能。
- **NativeAOT 的 trimming 会不会裁掉未使用的 `async` 方法名**：**Unknown** ——
  **如果会，那「元数据无名字」就不能推出「镜像没这个步骤」，R827 的结论要再降一级为 Inference。**

### 八、教训

**这一轮打掉的是我自己十分钟前想出来的判据。**
**而打掉它的方式很便宜：拿一个已知答案的样本（`GetHome`）去试同一个判据。**

**「这个量对所有样本都取同一个值」是我在 AGENTS.md §2.7 后面那条「不再写前缀分类器」里已经记过三次的错。
这次是第四次，形态是「恒为 0」。**
"""

VERDICT = """

---

## 第 828 轮：`0 xrefs` 不是证据 —— `GetHome` 也是 0

### 我想做的

R827 确认元数据里有 `HandleBlock`。这一轮想顺字符串 → xrefs → 函数 → 反编译。

### 走不通

```
HandleBlock → 0    SetRequest → 0    HandleResponse → 0
GetHome → 0        VerifySession → 0
```

**全是 0，而 `GetHome` 是肯定实现了的。**

> **所以「0 xrefs」不是「没有代码」，是「这些名字不被代码引用」——它们是 NativeAOT 保留的方法名元数据，反射与栈回溯用。**

**判据用错得很干净：我拿一个恒为 0 的量当证据。**
**如果没查 `GetHome` 这个校准项，我会写下「`HandleBlock` 没有代码引用，所以可能只是残留名字」—— 那是错的。**

### 要拿代码，路线不是 xrefs

**走类型图**：`<HandleBlock>d__54` 是父类的嵌套状态机类型 → 父类型 `MethodTable` → 方法表 → `MethodDesc` → entry point。
**这是一整轮的活，不是顺手一步。** 更省的替代：从「被谁调用」反向定位。

### 对 R827 的影响

**三条名字级事实不变**，但要分清证据等级：

> **「镜像元数据里有这个方法名」= Observation。**
> **「它被实现成代码并被调用」= Inference（高），本轮没看到那段代码。**

### 仍然 Unknown

**`HandleBlock` 的实现与调用点**（需走 MethodTable）· **`RefreshSession` 是缺名还是缺实现** ——
**trimming 可能裁掉未使用的 `async` 方法名，若会，则「元数据无名字」推不出「镜像没这个步骤」，R827 要降为 Inference。**

### 教训

**这一轮打掉的是我自己十分钟前想出来的判据，而方式很便宜：拿一个已知答案的样本去试它。**

**「这个量对所有样本取同一个值」已在 §2.7 记过三次。这是第四次，形态是「恒为 0」。**
"""

BACKLOG_ADD = """

## 纪律 — `0 xrefs` 不是证据（R828）

**R827 想顺着 `HandleBlock` 的字符串走 xrefs 找代码。走不通，理由是校准项：**

```
HandleBlock 0 · SetRequest 0 · HandleResponse 0 · GetHome 0 · VerifySession 0
```

**`GetHome` 是肯定实现的步骤，它也是 0。**

> **这些名字是 NativeAOT 保留的方法名元数据（反射/栈回溯），代码从不引用它们。**
> **所以「0 xrefs」与「步骤是否存在」无关。**

### 对 R827 的证据分级

| 陈述 | 等级 |
|---|---|
| 镜像元数据里有 `HandleBlock` 这个方法名 | **Observation** |
| 它在镜像里被实现成代码并被某处调用 | **Inference（高）—— 本轮没看到那段代码** |
| 镜像元数据里没有 `RefreshSession` | **Observation** |
| 因此镜像没有这个步骤 | **Inference** —— **trimming 可能裁掉未使用的 `async` 方法名** |

### 拿代码的正确路线（下一轮）

**走类型图**：`<HandleBlock>d__54` 是父类的嵌套状态机类型 → 父类型 `MethodTable` → 方法表 → `MethodDesc` → entry point。
**替代**：从「被谁调用」反向定位（`GetHome` 那批函数有相同的调用形状）。

| 仍 Unknown | |
|---|---|
| `HandleBlock` 的实现与调用点 | 需走 MethodTable |
| `RefreshSession` 缺名还是缺实现 | **trimming 可能性未排除** |

**纪律**：**「这个量对所有样本取同一个值」§2.7 已记三次，这是第四次，形态是「恒为 0」。**
**打掉它的方式：拿一个已知答案的样本去试同一判据。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R828", BLOCKER)
    ensure(RSTATUS, "R828", BLOCKER)
    ensure(RVERDICT, "第 828 轮", VERDICT)
    ensure(BACKLOG, "R828", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    h = h.replace("1. **`RefreshSession` 在镜像里零匹配（R827 已证实）** → **镜像没这个步骤，该删声明而不是补调用**。",
                  "1. **`RefreshSession` 在镜像元数据里零匹配（R827）** → 方向看起来是删声明。"
                  "**但 R828 补了一个限定：trimming 可能裁掉未使用的 `async` 方法名，所以这是 Inference 不是 Observation。**")
    if "R828" not in h:
        h += ("\n## R828 补充\n\n"
              "**`0 xrefs` 不是证据**：`HandleBlock`/`SetRequest`/`HandleResponse`/`GetHome`/`VerifySession` 的字符串 xrefs 全是 0，"
              "**而 `GetHome` 肯定实现了**。\n"
              "这些名字是 NativeAOT 保留的方法名元数据，代码不引用它们。\n"
              "**要拿代码得走类型图**（`MethodTable` → 方法表 → `MethodDesc` → entry point），或从调用点反向定位 —— 都是一整轮的活。\n")
    io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
    print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R828"), (RSTATUS, "R828"), (RVERDICT, "第 828 轮"), (BACKLOG, "R828")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R828: zero xrefs is not evidence, because GetHome has zero too\n\n"
         "R827 established that the image's metadata names HandleBlock while the replica has nothing of the kind, and"
         " this round set out to follow that string to code: string, xrefs, enclosing function, decompile.\n\n"
         "It does not work, and the reason is worth more than the attempt. Every one of these name strings has zero"
         " cross-references -- HandleBlock, SetRequest, HandleResponse, GetHome, VerifySession -- and GetHome is a step"
         " that is certainly implemented. They are the method-name metadata NativeAOT retains for reflection and stack"
         " traces, the shape `<HandleBlock>d__54` being the compiler's state machine type for an async method. Code never"
         " references them, so a count of zero says nothing about whether the step exists.\n\n"
         "Without GetHome as a calibration case I would have written that HandleBlock has no code reference and might"
         " therefore be a leftover name. That sentence would have been false, and it would have rested on a quantity I"
         " had not checked against anything known.\n\n"
         "The R827 facts stand at the level they were established. The image's metadata contains those method names and"
         " does not contain RefreshSession; the replica is the other way round for both. What is inference rather than"
         " observation is that each named step corresponds to code that something invokes. Every named step presumably"
         " does, but no code was seen this round, and the difference has to be written down or the next round will read"
         " metadata presence as located code.\n\n"
         "Reaching the code needs the type graph: the state machine type is nested in its parent, and the parent's"
         " MethodTable leads through its method list to MethodDesc entry points. That is a round's work rather than a"
         " step. The cheaper alternative is to work backwards from call sites, since the GetHome-shaped functions share a"
         " calling shape.\n\n"
         "Unknown, and sharpened: HandleBlock's implementation and call site; and whether RefreshSession is a missing"
         " name or a missing implementation, because trimming may strip the metadata name of an unused async method,"
         " which would demote R827's conclusion from observation to inference.\n\n"
         "The lesson is the cheapest kind to learn: I refuted a criterion I had invented ten minutes earlier by testing"
         " it against a sample whose answer I already knew. A quantity that takes the same value on every sample is the"
         " trap already recorded three times in section 2.7; this is the fourth occurrence and its form is a constant"
         " zero.\n\n"
         "No product code changed; four metrics unchanged at 4 / 0 / 17 / 78 / 0."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
