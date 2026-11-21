"""R1327 record: the paste-damage audit becomes a repository-wide invariant."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1327 轮：把"粘贴损坏"做成全仓不变量——审计先自己错了两次，才收敛

- **上轮的教训要变成机制**，不是又一条注意事项。于是写 `analysis/audit_document_constants.py`：
  扫 `replica/src` 里**所有文档形常量**（≥200 字符且含 `mutation`/`query`/`fragment`/`{`），查四类信号：
  截断标记、裸省略号、花括号不平衡、引号数为奇、结尾不是 `}`。
- **审计自己先报了 8 个警报，7 个是假阳性**，两次修正都记在脚本头：
  1. 把 `...` 一律当截断标记 —— 但 GraphQL 里 `...Frag`、`... on ProductVariant` 是**片段展开**，到处都是；
  2. 第一次修正后还剩 3 个，因为 `... on X` 中间有空格，被当成裸省略号 —— 规则要允许 `...` 后跟 `on`。
  **收敛后的规则**：裸省略号 = `...` 后面不跟标识符、`on` 或 `{`。
- **唯一一个"结构性不平衡"是真的但也是对的**：`ShopifyGraphQl.CartSelection` 花括号 12/13、引号 1 个奇数 ——
  因为它是**池子里存的片段**，开头就是被剥掉的 operation header 的尾巴（`"){id,checkoutUrl…`）。
  文档注释里早就写了这件事。所以规则加一条豁免：**以 `)`/`,`/`"` 开头的常量为声明式片段**，不平衡是预期。
- **最终结果**：14 个文档形常量，**0 个有问题**；其中 1 个是声明式片段。
- **做成不变量**：新增 `GeneratedDocumentTests` —— 全仓扫描 + 12 条 MemberData 用例 + **一条"扫描确实找到了东西"的用例**
  （扫描静默返回空会让下面所有断言空转，所以人口数先断言 ≥10）。
  上轮那条只覆盖 `WarhammerQueries` 一个类的反射守卫保留，两层都在。
- **本轮未改 `replica/src`** —— 产出是测试与分析工具，故不重发布；产物与 METRICS 的产物数字不变。

### 五要素

- **改了什么**：新增 `analysis/audit_document_constants.py`、`analysis/add_document_guard_test.py`、
  `replica/tests/Cybersole.Tests/GeneratedDocumentTests.cs`（13 条）；`replica/docs/VERDICT.md` 与 `docs/HANDOFF.md` 记录。
- **验证命令与输出**：`python analysis/audit_document_constants.py` → `document-shaped constants: 14`、
  `declared fragments: 1`、`constants with a problem: 0 of 14`；
  `dotnet test --filter GeneratedDocumentTests` → **13/13**。
- **数字变化**：套件 2657 → 见 METRICS 当前值（+13）；产物不变。
- **证据等级**：Observation —— 14 个常量的扫描结果、两次规则修正前后的假阳性数（8 → 3 → 0）、
  `CartSelection` 的片段性质。**本轮无行为变化**，故无 Inference 级新增结论。
- **还剩什么**：方言条件（blocker，需抓包）；`OnboardGuestMutation`(3104)、`CurrencyConversion`(10406) 待落；
  AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1327 轮

- 上轮的粘贴教训**变成机制**：`analysis/audit_document_constants.py` 查四类信号（截断标记/裸省略号/花括号/引号/结尾）。
- **审计自己错了两次**：先把 `...` 一律当截断（GraphQL 片段展开到处都是），修完又漏了 `... on X` 的空格。
  最终规则：裸省略号 = `...` 后不跟标识符、`on` 或 `{`。**14 个常量，0 个有问题。**
- `ShopifyGraphQl.CartSelection` 的不平衡是**对的**：它是池子里的片段，开头就是被剥掉的 header 尾巴。
  规则因此给"以 `)`/`,`/`"` 开头"的常量豁免。
- **全仓不变量**：`GeneratedDocumentTests`（13 条，含一条"扫描确实找到东西"的人口断言）。未改 `replica/src`。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1327 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1327 \u8f6e')
