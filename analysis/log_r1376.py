"""R1376 record: the last GraphQL operation lands, and the Saucony claim gets full-table evidence."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1376 轮：**64/65** —— 最后一个 GraphQL 操作落地；Saucony 的"没有路径"结论也用全表核了一遍

- **`updateMyPaymentWithActions`(401)** 并入 `CybersourcePayment`（`updateMyPaymentWithActions` 文档 + `UpdateAsync`），
  声明集实测为 **`$actions` / `$id` / `$version`**。同一处理器（`0x140E55A00`，R1364 读过）同一拒绝语
  `No capture context`。接进 `GetPaymentTokenAsync` 的 `cybersource.updateMode` 分支。
  → **65 个操作里 64 个已落地，只剩 `Saucony` 一族。**
- **顺手核了 Saucony 那条老结论**（"镜像里没有拼出 Saucony API 路径的字面量"）：
  遍历 `analysis/ida_strings.txt` **全表 324,901 条**，`saucony` 相关只有 **15 条** ——
  `Saucony`/`Saucony CA/EU/UK/US`/`SAUCONY`/`SAUCONY-3DS`/`SAUCONY-DEBUG`/`saucony_ca|eu|europe|us`/
  `SauconyVariant…`/`https://www.saucony.com` —— **没有一条是路径**。
  **这不是"没搜到"，是全表只有这些** ⇒ 结论成立，且现在有全量证据。
- **又一次 IDA 死亡**（第 3 次）：`ida-mcp-doctor -Path` → **加载现有 → Proceed with unpacked base → Repair → 确定**。
  其中 `foreground_fallback` 的像素点击**报 `foreground_unavailable`**（前台被别的窗口占着），
  **改用 `element_token` 的 UIA Invoke 才生效** —— 这条与上一轮记的配方**互补**，已合并进 BLOCKERS。
- **一处自我的格式错误**：插入的分支缩进错（24 空格 + `return` 顶格），编译能过但读起来是坏的 ——
  **单独一轮修掉**，不留"能跑就行"的代码。
- **产物**：`mutation updateMyPaymentWithActions` UTF-16 命中 **1**；尺寸 62,063,616 → **62,069,248**。

### 五要素

- **改了什么**：`CybersourcePayment.cs`（+文档 + `UpdateAsync`）；`StoreFlow.GetPaymentTokenAsync` 加 update 分支；
  `CybersourcePaymentTests`（+2，共 17）；新增 2 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`Cybersource*` → **17/17**；`StoreFlow|Payment` → **101/101**；
  `operation_gap.py` → 覆盖 **64/65**（缺 1）；`orphan_documents.py` → 0；产物命中 1；尺寸见上。
- **数字变化**：覆盖 63 → **64/65**；缺 2 → **1**；套件 +2；产物 +5,632 字节。
- **证据等级**：Observation —— 文档 401 字符与三个声明、处理器拒绝语、**全表 15 条 Saucony 字符串**、产物命中。
- **还剩什么**：1 条 —— Saucony 六条 API 路径（**全表已证镜像里没有**），加浏览器侧结账面（需界面上下文）。
"""

POINTER = """
---

## 第 1376 轮

- **`updateMyPaymentWithActions`(401) 并入 `CybersourcePayment`**（声明 `$actions`/`$id`/`$version`，同一处理器与拒绝语），
  接进 `GetPaymentTokenAsync`。**覆盖 63 → 64/65**，只剩 Saucony 一族。
- **Saucony 结论全表核实**：324,901 条字符串里 `saucony` 相关**仅 15 条**（名字/区域/标识/一个 host），
  **无一条路径** ⇒ "镜像里没有 Saucony API 路径"成立，且这次是**全量证据**。
- **IDA 第 3 次死亡**：`foreground_fallback` 像素点击会报 `foreground_unavailable`，
  **改用 `element_token` UIA Invoke** 才生效（配方已合并进 BLOCKERS）。
- 一处自伤：插入分支缩进坏（编译过但读起来坏）→ 单独修掉，不留"能跑就行"。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1376 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1376 \u8f6e')

blockers = io.open('docs/BLOCKERS.md', encoding='utf-8').read()
if 'foreground_unavailable' not in blockers:
    blockers += """
### 补充：`foreground_fallback` 的像素点击可能报 `foreground_unavailable`（R1376）

若前台被别的窗口占着，`delivery_mode:"foreground"` 的像素点击会直接拒绝。
**改用 `element_token` + UIA Invoke**（同一个 `run_steps` 里 `foreground_fallback: true`）即可生效。
顺序：**先试 `element_token` 的 UIA Invoke，再试像素点击，最后才试 foreground 像素点击。**
"""
    io.open('docs/BLOCKERS.md', 'w', encoding='utf-8', newline='').write(blockers)
    print('BLOCKERS updated with the UIA-first order')
