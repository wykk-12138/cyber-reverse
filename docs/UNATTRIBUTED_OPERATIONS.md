# 不可归属的 GraphQL 操作（R1352–R1353）

这六份文档的发送方**既无主机也无路径**，且三种静态手法都试过：

| 手法 | 做法 | 结果 |
|---|---|---|
| 主机扫描 | 扫发送方函数里的全部字面量 | 无 `http`、无 `graphql.json` |
| 路径扫描 | 扫 `api/` / `/graphql` / 含 `?` 的相对路径 | 无 |
| 调用方扫描 | 反编译出来是异步状态机 → 扫"谁 Start 了这个 MoveNext" | 三个调用方函数**字面量全为 0**（元数据，不是代码） |

| 操作 | 长度 | 声明集 |
|---|---|---|
| `getCart` | 3234 | `key`、`locale` |
| `createCartByStore` | 421 | `country`、`currency`、`locale`、`storeKey`、`taxMode` |
| `createMyPayment` | 493 | `amount`、`customFields`、`key`、`paymentInterface`、`paymentMethod` |
| `initiateCheckout` | 251 | 无 |
| `saveAddress` | 296 | `address`、`editAddress`、`saveAddress`、`setDefault` |
| `maintainShippingGroups` | 223 | `cartId` |

**需要什么才能定**：一次**运行期抓包**，看到这些操作实际打到哪个主机。
静态一律到此为止 —— 再往下的推断没有证据支撑。

另有两条不是"无主机"，而是**别的语境缺失**：

- `approveMemberPayment` 有两份方言（5407 / 5620 字符），**选择条件**不明；
- `/cartApi/checkout` 有完整变量（cartType / lineItems / locationId / sourceSystem，值 Retail / Shopify）但**没有发送方 URL**。

## 无独立操作名字符串的（R1358）

| 操作 | 长度 | 情况 |
|---|---|---|
| `CreditCard` | 2867 | `ida.py str "CreditCard"` 只回元数据（`CreditCard*CreditCardNetworkType`、`ICreditCards`） |
| `getShippingMethods` | 531 | 只回别处的 PascalCase 闭包名 |

**这两份不能靠"名字 → 处理器"定位**，需要别的入口（调用点或运行期）。
