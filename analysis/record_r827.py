"""Record R827: IDA is open, and three name-level facts change R824's conclusion."""

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

## 251. IDA 开了；**`RefreshSession` 在镜像里根本不存在** —— R824 的结论要翻

> R827。`analysis/ida.py` 直连插件（PROXY: MISSING 符合预期）。未改产品代码。

### 一、开 IDA 的过程（记住这个顺序）

```
powershell -File "...\\ida-mcp-doctor.ps1" -Path "<target.i64>"   # 后台
```

**然后按 goal 的规则点框：**

| 框 | 正文 | 动作 |
|---|---|---|
| ① 「请确认」 | `IDA has found an unpacked version of database …` | **Proceed with unpacked base** |
| ② 「请确认」 | `Database for file '…id0' is not closed. Do you want IDA to repair it?` | **是(Y)** |
| ③ 「请稍候...」 | —— | **等，不点** |

**判据是「再读一次没有框」，不是「点了 N 次」。** 之后 13337 LISTENING、`health` 回
`status=ok / hexrays_ready=true`。**doctor 自己报 `PROXY: MISSING`，那是因为我用 `ida.py` 直连，不是故障。**

### 二、三条名字级事实

| 名字 | 镜像 | 复刻件 |
|---|---|---|
| **`RefreshSession`** | **0 匹配 —— 镜像里没有** | 声明了（`StoreFlow`）+ UI 里 6 处引用 |
| **`HandleBlock`** | **有**（`<HandleBlock>d__54`） | **0 —— 完全没有** |
| `HandleResponse` | **有**（`<HandleResponse>d__55`、`<HandleResponse>d__6`） | 声明了，从不调用 |
| `SetRequest` | **有**（`<SetRequest>d__53`、`<SetRequest>d__27`、`<SetRequest>d__8`） | 声明了，仅 `StepAction` 里被列为一步 |

### 三、R824 的结论要翻

R824 说：

> `RefreshSessionAsync` 真死 —— 注释写「keeps the session cookie warm between polls」，**从不调用 = 长轮询时 session 冷掉**。
> **下一步：读反编译，看 `RefreshSession` 挂在哪个时刻。**

**镜像里 `RefreshSession` 零匹配。所以它不是「挂了没接线的步骤」，是「镜像没这个步骤、复刻件自己加的」。**

**要做的不是补调用，是删声明。** **方向从「加」变成「减」。**

**这是判据 d 那类错误的镜像版本**：我先假定「声明了但没调用 ⇒ 少了一段接线」，
**而另一种可能「声明本身是多余的」我没想到 —— 直到查镜像。**

### 四、`HandleBlock` 是复刻件缺的名字

**镜像有 `<HandleBlock>d__54`，复刻件 0 匹配。**
**这是一个复刻件完全没有的步骤名** —— 判据 (a) 的「类型缺失」是类型级，**这是名字级的一个缺口**。

### 五、我没敢下的一条结论

**`0x143454a52` 的串是：**

```
<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55
```

**三个异步状态机名字相邻，分隔符是 `$` 与 `*`。**

**我本来想写「镜像的管线是 SetRequest → HandleBlock → HandleResponse」。**
**但那三个名字相邻，是编译器在元数据里按类内源码顺序排的，不等于执行顺序。**

**把「相邻」读成「管线」就是又一个过度解读。** **所以这条不写进结论。**

**另一处 `0x1434551d5` 是 `<Generate>d__26"<SetRequest>d__27*<HandleResponse>d__28` —— 少了 `HandleBlock`。
两组不同、都不含 `RefreshSession`。**

### 六、验证

```
python analysis\\ida.py health     status=ok, hexrays_ready=true, idb_path=target\\Cybersole.exe.i64
python analysis\\ida.py str RefreshSession     matches=0
python analysis\\ida.py str HandleBlock        matches=2
复刻件 HandleBlock: 0 匹配（全 src）
本轮未改产品代码
完整套件 1766 通过 / 0 失败（重启后复跑确认）
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **`SetRequest`/`HandleResponse` 在镜像里被谁调用**：**Unknown** —— 需要反编译调用点，
  **而状态机名字本身不含调用者。**
- **`HandleBlock` 做什么**：**Unknown** —— 名字暗示「处理封锁」，**与风控对抗（优先级 ②）直接相关，
  值得单独一轮。**
- **`RefreshSession` 那 6 处 UI 引用是什么**：**Unknown** —— `MainWindow.cs×5`、`MainViewModel.cs×1`，
  **可能是刷新任务列表而不是刷新 HTTP 会话，同名不同物。删声明前要分清。**

### 八、教训

**「声明了但没调用」有两个方向的原因，我只想过一个。**
**可能是接线少了，也可能是声明多了。而我先假定是前者，因为前者更像「工作量」。**
**查一次镜像字符串就把方向定了 —— 而这一步被内存挡住了一整轮。**
"""

VERDICT = """

---

## 第 827 轮：IDA 开了；`RefreshSession` 在镜像里根本不存在

### 开 IDA 的顺序（记住）

| 框 | 动作 |
|---|---|
| `unpacked version … safer to restart from packed` | **Proceed with unpacked base** |
| `…id0 is not closed. Do you want IDA to repair it?` | **是(Y)** |
| 「请稍候...」 | **等，不点** |

**判据是「再读一次没有框」。** 之后 `health` 回 `status=ok / hexrays_ready=true`。
**doctor 报 `PROXY: MISSING` 是正常的 —— 我走 `ida.py` 直连 13337。**

### 三条名字级事实

| 名字 | 镜像 | 复刻件 |
|---|---|---|
| **`RefreshSession`** | **0 —— 没有** | 声明 + UI 6 处引用 |
| **`HandleBlock`** | **有** | **0 —— 完全没有** |
| `HandleResponse` | **有** | 声明了，从不调用 |

### R824 的结论翻了

R824：「`RefreshSessionAsync` 真死 ⇒ 该补调用，因为它是 keep-warm 的 GET」。
**镜像零匹配 ⇒ 它不是「没接线」，是「镜像没这个步骤」。**

> **要做的不是补调用，是删声明。方向从「加」变成「减」。**

**「声明了但没调用」有两个方向：接线少了，或声明多了。我只想过前者 —— 因为前者更像工作量。**

### 没敢下的一条

`<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55` 三个名字相邻。

**那是编译器按类内源码顺序排的，不等于执行顺序。把「相邻」读成「管线」是过度解读，所以不写进结论。**

### 验证

```
health ok · str RefreshSession = 0 · str HandleBlock = 2 · 复刻件 HandleBlock = 0
整套 1766 / 0（重启后复跑）· 度量 4 / 0 / 17 / 78 / 0
```

### 仍然 Unknown

**`SetRequest`/`HandleResponse` 在镜像里被谁调用**（需反编译调用点）· **`HandleBlock` 做什么**（名字暗示「处理封锁」，与优先级 ② 直接相关）· **UI 里那 6 处 `RefreshSession` 引用是什么**（可能是刷新任务列表，同名不同物 —— 删声明前要分清）
"""

BACKLOG_ADD = """

## 优先级 ① — IDA 已开；三条名字级事实（R827）

| 名字 | 镜像 | 复刻件 | 含义 |
|---|---|---|---|
| **`RefreshSession`** | **0** | 声明 + UI 6 处 | **镜像没这个步骤 → 该删声明，不是补调用** |
| **`HandleBlock`** | **有** | **0** | **复刻件缺的名字级缺口** |
| `HandleResponse` | 有 | 声明、从不调用 | 待查调用点 |
| `SetRequest` | 有 | 声明、仅 `StepAction` 列为一步 | 待查调用点 |

**R824 的结论翻转**：`RefreshSessionAsync` 不是「keep-warm 的步骤没接线」，是**镜像里不存在这个步骤**。
**「声明了但没调用」有两个方向 —— 接线少了 / 声明多了。我只想过前者。**

### 没写进结论的一条

`<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55` 相邻 ≠ 执行管线
（编译器按类内源码顺序排列）。**过度解读的典型形态，挡在记录之外。**

| 仍 Unknown | |
|---|---|
| `SetRequest`/`HandleResponse` 的调用点 | 需反编译 |
| **`HandleBlock` 做什么** | **与优先级 ② 风控直接相关，值得单独一轮** |
| UI 里 6 处 `RefreshSession` | 可能是刷新任务列表，同名不同物；**删声明前要分清** |

### IDA 开启流程（记住）

`unpacked` 警告 → **Proceed with unpacked base** · `id0 not closed` → **是(Y)** · 「请稍候」→ **等，不点**。
**判据：再读一次没有框。** `doctor` 报 `PROXY: MISSING` 正常（走 `ida.py` 直连）。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R827", BLOCKER)
    ensure(RSTATUS, "R827", BLOCKER)
    ensure(RVERDICT, "第 827 轮", VERDICT)
    ensure(BACKLOG, "R827", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    h = h.replace("- **内存**：1.91 GB / 31.71 GB。**低于 2 GB ⇒ 只用 `-m:1`，不跑全量。** 低于 1 GB 停构建。",
                  "- **内存**：重启后 20.1 GB / 31.71 GB，**全量已复跑：1766 / 0**。\n"
                  "- **IDA**：**已开启并就绪**（`health` = `status=ok / hexrays_ready=true`，13337 LISTENING）。")
    h = h.replace("1. **两个真死步骤（R824）**：`HandleResponseAsync` 与 `RefreshSessionAsync`，**总提及都是 1**（只有自己的声明）。\n"
                  "   `StoreFlowParityTests` 的规范步骤表含 `RefreshSession`/`VerifySession` → **镜像有这些阶段**。\n"
                  "   **下一步：读反编译，看 `RefreshSession` 挂在哪个时刻。猜一个调用点 = 假覆盖（R799）。**",
                  "1. **`RefreshSession` 在镜像里零匹配（R827 已证实）** → **镜像没这个步骤，该删声明而不是补调用**。\n"
                  "   `HandleBlock` 反过来：**镜像有、复刻件 0 匹配** —— 名字级缺口，且名字暗示「处理封锁」，"
                  "**与优先级 ② 直接相关，值得单独一轮**。\n"
                  "   `SetRequest` / `HandleResponse` 在镜像里有，调用点待反编译。")
    if "R827" not in h:
        h += ("\n## R827 补充\n\n**IDA 已开**（unpacked 警告 → Proceed with unpacked base；id0 → 是(Y)；「请稍候」等）。\n"
              "`RefreshSession` 镜像 0 匹配 → 删声明，不是补接线。`HandleBlock` 镜像有、复刻件 0 → 名字级缺口。\n")
    io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
    print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R827"), (RSTATUS, "R827"), (RVERDICT, "第 827 轮"), (BACKLOG, "R827")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R827: RefreshSession does not exist in the image, which reverses R824's conclusion\n\n"
         "After the restart, memory is 20 GB and the full suite re-runs at 1766 of 1766. IDA opens with the documented"
         " sequence -- the unpacked-version prompt takes Proceed with unpacked base, the id0-not-closed prompt takes"
         " yes, and the wait dialog is left alone until a re-read finds no more boxes -- and health reports ok with"
         " hexrays_ready true. The doctor's PROXY: MISSING is expected because analysis/ida.py talks to the plugin"
         " directly.\n\n"
         "Three name-level facts come out of it. RefreshSession has zero matches in the image. HandleBlock has two, and"
         " the replica has none. HandleResponse and SetRequest exist in both, declared in the replica and invoked"
         " nowhere.\n\n"
         "The first reverses R824. That round concluded RefreshSessionAsync was dead and that the next step was to find"
         " where the image placed it, reasoning from its own comment that it is the cheap GET keeping the session cookie"
         " warm between polls. The image has no such step at all, so the declaration is the thing that is wrong: the"
         " direction is to remove rather than to wire. A declaration with no caller has two possible causes, a missing"
         " connection or a surplus declaration, and I had only considered the first because it looks like work. One"
         " string search settled it, and that search had been blocked by memory for a round.\n\n"
         "HandleBlock runs the other way: present in the image, absent from the replica. The name suggests handling a"
         " block, which puts it in scope for priority two.\n\n"
         "What I did not conclude is that the three adjacent state-machine names form a pipeline in the order they"
         " appear. Compiler-emitted names sit together in metadata by source order within a class, not by execution"
         " order, and reading adjacency as a call sequence would be the same over-reading this session keeps catching.\n\n"
         "Unknown: which code invokes SetRequest and HandleResponse, since the state-machine names carry no caller; what"
         " HandleBlock does; and what the six RefreshSession references in the UI are, which may be refreshing a task"
         " list rather than a session and must be distinguished before the declaration is removed.\n\n"
         "No product code changed; four metrics unchanged at 4 / 0 / 17 / 78 / 0."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
