"""Log R1283 (the Stripe challenge wiring) and keep it short."""

import io

B = """
## R1283 —— 支付主链接通 `StripeChallenge`（此前 src 内零调用者）

**改了什么**

- `StripeChallenge.ChallengeRequiredMarker = "CAPTCHA_REQUIRED"`（0x146B65A14，镜像大写拼法）——这是"要不要跑确认机"的判据。
- `StripeGateway.AuthorizeAsync`：intent 应答含该 marker ⇒ 认领验证码令牌 → `ConfirmChallengeAsync` →
  **重发同一次 intent confirm**，用重试的 status 说话；无令牌则不 PUT、直接报失败（与 `ConfirmAsync` 的失败分支一致）。
- 挑战分支**放在 `requires_action` 之前**：被挑战的 intent 也会报 `requires_action`，先判 `requires_action`
  会让墙永远轮不到。
- `ConfirmChallengeAsync`：host 走 `ApiUrl(c)`（`stripe.apiUrl` 注入缝），**path 单独拼接**——
  `ConfirmAsync` 的 url 参数是整体替换，直接传 host 会丢掉逐单路径。

**取证**：`dec 0x140BE31F0`（121 行）显示状态机在 emit `Solving Stripe challenge` 后 await 令牌，再
`sub_14130CC50` 五次（= `Dictionary.Add`）填五字段——即该函数就是确认机本体，`sub_14130CC50` 是字典 Add 而非
ConfirmAsync。外层由 billing 步骤驱动。

**验证**：`StripeChallenge` **6/6**（4 旧 + 2 新端到端）；全量 **2465 通过 / 0 失败 / 2 跳过 / 2467**。

**踩到的两处契约**（写下来省下一轮）：`Session.PaymentMethodId` 是**属性**不是 Vars，设 Vars 会让
`TokenizeAsync` 真的跑起来并因无卡早退；`TinyServer` 回调第一参是 `HttpListenerRequest`，路径要读
`Url.AbsolutePath`。

**Unknown**：挑战的**外层**触发条件（billing 步骤如何判定）镜像里没有状态码比较，判据由外层决定；
本轮以 `CAPTCHA_REQUIRED` 落地，属 Inference，已在源码注释标明。
"""

V = """
---

## 第 1283 轮：`StripeChallenge` 接进支付主链（零调用者 → 真实调用）

- 判据 `CAPTCHA_REQUIRED`（0x146B65A14）加进 `StripeChallenge`；`AuthorizeAsync` 命中即跑确认机并**重发 intent**。
- 分支放在 `requires_action` **之前**（否则墙永远轮不到）。
- `ConfirmChallengeAsync` host 走 `ApiUrl` 注入缝、path 单独拼（`ConfirmAsync` 的 url 是整体替换）。
- 端到端两测：有令牌 → `POST intent` → `PUT /challenge/confirm` → `POST intent` 成功；无令牌 → 只发一次、报失败。
- `StripeChallenge` 6/6；全量 **2465/0/2/2467**。
"""

H = """
## R1283 —— StripeChallenge 接主链：CAPTCHA_REQUIRED 判据 + 确认后重发 intent；全量 2465/0/2/2467

Observation：
- `dec 0x140BE31F0` 121 行：emit 状态 → await 令牌 → 五次 `sub_14130CC50`（字典 Add）填五字段。
- 新测 2 条端到端（TinyServer）：请求序列 `POST intent` / `PUT /challenge/confirm` / `POST intent`。
- 全量 2465/0/2/2467；`StripeChallenge` 6/6。

Inference：外层触发条件由 billing 步骤决定（镜像无状态码比较），以 `CAPTCHA_REQUIRED` 落地。
下轮：BstnFlow 的 4 个 `endpoint unknown`（`chars_va-12` 链）；随后 Captcha 协议层；再 `Cybersole.Http`。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
