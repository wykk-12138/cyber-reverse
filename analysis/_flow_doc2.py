import io
p = r'D:\projects\cyber-reverse\replica\docs\FLOW_SEQUENCES.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## 六、把段绑定到商店：三条路，两条走通一半、一条死

### 1. 方法名指纹（**9 / 69** 段绑上，且看起来是对的）

用"独有名词"（`Get6Js`/`FetchSensor`→Nike、`GetLotteryForm`/`CheckRaffleStatus`→Popmart、
`AddToCartStoreFront`/`SubmitDiscount`→Shopify、`DeleteBasket`/`SubmitBilling`→Demandware），
**只有 9 段命中**，但命中都很像真的：

| 地址 | 指纹 | 全段 |
|---|---|---|
| `0x03390d79` | Shopify | `26:FindProduct, 28:AddToCart, 29:SubmitDiscount, 30:GetCheckout, 31:GetShippingRates, 33:GetPaypalId, 34:GetPaypalBearer, 35:ProcessPaymentPaypalCreditCard, 37:ProcessOrderPaypalCreditCard, 38:SubmitOrder, 39:ProcessOrder` |
| `0x0336dea7` | Shopify | `33:GetCsrf … 38:SubmitDiscount, 39:SubmitShipping, 40:SubmitOrder` |
| `0x0338a27a` | Demandware | `12:GetShippingRates, 13:SubmitShipping, 14:SubmitBilling, 15:SubmitOrder` |

用**通用**名词（`GetCsrf`/`SubmitOrder`/`SubmitShipping`）会命中 27 段，但那些名字几乎每家都有 → **不可用**。

### 2. 段邻近字面量里找商店名：**0 / 69**

**死路。** 段附近从没出现过商店名 —— 类名不在字面量池的这一带。

### 3. 用已解开的 John Lewis 段当锚点：未做

## 七、两个数据质量警告（这一轮才发现的）

1. **段内序号并不连续**：`0x03398963` 是 `5:CheckRaffleStatus, 68:GenerateVariables`。
   所以"连续段"其实是**同一个类的方法在元数据里的顺序**，中间可以跳号；
   拿它当"步骤表"时**不能按序号连续性推步骤**。
2. **序号可能是解析产物**：`0x03380d89` 里出现 `356:SubmitPayment` —— 明显是相邻数字粘连。
   **凡序号 > 200 的一律复核**再入库。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('FLOW_SEQUENCES.md updated with the binding results and data warnings')
