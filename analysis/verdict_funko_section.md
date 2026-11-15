### 最后两个 flow 类型验证完毕：又抓到一个错的

按 `docs/PLATFORM_VERIFICATION.md` 的清单，验证 `DemandwareFlow` 和 `FootsitesFlow`。

**Funko 是 Demandware（A 级证据），但 site id 是错的。**

```
https://funko.com/on/demandware.store/Sites-FunkoUS-Site/en_US/__Analytics-Start
https://funko.com/on/demandware.static/Sites-FunkoUS-Site/-/default/dw43a14dfa/...
```

代码里写的是 `Funko-Site`，实际是 **`FunkoUS-Site`**，locale 是 `en_US`。

```csharp
// 之前
public FunkoFlow() : base("funko", "Demandware (Funko)", new[] { "funko.com" }, "Funko-Site")

// 现在
public FunkoFlow() : base("funko", "Demandware (Funko)", new[] { "funko.com" },
    "FunkoUS-Site", "en_US")
```

**这是六个平台配置错误里最安静的一个**：主机对、平台对、只有 site id 少了一个 `US`。
每次 controller 请求都 404，但看起来像"店铺维护中"而不是"参数写错了"。

（顺带把 `DemandwareFlow.Locale` 暴露出来，之前只有私有字段，测试没法断言。）

**六个 footsites 主机全是自建**（不是 Demandware）：

```
footlocker.com      HTTP 200  1,042,160B   marker: queue-it
champssports.com    HTTP 200  1,000,190B   marker: queue-it
footaction.com      HTTP 200  1,002,298B   marker: queue-it
kidsfootlocker.com  HTTP 200    985,335B   marker: queue-it
eastbay.com         HTTP 200  1,000,190B   marker: queue-it
ladyfootlocker.com  HTTP 200  2,432,459B   marker: queue-it
```

六个都只有 Queue-it，**没有 Demandware / Shopify / Next.js 的任何标记**。
`FootsitesFlow` 是自己的实现，和这个观察一致——**这个注册是对的**。

### 平台验证全部清账

| Flow 类型 | 数量 | 结果 |
|---|---|---|
| `ShopifyFlow` | 30 | ✅ 25 确认 + 3 改 + 4 域名问题 |
| `MagentoFlow` | 4 | ✅ 2 改 Shopify + 2 待查（C 级） |
| `DemandwareFlow` | 2 | ✅ Converse 新写、**Funko site id 已修** |
| `FootsitesFlow` | 1 | ✅ 确认是自建，注册正确 |
| 其余单一 flow | 各 1 | ✅ 逐个已单独抓过 |

**六个已修正的平台配置错误**：

| 模块 | 错误 |
|---|---|
| `hbx` | ShopifyFlow → 自建 `/api/v2/` |
| `converse` | ShopifyFlow → Demandware |
| `bstn` | ShopifyFlow → 自建 `/api/beast/` |
| `footpatrol` | MagentoFlow → Shopify |
| `size` | MagentoFlow → Shopify |
| **`funko`** | **site id `Funko-Site` → `FunkoUS-Site`** |

### 两种错误的对比

| 类型 | 症状 | 发现难度 |
|---|---|---|
| 平台选错（5 个） | 请求打到完全不存在的路由 | 中——特征路径会 404 |
| **参数写错（1 个）** | 请求打到正确平台的错误路径 | **高**——主机对、平台对、只有 id 错 |

`funko` 这个最值一提：如果只验证"是不是 Demandware"就会通过（它确实是），
但真正要验证的是"**声明的 site id 在这个站点上是否存在**"。

**验证平台类型不够，还要验证标识符。**

---
