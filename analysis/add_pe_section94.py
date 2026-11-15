import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\IDB_EVIDENCE.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 不用 IDA 也能取证（第 94 轮，PE 字符串提取）

R93 丢了分析库，于是换了工具：**直接从 PE 里抽 UTF-16LE 字面量**。

```bash
python analysis/pe_strings.py current\\Cybersole.exe pe_strings.txt 8
# read 129243216 bytes → distinct strings: 180228   (9.3 MB 文本)
```

这不需要 IDA，也不需要分析完成 —— 文件本身就有全部字符串。用它查到的第一组事实是
Salesforce Commerce Cloud（Demandware）的控制器族：

| 事实 | 正则/来源 | 命中 |
|---|---|---|
| Demandware 站点 id | `Sites-([A-Za-z0-9_]+)` | 8 个：`asics cpcompany crocs_ crocs_on crocs_s mjsfra StoneNA vans` |
| 控制器名 | `/([A-Z][A-Za-z]+-[A-Za-z]+)` | 191 条 → 去重后 17 个真名 |

确认的控制器（按命中次数）：

```
Checkout-Begin 22        Cart-AddProduct 20      Product-Variation 13
CSRF-Generate 11         Account-Login 10        Cart-RemoveProductLineItem 6
Cart-Get 3               Cart-AddCoupon 5        Cart-MiniCartShow 5
Cart-EditProductLineItem 3                        Product-Show 3
CheckoutServices-SubmitCustomer 3                 CheckoutServices-SubmitPayment 4
CheckoutShippingServices-SubmitShipping 3         CheckoutServices-PlaceOrder 5
Wishlist-AddToCart 2     AdyenUpgrade-Authorize 3
```

> 字符串池会把相邻字面量粘在一起（`Cart-AddProducton` = `Cart-AddProduct` + 下一个的尾巴），
> 所以只把**干净出现**的名字算数，粘连版本仅作旁证。

### 直接结论：replica 又在打不存在的控制器

| replica 的 `DemandwareFlow` 现在 | 镜像里 |
|---|---|
| `Checkout-Submit` | **不存在** → `CheckoutServices-PlaceOrder` |
| `Checkout-SubmitShipping` | **不存在** → `CheckoutShippingServices-SubmitShipping` |
| `Checkout-SubmitPayment` | **不存在** → `CheckoutServices-SubmitPayment` |
| `Cart-Show` | **不存在** → `Cart-Get` |

已全部改正，并把整套词汇固化为 `DemandwareControllers`（17 个真名 + 8 个站点 id +
`Invented` 三个反面例子）。`DemandwareControllerTests` 钉住：
链条名字、子集关系、**三个假名不在词汇表里**、`DemandwareFlow.cs` 里不再有那三个字符串字面量。

这和 Nike 的 `buy/orders/v2` 是同一类错误：**看起来合理、实际属于另一个家族**。

## 附带发现（第 94 轮，来自 IDA 的 PDB 提示框）

载入 `Cybersole.exe` 时 IDA 问：

```
The input file was linked with debug information stored here:
C:\\actions-runner\\_work\\Cybersole\\Cybersole\\Cybersole\\bin\\Release\\net10.0\\win-x64\\native\\Cybersole.pdb
```

两条事实：

1. **目标是用 .NET 10 构建的**（`net10.0`），而且是 GitHub Actions 产出的（`_work` 路径）；
2. 存在一份 **PDB**，但不在本机、也不在微软符号服务器上 —— 选「否」继续无符号分析。
   如果哪天能拿到那份 PDB，`sub_140xxxxxx` 就会变成真名，Nike 那 14 步的名字也能直接读。
'''

if "## 不用 IDA 也能取证" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("IDB_EVIDENCE: PE-extraction section appended")
else:
    print("already present")
