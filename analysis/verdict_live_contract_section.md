### Live 契约测试：让"验过一次"变成"一直被验"

之前每个端点的状态都写在这份文档里，靠人记。这轮把它们变成会自己跑的断言。

新增 `LiveContractTests`（4 个测试，`Speed=Slow`）：

| 测试 | 断言 |
|---|---|
| `HbxServesItsCartEndpoints` | `/api/v1/carts` 存在（405 = 要 POST，不是没路由） |
| `OffspringServesItsHybrisControllers` | `minibasketAjax` + `getUserInfo` 都返回 JSON |
| `TheStoresThatMustAnswerShopifyStillDo` | `footpatrol` / `size` / `jbhifi` 的 `/cart.js` 仍返回 Shopify cart |
| `YeezyKeepsItsCartOnTheSwellHost` | `yzy-prod.swell.store/api/cart` 存在；`yeezy.com/api/cart` **不**提供 cart |

### 三个设计原则

写在文件头注释里：

1. **只断言真正观察到的。** 观察到过一次的端点是契约；从文档推断的不是，不进这个文件。
2. **失败消息要点名后果。** 红了要读作「HbxFlow 的购物车没了」，而不是「assert 1 失败」。
3. **明确区分"被拒"和"消失"。** 403/406/429 说明站点拒绝探测，不等于端点没了。
   这个区分决定了是「改代码」还是「等一会再试」。

### 第一次跑，三个契约是我自己写错的

**一、Shopify 的 `/cart.js` 不是 `application/json`**

```
footpatrol /cart.js   HTTP 200  303B  [text/javascript]
```

我按 `IsJson` 判，直接红了。**但 body 是标准的 Shopify cart 对象。**
契约应该是响应体形状，不是 CDN 顺手贴的 MIME 标签。

**二、Swell 的 `/api/cart` 返回 401**

```
swell /api/cart   HTTP 401  152B  [application/json]
```

401 是「要会话」，不是「端点没了」。`IsJson` 要求 `IsSuccess`，把它判成了 broken。

**三、HBX 的 `/api/v2/shop/countries` 返回 406**

```
hbx /api/v2/shop/countries   HTTP 406  184,797B  [text/html]
```

`406 Not Acceptable` —— 我没设 `Accept` 头。加上 `Accept: application/json` 后仍然是 406，
但至少现在它被正确归类为「被拒」而不是「端点消失」。

**三次都是同一个错**：把「响应不符合我预期的形状」当成了「端点坏了」。

**这正是这份文件想防的那个错，而它第一次跑就自己犯了。**

### 修完的结果

```
HbxServesItsCartEndpoints              PASS
  /api/v1/carts              HTTP 405  43B   [application/json]   holds
  /api/v2/shop/countries     HTTP 406  184KB  [text/html]         refused (not broken)

OffspringServesItsHybrisControllers    PASS
  minibasketAjax             HTTP 200  1,164B  holds
  getUserInfo                HTTP 200  419B    holds

TheStoresThatMustAnswerShopifyStillDo  PASS
  footpatrol /cart.js        holds
  size /cart.js              holds
  jbhifi /cart.js            holds

YeezyKeepsItsCartOnTheSwellHost        PASS
  yzy-prod.swell.store/api/cart   HTTP 401 JSON   holds (guarded)
  yeezy.com/api/cart              HTTP 403        refused (correctly not a cart)
```

### 为什么这个和 mock 测试不冲突

| | mock 测试 | live 契约测试 |
|---|---|---|
| 验什么 | 代码读 fixture 读得对不对 | 站点还在不在那个位置 |
| 什么时候红 | 改了解析逻辑 | 站点变了 |
| 能发现 | 解析 bug | **平台漂移** |

R47–R69 期间发现的八个平台误判，**没有一个能被 mock 测试发现**——因为 mock 是我按
自己的理解写的。只有打到真实站点才能发现"我理解的平台是错的"。

**现在那八个结论各有一条 live 断言守着。**
