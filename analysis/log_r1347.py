"""R1347 record: clustering by address, and the rule that decided the block's membership."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1347 轮：按**地址聚类**找族——并且守住一条界线：邻居只是线索，**主机才是证据**

- **先聚类，不先派活**：`.operations_in_image.json` 里 39 个未覆盖操作**按地址排序、按 0x4000 间隔切块**，
  三块立现：
  ```
  A  15 个  17654 字符   0x1470ef5fc..0x1470f5b24   cartApiObjectCreate / createCart / setBillingAddress …
  B   7 个   8127 字符   0x14714348c..0x147146f94   generateClientToken / getCart / getPaymentdMethods …
  C   3 个   6985 字符   0x14713ab24..0x14713e034   ShopProductSearch / addToCart / buynow
  ```
- **C 块最小，先验证再动手**：`ShopProductSearch` 的发送方（`0x140D26050`，1264 字节）带
  **`https://server.shop.app/graphql`**，变量 `brokerId`/`filter`/`first`/`inStock`/`includeProductFilters`/`key`/`searchKind`，
  标签 `SHOP_STORE_PRODUCT_SEARCH` —— **与 `ProductDetails` 同一个主机**，所以归 Shop app。
- **但邻居 `addToCart`/`buynow` 的发送方（`0x140B60250`）没有任何主机**，只有店铺购物车词汇
  （`handle`/`qty`/`sku`/`type`/`simple`）。**所以它们不属于这一族，本轮不并入。**
  **这正是本轮要守的界线：地址接近把人带到块里，主机决定谁进这个类。**
- **落码**：`ShopAppProduct` 增 `SearchOperation`/`SearchDocument`(6537)/`SearchVariableNames`/`SearchAsync`；
  `ShopifyFlow.FindProductAsync` 增搜索分支（`shopapp.searchKey` 触发）。
- **产物**：`query ShopProductSearch` UTF-16 命中 **1**；尺寸 61,739,520 → **61,766,144**。
  （`shopapp.searchKey` 那个会话键两编码都没命中 —— 按 §4.5 无结论。）

### 五要素

- **改了什么**：`ShopAppProduct.cs`（搜索）；`ShopifyFlow.cs`（搜索分支）；`ShopAppProductTests.cs`（+3 条，共 9）；
  新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`ShopAppProductTests|ShopifyGraphQlTests` → **21/21**；
  `operation_gap.py` → 覆盖 **27/65**（缺 38）；`orphan_documents.py` → 0；`audit_document_constants.py` → **30 常量 / 0 问题**；
  产物命中 1；尺寸 61,739,520 → 61,766,144。
- **数字变化**：覆盖 26 → **27**；缺 39 → **38**；套件 +3；产物 +26,624 字节。
- **证据等级**：Observation —— 三块地址聚类的成员与字符数、两个发送方的主机差异、搜索文档与七个变量、产物命中。
- **还剩什么**：A 块（15 个，17654 字符）与 B 块（7 个，8127 字符）；`approveMemberPayment` 两方言；
  浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1347 轮

- **按地址聚类** 39 个未覆盖操作（0x4000 间隔切块）→ 三块：A 15 个/17654、B 7 个/8127、C 3 个/6985。
- **邻居只是线索，主机才是证据**：C 块里 `ShopProductSearch` 的发送方带 `server.shop.app` → 归 Shop app 并落地；
  同块的 `addToCart`/`buynow` **没有任何主机** → **不并入**。
- `ShopAppProduct` 增搜索（6537 字符文档 + 七个变量 + `SearchAsync`），`ShopifyFlow` 增搜索分支。
- 覆盖 26 → **27/65**，缺 39 → **38**；产物 `query ShopProductSearch` UTF-16 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1347 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1347 \u8f6e')
