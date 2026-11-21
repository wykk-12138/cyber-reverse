"""R1336 record: CurrencyConversion lands, including the variable the image spells wrong."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1336 轮：`CurrencyConversion`(10406) 落地——镜像把一个变量名拼错了，我照它拼

- **同一套方法第二次奏效**：文档 `0x1470D0FB4`（10406）→ **单引用点** `0x14110FB42` → `sub_14110F8C0`（1173 字节）。
  发送方交出：
  ```
  0x147097E78 "https://www.paypal.com/graphql/"   ← 与审批**同一个基址**
  0x146BAAEC8 "CurrencyConversion"
  0x147171D48 "token"   0x146FD6F98 "conversionType"   0x1470210A8 "expeirences"
  0x146F1AF90 "VENDOR"
  ```
- **关键发现：`expeirences`（sic）**。文档声明的是 `$experiences`，而**发送方写的是 `expeirences`**。
  **这不是该修的错别字，是要照抄的行为** —— 改成正确拼写就是一次伪装成"顺手清理"的行为变更。
  钉了一条测试，并在断言旁边写明理由：它是**防未来的人来"修"它**的。
- **落码**：`Payments/PayPalPartnerCurrency.cs` —— `BaseUrl`（**引用** `PayPalPartnerApprove.BaseUrl`，不重复写字面量）/
  `OperationName` / `Url` / `Document`(10406 逐字节) / `VariableNames`(`token`,`conversionType`,`expeirences`) /
  `ConversionTypeVendor` / `Envelope` / `ConvertAsync`。
- **接上调用者**：`PayPalGateway.AuthorizeAsync` —— **有 `paypal.conversionType` 就先换汇、再审批**，两次请求顺序被测试钉住。
- **产物证据**（正向）：`mutation CurrencyConversion` 在 **UTF-16 命中 1**；尺寸 61,423,104 → **61,449,728**。
  **`expeirences` 两种编码都搜不到** —— 按 §4.5 这**不推出任何结论**（存储是混合的）；
  它的证据是**行为级**的：测试断言请求体里确实带 `expeirences`。

### 五要素

- **改了什么**：新增 `PayPalPartnerCurrency.cs`、`PayPalPartnerCurrencyTests.cs`（6 条）；
  `Gateways.cs`（换汇前置分支）；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter PayPalPartnerCurrencyTests` → **6/6**；
  `orphan_documents.py` → **0**；`audit_document_constants.py` → **17 常量 / 0 问题**；
  产物 `mutation CurrencyConversion` UTF-16 命中 1；尺寸 61,423,104 → 61,449,728；内嵌 `05f708a5813f`。
- **数字变化**：套件 2694 → 见 METRICS 当前值（+6）；产物 +26,624 字节。
- **证据等级**：Observation —— 基址/操作名/三个变量键（含错拼）/枚举/文档 10406 字符，全部有地址。
- **还剩什么**：`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径；
  `createCart`/`updateMyCart`/`SubmitOrder` 是否该改到 `/cartApi/checkout`。
"""

POINTER = """
---

## 第 1336 轮

- **`CurrencyConversion`(10406) 落地**（方法同 R1335：文档单引用点 → 读发送方）。
  端点与审批**共用基址** `https://www.paypal.com/graphql/`，操作名 `CurrencyConversion`。
- **镜像把变量名拼成 `expeirences`（sic）**，文档里是 `$experiences`。**照抄，不修** ——
  修了就是伪装成清理的行为变更。已钉测试并在断言旁写明理由。
- 接进 `PayPalGateway.AuthorizeAsync`：**有 `paypal.conversionType` 先换汇再审批**，顺序被测试钉住。
- 产物：文档 UTF-16 命中 1；`expeirences` **两编码都搜不到**，按 §4.5 **无结论**，
  行为证据来自测试对请求体的断言。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1336 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1336 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'PayPalPartnerCurrency' not in text:
    text = text.replace(
        '| `0x1470D0FB4` | 10406 | `CurrencyConversion` | 结账换汇，缺端点 |',
        '| `0x1470D0FB4` | 10406 | `CurrencyConversion` | **R1336 已落地**：`PayPalPartnerCurrency`，'
        '端点 `https://www.paypal.com/graphql/CurrencyConversion`；变量键 `token`/`conversionType`/'
        '**`expeirences`**（镜像原拼写，勿修）|')
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
