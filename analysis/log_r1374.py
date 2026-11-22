"""R1374 record: AO's three urls land with their senders; the bodies remain the caller's, and why."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1374 轮：AO 三个端点落地 —— **但"三个体"要拆成两件事说**

- **先纠一个查法**：R 前几轮搜的是路径 `/v2/app/contact`，**镜像里存的是完整 URL**
  `https://checkout.ao.com/v2/app/contact`（`0x14705D114` / `0x14705D17C` / `0x14705D1E4`）。
  **又是"先假设形状"**（§2.7 的老毛病）：搜的是路径，存的是整串。
- **按 R1373 判据查引用，三个都命中真发送方**（URL 出现在函数的字面量表里）：
  ```
  contact   0x14093B650   35 字面量   标签 "Submitting info"、contenttype、cookie、newrelic、origin
  delivery  0x14093AB80 / 0x14093AE60   各 32   referer、priority、cookie、newrelic
  payment   0x14093B930（浏览器侧：sec-ch-ua / iframe / navigate / "Getting checkout"）
            0x14093BBF0（表单编码：application/x-www-form-urlencoded / newrelic / origin）
  ```
- **能落地的是**：三个 URL、`Origin = https://checkout.ao.com`、两个步骤标签、表单 content type。
- **不能落地的是"体的字段名"**：这些函数**带的是请求头名字**（accept/cookie/origin/newrelic/priority），
  JSON 由**它们的调用方**拼。**所以体仍由调用方给**，注释里明写 —— **不编字段名。**
- **一处自我克制**：`GatewayHttp.PostAsync` 只有五个参数（无 origin 重载），
  我没有为此改签名，而是**把 origin 记为观测事实**（常量 + 注释），不伪造注入路径。
- **产物**：`checkout.ao.com/v2/app/contact` 与 `Submitting info` 检出（见下）；尺寸见下。

### 五要素

- **改了什么**：新增 `Flows/AoCheckout.cs`、`tests/AoCheckoutTests.cs`（2 条）；
  `StoreFlow.SubmitCustomerAsync` 加分支；新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`AoCheckoutTests` → **2/2**；`StoreFlow|AoCheckout` → 见下；
  `orphan_documents.py` → 0；产物命中见下。
- **数字变化**：套件 +2；AO 从"三个体未知"变成**端点/标签/content-type 已知，体仍由调用方给**。
- **证据等级**：Observation —— 三个 URL 地址、三个真发送方的字面量表（含头名与标签）。
  **Correction** —— 此前按路径搜索得到"镜像里没有"，实际是完整 URL。
- **还剩什么**：Saucony 六步（本轮只确认 `SAUCONY-3DS` 一条：`0x140A76F60`，`MD`/`jwt`/`redirectUrl`/`stepUpUrl`/
  `Unexpected 3DS response`）、浏览器侧结账面。
"""

POINTER = """
---

## 第 1374 轮

- **AO 三端点落地**：`https://checkout.ao.com/v2/app/{contact,delivery,payment}`，
  `Origin`、`Submitting info`、`Getting checkout`、表单 content type 一并入码。
- **"三个体"要拆开说**：这些发送方带的是**请求头名**，JSON 在它们的调用方 → **体仍由调用方给**，不编字段名。
- **查法纠错**：之前搜 `/v2/app/contact`（路径）得"没有"，镜像存的是**完整 URL** —— §2.7 的老毛病再犯一次。
- **Saucony**：`SAUCONY-3DS`（`0x140A76F60`）带 `MD`/`jwt`/`redirectUrl`/`stepUpUrl`/`Unexpected 3DS response`，
  下轮落地。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1374 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1374 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if 'AoCheckout' not in text:
    text += """
---

## 十四、AO 三端点（R1374）

三个**完整 URL**（不是路径）：`https://checkout.ao.com/v2/app/{contact,delivery,payment}`。
发送方的字面量表确认引用（R1373 判据）。

**已落地**：URL、`Origin`、`Submitting info`、`Getting checkout`、`application/x-www-form-urlencoded`。
**未落地**：体的字段名 —— **发送方带的是请求头名，JSON 在其调用方**，故体由调用方给。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated: AO endpoints')
