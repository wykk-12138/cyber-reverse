### 契约覆盖扩到 7 组，每个平台误判都有断言守着

上轮 4 组，这轮加到 7 组：

| 测试 | 覆盖的结论 |
|---|---|
| `HbxServesItsCartEndpoints` | HBX 自建 `/api/v1/carts` |
| `OffspringServesItsHybrisControllers` | Offspring = Hybris |
| `TheStoresThatMustAnswerShopifyStillDo` | footpatrol / size / jbhifi = Shopify |
| `YeezyKeepsItsCartOnTheSwellHost` | Yeezy = Swell，且 cart 在平台子域 |
| **`FunkoUsesTheSiteIdThatActuallyAnswers`** | **site id 是 `FunkoUS-Site` 不是 `Funko-Site`** |
| **`ConverseIsDemandwareAndNotShopify`** | **Converse = Demandware，且 `/cart.js` 不是 Shopify** |
| **`ScheelsKeepsItsKasadaSensorEndpoint`** | **Scheels 的 Kasada 端点位置** |

### 新增的三个都用了「正反两面」的写法

```csharp
// funko：正确的 id 要通，错误的 id 要 404
var correct = CheckAsync(..., "Sites-FunkoUS-Site/...", r => r.StatusCode < 400, ...);
var wrong   = CheckAsync(..., "Sites-Funko-Site/...",   r => r.StatusCode >= 400, ...);

// converse：Demandware 路径要通，/cart.js 不能是 Shopify cart
var demandware = CheckAsync(..., "/on/demandware.store/Sites-ConverseUS-Site/...", ...);
var shopify    = CheckAsync(..., "/cart.js", r => !IsShopifyCart(r), ...);
```

**为什么两面都断言**：单项断言只能证明「A 是对的」，双向断言还能发现
「A 和 B 同时成立」这种矛盾状态——那说明**我理解的平台分裂了**。

实测输出：

```
funko Sites-FunkoUS-Site            HTTP 200  35B    [image/gif]    holds
funko Sites-Funko-Site (must NOT)   HTTP 404  1,122B  [text/html]    holds

converse on/demandware.store        HTTP 200  822KB   [text/html]    holds
converse /cart.js (must NOT)        HTTP 200  220KB   [text/html]    holds
```

### 又踩了同一个坑：`/cart.js` 的判据

`ConverseIsDemandwareAndNotShopify` 第一次跑就红了：

```
converse /cart.js (must NOT be a Shopify cart): HTTP 200 220,602B [text/html]
  CONTRACT BROKEN
```

**Converse 的 `/cart.js` 返回 200 + 220KB HTML。** 我的 `IsShopifyCart` 只查 body 里
有没有 `"token"`，而那个 HTML 页面里恰好有 CSRF token 之类的东西。

修法：加上 `content-type` 不含 `html` 这个前提。

**这是这个文件第二次因为「只查 body 不查类型」而误判。** 上轮是
`text/javascript` 被 `IsJson` 拒；这轮是 `text/html` 被 `IsShopifyCart` 收。

**两次都是我把「形状」理解得太窄。**

### 现在的状态

```
LiveContractTests: 7 个测试，13 个端点，全部 PASS
```

八个平台误判里，七个有 contract 守着（`bstn` 没有——它的 `/api/beast/` 需要更复杂的
请求才能验，留给下轮）。

---
