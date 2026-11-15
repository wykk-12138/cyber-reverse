# IDA 取证记录（可复核的查询与其完整性）

每次从二进制里取一组事实，都记在这里：**模式、命中数、`cursor.done`**。
R89 的教训是「分页只给一页」，所以这份文档的核心是第三列：**这次取到的到底是不是全部**。

工具：`python analysis/ida_mcp.py call find_regex @args.json`
（本会话没有 `mcp__ida__*` 工具，走 HTTP JSON-RPC 到 IDA 插件的 `127.0.0.1:13337/mcp`）

| 事实 | 模式 | 命中 | `done` | 轮次 |
|---|---|---|---|---|
| Nike API base URL | `api\.nike\.com` | **20** | ✅ | R87 |
| Nike 标识 | `nike-[a-z-]+｜NIKE-[A-Z]+｜Nike-Kasada-Version` | **7** | ✅ | R88 |
| Nike 市场 | `Nike [A-Z]{2}$` | **42** | ✅ | R89（R86 的 22 是错的） |
| `checkouts/` 片段 | `checkouts/c?/` | 1 | ✅ | R90 |
| 识别签名键 | `IdentificationSignature` | 2 | ✅ | R90 |
| Nike 结账 URL | `buy/checkouts/v3` | 1 | ✅ | R87 |

## 数字与代码的对应

| 代码 | 数量 | 由哪条查询支撑 |
|---|---|---|
| `NikeEndpoints.All` | 19 | `api\.nike\.com` = 20（产品流的 query 拼在字面量里，两条合并） |
| `NikeHeaders.All` | 7 | `nike-…｜NIKE-…｜Nike-Kasada-Version` = 7 |
| `NikeFlow.Countries` | 42 | `Nike [A-Z]{2}$` = 42 |

`IDBEvidenceTests` 把这三条钉在代码侧：**改了常量而没改文档、或反过来，测试都会红。**

## 已知取不到的东西（不要再试）

| 目标 | 结论 | 依据 |
|---|---|---|
| Nike 14 步的**子路径** | 字符串里没有、邻域没有、符号里没有 | R88 三条路都走过；修复后的 IDB 函数名全是 `sub_140xxxxxx` |
| 各步的**请求体字段** | 只能靠字母序字符串池做窗口摘录，无法确定哪个字段属于哪一步 | 池是全局共享的，`checkoutConfig` 后面紧跟着 `chi21120` 这种无关项 |

## 字符串池是**字母序**的（可复用）

`/Views/…` 与 JSON 键都按字母序连续存放，0x28 字节间隔。因此：

```bash
python analysis/dump_strings.py <addr> <size>
```

可以按需摘出一段连续词汇。R90 在 `checkoutCardsinkCallerIdentificationSignature`
（0x146faa644）之后 0x1400 字节里读到 88 个字面量，从 `checkoutConfig` 一路到 `chi21152`——
**跨店铺共享**，所以只能作为「这个词存在」的证据，不能作为「它属于 Nike」的证据。

## 店铺名的存放方式（第 92 轮）

店铺在二进制里以**类型名**形式出现，且带一个 `0x1b 0x08` 后缀（字符串池的长度/元数据标记）：

```
0x143271152  OffSpring\u001b\b
0x143327112  &OffSpringAppHandler\u001b\b
0x1433271ad   OffSpringHandler\u001b\b
```

所以 `^[A-Z]\w+(Handler|Tester)$` 这种带 `$` 锚点的正则**匹配不到它们** ——
尾部控制字符会把 `$` 顶掉。要么去掉 `$`，要么用 `get_string` 按地址取。

### 店铺也出现在 User-Agent 里

同一个店的身份还写在 UA 字符串中，这比类型名更能说明「它是什么平台」：

```
Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 ...) OFFSPRING/3 (iPhone; iOS/18.3.2)
  CFNetwork/3826.400.120 Darwin/24.3.0 poq.ios/21.1.6 poq-webview/26.1.0
OFFSPRING/1 (iPhone; iOS/18.3.2) CFNetwork/3826.400.120 Darwin/24.3.0 poq.ios/21.1.6
```

`poq.ios` / `poq-webview` 是 **Poq**（一个移动电商 App 平台）。
也就是说 OffSpring 跑的是 Poq 的 App，而不是 Magento —— replica 里 `offspring` 挂
`MagentoFlow` 是**没有依据的**（VERDICT 里那条「offspring 平台未定 · C 级证据」由此有了方向）。

### 第 92 轮的查询账

| 事实 | 模式 | 命中 | `done` |
|---|---|---|---|
| 店铺类型名（带后缀） | `(bodega｜undefeated｜offspring｜scheels｜hbx｜converse)` | 137 | ✅ |
| `Handler`/`Tester` 结尾的类名 | `^[A-Z][A-Za-z0-9]+(Handler｜Tester)$` | 53 | ✅ |
| OffSpring 全部字面量 | `OffSpring` | 8 | ✅ |

53 条里绝大多数是框架类名（`EventHandler`、`PropertyChangedEventHandler`…），
真正是店铺的只有 `FootsitesTester`、`FunkoTester`、`OffSpringTester`、`OffWhiteTester` 等少数几条 ——
**这条路径不足以枚举全部店铺，只能用来确认某个店存在。**

## 不用 IDA 也能取证（第 94 轮，PE 字符串提取）

R93 丢了分析库，于是换了工具：**直接从 PE 里抽 UTF-16LE 字面量**。

```bash
python analysis/pe_strings.py current\Cybersole.exe pe_strings.txt 8
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
C:\actions-runner\_work\Cybersole\Cybersole\Cybersole\bin\Release\net10.0\win-x64\native\Cybersole.pdb
```

两条事实：

1. **目标是用 .NET 10 构建的**（`net10.0`），而且是 GitHub Actions 产出的（`_work` 路径）；
2. 存在一份 **PDB**，但不在本机、也不在微软符号服务器上 —— 选「否」继续无符号分析。
   如果哪天能拿到那份 PDB，`sub_140xxxxxx` 就会变成真名，Nike 那 14 步的名字也能直接读。

## 5.18.32 的新库：能做什么、不能做什么（第 95 轮）

数据库重建完成（`auto_analysis_ready: true`，约 14 分钟），`find_regex` 恢复正常。
但**两条「定位代码」的路都被证明走不通**，这是确定结论，不要再试：

| 想做的事 | 结果 | 原因 |
|---|---|---|
| `xrefs_to <字符串地址>` | `xref_count: 0` | NativeAOT 不产生数据交叉引用，字符串通过偏移表间接访问 |
| `find type=immediate/imm/refs/ref/data` 找绝对地址 | `count: 0`（全部类型） | 同上：代码用 RIP 相对寻址，绝对地址不是立即数 |
| `insn_query` 找引用该地址的 `lea` | `scanned: 200000, count: 0` | ① 需要整数操作数；② 默认只扫 20 万条指令（全 `.text` 是 200 万级） |

> **结论：在这份镜像上，「哪个函数引用了这条字符串」无法用 IDA 查出来。**
> 能做的是「这条字符串存在/不存在」（`find_regex`）和「函数级反编译给定地址」（`decompile`），
> 前者已经用了 5 轮，后者缺一个入口地址 —— 而入口地址只能从前者来，闭环断在这里。

### 本轮真正拿到的东西：Demandware 的完整 URL 模板

```
find_regex "Sites-[A-Za-z0-9_]+-Site"  limit 12  →  5 条
```

```
https://www.cpcompany.com/on/demandware.store/Sites-cpcompany-Site/
https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Cart-AddProduct
https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Product-Variation?pid=
https://www.stoneisland.com/on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-SignupSubmit
on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-Config
```

四条独立事实：

1. **路径形状确认**：`/on/demandware.store/Sites-{site}-Site/{locale}/{controller}` —— replica 的
   `Controller()` 一直是对的（这条是难得的「猜对了」）。
2. **locale 不是常量**：Marc Jacobs 用 `default`，Stone Island 用 `en_US`。
3. **两个新控制器**：`SaleRegistration-SignupSubmit`、`SaleRegistration-Config` —— 抽签/发售登记链。
4. **站点 id ↔ 域名**：`cpcompany→cpcompany.com`、`mjsfra→marcjacobs.com`、`StoneNA→stoneisland.com`。
   只有这三对是**同一字面量里成对出现**的；`asics/crocs/vans` 只出现站点 id，**不猜域名**。

已固化为 `DemandwareControllers` 的 `Hosts` / `SitePath()` / `SiteRoot()`，
`DemandwareControllerTests.TheSitePathReproducesTheImagesUrls` 逐字比对三条 URL。
