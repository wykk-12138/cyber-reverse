"""R1343 record: the checkout pair, and the trimming the artifact proved by not changing size."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1343 轮：清单第二位（`PayWithQuery` 12561）落地——**并且抓到"类被裁掉"这件事**

- **取 12561 那份**：`0x14712190C` → 两个引用点，最重要的 `0x14110D030`（1512 字节）**一个函数发两份文档**：
  ```
  https://www.paypal.com/graphql/   （与审批/换汇同一个基址）
  operationName PayWithQuery   文档 12561 @0x14712190C  变量 token / withSplitTender / expeirences
  operationName ShipToQuery    文档  2031 @0x147139B2C  变量 token
  ```
  **`expeirences` 又是镜像的错拼**（文档里是 `$experiences`），照抄并钉测试。
- **另一个发送方 `0x140F4C550`（2099 字节）走的是浏览器侧结账面**：`x-app-name: checkoutuinodeweb_hermione`、
  `x-paypal-internal-euat`、`paypal-client-metadata-id` + 一整套 `sec-fetch-*`。
  **同一个 query，两条传输路径；哪条由什么条件决定没有证据 —— 本轮只实现"另外四个操作都在用"的合作方路径。**
- **本轮最重要的发现（不是这个类，是它的缺席）**：
  加完 `PayPalCheckoutQueries`（20650 字节源码、两份文档）后**产物尺寸一字未动**（61,630,976 → 61,630,976），
  两份文档**两种编码都搜不到** —— **整个类被 AOT 裁掉了**。
  原因：文档常量确实被 `PayWithAsync`/`ShipToAsync` 引用（**R1331 的不变量在源码层面是绿的**），
  但**这两个方法本身没有任何调用者**，于是整类不可达。
  **§4.5 说"搜不到不证明被裁"，但"加了 20 KB 源码尺寸完全不变"这件事本身说明问题。**
- **修法**：在 `PayPalGateway.AuthorizeAsync` 的合作方分支里加一段（`paypal.checkout` 触发），
  先查 PayWith、再查 ShipTo、再走审批。**重发后**：`query PayWithQuery` **1**、`query ShipToQuery` **1**、
  `withSplitTender` **2**，尺寸 **+41,984 字节**。
  **同一份源码，唯一差别是有没有调用者 —— 这就是 §4.5 的正向对照。**
- **结论（写进方法论）**：**可达性规则必须覆盖到"API 表面"，不只是"常量"。**
  "文档有调用者"不等于"调用它的方法有调用者"。

### 五要素

- **改了什么**：新增 `Payments/PayPalCheckoutQueries.cs`、`tests/PayPalCheckoutQueriesTests.cs`（6 条）；
  `Gateways.cs`（结账对前置分支）；新增 4 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`PayPalCheckoutQueriesTests` → **6/6**；`PayPal|Gateway` 全量 → **130/130**；
  `operation_gap.py` → 覆盖 **22/65**（缺 43）；`orphan_documents.py` → 0；`audit_document_constants.py` → **25 常量 / 0 问题**；
  产物三串 UTF-16 命中 1/1/2；尺寸 61,630,976 → **61,672,960**。
- **数字变化**：覆盖 20 → **22**；缺 45 → **43**；套件 +6；产物 +41,984 字节（**接上调用者之后**）。
- **证据等级**：Observation —— 主机/两个操作名/变量/两份文档长度、产物差分的两次测量（无调用者 vs 有调用者）。
- **还剩什么**：43 个未覆盖操作；`approveMemberPayment` 两份方言；浏览器侧结账面那条传输路径；
  `/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1343 轮

- **`PayWithQuery`(12561) + `ShipToQuery`(2031) 一起落地**（同一个发送方 `0x14110D030` 发两份）。
  `expeirences` 错拼照抄。另有浏览器侧结账面（`checkoutuinodeweb_hermione` 等）**未实现**，无选用证据。
- **抓到"整类被裁"**：加完类后**产物尺寸一字未动、两份文档两编码都搜不到** → 文档有调用者，但**方法没有调用者**。
  接到 `PayPalGateway.AuthorizeAsync` 后：三串命中 1/1/2，尺寸 **+41,984**。**同一份源码的正向对照。**
- **方法论更新**：**可达性规则要覆盖"API 表面"，不只是"常量"。**
- 覆盖 20 → **22/65**，缺 45 → **43**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1343 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1343 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'PayPalCheckoutQueries' not in text:
    text = text.replace(
        "`PayWithQuery`(12561)、",
        "**`PayWithQuery`(12561) 与 `ShipToQuery`(2031) 已落地（R1343）：`PayPalCheckoutQueries`**、")
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
