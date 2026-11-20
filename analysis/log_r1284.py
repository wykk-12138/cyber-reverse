"""Log R1284: BstnFlow's four placeholders classified instead of left "unknown"."""

import io

B = """
## R1284 —— `BstnFlow` 的 4 个 `endpoint unknown` 分类结案（不是继续放着）

**先取证再改**：`ida.py str` 对 `bstn` / `BSTN` / `bstn.com` / `BstnFlow` / `Bstn` **五种写法全部 0 命中**
（`saturated: false`）；`beast` 只有 ARROW & BEAST 的 `arrowandbeast.com` 与 `arrowbeast.myshopify.com`。
`ORIGINAL_ENDPOINTS.md` 独立记过同一条：`api/beast` 在镜像里 **0 条**。

`ENDPOINT_PROVENANCE.md` 把 `/api/beast` 归在 **`live`**（有响应证据、镜像无字面量）。
所以这 4 处不是"没查"，而是**三种不同性质**：

| 位置 | 原文案 | 结案分类 | 依据 |
|---|---|---|---|
| `AddToCartAsync` | `cart endpoint unknown` | **route unrecorded** | `/api/beast` 只证了 geoIP 与 monetate；加车子路由无证据；`/cart.js` 404 |
| `GetCartAsync` | `cart endpoint unknown` | **route unrecorded** | 同上 |
| `GetCheckoutAsync` | `checkout endpoint unknown (Adyen)` | **live host, route unrecorded** | `checkoutanalytics-live.adyen.com` 是 live，结账路由未记录 |
| `SubmitOrderAsync` | `order endpoint unknown` | **route unrecorded** | Adyen 应答，提交路径未背书 |

**同时修的两处守卫**（都是"绑定措辞"而非绑定行为）：

1. `EndpointEvidenceRatchetTests` 要求**每一行使用未背书路径的代码行**自带
   `inferred: no image evidence` 标记——把标记移到使用行行尾（C# 允许 `"..." +  // comment`）；
2. `FlowWorkAuditTests.AFlowWithPlaceholdersSaysWhy` 把 `"endpoint unknown"` 写死。判据的**意图**是
   "必须说明为什么"，故放宽为 `endpoint unknown` **或** `unrecorded`，并注明 R1284 的理由。

**验证**：`EndpointEvidenceRatchet` 3/3；Bstn 相关 28/28；全量 **2465 通过 / 0 失败 / 2 跳过 / 2467**。

**还剩什么**：这 4 条**永远**只能是 unrecorded，除非拿到 BSTN 加车/下单的**活抓包**（原版靠页面 JS，
客户端不持字面量）。要真落地就得有新的 live capture，属外部条件。
"""

V = """
---

## 第 1284 轮：BstnFlow 4 个占位分类结案（镜像五写法 0 命中 → 三种性质）

- `bstn`/`BSTN`/`bstn.com`/`BstnFlow`/`Bstn` **全部 0 命中**；`/api/beast` 只有 live 证据（geoIP、monetate）。
- 4 处文案从 `unknown` 改成 **route unrecorded / live host route unrecorded**，并指向 `ENDPOINT_PROVENANCE.md`。
- 两处守卫从"绑措辞"改为"绑意图"（每行标记移到使用行；占位说明接受 `unrecorded`）。
- 全量 **2465/0/2/2467**。
"""

H = """
## R1284 —— BstnFlow 占位分类结案；两处守卫改为绑意图；全量 2465/0/2/2467

Observation：
- `ida.py str`：`bstn`/`BSTN`/`bstn.com`/`BstnFlow`/`Bstn` 全 0（`saturated:false`）；`/api/beast` 仅 live 证据。
- 4 处占位改判：cart×2 / checkout / order 全部 `route unrecorded`（checkout 为 live host）。
- 全量 2465/0/2/2467；Bstn 相关 28/28。

Unknown：BSTN 的加车与下单真实路由——需要新的 live capture（原版页面 JS 驱动，客户端无字面量）。
下轮：`docs/CAPTCHA_COVERAGE.md` 的 `CaptchaProvider.Type` 分发语义 + 缺失客户端协议（优先级②）。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
