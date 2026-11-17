"""Record R1000: publish done, and the artifact proves two earlier fixes never reached it."""

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
### publish 完成 —— 而产物证明我**两处修复根本没进去**（R1000）

**内存回到 16.9 GB → publish 跑通（50 秒）。而量完之后最有价值的不是新数字，是一个否定结论。**

### ① publish 的数字

```
函数数   173,952 → 173,994（+42）
函数比   62.77%  → 62.79%
陈旧度   15 / 10,753 → 0 / 0
产物大小  53.4 MB → 53.5 MB
套件     2210 通过 / 0 失败 / 0 跳过
```

**而 R999 那个「时效警告（生成）」块**消失了** —— 因为被它警告的两件事都真的被做了。
（两次证明：R999 里变异那条消失，R1000 里产物这条消失。）**

### ② 而 `+42` 与 R963 记录的 `+42` 是同一个数 —— 查了，**不是同一件事**

**R963 记的是 `+42/+43/+43` 三段，而它的结论是：**

> **「那三段 +42/+43/+43 的真实来源是**静态协议类变得可达** —— 不是我写了步骤体。」
> 「`StoreFlow` 的虚方法只在**有覆写**时保留。零覆写的基类体被裁 ——
> 因为派发表靠 `MethodInfo.Invoke`，**反射在 NativeAOT 下不 root 方法**。」**

### ③ 所以我去验了一件事：这两轮的修复进产物了吗

**R991 把 `GetPaymentTokenAsync` 的伪造令牌改成 `Fail("… will not invent one")`；
R992 把 `GetTokenAsync` 改成 `Fail("… not invent a credential")`。**

**在两个产物里直接搜那两句话：**

| 串 | 新 `.publish-aot` | 旧 `.publish-aot-prev` |
|---|---|---|
| `will not invent one`（R991） | **absent** | absent |
| `not invent a credential`（R992） | **absent** | absent |
| `DataDome clearance acquired`（R996） | **IN（UTF-16LE）** | absent |

> **决定性：R991 与 R992 那两处改动**没有进产物**。
> R963 的规则兑现了 —— 零覆写的基类虚方法被裁掉，**改它的身体不改变产物**。
> → 而 R996 的 `DataDomeClearance`**进了**，因为它是被 `SolveDetectedWallAsync` **直接调用**的
> （静态可达），不是靠反射派发。**
> **→ 所以 `+42` 的来源可以**归因**：那个新静态类及其可达成员。
> 这不是 Inference —— 那句串在新产物里、旧产物里没有。**

### ④ 而这把 R991/R992 的成果**重新定位**了

**那两轮让源码不再伪造凭据 —— 那是对的，而它在**源码层**。
产物里没有那段代码，所以它对函数数、对运行时行为**都没有影响**。**

> **这不是白做（源码里一个伪造的兜底仍然该删），但它也**不是产物级进展**。
> 而如果只看函数数不变，会把它读成「那两轮没成果」；如果只看源码改对了，
> 会把它读成「产物里那条路现在正确了」—— **两个读法都错。**
> **→ 正确答案：**源码层正确，产物层不存在**。而后者是 R963 那条规则决定的，不是我决定的。**

### ⑤ 而那给出一个可操作的判断规则

**想让一个步骤**真的进产物**，二选一：**
1. **给它一个真实调用点**（像 `DataDomeClearance` 被 `SolveDetectedWallAsync` 直接调）
2. **让某个 flow 覆写它**（镜像里的形状就是「`GetCsrf` 二十份」）

> **而「把基类虚方法的身体写好」不属于这两条 —— 它是**源码整洁**，不是**产物进展**。**

### 数字

| 度量 | R999 | **R1000** |
|---|---|---|
| 套件 | 2210 | **2210** |
| **产物陈旧度** | 15 / 10,753 | **0 / 0（已 publish）** |
| **函数数** | 173,952（陈旧） | **173,994（当前）** |
| **函数比** | 62.77% | **62.79%** |
| 产物大小 | 53.4 MB | **53.5 MB** |
| **时效警告** | 1 条 | **0 条** |
| **R991/R992 的改动在产物里** | 未测 | **不在（两句话都 absent）** |

### 教训

> **「改对了源码」与「改动了产物」是两件事，而它们在某几轮里长得一模一样：
> 两种情况下套件都绿、两个文件都变了。**
> **→ 区分它们只需要一件事：**在产物里搜你写的那句话**。
> 而这件事我做了三轮才第一次做。**
"""

if "publish 完成 —— 而产物证明" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1000 轮：publish 完成 —— 而产物证明我两处修复根本没进去

### ① publish 的数字

```
函数数  173,952 → 173,994（+42）      函数比  62.77% → 62.79%
陈旧度  15 / 10,753 → 0 / 0          产物   53.4 MB → 53.5 MB
套件    2210 通过 / 0 失败 / 0 跳过
```

**而 R999 那个「时效警告（生成）」块**消失了** —— 被它警告的两件事都真的被做了。
（R999 里变异那条消失；R1000 里产物这条消失。两次都证明那个块跟着数据走。）**

### ② `+42` 与 R963 的 `+42` 是同一个数 —— 查了，不是同一件事

**R963 的结论：「那三段 +42/+43/+43 的真实来源是**静态协议类变得可达**，不是我写了步骤体。」
「`StoreFlow` 的虚方法只在**有覆写**时保留。零覆写的基类体被裁 —— 反射在 NativeAOT 下不 root 方法。」**

### ③ 所以验了一件事：这两轮的修复进产物了吗

| 串 | 新 `.publish-aot` | 旧 `.publish-aot-prev` |
|---|---|---|
| `will not invent one`（R991 `GetPaymentToken`） | **absent** | absent |
| `not invent a credential`（R992 `GetToken`） | **absent** | absent |
| `DataDome clearance acquired`（R996 新类） | **IN（UTF-16LE）** | absent |

> **决定性：R991 与 R992 那两处改动**没有进产物**。R963 的规则兑现 ——
> 零覆写基类虚方法被裁，改身体不改变产物。
> → 而 R996 的 `DataDomeClearance`**进了**，因为它被 `SolveDetectedWallAsync` **直接调用**（静态可达）。
> → 所以 `+42` **可归因**到那个新静态类 —— 这是 Observation，不是 Inference。**

### ④ 这把 R991/R992 的成果重新定位了

**那两轮让源码不再伪造凭据 —— 对的，而在**源码层**。产物里没有那段代码，
所以它对函数数、对运行时行为**都没有影响**。**

> **这不是白做（源码里一个伪造的兜底仍然该删），但它**不是产物级进展**。
> 只看函数数会读成「那两轮没成果」；只看源码会读成「产物里那条路现在正确了」—— **两个读法都错。
> 正确答案：源码层正确，产物层不存在。****

### ⑤ 可操作的判断规则

**想让一个步骤真的进产物，二选一：**
1. **给它一个真实调用点**（`DataDomeClearance` 被直接调）
2. **让某个 flow 覆写它**（镜像的形状就是「`GetCsrf` 二十份」）

**「把基类虚方法的身体写好」不属于这两条 —— 它是**源码整洁**，不是**产物进展**。**

### 数字

| 度量 | R999 | **R1000** |
|---|---|---|
| 套件 | 2210 | **2210** |
| **产物陈旧度** | 15 / 10,753 | **0 / 0** |
| **函数数** | 173,952（陈旧） | **173,994（当前）** |
| **函数比** | 62.77% | **62.79%** |
| 产物大小 | 53.4 MB | **53.5 MB** |
| **时效警告** | 1 条 | **0 条** |
| **R991/R992 的改动在产物里** | 未测 | **不在** |

### 教训

> **「改对了源码」与「改动了产物」是两件事，而它们在某几轮里长得一模一样：
> 两种情况下套件都绿、两个文件都变了。
> → 区分它们只需要一件事：**在产物里搜你写的那句话**。而这件事我做了三轮才第一次做。**
"""

BACKLOG_ADD = """

## 判据 (c)/核心 — **publish 完成：173,994 / 62.79%，陈旧度 0/0；而 R991/R992 的改动不在产物里**（R1000）

### publish

```
函数数 173,952 → 173,994（+42）· 比 62.77% → 62.79%
陈旧度 15 / 10,753 → 0 / 0 · 产物 53.4 → 53.5 MB · 套件 2210
时效警告块 1 条 → 0 条（被警告的事都做了）
```

### 产物级验证（新方法）

| 串 | 新产物 | 旧产物 |
|---|---|---|
| `will not invent one`（R991） | **absent** | absent |
| `not invent a credential`（R992） | **absent** | absent |
| `DataDome clearance acquired`（R996） | **IN** | absent |

**→ R991/R992 的修复**没进产物**（R963：零覆写基类虚方法被裁，改身体不改变产物）。
→ R996 的新类**进了**（被直接调用、静态可达）。
→ `+42` **可归因**到它 —— Observation，不是 Inference。**

### 规则

**进产物二选一：① 有真实调用点 ② 被某个 flow 覆写。
「把基类虚方法身体写好」是**源码整洁**，不是**产物进展**。**

### 数字

**套件 2210 · 陈旧度 0/0 · 函数数 173,994 · 比 62.79% · 时效警告 0**

| 仍 Unknown | |
|---|---|
| `+42` 具体是哪 42 个函数 | 布局独立，地址分桶不能本地化（R969） |

**纪律**：区分「改对源码」与「改动产物」只需在产物里搜你写的那句话 —— 我三轮后才第一次做。
"""

BLOCKER = """

---

## 424. **publish 完成：173,994 / 62.79%，陈旧度 0/0；R991/R992 的改动不在产物里**

> R1000。**publish + 产物级验证。** 套件 **2210 通过 / 0 失败 / 0 跳过**。

### 一、publish 的数字

**内存回到 16.9 GB → AOT publish 跑通（50 秒，exit 0）。**

```
函数数   173,952 → 173,994（+42）
函数比   62.77%  → 62.79%
陈旧度   15 / 10,753 → 0 / 0
产物大小  53.4 MB → 53.5 MB
套件     2210 通过 / 0 失败 / 0 跳过
```

**而 R999 那个「时效警告（生成）」块**消失了** —— 被它警告的两件事都真的被做了。
（R999 里变异那条消失；R1000 里产物这条消失。两次都证明那个块跟着数据走。）**

### 二、`+42` 与 R963 的 `+42` 是同一个数 —— 但不是同一件事

**R963 的结论：**

> 「那三段 +42/+43/+43 的真实来源是**静态协议类变得可达** —— 不是我写了步骤体。」
> 「`StoreFlow` 的虚方法只在**有覆写**时保留。零覆写的基类体被裁 ——
>  因为派发表靠 `MethodInfo.Invoke`，**反射在 NativeAOT 下不 root 方法**。」

### 三、所以验了一件事：这两轮的修复进产物了吗

| 串 | 新 `.publish-aot` | 旧 `.publish-aot-prev` |
|---|---|---|
| `will not invent one`（R991 `GetPaymentToken`） | **absent** | absent |
| `not invent a credential`（R992 `GetToken`） | **absent** | absent |
| `DataDome clearance acquired`（R996 `DataDomeClearance`） | **IN（UTF-16LE）** | absent |

**→ 决定性：R991 与 R992 那两处改动**没有进产物**。
→ R963 的规则兑现了 —— 零覆写的基类虚方法被裁掉，**改它的身体不改变产物**。
→ 而 R996 的 `DataDomeClearance`**进了**，因为它是被 `SolveDetectedWallAsync` **直接调用**的
（静态可达），不是靠反射派发。
→ **所以 `+42` 的来源可以**归因**：那个新静态类及其可达成员。
  这不是 Inference —— 那句串在新产物里、旧产物里没有。**

### 四、这把 R991/R992 的成果重新定位了

**那两轮让源码不再伪造凭据 —— 那是对的，而它在**源码层**。
产物里没有那段代码，所以它对函数数、对运行时行为**都没有影响**。**

**→ 这不是白做（源码里一个伪造的兜底仍然该删），但它也**不是产物级进展**。
→ 只看函数数会读成「那两轮没成果」；只看源码会读成「产物里那条路现在正确了」——
**两个读法都错。正确答案：源码层正确，产物层不存在。****

### 五、可操作的判断规则

**想让一个步骤**真的进产物**，二选一：**

1. **给它一个真实调用点**（像 `DataDomeClearance` 被 `SolveDetectedWallAsync` 直接调）
2. **让某个 flow 覆写它**（镜像里的形状就是「`GetCsrf` 二十份」）

**→ 「把基类虚方法的身体写好」不属于这两条 —— 它是**源码整洁**，不是**产物进展**。**

### 六、数字

| 度量 | R999 | R1000 |
|---|---|---|
| 套件 | 2210 | **2210** |
| **产物陈旧度** | 15 / 10,753 | **0 / 0** |
| **函数数** | 173,952（陈旧） | **173,994（当前）** |
| **函数比** | 62.77% | **62.79%** |
| 产物大小 | 53.4 MB | **53.5 MB** |
| **时效警告** | 1 条 | **0 条** |
| **R991/R992 的改动在产物里** | 未测 | **不在（两句话都 absent）** |

### 七、验证

```
cd replica
dotnet publish src/Cybersole.Ui/Cybersole.Ui.csproj -c Release -r win-x64 -p:PublishAot=true -p:StripSymbols=true -o .publish-aot-new --nologo
  -> exit 0，50 秒
轮换：.publish-aot -> .publish-aot-prev；.publish-aot-new -> .publish-aot
python tools/metrics_report.py
  -> functions: replica 173,994 · ratio 62.79% · source files newer 0 · 完整套件 2210 通过
python - 在两个 exe 的字节里搜
  -> 'will not invent one' 新/旧都 absent；'DataDome clearance acquired' 新 IN、旧 absent
```

### 八、仍然 Unknown

- **`+42` 具体是哪 42 个函数**：**Unknown** —— 布局独立，地址分桶不能本地化差异（R969）。

### 九、教训

**「改对了源码」与「改动了产物」是两件事，而它们在某几轮里长得一模一样：
两种情况下套件都绿、两个文件都变了。**

**区分它们只需要一件事：**在产物里搜你写的那句话**。
而这件事我做了三轮才第一次做。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1000", BLOCKER)
    ensure(RSTATUS, "R1000", BLOCKER)
    ensure(RVERDICT, "第 1000 轮", VERDICT)
    ensure(BACKLOG, "R1000", BACKLOG_ADD)

    note = (
        "\n## R1000 补充 — **publish 完成：173,994 / 62.79%，陈旧度 0/0；R991/R992 的改动不在产物里**（套件 2210）\n\n"
        "内存回到 16.9 GB → AOT publish 跑通（50 秒，exit 0）。\n"
        "**函数数 173,952 → 173,994（+42）· 比 62.77% → 62.79% · 陈旧度 15/10,753 → 0/0 · 产物 53.4 → 53.5 MB**\n"
        "→ **R999 那个时效警告块消失了**（被它警告的两件事都做了；两次证明那个块跟着数据走）。\n\n"
        "**而最有价值的不是新数字，是一个否定结论**：在两个 exe 的字节里搜我这三轮写的话 ——\n"
        "| 串 | 新产物 | 旧产物 |\n|---|---|---|\n"
        "| `will not invent one`（R991） | **absent** | absent |\n"
        "| `not invent a credential`（R992） | **absent** | absent |\n"
        "| `DataDome clearance acquired`（R996） | **IN** | absent |\n"
        "→ **R991/R992 的修复没进产物**（R963：零覆写基类虚方法被裁，改身体不改变产物）。\n"
        "→ R996 的新类**进了**（被 `SolveDetectedWallAsync` 直接调用、静态可达）。\n"
        "→ **`+42` 可归因到它 —— 这是 Observation 不是 Inference。**\n\n"
        "**规则：进产物二选一 —— ① 有真实调用点 ② 被某个 flow 覆写。"
        "「把基类虚方法身体写好」是源码整洁，不是产物进展。**\n\n"
        "数字：套件 2210 · 陈旧度 0/0 · 函数数 173,994 · 比 62.79% · 时效警告 0 条。\n\n"
        "纪律：**区分「改对源码」与「改动产物」只需在产物里搜你写的那句话 —— 我三轮后才第一次做。**\n\n"
        "下一轮：按新规则做核心 —— 给步骤真实调用点或让 flow 覆写它（优先级 ① 的 4 个真缺端点最合这条）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1000" not in h:
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
             for p, k in ((RBLOCK, "R1000"), (RSTATUS, "R1000"), (RVERDICT, "第 1000 轮"), (BACKLOG, "R1000")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1000: published, and the artifact shows two earlier fixes never reached it\n\n"
         "Memory came back at 16.9 GB, so the AOT publish that R999 could not run went through in fifty seconds. The\n"
         " function count moves from 173,952 to 173,994, the ratio from 62.77 to 62.79 percent, artifact size from 53.4 to\n"
         " 53.5 MB, and freshness from fifteen files and ten thousand lines stale to zero.\n\n"
         "The freshness warning block R999 added is now gone. That is the second time it has disappeared because the thing\n"
         " it warned about was actually done, which is the only evidence such a block needs.\n\n"
         "The figure that matters is not the new one. +42 is the same increment R963 recorded three times and then\n"
         " attributed differently, so I checked whether it means the same thing, and then checked something larger: whether\n"
         " my own recent fixes are in the artifact at all.\n\n"
         "They are not. Searching both executables for the strings I wrote: \"will not invent one\", from the payment-token\n"
         " fallback in R991, is absent from the new artifact and the old one alike; \"not invent a credential\", from the\n"
         " generic token step in R992, likewise. R963's rule holds and applies to my own work -- a base-class virtual method\n"
         " with no override is trimmed, so editing one changes nothing in the binary, because the invoker table reaches\n"
         " methods through MethodInfo.Invoke and reflection does not root them under NativeAOT.\n\n"
         "The DataDome helper added in R996 is present, by contrast, because SolveDetectedWallAsync calls it directly rather\n"
         " than reflectively. So the +42 is attributable to that new static class and what it makes reachable -- established\n"
         " by the string being in one artifact and not the other, which is observation rather than inference.\n\n"
         "That repositions the two earlier rounds. They made the source stop fabricating credentials, which was right, and\n"
         " they did it at the source level. Reading the unchanged function count as \"those rounds achieved nothing\" is\n"
         " wrong, and reading the corrected source as \"that path is now right in the binary\" is also wrong. The accurate\n"
         " statement is that the source is right and the binary does not contain it.\n\n"
         "The usable rule is that getting a step into the artifact takes one of two things: a real call site, or a flow that\n"
         " overrides it. Writing a better body on an unoverridden base method is source tidiness, not artifact progress.\n\n"
         "Figures: suite 2210, freshness zero, functions 173,994, ratio 62.79 percent, artifact 53.5 MB, no freshness\n"
         " warnings remaining.\n\n"
         "Unknown: which forty-two functions are new, since the layouts are independent and address bucketing cannot localise\n"
         " the difference.\n\n"
         "The lesson is that a corrected source file and a changed binary look identical from the outside -- green suite,\n"
         " modified file -- and telling them apart costs one string search in the artifact. It took me three rounds to run\n"
         " that search once.\n\n"
         "Published and verified; suite green at 2210."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()