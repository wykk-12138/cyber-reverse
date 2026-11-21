# 未结案项清单（R1364 收口）

**65 个 GraphQL 操作里，54 个已落地**；以下 11 条是剩下的，每条写明**缺什么证据、拿到后怎么验、验完落哪里**。
所有「静态三探」（主机扫描 / 路径扫描 / 状态机调用方）/「操作名 → 处理器」的结论都在这一栏里，**不要重跑**。

---

## 一、缺运行期抓包（5 条：发送方既无主机也无路径）

| 操作 | 长度 | 文档声明 | 已试过 |
|---|---|---|---|
| `getCart` | 3234 | `$key`、`$locale` | 主机 / 路径 / 调用方三探全空 |
| `createCartByStore` | 421 | `$country`、`$currency`、`$locale`、`$storeKey`、`$taxMode` | 同上 |
| `createMyPayment` | 493 | `$amount`、`$customFields`、`$key`、`$paymentInterface`、`$paymentMethod` | 同上 |
| `initiateCheckout` | 251 | 无 | 同上 |
| `maintainShippingGroups` | 223 | `$cartId` | 同上 |
| `saveAddress` | 296 | `$address`、`$editAddress`、`$saveAddress`、`$setDefault` | 同上 |

**需要**：一次运行期抓包，看到这些操作打到哪个主机（`getCart` 一份即可推出同族其余）。

**拿到后**：若主机与 `StoreSessionQueries` 的 origin 相同 → 把对应文档加进那个类（声明集已在表里）；
若是别的主机 → 新开一个类，沿用「origin 由调用方给」的写法。

---

## 二、缺「选哪个处理器」的条件（2 条）

| 情况 | 现状 |
|---|---|
| `approveMemberPayment` 两份方言 | 5407 字符（0x1470E9FA4，已用）/ 5620 字符（0x1470EC9FC），**选择条件不明** |
| `UpdateContactDetails` 两个处理器 | 一个 `https://`+host+`/graphql`（已用），一个按哈希（未用） |
| `updateShipAddress` / `getCartCookie` 族 | 已按哈希实现，**但哈希与操作的配对未成立**（两个 64 位值对三个操作） |

**需要**：一次抓包看到实际用的是哪一份（或哪一对哈希）。
**拿到后**：把条件写成一个 `Session.Vars` 开关 + 测试钉住，**不要按"看起来更新"来选**。

---

## 三、缺界面上下文（2 条）

| 项 | 现状 |
|---|---|
| 浏览器侧结账面（`checkoutuinodeweb_hermione`、`x-paypal-internal-euat`、`paypal-client-metadata-id`） | `PayWithQuery` 的第二条传输，**未实现**；合作方那条已实现 |
| `AddressInput` 的形状 | 多个文档引用它，**镜像里没有它的字段列表**；实现里由调用方给 |

**需要**：一次带浏览器上下文的抓包（前者的请求头与 body；后者一个真实 `AddressInput` 实例）。

---

## 四、缺平台/协议面（3 项）

| 项 | 现状 |
|---|---|
| `/cartApi/checkout` | 变量完整（`cartType`/`lineItems`/`locationId`/`sourceSystem`，值 `Retail`/`Shopify`），**发送方 URL 未定位** |
| AO 三个 checkout body（`/v2/app/{contact,delivery,payment}`） | 未落地 |
| Saucony 六步路径 | 未落地 |
| Salesforce SCAPI（`/scapi/ShopperBaskets/...`） | `UpdateShippingAddress` 的另一条传输，**只记不实现** |

**需要**：各自的抓包或文档；**不要用"看起来像"补**。

---

## 五、本清单之外的两个约定

1. **文档声明集 > 发送方字段集**：三个案例（`addToCartByChannel`、`PayWithQuery`、`CurrencyConversion`）证明
   发送方会提到文档不接受的字段 —— **以文档为准**，多出来的字段是发送方别处的记账。
2. **错拼照抄**：`expeirences`、`getPaymentdMethods` 等是镜像原文，**改对就是发另一个请求**。

---

## 六、复核入口（第三方可重算）

```
python analysis/operation_gap.py         # 覆盖 54/65
python analysis/orphan_documents.py      # 文档常量必须有生产调用者（0）
python analysis/audit_document_constants.py
python tools/metrics_report.py           # 全量套件 + 五项度量
python tools/mutation-check.py           # 变异套件
```
