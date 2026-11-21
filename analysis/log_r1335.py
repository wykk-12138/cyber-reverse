"""R1335 record: the PayPal partner approval lands, with its endpoint and its eleven variables."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1335 轮：`approveMemberPayment` 落地——端点、信封、十一个变量名全是观测所得

- **顺着文档找到发它的函数**：`0x1470E9FA4`（5407 字符）→ **单引用点** `0x14110CA4A` → `sub_14110C600`（1647 字节）。
  这函数把整份请求交了出来：
  ```
  0x147097E78 len=31  "https://www.paypal.com/graphql/"   ← 基址，结尾带斜杠
  0x1470E9F98         5407 字符文档
  0x147109320 "operationName"  0x14711CCB0 "query"  0x14717D2E8 "variables"
  0x146F76688 "application/json"  0x146F79800 "approveMemberPayment"
  ```
  **注意这是路径式**（`graphql/approveMemberPayment`），与另外六个的**查询式**（`graphql?<Operation>`）不同。
- **十一个变量名**（原文拼写）：`token`、`selectedAddressId`、`preferredShippingAddressId`、
  `selectedFundingOptionId`、`preferredFundingOptionId`、`secondaryFundingOptionIds`、`preAuthorizationRequired`、
  `fundingMethodType`、`setStickyFiRequired`、`scaCompleted`、`experiences`；
  另有两个枚举字面量 `IFRAME`(0x146DB53D8)、`INSTANT`(0x146DB59A8)。
- **落码**：`Payments/PayPalPartnerApprove.cs` —— `BaseUrl`/`OperationName`/`Url`/`Document`（5407 逐字节）/
  `VariableNames`/`Envelope`/`ApproveAsync`。**变量由调用方给，本类不造默认值**：
  十一个里有七个是调用方的（支付方式 id、地址 id、token），造默认值等于让合作方接受一个**语义错误但合法**的请求。
- **接上调用者**（否则会被 R1331 的不变量拦下）：`PayPalGateway.AuthorizeAsync` **前置分支** ——
  会话里有 `paypal.partnerToken` 走合作方审批，**没有就照旧**走原来的 `orderId` 捕获 / 令牌化。
  返回的 `state` 不是 `COMPLETED`/`APPROVED` 就算未批准，并把 `cart.paymentId` 落进 `PaymentMethodId`。
- **产物确认走正向证据**（不是"搜不到就算了"）：`https://www.paypal.com/graphql/`、`mutation approveMemberPayment`、
  `fundingMethodType`、`preAuthorizationRequired` **在 UTF-16 下都能搜到**。

### 五要素

- **改了什么**：新增 `Payments/PayPalPartnerApprove.cs`、`tests/PayPalPartnerApproveTests.cs`（6 条）；
  `Gateways.cs`（`AuthorizeAsync` 前置分支）；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter PayPalPartnerApproveTests` → **6/6**；
  `orphan_documents.py` → **0**；`audit_document_constants.py` → **16 常量 / 0 问题**；
  产物 UTF-16 命中 4 串（见上）；尺寸 61,403,648 → **61,423,104**；内嵌 `f0aa7ed3dda2`。
- **数字变化**：套件 2687 → 见 METRICS 当前值（+6）；产物 +19,456 字节。
- **证据等级**：Observation —— 基址/操作名/信封键/内容类型/十一个变量名/两个枚举/文档 5407 字符，全部有地址。
  Inference —— `IFRAME`/`INSTANT` 属于 `fundingMethodType`（同函数内相邻，无赋值配对，故以常量暴露由调用方选）。
- **还剩什么**：`CurrencyConversion`(10406) 归宿；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1335 轮

- **`approveMemberPayment`(5407) 落地**：文档单引用点 → `sub_14110C600` 交出基址 `https://www.paypal.com/graphql/`
  （**路径式**，与另外六个的**查询式**不同）、信封三键、内容类型、**十一个变量名**、两个枚举 `IFRAME`/`INSTANT`。
- `PayPalPartnerApprove`（Document/Url/VariableNames/Envelope/ApproveAsync）**变量由调用方给，不造默认值** ——
  七个变量是调用方的，造默认值 = 让合作方接受语义错误但合法的请求。
- 接进 `PayPalGateway.AuthorizeAsync` 前置分支（有 `paypal.partnerToken` 才走，否则原路径不变）。
- 产物用**正向证据**确认（UTF-16 四串命中），不靠"搜不到"。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1335 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1335 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'PayPalPartnerApprove' not in text:
    text = text.replace(
        '| `0x1470E9FA4` | 5407 | `approveMemberPayment` | PayPal/Braintree 支付编排，缺端点 |',
        '| `0x1470E9FA4` | 5407 | `approveMemberPayment` | **R1335 已落地**：`PayPalPartnerApprove`，'
        '端点 `https://www.paypal.com/graphql/approveMemberPayment`（路径式）|')
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
