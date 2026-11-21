"""R1366 record: saveAddress landed, and the async tail's real limits written down."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1366 轮：转向**异步名长尾**（另一条静态队列）——`saveAddress` 落地，长尾的边界写清

- **换了队列**：65 个 GraphQL 操作已到 54，剩下的都要外部证据。`REMAINING_REPLICATION_ROADMAP.md`
  「路线 A（无新凭据）」里还有一条静态队列：**店铺流程异步名长尾**。
  跑 `analysis/async_tail.py --family store` 得到 **34 个**原版有、复刻件没有的店铺异步名
  （`AddAddress`/`ClearActiveCart`/`GetCartId`/`GetCartCsrf`/`ReserveProduct`/`SaveAddress`/`SelectVariant` …）。
- **先试能不能按名追**：探 `GetCartId`/`GetCartCsrf`/`GetCartItemId` 三个 ——
  **全部只以 `<Name>d__NN` 状态机串存在**，没有独立操作名字符串。
  这与 R1353 的结论一致（跟着状态机走只会到元数据），**所以这一队列不能按名追**。
- **能做的是有证据那份**：`saveAddress`(296) 声明 `$address`/`$editAddress`/`$saveAddress`/`$setDefault`，无主机，
  而**长尾清单里正好有 `SaveAddress` 这个名字** —— 两条线索互证它是个店铺步骤而不是辅助函数。
  → 并入 `StoreSessionQueries`（origin 由调用方给）。
- **`docs/ASYNC_TAIL.md` 已按当前状态重生成**（`async_tail.py --write-doc`），把 34 个店铺名与 64 个支付名
  连同"按名匹配不等于有/没有行为"的三条限制一起留在文件里。
- **一处锚点失误**：`UpdateContactDetails` 的注释是**多行 `<summary>`**，按单行匹配报 0 次；
  改锚到单行的 `getCart` 注释后通过。**这已是本轮第 5 次锚点问题，全部记录在案。**
- **产物**：`mutation saveAddress` UTF-16 命中 **1**；尺寸 61,988,864 → **61,990,400**。

### 五要素

- **改了什么**：`StoreSessionQueries.cs`（+1 文档/声明/分支）；`StoreSessionQueriesTests.cs`（+2，共 12）；
  `docs/ASYNC_TAIL.md` 重生成；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`StoreSessionQueriesTests` → **12/12**；`operation_gap.py` → 覆盖 **55/65**（缺 10）；
  `orphan_documents.py` → 0；产物命中 1；尺寸见上。
- **数字变化**：覆盖 54 → **55**；缺 11 → **10**；套件 +2；产物 +1,536 字节。
- **证据等级**：Observation —— 34 个店铺异步名（可重算）、三个名字只有状态机串、`saveAddress` 的声明集、产物命中。
  Unknown —— 34 个店铺名与 64 个支付名各自的**行为**（按名匹配无法推断，需逐条反编译或实机）。
- **还剩什么**：10 条 GraphQL + 34 个店铺异步名 + 64 个支付异步名，**全部登记在 OPEN_ITEMS / ASYNC_TAIL**。
"""

POINTER = """
---

## 第 1366 轮

- **换队列**：GraphQL 操作 54→55 之后，转向 `REMAINING_REPLICATION_ROADMAP.md` 路线 A 的另一条静态队列 ——
  **店铺异步名长尾**（`analysis/async_tail.py --family store` → **34 个**）。
- **按名追不通**：`GetCartId`/`GetCartCsrf`/`GetCartItemId` **只以 `<Name>d__NN` 状态机串存在**（同 R1353 结论）。
- `saveAddress`(296) 落地到 `StoreSessionQueries` —— **长尾里的 `SaveAddress` 名字与文档互证**它是店铺步骤。
- `docs/ASYNC_TAIL.md` 已重生成（34 店铺名 + 64 支付名 + 三条限制）。
- 覆盖 54 → **55/65**，缺 11 → **10**；产物 `mutation saveAddress` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1366 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1366 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if '异步名长尾' not in text:
    text = text.replace(
        '| `saveAddress` | 296 | `$address`、`$editAddress`、`$saveAddress`、`$setDefault` | 同上 |\n', '')
    text += """
---

## 七、异步名长尾（R1366 新增）

`python analysis/async_tail.py --family store` → **34 个**原版有、复刻件没有的店铺异步名；
`--family payment` → **64 个**。完整名单与三条限制见 `docs/ASYNC_TAIL.md`。

**已证**：这些名字**只以 `<Name>d__NN` 状态机串存在**，没有独立操作名可跟（`GetCartId`/`GetCartCsrf`/`GetCartItemId`
三个都试过）。**所以这一队列要按地址逐条反编译，不能按名。**

**已落地其一**：`saveAddress`(296) → `StoreSessionQueries`（长尾里的 `SaveAddress` 名字与文档互证）。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated with the async-tail section')
