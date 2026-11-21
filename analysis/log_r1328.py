"""R1328 record: the onboarding hop lands in the flow that already sends its sibling."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1328 轮：`OnboardGuestMutation` 有了归宿——接在已经在发它兄弟的那条流上

- **先找家再落码**（上轮定的规矩）：`OnboardGuestMutation` 的变量是
  `billingAddress`/`shippingAddress`/`card`/`country`/`email`/`firstName`/`lastName`/`phone`/`token`，
  **正好就是 Warhammer 那条流已经收集的东西**；而它的兄弟 `ApproveOnboardPaymentMutation`
  就是那条流在 `SubmitPaymentAsync` 里发的。两者的 URL 在镜像里**相邻**（`0x147097fe4` / `0x147098064` 一带）。
  **所以不造新家，接在现成调用点上。**
- **落码**：`WarhammerQueries.OnboardGuestMutation`（**3104 字符，脚本从字节生成**）+ `SubmitPaymentAsync`
  在审批**之前**先跑安户跳。
- **一处不肯编**：`AddressInput` 的字段形状**镜像里没有**（这条流自己也不构造地址对象——它把地址内联在
  各自步骤里）。所以只有会话里带了 `wh.onboard.billing` / `wh.onboard.shipping` 时才发这一跳；
  否则**发一条 StatusInfo 说明"跳过了、因为缺这两个键"**，然后照旧走审批。
  拿 Magento 的字段名去猜另一个 API 的形状，会让店铺收到一份它拒绝的文档——比不发更坏。
- **顺序是 Inference**，写明了：安户产出审批回复里指代的那个 buyer，但镜像没有字面量展示先后。变量对齐是选这个顺序的理由。
- **顺手补一条测试缝**：`PostJsonAsync` 拿的是 `ApiHost + "/graphql"` 绝对地址，测试拦不到。
  按本文件已有风格加 `wh.apiHost` 会话覆盖（**默认不变**），两处 POST 都走它。
- **审计确认**：`audit_document_constants.py` → 15 个文档形常量、**0 个有问题**；产物 `onboardGuest` 命中 1。

### 五要素

- **改了什么**：`WarhammerQueries.g.cs`（+3104 字符文档）；`RetailFlows.cs`（安户跳 + `ApiHostFor` 会话缝）；
  `WarhammerGraphQlTests.cs`（+3 条、补两个 using、两处指向测试服务器）；新增 4 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter Warhammer` → **18/18**；
  `audit_document_constants.py` → 15 / 0 problems；产物 `onboardGuest` **1**；
  尺寸 61,370,368 → **61,383,680**；内嵌 `a67bc3f33004`。
- **数字变化**：套件 2670 → 见 METRICS 当前值（+3）；产物 +13,312 字节。
- **证据等级**：Observation —— 3104 字符文档、变量清单与流程已有数据的对齐、URL 相邻、产物命中。
  Inference —— 安户在审批之前。
  Unknown —— `AddressInput` 的字段形状（需抓包）。
- **还剩什么**：`AddressInput` 形状（拿到就能让安户跳真正跑起来）；方言条件（blocker）；
  `CurrencyConversion`(10406) 无归宿；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1328 轮

- `OnboardGuestMutation`(3104) **接在 Warhammer 流**：它的变量正是那条流已收集的地址+资料+token，
  兄弟 `ApproveOnboardPaymentMutation` 就在同一步里发，URL 在镜像里相邻。**不造新家。**
- **不发猜的形状**：`AddressInput` 字段形状镜像里没有 → 只有会话带 `wh.onboard.billing/shipping` 才发安户跳，
  否则**发 StatusInfo 说明跳过原因**再照旧审批。顺序（安户→审批）标为 Inference。
- 加了 `wh.apiHost` 会话覆盖（默认不变），让这条流可被测试拦截 —— 原先是绝对地址，测试够不着。
- 审计 15 个常量 0 问题；产物 `onboardGuest` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1328 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1328 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'R1328' not in text:
    text = text.replace(
        '| `0x1470D611C` | 3104 | `OnboardGuestMutation` | 已解码，`analysis/.paypal_onboard.json`；没有已证实的步骤接它 |',
        '| `0x1470D611C` | 3104 | `OnboardGuestMutation` | **R1328 已落地**：`WarhammerQueries.OnboardGuestMutation`，接在审批之前 |')
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
