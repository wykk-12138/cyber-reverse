### 全模块可达性扫描：61 个模块，44 个活着

覆盖率说明「实现了七步」，但**说明不了那些步骤指向的站点还在不在**。
R47–R77 发现的九个平台误判都是这一类——代码没问题，世界变了。

所以做了一次全量扫描：61 个模块，每个取 `Domains.First()`，GET 根路径。

### 分类（四类，含义不同）

| 类别 | 判据 | 含义 |
|---|---|---|
| **Live** | 2xx / 3xx | 有地方可以跑 |
| **Guarded** | 401 / 403 / 429 | 主机在，拒绝自动化——**不算腐烂** |
| **Missing** | 404 / 410 | 域名解析但没站点 |
| **Dead** | DNS / TLS 失败 | 没人应答 |

### 结果

```
total 61 modules
  Live      44
  Guarded    6   fanatics, goat, offspring, pocketgames, scheels, yeezysupply
  Missing    2   shopify, trophyroom
  Dead       9   bodega, demandware, hypecommerce, livestock, nakedcph,
                 nike-gs, offthehook, premiumgoods, shophmvs
```

**44 + 6 = 50 / 61 有地方可跑（82%）。**

### 扫描抓到一个真 bug

`footpatrol` 报了 **Dead**，但 R47 明确验证过它是 Shopify。

```
https://footpatrol.co.uk/        DNS 失败
https://www.footpatrol.com/      200, 892 KB
https://www.footpatrol.com/cart.js   200, 303 B  ← Shopify cart
```

**`FootpatrolFlow` 的 `Domains` 是 `["footpatrol.co.uk", "footpatrol.com"]`——死的那个排在前面。**

而 `Domains.First()` 既是扫描用的，也是路由用的。**死域名排第一，让一个能用的模块报成不可达。**

已调换顺序，`footpatrol` 从 Dead → Live。

### 三个 Dead 是「预期内」的

| 模块 | 为什么 Dead | 处理 |
|---|---|---|
| `demandware` | `demandware.example` 是占位域名，那个实例是平台模板 | 加了注释说明它是模板 |
| `shopify`（Missing） | `myshopify.com` 是 Shopify 的通用域名，没有具体店铺 | 正常 |
| `nike-gs` | `kids.nike.com` 无 DNS 记录 | 见下 |

### `nike-gs` 的问题没有好解法

`NikeGsFlow` 需要**真实且唯一**的域名（`NikeFlow` 已经 claim 了 `nike.com`，
`DomainClaimTests.NoTwoModulesClaimTheSameDomain` 禁止重复）。

实测所有候选：

```
kids.nike.com     DNS 失败
snkrs.nike.com    DNS 失败
launch.nike.com   DNS 失败
www.nike.com      200   ← 但 nike.com 已被 claim
nike.com          200   ← 同上
```

**Nike 没有 kids 子域，也没有 SNKRS 子域。** GS 本来就不该按域名区分——
它是按**尺码**（3.5Y–7Y）区分的，`NikeGsFlow.IsGradeSchoolSize` 就是这个。

**当前状态**：`kids.nike.com` 是占位，已记进 knownDead，注释里写明了原因。

### 顺手记了四个新的死域名

`DomainClaimTests` 的 knownDead 从 6 条涨到 10 条：

```
kids.nike.com        no DNS record — Nike has no kids subdomain
snkrs.nike.com       no DNS record — the SNKRS app is not a host
footpatrol.co.uk     no DNS record — the store moved to footpatrol.com
demandware.example   placeholder, kept as a platform template
```

### 六个 Dead 是真的腐烂

`bodega` `hypecommerce` `livestock` `nakedcph` `offthehook` `premiumgoods` `shophmvs`

这七个域名解析不了（或已停放）。它们在 R47 那次平台检查里就已经连不上，
这次扫描只是把状态固化下来。

**没有删掉它们的注册**——用户可能知道这些站的新地址。记录比删除有用。

---
