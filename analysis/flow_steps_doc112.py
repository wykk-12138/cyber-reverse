import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 每个店的步骤清单（第 111–112 轮，字符串池实证）

每个流程的步骤在池子里是**一段相邻字面量**，带编译器分配的 `d__N` 序号 ——
所以「这个店几步、先后顺序如何」不再靠猜。

| 店 / 流程 | 步数 | 关键步骤 | 对应端点族 |
|---|---|---|---|
| Nike | **16** | `StartEcomSession 41` … `SubmitOrder 58` | `NikeEndpoints`（R87）+ persisted GraphQL（R101） |
| Pop Mart | **24** | `StartDrawFlow 115`、`FindMegaDraw 133`、`RedeemLuckPoints 137`、`EnterReservation 153` | `/shop/v1/*`（R100） |
| John Lewis | **17** | `WebHandOver 23`、`GuestCallback 25`、`SubmitOrderStripe 32`、`GetStripePaymentIntent 39` | `bff/v1..v4`（R103） |
| Demandware 经典 | **12** | `InitiateCheckout 33`、`GenerateCSRF 34`、`SubmitConsignment 37`、`ConfirmPayment 43` | 经典控制器（R94） |
| Demandware 双路 | **15** | `StartAppFast 36`、`GetCartDw 39`、`AddToCartApp 41`、`AddToCartAppDw 42`、`SaveSessionDw 43` | SCAPI + 经典（R101 / R107） |

### 三条从步表里读出来的结论

1. **Pop Mart 有 24 步，比 Nike 还多** —— 它不是「结账流程」，是抽签/积分/预约平台：
   `EnterDraw`、`FindMegaDraw`、`RedeemMemberPoints`、`RedeemLuckPoints`、`EnterExhibit`、
   `EnterReservation`。这解释了为什么它的端点族有 39 条（R100）。
2. **Demandware 的两套步数是两件事**：经典 12 步（`SubmitConsignment` = Salesforce 的「配送」），
   和 15 步的**双路流程** —— `AddToCartApp` 与 `AddToCartAppDw`、`GetCartDw`、`SaveSessionDw`
   同时存在，说明原版在某些店上**两条路都养着**。这正是 R101 在端点里看到的 SCAPI/经典并存，
   也是 R107 接进 `DemandwareFlow` 的那个形状。
3. **John Lewis 的 Stripe 链是完整的**：`SubmitOrderStripe` → `AuthenticatePayment` →
   `HandleRequiresAction` → `GetStripePaymentIntent` —— 四个步骤才是一个 3DS 循环，
   少一个就卡在 `requires_action`。

已固化为 `Cybersole.Stores.Flows.StoreFlowSteps`（5 个流程 + `FlowFor()` + `AllStepNames()`），
`StoreFlowStepsTests` 六条钉住：五个步数、序号升序、Pop Mart 的抽签/积分/预约、
Demandware 双路的 App/Dw 成对、经典链里的 `SubmitConsignment`、按名字反查所属流程。
'''

if "## 每个店的步骤清单" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("ENDPOINT_FAMILIES: step tables appended")
else:
    print("already present")
