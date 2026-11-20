"""R1320 record: Magento's cart documents land, and Casio's dead /cart/add gets a working sibling."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1320 轮：镜像里三份 Magento 购物车文档逐字节落地，Casio 那条 404 的加购终于有了可用的兄弟路径

- **发现**：镜像里躺着三份**冻结的 GraphQL 文档**（UTF-16，按对象头长度解出，长度分别是 240 / 32 / 61）：
  - `0x1470FD624`：`mutation { addProductsToCart(cartId: "%CART_ID%", cartItems: [{ quantity: %QTY%, sku: "%SKU%" }])
    { cart { id items { id quantity } total_quantity prices { grand_total { value currency } } }
    user_errors { code message } } }`
  - `0x1470FD4C4`：`mutation { createEmptyCart }`
  - `0x14718FB74`：`{ customerCart { id total_quantity items { uid quantity } } }`
  **注意第一份用的是字面替换令牌** `%CART_ID%` / `%QTY%` / `%SKU%`，**不是 GraphQL 变量**——
  把它"顺手改成变量"就是换了一份请求，所以测试把三个令牌钉住了。
- **落码**：`Flows/MagentoCart.cs`——三份文档逐字节、`FillAddProducts`（含引号转义）、`Body`、
  `CreateEmptyAsync`、`AddProductAsync`。
  **`user_errors` 优先于 HTTP 状态**：Magento 拒绝一行时仍回 200，只看状态码会把失败当成功——这条单独有用例。
- **接进 `CasioFlow.AddToCartAsync`**：原来的实现 POST `/cart/add`，而且它自己的注释就写着**这条路 404**
  （AEM + Akamai，根相对路径全是 SPA 404）。现在 **GraphQL 优先、旧路径兜底**：
  有 sku → 建空车 → 加行 → 落 `cart` / `casio.cartTotal` / `casio.cartGrandTotal`；GraphQL 失败则落
  `casio.cartGraphQlError` 再走旧 POST。**旧路径的 404 注释保留**——那是一条发现，不是猜测。
- **我犯的一个错，也是这轮唯一一次返工**：我直接写了一个新的 `AddToCartAsync` 重写，编译报
  `CS0111 已定义了同名成员`——**`CasioFlow.AddToCartAsync` 早就在那里**。
  按 AGENTS §2.7c 该先跑 `where_is`。处理方式是把新逻辑**并进**既有方法而不是并存，并把旧路径留作兜底。

### 五要素

- **改了什么**：新增 `replica/src/Cybersole.Stores/Flows/MagentoCart.cs`、
  `replica/tests/Cybersole.Tests/MagentoCartTests.cs`（9 条）；`RetailFlows.cs` 的 `CasioFlow.AddToCartAsync`
  改为 GraphQL 优先 + 旧路径兜底；新增 `analysis/read_magento_cart.py`；NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter "MagentoCartTests|Casio"` → **42/42**；
  产物搜 `MagentoCart` **2**、`%CART_ID%` **1**、`createEmptyCart` **1**、`customerCart` **1**；
  尺寸 61,295,104 → **61,314,560**；`artifact_freshness.py` → 内嵌 `99fd82630563 (is HEAD)`；
  `metrics_report.py` → 全部 exit 0；`mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**：套件 2626 → 见 METRICS 当前值（+9）；产物见上。
- **证据等级**：Observation —— 三份文档的地址与长度、三个替换令牌、产物四串命中。
  Inference —— 购物车与商品查询共用 `/graphql`（无反证，`casio.graphqlPath` 可覆盖）。
- **还剩什么**：`approveMemberPayment` / `addBillingAddressToCart` / `addToCart(query)` 等**另外几份**冻结文档
  还没落地（下一步）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1320 轮

- 镜像里三份 **Magento GraphQL 购物车文档**逐字节落地（240/32/61 字符），`addProductsToCart` 用的是
  **字面替换令牌** `%CART_ID%`/`%QTY%`/`%SKU%` 而非 GraphQL 变量——测试把令牌钉住了。
- `MagentoCart`（`FillAddProducts` / `CreateEmptyAsync` / `AddProductAsync`），**`user_errors` 优先于 HTTP 200**。
- `CasioFlow.AddToCartAsync` 原来是 POST `/cart/add`（自带注释承认 404）；现在 **GraphQL 优先 + 旧路径兜底**。
- 返工一次：我直接写了新的 `AddToCartAsync`，撞 `CS0111`——它早就存在。**该先跑 `where_is`。**
- 还留着没落地的冻结文档：`approveMemberPayment`、`addBillingAddressToCart`、`addToCart(query)`、`buynow`。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1320 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1320 \u8f6e')
