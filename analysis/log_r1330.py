"""R1330 record: a dropped rate id, a wrong error test, and an orphan scan that had to be fixed first."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1330 轮：扫孤儿常量，扫出两个真缺陷——一个被丢掉的运价 id，一个把"成功"读成"失败"的判断

- **先建工具**：`analysis/orphan_documents.py` —— **只报"文档形常量且没有任何生产调用者"**。
  上一版写了 `orphan_constants.py`，937 个常量里报出一大堆**说明性字符串**，噪音太大；
  文档形（≥60 字符、含 `mutation`/`query`/`fragment`/`{`）才是"复刻件发不出去的东西"。
- **工具自己先错了一次**：它从声明处往后 4000 字符里找第一个字面量，于是把**下一个常量**的 630 字符文档
  算到了 `ChallengeWindowUrl`/`MdFormField`/`ResolveStatusFailed` 三个短常量头上，虚报三个孤儿。
  改成**只取声明到分号之间**的字面量后，数字从 6 变 1。
- **第一个真缺陷**：`WarhammerQueries.UpdateShippingRate`（2248 字符，观测所得）**没有调用者**，
  而 `SubmitShippingAsync` 在 1030 行**把运价 id 读出来就丢掉了**。
  也就是说地址发了、**运价从没选过**，订单会停在 mutation 自己报告的 `isShippingValid=false`。
  现在补上第二跳：有 id 才发，落 `shippingRate`，并抽 `checkoutVersion`/`guestToken`；
  没 id 就**发事件说明**，不再假装运价步骤完成。
- **第二个真缺陷（新用例逼出来的）**：这条流判断失败用的是
  `res.Body.Contains("\\"errors\\"")`。**观测到的 mutation 自己就把 `errors` 当字段返回**
  （`updateShippingRate { errors order {…} }`），**空数组是成功**，所以每一次成功都会被读成失败。
  已换成结构化判断 `HasGraphQlErrors`：顶层的 `errors` 非空、或 `data.<操作>.errors` 非空才算失败，
  **解析不了的响应也不能算成功**。文件里 5 处朴素判断全部换掉。
- **顺手补测试缝**：`SubmitShippingAsync` 原来也走 `ApiHost + "/graphql"` 绝对地址，测试拦不到；
  已统一走 `ApiHostFor(c)`（R1328 加的会话覆盖，默认不变）。

### 五要素

- **改了什么**：`RetailFlows.cs`（运价跳 + `HasGraphQlErrors` + 5 处判断替换 + 发货 POST 走会话缝）；
  `WarhammerGraphQlTests.cs`（+2 条）；新增 6 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter "Warhammer|MagentoCart|Casio"` → **73/73**；
  `orphan_documents.py` → 孤儿 **6 → 1**（剩下 `ShopifyGraphQl.CartLinesUpdate`）；
  `audit_document_constants.py` → 15 常量 / 0 问题；产物 `updateShippingRate` 命中 **1**；
  尺寸 61,390,848 → **61,398,016**；内嵌 `8ec95d748c81`。
- **数字变化**：套件 2676 → 见 METRICS 当前值（+2）；产物 +7,168 字节。
- **证据等级**：Observation —— 孤儿清单（源码级）、运价 id 被丢弃的位置、`errors` 字段是文档的一部分、产物命中。
  **本轮修掉的两个缺陷都是我自己此前留下的。**
- **还剩什么**：`ShopifyGraphQl.CartLinesUpdate`（最后一个文档孤儿）；`AddressInput`；方言条件（blocker）；
  `CurrencyConversion`(10406) 无归宿；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1330 轮

- **孤儿扫描**：`analysis/orphan_documents.py` 只报"文档形且无生产调用者"。它自己先错一次（把下一个常量的字面量
  算到前一个头上，虚报 3 个），修成"只取声明到分号之间"后 **6 → 1**。
- **真缺陷一**：`UpdateShippingRate`(2248) 无人调用，而 `SubmitShippingAsync` **读出运价 id 就丢掉**——
  运价从没选过，订单停在 `isShippingValid=false`。现在补上第二跳。
- **真缺陷二**：这条流用 `Body.Contains("errors")` 判失败，可**观测到的 mutation 自己就返回 `errors` 字段**，
  空数组是成功 → **每次成功都被读成失败**。换成结构化的 `HasGraphQlErrors`（文件里 5 处全换）。
- 两个都是我自己此前留下的。剩下的文档孤儿只有 `ShopifyGraphQl.CartLinesUpdate`。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1330 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1330 \u8f6e')
