"""R1342 record: the Shop app surface, a 26 KB document, and an IDA restart."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1342 轮：全清单里最大那份（`ProductDetails`，26206 字符）落地——它属于 **Shop app**，不是任何一家店

- **取最大的一份**：`0x14712CE54`（26206）→ 单引用点 `0x140D26DDB` → `sub_140D26A20`（1266 字节）。发送方交出：
  ```
  https://server.shop.app/graphql   31 字符，0x147080990
  operationName ProductDetails      0x146E4BF60
  productId / productInput / brokerId / imageWidth / sampleReviews / sortReviewsBy
  userHasEntryPointsV2 / variantsLimit
  RECOMMENDED                       0x146E59A08
  ```
  **这不是某家店的流程，是 Shopify Shop app 的 API。** `where_is.py "shop.app"` 在复刻件里**零命中** —— 一条全新表面。
- **落码**：新增 `Flows/ShopAppProduct.cs`（Url / OperationName / SortRecommended / Document 26206 / 八变量名 /
  Envelope / FetchAsync）。变量由调用方给 —— 镜像没说这些 id 从哪来。
- **顺带答了一个机械问题**：**26 KB 的字符串常量能不能过源码 → 编译器 → AOT**。能 ——
  产物里 `query ProductDetails` **UTF-16 命中 1**，`userHasEntryPointsV2` 命中 2，尺寸 +86,016 字节。
  （`server.shop.app/graphql` 那个 URL 两编码都没命中 —— 按 §4.5 **无结论**，存储是混合的。）
- **两次自伤，都记下来**：
  1. 断言文档以 `"}\\n"` 结尾 —— **实测尾部是 `}\\r\\n` 加 24 个空格**。又是"先假设形状再看不符"的老毛病；
     改成用**测量出来的尾部**写断言。
  2. `GatewayHttp` 缺 using（`Cybersole.Stores.Payments`），编译一次就报。

### 环境：IDA 又掉了，本轮自愈

- 开工时 `ida.py health` **连接被拒**，`list_windows` 显示 **ida 进程根本不在**（不是端口漂移）。
- 重启 `D:\\projects\\IDA-pro\\ida.exe`（**注意：不是 `ida64.exe`**，本机叫 `ida.exe`），依次点掉三个模态框：
  **Proceed with unpacked base** → **Yes（修复 .id0）** → **OK（inconsistencies）**，`health` 恢复 `status: ok`。
- 步骤已并入 BLOCKERS 的既有条目。

### 五要素

- **改了什么**：新增 `Flows/ShopAppProduct.cs`、`tests/ShopAppProductTests.cs`（6 条）；
  新增 4 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`ShopAppProductTests` → **6/6**；`operation_gap.py` → 覆盖 **20/65**（缺 45）；
  `orphan_documents.py` → 0；`audit_document_constants.py` → **23 常量 / 0 问题**；
  产物 `query ProductDetails` UTF-16 命中 1；尺寸 61,544,960 → **61,630,976**。
- **数字变化**：覆盖 19 → **20**；缺 46 → **45**；套件 +6；产物 +86,016 字节。
- **证据等级**：Observation —— 主机/操作名/八变量/枚举/26206 字符文档、产物命中、IDA 重启步骤。
- **还剩什么**：45 个未覆盖操作（下一份 `PayWithQuery` 12561）；两份 `approveMemberPayment` 方言；
  `/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1342 轮

- **全清单最大的 `ProductDetails`(26206) 落地** —— 它属于 **`https://server.shop.app/graphql`（Shopify Shop app）**，
  复刻件此前**零命中**，是全新表面。新增 `ShopAppProduct`（Document 26206 / 八变量 / FetchAsync）。
- **26 KB 常量能过源码 → 编译器 → AOT**：产物 `query ProductDetails` UTF-16 命中 1，尺寸 +86,016 字节。
- **覆盖 19 → 20/65，缺 45**。
- **IDA 又掉了一次并自愈**：进程不在 → 重启 **`ida.exe`**（不是 ida64）→ 三个模态框
  （Proceed with unpacked base / Yes 修 .id0 / OK inconsistencies）→ health ok。
- 又一次"先假设形状"：断言文档尾是 `"}\\n"`，实测是 `}\\r\\n` + 24 空格。改成用测量值。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1342 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1342 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'ShopAppProduct' not in text:
    text = text.replace(
        "`ProductDetails`(26206)、",
        "**`ProductDetails`(26206) 已落地（R1342）：属于 `https://server.shop.app/graphql`，见 `ShopAppProduct`**、")
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')

blockers = io.open(BLOCKERS, encoding='utf-8').read()
if 'ida.exe' not in blockers:
    blockers += """
---

## R1342 · IDA 进程整个不在时怎么起（补充既有条目）

- **症状**：`analysis/ida.py health` 连不上，且 `list_windows(app="ida")` 返回 **0 个窗口** ——
  **不是端口漂移，是进程根本没了**。
- **可执行文件名**：本机是 **`D:\\projects\\IDA-pro\\ida.exe`**（`ida64.exe` 不存在，直接 Start-Process 会报找不到文件）。
- **启动**：`Start-Process D:\\projects\\IDA-pro\\ida.exe -ArgumentList "<db>.i64"`，
  然后依次点掉三个模态框：**Proceed with unpacked base** → **Yes（修复 .id0）** → **OK（inconsistencies）**。
- **判定**：`analysis/ida.py health` 返回 `status: ok` 且 `hexrays_ready: true`。
"""
    io.open(BLOCKERS, 'w', encoding='utf-8', newline='').write(blockers)
    print('BLOCKERS updated with the launch detail')
