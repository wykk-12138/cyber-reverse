"""R1367 record: the tail cannot be worked by name, and three more operations landed anyway."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'
TAIL = 'docs/ASYNC_TAIL.md'

ROUND = """
---

## 第 1367 轮：长尾**按名彻底走不通**（30 个名全查完）；顺带把无主机那组补到只剩两条

- **把 30 个店铺长尾名一次查完**（`analysis/classify_tail_names.py`）：
  **29 个只有 `<Name>d__NN` 状态机串**；唯一有独立串的 `AddAddress`（`0x1433082B7`）
  **两个地址形式都是 0 引用**。
  **结论：这一队列按名无法推进** —— 与 R1366 从三个名字得出的结论一致，但现在**有全量证据**。
- **无主机那组重新点数**：`open_items` 里写着 6 条，实际 `getCart`（R1359）与 `saveAddress`（R1366）
  **早已落地** —— **文档是陈的，已更正**。
  `createMyPayment` 按 R1364 的证据（`cybersource`/`isv_*`）**属于 Cybersource 族，不进会话族**。
  剩下三条 `createCartByStore`/`initiateCheckout`/`maintainShippingGroups` **按 R1359 的先例并入会话族**。
- **一条必须写下的告诫**：把这几份文档按**单个变量名**去匹配已知族，会得到
  `key → shop app`、`locale → tm-api` 这种"匹配" —— **那是一个 token 的重叠，正是 R1350 警告过的假阳性**。
  **没有据此推出任何主机**，脚本头写明。
- **又一次锚点事故（第 6 次）**：`saveAddress` 的注释是**三行 `<summary>`**，我按单行 `/// <summary>saveAddress,`
  去匹配 → 0 次。改成**从源码复制的整行**后通过。**这条已经 6 次了，每次都是同一个原因。**
- **产物**：三串 `mutation …` **UTF-16 各命中 1**；尺寸 61,990,400 → **61,993,984**。

### 五要素

- **改了什么**：`StoreSessionQueries.cs`（+3 文档/声明/分支）；`StoreSessionQueriesTests.cs`（+3，共 15）；
  `docs/OPEN_ITEMS.md` 更正两行；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`StoreSessionQueriesTests` → **15/15**；`operation_gap.py` → 覆盖 **58/65**（缺 7）；
  `orphan_documents.py` → 0；产物三串各命中 1；尺寸见上。
- **数字变化**：覆盖 55 → **58**；缺 10 → **7**；套件 +3；产物 +3,584 字节。
- **证据等级**：Observation —— 30 个长尾名的全量分类、`AddAddress` 零引用、三份文档的声明集、产物三串命中。
  Unknown —— 30 个店铺名与 64 个支付名的**行为**（需按地址逐条反编译）。
- **还剩什么**：7 条 GraphQL（`CreditCard`/`getShippingMethods` 无名字串、`createMyPayment`（Cybersource）、
  `getCart`/`saveAddress` 已落地不计、两方言、AO/Saucony/cartApi）+ 30 店铺名 + 64 支付名。
"""

POINTER = """
---

## 第 1367 轮

- **长尾按名彻底不通**：30 个店铺名全查 —— **29 个只有状态机串**，唯一有独立串的 `AddAddress` **零引用**。
- **OPEN_ITEMS 有两行是陈的**（`getCart` R1359 已落地、`saveAddress` R1366 已落地）→ 已更正。
- 三条 `createCartByStore`/`initiateCheckout`/`maintainShippingGroups` **按 R1359 先例并入会话族**；
  `createMyPayment` **按 R1364 属于 Cybersource，不进**。
- **告诫**：单变量名匹配会给出 `key→shop app`、`locale→tm-api` 的假阳性，**没有据此推主机**。
- 覆盖 55 → **58/65**，缺 10 → **7**；产物三串各 UTF-16 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1367 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1367 \u8f6e')

tail_text = io.open(TAIL, encoding='utf-8').read()
if 'classify_tail_names' not in tail_text:
    tail_text += """
## 按名能否追（R1367 全量核查）

`analysis/classify_tail_names.py` 把 30 个店铺长尾名一次查完：

- **29 个只有 `<Name>d__NN` 状态机串**，没有独立操作名；
- 唯一有独立串的是 `AddAddress`（`0x1433082B7`），**头地址与字符地址两种形式都是 0 引用**。

**结论：这一队列按名无法推进**，只能按地址逐条反编译（每个名的 `MoveNext` 需要从状态机元数据反推）。
"""
    io.open(TAIL, 'w', encoding='utf-8', newline='').write(tail_text)
    print('ASYNC_TAIL.md got the by-name verdict')

open_text = io.open(OPEN, encoding='utf-8').read()
if '`getCart` | 3234' in open_text:
    open_text = open_text.replace('| `getCart` | 3234 | `$key`、`$locale` | 同 上一行 |\n', '')
    open_text = open_text.replace('| `getCart` | 3234 | `$key`、`$locale` | 主机 / 路径 / 调用方三探全空 |\n', '')
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(open_text)
    print('OPEN_ITEMS stale getCart row removed')
