# AddToCart 覆盖表（从 `replica/src` 迁出，R1270）

这张表原先放在 `replica/src/Cybersole.Stores/Scripts/AddToCartCoverage.cs`——**那是产品代码**。
按 `AGENTS.md` §3 的红线，覆盖表属于考据，归 `docs/`。表里的**判据与错案**逐条保留如下，
一个字都没丢；源里那个类与它的钉子测试已删除。

## 一、逐名判定

| 名字 | 有实现 | 注 |
|---|---|---|
| `AddToCart` | 是 | 通用步骤，Demandware 各路径在用 |
| `AddToCartApp` | 是 | app 客户端路径 |
| `AddToCartAppDw` | 是 | Demandware 上的 app 客户端 |
| `AddToCartBox` | 是 | PopMart 抽签步骤 |
| `AddToCartDummy` | 否 | **只提名**：与 `RemoveDummy` 配套的购物车预置，**不是试运行**（R941 修正） |
| `AddToCartGraphQL` | 是 | GraphQL 传输 |
| `AddToCartMulti` | 是 | **PopMart 的加多盒**，不是通用多件购物车（R942，四轮内第四次误归类） |
| `AddToCartPreload` | 是 | 购物车预载 |
| `AddToCartPreloadGraphQL` | 是 | 走 GraphQL 的预载 |
| `AddToCartNext` | 否 | 表面在、步骤不在：购物车端点是**按店**而不是按框架 |
| `AddToCartAstro` | 否 | 同上 |
| `AddToCartSvelte` | 否 | 同上 |
| `AddToCartFrontend` | 否 | 同上 |

## 二、两处**方向相反**的错案（保留原文，防止再犯）

- **R941**：原先写「`AddToCartDummy` 是试运行」，**错**。它紧跟着 `RemoveDummy`，
  是一个**提前加入、稍后移除的占位商品**——购物车预置。名字讲的是**商品**，不是**这次调用**。
- **R942**：`AddToCartMulti` 原先被当成「通用多件购物车」，**错**。相邻性把它放进 PopMart 那一类，
  它其实是**加多盒**。

**共同点**：两次都是**先按名字的字面意思归类，再去找证据**。名字形状不能当分类判据（§「不再写前缀分类器」）。

## 三、四个「表面在、步骤不在」的形状

`AddToCartNext` / `AddToCartAstro` / `AddToCartSvelte` / `AddToCartFrontend` 是**最容易被误读成已完成**的一类：
镜像里有这个字面量，但复刻件没有对应步骤——因为**购物车端点是按店配置的，不是按前端框架**。
把它们算进"已实现"会让覆盖率虚高。

## 四、怎么复算

删掉那个类之后，这张表不再由代码生成，也没有钉子测试。
判断某个名字有没有实现：

```
python tools\where_is.py <名字>
```

`implementation` 组里出现即"有实现"；只在 `analysis`/`doc` 里出现即"只提名"。
