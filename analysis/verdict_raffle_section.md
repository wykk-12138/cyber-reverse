### `pocketgames` / `riotgames` 的 29% 不是缺口

上轮说「按 supreme 的经验，它们的 29% 可能也意味着平台判断是错的」。查下来**两种猜测都不对**。

### 实际覆盖率：满分

矩阵第二段（非电商，按自己的步骤量）：

```
non-commerce flows (measured against their own steps):
  raffle                  4/4  + + + +
  pocketgames             6/6  + + + + + +
  riotgames               7/7  + + + + + + +
```

**三个抽签模块全部满分。**

第一段那个「29%」是**按电商 7 步量的结果**——而抽签流程没有购物车、没有结账，那五步本来就不该存在。

### 数字本身在误导

同一份输出里，同一个模块出现两个数字：

```
riotgames    +  +  -  -  -  -  -   29%
...
   riotgames    7/7  + + + + + + +
```

**「29%」和「100%」说的是同一个模块，只是尺子不同。**

已加标记：

```
riotgames    +  +  -  -  -  -  -   29%   (non-commerce — see below)
```

### 平台判断这次是对的

`playriftbound.com` 抓包结果：

```
cmsassets.rgpub.io/sanity/...     ← Sanity CMS
cmp.osano.com/                    ← Cookie 同意
xsso.playriftbound.com/xsso        ← Riot 的 SSO
auth.riotgames.com/                ← Riot 认证
youtube.com/embed/...              ← 营销视频
```

**这是营销站，不是商店。** 没有购物车、没有商品 API。

而 `RiotGamesFlow` 的 8 个 override 全是抽签相关的（`Register` / `CompleteRegistration` /
`Login` / `EnterRaffle`）——**它本来就没打算做电商**。

**所以这次的平台判断是对的**，29% 只是个度量口径的产物。

`pocketgames.nl` 403 被拦，同样拿不到更多信息，但它的 6/6 说明实现完整。

### 三种「低分」的含义完全不同

| 模块 | 分数 | 真实含义 |
|---|---|---|
| `riotgames` | 29% | **尺子不对**，实际 7/7 |
| `supreme`（改之前） | 86% | **六步全错**，只有一步缺 |
| `bstn` | 71% | **诚实的三步缺口** |

**同一个百分号，三种完全不同的情况。**

这解释了为什么 VERDICT 里每一项都要写依据而不是只写数字——**数字单独看没有意义**。

### 一个模式

`supreme` 和 `riotgames` 这轮一起看，正好是反例：

- `supreme` 分数高（86%），但**全是错的**
- `riotgames` 分数低（29%），但**全是对的**

**分数高低和正确性没有关系。**

---
