"""Append the R1282 ledger to the docs (UTF-8, LF)."""

import io

BLOCKERS = """
## R1282 —— 台账与孤岛一次性收尾（合并 4 项，不拆轮）

### 一、删掉的类（全部经调用者实测，不是凭印象）

| 类 | 处置 | 依据 |
|---|---|---|
| `Stores/Scripts/VendorWiring.cs` | 删 | 台账：7 个测试文件读它，行数据早已在 `docs/VENDOR_WIRING.md` |
| `Payments/VendorPaymentEndpoints.cs` | 删 | **src 内真实调用者 0**（R1269 换皮常量表） |
| `Flows/AccountRoutes.cs` | 删 | 真实调用者 0（R1257 常量表） |
| `Flows/HbxApi.cs` | 删 | 真实调用者 0（R1258 常量表） |
| `Flows/CheckoutRoutes.cs` | 删 | 真实调用者 0——`MagentoFlow:221-224` 三处**全是注释**，逐行看过 |
| `WaitwhileQueue.cs` | 删 | 真实调用者 0 |

同时删掉只为它们存在的 6 个测试文件（`VendorWiringTests` / `VendorPaymentEndpointTests` /
`AccountRoutesTests` / `HbxApiTests` / `CheckoutRoutesTests` / `WaitwhileQueueTests`）。

### 二、解耦的 7 处引用（断言台账/源码散文的一律删，断行为的一律留）

`WallDispatchTests`（2 条台账断言）· `WallSolvingTests`（2 条）· `VendorNegativeClaimsTests`（读
`VendorWiringTests.cs` 源文件的 2 处）· `CaptchaDeliveryAttributionTests`（读 `VendorWiring.cs` 源文件）·
`AntiBotProtocolTests` / `PerimeterXMarkerTests` 的散文与 `<see>` · `CasioEndpointTests` 的
`TheCheckoutRoutesAreWhereTheFlowThinksTheyAre`（随 `CheckoutRoutes` 归档）。

### 三、顺带补上一个**真缺口**（不是掩盖）

删 `VendorWiring` 让 `Cybersole.Models.State` 变成 ABSENT 未分类（此前被 `VendorWiring` 的嵌套 `State` 偶然满足）。
本轮按镜像实现它，**并接入真实运行时路径**：

镜像证据 `0x143211f9d` 的 descriptor 串逐字给出模型形状：
`Cybersole.Models.State` 只有 `Name`；`Country` 有 `Name`/`Code`/`States`；`Address` 有
`FirstName`/`LastName`/`Address1`/`Address2`/`City`/`ZipCode`/`Country`/`State`/`Barangay`。

`src/Cybersole.Core/Models/AddressModels.cs` 落地三个记录；
`DemandwareFlow.SubmitShippingAsync` 把 `c.Shipping` 投影成 `Address`，
`states_stateCode` 从 `address.State?.Name` 取——**有真实调用点，不是孤岛**。

### 四、工作区与基线

- 清掉 `.tmp-*.log` **272 个**（根 18 + `replica/` 254）；`.gitignore` 加规则，日志从今写 `%TEMP%`。
- IDA 三个模态框（未打包库 / `.id0` 修复 / 库不一致）已用 CUA 点掉，`ida.py health` = `ok`、
  `hexrays_ready: true`。
- `metrics_report.py`（**不带** `--skip-tests`）：完整套件 **2446 通过 / 0 失败 / 0 跳过**。
- `mutation-check.py`：**59/59 fired**、decorative 0、skipped 0、`restored tree: GREEN`。

### 五、一个必须写清的**非零退出**

`metrics_report.py` 整体 exit 1：来自 `store` / `vendor` 两个**核心覆盖检查**（exit 1 / exit 2），
不是套件失败。原因是删掉若干零调用常量类后，那些"端点已登记"的计数下降。
**下一轮用真实 Flow 端点补回来**，不靠重新引入常量表凑数。

证据等级：Observation = 调用者计数、descriptor 串、2446/0、59/59、272 个日志；
Inference = 「覆盖检查非零源于删表」；Unknown = 每个站点的真实端点还差几条（下一轮逐站核）。
"""

VERDICT = """
---

## 第 1282 轮：台账 + 5 孤岛一次性收尾，并补上 `Cybersole.Models.State` 真缺口

**删除**：`VendorWiring`（台账）+ 4 个零调用常量类（`VendorPaymentEndpoints`/`AccountRoutes`/`HbxApi`/`WaitwhileQueue`）
+ `CheckoutRoutes`（`MagentoFlow` 三处引用**全是注释**）+ 6 个只为它们存在的测试文件。

**解耦**：7 处引用（删台账/散文断言，留行为断言）。

**补真缺口**：按 `0x143211f9d` 的 descriptor 实现 `State`/`Country`/`Address`，
并在 `DemandwareFlow.SubmitShippingAsync` 真实使用。

**卫生**：清 272 个 `.tmp-*.log`、`.gitignore` 加规则、日志改写 `%TEMP%`。

**基线**：套件 2446/0/0/2446；mutation 59/59 fired、GREEN。
`metrics` 整体 exit 1 来自 store/vendor 覆盖检查（删表的真实代价），下一轮用真实端点补。
"""

HANDOFF = """
## R1282 —— 一次性收尾：删 6 类 + 6 测试文件、解耦 7 处、实现 State/Country/Address 并接入 Demandware

Observation：
- 真实调用者计数：5 个孤岛均为 0（`CheckoutRoutes` 的 3 处是注释）。
- `0x143211f9d` descriptor：`State{Name}` / `Country{Name,Code,States}` / `Address{...State,Country,Barangay}`。
- 套件 2446/0/0/2446；mutation 59/59 fired、GREEN；272 个日志已清。
- IDA `health=ok`、`hexrays_ready=true`（三个模态框已点掉）。

下一轮（既定）：把 `StripeChallenge.ConfirmAsync` 接进 `StripeGateway`/`StoreFlow` 主链，补端到端行为测试。
之后按 ① BstnFlow 4 个 `endpoint unknown` → ② Captcha 协议 → ③ `Cybersole.Http`。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', BLOCKERS),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', VERDICT),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', HANDOFF)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('appended', path)
