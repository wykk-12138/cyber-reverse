### BSTN 探测：路径结构摸清了，商品页还没找到

按 HBX 的成功打法试了 BSTN，四次都停在分类页。

### 摸清的路径结构

```
https://www.bstn.com/en-US/us_en/                          首页（/us_en 会重定向到这里）
https://www.bstn.com/us_en/men/new-arrivals/footwear       分类
https://www.bstn.com/us_en/men/new-arrivals/apparel
https://www.bstn.com/us_en/men/collection/silhouettes/samba        系列
https://www.bstn.com/us_en/men/collection/silhouettes/Gazelle
```

**规律**：`/{locale}/{gender}/{category}/{subcategory}`，系列是多一层 `collection/silhouettes/{name}`。

### 四次尝试

| 尝试 | 命令 | 结果 |
|---|---|---|
| 1 | `/us_en/new-arrivals` | **404** — 这条路不存在 |
| 2 | `/en-US/us_en/` + `--scroll` | 194 个链接，全是分类 |
| 3 | 深度 ≥7 的链接 | 12 个，全是 `/{locale}/{gender}/{category}/{subcategory}` |
| 4 | `/us_en/men/new-arrivals/footwear` + `--scroll` | 8 个，全是 `collection/silhouettes/{name}` |

**商品页比系列页还深一层，而系列页本身又是一个列表。**

### 为什么停在这里

不是"再试一次就能成"——是**每一层都是列表，商品页可能还要再下两层**。
而每跑一次 `NetworkCapture` 要 6–8 秒，加上构建和解析，一次探测占掉相当一轮。

**HBX 那次成功是因为它足够浅**：首页 → 品牌页 → 商品页，三层。
BSTN 至少四层，而且是动态懒加载。

### 一个可选的下一步

`CollectLinksAsync` 的启发式目前只认 `/p/`、`/product`、`/item`、`/shop/` 和数字尾巴。
BSTN 的商品 URL 可能长得完全不一样（比如 `/us_en/men/sneakers/adidas-samba-og-b75806`）。

**更省力的做法**：让 `NetworkCapture` 支持"递归下钻一层"——
`--follow=<n>`，自动访问列表页上深度最大的 N 个链接，再从那些页面找商品。
一次运行顶三次手工探测。

### 这一轮没有代码改动

没有改 `BstnFlow`——因为没拿到端点，改了也只是把 `Fail` 的措辞换个说法。

**探测失败也是信息**：BSTN 的商品入口比 HBX 深两层，这决定了下次要用什么工具，
而不是再手工试一次。

---
