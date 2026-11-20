"""R1312 round record: Casio is a Magento GraphQL store, and the flow now asks it a question."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1312 轮：Casio 不是靠扒页面的店，它答 Magento GraphQL——而且选择集里有三个自家属性

- **先证伪了自己的假设**：本想去解 `_timestamp`/`_hash` 这对签名。沿 `productCode` 的引用链一路下去，
  六个引用点里最大的两个是**PayPal 的 3DS JWT GraphQL 构造器**
  （`https://www.paypal.com/graphql?GetThreeDsJwtQuery`、`jwtIssuer`/`jwtOrgUnitId`/`jwtSpecification`、
  `contingencyContext`、`bankIdentificationNumber`、`checkoutuinodeweb_hermione`/`_weasley`）——
  与 Casio 无关。**而且这套复刻件已经有了**（`PayPalThreeDs.cs` 里全在），所以没有任何缺口可补。
  签名那对 `_timestamp`/`_hash` **本轮仍未解出**，如实记在下面。
- **真正的发现在 `casioid` 旁边**：`0x146A758CC` 起的冻结 UTF-16 串是一份 **Magento GraphQL 文档的字段选择尾部**：
  ```
  "]}},sort:{name:ASC},pageSize:40){items{sku name url_key stock_status only_x_left_in_stock
   casio_sales_type casio_can_purchase casio_sales_start_date casio_sales_end_date casio_image_url
   image{url label} price_range{minimum_price{final_price{value currency}}}} total_count}}
  ```
  **`casio_sales_type` / `casio_can_purchase` / `casio_sales_start_date` 是 Casio 自家属性**，标准 Magento 没有——
  这正是这家店不能当普通商品页扒的原因。而复刻件的 `CasioFlow.FindProductAsync` 一直是 `<title>` + 价格正则扒 HTML。
- **开头那个 `"]`** 也是证据：`]` 关不了对象，只能关**数组**，所以过滤器带的是列表——
  文档头必须是 `sku:{in:[` 而**不是** `sku:{eq:`。第一版我写成 `eq:` 又接上以引号开头的尾部，
  括号失衡，测试当场红了；改成 `in:[` 后括号才配平。
- **落码**：`Flows/CasioGraphQL.cs`——`ObservedSelection`（274 字符逐字节）、`Fields`（13 项）、
  `SearchDocument` / `SearchBody` / `SearchAsync`、`ReadProduct`、`CanBuy`
  （`casio_can_purchase` 优先于 `stock_status`：有货但未开卖是真实状态）。**文档头标 Inference**——
  捕获窗口里只有尾部，前半段没有。
- **接入**：`CasioFlow.FindProductAsync` 先问 GraphQL（有 `casio.sku`/`productSku` 时），
  拿到就落 `casio.canPurchase`/`casio.salesStart`/`casio.salesEnd`/`stock`/`sku`；**拿不到退回原来的 HTML 读取**——
  一个答错误的店不该让流程连商品页都不看了。
- **顺手修了自己的一个 bug**：`SearchAsync` 把绝对 URL 也拼到 origin 后面，得到 `http://hosthttp://host/graphql`。
  测试用的是 TinyServer 的绝对地址，所以这条只有跑起来才看得见。
- **产物复核（仍放在报告之前）**：`CasioGraphQL` **1** 次、`casio_can_purchase` **2** 次、
  `casio_sales_type` **1** 次命中；尺寸 61,270,016 → **61,284,864**。这次字符串**搜得到**，
  与上一轮 Square 的情况正好相反——同一套仪器，两种结果，说明它测的是真的。

### 五要素

- **改了什么**：新增 `replica/src/Cybersole.Stores/Flows/CasioGraphQL.cs`、
  `replica/tests/Cybersole.Tests/CasioGraphQLTests.cs`（12 条）；
  `RetailFlows.cs` 的 `CasioFlow.FindProductAsync` 加 GraphQL 分支 + HTML 回退；
  新增 `analysis/read_casio_graphql.py`、`analysis/fix_r1312_doc_head.py`；
  NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter CasioGraphQLTests` → **12/12**；
  `--filter FullyQualifiedName~Casio` → **24/24**（既有 Casio 用例无回归）；
  产物搜三个名字 → 1 / 2 / 1，尺寸 61,284,864；`artifact_freshness.py` → `state: current`；
  `metrics_report.py` → 全部 exit 0；`mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**：套件 2599 → 见 METRICS 当前值（+12）；产物见上。
- **证据等级**：Observation —— 274 字符选择集逐字节、13 个字段名、`pageSize:40`、`sort:{name:ASC}`、
  产物中三个串命中。Inference —— 文档头 `products(filter:{sku:{in:[`（由尾部 `"]}}` 的括号配平推出，
  前半段未捕获）。Unknown —— `_timestamp`/`_hash` 签名方案仍未解；GraphQL 端点的绝对路径
  （现用 `/graphql`，可由 `casio.graphqlPath` 覆盖）。
- **还剩什么**：Casio 的签名对；Casio 其余步骤（`SetAdyenPayment` d__6 等）；Saucony 六步 API 路径。
"""

POINTER = """
---

## 第 1312 轮

- **Casio 是 Magento GraphQL 店**：镜像 `0x146A758CC` 是一份 GraphQL 字段选择尾部，含三个**自家属性**
  `casio_sales_type` / `casio_can_purchase` / `casio_sales_start_date`。已落 `Flows/CasioGraphQL.cs`，
  并接进 `CasioFlow.FindProductAsync`（GraphQL 优先、HTML 回退）。产物中三个串均命中，尺寸 61,284,864。
- 尾部开头 `"]}}` 的 `]` 证明过滤器是**列表**（`sku:{in:[`），不是 `eq:`——第一版写错，测试当场抓到。
- 顺带证伪：`productCode` 的引用链通向 **PayPal 3DS JWT GraphQL 构造器**，与 Casio 无关，且复刻件已有。
- **`_timestamp`/`_hash` 签名仍未解**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1312 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1312 \u8f6e')
