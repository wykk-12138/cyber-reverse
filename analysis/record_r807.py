"""Record R807: the risk-control reconciliation, done twice because the first one was wrong."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 231. 风控清单对账：**第一次对错了，第二次才有结论**；`Signifyd` 进表，`Riskified` 单列

> R807。`AntiBotVendors.cs` 加 `Signifyd`（第 8 家）与 `NamedButNotHandled`；`AntiBotVendorTests` 从 7 改 8。

### 一、第一次对账是错的

我写了个脚本，从 `AntiBotVendors` 里抽出所有字符串字面量（9 条），拿它当厂商清单去和镜像比，
**得出「18 个厂商在镜像里但未声明」。**

**这个结论从头就不成立**：那 9 条是 `DataDomeKey`、`datadome.cybersole.io/sensor` 这类**具体 token 键**，
不是厂商清单。**真实的清单位于 `Vendor` 记录里 —— 7 条。**

**而且计数也可疑**：`kasada` / `cloudflare` / `shape` / `recaptcha` / `adyen` / `stripe` 全是 40，
和 `dwfrm` 的 40 一样 —— **那是搜索结果上限，不是巧合。**

**如果我把第一版写进文档，"18 个缺口"会变成一条查不出来的假账。**

### 二、真实清单

```
AntiBotVendors.All (7 -> 8)
  DataDome · PerimeterX · Akamai · Kasada · TrustDecision · Cloudflare · Forter · Signifyd
AntiBotProtocol: Akamai/DataDome/Cloudflare/Kasada 的 cookie 表 + QueueIt + TrustDecisionScripts
CaptchaKind (5): ReCaptcha · HCaptcha · Turnstile · Geetest · Question
```

**12 个已声明项全部在镜像里** —— **没有虚报。**

### 三、三个候选，三种结论

| 厂商 | 镜像里的样子 | 结论 |
|---|---|---|
| **`shape`** | 34 条**全是假阳性**：`ShapeText`、`HarfBuzzTextShaper`、`BuiltinShape`、`MicroComIShapeVisual` | **不在镜像里** —— 复刻件不声明是对的 |
| **`signifyd`** | `HandleSignifydStepUp` · `SendSignifydStepUpCode` · `GetSignifydCode` · `CompleteSignifydStepUp` · `requiresSignifydStepUp` · `apihub.scheels.com/frontastic/action/cart/{sendSignifydStepUpCode, completeSignifydStepUpCheckout}` | **真厂商且真被处理 → 进 `All`（第 8 家）** |
| **`riskified`** | `_riskified` / `_riskifiedId` / `_riskifiedToken` / `FNL_RISKIFIED_ID` / `riskified_cookie` · `beacon.riskified.com` · `c.riskified.com/v2/client_infos` · `img.riskified.com` —— **但 `BuildRiskified`/`HandleRiskified`/`GetRiskified` 全是 0** | **被提到但未被处理 → 单列 `NamedButNotHandled`** |

### 四、为什么这个区分必须做

跑测试时 `TheImageKnowsSevenVendors` 红了 —— 我把 Riskified 加进了 `All`，而它把数量钉在 7。

**红得有道理。** `All` 是「反机器人层声称能对付的厂商」；
**一条主机串只能证明原版知道这个厂商存在，不能证明原版对它做了什么。**

**而 Signifyd 有完整的 step-up 状态机**（发码 → 取码 → 完成），那是处理，不是提及。

**所以**：

- `Signifyd` → `All`，测试改名 `TheImageKnowsEightVendors`
- `Riskified` → `NamedButNotHandled`，附上「三个 host、四个 cookie，零个 handler」的理由

### 五、`shape` 那次假阳性值得单独记

`shape` 在镜像里 34 条，**每一条都是 Avalonia/WinRT 的文本整形**
（`ShapeText`、`HarfBuzzTextShaper`、`BuiltinShape`、`MicroComIShapeVisual`）。

**一个 4 字母的英文常用词，在任何 UI 框架里都会命中几十次。**
**把它当厂商证据，就是把「词出现过」当成「厂商存在」** —— §2.7 那个错的最短形式。

### 六、验证

```
构建                已成功
AntiBot 相关用例    36 通过 / 0 失败
完整套件            1766 通过 / 0 失败 / 0 跳过（回到绿）
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **`Signifyd` 的 step-up 流程要不要实现**：**Unknown** —— 两个端点与三个方法名都在，
  **但请求体没读**（第五次同一形状）。
- **`Riskified` 在镜像里到底怎么用**：**Unknown** —— 三个 host 说明它会发信标，
  **但没有 handler，可能只是某个第三方库带进来的常量。**
- **其余候选**：`AWS WAF`（2 条，`WarhammerFlow` 已带 `AwsWafTokenHeader`）、
  `Datadog RUM`（4 条，已知故意未加）。

### 八、教训

**拿「一个字符串列表」当「一个分类清单」之前，先问这个列表是干什么用的。**
`AntiBotVendors` 里那 9 条字面量长得像清单，**职责却是记录具体的 token 键** ——
**用它对账厂商，得到的是 18 个不存在的缺口。**
"""

VERDICT = """

---

## 第 807 轮：风控清单对账，第一次对错了

### 第一次是错的

我从 `AntiBotVendors` 抽出 9 条字符串字面量当厂商清单，**得出「18 个缺口」。**

**那 9 条是 token 键，不是清单。真实清单是 `Vendor` 记录 —— 7 条。**
**而且计数可疑：`kasada`/`cloudflare`/`shape`/`recaptcha`/`adyen`/`stripe` 全是 40 —— 那是搜索上限。**

### 真实清单：12 个已声明项全在镜像里，没有虚报

```
All (7 → 8): DataDome · PerimeterX · Akamai · Kasada · TrustDecision · Cloudflare · Forter · Signifyd
AntiBotProtocol: 四个 cookie 表 + QueueIt + TrustDecisionScripts
CaptchaKind (5): ReCaptcha · HCaptcha · Turnstile · Geetest · Question
```

### 三个候选，三种结论

| 厂商 | 镜像里的样子 | 结论 |
|---|---|---|
| **`shape`** | 34 条**全是假阳性**（`ShapeText`/`HarfBuzzTextShaper`/`BuiltinShape`） | **不在镜像里** |
| **`signifyd`** | 完整 step-up 状态机 + `apihub.scheels.com` 两个动作 | **真被处理 → 进 `All`** |
| **`riskified`** | 三个 host、四个 cookie，**零个 handler** | **单列 `NamedButNotHandled`** |

### 测试红了，红得有道理

它把数量钉在 7，我加了 Riskified。

> **`All` 是「声称能对付的厂商」。一条主机串只证明原版知道它存在，不证明原版做了什么。**
> **而 Signifyd 有发码→取码→完成的状态机 —— 那是处理。**

### `shape` 的假阳性值得单独记

**一个 4 字母常用词，在任何 UI 框架里都会命中几十次。**
**把它当厂商证据，就是把「词出现过」当成「厂商存在」—— §2.7 那个错的最短形式。**

### 验证

```
构建绿 · AntiBot 36/36 · 整套 1766 / 0 · 度量未变
```

### 教训

**拿「一个字符串列表」当「一个分类清单」之前，先问它原本是干什么用的。**
"""

BACKLOG_ADD = """

## 风控 — 清单对账（R807）

**已声明 12 项全部在镜像里，没有虚报。**

```
AntiBotVendors.All (7 -> 8)   DataDome · PerimeterX · Akamai · Kasada · TrustDecision
                             · Cloudflare · Forter · **Signifyd**
AntiBotProtocol               四个 vendor cookie 表 + QueueIt + TrustDecisionScripts
CaptchaKind (5)               ReCaptcha · HCaptcha · Turnstile · Geetest · Question
```

| 候选 | 结论 |
|---|---|
| `shape` | **不在镜像里** —— 34 条命中全是 Avalonia 文本整形（假阳性） |
| `signifyd` | **进 `All`**：`HandleSignifydStepUp` / `SendSignifydStepUpCode` / `GetSignifydCode` / `CompleteSignifydStepUp` + `apihub.scheels.com/frontastic/action/cart/*` |
| `riskified` | **`NamedButNotHandled`**：三 host + 四 cookie，**`Build/Handle/GetRiskified` 全 0** |

**`All` 的含义是「声称能对付」，不是「提到过」。**
**一条主机串只证明原版知道厂商存在；Signifyd 有发码→取码→完成的状态机，那才是处理。**

| 仍 Unknown | |
|---|---|
| Signifyd step-up 的请求体 | 端点与方法名都在，**请求体没读**（第五次同一形状） |
| Riskified 在镜像里怎么用 | 无 handler，可能是第三方库带入的常量 |
| `AWS WAF`（2 条）/ `Datadog RUM`（4 条） | WAF 已由 `WarhammerFlow` 处理；Datadog 已知故意未加 |

**纪律**：**拿「一个字符串列表」当「一个分类清单」之前，先问它原本是干什么用的。**
`AntiBotVendors` 里那 9 条字面量长得像清单，职责却是记录 token 键 —— 用它对账得到 18 个不存在的缺口。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R807", BLOCKER)
    ensure(RSTATUS, "R807", BLOCKER)
    ensure(RVERDICT, "第 807 轮", VERDICT)
    ensure(BACKLOG, "R807", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R807"), (RSTATUS, "R807"), (RVERDICT, "第 807 轮"), (BACKLOG, "R807")):
        body = io.open(path, encoding="utf-8").read()
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R807: the risk-control reconciliation, done twice because the first one counted token keys as vendors\n\n"
         "The first attempt pulled nine string literals out of AntiBotVendors and compared them against the image,\n"
         "concluding that eighteen vendors were present and undeclared. That was wrong at the root: those nine are\n"
         "specific token keys like DataDomeKey and datadome.cybersole.io/sensor, while the inventory lives in Vendor\n"
         "records and numbered seven. The counts were a warning too -- kasada, cloudflare, shape, recaptcha, adyen and\n"
         "stripe all came back at exactly forty, the same as dwfrm, which is the search ceiling rather than a fact.\n\n"
         "Read properly, all twelve declared items are in the image, so nothing was overstated. Of the three\n"
         "candidates, shape turned out to be thirty-four false positives, every one Avalonia text shaping:\n"
         "ShapeText, HarfBuzzTextShaper, BuiltinShape, MicroComIShapeVisual. A four-letter English word is going to hit\n"
         "dozens of times in any UI framework, and treating that as vendor evidence is 'the word appeared' standing in\n"
         "for 'the vendor exists' -- section 2.7 in its shortest form.\n\n"
         "Signifyd is genuinely handled and joins the list: HandleSignifydStepUp, SendSignifydStepUpCode,\n"
         "GetSignifydCode, CompleteSignifydStepUp, requiresSignifydStepUp, and two frontastic cart actions on\n"
         "apihub.scheels.com. A send-code, read-code, complete-step-up machine is handling, not mention. Riskified is\n"
         "the opposite: three hosts and four cookie names, with BuildRiskified, HandleRiskified and GetRiskified all\n"
         "absent, so it goes into a separate NamedButNotHandled list rather than among the vendors the layer claims to\n"
         "defend against.\n\n"
         "The test disagreeing was the useful part. It pins the count at seven, and it was right to fail when Riskified\n"
         "was added, because a host string proves the original knew a vendor existed and not that it did anything\n"
         "about it. The test is now eight and named for it.\n\n"
         "Unknown: whether Signifyd's step-up should be implemented, since its endpoints and method names are known and\n"
         "its request bodies are not -- the fifth time that asymmetry has appeared; how Riskified is actually used by\n"
         "the image, given it has no handler and may be a constant a third-party library brought in; and the standing\n"
         "question of AWS WAF and Datadog RUM, both partially handled and deliberately not declared.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
