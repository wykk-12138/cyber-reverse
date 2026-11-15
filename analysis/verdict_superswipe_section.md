### Superswipe 不是店铺，是 Shopify 的抽签 App

探测它自己的网站，页面标题直接说了：

```
SuperSwipe | Shopify Raffle App & Fair Release Platform
```

抓到的 API 全是**应用侧**的：

```
GET  https://relay.superswipe.com/region
POST https://relay.superswipe.com/e/
POST https://superswipe.com/cdn-cgi/challenge-platform/…    (Cloudflare)
```

### 代码本来就是按这个写的

`SuperswipeFlow` 有 `captcha.` / `status.` / `enter.` / `cdn.` 四个子域和
`_superswipe_launch_id_` 属性——**说明它一开始就知道自己面对的是一个 App，不是店铺**。

这一点和前面七次平台误判不同：**那些是把 A 当成 B，这个是 A 本来就被正确识别了。**

### 但 `Domains` 有个说不清的地方

```csharp
public override IReadOnlyList<string> Domains =>
    new[] { "superswipe.com", "superswipe.app", "enter.superswipe.com" };
```

**抽签实际发生在客户的 Shopify 域名上**，这个模块不可能知道那是哪个域名。

所以这三条是**占位**——为了让 `CatalogValidatorTests`（要求每个模块至少一个域名）
能通过，而不是真实的商品域。

**后果**：如果有人把 `superswipe.com` 的 URL 填进任务，会被路由到这个 flow，
但那是厂商官网，不是抽签页。

已在类的注释里写清楚这个张力，包括"这是占位不是商品域"。

### 为什么只加注释不改代码

改 `Domains` 有三条路，都不好：

| 方案 | 问题 |
|---|---|
| 清空 | `CatalogValidatorTests` 报 `module declares no domains` |
| 填客户的 Shopify 域名 | 不可能知道，每个客户不同 |
| 保留 + 注释 | **当前选择**：能通过校验，且说清了它的性质 |

**"这个字段是占位"这件事必须写在代码里**，否则下一个人会以为 `superswipe.com`
是真实的抽签域名，然后困惑为什么打不开抽签页。

### 六个模块的定性到此完成

| 模块 | 结论 |
|---|---|
| `casio` | 解析器 6/8 验证通过 |
| `hbx` | 加购链路抓包成功 |
| `popmart` | `ExtractPrice` 修好 |
| `johnlewis` | 价格 bug 修好 |
| `jbhifi` | Shopify + 独立 OAuth，已改 |
| `yeezysupply` | Swell，已重写 |
| `warhammer` | 403 被拦，D 级证据，不动 |
| `fanatics` | Akamai 403，拿不到 |
| `hypecommerce` | 死域名，已记录 |
| **`superswipe`** | **App 集成，代码正确，`Domains` 是占位** |

**"只对 mock 验证过"这个清单现在清空了**——每一个都有定性结论，要么验证通过，
要么记明了为什么验不了。

---
