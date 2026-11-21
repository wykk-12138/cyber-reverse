"""R1333 record: the cartApi family's endpoint, found — and why six documents had no home."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1333 轮：六份"无归宿"文档的端点找到了——`https://themeapis.<host>/cartApi/checkout`

- **一直在问"这些文档发给谁"**。这轮直接搜路径：`/cartApi/checkout`（`0x146AB27FC`），
  **`.text` 里只有一个引用点**（`0x140C32483`，`sub_140C32160`，1072 字节）——按单引用点判据，这是专用串。
- **反编译把 URL 的拼法说全了**：
  ```
  v43 = sub_141CF82E0(v42, "www", "themeapis");            // 两个主机标签
  v44 = sub_141CF62D0("https://", v43, "/cartApi/checkout"); // https:// <v43> /cartApi/checkout
  ```
  同一函数里的字段名是 `cartType` / `couponReferences` / `lineItems` / `locationId` / `sourceSystem`，
  取值 `Retail` / `Shopify`；另有 `https://themeapis.`（`0x14708885C`）与 `themeapis`（`0x14716CAE4`）两个字面量。
  **结论**：这一族（`createCart`/`updateMyCart`/`addPaymentToCart`/`SubmitOrder`/`OnboardGuestMutation`/
  `CurrencyConversion`/`approveMemberPayment`）挂在**店铺自己的 `themeapis.` 子域**下，路径 `/cartApi/checkout`，
  **不是 PayPal 的 `/graphql`**。
- **这解释了为什么六份文档一直没有归宿**：它们不属于 PayPal 挑战流（`paypal.com/graphql?<Operation>` 那六个），
  而属于**店铺侧的购物车 API**。R1320/R1321 把 `createEmptyCart`/`updateMyCart`/`submitOrder`
  接到 `/graphql` 上，当时标的是 **Inference**，现在这条推断**存疑** —— 见下方"待纠正"。
- **本轮未改 `replica/src`**：端点形状有了，但**哪家店在用**还没有证据；把文档挂到某个店的 `themeapis.` 子域上仍是猜。
  上轮的 `EveryDocumentConstantHasAProductionCaller` 正在盯着这件事，所以我**不往 src 里放没有调用者的东西**。
  这是"不变量起作用"的第一例：它没有阻止我记录发现，只阻止我把猜测塞进产品代码。

### 待纠正（下一轮或抓到证据时）

- `MagentoCart` 的 `CreateEmptyAsync` / `AddProductAsync` / `SetBillingAsync` / `AddPaymentAsync` /
  `SubmitOrderAsync` / `ReadCartAsync` 都接收 `endpoint`，**调用方传的是 `<origin> + /graphql`**
  （`CasioFlow` / Warhammer）。若这一族其实在 `/cartApi/checkout`，那么这些调用点的默认值要改，
  而 `casio.graphqlPath` 这种会话覆盖**恰好**能让抓包时无需改码。**改了会破坏现有测试的假设，所以要有证据再动。**

### 五要素

- **改了什么**：只改文档（`docs/GRAPHQL_DOCUMENTS.md`、VERDICT、HANDOFF）。**未改 src 与 tests**，故不重发布、不重跑变异。
- **验证命令与输出**：`disp32_scan_any.py 0x146AB27F0` → **1 site**；`site_to_func.py` → `sub_140C32160`(1072B)；
  `names_at.py` → 11 个字面量（含 `CartType`/`LineItems`/`LocationId`/`SourceSystem`/`Retail`/`Shopify`/`https://`/`themeapis`/`www`）；
  `ida_strings` → `https://themeapis.` 与 `/cartApi/checkout`。
- **数字变化**：无（本轮无代码）。
- **证据等级**：Observation —— 单引用点、URL 拼接的两条指令、`https://themeapis.` 字面量、字段名清单。
  Inference（存疑，已标注）—— R1320/R1321 的"购物车与商品查询共用 `/graphql`"。
- **还剩什么**：确认哪家店用 `themeapis.`；据此纠正 `MagentoCart` 调用点的默认端点；
  `CurrencyConversion`(10406)、`approveMemberPayment`(5407) 的归宿；`AddressInput`；方言条件（blocker）。
"""

POINTER = """
---

## 第 1333 轮

- **六份"无归宿"文档的端点找到了**：`/cartApi/checkout`（`0x146AB27FC`，**单引用点** `sub_140C32160`）。
  反编译显示拼法是 `"https://" + (www|themeapis 主机) + "/cartApi/checkout"`，字段 `cartType`/`lineItems`/
  `locationId`/`sourceSystem`，取值 `Retail`/`Shopify`；另有 `https://themeapis.` 字面量。
  **这一族挂在店铺自己的 `themeapis.` 子域，不是 PayPal 的 `/graphql`。**
- **R1320/R1321 的"共用 /graphql"因此存疑**（当时标的就是 Inference）。改默认端点要有证据再动。
- **本轮未改 src** —— 端点有了但"哪家店在用"没有证据。上轮的不变量正在盯着：**它没阻止我记录发现，只阻止我把猜测塞进产品代码。**
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1333 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1333 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'cartApi/checkout' not in text:
    text += """
## 这一族文档发到哪里（R1333）

`createCart` / `updateMyCart` / `addPaymentToCart` / `SubmitOrder` / `OnboardGuestMutation` /
`CurrencyConversion` / `approveMemberPayment` 属于**店铺侧的购物车 API**，不是 PayPal 的挑战流。

- 路径字面量：`/cartApi/checkout`（`0x146AB27FC`），**`.text` 里只有一个引用点**（`sub_140C32160`，1072 字节）。
- 拼法（反编译原样）：`"https://" + (主机标签 www|themeapis) + "/cartApi/checkout"`；
  另有 `https://themeapis.`（`0x14708885C`）与 `themeapis`（`0x14716CAE4`）。
- 同函数的字段名：`cartType`、`couponReferences`、`lineItems`、`locationId`、`sourceSystem`；取值 `Retail`、`Shopify`。

**因此**：`MagentoCart` 里那些方法接收的 `endpoint` 由调用方传入（当前是 `<origin> + /graphql`），
这条默认值**存疑**，需要用一次抓包或一个明确的店来定，不要凭形状改。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md got the endpoint section')
