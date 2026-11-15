### `casio` 的四条结账路径全是 404

上轮把「`casio` 的 2 个未覆盖解析点」列进 A 类待办。查下来**那 2 个点不是"没写"，是"写不了"**。

### 探测结果

```
/cart/add          HTTP 404  160,416B  [text/html]
/checkout          HTTP 404  160,416B  [text/html]
/checkout/submit   HTTP 404  160,416B  [text/html]
/api/cart/add      HTTP 404  160,048B  [text/html]
```

**四条全 404**，160 KB 是 SPA 的 404 页。

### 但站点本身活着

抓 `casio.com/us/` 看到：

```
200  /us/                                                ← 地区前缀
200  /akam/13/6b5aec1f                                   ← Akamai
200  /bin/servlet/get-akamai-country-code?site=casio     ← AEM
```

**`/bin/servlet/` 是 Adobe Experience Manager 的标准路径。**

所以 Casio 是 **AEM + Akamai**，真实路径在 `/{region}/` 前缀下面。我们的四条路径都缺了那个前缀。

### 修了两处成诚实失败

**`AddToCartAsync`**：404 时说明原因，而不是报 `HTTP 404`

```csharp
if (res.StatusCode == 404)
    return StepOutcome.Fail("casio: /cart/add is not there — Casio runs AEM behind Akamai, " +
                            "and every root-relative cart path returns the SPA 404; the real " +
                            "path is under the /{region}/ prefix and has not been captured");
```

**`SubmitOrderAsync`**：从「POST `{}` 到 `/checkout/submit`」改成明确失败

```csharp
public override Task<StepOutcome> SubmitOrderAsync(...) =>
    Task.FromResult(StepOutcome.Fail(
        "casio: the order path is not /checkout/submit — that route returns 404, and Casio's " +
        "checkout is an AEM flow under /{region}/, not a single JSON POST. Both SubmitShipping " +
        "and SubmitPayment are unimplemented for the same reason: the staged controller paths " +
        "have not been captured"));
```

### 为什么这个改动比「补齐 2 个点」更有价值

原来的 `SubmitOrderAsync` 是这样的：

```csharp
var res = await PostJsonAsync(c, ... + "/checkout/submit", "{}", "casio-order", ct);
if (!res.IsSuccess) return StepOutcome.Fail($"casio order HTTP {res.StatusCode}");
```

**它发一个空 body 到一个不存在的路由。**

如果那个路由碰巧返回 200（比如 SPA 的 catch-all），代码会 `Success()` 并**假装下了单**。

**这正是前面九次平台误判的共同形态：发了请求、收到了响应、什么都没发生。**

### 覆盖率没变，含义变了

`casio` 仍然是 71%（`SubmitShipping` / `SubmitPayment` 缺）。**但现在是诚实的 71%**：

- 四个步骤真的能跑（找商品、找变体、查库存、拿价格——R39 验过解析器）
- 三个步骤明确说了「路由没抓到」

**和改之前那些"六步都实现、但都在打 404"完全不同。**

### A 类待办少了一项

上轮列的 5 项 A 类，`casio` 那项要移出去——它实际属于 B 类（需要抓 `/{region}/` 前缀下的真实路径，
而 Casio 也有 Akamai）。

**修正后的 A 类**：

| 项 | 差什么 |
|---|---|
| `bstn` 商品卡选择器 | 下一层探测（CSS `background-image`） |
| `bstn` 加购端点 | 依赖上一条 |
| `offspring` 加购 controller | 依赖过 reCAPTCHA |

**实际只有两个模块，而且第一个依赖第二个。**

---
