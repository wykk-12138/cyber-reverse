# 未结案项清单（R1364 收口）

**65 个 GraphQL 操作里，54 个已落地**；以下 11 条是剩下的，每条写明**缺什么证据、拿到后怎么验、验完落哪里**。
所有「静态三探」（主机扫描 / 路径扫描 / 状态机调用方）/「操作名 → 处理器」的结论都在这一栏里，**不要重跑**。

---

## 一、缺运行期抓包（5 条：发送方既无主机也无路径）

| 操作 | 长度 | 文档声明 | 已试过 |
|---|---|---|---|
| `createCartByStore` | 421 | `$country`、`$currency`、`$locale`、`$storeKey`、`$taxMode` | 同上 |
| `createMyPayment` | 493 | `$amount`、`$customFields`、`$key`、`$paymentInterface`、`$paymentMethod` | 同上 |
| `initiateCheckout` | 251 | 无 | 同上 |
| `maintainShippingGroups` | 223 | `$cartId` | 同上 |

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

---

## 七、异步名长尾（R1366 新增）

`python analysis/async_tail.py --family store` → **34 个**原版有、复刻件没有的店铺异步名；
`--family payment` → **64 个**。完整名单与三条限制见 `docs/ASYNC_TAIL.md`。

**已证**：这些名字**只以 `<Name>d__NN` 状态机串存在**，没有独立操作名可跟（`GetCartId`/`GetCartCsrf`/`GetCartItemId`
三个都试过）。**所以这一队列要按地址逐条反编译，不能按名。**

**已落地其一**：`saveAddress`(296) → `StoreSessionQueries`（长尾里的 `SaveAddress` 名字与文档互证）。

---

## 八、一条方法论纠正（R1368）

R1358 曾把 `CreditCard` 与 `getShippingMethods` 判为"没有独立操作名字符串"。**两者都有**：

| 操作 | 独立串地址 | 两个处理器 |
|---|---|---|
| `CreditCard` | `0x146BA9704` | `api/checkout/v1/orders/<id>/finalize`（已落地）/ Nike NL 变体 |
| `getShippingMethods` | `0x14703FA94` | Magento 费率字段 / PANINI 族 |

**错因**：`ida.py str <名> --limit 8` 先返回八个 PascalCase 闭包名就截断了。

> **一次被截断的搜索不是"不存在"的证据。** 反向结论必须用不截断的检索，或换地址直查。

`getShippingMethods` 仍未落地：两个处理器**都没有主机**，需要抓包。

---

## 九、`getShippingMethods` 已结案（R1369）

不是"缺主机"，是**它本来就不该有主机**：文档是 Magento 2 的运费查询，端点就是店铺自己的 `/graphql`。

- 实现：`MagentoCart.GetShippingMethodsAsync`，端点与地址变量由调用方给；
- **文档引用 12 个变量、声明 0 个** —— 保持原样，`MagentoCartTests` 断言 `$region` 存在而 `$region:` 不存在。
