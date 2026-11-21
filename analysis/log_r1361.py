"""R1361 record: UpdateShippingAddress joins the api/graphql family, and its other handler is Salesforce's."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1361 轮：`UpdateShippingAddress` 归入 `api/graphql` 族 —— 而它**另一个**处理器是 **Salesforce SCAPI**

- **操作名两个引用点，指向两种传输**：
  - `sub_140E1DD80`：`api/graphql` + `Submit info` + `firstName`/`lastName`/`address1`/`address2`/`city`/
    `countryCode`/`phone` —— **就是 R1346 那个相对路径族**；
  - `sub_14098C830`：**`/scapi/ShopperBaskets/updateShippingAddressForShipment`** ——
    **Salesforce Commerce API**（`basketId`/`shipmentId`/`c_setAsDefault`/`c_saveAddress`/`locale`/`me`）。
- **所以它并入 `StorefrontApiQueries`**，而不是新造类；SCAPI 那条**记进文档、不实现** ——
  复刻件没有别的商业平台面，为一条路径造一套传输是过度延伸。
- **声明集**：`$input`（2386 字符文档）。
- **一处锚点失误**：常量锚点写成"133 characters **from** 0x147146994"，实际是 "**at**" —— 脚本报"找到 0 次"，
  改成与源码一致后通过。**锚点必须从源码复制，不能凭记忆写。**（这条已犯过多次，今天又犯一次。）
- **产物**：`mutation UpdateShippingAddress` UTF-16 命中 **1**；尺寸 61,970,944 → **61,979,136**。

### 五要素

- **改了什么**：`StorefrontApiQueries.cs`（+1 文档、+1 声明行、+1 switch 分支）；
  `StorefrontApiProductTests.cs`（+2 条，共 8）；新增 2 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`StorefrontApi*` → **8/8**；`operation_gap.py` → 覆盖 **50/65**（缺 15）；
  `orphan_documents.py` → 0；产物命中 1；尺寸见上。
- **数字变化**：覆盖 49 → **50**；缺 16 → **15**；套件 +2；产物 +8,192 字节。
- **证据等级**：Observation —— 两个处理器各自的路径与字段名、文档 2386 字符与 `$input`、产物命中。
- **还剩什么**：15 个 —— `UpdateCustomerForCart`(382)/`UpdateContactDetails`(244)/`SignInAsGuest`(453)（同窝未探）；
  `CreditCard`(2867)/`getShippingMethods`(531)（无操作名串）；`addToCartByChannel`(2271)；
  `updateShipAddress`(140)/`updateMyPaymentWithActions`(401)；
  五份无主机；两方言；浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；AO 三个体；Saucony 六步。
"""

POINTER = """
---

## 第 1361 轮

- `UpdateShippingAddress`(2386) **有两个处理器、两种传输**：`api/graphql`（相对路径族）与
  **Salesforce SCAPI**（`/scapi/ShopperBaskets/updateShippingAddressForShipment`）。
  **并入 `StorefrontApiQueries`**；SCAPI 那条**只记不实现**。
- 锚点失误一次：写成 "from 0x147146994"，源码是 "**at**" → 脚本报 0 次。**锚点必须从源码复制。**
- 覆盖 49 → **50/65**，缺 16 → **15**；产物 `mutation UpdateShippingAddress` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1361 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1361 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'Salesforce' not in text:
    text += """
## 一条操作、两种传输（R1361）

`UpdateShippingAddress` 的操作名有两个处理器：

| 处理器 | 路径 | 平台 |
|---|---|---|
| `sub_140E1DD80` | `api/graphql` | 已实现的相对路径族 |
| `sub_14098C830` | `/scapi/ShopperBaskets/updateShippingAddressForShipment` | **Salesforce Commerce API** |

只实现前者；SCAPI 那条**只记不实现**（复刻件没有其它商业平台面）。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
