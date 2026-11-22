# 核心覆盖表（生成物 —— 不要手改）

由 `python tools/core_coverage.py` 生成。完成判据 (f) 的两半：
**复刻件侧可算**，**原版站清单不可得**，后者按 (a) 的形态写 Unknown + 缺什么。

## 一、复刻件侧（可复算）

| 度量 | 值 | 命令 |
|---|---|---|
| flow 文件 | 20 | `ls src/Cybersole.Stores/Flows/*Flow*.cs` |
| 覆写步骤总数 | 405 | 本文件生成时统计 |
| 其中报告「端点为 Unknown」的 | 3 | 同上（匹配 `endpoint unknown` / `not captured`） |
| 含报告的 flow | 2 | 同上 |
| 端点常量 / 逐字在池 | 249 / 249 | `python tools/endpoint-provenance.py` |
| 常量 invented / unresolved | 0 / 1 | 同上 |
| inline 字面量 / 不在池 | 381 / 33 | 同上 |
| inline 已登记 / 未登记 | 33 / 0 | 同上 |
| 端点门 exit | **0** | 同上 |

### 逐 flow

| flow | 覆写步骤 | 报告 Unknown | 行数 |
|---|---|---|---|
| `AoFlow.cs` | 5 | 0 | 104 |
| `BstnFlow.cs` | 12 | 0 | 196 |
| `DemandwareFlow.cs` | 16 | 0 | 795 |
| `DicksSportingGoodsFlow.cs` | 6 | 0 | 145 |
| `FarfetchFlow.cs` | 13 | 0 | 223 |
| `FlowStoreModule.cs` | 4 | 0 | 61 |
| `FootsitesFlow.cs` | 21 | 0 | 468 |
| `GoatFlow.cs` | 11 | 0 | 329 |
| `HbxFlow.cs` | 13 | 0 | 330 |
| `HybrisFlow.cs` | 13 | 0 | 375 |
| `MagentoFlow.cs` | 57 | 0 | 1626 |
| `NikeFlow.cs` | 23 | 0 | 980 |
| `NikeGsFlow.cs` | 5 | 0 | 68 |
| `PopMartFlow.cs` | 27 | 0 | 715 |
| `PoqAppFlow.cs` | 8 | 0 | 242 |
| `RetailFlows.cs` | 115 | 0 | 2499 |
| `SauconyFlow.cs` | 9 | 1 | 152 |
| `ScheelsFlow.cs` | 15 | 0 | 353 |
| `ShopifyFlow.cs` | 25 | 2 | 1367 |
| `SportsshoesFlow.cs` | 7 | 0 | 130 |

## 二、原版侧（不可得 —— Unknown + 缺什么）

**问题**：原版支持哪些站？

**结论**：**Unknown。**

**已试并全空的取证路径**（R1040）：

| 路径 | 查询 | 结果 |
|---|---|---|
| 反射元数据里的命名空间 | `str "Stores\.Flows\.[A-Za-z0-9_]+" --limit 600` | **0** |
| 类型名 | `str "FarfetchFlow"` | **0** |
| 任意 `*Flow` 类型 | `str "[A-Za-z]+Flow,"` | 1（TPL Dataflow 文档，无关） |
| 站名 + 步骤的数据行 | `str "^[A-Za-z0-9 .&'-]+ Checkout$"` | 34，其中站名 **4** 条 |

**为什么可能是服务端下发**：复刻件有 20 个 flow 文件，而二进制里没有对应数量的名字；镜像有 `api.cybersole.io` 与 `/connect/app`（R1032）。

**缺什么**：`api.cybersole.io/connect/app` 的响应。取它需要**原版登录凭据** —— 那是本工作允许停下等 YG 的两类事之一。

**已得的替代证据**：`Farfetch` · `Farfetch Checkout` 在池里，且后者与 `Shopify Checkout` · `Kith EU Checkout` · `FUNKO CHECKOUT` 同列 —— 4 个站的**定制结账文案**。那不是完整清单，但它是**二进制侧对具体站的正面证据**。

### 而 Nike 链上有一个**更具体**的未决问题

镜像里有 `api.nike.com/buy/` 的 **7** 条实名 URL：`checkouts/v3` · `checkout_previews/v3` · `checkouts_jobs/v3` · `checkout_previews_jobs/v3` · `fulfillment_offerings_jobs/v2` · `partner_cart_preorder/v2` · `partner_cart_preorder_jobs/v2`。

**所以「Nike 没有结账面」是错的** —— 而有的是**两个**候选资源。

**未决的是**：哪一个承接 **shipping 写入**（`checkouts/v3` 还是 `checkout_previews/v3`）。

**为什么不能靠名字猜**：R1013 换成 `checkouts/v3` 被 R1014 撤回，理由是「路由存在不解决哪个承接写入」；R48 的裁决「换一个猜测只是移动失败」就在 `NikeFlow.cs` 里那段代码上方。

**更正 R1044/R1045 的误判（该项可取证，非不可得）**：

R1044 曾对 `0x147053d8c`（`checkouts/v3`）与 `0x147053c94`（`checkout_previews/v3`）直接查 `xrefs_to` 得 `0`，
并据此误判为「字符串无 xref，只剩全盘数据流工程，记为不可得」。
**错因是漏了 NativeAOT 冻结字符串对象头偏移（R702 早已验证）**：
冻结 `System.String` 布局为 `[MethodTable*: 8B][Length: 4B][UTF-16 chars...]`；
`ida.py str` 返回的是字符首地址 `chars_va`，而 `.text` 中 `lea reg, [rip+disp32]` 指向的是对象头 **`obj_va = chars_va - 12`（`-0x0C`）**。

对 `chars_va - 12` 实测（可复算命令：`python analysis/disp32_scan_any.py 0x147053d80 0x147053c88` → `python analysis/site_to_func.py 0x140B26A5E 0x140B1EDB1`）：

| URL 串 | `chars_va` | 对象头 `obj_va`（`-12`） | `.text` 引用点 | 所属业务函数（`.pdata`） |
|---|---|---|---|---|
| `checkouts/v3/` | `0x147053d8c` | `0x147053d80` | `0x140B26A5E` | **`sub_140B248A0`..`0x140B26B87`（8,935 字节）** |
| `checkout_previews/v3/` | `0x147053c94` | `0x147053c88` | `0x140B1EDB1` | **`sub_140B1DCC0`..`0x140B1EEC9`（4,617 字节）** |

**→ 已结案（R1076，详见 `docs/NIKE_PARITY.md` §15）**：**两个 POST 都承接** —— 配送块内联在
`checkout_previews/v3` 的 request 体（`sub_140B1DCC0`），订单提交是 `checkouts/v3` 的 POST
（`sub_140B248A0`，请求级 `paymentToken`）。`NikeFlow.cs` 的 SubmitShipping / SubmitOrder
已按反编译落地（钉测 `NikeBuyRequestTests`），Nike 行占位只剩 GetPaymentMethods / SubmitPayment（归队列②支付层）。

**→ Farfetch 分类结案（R1077）**：镜像内足迹仅显示名×2（站点目录条目 `{name, display, typeId 4, flag 1}`，
构造于 70KB 设置描述符构建器 `sub_140F7DDE0`）+ 结账类型枚举 `'Farfetch Checkout'`（`sub_1407528C0` 的
任务设置数组，与 Shopify / Kith EU / Finishline 并列）——**零路由字面量**。传输层为服务端下发：
`https://api.cybersole.io/connect/app`（0x14705357c，`sub_140F3D400`）以 **ConfigAdded / SharedAdded /
ConfigRemoved / SharedRemoved / SubscribeGroups / UnsubscribeGroups** 六键同步配置条目。配置条目的 schema
需原版登录凭据捕获 —— `FarfetchFlow` 的 7 条占位据此改判为「凭据受阻」分类（消息保留 `endpoint unknown`
短语，本表计数不变，缺的条件已在消息与流程头写明）。

## 三、风控清单（可复算）

由 `VendorWiring.Rows` 与 `tests/Cybersole.Tests/VendorWiringTests.cs` 逐条钉住：
接线表已于 R1282 删除（`VendorWiring.cs` 在运行期无真实调用者，取证与对照移入 `docs/VENDOR_WIRING.md`）—— 这里不再有行数可数。
复算：`dotnet test --filter "FullyQualifiedName~VendorWiring"`，完整对账见 `docs/VENDOR_COVERAGE.md`。

原版在进度文案或请求头中点名 8 家站点风控（cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx · botdeflector · vercel）；
`Solving Incapsula` 为 **0**，是 imperva 的第三个独立证据（R1024）。
