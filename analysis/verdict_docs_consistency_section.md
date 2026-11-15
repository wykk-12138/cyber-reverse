### 文档里的数字第一次被测试锁住

上轮说「把 VERDICT 的断言对应到测试」。第一个跑出来的是个真问题。

### 62 vs 61

`verify.ps1` 一直报 `store modules PASS 62 registered`，而 VERDICT 说「61 个模块」。
两个数字都是"实测"的，所以必有一个是错的。

查下来是脚本：

```powershell
# 之前：数整个文件里的字面出现次数
$modules = ([regex]::Matches($registry, 'new \w+Module\(')).Count   # 62
```

`Registry.cs` 第 279 行有一个辅助方法：

```csharp
registry.Register(new FlowStoreModule(new ShopifyFlow(id, name, new[] { host })));
```

**这是 `RegisterShopifyHost`，被 30 个 Shopify 模块调用。** 脚本把辅助方法里的
构造也算成了一个模块。

真实数量是 **61**（`CreateAll()` 里 61 个 `FlowStoreModule`）。

```powershell
# 现在：只数 CreateAll() 方法体内的
$start = $registry.IndexOf('public static IReadOnlyList<IStoreModule> CreateAll()')
$end   = $registry.IndexOf('};', $start)
$modules = ([regex]::Matches($registry.Substring($start, $end - $start),
                             'new FlowStoreModule\(')).Count   # 61
```

### 新增 `DocsConsistencyTests`

三条断言：

| 测试 | 断言 |
|---|---|
| `TheModuleCountInVerdictMatchesTheCatalogue` | VERDICT 里每处「N 个模块」== `CreateAll().Count` |
| `TheCoverageTestAndTheCatalogueAgree` | 模块数 == 去重后的 id 数（防止 id 重复） |
| `EveryModuleHasAtLeastOneDomain` | 每个模块至少一个域名 |

第一条会**扫描文档正文**找所有「N 个模块」的说法，所以以后改了 `Registry` 而忘改文档，
测试会红。

输出：

```
catalogue: 61 modules
claims in VERDICT: 61
modules: 61, distinct ids: 61
```

### 为什么这件事值得做

**一份和代码脱节的文档比没有文档更糟**——它被当作权威读，而且是错的。

这份 VERDICT 已经 65KB、跨 50 轮。里面有几十个数字：模块数、平台数、测试数、
p50 比值、Settings 页数、错误文案条数。**每一个都可能悄悄过期。**

现在至少模块数这一条被钉住了。剩下的（平台数、p50）还需要各自的锚点。

---
