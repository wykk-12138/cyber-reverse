import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## Pop Mart：24 步 ↔ 39 端点（第 116 轮）

本会话里**步数与端点数都最大的一对**。名字一致的地方连线，不一致的地方**留空并记下来**。

| 步 | 端点 |
|---|---|
| `GetOrders` | `/shop/v1/order/list` |
| `StartDrawFlow`、`FindDraw` | `/shop/v1/drawScratch/detail?uniqCode=` |
| `EnterDraw` | `/shop/v1/drawScratch/draw` |
| `ChooseGoods` | `/shop/v1/drawScratch/chooseGoods` |
| `FindMegaDraw`、`EnterDrawEvent` | `/shop/v1/drawScratch/megaDraw/hit` |
| `RedeemMemberPoints` | `/shop/v1/redeem/points_redeem_draw` |
| `RedeemLuckPoints` | `/shop/v1/redeem/lucky_points_redeem_draw` |
| `FindExhibit` | `/shop/v1/storeOfflineDraw/info?alias=` |
| `EnterExhibit`、`EnterReservation` | `/shop/v1/storeOfflineDraw/join` |
| `FindDates` | `/shop/v1/store_ticket/dateList` |
| `FindTimeSlots` | `/shop/v1/store_ticket/mainPage?uniqID=` |

**14 对。**

### 留空的 10 步（名字不settle）

```
CheckResult        StartDrawCheckFlow   StartDrawEventFlow   CheckDraw
FetchAliases       FetchDetails         StartExhibitFlow     StartReservationFlow
GetInstoreOrders   还有 1 个
```

`CheckResult` 可能是 `drawScratch/detail` 的轮询，也可能是另一个接口 —— **镜像里没有任何东西能定这个**，
所以留空。这 10 步现在是「待抓包确认」的清单，而不是一片空白。

### 另一侧：39 个端点里 25 个没有被任何步名点到

包括整个收银台族（`cash/desk/{adyen,alipayGlobal,paypal,stripe}`）、
`coupons/*`、`promotion/getList`、`freight/result`、`mission/*`。
这些是**结账后半段**用的 —— 而 Pop Mart 的 24 步全是「抽签/积分/预约」，
**结账那半段不在这个 flow 里**。这本身就是一条结论：**抽签流程和结账流程是两套。**

> 这张表和 R115 的 Scheels 表一样，写的是
> `name correlation … no request capture … unmapped steps and endpoints are recorded, not guessed`。
> 测试断言这句话必须留着。
'''

if "## Pop Mart：24 步 ↔ 39 端点" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("pop mart map documented")
else:
    print("already present")
