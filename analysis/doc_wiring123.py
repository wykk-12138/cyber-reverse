import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## Pop Mart 的购买半边走通了（第 123 轮）

R122 找到那个 6 方法的购物车类之后，这一轮把能落的三个落进 `PopMartFlow`：

| 类方法 | 端点 | 状态 |
|---|---|---|
| `GetCartDataList` | `shoppingCartDataList` | **已实现** `GetCartAsync` |
| `FetchCoupons` | `coupons/list` | **已实现**（私有 helper，由购物车读取调用） |
| `SubmitDiscount` | `coupons/verify` | **已实现** `SubmitDiscountAsync` |
| `ClearCart` | —— | **不实现**：端点族里没有 |
| `FetchAddress` | —— | **不实现**：端点族里没有 |

### 为什么 `FetchCoupons` 是 helper 而不是 step

`StoreFlow` 的步骤词表里**没有** `FetchCoupons` 这个虚方法。为了把行为做出来而去**发明一个 step**，
等于往词表里塞一个二进制从没要求过的东西 —— 所以它是私有 helper，由购物车读取调用，
**行为存在，虚构的 step 不存在**。

### 一个行为上的变化

改动前：商品 → 加购 → 直接下单，**从不读自己刚建的购物车**，所以优惠券和地址根本无法影响订单。
改动后：`GetCart → FetchCoupons → SubmitDiscount → 下单`，顺序与购物车类一致
（测试断言 coupons 调用在 cart 之后）。

### 优惠券被拒不是失败

```csharp
c.Session.Vars["discount"] = "absent" | "applied" | "rejected";
return StepOutcome.Success();   // 三种都算走完了
```

一个用不上的券**不会让购物车不可下单** —— 这是 R99「没有这个功能 ≠ 这个功能失败了」的同一条原则。
测试断言 `SubmitDiscountAsync` 体内**没有** `StepOutcome.Fail`。
'''

if "## Pop Mart 的购买半边走通了" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("pop mart wiring documented")
else:
    print("already present")
