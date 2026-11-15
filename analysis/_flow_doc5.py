import io
p = r'D:\projects\cyber-reverse\replica\docs\FLOW_SEQUENCES.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## 十一、把两种布局合起来清点：**18 条流水线 / 141 步**（R273）

### 1. 布局 B 会混进非商店类

放宽判据（≥2 行、间隔 ≤0xC0）后 B 有 **129 段 / 380 步**，但里面混着编辑器的 `Copy/Cut/Paste`、
连接的 `ConnectionLoop`、传感器的 `GenerateSensor` —— **B 抓的是"所有异步类"，不是"所有商店流程"**。

### 2. 用"结账词汇"过滤

一段里若出现 ≥2 个结账动作名（`AddToCart`/`FindProduct`/`GetCheckout`/`SubmitOrder`/`SubmitShipping`/
`SubmitBilling`/`GetCartCsrf`/`SubmitDiscount`/`EnterRaffle` …）才算流水线：

```
布局 A 69 段 -> 流水线 15 段
布局 B 129 段 -> 流水线 3 段
合并去重         -> 18 条流水线 / 141 步
```

### 3. 最长的几条（真实输出）

| 段基址 | 步数 | 开头 |
|---|---|---|
| `0x034b14b8` | 15 | `FindProductMulti, FindProductFlow, FindVariant, AddToCartMulti, GetCheckout, GetMerchantCode …` |
| `0x3371cea` | 15 | `Start, GetHome, FindProduct, GetProductHtml, FindVariant, AddToCartPreload …`（**John Lewis**） |
| `0x034b23a5` | 12 | `EditLine, AddToCart, GetCheckout, GetShippingRate, SubmitShipping, CalculateTaxes …` |
| `0x03390d79` | 11 | `FindProduct, AddToCart, SubmitDiscount, GetCheckout, GetShippingRates, GetPaypalId …`（Shopify） |
| `0x033895e0` | 11 | `GetCsrf, GetCheckout, ApplyDiscount, GetShippingRates, SubmitShippingInformation, SubmitPaymentDetails …` |
| `0x337fa33` | 10 | `GetCart, ClearCart, FindProduct, AddToCart, ReplaceProduct, GetCsrf …` |

### 4. 与复刻件的关系

复刻件的 `StoreFlowSteps` 目前只钉住六条流。这里的 18 条是**可以逐条核对/扩充的上限**，
但每条的**商店归属**仍然只解出 9 条（独有指纹），其余 9 条只能按"步骤形状"归档。

> 注意：`0x3371cea` 只有 15 步（含 `Start`），而正文里写的 John Lewis 是 16 步 —— 差的一步是
> `21`/`23` 那种**跳号**造成的。**段内序号不连续，别拿"步数"当"序号差"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('FLOW_SEQUENCES.md: the combined inventory (18 pipelines / 141 steps) is recorded')
