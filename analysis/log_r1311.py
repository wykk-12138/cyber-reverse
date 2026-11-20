"""R1311 round record: Cybersource Flex lands and this time it ships."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1311 轮：Cybersource Flex 落地，并且这次**确认进了产物**

- **上一轮的教训直接用上了**：新类型属于不可达代码就会被 AOT 裁掉，所以这一轮先把调用链接好再谈交付。
  `StoreFlowRunner` 第 141 行注册了 `("GetPaymentToken", flow.GetPaymentTokenAsync)`，`StoreFlow` 自己也
  在 1410/1547/1581 调用它——**在 `CasioFlow` 里重写它，就从运行器可达**。
- **镜像里的一整套 Flex 字面量**（全冻结串，带地址）：
  `https://flex.cybersource.com/flex/v2/tokens`(0x147066CCC)；
  **两代**微表单 iframe `.../cybersource/assets/microform/0.11.8/iframe.html?keyId=`(0x147066C0C) 与
  `.../microform/bundle/v2.0.2/iframe.html?keyId=`(0x147066D3C)；
  `https://api.cybersource.com`(0x1470535DC)、`api.cybersource.com`(0x146F748D4)；
  `https://secureacceptance.cybersource.com/silent/embedded/pay`(0x14708014C) 及两个 payer-authentication 入口。
  Casio 类的元数据里还有 `_flexTokensUrl` / `_captureContext` / `_cybersource` 三个字段，和
  `GetCaptureContext` / `Tokenize` / `GetCardBrand` 三个辅助方法名，以及 JSON 键 `cardInfo`(0x146FC03B4)。
- **落码**：`Payments/CybersourceFlex.cs`——三个 URL 常量 + 两代 iframe 构造器 + `TokenizeBody`
  （`cardInfo` 是镜像实证的键；`expirationMonth`/`expirationYear`/`securityCode`/`tokenInformation`
  是厂商公开契约，**逐条标 Inference**）+ `TokenizeAsync`（capture context 走 `Authorization: Bearer`）。
- **接入**：`CasioFlow.GetPaymentTokenAsync` 重写——无 capture context 时**拒绝并指名 `d__37`**
  （`GetCaptureContext` 在镜像里是字段不是字面量，没有串拼出那个端点）；有则 tokenize 并落
  `casio.flexToken` / `casio.cardType`。
- **产物复核（这次先看再报）**：`CybersourceFlex` 类型名在产物里 **1 次命中**，尺寸
  61,259,776 → **61,270,016**。对照：`SquareBrowserData` 仍是 **0**（上轮记录的裁剪项没变）。
  URL 常量按字节搜不到——与 §4.5 一致（字符串存储是混合的），所以**不拿"搜不到 URL"当反证**，
  依据是类型名在 + 尺寸涨 + 调用链可达。
- **测试基础设施的一处小改**：`TinyServer` 原来只记 (method, path, body)，无法区分"带了 Authorization"
  和"没带"。加了一个并行的 `RequestHeaders` 列表（**additive，`Requests` 形状不变**，既有用例零影响），
  否则"capture context 被当作 bearer 使用"这条根本没有断言点。

### 五要素

- **改了什么**：新增 `Payments/CybersourceFlex.cs`、`tests/Cybersole.Tests/CybersourceFlexTests.cs`（12 条）；
  `RetailFlows.cs` 加 `CasioFlow.GetPaymentTokenAsync` 重写 + 一个 using；
  `Support/TinyServer.cs` 加 `RequestHeaders`；NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter CybersourceFlexTests` → **12/12**；
  产物搜 `CybersourceFlex` → **1**，尺寸 **61,270,016**（上轮 61,259,776）；
  `artifact_freshness.py` → `state: current`；`metrics_report.py` → 全部 exit 0；
  `mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**：套件 2587 → 见 METRICS 当前值（+12）；产物见上。
- **证据等级**：Observation —— 七个 URL 字面量及其地址、三个字段名、三个辅助方法名、`cardInfo` 键、
  以及产物里该类型名命中。Inference —— Flex v2 请求体成员与 bearer 用法、`token`/`cardType` 响应成员
  （厂商公开契约，非反编译）。Unknown —— capture context 的签发端点；镜像在哪一步调用 tokenize。
- **还剩什么**：Casio 其余步骤（`SetAdyenPayment` d__6 / `SubmitAdyenOrder` d__7 / `GetAdyenPaymentStatus` d__8 /
  `HandleAdyenResult` d__9 / `HandleAdyenAction` d__10，以及 Start/Login/ClearCart/GetCustomerToken d__39–42）；
  `_timestamp`/`_hash` 的签名方案；Saucony 六步 API 路径。
"""

POINTER = """
---

## 第 1311 轮

- **Cybersource Flex 落地并确认进产物**：`Payments/CybersourceFlex.cs`（7 个 URL 字面量、两代微表单 iframe、
  `TokenizeBody`、`TokenizeAsync`），接在 `CasioFlow.GetPaymentTokenAsync`——该步骤由
  `StoreFlowRunner` 注册，所以可达。产物里类型名 **1 次命中**，尺寸 61,259,776 → 61,270,016。
- 无 capture context 时**拒绝并指名 d__37**：那个签发端点在镜像里是字段不是字面量，没有串拼出它。
- `TinyServer` 加了并行 `RequestHeaders`（additive），否则"bearer 真的发出去了"没有断言点。
- 对照：`SquareBrowserData` 仍不在产物里（R1310 记录的裁剪项）。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1311 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1311 \u8f6e')
