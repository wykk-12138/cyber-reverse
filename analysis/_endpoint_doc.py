import io
p = r'D:\projects\cyber-reverse\replica\docs\ENDPOINT_LEDGER.md'
t = '''# 端点证据账（R293）

复刻件 `src/` 里的 API 路径，逐条对照镜像字符串池的结论。重算：`tools/endpoint-ledger.py`。

## 总数

| 桶 | 条数 | 含义 |
|---|---|---|
| **逐字命中** | **44** | 路径在池子里原样存在 |
| **由片段组成** | **23** | 整条没有，但它的尾段在池子里（如 `/cart/add`）—— 属于组合，不是自造 |
| **无证据** | **22** | 整条和尾段都找不到 |

```
复刻件 API 路径 89  =  44 逐字 + 23 组合 + 22 无证据
```

## 无证据的 22 条（`EndpointEvidenceRatchetTests` 盯着）

| 路径 | 使用处 |
|---|---|
| `/account/recover` | `Flows/StoreFlow.cs` |
| `/account/verify` | `Flows/MagentoFlow.cs` |
| `/api/basket/v1/items` | `Flows/FarfetchFlow.cs` |
| `/api/beast` | `Flows/BstnFlow.cs` |
| `/api/checkout/submit` | `Flows/RetailFlows.cs` |
| `/api/checkout/v1/basket/{basketId}` | `Flows/FarfetchFlow.cs` |
| `/api/checkout/v1/basket/{basketId}/place-order` | `Flows/FarfetchFlow.cs` |
| `/api/checkout/v1/basket/{basketId}/shipping` | `Flows/FarfetchFlow.cs` |
| `/api/order/submit` | `Flows/PopMartEndpoints.cs` |
| `/api/preorder/entry` | `Flows/RetailFlows.cs` |
| `/api/search` | `Flows/ScheelsFlow.cs` |
| `/api/stock` | `Flows/PopMartEndpoints.cs` |
| `/api/v1/carts/{c.Session.CartId}` | `Flows/HbxFlow.cs` |
| `/api/v1/carts/{c.Session.CartId}/items` | `Flows/HbxFlow.cs` |
| `/api/v2/shop/countries` | `Flows/HbxFlow.cs` |
| `/collections/new-releases` | `Flows/MagentoFlow.cs` |
| `/rest/V1/carts/mine/totals` | `Flows/MagentoFlow.cs` |
| `/v1/buys` | `Flows/GoatFlow.cs` |
| `/v1/buys/{c.Session.CartId}` | `Flows/GoatFlow.cs` |
| `/view/resources/getUserInfo` | `Flows/HybrisFlow.cs` |
| `/v1/carts/{c.Session.CartId}/items` | `Flows/HbxFlow.cs` |

## 这 22 条怎么处理（按优先级）

1. **先找证据**：有些可能以别的形态存在（拼接、模板、变量前缀），值得再查一轮；
2. **找不到就标"推断"**：在源码注释里写明"无镜像证据"，不冒充 1:1；
3. **不删**：它们是可用逻辑，删掉会让对应商店流程退化；账本负责让它们**可见**，而不是让它们消失。

## 口径说明（重要）

- "逐字命中"= 整条字符串在池子里；
- "由片段组成"= 尾 1–2 段能在池子里找到 —— 这是**弱证据**，只证明"名字不假"，不证明整条路径对；
- 池子里还有 218 条 API 形状路径，其中多数（`/Assets/*`、挑战 URL、3DS 回调）不属于本账范围。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ENDPOINT_LEDGER.md written')
