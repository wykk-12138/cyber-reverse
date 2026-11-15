### `--follow` 有个 bug：它丢掉了 scroll

想用 `--follow` 下钻找 Offspring 的商品页，第一次跑出来：

```
--- level 1: 0 candidate(s), following 0 ---
--- 0 same-host link(s), deepest first ---
```

**0 个链接。** 但同一个页面加 `--scroll` 手工跑是能出链接的。

原因在 `--follow` 的实现：

```csharp
foreach (var page in frontier.Take(4))
{
    await rec.VisitAsync(page);          // 重新导航
    await rec.WaitAsync(3s);             // 然后干等
    var walked = await rec.CollectLinksAsync();
```

**`VisitAsync` 是重新导航**——入口页上 `--scroll` 渲染出来的内容被丢掉了，
而 `--follow` 自己从不滚动。

修复：每个下钻的页面也滚动。

```csharp
await rec.VisitAsync(page);
if (scroll)
{
    for (var step = 1; step <= 3; step++)
    {
        await rec.RunAsync($"window.scrollTo(0, document.body.scrollHeight * {step} / 3)");
        await rec.WaitAsync(1s);
    }
}
await rec.WaitAsync(2s);
```

**这是同一个坑的第三次**：R51（HBX 0 个按钮 → 加 `--scroll`）、R78（reachability
只看第一个域名）、现在（`--follow` 忘记滚动）。**每次都以为「滚动是入口页的事」，而它其实是每一页的事。**

### 修完还是 0，但原因换了

```
{"url":"https://www.offspring.co.uk/mens/trainers",
 "title":"OFFSPRING",
 "anchors":0, "divs":11, "bodyLen":3298,
 "sample":[], "deepest":[], "tiles":[]}
```

**整个 DOM 只有 11 个 div、3298 字节。**

等 25 秒也一样。**首页也一样。**

而 R64 用 `NetClient` 抓同一个首页拿到的是 **192,133 字节的 HTML**。

### 两个数字说的是两件事

| 来源 | 大小 | 说明什么 |
|---|---|---|
| `NetClient` GET | 192,133 B | 服务器返回了完整 HTML |
| 浏览器渲染后的 DOM | 3,298 B | **JS 没执行成功** |

**页面到了，但没渲染。**

这解释了为什么 R64 能验证 Hybris（靠 HTML 里的 `hybris` 标记和 `/view/` controller），
却拿不到任何交互入口——**交互需要 DOM，而 DOM 没建立**。

最可能的原因：Akamai 在 JS 层拦了。R64 抓到的 `/akam/13/...` 就是 Akamai 的 sensor，
它可能要求一个浏览器不会自动满足的条件。

### 所以 Offspring 的加购路径拿不到

不是因为找不到商品页，是因为**这个站点在自动化浏览器里根本渲染不出页面**。

`HybrisFlow.AddToCartAsync` 保持诚实失败：

```
offspring: cart-add controller not found — /cart/add, /view/cart/add,
/view/component/cart/add and /view/component/basket/add all return 404 while the
control minibasketAjax returns 200, so the route is customised; needs a click-through
capture of the add-to-basket button
```

**要抓那个按钮，需要的不是更好的探针，是一个 Akamai 认的浏览器会话。**

### 这一轮的净收获

**一个工具 bug 修掉了**（`--follow` 现在会滚动每个下钻页），**一个站点定性完成**（Offspring 在自动化环境里不渲染）。

后者比前者重要：它把「Offspring 加购端点未知」从一个**待办**变成了一个**已知限制**——
和 `bstn`（JS 路由）、`scheels`（Kasada）是同一类，不是「再试一次就能拿到」的那种。

---
