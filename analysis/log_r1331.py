"""R1331 record: the last document orphan is wired, and the orphan rule becomes a suite invariant."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1331 轮：最后一个文档孤儿接上了，"文档必须有生产调用者"进了套件

- **孤儿清零**：`ShopifyGraphQl.CartLinesUpdate`（346 字符）此前无人调用，而 `ShopifyFlow.EditLineAsync` 发的是
  REST `/cart/update.js`。现在：**有 cart id + line id + storefront token 时走结构化路径**
  （观测到的 `cartLinesUpdate`），**缺任一个就照旧走 REST** —— 是加路径，不是替掉能用的那条。
- **顺手补上一环**：结构化路径要 **line id**，而购物车读数本来就收到了它（`lines.nodes[].id`）却没留 ——
  现在读的时候记下第一条的 id。
- **测试逼出的第二个硬编码**：`ShopifyGraphQl.Endpoint` 拼的是 `https://…`，本地测试服务器是 http，
  请求直接打到 `https://127.0.0.1` 上 TLS 失败 —— **这条路径原本根本没法被拦**。
  加 `shopify.graphqlBase` 会话覆盖（默认不变），和 `wh.apiHost` 同一种缝。
- **做成不变量**：`GeneratedDocumentTests.EveryDocumentConstantHasAProductionCaller` ——
  扫全仓文档形常量，**引用数（含声明）为 1 就红**，并带一张**空的允许清单**：
  往里加名字必须写理由。R1329 撞到一个、R1330 撞到两个（其中一个是丢掉的运价 id），
  这个检查本来就该在第一份文档落地那轮就有。
- **当前状态**：`orphan_documents.py` → **0**；`audit_document_constants.py` → 15 常量 / 0 问题。

### 五要素

- **改了什么**：`ShopifyFlow.cs`（结构化行编辑 + line id 记录 + `shopify.graphqlBase` 缝）；
  `ShopifyGraphQlTests.cs`（+2 条）；`GeneratedDocumentTests.cs`（+1 条不变量）；新增 5 个 analysis 脚本；
  重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter ShopifyGraphQlTests` → **9/9**；
  `dotnet test --filter GeneratedDocumentTests` → **15/15**；
  `orphan_documents.py` → 0；`audit_document_constants.py` → 0 problems；
  产物 `cartLinesUpdate` 命中 **1**；尺寸 61,398,016 → **61,401,600**；内嵌 `2aeb7f88048e`。
- **数字变化**：套件 2678 → 见 METRICS 当前值（+3）；产物 +3,584 字节；**文档孤儿 1 → 0**。
- **证据等级**：Observation —— 孤儿清零、产物命中、审计通过、测试拦截点存在（此前 HTTP/TLS 打不通）。
- **还剩什么**：`AddressInput`；方言条件（blocker）；`CurrencyConversion`(10406) 与 `approveMemberPayment`(5407)
  仍无归宿（已解码待接）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1331 轮

- **文档孤儿清零**：`CartLinesUpdate` 接进 `ShopifyFlow.EditLineAsync`（有 cart id + line id + token 走 GraphQL，
  否则照旧 REST）；顺带让购物车读记下 `lines.nodes[].id`。
- **`ShopifyGraphQl.Endpoint` 硬编码 https**，本地服务器拦不到 → 加 `shopify.graphqlBase` 会话覆盖（默认不变）。
- **不变量进套件**：`EveryDocumentConstantHasAProductionCaller`（引用数为 1 就红，允许清单为空且必须写理由）。
  这类检查本应在第一份文档落地那轮就有。
- 现状：`orphan_documents.py` → 0；`audit_document_constants.py` → 15 常量 / 0 问题。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1331 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1331 \u8f6e')
