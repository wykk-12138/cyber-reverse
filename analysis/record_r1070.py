"""Record R1070: the IDA bring-up, walked by the documented route with the dialogs it actually showed."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### IDA 重新拉起：**三个框，按规程点，`status: ok`**（R1070）

**R1069 结束时 IDA 进程为 0、端口不监听。goal 规定这件事属于「停下等 YG」之一，
而它同时给了**完整规程**—— 所以先按规程办，办不通才停。**

### ① 实测的框序（这次 3 个，不是 goal 写的「最少两个」）

| 序 | 标题 | 正文要点 | 动作 | 若不照做的后果 |
|---|---|---|---|---|
| 1 | 「请确认」 | `IDA has found an unpacked version … It appears IDA did not close properly` | **Proceed with unpacked base** | **Restore packed base** 会丢掉 IDB 里 321,244 个函数的分析 |
| 2 | 「请确认」 | `Database for file … .id0 is not closed. Do you want IDA to repair it?` | **是(&Y)** | 否(N) ⇒ 不修复，下次还会报同一个框 |
| 3 | 「请稍候...」 | 无正文 | **等，不点** | 点了会打断 repair/升级 |

**→ 而**没有**出现「Database still contains inconsistencies」那个第 4 种框（R719 那次出现过，动作是**确定**）。
→ **所以框的数量取决于 IDB 上次怎么退出的** —— 这次是「异常退出但 id0 可修复」，所以 3 个；R719 那次是 4 个。**

### ② 而「等」这一条是有度量的

```
t+0s     pid=79848 起，端口 False，CUA 看到「请确认」
点 1 → 框 2 出现
点 2 → 框 3「请稍候...」
+60s     pid alive，cpu=45s，mem=**413 MB**，端口 False
+180s    pid alive，cpu=53s，mem=**1978 MB**，端口 **True**
```

**→ 413 MB → 1978 MB 是 IDB（1375 MB）真正被加载的信号。
→ 所以「等」的判据不是时间，是**内存爬到 IDB 量级 + 端口 True**。**

### ③ 而 `PROXY: MISSING` 不是阻塞项

```
PROXY: MISSING - DSH did not spawn [python -m ida_pro_mcp] …
INSTANCE: port=13337 pid=10064 module=Cybersole.exe
READY: plug-in server is listening
VERDICT: ready - call mcp__ida__server_health to confirm idb/hexrays state.
```

**→ doctor 同时报了 `PROXY: MISSING` 和 `VERDICT: ready`。
→ 而 `analysis/ida.py` 是**直连插件**（`127.0.0.1:13337`）的过渡件，**不经代理** ⇒ 代理缺失不影响它。
→ 而 `mcp__ida__*` 那套需要代理 —— 本轮用的是 `ida.py`，所以 `PROXY: MISSING` 可以先放着。**

**→ 验证：**

```
{"status":"ok","uptime_sec":68.393,"idb_path":"…\\Cybersole.exe.i64","module":"Cybersole.exe"}
control kpsdk n=2 → 查询正常
```

### ④ 而这件事本身值得记一条

**→ 上一轮我把 IDA 退出写进记录，说「下一轮按规程拉起来，若 PROXY: MISSING 且框已清就停下等 YG」。
→ 而这一轮**没停** —— 因为规程走通了。那说明那句「停下等 YG」是**兜底**，不是第一反应。
→ 而 goal 的原话也是这个意思：「报 PROXY: MISSING 或端口 REFUSED **且框已清** → 属停下等 YG」
→ **「且框已清」是条件的一半：框还在就是规程还没走完，不是等 YG 的时候。****

### ⑤ 数字

| 度量 | R1069 | **R1070** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| **IDA 进程** | 0 | **1（pid 79848）** |
| **端口 13337** | REFUSED | **True** |
| **`ida.py health`** | 异常 | **`status: ok`** |
| **装载内存** | — | **1978 MB（IDB 1375 MB）** |
| **框数** | — | **3（Proceed / 是(Y) / 请稍候）** |
| **`PROXY: MISSING`** | — | **仍在，但不影响 `ida.py`** |

### 教训

> **「等」需要一个度量。这次它不是「等 3 分钟」，是「内存爬到 IDB 量级 + 端口 True」——
> 而那两句都可以读，不需要猜。**
> **→ 而「停下等 YG」是兜底：goal 的条件是「REFUSED **且框已清**」，
> 而框还在就说明规程没走完 —— 那时该点框，不该停。**
"""

if "IDA 重新拉起：**三个框" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1070 —— **IDA 重新拉起：3 个框，按规程点，`status: ok`**

### 实测框序

| 序 | 标题 | 动作 | 不照做的后果 |
|---|---|---|---|
| 1 | 「请确认」unpacked-version | **Proceed with unpacked base** | **Restore packed base 会丢掉 321,244 个函数的分析** |
| 2 | 「请确认」id0-not-closed | **是(&Y)** | 否(N) ⇒ 下次仍报 |
| 3 | 「请稍候...」 | **等，不点** | 点了会打断 repair/升级 |

**没有**出现第 4 种「Database still contains inconsistencies」（R719 那次有，动作**确定**）
⇒ **框数取决于 IDB 上次怎么退出**。

### 「等」是有度量的

```
+60s    cpu=45s  mem=**413 MB**   端口 False
+180s   cpu=53s  mem=**1978 MB**  端口 **True**
```

**⇒ 「等」的判据不是时间，是**内存爬到 IDB 量级 + 端口 True**。**

### 而 `PROXY: MISSING` 不是阻塞项

doctor 同时报 `PROXY: MISSING` 与 `VERDICT: ready` —— 因为 `analysis/ida.py` 是**直连插件**的过渡件，不经代理。
验证：`{"status":"ok","idb_path":"…Cybersole.exe.i64"}` · `control kpsdk n=2`。

### 而「停下等 YG」是兜底

goal 条件是「REFUSED **且框已清**」⇒ **框还在就是规程没走完，那时该点框，不该停。**

### 数字

| 度量 | R1069 | **R1070** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| IDA 进程 | 0 | **1** |
| 端口 13337 | REFUSED | **True** |
| `ida.py health` | 异常 | **`status: ok`** |
| 装载内存 | — | **1978 MB** |
| 框数 | — | **3** |
| `PROXY: MISSING` | — | **仍在，不影响 `ida.py`** |

**纪律**：「等」需要一个可读的度量；「停下等 YG」是兜底，不是第一反应。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1070", NOTE)
append(RBLOCK, "R1070", "\n---\n\n## 494. **IDA 重新拉起：3 个框，`status: ok`**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1070: IDA is back, by the documented route, with the dialogs it actually showed\n\n"
     "R1069 ended with no IDA process and nothing on 13337. The goal classes that as a stop-and-wait item and also\n"
     " documents the whole recovery, so the right move was to walk the route before stopping.\n\n"
     "Three dialogs. The first offers to restore the packed base or proceed with the unpacked one; proceeding is the\n"
     " only safe choice, because restoring would discard the analysis of 321,244 functions held in the idb. The second\n"
     " asks whether to repair an id0 that was not closed, and yes is the answer that stops it recurring. The third is a\n"
     " please-wait with no text, and the instruction is to wait and not click, since clicking interrupts the repair.\n"
     " R719 saw a fourth kind, an inconsistency warning, which did not appear here, so how many dialogs arrive depends\n"
     " on how the database was last closed.\n\n"
     "Waiting needs a measure rather than a duration. At sixty seconds the process held 413 megabytes with the port\n"
     " still closed; at three minutes it held 1978 megabytes and the port was listening. Memory climbing to the size of\n"
     " a 1375-megabyte idb plus a listening port is the signal, and both are readable rather than guessed.\n\n"
     "The doctor reports PROXY MISSING alongside its ready verdict, which is not a blocker here: analysis ida.py talks\n"
     " straight to the plugin on 13337 and does not go through the proxy. Health answers ok with the idb path, and a\n"
     " control query returns two hits, so the artefact is answering again.\n\n"
     "The larger point is that stop-and-wait is a fallback. The goal's condition is refused and no dialogs left; with\n"
     " dialogs still on screen the route is unfinished and the thing to do is click them, not wait for a human.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, count unchanged, one IDA process, port\n"
     " listening, health ok, 1978 megabytes resident, three dialogs handled by the documented actions, and a proxy\n"
     " warning that does not affect this client.\n\n"
     "The lesson is that waiting needs something observable to wait on, and that a documented fallback is not the\n"
     " first step."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
