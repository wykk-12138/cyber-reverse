### BSTN 停手：商品卡不是 div，也不是 img

上轮定的止损条件是「点了 3 个候选都没变成 `/us_en/{gender}/brands/{brand}/{slug}` 形状就停」。
这一轮第一次尝试就满足了止损条件——**而且排除了两种最可能的形状**。

### 探测结果

```
{"url": "https://www.bstn.com/us_en/men/collection/silhouettes/samba",
 "bigCards": 1,
 "picked": [{"w":1252, "h":9347,
             "cls": "page-wrapper flex flex-col min-h-screen overf…",
             "imgAlt": "BSTN STORE MUNICH"}],
 "clicked": {"w":1252, "h":9347, "imgAlt": "BSTN STORE MUNICH"}}
```

**筛选条件是「含 `<img>` 且宽高都 >180px 的 `div[flex-col]`」，结果只有一个匹配——
整个页面 wrapper，1252×9347 像素。**

里面第一张图是门店照（`BSTN STORE MUNICH`），点了就跳到 `/bstn-stores#munich-store`。

### 两种形状都被排除了

| 假设 | 结果 |
|---|---|
| 商品卡是 `div[flex-col]`（R56 的猜测） | ❌ 那是页面 wrapper |
| 商品卡里有一个大的 `<img>` | ❌ 没有这样的 img |
| **商品卡用 CSS `background-image`** | ⬜ 未被排除，是最可能的 |

**所以商品卡是「背景图 + 绝对定位覆盖层」那种结构**——这在 Tailwind 系的设计里很常见
（`bg-[url(...)]` + `absolute inset-0`）。R85 那次点到 `img.h-9` 也印证了这一点：
页面里那些 `<img>` 都是图标尺寸。

### 四轮 BSTN 的完整记录

| 轮次 | 方法 | 结果 |
|---|---|---|
| R53 | `/us_en/new-arrivals` | 404 |
| R53 | `/en-US/us_en/` + scroll | 194 链接，全是分类 |
| R54 | `--follow=3` | 940 链接，最深 d5 全是系列页 |
| R56 | `--eval-file` 探卡片 | 61 张卡，2 个 `<a>` 都是导航 |
| R85 | `--await-url` + 点 img | 点到图标，跳到门店页 |
| **R86** | **找 >180px 的 img** | **只匹配到页面 wrapper** |

**六次尝试，零个商品 URL。**

### 记账

`BstnFlow` 保持现状：4 步实现（找商品、找变体、查库存、拿价格）+ 3 步诚实失败。
`AddToCartAsync` 的失败信息是：

```
bstn: cart endpoint unknown — /cart.js is 404 and the cart lives under /api/beast/
```

**这句话准确。** 现在还可以补一句：商品页的 DOM 结构也探不明。

### 三个站点的最终分类

| 模块 | 障碍 | 性质 | 还能做什么 |
|---|---|---|---|
| `offspring` | reCAPTCHA 门禁 | **运行时配置**（要打码服务） | 无 |
| `scheels` | Kasada | **需要 Kasada 会话** | 逆向 sensor |
| `bstn` | 商品卡是 CSS 背景图 | **DOM 结构未探明** | 下一层探测（`bg-[url(...)]`） |

**三个都不一样，但都不是「再试一次同样的方法」能解决的。**

### 为什么停

**边际收益已经连续两轮接近零。**

R85 的产出是 `--await-url`（通用工具，有价值）；R86 的产出是**排除了两种形状**（是信息，
但不是进展）。

**再投一轮大概能确认是不是背景图**——但即使确认了，后面还有「点中了但加购端点未知」
这一关。**这个模块的完整链路比其它模块多两道未知。**

---
