"""R1372 record: AddressInput's four names, and a reference claim I had to withdraw."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1372 轮：`AddressInput` 的四个字段名落成模型 —— **同时撤回我自己刚写下的引用结论**

- **IDA 又挂了**（`URLError` + 无进程无端口）。按配方用 `ida-mcp-doctor.ps1 -Path` 重拉，
  三个模态框依次点掉：**加载现有** → **Proceed with unpacked base** → **Repair** → **确定**（inconsistencies），
  `health` 回到 `status: ok`。**其中两次 UIA Invoke 报成功但窗口未变，改用像素点击 / `foreground_fallback` 才真正生效** ——
  这条要记进 BLOCKERS。
- **`AddressInput` 的类型名在镜像里不是字符串**，这就是它一直"形状未知"的原因。但**字段名是**：
  ```
  recipientName  0x147149A94    addressLine1  0x146F6EC6C
  addressLine2   0x146F6EC9C    locality      0x146FC9852
  ```
- **撤回一条结论**：我先是据 `disp32_scan_any` 的命中写下"前三个有代码引用"。随后把命中函数
  `0x140AAE300`（`CreditCard` 的发送方）的**全部 20 个字面量**解码出来 —— **里面一个地址字段都没有**。
  **`disp32` 命中是字节图案，不是引用；只有当那个函数的字面量表里出现这个名字，才算引用。**
  已把模型注释改写并把这条写进测试（`TheNamesSurviveButTheReferenceClaimDoesNot`）。
- **顺带确认一条边界**：`api/checkout/v1/orders/<id>/finalize` 这个发送方**不吃 AddressInput**
  （它吃 `cardNumber`/`cardCvv`/…/`paymentMethodId`/`paymentMethodType`/`savePaymentMethodAsToken`）——
  **这缩小了 `AddressInput` 可能出现的位置**。
- **落码**：`Flows/AddressInput.cs`（四个镜像拼写的字段名 + 八个文档拼写名 + `ToJson()` 空值不写 + `EmittedFieldNames`）。

### 五要素

- **改了什么**：新增 `Flows/AddressInput.cs`、`tests/AddressInputTests.cs`（4 条）；新增 3 个 analysis 脚本；
  重发布；METRICS 重生成；BLOCKERS 补模态框处置。
- **验证命令与输出**：`AddressInputTests` → **4/4**；`operation_gap.py` → 覆盖 63/65 不变（本条是模型不是操作）；
  `orphan_documents.py` → 0；产物见下。
- **数字变化**：套件 +4。
- **证据等级**：Observation —— 四个名字的字符串地址、CreditCard 发送方的 20 个字面量清单。
  **Correction** —— 先前"三个有代码引用"的说法被同一轮的解码推翻。
- **还剩什么**：4 类 —— AO 三个体、Saucony 六步、`/cartApi/checkout` 发送方、浏览器侧结账面；`AddressInput` 现为
  "名字已知、构造点未知"。
"""

POINTER = """
---

## 第 1372 轮

- **IDA 又挂**：用 `ida-mcp-doctor.ps1 -Path` 重拉 + 依次点掉**加载现有 / Proceed with unpacked base / Repair / 确定**。
  **两次 UIA Invoke 报成功但无效**，改像素点击与 `foreground_fallback` 才生效（已记 BLOCKERS）。
- **`AddressInput` 四个字段名落地**（`recipientName`/`addressLine1`/`addressLine2`/`locality`），
  类型名在镜像里不是字符串。
- **撤回一条自写结论**：`disp32` 命中 ≠ 引用。`CreditCard` 发送方 20 个字面量里**没有**地址字段。
  **只有函数字面量表里出现该名字，才算引用。**
- 覆盖仍 63/65；`AddressInput` 从"形状未知"变成"名字已知、构造点未知"。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1372 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1372 \u8f6e')

blockers = io.open(BLOCKERS, encoding='utf-8').read()
if 'UIA Invoke' not in blockers:
    blockers += """
## IDEA 模态框：UIA Invoke 可能"报成功但无效"（R1372）

重拉 IDA 时，`click(element_token=...)` 对 `请确认` 对话框**返回 ok 但窗口内容不变**（截图逐像素相同）。
有效做法按顺序试：

1. **像素点击**（`x, y` 取自 `get_window_state` 的截图）；
2. **`foreground_fallback: true`** 的 `run_steps`；
3. 每次动作后**重新 `list_windows`** —— 对话框 id 会变（本轮 3017454 → 1969868 → 3148526 → 2297548）。

**判据**：`ida.py health` 返回 `{"status":"ok", ... "hexrays_ready":true}`；`strings_cache_ready` 会晚几十秒才为真。
"""
    io.open(BLOCKERS, 'w', encoding='utf-8', newline='').write(blockers)
    print('BLOCKERS got the modal recipe')

text = io.open(OPEN, encoding='utf-8').read()
if 'recipientName' not in text:
    text += """
---

## 十二、`AddressInput`：名字已知，构造点未知（R1372）

类型名**不是字符串**，但四个字段名是：`recipientName`(0x147149A94)、`addressLine1`(0x146F6EC6C)、
`addressLine2`(0x146F6EC9C)、`locality`(0x146FC9852)。

**已撤回的说法**：曾据 `disp32` 命中称"三个有代码引用"；`CreditCard` 发送方（0x140AAE300）的 20 个字面量里
**没有地址字段**。**`disp32` 命中只是字节图案，函数字面量表中出现才算引用。**

**边界**：`api/checkout/v1/orders/<id>/finalize` 不吃 `AddressInput`。模型在 `Flows/AddressInput.cs`。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated: AddressInput status')
