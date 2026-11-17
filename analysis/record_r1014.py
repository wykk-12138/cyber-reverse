"""Record R1014: CartUrl's note had already ruled on the exact move I made twice."""

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
### `CartUrl()` 的注释早就裁决了我这两轮做的事（R1014）

**R1013 说下一轮取证 Nike checkout 的创建语义，改那 3 处。取证的第一步是读那 3 处 —— 而第一处旁边就写着答案，
而答案是我上一轮做错的事。**

### ① R48 的注释，原文

**`NikeFlow.CartUrl()`（656-682，R48 写的）：**

> **「Not changed, deliberately. The original's fourteen checkout steps share those five URLs,
> which means most of them write to one checkout resource rather than hitting fourteen endpoints;
> without the decompiled step bodies there is no way to tell which of `checkouts/v3` and
> `checkout_previews/v3` carries the add. **Swapping one guess for another would move the failure,
> not remove it.」**

**→ 它把这件事说完了：**
1. 五个 URL 被十四个步骤共享
2. **没有反编译的步骤体，就无法判断哪个 step 打哪个资源**
3. **换一个猜是移动失败，不是消除失败**

### ② 而我 R1012 与 R1013 做的正是它拒绝的事

| 轮 | 我做了什么 | 依据 |
|---|---|---|
| R1012 | `GetPaymentMethodsAsync` 的地址改成 `NikeEndpoints.Checkouts` | 「每个 step 都写它」 |
| R1013 | `/delivery` 的地址改成 `NikeEndpoints.Checkouts` | 同一句 |

**→ 而「每个 step 都写它」是**真**的，而它**不决定**哪个 step 写什么。
→ 而那句注释自己说「no way to tell which of the two carries the add」。**

### ③ 而交换猜测**比 404 更坏**

**旧地址（`buy/orders/v2/...`）**只能** 404，而它**说得出来**。
新地址（`checkouts/v3/{id}`）会返回 **200 或一个关于 payload 的错误** ——
**而那时错误消息不再指向「地址不存在」。**

> **→ 一条「nike payment methods HTTP 200，但没有付款方式」读起来像**商店不支持刷卡**，
> 而真相是**我们在读一个不承载那份数据的资源**。
> → 那正是 R823/R991/R1001/R1011 那条原则的**同一次违反**，只是这次披着「有据替换」的外衣。**

### ④ 所以这一轮回滚两处，改成报告

**`/delivery` 与 `payment-methods` 都改成 `Fail(..., retryable: false)`，并在文本里点名三个候选资源
（`checkout_previews/v3` · `checkouts/v3` · 两者的 jobs），让下一次从那里开始而不是从零。**

**而**保留**的是两件从来不是猜测的事：**
1. **那个覆写本身** —— 它让步骤不再被裁（R963），那与地址无关
2. **候选资源清单** —— 镜像真的只有那五个

### ⑤ 而这一轮真正的产出是**一条被遵守的既有裁决**

**R48 那条注释存在了 900 多轮，而我在 R1012/R1013 两轮里**没有读它** —— 尽管我**改的就是它下面的那个文件**。

> **→ 而那与 R995 那次同形：答案早就在仓里，而我先动手。
> → 两次都是「读到手边的文件」这一步没做。**

### 数字

| 度量 | R1013 | **R1014** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0 / 0** |
| 全套 | 2236 / 0 / 2 | **2236 / 0 / 2** |
| 产物陈旧度 | 1 / 711 | **1 / 681（净减 30 行）** |
| 函数数 | 174,336 | **174,336** |
| **Nike 里「有据替换」的地址** | 2 | **0（两处都改回报告）** |
| **Nike 里打不存在族的活代码** | 3 | **3（未动，且现在有理由不动）** |
| **引用 R48 裁决的地方** | 0 | **2 处（两段的注释都指向它）** |

### 教训

> **「有据」有两种：证据说明**这个地址存在**，和证据说明**这个 step 用这个地址**。
> 我这两轮满足的是第一种，而它不够 —— 而我把它当成了第二种。**
> **→ 而区分它们的成本是**读那段代码旁边的注释**。R48 已经替我把这笔账算过了，
> 而我改那个文件时没读它下面那一屏。**
"""

if "`CartUrl()` 的注释早就裁决了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1014 轮：`CartUrl()` 的注释早就裁决了我这两轮做的事

### ① R48 的原文

> **「Not changed, deliberately. The original's fourteen checkout steps share those five URLs …
> without the decompiled step bodies there is no way to tell which of `checkouts/v3` and
> `checkout_previews/v3` carries the add. **Swapping one guess for another would move the failure, not remove it.」**

**→ 它把这件事说完了：五个 URL 被十四个步骤共享；没有步骤体就无法判断哪个打哪个；换一个猜是**移动**失败。**

### ② 而我 R1012 与 R1013 做的正是它拒绝的事

| 轮 | 我做了什么 | 依据 |
|---|---|---|
| R1012 | `GetPaymentMethodsAsync` 地址 → `NikeEndpoints.Checkouts` | 「每个 step 都写它」 |
| R1013 | `/delivery` 地址 → `NikeEndpoints.Checkouts` | 同一句 |

**→ 而那句「每个 step 都写它」是**真**的，而它**不决定**哪个 step 写什么。**

### ③ 而交换猜测**比 404 更坏**

**旧地址**只能** 404，而它**说得出来**。新地址会返回 **200 或关于 payload 的错误** ——
**而那时错误消息不再指向「地址不存在」。**

> **→ 「nike payment methods HTTP 200，但没有付款方式」读起来像**商店不支持刷卡**，
> 而真相是**我们在读一个不承载那份数据的资源**。
> → 那是 R823/R991/R1001/R1011 那条原则的**同一次违反**，只是这次披着「有据替换」的外衣。**

### ④ 所以回滚两处，改成报告

**`/delivery` 与 `payment-methods` 都改成 `Fail(..., retryable: false)`，点名三个候选资源
（`checkout_previews/v3` · `checkouts/v3` · 两者 jobs）。**

**保留两件从来不是猜测的事：**
1. **那个覆写本身** —— 让步骤不再被裁（R963），与地址无关
2. **候选资源清单** —— 镜像真的只有那五个

### ⑤ 而这一轮真正的产出一条**被遵守的既有裁决**

**R48 那条注释存在了 900 多轮，而我在 R1012/R1013 里**没有读它** —— 尽管我改的就是它下面的那个文件。
→ 与 R995 同形：答案早就在仓里，而我先动手。**

### 数字

| 度量 | R1013 | **R1014** |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0 / 0** |
| 全套 | 2236 / 0 / 2 | **2236 / 0 / 2** |
| 产物陈旧度 | 1 / 711 | **1 / 681（净减 30 行）** |
| 函数数 | 174,336 | **174,336** |
| **Nike 里「有据替换」的地址** | 2 | **0（都改回报告）** |
| **打不存在族的活代码** | 3 | **3（未动，且现在有理由不动）** |
| **引用 R48 裁决处** | 0 | **2** |

### 教训

> **「有据」有两种：证据说明**这个地址存在**，和证据说明**这个 step 用这个地址**。
> 我这两轮满足的是第一种，而它不够 —— 而我把它当成了第二种。**
> **→ 区分它们的成本是**读那段代码旁边的注释**。R48 已经把那笔账算过了，
> 而我改那个文件时没读它下面那一屏。**
"""

BACKLOG_ADD = """

## 优先级 ① — **撤回 R1012/R1013 的两次地址替换：R48 早已裁决「换猜是移动失败」**（R1014）

### R48 的裁决（`NikeFlow.CartUrl()` 注释，656-682）

> 「the fourteen checkout steps share those five URLs … **no way to tell which of `checkouts/v3` and
> `checkout_previews/v3` carries the add. Swapping one guess for another would move the failure, not remove it.**」

### 我违反它两次

**R1012 `GetPaymentMethodsAsync` 与 R1013 `/delivery` 都把地址换成 `NikeEndpoints.Checkouts`，
依据是「每个 step 都写它」—— 那是**真**的，而不决定哪个 step 写什么。**

**→ 而交换猜测比 404 更坏：旧地址只能 404 且说得出来；新地址返回 200 或 payload 错，
错误消息不再指向地址不存在。**

### 回滚

**两处都改成 `Fail(..., retryable: false)`，点名三个候选（`checkout_previews/v3` · `checkouts/v3` · jobs）。**
**保留：① 覆写本身（让步骤不被裁，R963）② 候选清单（镜像真的只有那五个）。**

### 「有据」的两种含义（本轮的教训）

- **证据说明这个地址存在** ← 我满足的
- **证据说明这个 step 用这个地址** ← 我需要的

**区分成本 = 读那段代码旁边的注释。R48 已算过这笔账。**

### 数字

**套件 2219/0/0 · 全套 2236/0/2 · 陈旧度 1 / 681（净减 30 行）· 函数数 174,336 ·
「有据替换」地址 2 → 0 · 活代码仍 3（有理由不动）· 引用 R48 处 0 → 2**

| 仍 Unknown | |
|---|---|
| 哪个 step 打哪个资源 | 需反编译步骤体 |

**纪律**：「有据」有两种含义，而第二种才够；区分它们只需读旁边的注释。
"""

BLOCKER = """

---

## 438. **撤回 R1012/R1013 的两次地址替换：R48 早已裁决「换猜是移动失败」**

> R1014。**改 1 个源文件（两处回滚）。** 套件 **2219 通过 / 0 失败**（metrics filter）· 全套 **2236 / 0 / 2**。

### 一、R48 的裁决原文

**`NikeFlow.CartUrl()`（656-682，R48 写的）：**

> **「Not changed, deliberately. The original's fourteen checkout steps share those five URLs,
> which means most of them write to one checkout resource rather than hitting fourteen endpoints;
> without the decompiled step bodies there is no way to tell which of `checkouts/v3` and
> `checkout_previews/v3` carries the add. **Swapping one guess for another would move the failure,
> not remove it.」**

### 二、而我 R1012 与 R1013 做的正是它拒绝的事

| 轮 | 我做了什么 | 依据 |
|---|---|---|
| R1012 | `GetPaymentMethodsAsync` 的地址改成 `NikeEndpoints.Checkouts` | 「每个 step 都写它」 |
| R1013 | `/delivery` 的地址改成 `NikeEndpoints.Checkouts` | 同一句 |

**→ 而「每个 step 都写它」是**真**的，而它**不决定**哪个 step 写什么。
→ 而那句注释自己说「no way to tell which of the two carries the add」。**

### 三、而交换猜测**比 404 更坏**

**旧地址（`buy/orders/v2/...`）**只能** 404，而它**说得出来**。
新地址（`checkouts/v3/{id}`）会返回 **200 或一个关于 payload 的错误** ——
**而那时错误消息不再指向「地址不存在」。**

**→ 一条「nike payment methods HTTP 200，但没有付款方式」读起来像**商店不支持刷卡**，
  而真相是**我们在读一个不承载那份数据的资源**。
→ 那是 R823/R991/R1001/R1011 那条原则的**同一次违反**，只是这次披着「有据替换」的外衣。**

### 四、回滚

**`/delivery` 与 `payment-methods` 都改成 `Fail(..., retryable: false)`，并在文本里点名三个候选资源
（`checkout_previews/v3` · `checkouts/v3` · 两者的 jobs），让下一次从那里开始而不是从零。**

**而**保留**的是两件从来不是猜测的事：**

1. **那个覆写本身** —— 它让步骤不再被裁（R963），那与地址无关
2. **候选资源清单** —— 镜像真的只有那五个

### 五、而这一轮真正的产出是**一条被遵守的既有裁决**

**R48 那条注释存在了 900 多轮，而我在 R1012/R1013 两轮里**没有读它** ——
尽管我**改的就是它下面的那个文件**。**

**→ 而那与 R995 那次同形：答案早就在仓里，而我先动手。
→ 两次都是「读到手边的文件」这一步没做。**

### 六、数字

| 度量 | R1013 | R1014 |
|---|---|---|
| 套件 | 2219 / 0 | **2219 / 0 / 0** |
| 全套 | 2236 / 0 / 2 | **2236 / 0 / 2** |
| 产物陈旧度 | 1 / 711 | **1 / 681（净减 30 行）** |
| 函数数 | 174,336 | **174,336** |
| **Nike 里「有据替换」的地址** | 2 | **0（两处都改回报告）** |
| **Nike 里打不存在族的活代码** | 3 | **3（未动，且现在有理由不动）** |
| **引用 R48 裁决的地方** | 0 | **2 处（两段的注释都指向它）** |

### 七、验证

```
cd replica
dotnet build src/Cybersole.Stores/Cybersole.Stores.csproj -c Debug  -> 已成功生成
dotnet test --filter "FullyQualifiedName~Nike" -m:1                 -> 47 通过
python tools/metrics_report.py                                      -> 完整套件 exit 0  2219 / 0 / 0
python - 读 src/Cybersole.Stores/Flows/NikeFlow.cs 656-682          -> R48 的裁决原文
```

### 八、仍然 Unknown

- **哪个 step 打哪个资源**：**Unknown** —— 需反编译步骤体，而那在 NativeAOT 下按名不可得（R958）。

### 九、教训

**「有据」有两种：证据说明**这个地址存在**，和证据说明**这个 step 用这个地址**。
我这两轮满足的是第一种，而它不够 —— 而我把它当成了第二种。**

**→ 而区分它们的成本是**读那段代码旁边的注释**。R48 已经替我把这笔账算过了，
而我改那个文件时没读它下面那一屏。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1014", BLOCKER)
    ensure(RSTATUS, "R1014", BLOCKER)
    ensure(RVERDICT, "第 1014 轮", VERDICT)
    ensure(BACKLOG, "R1014", BACKLOG_ADD)

    note = (
        "\n## R1014 补充 — **撤回 R1012/R1013 的两次地址替换：R48 早已裁决「换猜是移动失败」**\n\n"
        "**`NikeFlow.CartUrl()` 的注释（R48，656-682）原文**：\n"
        "> 「the fourteen checkout steps share those five URLs … **no way to tell which of `checkouts/v3` and\n"
        "> `checkout_previews/v3` carries the add. Swapping one guess for another would move the failure, not remove it.**」\n\n"
        "**而我 R1012（`GetPaymentMethodsAsync`）与 R1013（`/delivery`）都把地址换成了 `NikeEndpoints.Checkouts`，\n"
        "依据是「每个 step 都写它」—— 那是**真**的，而不决定哪个 step 写什么。**\n\n"
        "**而交换猜测比 404 更坏**：旧地址只能 404 且说得出来；新地址返回 200 或 payload 错，\n"
        "错误消息不再指向地址不存在。「payment methods HTTP 200 但没有付款方式」读起来像**商店不支持刷卡**。\n"
        "→ 那是 R823/R991/R1001/R1011 那条原则的同一次违反，**只是披着「有据替换」的外衣**。\n\n"
        "**回滚**：两处都改成 `Fail(..., retryable: false)` 并点名三个候选；**保留**① 覆写本身（让步骤不被裁，R963）\n"
        "② 候选清单（镜像真的只有那五个）。\n\n"
        "**R48 那条注释存在了 900 多轮，而我改的就是它下面的那个文件 —— 而我没读它。与 R995 同形。**\n\n"
        "数字：套件 2219/0/0 · 全套 2236/0/2 · 陈旧度 1 / 681（净减 30 行）· 函数数 174,336 ·\n"
        "「有据替换」地址 2 → **0** · 引用 R48 处 0 → **2**。\n\n"
        "教训：**「有据」有两种 —— 这个地址存在，和这个 step 用这个地址。我满足的是第一种。**\n\n"
        "下一轮：换一个站（那 3 处已封口，理由写清）；或取证 Nike 的 checkout 步骤体（R958 说按名不可得）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1014" not in h:
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
             for p, k in ((RBLOCK, "R1014"), (RSTATUS, "R1014"), (RVERDICT, "第 1014 轮"), (BACKLOG, "R1014")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1014: CartUrl's note had already ruled on the exact move I made twice\n\n"
         "R1013 sent this round at Nike's checkout creation semantics. Reading the three sites first, the very first one\n"
         " had the answer sitting beside it, and the answer was that I had done the wrong thing two rounds running.\n\n"
         "CartUrl's note, written at round 48 and untouched since, says the original's fourteen checkout steps share five\n"
         " URLs, that without the decompiled step bodies there is no way to tell which of checkouts/v3 and\n"
         " checkout_previews/v3 carries the add, and that swapping one guess for another would move the failure rather\n"
         " than remove it.\n\n"
         "That is exactly what R1012 and R1013 did. Both replaced an address with NikeEndpoints.Checkouts on the strength\n"
         " of a header sentence saying every step writes to that resource. The sentence is true and it does not say which\n"
         " step writes what, which the note says explicitly.\n\n"
         "And the swap is worse than what it replaced. The old address could only 404, and it said so. The new one comes\n"
         " back with 200 or with an error about the payload, and then the message no longer points at the address --\n"
         " a payment-methods read that returns the checkout's JSON reads as a shop that will not take cards, when the\n"
         " truth is that we are reading a resource that does not hold that data. That is the R823 and R991 and R1001\n"
         " principle violated again, this time wearing the clothes of a well-evidenced substitution.\n\n"
         "So both are rolled back to reporting, naming the candidate resources so the next attempt starts from a list.\n"
         "What stays is the part that was never a guess: the override still exists, so the step is no longer trimmed, and\n"
         " that has nothing to do with the address.\n\n"
         "The note had been in the tree for nine hundred rounds, in the file I was editing, below what I was reading. This\n"
         " is the same shape as R995: the answer was already written down and I moved first.\n\n"
         "Figures: suite 2219 with no failures on the metrics filter and 2236 in full, freshness one file and 681 lines\n"
         " after a net thirty-line reduction, count 174,336, no substituted addresses left in Nike, three sites still\n"
         " non-existent and now with a reason to leave them, two places citing the round-48 ruling that had none.\n\n"
         "Unknown: which step hits which resource, which needs decompiled step bodies that NativeAOT does not give up by\n"
         " name.\n\n"
         "The lesson is that \"evidenced\" has two meanings -- evidence that the address exists, and evidence that this\n"
         " step uses it -- and I satisfied the first and treated it as the second. Telling them apart costs reading the\n"
         " note beside the code, which round 48 had already written on my behalf.\n\n"
         "One source file changed, two substitutions withdrawn; suite green at 2219."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()