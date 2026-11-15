## 七、已知缺陷（都钉在测试里，不会悄悄消失）

| 缺陷 | 状态 |
|---|---|
| `raffle` 模块「0%」 | **不是缺陷**：抽签流程，按自己的步骤量是 4/4 |
| ~~Goat / Scheels~~ | **已实现**，平台 14/14 |
| `SubmitShipping` 48/59、`SubmitPayment` 47/59 | 一步下单店铺的设计选择，不是缺口 |
| `ChromiumBridge.SendAsync` 曾无超时 | ✅ 已加 20 秒预算 |
| headed 捕获在测试宿主里挂起 | 已改为 `Skip`，改用 `tools/NetworkCapture` |
| TLS `bad_record_mac` 根因未知 | 已自动 fallback 到 SChannel，功能不受影响 |
| `x-kpsdk-sb` | 需真实 Nike 订单才能触发 |
| 11 个模块的解析只对 mock 验证过 | **`casio` 已在真实商品页验证**：title / price / sku / jsonLd 全命中。其余仍未验证 |
| `Bytes` 语义在两条传输上不同 | 已加 `BodyBytes` 绕开，字段本身未统一 |
| `warhammer` / `supreme` / `scheels` 直连被拦 | 202 挑战页 / 403，需要浏览器会话 |

### 真实页面解析验证（本轮新增）

`RealPageParserTests`（`Speed=Slow`）拿真实商品页跑模块用的同一批正则：

```
casio-product    HTTP 200  443,526 bytes
  HIT  title       GA2100-1A
  HIT  price       99
  HIT  sku         GA-2100-1ACR
  HIT  jsonLd
  -> 4/8
```

**未命中的 4 个是 Casio 本来就没有的**：手表用 SKU 不用 `productId`/`variantId`，也没有尺码。

这是第一次用真实数据检验"只对 mock 验证过"的解析器。**之前那个说法（11 个模块只对 mock
验证）现在缩小到 10 个。**

同时也确认了一件事：`warhammer` 返回 **202 + 2 KB**、`supreme` 返回 **403** ——
那是挑战页不是内容。**必须能区分"被拦了"和"页面结构变了"**，否则改版和反爬会被混为一谈。
`BlockedPagesAreDistinguishableFromChangedMarkup` 专门断言这一点。

---
