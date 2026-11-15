import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\NIKE_PARITY.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 14. 步数是 **16**，不是 14 —— 而且名字是编译器给的（第 111 轮）

R111 在重建后的 IDA 库里，字符串池中**一段相邻的字面量**就是整条 Nike 结账链，
带着编译器分配的 `d__N` 序号：

```
d__41 StartEcomSession      d__42 Authorize              d__43 GetAccessToken
d__44 FindVariant           d__46 CreateBasket            d__48 SubmitCustomer
d__49 ValidateAddress       d__50 SubmitShippingAddress   d__51 GetShippingMethods
d__52 SubmitShippingMethod  d__53 SubmitBillingAddress    d__54 BeginCheckout
d__55 CheckInventory        d__56 GetShopperIp            d__57 GetPaymentMethods
d__58 SubmitOrder
```

**16 步。** 文档从第 50 轮起一直写「14 步」，那是**读了一段就当全表**的又一次重犯。

序号跳过了 45 和 47 —— 那两个是编译器在两步之间插入的 `MoveNext` 辅助方法，
**不是步骤**。所以「有缺口」不代表「漏了步骤」。

### 手写清单会合并的那两对

| 手写时容易合并 | 镜像里 |
|---|---|
| `StartEcomSession` + `BeginCheckout` | **两步**（41 / 54） |
| `Authorize` + `GetAccessToken` | **两步**（42 / 43） |

**14 → 16 差的正好是这两对。** 这也解释了为什么之前那张表「看起来对、数起来少」。

已固化为 `Cybersole.Stores.Flows.NikeSteps`（16 条 + `Position()` + `IsStep()`），
`NikeStepTests` 五条钉住：16 条、序号升序、**只缺 45/47**、两对必须不同、位置 1-based。

### 与 persisted GraphQL 对上了

`BeginCheckout` / `SubmitOrder` / `GetPaymentMethods` 这三步，
正好对上第 13 节那 6 个 `persisted?operationName=`（`Proposal` / `SubmitForCompletion` /
`PollForReceipt` / `PaypalDetails` / `PaypalToken` / `CheckoutExtensionSessionToken`）。
**两条独立证据指向同一个形状：Nike 的结账后半段是持久化 GraphQL，不是 REST 子路径。**
'''

if "## 14. 步数是 **16**" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("NIKE_PARITY section 14 appended")
else:
    print("already present")
