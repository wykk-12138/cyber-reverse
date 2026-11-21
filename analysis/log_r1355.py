"""R1355 record: the operation name led to the handler, and the handler carries the vocabulary."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1355 轮：文档函数没有字面量时，**跟着"操作名"走**——结果拿到一整段行为

- **两块先探**：`GetCart`/`GetCartCookie`/`GetProductInventory` 与 `CartLineItemSet`/`CreditCard` 的发送方
  **五个函数全部零字面量**（都是异步状态机）。主机/路径扫描在这条路上到此为止。
- **换一条路：跟着操作名字符串走**。`cartLineItemSet` 的字符串在 `0x146FC1A38`，
  **头地址（-12）形式有一个引用点** `0x140D1189E` → `sub_140D11730`（1049 字节）。
  这个函数**不是**状态机，而是**处理 Shop app 加购结果的分支**，它带着整整一套词：
  ```
  Password page up
  The product in the cart does not exist.
  The product in the cart is out of stock.
  The shopify shop of this cart is not eligible
  cannot be fulfilled
  tries exhausted on cart
  ```
  **这就是"只抄文档会丢掉的那一半"**：请求发出去了，**反应呢**。
- **落码**：`ShopAppCart`（Document 1255 / 四个变量 / `AddLineAsync`），
  **六条消息作为常量**并按回复内容映射成相应失败 —— **用镜像自己的话**，不是新编的文案。
  接进 `ShopifyFlow.AddToCartAsync`（`shopapp.brokerId` + `variantId` 齐全才走）。
- **IDA 又一次倒下并自愈**（本轮耗时大半在这里）：进程不在 → 重启 → 三个模态框
  （**加载现有** / **Proceed with unpacked base** / **Repair**）→ `health status: ok`。
  **注意第二个框不能选 "Restore packed base"**（那会丢掉分析），第三个只能选 Repair。
- **产物**：`mutation CartLineItemSet` UTF-16 命中 **1**；尺寸 62,074,688 → **62,088,000**。
  （`Password page up` 两编码皆 0 —— 常量被内联进比较，字面量不独立存在，按 §4.5 无结论。）

### 五要素

- **改了什么**：新增 `Flows/ShopAppCart.cs`、`tests/ShopAppCartTests.cs`（6 条）；
  `ShopifyFlow.cs`（shop-app cart 分支）；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`ShopAppCartTests|ShopifyGraphQlTests` → **18/18**；`operation_gap.py` → 覆盖 **39/65**（缺 26）；
  `orphan_documents.py` → 0；产物命中 1；尺寸见上。
- **数字变化**：覆盖 38 → **39**；缺 27 → **26**；套件 +6；产物 +13,312 字节。
- **证据等级**：Observation —— 五个零字面量函数、操作名头地址的一个引用点、六条消息的原文、文档 1255 字符与四变量、产物命中。
- **还剩什么**：`CreditCard`(2867)/`GetCart`(3520)/`GetCartCookie`(74)/`GetProductInventory`(490)；
  `SignInAsGuest` 等五份；`addToCartByChannel`(2271)；`updateShipAddress`(140)/`updateMyPaymentWithActions`(401)；
  Unknown 六份（已登记）；B 块其余；`approveMemberPayment` 两方言；浏览器侧结账面；`/cartApi/checkout` 归属；
  `AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1355 轮

- **新手法：跟着"操作名字符串"走**。文档函数零字面量（异步状态机）时，操作名自己的引用点往往是**真正的处理器**。
  `cartLineItemSet` → `sub_140D11730`（1049 字节）→ 六条处理消息（`Password page up`、`The product in the cart is out of stock.` …）。
- **落码** `ShopAppCart`：文档 1255 + 四个变量 + **六条消息 + 按回复映射**（用镜像自己的话）。
  **只抄文档会丢掉"反应"这一半。**
- **IDA 重启手册补充**：三个模态框依次为 **加载现有** → **Proceed with unpacked base** → **Repair**。
  **不可选 "Restore packed base"**（会丢分析）。
- 覆盖 38 → **39/65**，缺 27 → **26**；产物 `mutation CartLineItemSet` 命中 1。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1355 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1355 \u8f6e')

note = """
## IDA 重启的三步（R1355 实测）

进程不在或端口 REFUSED 时，按顺序点掉三个模态框：

1. **「加载现有(L)」** —— 不要选「覆盖」(会重写 .i64)；
2. **「Proceed with unpacked base」** —— **不要选 "Restore packed base"**（那会退回到打包库，丢掉后续分析）；
3. **「Repair」** —— 修 `id0`，之后还会弹一次「Database still contains inconsistencies」→ 确定。

之后 `python analysis/ida.py health` 应返回 `status: ok`（含 `hexrays_ready`）。
"""

text = io.open(BLOCKERS, encoding='utf-8').read()
if 'IDA 重启的三步' not in text:
    with io.open(BLOCKERS, 'a', encoding='utf-8', newline='') as fh:
        fh.write(note)
    print('BLOCKERS got the restart recipe')
