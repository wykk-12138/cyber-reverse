"""Record R1054: the captcha half enumerated, including the two that are absent."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 「各家 captcha」第一次被枚举 —— 而其中**两家明确缺席**（R1054）

**goal 的 ② 明列「Kasada / Cloudflare / DataDome / PerimeterX / Queue-it / **各家 captcha**」。
前五家在 `VendorWiring`，而 captcha 一直没枚举过 —— R1053 把它们当成「3 个通用挑战类型」放在缺口表的边角。**

### ① 6 个家族，各有变体

| 家族 | 变体（取自属性与任务名） |
|---|---|
| **reCAPTCHA** | `Recaptcha` · `RecaptchaInvisible` · `RecaptchaV3` · `RecaptchaEnterprise` |
| **hCaptcha** | `HCaptcha` · `HCaptchaInvisible` · `HCaptchaSpoof` |
| **Cloudflare Turnstile** | `Turnstile` · `CloudflareTurnstile` · `LoopTurnstile` · `turnstileToken` |
| **GeeTest** | `Geetest` · `GeetestV4` · `GeeTestTask` · `GeeTestTaskProxyLess` · `Geetest.html` · `GeetestV4.html` |
| **Castle** | `get_Castle` |
| **TrustDevice** | `TrustDeviceGen` · `TrustDeviceBotDOpen` · `static.trustdecision.com` |

### ② 而两家**明确缺席**（有对照）

```
Funcaptcha / ArkoseLabs   0
MTCaptcha                 0
对照 kpsdk               17
```

**→ 所以「原版支持所有主流 captcha」是**错的**。
→ 而这是**负结论**，它只有在对照成立时才有意义 —— 而对照是 `kpsdk 17`。**

### ③ 而 provider **不是内建的** —— 那是 `UserThirdParty` 的正面依据

`Cybersole.CaptchaProviders.CaptchaProvider` 的 9 个字段（24 条元数据命中）：

```
Priority · Name · Type · ApiKey · Balance · Count · Concurrency · BalanceSupported · IsFetchingBalance
```

**→ 那是一张**用户配置**的服务表**：每家有自己的 key、余额、并发、优先级，
而 `Settings.CaptchaProvidersView` 带 `EnabledProviders` / `Add` / `Reorder` ⇒ 可启用、可排序。**

**→ 所以原版 captcha 走**用户第三方**（`Solver.UserThirdParty`）。
→ 而那让那个值**第一次有了正面依据**：此前它只靠「没有本地 solver」这个**缺席**来支撑。**
**→ 而「缺席支撑一个值」与「结构支撑一个值」是完全不同的证据强度 —— 而这一轮拿到了后者。**

### ④ 而 `Geetest.html` / `GeetestV4.html` 说明 GeeTest 有**两条路**

**→ 页面内联（本地）+ `GeeTestTaskProxyLess`（第三方）。
→ 与 R1025 的 queue-it「两种表面并存」同族：**一个家族可以两种方式都在。****

### ⑤ 而我又踩了同一个坑：假数字

**第一版生成器报 `provider metadata=0` —— 而它的正则 `CaptchaProviders\\.CaptchaProvider\\.[A-Za-z]` 匹配不到真实形状。
→ 于是文档里写着「命中 0 条元数据」，而**下面却列了 9 个字段** —— 数字与内容自相矛盾。
→ 真实形状是 `CaptchaProviders.CaptchaProvider,`（逗号），改成它之后 **24**。**

**→ 那是 R1047 那次「解析器错 ⇒ 结论假」的同一个错，而这已经是**第三次**（R764 · R1047 · R1054）。
→ 而这次的自相矛盾是自己暴露的：**0 条元数据不可能支撑 9 个字段**。**

### ⑥ 数字

| 度量 | R1053 | **R1054** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 3 / 650 | **3 / 650** |
| 函数数 | 174,293 | **174,293** |
| **captcha 家族** | 未知 | **6** |
| **明确缺席** | 未知 | **2（Funcaptcha/Arkose · MTCaptcha）** |
| **`CaptchaProvider` 元数据** | 未知 | **24 条 / 9 个字段** |
| **`Solver.UserThirdParty` 的依据** | **缺席**（没有本地 solver） | **结构**（用户配置表 + ApiKey/Balance/Concurrency/Priority） |
| **`docs/CAPTCHA_COVERAGE.md`** | 不存在 | **3,448 字节（生成）** |
| **假数字** | — | **1（`0` 元数据 vs 9 字段）** |

### 教训

> **「缺席」与「结构」是两种证据，而它们对同一个结论的支撑强度不同。
> → `UserThirdParty` 之前靠「没有本地 solver」—— 那是**排除法**，而排除法在 96.87% 无符号的产物里很弱。
> → 这一轮拿到了那张**用户配置表**，于是同一个值从「排除了别的」变成「看见了它」。**
> **→ 而第二个教训：`0 条元数据` 与 `9 个字段` 写在同一页上就是自相矛盾。
> → 而那个矛盾是我自己排版排出来的 —— 它比任何测试都早地指出了正则错了。**
"""

if "「各家 captcha」第一次被枚举" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1054 —— **「各家 captcha」第一次被枚举：6 家 + 2 家明确缺席；`UserThirdParty` 有了结构依据**

### 6 个家族

| 家族 | 变体 |
|---|---|
| reCAPTCHA | `Recaptcha` · `Invisible` · `V3` · `Enterprise` |
| hCaptcha | `HCaptcha` · `Invisible` · `Spoof` |
| Cloudflare Turnstile | `Turnstile` · `CloudflareTurnstile` · `LoopTurnstile` · `turnstileToken` |
| GeeTest | `Geetest` · `V4` · `GeeTestTask` · `…ProxyLess` · `Geetest.html` · `GeetestV4.html` |
| Castle | `get_Castle` |
| TrustDevice | `TrustDeviceGen` · `TrustDeviceBotDOpen` · `static.trustdecision.com` |

### 而两家**明确缺席**（对照 `kpsdk 17` 成立）

```
Funcaptcha / ArkoseLabs   0        MTCaptcha   0
```

**⇒ 「原版支持所有主流 captcha」是**错的**。负结论只有在对照成立时才有意义。**

### provider **不是内建的** —— `UserThirdParty` 的正面依据

`CaptchaProvider` 9 个字段（**24** 条元数据）：
`Priority · Name · Type · ApiKey · Balance · Count · Concurrency · BalanceSupported · IsFetchingBalance`
+ `CaptchaProvidersView` 的 `EnabledProviders` / `Add` / `Reorder`。

**⇒ 用户配置的第三方服务表。`Solver.UserThirdParty` 此前只靠「没有本地 solver」这个**缺席**支撑，
现在有**结构**支撑 —— 两者证据强度不同。**

### 而 `Geetest.html` 说明 GeeTest 有**两条路**（本地内联 + 第三方 `…ProxyLess`），
与 R1025 的 queue-it「两种表面」同族。

### 而我又踩了假数字

第一版报 `provider metadata=0`，而文档下面列了 **9 个字段** —— **自相矛盾**。
正则 `CaptchaProviders\\.CaptchaProvider\\.[A-Za-z]` 匹配不到真实形状（`CaptchaProviders.CaptchaProvider,`，逗号），修后 **24**。
**⇒ R764 · R1047 · R1054 第三次同一个错。**

### 数字

| 度量 | R1053 | **R1054** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| captcha 家族 | 未知 | **6** |
| 明确缺席 | 未知 | **2** |
| `CaptchaProvider` 元数据 | 未知 | **24 / 9 字段** |
| `UserThirdParty` 依据 | **缺席** | **结构** |
| `CAPTCHA_COVERAGE.md` | — | **3,448 字节** |

**纪律**：「缺席」与「结构」是两种证据；而 `0 条元数据` 与 `9 个字段` 写在同一页上就是自相矛盾。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1054", NOTE)
append(RBLOCK, "R1054", "\n---\n\n## 478. **captcha 6 家 + 2 家缺席；`UserThirdParty` 有了结构依据**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1054: the captcha half enumerated, including the two that are absent\n\n"
     "The goal's risk-control list names five vendors and then the captcha services. The five have been in \n"
     "VendorWiring for rounds; the captchas were never enumerated, and R1053 filed them as three rows labelled\n"
     " generic challenge type, which describes what they are not.\n\n"
     "Six families, each with variants taken from properties and task names: reCAPTCHA with four, hCaptcha with three,\n"
     " Cloudflare Turnstile, GeeTest with four including two HTML files, Castle and TrustDevice. And two are absent with\n"
     " a control standing at seventeen -- Funcaptcha/ArkoseLabs and MTCaptcha return zero. So the common assumption\n"
     " that a tool like this supports every major captcha is wrong, and the negative is only worth anything because\n"
     " the control holds.\n\n"
     "The more useful finding is about how the providers work. CaptchaProvider is a record with a priority, a name, a\n"
     " type, an api key, a balance, a count, a concurrency and two balance flags, sitting behind a view with enabled\n"
     " providers, add and reorder. That is a user-configured service table, not a built-in solver, and it is the first\n"
     " positive evidence for Solver.UserThirdParty in VendorWiring -- a value that until now rested on the absence of a\n"
     " local solver. Absence and structure are different strengths of evidence for the same claim.\n\n"
     "GeeTest having both an HTML page and a proxyless task name says one family can be solved two ways at once, which\n"
     " is R1025's two-surfaces shape for queue-it.\n\n"
     "I also produced a false number again. The first run printed zero provider metadata and the document below it\n"
     " listed nine fields, which is a contradiction on one page: zero metadata cannot support nine fields. My regex\n"
     " expected a dot where the real shape has a comma. Fixed, and it reads twenty-four. That is the third round with a\n"
     " parser that silently returned nothing -- R764, R1047 and now this -- and the first where the document's own\n"
     " layout caught it before any test did.\n\n"
     "Figures: suite green at 2258, freshness three files and 650 lines, count 174,293, six captcha families, two\n"
     " absent with a live control, twenty-four provider metadata hits, and a fifth generated coverage document at\n"
     " 3,448 bytes.\n\n"
     "Unknown: what CaptchaProvider's Type field distinguishes, and the wire protocols inside each family's submit\n"
     " step, both of which need decompilation rather than string search.\n\n"
     "The lesson is that absence and structure support a claim with different force, and that a zero printed above a\n"
     " list of nine things is a contradiction that no test needed to catch."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
