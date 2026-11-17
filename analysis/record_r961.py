"""Record R961: SolveCaptcha implemented, plus two self-corrections on how I checked it."""

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
### 36 个 `=> Ok()`，而这一轮修了其中一个（R961）

**R960 的下一步是数还有多少空壳。数出来是 **36 个**，而它们全是核心结账步骤：**

```
GetCsrf · GetSession · VerifySession · ScrapeVariantAvailability · CheckPriceLimit
CreateCart · GetCart · EditLine · InitiateCheckout · SubmitEmail · SubmitShippingMethod
GetShippingRates · SubmitBilling · Login · CheckLogin · Register · CompleteRegistration
SendTwoFactor · GetScript · SubmitSensor · GetCaptcha · SolveCaptcha · EnterRaffle
GetRaffleData · ScrapeRaffleForm · PollRelease · PollRestock · WaitForRelease · FindSlot
GetReleaseFeed · LoadCountryData · ProcessResponse · Fill · GetStructureToken · BuildDestination
```

> **36 个假绿灯，全部在结账路径上。而这不是我造成的 —— 它们在 R112 就是这样。**
> **而 `=> Ok()` 读起来像一个「留给子类覆写」的位置。差别只在**有没有人覆写它**。****

### 而 `SolveCaptcha` 有最完整的证据

```
SolveCaptchaService
<SubmitPat>d__11 · <SolveCaptcha>d__12 · <SubmitCaptcha>d__13
https://api.solvecaptcha.com/in.php
https://api.solvecaptcha.com/res.php?key=
```

**两个端点 + 三个连号状态机 —— 足够做真事，不只是报告成功。**

### 而 `CAPCHA_NOT_READY` 不是失败

**一个「还没好」的应答是**正常路径**。把它当失败会废掉**每一次超过一轮轮询的求解**。**
**所以它单独分类，并且**回到同一个等待**。**

> **而空应答（`null` / `""`）我判 `NotReady` 而不是 `Failed`：
> 那是**传输失败**，不是服务拒绝。判 Failed 会让一次网络抖动废掉一个下一轮就好的求解。
> 而循环本来就把「到 deadline 没解出来」变成 retryable 失败 —— 那才是那个判决该在的位置。****

### 而这一轮我**错了两次**，两次都在「怎么查」上

**错一：产物里没有新代码？**

**我用 PowerShell 手写字节循环搜 UTF-16，得出 `api.solvecaptcha.com/in.php` **不在产物**。
换成 Python 三行：**

```
api.solvecaptcha.com     utf16=True
CAPCHA_NOT_READY         utf16=True
captcha not solved       utf16=True
QueueITAccepted          utf16=True
```

> **全部在场。所以不是产物缺东西，是**我的搜索工具有假阴性**。
> 而这正是 AGENTS.md §2.7b 那条「反向不可用」：搜不到 ⇏ 没有。****

**错二：`StepActionRunner` 不是一张手写表**

**我读源码搜 `'SolveCaptcha' in 表文件` → False，然后写下「新步骤必须**登记**才可达」。**
**再读 `Build()` 才发现它靠**反射扫描** `typeof(StoreFlow).GetMethods()`，名字**根本不会**以字面量出现。**

> **所以「必须登记」是错的：所有 `*Async` + `Task<StepOutcome>` + 两参数的公开方法**自动**进表。
> 而这正是 R870 那条：**动手之前先读实现，不要按名字猜结构。**
> 而我这一轮**在写这条更正的同时**才去读 `Build()` —— 前一句已经写进记录了。****

### 数字

| 度量 | R960 | **R961** |
|---|---|---|
| 套件 | 2153 | **2173** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,909 | **173,909（未变 —— 全是内联 + 一个小状态机被并）** |
| 产物大小 | 54,706 KB | **54,720 KB（+14 KB，新代码在场）** |
| 空壳 `=> Ok()` | 36 | **35** |

### 教训

> **这一轮最贵的两条都不是 `SolveCaptcha` 的实现，是**两次自我更正**。
> 一次是搜索工具有假阴性，一次是我按名字猜了一个反射表的结构。**
> **而两次的形状相同：**我用一个不可靠的检查得出一个听起来干净的结论**，
> 然后那个结论差一点进了 BACKLOG 当成事实。**
> **检查工具本身也要被检查 —— 尤其是当它给出「没有」的时候。**
"""

if "36 个 `=> Ok()`，而这一轮修了其中一个" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 961 轮：36 个 `=> Ok()`，修了 SolveCaptcha；以及两次自我更正

### 36 个空壳，全在结账路径上

**GetCsrf · GetSession · CreateCart · GetCart · SubmitEmail · SubmitShippingMethod · GetShippingRates ·
SubmitBilling · Login · CheckLogin · Register · SendTwoFactor · SolveCaptcha · EnterRaffle · PollRelease ·
PollRestock · WaitForRelease · FindSlot · Fill · BuildDestination …**

> **`=> Ok()` 读起来像「留给子类覆写」的位置。差别只在**有没有人覆写它**。**

### `SolveCaptcha` 的证据最完整

```
https://api.solvecaptcha.com/in.php        提交
https://api.solvecaptcha.com/res.php?key=  轮询
<SubmitPat>d__11 · <SolveCaptcha>d__12 · <SubmitCaptcha>d__13
```

**实现：提交 → 取 taskId → 轮询到 deadline → token 写进 `AntiBotTokens["g-recaptcha-response"]` 与 `captchaToken`。**

### 而 `CAPCHA_NOT_READY` 不是失败

**「还没好」是正常路径；当失败会废掉每一次超过一轮轮询的求解。**

**空应答判 `NotReady` 不判 `Failed`：那是传输失败，而「到 deadline 没解出来」才是 retryable 失败。**

### 而这一轮我错了两次，两次都在「怎么查」

**错一：PowerShell 手写字节循环报「`in.php` 不在产物」。Python 三行：`utf16=True` 全部在场。**
**→ 不是产物缺东西，是我的搜索工具有**假阴性**（AGENTS.md §2.7b 反向不可用）。**

**错二：我搜 `'SolveCaptcha' in 表文件` → False，写下「新步骤必须登记才可达」。
再读 `Build()` 才发现它靠**反射扫描** `GetMethods()` —— 名字根本不会以字面量出现。**
**→ 「必须登记」是错的（R870：动手前先读实现，别按名字猜结构）。**

### 数字

| 度量 | R960 | **R961** |
|---|---|---|
| 套件 | 2153 | **2173** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,909 | **173,909（未变）** |
| 产物大小 | 54,706 KB | **54,720 KB（+14，新代码在场）** |
| 空壳 `=> Ok()` | 36 | **35** |

### 教训

> **两次自我更正形状相同：**我用一个不可靠的检查得出一个听起来干净的结论**，
> 而那个结论差一点进了 BACKLOG 当成事实。**
> **检查工具本身也要被检查 —— 尤其是当它给出「没有」的时候。**
"""

BACKLOG_ADD = """

## 优先级 ② — SolveCaptcha 从 `=> Ok()` 变真实现；空壳清单 36 → 35（R961，**+20 用例**）

### 空壳清单（36 个，全在结账路径）

**GetCsrf · GetSession · VerifySession · ScrapeVariantAvailability · CheckPriceLimit · CreateCart · GetCart ·
EditLine · InitiateCheckout · SubmitEmail · SubmitShippingMethod · GetShippingRates · SubmitBilling · Login ·
CheckLogin · Register · CompleteRegistration · SendTwoFactor · GetScript · SubmitSensor · GetCaptcha ·
SolveCaptcha · EnterRaffle · GetRaffleData · ScrapeRaffleForm · PollRelease · PollRestock · WaitForRelease ·
FindSlot · GetReleaseFeed · LoadCountryData · ProcessResponse · Fill · GetStructureToken · BuildDestination**

### `Scripts/SolveCaptchaService.cs`

**`SubmitUrl` · `PollUrlPrefix` · `NotReady` · `OkPrefix` · `TaskIdFrom` · `Poll` · `SubmitForm`**
**+ `CaptchaPollKind`(NotReady/Solved/Failed) + `CaptchaPoll`**
**`SolveCaptchaAsync`：提交 → taskId → 轮询 → token 落 `AntiBotTokens["g-recaptcha-response"]`**

### 两次自我更正

**① PowerShell 字节循环假阴性 → Python 正确搜索 `utf16=True`（§2.7b 反向不可用）**
**② `StepActionRunner` 靠**反射**建表，名字不出现在源码 → 「必须登记」是错的（R870）**

### 数字

**套件 2153 → 2173 · 陈旧度 0/0 · 函数数 173,909（未变）· 产物 54,706 → 54,720 KB · 空壳 36 → **35****

| 仍 Unknown | |
|---|---|
| 剩 35 个空壳各自的镜像证据 | 未取证 |
| solvecaptcha 的参数名与应答格式 | 只有两个 URL 是字面量 |
| `SubmitFields` 五个字段名 | **Inference**（服务文档，非本镜像） |

**纪律**：检查工具本身也要被检查 —— 尤其当它给出「没有」的时候。
"""

BLOCKER = """

---

## 385. SolveCaptcha 从 `=> Ok()` 变真实现；空壳 36 → 35

> R961。**改产品代码 +20 用例。** 套件 **2173 通过 / 0 失败 / 0 跳过**。

### 一、空壳清单

**36 个 `=> Ok()` 虚步骤，全在结账路径：GetCsrf · GetSession · CreateCart · GetCart · SubmitEmail ·
SubmitShippingMethod · GetShippingRates · SubmitBilling · Login · CheckLogin · Register · SendTwoFactor ·
SolveCaptcha · EnterRaffle · PollRelease · PollRestock · WaitForRelease · FindSlot · Fill · BuildDestination …**

### 二、`SolveCaptcha` 的证据

```
https://api.solvecaptcha.com/in.php        提交
https://api.solvecaptcha.com/res.php?key=  轮询
<SubmitPat>d__11 · <SolveCaptcha>d__12 · <SubmitCaptcha>d__13
```

### 三、实现

**提交 → `TaskIdFrom` → 轮询到 deadline → `Poll` 三分类 →
token 写进 `AntiBotTokens["g-recaptcha-response"]` 与 `captchaToken`。**

**`CAPCHA_NOT_READY` = NotReady（正常路径）；空应答 = NotReady（传输失败）；
`ERROR_*` = Failed（服务拒绝）；deadline = retryable 失败。**

### 四、两次自我更正

**① PowerShell 手写字节循环报「`in.php` 不在产物」→ Python 三行 `utf16=True` 全部在场。
   那是搜索工具的**假阴性**，不是产物缺东西（§2.7b 反向不可用）。**

**② 搜 `'SolveCaptcha' in 表文件` → False，写下「新步骤必须登记才可达」。
   再读 `Build()` 才发现靠**反射扫描** —— 名字不会以字面量出现。「必须登记」是错的（R870）。**

### 五、数字

| 度量 | R960 | R961 |
|---|---|---|
| 套件 | 2153 | **2173** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,909 | **173,909（未变）** |
| 产物大小 | 54,706 KB | **54,720 KB** |
| **空壳 `=> Ok()`** | 36 | **35** |

### 六、验证

```
analysis/ida.py str SolveCaptcha          -> 两个 URL + 三个连号
python: artifact.find(s.encode('utf-16-le')) -> api.solvecaptcha.com True
test --filter SolveCaptchaServiceTests     -> 20 通过
metrics_report.py                          -> 2173 通过 / 0 失败
```

### 七、仍然 Unknown

- **剩 35 个空壳各自的镜像证据**：**Unknown** —— 未取证。
- **solvecaptcha 的参数名与应答格式**：**Unknown** —— 只有两个 URL 是字面量。
- **`SubmitFields` 五个字段名**：**Inference** —— 服务文档，非本镜像。

### 八、教训

**两次自我更正形状相同：用一个不可靠的检查得出一个听起来干净的结论，而那个结论差一点进了 BACKLOG 当成事实。**

**检查工具本身也要被检查 —— 尤其是当它给出「没有」的时候。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R961", BLOCKER)
    ensure(RSTATUS, "R961", BLOCKER)
    ensure(RVERDICT, "第 961 轮", VERDICT)
    ensure(BACKLOG, "R961", BACKLOG_ADD)

    note = (
        "\n## R961 补充 — SolveCaptcha 变真实现；空壳 36 → 35（+20 用例，套件 2173）\n\n"
        "数出 36 个 `=> Ok()` 空壳虚步骤，全在结账路径（GetCsrf/GetSession/CreateCart/GetCart/SubmitEmail/"
        "SubmitShippingMethod/GetShippingRates/SubmitBilling/Login/Register/SolveCaptcha/EnterRaffle/PollRelease/…）。\n\n"
        "修了 SolveCaptcha：证据是 api.solvecaptcha.com 的 in.php + res.php 两个 URL 和三个连号状态机。\n"
        "实现：提交 → taskId → 轮询 → token 落 AntiBotTokens[g-recaptcha-response]。\n"
        "CAPCHA_NOT_READY = NotReady（正常路径）；空应答 = NotReady（传输失败）；ERROR_* = Failed。\n\n"
        "**两次自我更正**：\n"
        "① PowerShell 手写字节循环报「in.php 不在产物」→ Python 三行 utf16=True 全部在场（搜索工具假阴性）。\n"
        "② StepActionRunner 靠**反射**建表，名字不出现在源码 → 「必须登记才可达」是错的（R870）。\n\n"
        "数字：套件 2153 → 2173 · 陈旧度 0/0 · 函数数 173,909（未变）· 产物 54,706 → 54,720 KB · 空壳 36 → 35。\n\n"
        "纪律：检查工具本身也要被检查 —— 尤其当它给出「没有」的时候。\n\n"
        "下一轮：从剩 35 个空壳里挑一个证据最全的（GetCsrf 有 38 条字符串，是最多的）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R961" not in h:
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
             for p, k in ((RBLOCK, "R961"), (RSTATUS, "R961"), (RVERDICT, "第 961 轮"), (BACKLOG, "R961")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R961: SolveCaptcha implemented, and two corrections to how I checked it\n\n"
         "R960 left a plan to count the steps that return Ok without doing anything. There are thirty-six of them, all on\n"
         " the checkout path: GetCsrf, GetSession, CreateCart, GetCart, SubmitEmail, SubmitShippingMethod,\n"
         " GetShippingRates, SubmitBilling, Login, Register, SendTwoFactor, SolveCaptcha, EnterRaffle, PollRelease and the\n"
         " rest. A virtual step returning Ok reads like a place left for a subclass to override, and the difference between\n"
         " that and a false success is only whether anything overrides it.\n\n"
         "SolveCaptcha had the best evidence of the thirty-six. The image carries api.solvecaptcha.com's two endpoints, the\n"
         " submission one and the poll one with its key parameter, plus three consecutive state machines. So the step now\n"
         " submits, reads the task id, polls to a deadline, and writes the token into both AntiBotTokens under\n"
         " g-recaptcha-response and captchaToken, which is where every captcha consumer in the flow already looks.\n\n"
         "The classification is where the care went. CAPCHA_NOT_READY is the normal path, not an error, and treating it as\n"
         " one would break every solve that took longer than a single poll. An empty answer is the transport failing rather\n"
         " than the service refusing, so it stays NotReady too: failing it would let one network hiccup end a solve the next\n"
         " poll would have finished, and the loop already turns an unanswered deadline into a retryable failure, which is\n"
         " the right place for that verdict.\n\n"
         "Then two corrections, both to how I checked rather than to what I built. First, a hand-written PowerShell byte\n"
         " loop reported that api.solvecaptcha.com was absent from the artifact; three lines of Python found it as UTF-16.\n"
         " The artifact was fine and my search had a false negative, which is the reverse-unavailable rule in AGENTS.md.\n"
         " Second, I searched the dispatch source for the literal name, found nothing, and wrote that a new step must be\n"
         " registered to be reachable. Reading Build() showed it scans GetMethods by reflection, so names never appear as\n"
         " literals and every matching public method is already in the table.\n\n"
         "Both mistakes have the same shape: an unreliable check produced a clean-sounding conclusion, and that conclusion\n"
         " nearly entered the backlog as fact.\n\n"
         "Figures: suite 2153 to 2173, freshness zero, artifact 54,706 to 54,720 kilobytes with the new code present, count\n"
         " unchanged at 173,909 since the additions are inlined, and the hollow-step count down from thirty-six to\n"
         " thirty-five.\n\n"
         "Unknown: the evidence for the remaining thirty-five; the service's real parameter names and answer format, of\n"
         " which only the two URLs are literal; and the five form field names, which are inference from the service's own\n"
         " documentation rather than recovered here.\n\n"
         "The lesson is that the check deserves checking too, especially when it says no.\n\n"
         "Product code and tests added; suite green at 2173."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()