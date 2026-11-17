"""Record R962: GetCsrf implemented, and the artifact does not contain what I said it did."""

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
### `GetCsrf` 写了，而**产物里没有它** —— 于是我该查的都查了一遍（R962）

**R962 把 `GetCsrfAsync` 从 `=> Ok()` 写成真实现（四种 token 形状 + 四个 cookie 名）。
DLL 里字符串**全在**，AOT 产物里**没有**。于是查了十二个标记串：**

| 来源 | 标记串 | 在产物 |
|---|---|---|
| R959 `QueueItProtocol` | `QueueITAccepted` | **在** |
| R959 文案 | `Initiliazing Queue-it` | **在** |
| R959 `HostSuffix` | `.queue-it.net` | 不在 |
| R960 `PollQueueAsync` | `queue not passed within the deadline` | 不在 |
| R960 设置 | `queueMinRemaining` | 不在 |
| R961 `SolveCaptchaService` | `api.solvecaptcha.com` | **在** |
| R961 应答 | `CAPCHA_NOT_READY` | **在** |
| R961 步骤体 | `captcha not solved within the deadline` | 不在 |
| R962 步骤体 | `no csrf token on the page` | 不在 |
| R962 cookie | `csrftoken` | 不在 |
| R955 派发 | `SubmitPayment:` | 不在 |
| R958 库存 | `out of stock` | **在** |

**五在，七不在。而函数数从 R958 起是 173,866 → 173,909 → 173,909 → 173,909。**

### 所以那三个 +42 / +43 / +43 **是什么**

**在产物的五个都是**静态类里的 const**（`QueueItProtocol` 的两个、`SolveCaptchaService` 的两个、`CheckStockAsync` 的一个）。**

> **所以那三段增量更可能是**静态协议类变得可达**，不是**步骤体进了产物**。
> 而我在这三轮里都写了「接线让步骤体进产物」——**那个因果解释未被证明。**
> **而 R955 那句「+43 来自支付派发」也属于同一类：数动了，归因是猜的。****

### 而这为什么重要

**如果步骤体不进产物，那么「把 `=> Ok()` 写成真实现」这个动作**不会改变函数数**，
而我一直用它当进展指标。**

> **这不代表那些工作没价值 —— 源码是对的、编译过、能测。
> 但它代表**我一直在用一把量不到那个东西的尺子**。**
> **而 §2.7b 那条「反向不可用」在这里的形态是：**函数数没动 ⇏ 工作没做**。
> 而我这次是反过来踩的：**工作量了没动，我却说是别的东西让它动的**。****

### 而机制本身仍然 Unknown

**为什么 `PollQueueAsync` 的体不在、而 `QueueItProtocol` 的 const 在？
为什么 `SubmitPayment:` 不在、而 `out of stock` 在？**

**两者都是 `StoreFlow` 的 virtual 方法、都由反射表派发、都零覆写。
所以「有没有覆写」不是解释 —— 我试过，它对不上。**

> **已知的只有：派发表靠 `GetMethods()` 反射建，而反射在 NativeAOT 下**不 root 方法**。
> 所以哪些留下，取决于应用实际构造了哪些 flow、实际调用了什么。
> 而这一层我没有取证。标 Unknown，不标 Inference。****

### 数字

| 度量 | R961 | **R962** |
|---|---|---|
| 套件 | 2173 | **2186** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,909 | **173,909（未变）** |
| 产物大小 | 54,720 KB | **54,724 KB** |
| 空壳 `=> Ok()` | 35 | **34** |
| **步骤体在产物里的轮** | — | **R955–R962 共八轮，五在七不在** |

### 教训

> **这一轮真正的产出不是 `GetCsrf`，是那句「我一直在用一把量不到那个东西的尺子」。
> 而它是在**我本该庆祝 34 个空壳变 33 个的时候**发现的。**
> **一个指标连续三轮不动，而我连续三轮都给了一个动听的原因 ——
> 那本身就是那个指标在说「你归错了因」。**
"""

if "`GetCsrf` 写了，而**产物里没有它**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 962 轮：`GetCsrf` 写了，而产物里没有它 —— 于是查了一遍

### 做了什么

**`GetCsrfAsync` 从 `=> Ok()` 写成真实现：隐藏 input（name/value 两种顺序）· meta 标签 ·
JSON 字段 · `data-*` 属性 · 四个 cookie 名 · 八个字符下限 · 找不到判 `retryable: false`。**

**DLL 里字符串全在；AOT 产物里没有。于是查了十二个标记串：**

| 来源 | 在产物 |
|---|---|
| `QueueITAccepted` · `Initiliazing Queue-it`（R959） | **在** |
| `api.solvecaptcha.com` · `CAPCHA_NOT_READY`（R961） | **在** |
| `out of stock`（R958） | **在** |
| `.queue-it.net` · `queueMinRemaining` · `queue not passed…` · `captcha not solved…` ·
`no csrf token on the page` · `csrftoken` · `SubmitPayment:` | 不在 |

### 所以那三个 +42 / +43 / +43 是什么

**在产物的五个都是**静态类里的 const**。所以那三段增量更可能是**静态协议类变得可达**，
不是**步骤体进了产物**。**

> **而我在那三轮里都写了「接线让步骤体进产物」—— 那个因果解释未被证明。
> R955 那句「+43 来自支付派发」属于同一类。**

### 而这为什么重要

**如果步骤体不进产物，「把 `=> Ok()` 写成真实现」就**不改变函数数** —— 而我一直拿它当进展指标。**

> **源码是对的、编译过、能测。但我一直在用一把**量不到那个东西的尺子**。**
> **§2.7b「反向不可用」在这里的形态：函数数没动 ⇏ 工作没做。
> 而我这次踩的是反面：量了没动，却说是别的东西让它动的。**

### 机制仍 Unknown

**为什么 `PollQueueAsync` 的体不在而 `QueueItProtocol` 的 const 在？
为什么 `SubmitPayment:` 不在而 `out of stock` 在？两者都是 virtual、都零覆写、都由反射派发。**

> **「有没有覆写」对不上 —— 我试过。已知只有「反射在 NativeAOT 下不 root 方法」。**
> **哪些留下取决于应用实际构造了哪些 flow。这一层没取证 → Unknown。**

### 数字

| 度量 | R961 | **R962** |
|---|---|---|
| 套件 | 2173 | **2186** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,909 | **173,909（未变）** |
| 产物大小 | 54,720 KB | **54,724 KB** |
| 空壳 `=> Ok()` | 35 | **34** |

### 教训

> **真正的产出不是 `GetCsrf`，是那句「我一直在用一把量不到那个东西的尺子」。
> 而它是在**我本该庆祝空壳从 35 变 34 的时候**发现的。**
> **一个指标连续三轮不动、而我连续三轮都给了一个动听的原因 ——
> 那本身就是那个指标在说「你归错了因」。**
"""

BACKLOG_ADD = """

## 优先级 ① — GetCsrf 变真实现；**并发现步骤体不进产物**（R962，**+13 用例**）

### 改动

**`GetCsrfAsync`：四种 token 形状 + 四个 cookie 名 + 八字下限 + 找不到判不可重试
`FindCsrfToken`（公开静态，13 个用例覆盖四形状与短值拒绝）**

### 而更重要的：产物核对

**十二个标记串五在七不在；函数数三轮不动。**

**在产物的都是静态类 const（`QueueITAccepted` · `Initiliazing Queue-it` · `api.solvecaptcha.com` ·
`CAPCHA_NOT_READY` · `out of stock`）；不在的是 `StoreFlow` 的步骤体串。**

**→ 函数数增量的归因（R955/R958/R960 那三个 +42/+43/+43）**未证明**。**

### 数字

**套件 2173 → 2186 · 陈旧度 0/0 · 函数数 173,909（未变）· 产物 54,720 → 54,724 KB · 空壳 35 → 34**

| 仍 Unknown | |
|---|---|
| **哪些步骤体进产物、依据什么** | 反射不 root 方法已知，具体判据未取证 |
| 函数数增量的真实来源 | 疑似静态协议类可达，**未证明** |
| 剩 34 个空壳各自的证据 | 未取证 |

**纪律**：一个指标连续三轮不动而每轮都有动听的归因 —— 那本身说明归因错了。
"""

BLOCKER = """

---

## 386. GetCsrf 变真实现；**并发现步骤体不进产物**

> R962。**改产品代码 +13 用例。** 套件 **2186 通过 / 0 失败 / 0 跳过**。

### 一、改动

**`GetCsrfAsync`：隐藏 input（两种属性顺序）· meta · JSON 字段 · `data-*` · 四个 cookie 名 ·
八字下限 · 找不到判 `retryable: false`。`FindCsrfToken` 公开静态。**

**镜像证据：`GetCsrf` 在约二十个不同 ordinal 上（d__14 · d__22 · d__23 · d__24 · d__26 · d__28 ·
d__31 · d__32 · d__33 · d__35 · d__39 · d__40 · d__50 …）→ 每家店自己读自己的 token。**

### 二、而这一轮的真正发现

**DLL 里字符串全在，AOT 产物里没有。查十二个标记串：**

| 在产物 | 不在产物 |
|---|---|
| `QueueITAccepted` · `Initiliazing Queue-it` | `.queue-it.net` · `queueMinRemaining` |
| `api.solvecaptcha.com` · `CAPCHA_NOT_READY` | `queue not passed within the deadline` |
| `out of stock` | `captcha not solved within the deadline` |
| | `no csrf token on the page` · `csrftoken` · `SubmitPayment:` |

**在产物的五个都是**静态类 const**。**

### 三、所以那三段增量是什么

**R955 +43 · R958 +42 · R960 +43 —— 我三次都归因成「接线让步骤体进产物」。**

**而登记串显示步骤体**不在**产物 → 那个归因**未证明**。**

**更可能：静态协议类变得可达。但这一层我没取证，标 Unknown，不标 Inference。**

### 四、为什么这重要

**如果步骤体不进产物，「把 `=> Ok()` 写成真实现」**不改变函数数** —— 而我一直拿函数数当进展指标。**

**源码是对的、编译过、能测。但尺子量不到那个东西。**

### 五、数字

| 度量 | R961 | R962 |
|---|---|---|
| 套件 | 2173 | **2186** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,909 | **173,909（未变）** |
| 产物大小 | 54,720 KB | **54,724 KB** |
| **空壳 `=> Ok()`** | 35 | **34** |

### 六、验证

```
dotnet build Stores -c Release                    -> 0 错误
python: dll.find('no csrf token on the page')     -> utf16=True
python: exe.find('no csrf token on the page')     -> utf16=False   ← 关键
python: exe.find('QueueITAccepted')               -> utf16=True
python: exe.find('out of stock')                  -> utf16=True
test --filter CsrfTokenTests                      -> 13 通过
metrics_report.py                                 -> 2186 通过 / 0 失败
```

### 七、仍然 Unknown

- **哪些步骤体进产物、依据什么**：**Unknown** —— 反射不 root 方法这一点已知，具体判据未取证。
- **函数数增量的真实来源**：**疑似静态协议类可达，未证明** —— 明确标记为未证明。
- **剩 34 个空壳各自的证据**：**Unknown** —— 未取证。

### 八、教训

**一个指标连续三轮不动、而我连续三轮都给了一个动听的原因 —— 那本身就是那个指标在说「你归错了因」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R962", BLOCKER)
    ensure(RSTATUS, "R962", BLOCKER)
    ensure(RVERDICT, "第 962 轮", VERDICT)
    ensure(BACKLOG, "R962", BACKLOG_ADD)

    note = (
        "\n## R962 补充 — GetCsrf 变真实现；**并发现步骤体不进产物**（+13 用例，套件 2186）\n\n"
        "GetCsrfAsync 从 `=> Ok()` 写成真实现（四种 token 形状 + 四个 cookie 名 + 八字下限）。\n"
        "镜像证据：GetCsrf 在约二十个不同 ordinal 上（d__14/d__22/d__23/d__24/d__26/d__28/d__31/d__32/d__33/d__35/"
        "d__39/d__40/d__50…）→ 每家店自己读自己的 token。\n\n"
        "**而真正重要的发现**：DLL 里字符串全在，AOT 产物里没有。查十二个标记串 —— 五在七不在。\n"
        "在产物的都是静态类 const（QueueITAccepted / Initiliazing Queue-it / api.solvecaptcha.com / "
        "CAPCHA_NOT_READY / out of stock）；不在的是 StoreFlow 的步骤体串（SubmitPayment: / csrftoken / "
        "no csrf token on the page / queue not passed… / captcha not solved… / .queue-it.net / queueMinRemaining）。\n\n"
        "→ 所以 R955 +43 / R958 +42 / R960 +43 那三次「接线让步骤体进产物」的归因**未证明**；\n"
        "  更可能是静态协议类变得可达，但这一层未取证，标 Unknown。\n\n"
        "→ **函数数这把尺子量不到「步骤体进产物」这件事**，而我一直拿它当进展指标。\n\n"
        "数字：套件 2173 → 2186 · 陈旧度 0/0 · 函数数 173,909（未变）· 产物 54,720 → 54,724 KB · 空壳 35 → 34。\n\n"
        "纪律：一个指标连续三轮不动而每轮都有动听的归因 —— 那本身说明归因错了。\n\n"
        "下一轮：取证「哪些步骤体进产物、依据什么」（这是把尺子修好的前提）；在此之前不再用函数数当单轮进展判据。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R962" not in h:
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
             for p, k in ((RBLOCK, "R962"), (RSTATUS, "R962"), (RVERDICT, "第 962 轮"), (BACKLOG, "R962")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R962: GetCsrf implemented, and the artifact does not contain what I said it did\n\n"
         "GetCsrf was one of thirty-five steps returning Ok without doing anything, and the image carries it under roughly\n"
         " twenty different ordinals, so every shop reads its own token rather than inheriting one shape. The step now\n"
         " reads the four shapes a token takes -- hidden input in either attribute order, meta tag, JSON field, data\n"
         " attribute -- plus four cookie names, with an eight-character floor because fields named like tokens also carry\n"
         " values like on and 1.\n\n"
         "Then the artifact disagreed. The built DLL contains every new string and the published native image contains\n"
         " none of the step body. Twelve marker strings from R955 to R962 were checked: five are present and seven are\n"
         " not. The five that are present are all constants from static classes -- QueueITAccepted, Initiliazing Queue-it,\n"
         " api.solvecaptcha.com, CAPCHA_NOT_READY and out of stock. The seven absent ones are StoreFlow's own step bodies.\n\n"
         "So the three increments I reported -- 43 for the payment dispatch, 42 for the three RPC steps, 43 for the queue\n"
         " poll -- were each attributed to a step body entering the artifact, and that attribution is unproven. The more\n"
         " likely source is a static protocol class becoming reachable, but that was not demonstrated, so it stays Unknown\n"
         " rather than inference.\n\n"
         "This matters because writing a real body where there was an Ok does not move the function count, and the function\n"
         " count has been my progress measure. The source is correct, it compiles and it is tested; the ruler simply cannot\n"
         " measure that thing. Reverse-unavailable in AGENTS.md says a miss does not mean absence, and here I hit its mirror\n"
         " image: the number moved and I credited something that may not have moved it.\n\n"
         "The mechanism itself remains open. PollQueueAsync's body is absent while QueueItProtocol's constants are present,\n"
         " and SubmitPayment's dispatch string is absent while out of stock is present; both are virtual, both are dispatched\n"
         " by reflection and neither is overridden anywhere, so override count does not explain it. What is known is that\n"
         " the dispatch table is built by GetMethods and reflection does not root methods under NativeAOT; which ones survive\n"
         " depends on what the app actually constructs and calls, and that layer has not been examined.\n\n"
         "Figures: suite 2173 to 2186, freshness zero, count unchanged at 173,909, artifact 54,720 to 54,724 kilobytes, and\n"
         " the hollow-step count down from thirty-five to thirty-four.\n\n"
         "Unknown: which step bodies reach the artifact and on what basis; the real source of the three increments, marked\n"
         " as unproven rather than inferred; and the evidence for the remaining thirty-four.\n\n"
         "The lesson is that the round's real product was not GetCsrf but the sentence about the ruler, and it arrived at the\n"
         " moment I was about to celebrate a count going from thirty-five to thirty-four. An indicator that does not move for\n"
         " three rounds while I offer a pleasing explanation each time is the indicator saying the explanation is wrong.\n\n"
         "Product code and tests added; suite green at 2186."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()