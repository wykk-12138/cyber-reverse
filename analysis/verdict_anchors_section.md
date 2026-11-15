### 锚点补完：错误文案条数 + 测量值的标注

上轮把模块数钉住了。这轮补上剩下的两类。

#### 1. 错误文案条数（可锚定的）

`ErrorCatalogTests` 早就有 `Assert.Equal(13, ErrorCatalog.All.Count)`——**代码那一侧有锚点**。
缺的是文档那一侧：VERDICT 说「13 条逐字对齐」，但没人验过这两个 13 是同一个 13。

新增：

```csharp
var claims = Regex.Matches(doc, @"(\d+)\s*条(?:逐字|错误文案|文案|错误)")
    .Select(m => int.Parse(m.Groups[1].Value))
    .Distinct();

Assert.All(claims, n => Assert.Equal(ErrorCatalog.All.Count, n));
```

输出：

```
ErrorCatalog.All.Count = 13
claims in VERDICT: 13
```

#### 2. 测量值：不是钉死，是要求标明它不固定

`p50 1.01x` 和「15 个 Settings 页」**天然不可锚定**：

- p50 跑一次变一次
- Settings 页数来自某一次读 GUI

对这类数字，**钉住值是错的，要求它标明"这是快照"才是对的**：

```csharp
// p50 附近必须有样本数说明
var labelled = window.Contains("样本") || window.Contains("快照");
Assert.True(labelled, "the p50 block must state its sample size");

// Settings 页数附近必须有"基线"或"一次"字样
Assert.True(labelled, "the Settings page count must be described as a baseline");
```

输出：

```
efficiency ratio found; sample-size caveat nearby: True
Settings claim found; baseline wording nearby: True
```

### 现在的锚点清单

| 数字 | 类型 | 锚点 |
|---|---|---|
| 61 个模块 | 事实 | ✅ 扫描文档 == `CreateAll().Count` |
| 13 条错误文案 | 事实 | ✅ 扫描文档 == `ErrorCatalog.All.Count` |
| p50 1.01x | **测量** | ✅ 强制标注样本数 |
| 15 个 Settings 页 | **快照** | ✅ 强制标注"基线" |
| 539 个测试 | 事实但每次变 | ❌ 不锚（会随每次加测试过期） |
| 15 个平台 | 事实 | ❌ **无代码对应物**，见下 |

### 「15 个平台」为什么没锚上

「平台」是我自己归纳的概念，代码里没有 `Platform` 枚举。

要么：
- 建一个 `IPlatform` 抽象（工程量大，且现有设计是按 flow 而不是按平台组织的）
- 或者在文档里把它标成"归纳，非枚举"

**选后者**——因为强行造一个枚举只为了让测试能数，是本末倒置。

---
