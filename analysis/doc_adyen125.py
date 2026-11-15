import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 第六个流程：Adyen/PayPal 快捷结账（第 125 轮）

上一轮说「下一步去查那四个无端点 app 步」。这一轮问了更根本的问题：**SCAPI 族是不是我记全了？**

### 两个结果，来自同一个问题

**结果一（否定，确认 R124）**：`/scapi/` 一共 **9 条** —— 7 个 `ShopperBaskets`（create / add /
update ×5）+ 2 个 `ShopperLogin`。**没有下单，没有优惠券。** 所以那四个 app 步确实无端点。

**结果二（新发现）**：一条相邻字面量里藏着一个**全新的流程**：

| 序号 | 步 |
|---|---|
| 33 | `AdyenSession` |
| 34 | `SubmitPaymentPayPal` |
| 35 | `AdyenPayPalPatchOrder` |
| 36 | `GetPayPalAccessToken` |
| 37 | `AdyenSaveExpressShopperDetails` |
| 38 | `ShowConfirmationPaymentFromComponent` |

### 读法：又用上了 R119 的教训

字面量的第一个 token 是 `<PlaceOrder>d__32` —— **它属于前一条字符串的尾部**。
照字面读会得到「7 步 + 一组不能升序的序号」；去掉尾巴才是 **6 步，序号 33–38 完全连续**。

> `TailToken` 常量把这件事写在代码里，测试断言 `PlaceOrder` **不是**这个流程的步。

### 与 R124 正好相反的形状

| 路 | 能不能在一侧走完 |
|---|---|
| Demandware app 路 | **不能** —— 只到购物车，必须切回经典 |
| **Adyen/PayPal 快捷路** | **能** —— 六个步全在一侧，序号连续无缺口 |

### 顺带补进词表的两个控制器

```
Adyen-SaveExpressShopperDetails      ← 步骤 37 的落地端点
ShopperInfo-IP                        ← 风险检查读的 shopper IP 端点
```

`Adyen-SaveExpressShopperDetails` 这个控制器**在本会话的表里从来没出现过** ——
和 R117 的 `CheckoutServices-SubmitBilling` 是同一种遗漏：表是窗口读出来的，窗口外还有东西。
'''

if "## 第六个流程：Adyen/PayPal 快捷结账" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("adyen flow documented")
else:
    print("already present")
