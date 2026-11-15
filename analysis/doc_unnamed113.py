import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

old = """### 三条从步表里读出来的结论"""
new = """### 三段没有店名的流程（第 113 轮）

池子里这三段没有配店名，所以代码里也**不写品牌** —— 只记「凭什么认出它」：

| 流程 id | 步数 | 识别依据 |
|---|---|---|
| `collectplus-app` | 17 | `GetCollectPlusLocations` / `SubmitCollectPlus`（CollectPlus 是英国自提网络）+ `*App` 步 + 以 `GetPaymentUrl` 收尾 |
| `structure-token-multi` | 15 | `GetMerchantCode` → `GetStructureToken` → `CreateTransaction` → `ProcessPayment`，多规格（`FindProductMulti`）+ `CalculateTaxes` |
| `structure-token-single` | 12 | 同一引擎的单规格形状（`EditLine` 开头），`GetStructureToken` 在序号 40 |

「structure token」不是编的名字：镜像里还有 `PaymentData.UrlStructureTokenEncoded`、
`_structureToken`、`#UrlStructureTokenEncoded` —— 它是真实支付集成的一个字段。
**但具体是哪家支付商、哪个品牌，没有证据，所以不写。**

两条 structure-token 流程**共享 10 个步骤名**（`GetCheckout`、`GetMerchantCode`、
`GetShippingRate`、`SubmitShipping`、`GetStructureToken`、`CreateTransaction`、`SubmitPayment`、
`GetPayPalToken`、`SubmitPayPal`、`ProcessPayment`）—— 同一引擎、两个店面。
测试里的这个数字**是从两份列表算出来的**，不是手数的（我手数了两次都错：先 8、后 9）。

### 三条从步表里读出来的结论"""

if old in t and "collectplus-app" not in t:
    t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("unnamed flows documented")
else:
    print("anchor missing or already documented")
