"""R1370 record: the dialect question is answered by one name in the declared sets."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1370 轮：两方言的**选择条件找到了** —— 差在一个变量名，`paycodeEncrypted`

- **做法**：不再问"哪个处理器在什么条件下被调"，而是**把两份文档的声明集并排比**：
  ```
  short(5407) 15 个：…selectedInstallmentOption, setStickyFiRequired, shareAddressWithDonatee, token
  long (5620) 16 个：同上 + paycodeEncrypted
  ```
  **除这一个名字外完全相同。**
- **结论**：方言跟着**支付方式**走，不跟店铺走 —— **带加密 paycode 的出资选项需要长文档，其余用短文档**。
  这是调用方**自己能从载荷里看出来**的条件；镜像里没有任何"店铺名单"，编一个是猜。
- **落码**：`PayPalPartnerApprove` 增 `PaycodeDocument`（5620）+ `PaycodeVariableName` + `DocumentFor(bool)` +
  `EnvelopeFor(variables)`；**原有 `Document` 常量不动**，所以既有调用点行为不变。
- **一处自己的失误**：第一版测试用**字符串手术**去"减掉"那个变量再比较两份文档 ——
  结果 `Expected: ···String, ) {` vs `Actual: ···String) {`，**中间多一个逗号**。
  改成**比较声明集**（`HashSet` 差集断言 `{paycodeEncrypted}`，15 vs 16）—— **断言要对着"我到底声称什么"写**。
- **产物**：`paycodeEncrypted` 检出（待本轮构建结果确认编码）；尺寸见下。

### 五要素

- **改了什么**：`PayPalPartnerApprove.cs`（+长文档 + 选择器 + `EnvelopeFor`）；
  `PayPalPartnerApproveTests.cs`（+3，共 9）；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`PayPalPartnerApproveTests` → **9/9**；`PayPal|StoreFlow` → **105/105**；
  `operation_gap.py` → 覆盖 **60/65**（缺 5，本条属"选择条件"而非新操作）；`orphan_documents.py` → 0。
- **数字变化**：套件 +3；长文档落地；**这一条从未结案清单里划掉**。
- **证据等级**：Observation —— 两份文档的声明集差集恰为 `{paycodeEncrypted}`（15 vs 16）。
- **还剩什么**：5 条 —— `createMyPayment`(493)（Cybersource）、`AddressInput`、AO 三个体、Saucony 六步、
  `/cartApi/checkout`、浏览器侧结账面。
"""

POINTER = """
---

## 第 1370 轮

- **两方言选择条件已解**：两份 `approveMemberPayment` 文档**声明集只差 `paycodeEncrypted`**（15 vs 16），
  其余完全相同 → **方言跟支付方式走**（带加密 paycode 用长文档），跟店铺无关。
- 落码 `PayPalPartnerApprove.PaycodeDocument` + `DocumentFor(bool)` + `EnvelopeFor(variables)`；**旧 `Document` 不动**。
- 一次自伤：第一版测试用字符串手术比较文档，被一个逗号打败 → 改成**声明集差集**断言。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1370 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1370 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if 'paycodeEncrypted' not in text:
    text += """
---

## 十、两方言已解（R1370）

`approveMemberPayment` 的 5407 与 5620 两份文档，**声明集只差 `paycodeEncrypted`**（15 vs 16），其余完全相同。

**条件**：带加密 paycode 的出资选项用长文档，其余用短文档 —— **跟支付方式走，不跟店铺走**。
实现：`PayPalPartnerApprove.DocumentFor(bool)` / `EnvelopeFor(variables)`；旧 `Document` 保持不变。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated: the dialect question is closed')
