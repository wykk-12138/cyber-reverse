"""R1369 record: getShippingMethods lands as Magento 2's query, and a bracing mistake cost a restart."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1369 轮：`getShippingMethods` 是 **Magento 2** 的运费查询 —— 读全文就定案，不需要主机

- **把文档整份读完**（不再只看前 64 字符）：它选 `carrier_code`/`method_code`/`carrier_title`/`method_title`、
  `amount`/`base_amount`/`available`/`error_message`/`price_excl_tax`/`price_incl_tax`，
  地址参数用 Magento 的**蛇形**形状（`region_id`/`country_id`/`save_in_address_book`）
  —— **这是 Magento 2 GraphQL**，主机就是店铺自己的 `/graphql`，本来就不该由镜像给出。
- **一个必须钉住的细节**：文档**引用 12 个变量、声明 0 个**（`$region` 出现但没有 `$region:` 段）。
  **"补全声明"就是发另一个请求**，测试里专门断言 `Contains("$region")` 且 `DoesNotContain("$region:")`。
- **先查有没有现成的**（AGENTS §2.7c）：`where_is.py Magento` → `MagentoCart.cs` 已有该平台的文档与 `PostAsync`
  → **并入 `MagentoCart`**，不新造类。
- **一次低级事故**：第一次插入用 `rfind('}')` 定位类的收尾大括号 —— **那是文件最后一个括号，方法落到了类外**，
  `CS0103` 三个。`git checkout --` 还原后改成**从类声明做括号配对**（跳过字符串与注释），一次通过。
  **第 N 次证明"按最后一个括号插入"不是锚点。**
- **产物**：`query getShippingMethods` **UTF-16 与 ASCII 各命中 1**；尺寸 62,010,880 → **62,017,024**。

### 五要素

- **改了什么**：`MagentoCart.cs`（+1 文档 + `GetShippingMethodsAsync`）；
  `MagentoCartTests.cs`（+3，共 23）；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`MagentoCartTests` → **23/23**；`operation_gap.py` → 覆盖 **60/65**（缺 5）；
  `orphan_documents.py` → 0；产物双编码各命中 1；尺寸见上。
- **数字变化**：覆盖 59 → **60**；缺 6 → **5**；套件 +3；产物 +6,144 字节。
- **证据等级**：Observation —— 文档全文的字段与蛇形地址形状、`where_is` 的既有落位、双编码产物命中。
- **还剩什么**：5 条 —— `createMyPayment`(493)（Cybersource）、两方言、AO 三个体、Saucony 六步、
  `/cartApi/checkout` 归属、`AddressInput`、浏览器侧结账面。
"""

POINTER = """
---

## 第 1369 轮

- **`getShippingMethods`(531) = Magento 2 运费查询**：`carrier_code`/`method_code` + 蛇形地址参数。
  **并入 `MagentoCart`**（`where_is` 显示该平台文档已在此），接 `GetShippingMethodsAsync`。
- **文档引用 12 个变量、声明 0 个** —— 测试钉住"不要补声明"，否则发的是另一个请求。
- **事故一次**：用 `rfind('}')` 当类收尾 → 方法落到类外（`CS0103` 三个）；
  `git checkout --` 还原后改成**从类声明做括号配对**。
- 覆盖 59 → **60/65**，缺 6 → **5**；产物双编码各命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1369 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1369 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if 'Magento 2' not in text:
    text += """
---

## 九、`getShippingMethods` 已结案（R1369）

不是"缺主机"，是**它本来就不该有主机**：文档是 Magento 2 的运费查询，端点就是店铺自己的 `/graphql`。

- 实现：`MagentoCart.GetShippingMethodsAsync`，端点与地址变量由调用方给；
- **文档引用 12 个变量、声明 0 个** —— 保持原样，`MagentoCartTests` 断言 `$region` 存在而 `$region:` 不存在。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated: getShippingMethods closed')
