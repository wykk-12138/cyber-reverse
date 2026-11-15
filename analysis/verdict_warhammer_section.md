### Warhammer：403 不等于 404，所以不动它

`WarhammerFlow` 用的是 REST 假设：

```
GET  api.prod.warhammer.com/api/products/{code}
POST api.prod.warhammer.com/api/basket/items
POST api.prod.warhammer.com/api/orders
```

抓包显示店铺实际在跑 GraphQL：

```
POST https://api.prod.warhammer.com/graphql
```

Next.js 前端（`/_next/static/`）+ 自建 `/api/i18n` + GraphQL 网关。

### 但探测结果不支持"REST 路径错了"

```
products (REST)    HTTP 403   42B  [application/json]
basket (REST)      HTTP 403   42B  [application/json]
orders (REST)      HTTP 403   42B  [application/json]
POST /graphql      HTTP 202  2,075B [text/html]      <- 挑战页
```

**`403` 加 `application/json` 说明路由存在**——只是拒绝未认证请求。
如果是路径不存在，会返回 404 或 HTML。

**这和 `jbhifi` 那次完全不同**：那次是 `/cart.js` 返回了 Shopify 的 cart 对象，
**A 级证据说"这是 Shopify"**。这次只有"被拦了"，**D 级证据，不能改**。

### 三个不同强度的信号

| 信号 | 含义 | 能推断什么 |
|---|---|---|
| `404` + HTML | 路由不存在 | 路径错了 |
| `403` + JSON | 路由存在，拒绝未认证 | **路径可能对** |
| `200` + 平台特征 | 路由存在且响应 | **确定是对的** |

**只有第三种允许改代码。** 第二种只能记录"需要认证"。

### 所以 WarhammerFlow 保持原样

REST 路径可能是对的（403 JSON 支持这一点），也可能是错的（GraphQL 是实际走的路径）。
**两种可能都存在时，不动。**

`WarhammerEndpointTests` 把这三条探测结果记下来了，包括那个容易误判的 403-JSON。

### 一个值得记的判据

**HTTP 状态码本身不够，还要看响应体格式。**

- `403` + 两行 JSON = "我知道你在问什么，但你没权限"
- `403` + 一大坨 HTML = "我拦了你，别问了"
- 42 字节的 JSON 说明后端真的处理了这个请求

这个区别决定了"改代码"还是"记限制"。

---
