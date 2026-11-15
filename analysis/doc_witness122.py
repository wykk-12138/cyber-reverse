import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 那把尺子量了八个流程：**只有两个有证人**（第 122 轮）

R121 的规则是「lambda 字面量证明归属」。R122 把它量到所有流程上，结论是**这条规则很窄**：

| 流程 | 有归属证人？ | 证人范围 |
|---|---|---|
| John Lewis | **有** | 方法 20–39 |
| Nike | **有** | 方法 41–58 |
| Pop Mart / Demandware ×2 / CollectPlus / StructureToken ×2 | **无** | — |

**证人只在「序数和流程自己的序号对得上」时成立。** Pop Mart 的 lambda 字面量里
**没有任何一条**带 104–153 范围的序号 —— 所以它的 121–130 缺口**没有证人**，
R120 那九条候选**保持候选**。

### 为什么名字本身不算证据

扫描找到过这样的 lambda 表：

```
1:Authorize   2:SubmitShippingAddress     ← 看着像 Nike 的步，其实不是
```

Nike 的 `Authorize` 在**序号 42**。序号 1 的 `Authorize` 是**另一个类**的方法，只是同名。

> **名字会重名，序号不会跨类。** 所以「这个名字出现在一条 lambda 表里」什么都不证明；
> 只有「这条表的序号区间和那个流程重合」才证明。

### 扫描的副产品：Pop Mart 的**购物车类**

| 序号 | 方法 |
|---|---|
| 1 | `GetCartDataList` |
| 2 | `FetchCoupons` |
| 3 | `SubmitDiscount` |
| 4 | `ClearCart` |
| 5 | `FetchAddress` |
| 6 | `FetchAddress`（重载，保留两条） |

这六个名字与 Pop Mart 的 `/shop/v1/*` 端点族**逐一对应**（`cartDataList`、`couponsList`、
优惠券提交、地址拉取）。

**所以 Pop Mart 有两半：**

| 半 | 形态 | 规模 |
|---|---|---|
| 抽签 / 积分 / 预约 | 24 步的 flow | `EnterDraw`、`RedeemLuckPoints`、`EnterReservation` |
| **购买** | 6 方法的购物车类 | `GetCartDataList`、`FetchCoupons`、`SubmitDiscount`、`ClearCart`、`FetchAddress` |

这是 R116「抽签与结账是两套」的**第二个独立证据** —— 那次是从「25 个端点没人点」推的，
这次是从「有另一个类专门做这几件事」看到的。
'''

if "## 那把尺子量了八个流程" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("witness survey documented")
else:
    print("already present")
