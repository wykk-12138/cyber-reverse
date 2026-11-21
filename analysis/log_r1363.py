"""R1363 record: the contact-details member, and the twin of the same operation that sends by hash."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1363 轮：`UpdateContactDetails` 归入会话族 —— 而它有**一个用哈希发同一操作的孪生处理器**

- **两个处理器**：
  - `sub_140891BB0`：**`https://` + 主机 + `/graphql`**，变量 `email`/`emailOptIn`/`phone`
    → 与 `StoreSessionQueries` 同形（origin 由调用方给，需要 `/graphql` 后缀时由调用方带上）；
  - `sub_14088C0C0`：**0x14088 那一块**（Sentry trace `00-d914eae0…-01` + 两个 64 位哈希 + `Submitting Email`）
    → **按哈希投递同一操作**。
- **只实现前者**：两个处理器**哪个由什么条件选中，没有证据** —— 与 `approveMemberPayment` 两方言是同一个未答问题。
  **把它写进类的注释，而不是挑一个看起来更像的。**
- **产物**：`mutation UpdateContactDetails` UTF-16 命中 **1**；尺寸 61,987,328 → **61,988,352**。

### 五要素

- **改了什么**：`StoreSessionQueries.cs`（+1 文档/声明/分支）；
  `StoreSessionQueriesTests.cs`（+2 条，共 10）；新增 2 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`StoreSessionQueriesTests` → **10/10**；`operation_gap.py` → 覆盖 **53/65**（缺 12）；
  `orphan_documents.py` → 0；产物命中 1；尺寸见上。
- **数字变化**：覆盖 52 → **53**；缺 13 → **12**；套件 +2；产物 +1,024 字节。
- **证据等级**：Observation —— 两处理器的路径/哈希头与变量集、文档 244 字符与三个变量、产物命中。
  Unknown —— 两个处理器之间的选择条件（未成立）。
- **还剩什么**：12 个 —— `SignInAsGuest`(453)/`updateShipAddress`(140)/`updateMyPaymentWithActions`(401)；
  `CreditCard`(2867)/`getShippingMethods`(531)（无操作名串）；五份无主机；两方言；浏览器侧结账面；
  `/cartApi/checkout` 归属；`AddressInput`；AO 三个体；Saucony 六步。
"""

POINTER = """
---

## 第 1363 轮

- `UpdateContactDetails`(244) → `StoreSessionQueries`（处理器 `https://`+host+`/graphql`，变量 email/emailOptIn/phone）。
  **它还有一个 0x14088 块的孪生处理器，用哈希发同一操作** —— 两者选择条件无证据，**只实现前者并写明**。
- 覆盖 52 → **53/65**，缺 13 → **12**；产物 `mutation UpdateContactDetails` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1363 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1363 \u8f6e')
