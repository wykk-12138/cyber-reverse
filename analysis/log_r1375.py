"""R1375 record: Saucony's payer step reads its reply, which the handler spells out completely."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1375 轮：Saucony 的 `PayerAuthenticate` 从"整步拒绝"变成"能读应答"

- **`SAUCONY-3DS` 的处理器 `0x140A76F60` 只有九个字面量**，但这一组恰好是一条完整规则：
  ```
  MD   SAUCONY-3DS   StatusInfo   Unexpected 3DS response   error   jwt   red   redirectUrl   stepUpUrl
  ```
  ⇒ 应答只有两种形状（**redirect** 或 **step-up**），旁边带 `jwt`，MD 是 3DS 的字段；**其它一律用处理器自己的话拒绝**。
- **改的是什么**：`SauconyFlow.PayerAuthenticate` 原本对**每一次调用**都返回
  `"… endpoint unknown …"`。**这句话对"建请求"仍然成立，对"读应答"已经不成立** ——
  所以它现在：给了 `saucony.threeDsReply` 就分类（并写回 `threeDsShape`/`threeDsUrl`/`threeDsJwt`），
  没给才退回原来的拒绝。**两个 url 同时出现时 redirect 优先**（浏览器会跟着走的那一个）。
- **不做的**：**不编请求路径** —— 那个类的注释本来就写着"没有字面量拼出 Saucony 的 API 路径"，这句仍然有效。
- **三处测试脚手架失误**（都是我没先看现有写法）：
  `FlowContext` 的 `Http`/`Url` 是**必填**（`CS9035`）；`StepOutcome.Success` 是**方法组**不是属性（`CS0019`）；
  两个测试各自需要自己的 `NetClient`（`CS0103`）。**照抄同文件既有写法**后一次通过。
- **产物**：`SAUCONY-3DS`、`Unexpected 3DS response`、`stepUpUrl` 检出（见下）；尺寸见下。

### 五要素

- **改了什么**：新增 `Flows/SauconyThreeDs.cs`、`tests/SauconyThreeDsTests.cs`（5 条）；
  `SauconyFlow.PayerAuthenticate` 重写为分类器；`SauconyFlowTests.cs`（+2，共 21）；重发布；METRICS 重生成。
- **验证命令与输出**：`Saucony*` → **21/21**；`orphan_documents.py` → 0；产物命中见下。
- **数字变化**：套件 +7；Saucony 从"整步 Unknown"变成"**应答可分类，请求仍未建**"。
- **证据等级**：Observation —— 九字面量清单、两条 url 字段、拒绝语、产物命中。
- **还剩什么**：Saucony 的六条 API 路径（仍未拼出）、浏览器侧结账面。
"""

POINTER = """
---

## 第 1375 轮

- **Saucony `PayerAuthenticate` 不再是"整步拒绝"**：处理器 `0x140A76F60` 的九个字面量给出完整规则
  （`redirectUrl` / `stepUpUrl` / `jwt` / `MD` / `Unexpected 3DS response`）→ 新增 `Flows/SauconyThreeDs` 分类器。
  **请求路径仍然没有**，注释与拒绝语照旧。
- 测试脚手架三处失误（`FlowContext` 必填项、`Success` 是方法组、每测试各自要 `NetClient`）——
  **照抄同文件既有写法后通过**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1375 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1375 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if 'SauconyThreeDs' not in text:
    text += """
---

## 十五、Saucony 的 3DS 应答已可读（R1375）

处理器 `0x140A76F60`（`SAUCONY-3DS`）九个字面量：`MD`、`StatusInfo`、`Unexpected 3DS response`、`error`、
`jwt`、`red`、`redirectUrl`、`stepUpUrl`。

⇒ 应答两形状（redirect / step-up）+ jwt；其它用处理器原话拒绝。实现 `Flows/SauconyThreeDs`，
`SauconyFlow.PayerAuthenticate` 改为分类。

**仍未解**：Saucony 六条 API 路径（镜像里没有拼出 Saucony API 路径的字面量）。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated: Saucony 3DS')
