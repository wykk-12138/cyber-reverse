"""R1378 record: the AddressInput builder, and the model I had to correct."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1378 轮：**找到 `AddressInput` 的构造点** —— 而它的字段和我 R1372 猜的不一样

- **新工具：`analysis/pe_read_direct.py`（不依赖 IDA）**。IDA 本次会话已死 **4 次**（每次都在发布/变异这类吃内存的操作之后）。
  剩下的静态工作只需要两件事：读冻结字符串、找引用者 —— **都不需要反汇编器**，而布局本项目早已定死
  （`[MethodTable][Length][UTF-16]`、`chars_va - 12`）。所以这个脚本自己读 PE 节表、VA→偏移、冻结字符串，
  并用 `.pdata` 的 `RUNTIME_FUNCTION` 把站点映射到函数。**它明确不是反汇编器**：
  `find_disp32` 只做 `site_va + 4 + disp32 == target` 这道算术，命中仍需按 R1372 的规矩用字面量表确认。
- **用它定位**：`recipientName` 有 5 个 header 形引用，其中两个函数被解出来：
  - **`0x140AD5B10`（29 字面量）—— 这就是构造点**：
    ```
    recipientName firstName lastName line1 line2 city postalCode countryCode phone email
    billingAddress checkoutType EXPRESS OTHER payerId nonce details
    /cart/paypal application/json PayPalAccount Store "Submit info"
    ```
  - `0x140F4BA90`（74 字面量）：另一个同类发送方，带 `Cyber IO`/`CyberTown`/`Cyberstreet 1` 这类**测试默认值**。
- **纠正 R1372**：我当时从字符串表里读到 `addressLine1`/`addressLine2`/`locality`，**并当成这个对象的字段**。
  **构造点用的是 `line1`/`line2`/`city`。**
  **字符串表说明"存在什么"，构造点说明"用了什么"** —— 这两件事我此前混为一谈。
- **落码**：`AddressInput` 重写为构造点的十个字段；新增 `PayPalExpressCart`（`/cart/paypal` + `EXPRESS`/`OTHER` +
  `billingAddress`/`payerId`/`nonce`/`details` + `Submit info`，`Body(...)` 只接受那两个 checkoutType）。
- **产物**：`/cart/paypal` 与 `Submit info` **ASCII 各命中 1**；`recipientName` UTF-16 5 / ASCII 6；
  尺寸 62,079,488 → **62,085,632**。

### 五要素

- **改了什么**：新增 `analysis/pe_read_direct.py`（+ `func` 子命令）、`Flows/PayPalExpressCart.cs`；
  `AddressInput` 按其构造点重写；`AddressInputTests` 重写（3 条）、新增 `PayPalExpressCartTests`（3 条）；
  重发布；METRICS 重生成。
- **验证命令与输出**：`AddressInputTests|PayPalExpressCartTests` → **6/6**；`orphan_documents.py` → 0；
  产物命中见上。
- **数字变化**：套件 +3；`AddressInput` 从"名字已知、构造点未知"变成**构造点已知、字段已纠正**。
- **证据等级**：Observation —— 两个函数的字面量表（含十个地址字段与 `/cart/paypal` 全套词汇）、产物命中。
  **Correction** —— R1372 用字符串表推断字段，构造点否决了三个名字中的两个。
- **还剩什么**：浏览器侧结账面（需界面上下文）。
"""

POINTER = """
---

## 第 1378 轮

- **新工具 `analysis/pe_read_direct.py`**：不依赖 IDA 读冻结字符串 + 扫 disp32 + `.pdata` 函数映射
  （IDA 本会话已死 4 次，且都死在发布/变异之后）。
- **`AddressInput` 构造点 = `0x140AD5B10`**（29 字面量）：字段是
  `recipientName/firstName/lastName/line1/line2/city/postalCode/countryCode/phone/email`，
  周围是 **`/cart/paypal`** 与 `checkoutType`(`EXPRESS`/`OTHER`)、`payerId`、`nonce`、`billingAddress`、`Submit info`。
- **纠正 R1372**：`addressLine1/addressLine2/locality` 在镜像里存在，**但不是这个对象用的**。
  **字符串表说"存在什么"，构造点说"用了什么"。**
- 新增 `Flows/PayPalExpressCart`；`AddressInput` 按构造点重写。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1378 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1378 \u8f6e')

blockers = io.open(BLOCKERS, encoding='utf-8').read()
if 'pe_read_direct' not in blockers:
    blockers += """
## IDA 反复死亡时的降级路径（R1378）

本会话 IDA 死了 **4 次**，**每次都发生在 `dotnet publish` 或 `mutation-check` 之后**（内存最紧张的时刻）。

**先用不依赖 IDA 的读法**：

```
python analysis/pe_read_direct.py str  <chars_va>   # 读冻结字符串
python analysis/pe_read_direct.py refs <chars_va>   # 扫 disp32（头形与字符形都试）
python analysis/pe_read_direct.py func <site_va>    # .pdata 映射到函数起点
```

**它不反汇编** —— 需要伪代码时仍要 IDA。**但"这个字符串在不在、谁引用它、属于哪个函数"三问已不需要 IDA**，
因此把 IDA 重启安排在**每轮开头**，发布与变异留在后面，可显著减少中断。
"""
    io.open(BLOCKERS, 'w', encoding='utf-8', newline='').write(blockers)
    print('BLOCKERS got the IDA-free path')
