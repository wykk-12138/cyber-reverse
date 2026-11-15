### 剩下 4 个"可疑"的真相：大多数是域名失效，不是平台误判

逐个抓包之后，四个都不是"配错平台"，而是**域名已经不在原主人手里了**：

| 域名 | 真实状态 | 证据 |
|---|---|---|
| `saintalfred.com` | **GoDaddy 停放页** | `web-api.aws.parking.godaddy.com/v1/parking/landers/...` |
| `sns.com` | **已易主**，现在指向 `thrivenextgen.com`（一家 IT 外包公司） | 页面的 GA 事件里 `dl=https://thrivenextgen.com/` |
| `trophyroomstore.com` | **404** | 根路径直接 404 |
| `civilistberlin.com` | **Sanity CMS，无电商 API** | 8 个请求，只有 `cdn.sanity.io` 和字体 |

### 但 `sns` 模块本身是对的

`sneakersnstuff.com`（主域名）**确实是 Shopify**：

```
/.well-known/shopify/monorail/unstable/produce_batch
/cdn/shop/videos/c/vp/...
/web-pixels@.../sandbox/modern/
```

所以 `SnsFlow` 没问题——**问题在它的第二个域名 `sns.com`**。

已修：

```csharp
// 之前
public SnsFlow() : base("sns", "Sneakersnstuff",
    new[] { "sneakersnstuff.com", "sns.com" })

// 现在
public SnsFlow() : base("sns", "Sneakersnstuff", new[] { "sneakersnstuff.com" })
```

**"认领了别人的域名"比"域名失效"危险得多**：

- 失效的域名没人访问，claim 挂着也无害
- 指向别家公司的域名会把**那个网站的 URL 路由进我们的 store flow**，
  然后在完全错误的地方失败，看起来像"店铺有问题"

### `DomainClaimTests` 把这两件事钉住

```
SnsNoLongerClaimsTheRepurposedAlias     sns.com 不再被认领
NoTwoModulesClaimTheSameDomain          任何域名只能被一个模块认领
EveryDeadDomainIsRecordedHereSoItIsNotRediscovered
                                        四个失效域名连同原因记在这里
```

第二条测试顺带发现：`sneakersnstuff.com` 曾被**两个** flow 声明
（`SnsFlow` 和未注册的 `SnsModule`），目前只有前者生效，但重复声明本身是隐患。

### 四个"可疑"的最终定性

**零个是平台误判。** 和 `hbx`/`converse`/`bstn` 完全不同的性质：

| 类型 | 例 | 症状 |
|---|---|---|
| 平台配错 | `hbx` `converse` `bstn` | 编译通过、请求返回、静默失效 |
| 域名失效 | `saintalfred` `trophyroomstore` `civilistberlin` | 请求根本到不了店铺 |
| 域名易主 | `sns.com` | 请求到了**别家公司** |

**三种都需要不同的处理**：改 flow、记录状态、删 claim。

这印证了那句"`/cart.js` 404 不等于不是 Shopify"——如果当时按 404 就改注册，
`civilistberlin` 会被换成一个更错的 flow，而它其实连店都没了。

---
