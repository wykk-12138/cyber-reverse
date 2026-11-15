import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 更正：`/v5/Order/` 是 **Nike** 的，不是 Scheels 的（第 127 轮）

用「这个族记全了吗」做普查，第一条就抓到**我自己造出来的端点**。

### 事情经过

R115 我记了 Scheels 移动 API 的第三个端点：

```csharp
public const string Orders = Base + "/v5/Order/";     // ← 拼出来的
```

理由是「见过一个 `/v5/Order/` 路径」。R127 普查把全库 `v5/Order` 找了一遍，只有一条字面量：

```
https://www.nike.com/gs/checkout-api/api/v5/Order/
```

**是 Nike 的，而且是 Nike 的下单端点** —— 本会话从 R87 起一直问「Nike 的订单打到哪」，
答案就在这儿：不在 `api.nike.com`，而在 `www.nike.com/gs/checkout-api/api`（游客结账代理），
所以它从没出现在 `api.nike.com` 那 19 条里。

### 三处修正

| 位置 | 修正 |
|---|---|
| `ScheelsMobile` | 3 端点 → **2 端点**（`v5/auth/guest`、`v5/products/`） |
| `DualApi.AppSteps` | `SubmitOrderApp` 的映射**删除**（目标不存在了），该步回到未映射 |
| `NikeEndpoints` | **新增 `OrderV5`** —— Nike 的下单端点 |

### 这是第几次同类错误

「凭见过的片段拼一个端点出来」：

| 轮次 | 编出来的东西 | 真相 |
|---|---|---|
| R87 | Nike `buy/orders/v2` | 不存在 |
| R91 | BSTN `/api/beast` | 不存在 |
| R94 | Demandware `Checkout-Submit*` | 名字不对 |
| R96 | Shopify `cart/change.js` | 不存在 |
| R100 | Pop Mart `/api/*` | 不存在 |
| **R115→R127** | **Scheels `/v5/Order/`** | **是 Nike 的** |

六次。所以这一轮把规则又说了一遍，并且这次**写进断言**：

> **一个端点的「主机 + 路径」必须来自同一条字面量。** 跨字面量拼接 = 发明。
> `TheOrderPathBelongsToNikeNotScheels` 断言 `NikeEndpoints.OrderV5` 含 `nike.com` 且**不含**
> `scheels`，同时断言 Scheels 族里**没有任何一条**含 "Order"。

### 顺带：三份普查数据

| 主机 | 不同路径数 |
|---|---|
| `apihub.scheels.com` | **17**（全在 `frontastic/action/`） |
| `mobile-api.scheels.com` | **2** |
| `checkout.johnlewis.com` | **15**（12 是 `bff/*`，另 3 条是裸路径 `/callback/login/guest?email=`、`/delivery`、`/payment`） |
| `api.nike.com` | **19**（`payment/*`、`buy/*`、`deliver/*`） |
| `api2.endclothing.com` | **2** |

**John Lewis 那 15 条里，`/callback/login/guest?email=` 是表里没有的** —— 又一个「窗口外」。
'''

if "## 更正：`/v5/Order/` 是 **Nike** 的" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("correction documented")
else:
    print("already present")
