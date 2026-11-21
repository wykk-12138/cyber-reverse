"""R1338 record: Highsnobiety becomes a store; a destructive anchor error and a live-host test are both recorded."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1338 轮：Highsnobiety 成为一家店——第一次"从端点建店"，中间捅破一次文件、被镜像纠正一次

- **方法**：R1337 读发送方拿到主机、两个操作名、变量名 → 这轮把两份文档按字节解出来（`addLineItem` **3435**、
  `addDiscountCode` **3399**，都带 CRLF，与旧表里 3847/3811 的数字不符 —— **旧表那两个长度是错的**）→ 建成 `HighsnobietyFlow` 并注册。
  店铺数 **67 → 68**，flow 类型 **37 → 38**。
- **镜像纠正了我一次**：我第一版把 `sku` 当作第四个顶层变量发出去。可**文档只声明并使用三个变量**
  （`$country`、`$action`、`$locale`），操作是 `addLineItem(country:, action:)` —— **根本没有 sku 参数**。
  也就是说 `$action` 的类型 `AddCartLineItem!` 是**输入对象**，货品在它里面。改成：调用方以 JSON 提供
  `highsnobiety.action`，步骤原样透传；缺了就说缺什么，**不猜字段名**。
- **两个我自己造成的伤口，都记下来**：
  1. **`edit` 工具把 verbatim 字符串里的 CRLF 改成了 LF**，206 个字符凭空消失 —— 是长度断言先发现的。
     修法：文档改成**显式 `\\r\\n` 转义的普通字符串**，并加 `TheDocumentKeepsItsLineEndings` 钉住 206 个 CRLF。
  2. **我又按"文件里第一个 `AddToCartAsync`"做锚点，把 `RetailFlows.cs` 从 2066 行砍到 235 行** ——
     这个文件里有几十个 flow 类，同名 override 有六个。从 `git show HEAD:` 恢复后按整块重写。
     **R1329 立的"按类查重"规矩，这轮在自己的切片脚本里没照做。**
- **一处环境性红**（与本轮改动无关，见 BLOCKERS）：`ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host("poq-app")`
  期望 `platform.poq.io` 对未归属请求回 **403**（Poq 面不看传入 URL，直接打真主机），而实测该主机现在回 **500**，
  于是流程报 `Error` 而不是 gate。**测试把第三方当前状态码写死了**，这是它的脆弱处，不是复刻件的行为退化。

### 五要素

- **改了什么**：`RetailFlows.cs`（+`HighsnobietyFlow`，两份文档逐字节）；`Modules/Registry.cs`（注册）；
  新增 `tests/HighsnobietyFlowTests.cs`（7 条）；四处钉子数字 67→68（`ArrowAndBeastTests`、`CoreTests`、
  `docs/PARITY.md`、`docs/VERDICT.md` 状态行）；新增 5 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`HighsnobietyFlowTests` → **7/7**；`ArrowAndBeastTests|CoreTests|ParityDocTests|DocsConsistencyTests|SummaryBlockTests`
  → **25/25**（数字跟上之后）；`store_catalog.py` → 68 模块 / 38 flow 类型 / 0 域名冲突；
  全量 → **3008 通过 / 1 失败 / 2 跳过**（唯一失败即 poq-app 那条环境项）；
  产物 61,448,192 → **61,480,448** 字节；内嵌 `87b9f1cc4da9`。
- **数字变化**：店铺 67 → **68**；flow 类型 37 → **38**；套件 +7。
- **证据等级**：Observation —— 两份文档的字节与 CRLF 数、三个变量名、`AddCartLineItem` 无 sku 参数、产物重发布。
  Unknown —— `AddCartLineItem` 的字段名（因此要调用方给 JSON）。
- **还剩什么**：Highsnobiety 的其余步骤（home/product/variant/shipping/payment 均未取证）；
  `/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

BLOCK = """
---

## R1338 · poq-app 监控用例的红是环境性的（第三方状态码变了）

- **用例**：`ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host("poq-app")`
- **断言**：期望该模块遇见 gate（`PoqAppFlow.IsBlocked` 把 **403** 视为 blocked）。
- **实测（本轮复现两次）**：`poq-app` 报 `Error`。
- **原因（已探查）**：该 flow **不使用传入 URL**，直接 POST `https://platform.poq.io/clients/offspring/account/guest-token`。
  当前该主机返回 **500**，不是 403，于是走传输错误分支。
  ```
  Invoke-WebRequest -Method POST https://platform.poq.io/clients/offspring/account/guest-token
  -> error: 远程服务器返回错误: (500) 内部服务器错误。
  ```
- **判定**：**测试把第三方当前状态码写死了**，红的是这条假设，不是复刻件行为。
  **不要为了让用例变绿去放宽断言** —— 那会抹掉证据。要修就先记录该主机的状态码分布，再决定断言成"非 200 即 gate"还是别的。
- `PoqAppFlow.cs` 自 R779 未改动，本轮亦未触及。
"""

POINTER = """
---

## 第 1338 轮

- **Highsnobiety 成为一家店**（67→68 / 37→38），从 R1337 的发送方证据建起：主机 `tm-api-eu.highsnobiety.com`、
  两个操作名、两份文档（`addLineItem` **3435**、`addDiscountCode` **3399**，均带 CRLF）。
  **旧文档表里 3847/3811 两个长度是错的。**
- **镜像纠正**：`addLineItem` 只声明 `$country`/`$action`/`$locale`，**没有 sku 参数** —— 货品在 `$action`
  （`AddCartLineItem` 输入对象）里。改为调用方提供 JSON、步骤透传。
- **两个自伤**：`edit` 工具把 verbatim 串里的 CRLF 吃掉 206 个（已改显式转义 + 加钉子测试）；
  按"文件里第一个 `AddToCartAsync`"切片把 `RetailFlows.cs` 砍到 235 行（从 HEAD 恢复重写）。
- **一条环境红**：`poq-app` 监控用例依赖 `platform.poq.io` 回 403，实测现在回 **500** → 见 BLOCKERS。
  **不为了让它变绿而放宽断言。**
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1338 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1338 \u8f6e')
append(BLOCKERS, BLOCK, 'R1338 \u00b7 poq-app')
