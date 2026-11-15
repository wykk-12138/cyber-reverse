### 把「第一个域名必须能解析」变成断言

上轮那个 `footpatrol` bug 的本质是：`Domains[0]` 死了，整个模块看起来就死了。
调换顺序修好了它，但**没有任何东西阻止它再次发生**。

新增 `FirstDomainResolvesTests`（2 个测试）：

```csharp
foreach (var module in StoreModuleCatalog.CreateAll())
{
    var host = module.Domains.First();
    await Dns.GetHostAddressesAsync(bare);   // 解析不了就失败
}
```

**只查 DNS，不发 HTTP**：

- 毫秒级（不是秒级），61 个模块 34 ms 跑完
- 没有 rate limit，不会因为 403 误判
- 正好抓到了那次发生的失败——**主机没有 DNS 记录**

输出：

```
checked 59, allowed-dead 2, failed 0
```

### 白名单只有两条，而且每条都要有理由

```csharp
["demandware"] = "platform template — demandware.example is a placeholder",
["nike-gs"] = "no Nike kids subdomain exists; GS is selected by size, not by host",
```

第二条测试保证**白名单不会变成垃圾桶**：

```csharp
// 白名单里的每个名字必须仍然是一个已注册模块
var stale = AllowedDead.Keys.Where(k => !ids.Contains(k)).ToList();
Assert.Empty(stale);
```

否则这个列表会慢慢填进已经不存在的名字，**看起来在豁免什么，实际上什么都没豁免**。

### 第一次跑就把白名单写错了一条

我一开始把 `shopify` 也放进了 allowed-dead，理由是「`myshopify.com` 是平台通用域名」。

但上轮扫描明明白白写着：

```
shopify  myshopify.com  404  Missing     ← 不是 Dead
```

**`myshopify.com` 能解析**，它只是没有具体店铺。把它放进「解析不了」的白名单是错的类别。

去掉后：`checked 58 → 59, allowed-dead 3 → 2`。

**白名单的第一条纪律是「只放真正需要豁免的」**——多放一条就少查一个模块。

### 现在的四类域名词表

| 类别 | 位置 | 例 |
|---|---|---|
| 活的 | 不需要记录 | `nike.com` |
| **死但允许** | `FirstDomainResolvesTests.AllowedDead` | `demandware.example` |
| **死且记录** | `DomainClaimTests.knownDead`（10 条） | `footpatrol.co.uk` |
| **易主** | 已从 `Domains` 删除 | `sns.com` |

两个列表的区别：`AllowedDead` 是「这个模块的第一个域名解析不了，但这是已知的」；
`knownDead` 是「这个域名死了，别再去试」。

### 验证

```
dotnet test (快速)   539 通过 / 0 失败 / 2 跳过（+2 FirstDomainResolvesTests）
release build        成功
store modules        PASS 61 registered
verify.ps1           VERDICT: all checks passed
```

---
