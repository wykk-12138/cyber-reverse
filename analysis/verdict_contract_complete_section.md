### 八个平台误判，八个 contract

`bstn` 是最后一个。它通过，而且带回来一个之前没验过的数据点：

```
bstn /api/beast/geoIP    HTTP 200  112B   [application/json]   holds
bstn /cart.js (must NOT) HTTP 404  47,536B [text/html]         holds
```

`/api/beast/geoIP` 返回 200 + 112 字节 JSON —— **这是 R25 之后第一次真正拿到它的响应体**。
之前只知道"这个前缀存在"（因为 geoIP 和 monetate 都在它下面），现在知道 geoIP 具体返回什么形状。

### 完整的契约表

| 误判 | contract | 正反两面 |
|---|---|---|
| `hbx` | `HbxServesItsCartEndpoints` | `/api/v1/carts` 存在 + `/api/v2/` 被拒 |
| `converse` | `ConverseIsDemandwareAndNotShopify` | Demandware 路径通 + `/cart.js` 非 Shopify |
| `bstn` | `BstnServesItsBeastApiAndNotAShopifyOne` | `/api/beast/geoIP` 通 + `/cart.js` 404 |
| `footpatrol` | `TheStoresThatMustAnswerShopifyStillDo` | `/cart.js` 返回 Shopify cart |
| `size` | 同上 | 同上 |
| `funko` | `FunkoUsesTheSiteIdThatActuallyAnswers` | `FunkoUS-Site` 通 + `Funko-Site` 404 |
| `jbhifi` | `TheStoresThatMustAnswerShopifyStillDo` | `/cart.js` 返回 Shopify cart |
| `offspring` | `OffspringServesItsHybrisControllers` | 两个 `/view/` controller 都返回 JSON |

加上两个非误判的：
- `YeezyKeepsItsCartOnTheSwellHost` — Swell 宿主分离
- `ScheelsKeepsItsKasadaSensorEndpoint` — Kasada 端点位置

**9 个测试，15 个端点。**

### 每个契约都写了「反了什么」

```csharp
$"{host} no longer looks like Shopify — its registration was decided on this endpoint"
"if converse starts serving Shopify carts, the Demandware registration is obsolete"
"if this starts working, Funko-Site became valid and the fix was unnecessary"
"if bstn starts serving Shopify carts, it became a Shopify store and BstnFlow is obsolete"
```

**「反了什么」比「验了什么」更重要**——因为世界会变。如果某天 BSTN 真的换成 Shopify，
`BstnFlow` 就该报废，而不是继续跑。契约失败消息里写明了那个判断。

### 三次自己写错契约，三次同一个原因

| 轮次 | 我的判据 | 真实 |
|---|---|---|
| R70 | `content-type` 含 json | Shopify 用 `text/javascript` |
| R71 | body 含 `"token"` | Converse 的 HTML 里也有 token |
| R71 | （同上，加了排除 html 才对） | — |

**三次都是把「形状」判断得太窄或太宽。**

对比一下：R47–R69 期间发现的八个平台误判，**没有一个是靠 mock 测试发现的**。
而这三次契约错误，**全部是靠打真实站点发现的**。

**同一件事的两面**：打到真实站点会让我发现自己理解错了，也会让我发现自己写的检查条件错了。

### 现在的完整验证层次

| 层次 | 数量 | 发现什么 |
|---|---|---|
| 单元测试 | 539 | 逻辑错、解析错 |
| Live 契约 | 9 | 平台漂移、端点消失 |
| 文档锚点 | 6 条 | 文档与代码脱节 |
| 手工探测 | 每轮 | 新的平台误判 |

**四层，各管一类失败。**
