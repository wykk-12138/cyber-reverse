### `--await-url` 能用了，但 BSTN 的商品卡还是点不中

上一轮说「`bstn` 最有可能成功，缺的是『点完等 URL 变』这个组合」。这轮把它做了。

### 工具本身是好的

```
--- eval-file bstn_click.js ---
{"tiles":61,"anchors":857,"productLinks":[],"clicked":{"tag":"img","cls":"h-9"}}
--- await-url (max 10s), from .../silhouettes/samba ---
--- url changed -> https://www.bstn.com/us_en/bstn-stores#munich-store ---
```

**`--await-url` 确实抓到了路由变化。** 机制成立。

### 但它抓的是点错元素的跳转

`clicked: {tag: "img", cls: "h-9"}` —— **点到了一个 36px 高的图标**，不是商品图。
所以跳到了 `/us_en/bstn-stores#munich-store`（门店列表）。

### 顺带修了一个执行顺序的 bug

`--await-url` 原本排在 `--eval-file` 和 `--steps` **之前**——

```csharp
// 修之前的实际顺序
scroll → mouse → await-url → follow → eval-file → find-add → steps
```

**它盯着 URL 变化，而所有能点击的步骤都排在它后面。** 移到 `steps` 之后：

```
scroll → mouse → follow → eval-file → find-add → steps → await-url
```

**这是「顺序 bug」的第二次**（上轮是 `--follow` 忘了滚动）。`NetworkCapture` 的参数越来越多，
但它们**按代码里的固定顺序执行，不按命令行顺序**——这个事实之前没写在任何地方。

### 857 个锚点里没有商品页

再确认一次 BSTN 的链接结构：

```
{"total": 273 (unique), "byDepth": {"0":2,"1":3,"2":22,"3":174,"4":62,"5":10}}
d3: /us_en/men/new-arrivals?categories=Men~New%20Arrivals&created_timestamp=1W …
d4: /us_en/men/new-arrivals/footwear, /us_en/men/sale/apparel …
```

**273 个唯一链接，d3 那 174 个全是带 `?categories=` 的分类页。**

商品页确实不在 `<a href>` 里——R56 的结论再次被证实。

### 所以 BSTN 的下一步

不是「再找一个更好的选择器」，是**找到正确的商品卡**。当前 `div[flex-col]` 选到了 61 个，
第一个是个小图标容器。

**需要的探测**：列出那 61 个 div 里，哪些含 `<img>` 且宽度 > 200px。那是商品卡的形状。

**但这件事的性价比开始下降了**——已经花了 R53、R54、R56、R85 四轮在 BSTN 上。

### 这轮的净收获

**一个工具能力**（`--await-url`），**一个顺序 bug**，**一次结论复核**。

工具是好的——它对任何 SPA 路由的站点都适用，不只是 BSTN。

---
