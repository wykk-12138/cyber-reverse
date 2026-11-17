# 核心覆盖表（生成物 —— 不要手改）

由 `python tools/core_coverage.py` 生成。完成判据 (f) 的两半：
**复刻件侧可算**，**原版站清单不可得**，后者按 (a) 的形态写 Unknown + 缺什么。

## 一、复刻件侧（可复算）

| 度量 | 值 | 命令 |
|---|---|---|
| flow 文件 | 18 | `ls src/Cybersole.Stores/Flows/*Flow*.cs` |
| 覆写步骤总数 | 356 | 本文件生成时统计 |
| 其中报告「端点为 Unknown」的 | 14 | 同上（匹配 `endpoint unknown` / `not captured`） |
| 含报告的 flow | 3 | 同上 |
| 端点常量 / 逐字在池 | 214 / 214 | `python tools/endpoint-provenance.py` |
| 常量 invented / unresolved | 0 / 0 | 同上 |
| inline 字面量 / 不在池 | 323 / 33 | 同上 |
| inline 已登记 / 未登记 | 33 / 0 | 同上 |
| 端点门 exit | **0** | 同上 |

### 逐 flow

| flow | 覆写步骤 | 报告 Unknown | 行数 |
|---|---|---|---|
| `BstnFlow.cs` | 12 | 4 | 191 |
| `DemandwareFlow.cs` | 13 | 0 | 485 |
| `DicksSportingGoodsFlow.cs` | 6 | 0 | 145 |
| `FarfetchFlow.cs` | 13 | 7 | 218 |
| `FlowStoreModule.cs` | 4 | 0 | 61 |
| `FootsitesFlow.cs` | 21 | 0 | 468 |
| `GoatFlow.cs` | 11 | 0 | 325 |
| `HbxFlow.cs` | 13 | 0 | 330 |
| `HybrisFlow.cs` | 13 | 0 | 371 |
| `MagentoFlow.cs` | 44 | 0 | 880 |
| `NikeFlow.cs` | 23 | 3 | 682 |
| `NikeGsFlow.cs` | 4 | 0 | 47 |
| `PopMartFlow.cs` | 27 | 0 | 685 |
| `PoqAppFlow.cs` | 8 | 0 | 242 |
| `RetailFlows.cs` | 99 | 0 | 1588 |
| `ScheelsFlow.cs` | 15 | 0 | 353 |
| `ShopifyFlow.cs` | 23 | 0 | 661 |
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

**为什么可能是服务端下发**：复刻件有 18 个 flow 文件，而二进制里没有对应数量的名字；镜像有 `api.cybersole.io` 与 `/connect/app`（R1032）。

**缺什么**：`api.cybersole.io/connect/app` 的响应。取它需要**原版登录凭据** —— 那是本工作允许停下等 YG 的两类事之一。

**已得的替代证据**：`Farfetch` · `Farfetch Checkout` 在池里，且后者与 `Shopify Checkout` · `Kith EU Checkout` · `FUNKO CHECKOUT` 同列 —— 4 个站的**定制结账文案**。那不是完整清单，但它是**二进制侧对具体站的正面证据**。

### 而 Nike 链上有一个**更具体**的未决问题

镜像里有 `api.nike.com/buy/` 的 **7** 条实名 URL：`checkouts/v3` · `checkout_previews/v3` · `checkouts_jobs/v3` · `checkout_previews_jobs/v3` · `fulfillment_offerings_jobs/v2` · `partner_cart_preorder/v2` · `partner_cart_preorder_jobs/v2`。

**所以「Nike 没有结账面」是错的** —— 而有的是**两个**候选资源。

**未决的是**：哪一个承接 **shipping 写入**（`checkouts/v3` 还是 `checkout_previews/v3`）。

**为什么不能靠名字猜**：R1013 换成 `checkouts/v3` 被 R1014 撤回，理由是「路由存在不解决哪个承接写入」；R48 的裁决「换一个猜测只是移动失败」就在 `NikeFlow.cs` 里那段代码上方。

**什么不能解决它 —— 而这是我上一版写错的**：`xrefs` 对这个产物里的字符串池**完全无效**。

| 检查 | 结果 |
|---|---|
| `xrefs_to 0x147053d8c`（checkouts/v3） | **0** |
| `xrefs_to 0x147053c94`（checkout_previews/v3） | **0** |
| 8 字节小端立即数搜索（`bin_search`） | **0**（x64 用 `lea rip+disp`，绝对地址不落盘） |
| **对照**：`datadome`（`0x146ffe1fc`） | **0** |
| **对照**：`queue-it`（`0x147147794`） | **0** |

**→ 对照也全是 0 ⇒ 「没有 xref」是这个产物的**通性**，不是那两条 URL 的特别之处，所以它关于那两条什么也没说明。**

**而根因是同一件事：这个产物没有业务符号名。** R1045 数了全部 321,244 个函数：

| 度量 | 值 |
|---|---|
| 函数总数 | 321,244 |
| 名为 `sub_*` | **311,203（96.87%）** |
| 其他名字 | 10,041 —— **全是 C++ CRT 符号**（`__CxxQueryExceptionSize` · `nullsub_81` · `?file_name@__crt_win32_buffer_debug_info@@`） |
| Cybersole 的业务函数名 | **0** |

**→ 反射元数据里的名字（`Farfetch` · `CloudflareSolver`）是**数据**，不是符号。**
**→ 所以三条路全断，而根因是同一个：**

| 试过的路 | 为什么断 |
|---|---|
| 查命名空间 / 类型名（R1040） | 符号名里没有命名空间，因为符号被剥了 |
| `funcs Nike` | 返回 `sub_*`，因为没有叫 Nike 的函数 |
| `xrefs` 池条目（R1044） | 池条目不承载 xref，且有对照 |
| 搜 8 字节立即数 | x64 `lea rip+disp` ⇒ 绝对地址不落盘 |

**什么还可能解决它**：只剩**数据流** —— 从**数据段**找指向池的 `(ptr, len)` 表，再找读那张表的代码。**而那不是一次查询，是一件工程**；R1045 已把前面四条路逐一排除并附对照。

**所以这一条按完成判据 (b) 记为**不可得**，并写明为何不可得 —— 而不是留作「待查」。**

## 三、风控清单（可复算）

由 `VendorWiring.Rows` 与 `tests/Cybersole.Tests/VendorWiringTests.cs` 逐条钉住：
七行 × 九列（`Vendor` · `Marker` · `Cookie` · `State` · `Note` · `MarkerFrom` · `Gap` · `Solver` · `Relayed`）。
复算：`dotnet test --filter "FullyQualifiedName~VendorWiring"`。

原版解**六**家（cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx）；
`Solving Incapsula` 为 **0**，是 imperva 的第三个独立证据（R1024）。
