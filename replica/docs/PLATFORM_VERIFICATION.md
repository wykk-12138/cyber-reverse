# 平台验证清单

> 为什么有这份文档：`Registry.cs` 里 40 个平台声明，**5 个是错的**（12.5%）。
> 它们都编译通过、都能跑、都返回响应，唯一的症状是业务静默失效。
> 这份清单是把那五轮排查的方法固定下来，新增或修改模块时先跑一遍。

---

## 一、九个已知误判

按发现顺序。每一行都有 A 级或 B 级证据——站点自己说出了"我是什么"，或者明确否认了某条路由。

| 模块 | 原注册 | 实际 | 决定性证据 |
|---|---|---|---|
| `hbx` | `ShopifyFlow` | 自建 `/api/v2/` + AWS WAF | `404 {"code":404,"message":"No route found for GET …products/….json"}` |
| `converse` | `ShopifyFlow` | Demandware `ConverseUS-Site` | `/on/demandware.store/Sites-ConverseUS-Site/…` |
| `bstn` | `ShopifyFlow` | 自建 `/api/beast/` + Adyen | `/api/beast/geoIP` + `/cart.js` 404 |
| `footpatrol` | `MagentoFlow` | **Shopify** | `/cart.js` → `{"token":"d1bee53c…"}` + `cdn.shopify.com` |
| `size` | `MagentoFlow` | **Shopify** | `/cart.js` → `{"token":"50e1612e…"}` + `cdn.shopify.com` |
| `funko` | `DemandwareFlow("Funko-Site")` | `DemandwareFlow("FunkoUS-Site")` | `/on/demandware.store/Sites-FunkoUS-Site/en_US/…` |
| `jbhifi` | 手写 `StoreFlow`（`/api/cart/add`） | **Shopify + 独立 OAuth** | `/cart.js` → 200 Shopify cart + `/.well-known/shopify/monorail/` |
| `offspring` | `MagentoFlow` | **SAP Commerce (Hybris)** | 页面含 `hybris`；`/view/component/basket/minibasketAjax` → 200 JSON |
| `supreme` | 手写 193 行（CSRF + `/shop/{id}/add`） | **Shopify** | `us.supreme.com/cart.js` → Shopify cart；页面调 `shopifysvc` 遥测 |

**共同点**：错误配置比缺失配置更难发现。缺失会报错，配错只是安静地不起作用。

`jbhifi` 是唯一一个"半对"的：OAuth 那半是对的，cart/checkout 那半是错的。
**同一个文件里对的和错的混在一起，比整块错更难发现**——登录能工作，会让人以为整个 flow 都能工作。

每个模块现在都有对应的断言钉在 `PlatformAssignmentTests` 里，改注册会让测试红。

---

## 二、特征路径表

每个平台有几条**只有它会用**的路径。探测这些比看 HTML 靠谱。

### Shopify

| 路径 | 期望 |
|---|---|
| `GET /cart.js` | `200` `{"token":"…","items":[…]}` |
| `GET /products/{handle}.json` | `200` `{"product":{…}}` |
| `/cdn/shop/` | 出现在 HTML 里 |
| `/.well-known/shopify/monorail/…` | 出现在网络请求里 |

**最强证据**：`/cart.js` 返回带 `token` 的 cart 对象。

### Magento / Adobe Commerce

| 路径 | 期望 |
|---|---|
| `GET /rest/V1/store/storeConfigs` | `200` JSON，含 `base_currency_code` / `store_name` |
| `GET /customer/section/load/?sections=cart` | `200` `{"cart":…}` |
| `/static/version…/frontend/` | 出现在 HTML 里 |
| `Magento_` / `mage/cookies` | 出现在 HTML 里 |

### Salesforce Commerce Cloud (Demandware)

| 路径 | 期望 |
|---|---|
| `/on/demandware.store/Sites-{SiteId}/…` | 出现在 HTML 或网络请求里 |
| `/on/demandware.static/Sites-{SiteId}/…` | 同上 |

**`SiteId` 就在路径里**，可以直接读到。

### Nike 系（Nike / Converse / Jordan）

| 特征 | 说明 |
|---|---|
| `x-kpsdk-v=j-1.2.988` | Kasada，和 Scheels 同一构建号 |
| `x-queueit-ajaxpageurl` | Queue-it 排队 |

### Next.js 自建

| 特征 | 说明 |
|---|---|
| `__NEXT_DATA__` | 出现在 HTML 里 |
| `/api/…` | 自建 API 前缀 |

### 其它已见

| 站点 | 特征 |
|---|---|
| Goat | `/web-api/`（**不是** `/api/`）+ `X-CSRF-TOKEN` |
| Scheels | Kasada（`apihub.scheels.com/…/fp?x-kpsdk-v=…`）+ `search.scheels.com/api/search` |
| HBX | `/api/v2/` + AWS WAF（`edge.sdk.awsswaf.com`） |
| BSTN | `/api/beast/` + Adyen |
| Converse | Demandware + Kasada + Queue-it |

---

## 三、证据强度分级（关键）

**只有 A 级才允许改注册。**

| 级别 | 含义 | 例 | 能改吗 |
|---|---|---|---|
| **A** | 站点**自报家门**，给出了"我是什么" | `/cart.js` 返回 Shopify token；`/on/demandware.store/` 路径 | ✅ 能 |
| **B** | 站点**明确否认**某条路由 | `404 "No route found for GET …json"` | ✅ 能 |
| **C** | 只确认"不是什么" | `/cart.js` 404，但无其它标记 | ❌ **不能** |
| **D** | 拿不到（DNS/TLS/停放/易主） | GoDaddy 停放页 | ❌ 不能 |

### C 级为什么不能改

`offspring.co.uk`：

```
/cart.js                          404
/rest/V1/store/storeConfigs       404
/customer/section/load/           404
主页标记                          无
```

**只知道它不是 Shopify 也不是 Magento，不知道它是什么。**

这时改注册只是**把一种错换成另一种**。正确做法是记进已知问题列表，等拿到 A/B 级证据。

### 域名失效的三种子情况

| 现象 | 例 | 危害 |
|---|---|---|
| 域名停放 | `saintalfred.com` → GoDaddy parking | 低（没人访问） |
| 域名 404 | `trophyroomstore.com` | 低 |
| **域名易主** | `sns.com` → 一家 IT 公司 | **高**：那个网站的 URL 会被路由进我们的 flow |

域名易主要**删 claim**，不是记录。

---

## 四、检查清单

新增或修改一个模块的注册时，按顺序做：

```
[ ] 1. 抓一次真实站点：dotnet run --project tools/NetworkCapture -- <url> 8 --scroll
[ ] 2. 看 hosts seen，找平台特征域名
       cdn.shopify.com      -> Shopify
       *.demandware.*       -> Demandware
       edge.sdk.awswaf.com  -> AWS WAF（自建）
       apihub.*/fp?x-kpsdk  -> Kasada
[ ] 3. 探测特征路径（见第二节）
[ ] 4. 给证据打 A/B/C/D 级
[ ] 5. A 或 B 级 -> 改注册，并在类注释里写明证据
[ ] 5b. 平台类型对不够：还要验证声明的标识符（site id / locale / region）
        在该站点上存在。funko 就是这个坑——Demandware 对了，
        但 Funko-Site 应该是 FunkoUS-Site，每个 controller 都 404
[ ] 6. C 级     -> 记进「已知未知平台」列表，不改
[ ] 7. 域名失效 -> 记进 DomainClaimTests.knownDead
[ ] 8. 域名易主 -> 删 claim
[ ] 9. 跑 PlatformAssignmentTests + DomainClaimTests
```

---

## 五、已探明的死域名

记在 `DomainClaimTests.EveryDeadDomainIsRecordedHereSoItIsNotRediscovered`：

| 域名 | 状态 |
|---|---|
| `saintalfred.com` | GoDaddy 停放页 |
| `sns.com` | 已易主（→ thrivenextgen.com），claim 已删 |
| `trophyroomstore.com` | 根路径 404 |
| `civilistberlin.com` | Sanity CMS，无电商 API |

---

## 六、已知未知平台（C 级，待查）

| 模块 | 现状 | 下一步 |
|---|---|---|
| ~~`offspring`~~ | **已定性**：SAP Commerce (Hybris)，新增 `HybrisFlow` | ✅ 解决 |
| `jdsports` | `__NEXT_DATA__` = Next.js 自建 | 需要专门的 flow |

---

## 七、还有哪些平台声明没验证过

| Flow 类型 | 数量 | 状态 |
|---|---|---|
| `ShopifyFlow` | 30 | ✅ 已验证（25 确认 + 3 改 + 4 域名问题 + 6 连不上） |
| `MagentoFlow` | 4 | ✅ 已验证（2 改 Shopify + 2 待查） |
| `DemandwareFlow` | 2 | ❌ 未验证 |
| `FootsitesFlow` | 1 | ❌ 未验证 |
| 其余单一 flow | 各 1 | 逐个已单独抓过 |

---

## 八、一条方法论

五轮排查里反复出现的模式：

> **拿不到数据时，先问「这份输入里到底有没有我要的东西」，
> 再决定是换输入还是改解析。**

应验过的场景：

- 分类页跑商品正则 → `sku` 全 MISS（数据不在这份输入里）
- 列表页找商品链接 → 静态 HTML 里一个都没有（JS 渲染）
- 编造商品 id → 路径对但实体不存在
- 探针复制模块的正则 → 测的不是那个东西

四次里有三次是"输入错了"，不是"解析错了"。

---
