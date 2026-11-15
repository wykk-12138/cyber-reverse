import io, os

# ---------- 1. VERDICT: append R186 ----------
v = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
a = io.open(v, encoding="utf-8").read()

section = """
---

## 第 186 轮：只包一层窗口，别的都不碰

R180 把整个键序层建完却**没接线** —— 接上之后 `mutation-check.py` 挂住。这一轮只接**最小的一片**：
`Object.keys` / `Object.getOwnPropertyNames`，且**只对 window 生效**，其他对象原样放过。

```js
const isWindow = target === G || (!!target && target.window === target && !!target.document);
if (!isWindow) return all;                       // ← 别的对象原样放过
return G.__topList(all, all, name === 'keys');
```

### 一、为什么只包窗口就够

api.js 真正调用的只有两处，且都对着 `window`（`Object.keys(window).sort().join(",")` → `wdata` → wasm）。
其他对象一个字节都没变 —— 这正是「不挂工装」的关键。

### 二、实测

```
probe = [true,"b,a","b,a",3]
          ↑页面变量在最后 ↑普通对象顺序不变 ↑Object.keys 同样 ↑源码三行（已伪装）
RealmReplayTests + SurfaceRuntimeTests + PatchJournalTests → 21 条全绿
```

### 三、轮次收尾状态（机器需重启）

- 已 PASS：`release build`、`store modules`、`docs present`、`endpoint provenance`、
  `WindowOrderWrapTests`(2)、`WindowOrderTests`(2)、`SurfaceOrderTests`+`JsGuardTests`(9)、重放三套(21)。
- **未完成**：`test-chunks.ps1` 全套（跑到一半）、`mutation-check.py`（内存吃紧）。
  重启后第一件事就是这两个。

### 四、这一轮的一句话

> 上一轮学会了「排序比删除更接近原版」，这一轮学会了**「只包该包的那一个对象」**比「包住所有对象」更安全。
>
> **能力越大越要先问：这个能力真的需要覆盖那么大范围吗？**
"""

if "第 186 轮" not in a:
    io.open(v, "w", encoding="utf-8", newline="").write(a.rstrip() + section)
    print("VERDICT appended", os.path.getsize(v))
else:
    print("VERDICT already has R186")

# ---------- 2. SESSION_STATE: header + notes ----------
p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 185 轮。", "最后更新：第 186 轮。", 1)

anchor = "- **窗口排序 `topList`（R185）**"
add = (
    "- **窗口键序只包一层（R186）**：`WindowOrderWrap` 只包 `Object.keys`/`getOwnPropertyNames`，且**只对 window**\n"
    "  生效（`target === G || target.window === target && target.document`），其他对象原样放过。\n"
    "  实测 `[true,\"b,a\",\"b,a\",3]`；重放三套 21 条全绿（说明不再挂工装）。组合链现为 **15 步**（待补 SurfaceOrder）。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "窗口键序只包一层" not in t:
    t = t.replace(anchor, add + anchor, 1)
    print("R186 note inserted")

# ---------- 3. the reboot handoff block, right under the title ----------
handoff = """
## 重启后从这里继续（R186 收尾快照）

**代码状态**：`D:\\projects\\cyber-reverse\\replica` 可编译；组合链 14 步已写进 `SurfaceOrder`，
第 15 步（`window-order-wrap`）**已接线但未登记**到 `SurfaceOrder`/`JsGuard` —— 下一轮先补这两处计数，
再跑验证。

**必须先跑的两件事（本机内存不足被中断）**：

```powershell
cd D:\\projects\\cyber-reverse\\replica
powershell -File tools\\clean-temp.ps1                      # 清 Chromium profile（曾一次回收 843 MB）
powershell -File tools\\test-chunks.ps1 -Size 12 -TimeoutSeconds 300   # 26 块，约 15 分钟
& 'D:\\projects\\IDA-pro\\python311\\python.exe' tools\\mutation-check.py   # 已加 600 s 上限 + hung 判定
```

**已知环境事实（不是代码缺陷）**：
- `%TEMP%` 会累积数千个目录；**单类测试 1 s、整套同进程跑会挂 20 分钟以上**。
- 多浏览器类在同一进程连跑会卡死 → 用 `test-chunks.ps1` 或逐个类跑。
- `verify-steps.ps1 -All` 的第 2/3/4/7 步在这台机器上常超窗，**逐步骤单独跑**才稳。

**下一步的功能工作**：
1. 把 `WindowOrderWrap` 登记为 `SurfaceOrder` 第 15 步 + `JsGuard` 第 18 份 body（含测试计数）；
2. 用 `test-chunks` + `mutation-check` 各跑一次，确认「只包 window」不再让工装挂住；
3. 若稳定，再把 `KeyOrderTable`（R180 建好未接线）里的 **CSS 实例只报数字索引** 那一支也接上（先只接 CSS，不动 ORDER 表）。
"""

marker = "\n## "
idx = t.find(marker, t.find("\n"))
if "重启后从这里继续" not in t and idx > 0:
    t = t[:idx] + "\n" + handoff + t[idx:]
    print("handoff block inserted")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved", os.path.getsize(p))
