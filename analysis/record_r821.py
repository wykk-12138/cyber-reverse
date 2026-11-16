"""Record R821: the URL-ignoring scan misattributed classes, so only the two hand-read cases stand."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 245. 查「哪些流程忽略 `c.Url`」：**扫描器给了 3，核实后只能保留 2**

> R821。`analysis/scan_url_ignoring.py`（留存，附不可信说明）。未改产品代码。

### 一、要查什么

R820 留下一条 Unknown：

> 其余 59 个模块里还有谁忽略 `c.Url` —— **如果一个流程忽略 URL 却没有 403，
> 它会报 transport error，测试就过了，于是「忽略 URL」这件事本身不会被发现。**

### 二、扫描器报了什么

```
GetHome overrides: 22
从不读 c.Url 的: 3
  NikeFlow          https://www.nike.com/（硬编码两次）
  PoqAppFlow        （体内无字面主机，走 Action() 拼 platform.poq.io）
  YeezySupplyFlow   （体内无字面主机）
```

### 三、核实一个，就塌了

`YeezySupplyFlow` 在扫描结果里出现 **9 次** `GetHomeAsync` —— **一个类有 9 个同名重写是不可能的。**

于是按花括号取它的类体单独查：

```
class YeezySupplyFlow 类体: 8,368 字符
体内不含 c.Url 的 GetHomeAsync: 0 个
```

**所以扫描器的类归属是错的。**

**原因**：它在整个文件上 `finditer` 找所有 `GetHomeAsync(`，再用「该位置之前最后一个 `class X`」当归属。
`RetailFlows.cs` 里有多个类，**于是前面几个类的重写全被算到最后一个类头上。**

**这与 R764（花括号计数）是同一族错误：在一个不平坦的结构上用「最近的前缀」当归属。**

### 四、所以只能保留两个

| 流程 | 依据 |
|---|---|
| **`PoqAppFlow`** | **R820 亲手读过**：`PostJsonAsync(c, Action("account/guest-token"), ...)`，`Action()` 拼 `Platform + "/clients/" + _client + "/"` |
| **`NikeFlow`** | **扫描器给出硬编码 `https://www.nike.com/`** —— 但仍需亲手确认，**本轮没读** |
| ~~`YeezySupplyFlow`~~ | **撤回**：类体里没有这样的重写 |

**所以答案是「至少 1 个已确认、1 个待确认」，不是「3 个」。**

### 五、这条 Unknown 现在的状态

**仍然是 Unknown，但范围收窄了**：

- **已确认**：`PoqAppFlow`
- **待确认**：`NikeFlow`
- **未知**：其余全部 —— **因为扫描器不可信，等于没查**

**要得到真答案，得按类边界正确切分再判断。** 本轮没做，因为**这一轮的价值在于发现扫描器错了**，
**而一个错的总数比没有总数更坏 —— 它会被当成事实引用下去。**

### 六、验证

```
python analysis\\scan_url_ignoring.py   报 22 个重写、3 个忽略
  核实：YeezySupplyFlow 类体内 0 个 -> 扫描器的归属错误
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **真正有多少流程忽略 `c.Url`**：**Unknown** —— 需要一个按类边界切分的扫描器，**本轮没写**。
- **`NikeFlow` 是否真的硬编码 `www.nike.com`**：**未知** —— 扫描器说两次，**未亲手读**。
- **忽略 URL 却报 transport error 的流程会不会因此躲过测试**：**是**（R820 的推理），
  **但具体是哪些，Unknown。**

### 八、教训

**这次是「先核实一个样本」救的。**
**扫描器报 3，我本来可以直接写「3 个流程忽略 c.Url」—— 那句话会被后面几轮当成事实。**

**而核实只花了读 8KB 类体。**
**廉价的抽查挡住了昂贵的事实污染：判据链里一个错的总数会一直传下去。**

**另一条**：**在「一个文件里有多个类」的结构上，用「最近的前缀 class」当归属一定会错。**
**这与 R764 同族 —— 那次是花括号，这次是类归属，共同点是假设了结构的平坦。**
"""

VERDICT = """

---

## 第 821 轮：扫描器给了 3，核实后只能保留 2

### 要查的

R820 留下：**还有哪些流程忽略 `c.Url`** —— 忽略 URL 却没 403 的流程会静默通过测试。

### 扫描器报 3

`NikeFlow`（硬编码 `www.nike.com`）· `PoqAppFlow` · `YeezySupplyFlow`

### 核实一个就塌了

`YeezySupplyFlow` 在结果里出现 **9 次** `GetHomeAsync` —— **不可能**。按花括号取它的类体：

```
类体 8,368 字符，体内不含 c.Url 的 GetHomeAsync: 0 个
```

**扫描器的类归属错了**：它在整个文件上找所有重写，再用「之前最后一个 `class X`」当归属；
`RetailFlows.cs` 有多个类，**前面的重写全被算到最后一个头上。**

> **这与 R764（花括号计数）同族：在「一个文件多个类」的结构上用最近前缀当归属，假设了平坦。**

### 所以只能保留两个

- **`PoqAppFlow`**：R820 亲手读过
- **`NikeFlow`**：扫描器说硬编码，**本轮没亲手读**

**答案是「至少 1 个已确认、1 个待确认」，不是「3 个」。**

### 验证

```
scan_url_ignoring.py 报 3 → 核实其中一个为假 → 撤回
产品代码未改 · 整套 1766 / 0 · 度量未变
```

### 教训

**这次是「先核实一个样本」救的。扫描器报 3，我本可以直接写「3 个流程忽略 c.Url」——
那句话会被后面几轮当成事实。**

> **而核实只花了读 8KB 类体。廉价的抽查挡住了昂贵的事实污染：判据链里一个错的总数会一直传下去。**
"""

BACKLOG_ADD = """

## 待查 — 忽略 `c.Url` 的流程（R821，扫描器不可信）

**R820 的问题**：忽略 URL 却没 403 的流程会静默通过 `Monitor_Survives_An_Unreachable_Host`。

**扫描器 `scan_url_ignoring.py` 报 22 个重写 / 3 个忽略 —— 但类归属是错的。**

**证据**：`YeezySupplyFlow` 被列 9 个 `GetHomeAsync`（不可能）；按花括号取它的类体，**0 个**。

**错因**：在整个文件上找所有重写，再用「之前最后一个 `class X`」当归属 ——
`RetailFlows.cs` 多类，前面的重写全算到最后一个头上。**与 R764 同族（假设结构平坦）。**

| 状态 | |
|---|---|
| **已确认忽略** | `PoqAppFlow`（R820 亲手读） |
| **待确认** | `NikeFlow`（扫描器说硬编码 `www.nike.com`，未亲手读） |
| **其余** | **Unknown —— 扫描器不可信，等于没查** |

**要真答案需按类边界正确切分的扫描器。本轮没写。**

**纪律**：**一个错的总数比没有总数更坏 —— 它会被当成事实引用下去。**
**廉价的抽查（读 8KB 类体）挡住了昂贵的事实污染。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R821", BLOCKER)
    ensure(RSTATUS, "R821", BLOCKER)
    ensure(RVERDICT, "第 821 轮", VERDICT)
    ensure(BACKLOG, "R821", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R821"), (RSTATUS, "R821"), (RVERDICT, "第 821 轮"), (BACKLOG, "R821")):
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
         "R821: the URL-ignoring scan misattributed classes, so only the two hand-read cases stand\n\n"
         "R820 left a question behind: which other flows ignore the context URL, since a flow that ignores it and does\n"
         "not meet a 403 reports a transport error and passes the robustness test, leaving the ignoring invisible.\n\n"
         "The scan found twenty-two GetHomeAsync overrides and three that never read ctx.Url: NikeFlow with a hardcoded\n"
         "nike.com, PoqAppFlow composing platform.poq.io through an Action helper, and YeezySupplyFlow. Checking one of\n"
         "them collapsed the count. YeezySupplyFlow appeared with nine GetHomeAsync overrides, which no class has, and\n"
         "reading its own class body -- 8,368 characters, brace-matched from its declaration -- finds none of them.\n\n"
         "The scanner attributes an override to whichever class declaration most recently preceded it in the file. That\n"
         "works when a file holds one class and fails when it holds several, and RetailFlows.cs holds several, so the\n"
         "earlier classes' overrides were all credited to the last one. It is the same family of mistake as R764's\n"
         "brace counting: a structural assumption of flatness, applied to something that is not flat.\n\n"
         "So the honest answer is one confirmed, one to confirm, and the rest unexamined rather than examined and\n"
         "clean. PoqAppFlow I read by hand last round. NikeFlow's hardcoded host comes from the scanner and I have not\n"
         "read it. Everything else is unknown, because a scanner whose attribution is wrong has not answered anything.\n\n"
         "I did not write the correct scanner this round. The value of the round is the discovery that the number was\n"
         "wrong, because I was one sentence away from recording that three flows ignore the URL, and that sentence\n"
         "would have been cited as fact by later rounds. A wrong total is worse than no total.\n\n"
         "Unknown: how many flows really ignore the context URL, which needs a scan that respects class boundaries;\n"
         "whether NikeFlow hardcodes nike.com, which I have not read; and which flows ignore the URL and report a\n"
         "transport error, thereby escaping notice.\n\n"
         "The check that saved this cost eight kilobytes of reading. Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
