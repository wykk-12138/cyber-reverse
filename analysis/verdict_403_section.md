### 一个推理被推翻了：403 + JSON 不代表「路由存在」

R59 我写过一条判断标准：

> `403` + 两行 JSON = 「我知道你在问什么，但你没权限」→ 路由可能对
> 所以 `warhammer` 的 REST 路径「不能断定是错的」

**这条推理错在它假设 403 会区分路径。**

### 对照实验

抓包显示店铺真实调的是 `www.warhammer.com/api/i18n`（200）。于是把同一组路径
分别打到两个主机上：

```
www.warhammer.com/api/i18n             HTTP 200  13,368B  [application/json]   ← 真端点
www.warhammer.com/api/products/…       HTTP 404   4,642B  [text/html]         ← 不存在
www.warhammer.com/api/basket/items     HTTP 404   4,642B  [text/html]         ← 不存在
www.warhammer.com/api/orders           HTTP 404   4,642B  [text/html]         ← 不存在

api.prod.warhammer.com/api/i18n        HTTP 403      42B  [application/json]
api.prod.warhammer.com/api/products/…  HTTP 403      42B  [application/json]
api.prod.warhammer.com/api/basket/…    HTTP 403      42B  [application/json]
```

**关键在最后三行**：`api.prod.warhammer.com` 对一个**已知存在**的路径（`/api/i18n`，
在另一个主机上返回 13 KB JSON）也返回 **403 + 42 字节**。

**说明这个 403 是 WAF 的通用拒绝，不携带任何路径信息。**

### 修正后的判据表

| 信号 | 含义 | 能推断什么 |
|---|---|---|
| `404` + HTML | 路由不存在 | **路径错了** |
| `403` + 极短 JSON，且**同一路径在别处能通** | WAF 通用拒绝 | **什么都不能推断** |
| `403` + 短 JSON，且没有对照 | 未知 | 需要对照实验 |
| `200` + 平台特征 | 路由存在且响应 | **确定是对的** |

**R59 那条「403+JSON = 路由存在」要加一个前提：必须先证明同一个 403 只出现在可疑路径上。**

### 所以 `warhammer` 的状态反而更糟了

之前记的是「403 被拦，D 级证据，不能改」。

**现在知道那个 403 连"被拦的是这个路径"都证明不了**——它是无差别的。

**`WarhammerFlow` 的三条 REST 路径现在没有任何证据支持**：既没有 200 证明对，
也没有 404 证明错。

### 但也不是没有收获

`www.warhammer.com/api/i18n` 返回 **13,368 字节的真实 JSON**（多语言文案）。
这说明：

- 站点有 `/api/` 前缀，但只有内容类端点
- 商品/购物车/订单走的是 **GraphQL**（`api.prod.warhammer.com/graphql`），不是 REST

**所以 `WarhammerFlow` 用 REST 假设本身可能就是错的**——只是现在没有证据能确认。

### 修了一处：`WarhammerFlow` 的注释

原来写的是「403 + JSON 说明路由存在」。改成记录了对照实验结果，
并说明「三条 REST 路径现在没有任何证据支持」。

---
