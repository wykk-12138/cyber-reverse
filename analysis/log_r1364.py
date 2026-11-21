"""R1364 record: the last two probes, the open-items map, and where the goal stands."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1364 轮：最后两份落地 + **写出一张接手地图**

- **`updateShipAddress`(140) → 哈希族**：处理器 `sub_14088C350` 带 **`x-graphql-hash`** 与另外两个 64 位值
  （`b9983aba…`、`e3a06590…`），与 R1357 同一块。文档声明 `$address`。**并入 `GraphQlHashQueries`。**
- **`updateMyPaymentWithActions`(401) → 认出供应商，但不实现**：处理器 `sub_140E55A00` 带
  **`cybersource`**、`isv_payment_data`、`isv_screenHeight`/`isv_screenWidth`/`isv_store`/`isv_customerIpAddress`、
  `creditCardWithPayerAuthentication`、`centAmount`、`currencyCode`、`customFields` 与 **`No capture context`**
  —— **Cybersource 的 ISV 字段**，同块的 `createMyPayment` 也属这一族。
  **复刻件不实现这套供应商集成**；已记进 OPEN_ITEMS。
- **`docs/OPEN_ITEMS.md`**（本轮第二个交付物）：把 11 条未结案项按「缺什么」分成四类 ——
  缺运行期抓包（6）/ 缺处理器选择条件（3）/ 缺界面上下文（2）/ 缺平台面（4），每条写明**拿到后怎么验、验完落哪个类**。
  附两个约定（文档声明集 > 发送方字段集；错拼照抄）与四个可重算的复核入口。
- **产物**：`mutation updateShipAddress` UTF-16 命中 **1**；尺寸 61,988,352 → **61,988,864**。

### 五要素

- **改了什么**：`GraphQlHashQueries.cs`（+1 文档/分支）；`GraphQlHashQueriesTests.cs`（+2，共 9）；
  新增 `docs/OPEN_ITEMS.md`；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`GraphQlHashQueriesTests` → **9/9**；`operation_gap.py` → 覆盖 **54/65**（缺 11）；
  `orphan_documents.py` → 0；产物命中 1；mutation **59 fired / 0 / 0 / GREEN**；扫描 59,313 文件 0 命中。
- **数字变化**：覆盖 53 → **54**；缺 12 → **11**；套件 +2。
- **证据等级**：Observation —— 两处理器的哈希头与 Cybersource 字段、文档 140 字符与 `$address`、产物命中。
  Unknown —— 六份无主机操作的归属、三处处理器选择条件、`AddressInput` 形状（**全部写进 OPEN_ITEMS**）。
- **还剩什么**：11 条，**全部需要外部证据**，已分类登记。
"""

POINTER = """
---

## 第 1364 轮（本轮收口）

- `updateShipAddress`(140) → **哈希族**（处理器带 `x-graphql-hash` + 两个 64 位值）。
- `updateMyPaymentWithActions`(401) → **Cybersource 供应商集成**（`cybersource`、`isv_*`、`No capture context`），
  **认出但不实现**，与同块 `createMyPayment` 一起记进未结案。
- **新增 `docs/OPEN_ITEMS.md`**：11 条未结案项按缺件分四类，每条写明验法与落点；附两个约定与四个复核入口。
- 覆盖 53 → **54/65**，缺 12 → **11**；**静态能推的到此为止**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1364 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1364 \u8f6e')
