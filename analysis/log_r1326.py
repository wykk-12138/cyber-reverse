"""R1326 record: a shipped document was truncated by a pasted display marker, and the dialect question is blocked."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
BLOCKERS = 'docs/BLOCKERS.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1326 轮：查方言没查出来，却查出一条**已经在发布的坏文档**

- **方言方向收尾（记录在 BLOCKERS）**：三条否定把这条路堵死——
  ① 六个 PayPal GraphQL 操作**共用同一个端点族** `https://www.paypal.com/graphql?<Operation>`
     （`0x147097edc`..`0x14709817c` 一整块字典序，无 `graphql/partner` 形态），所以方言split**不是 URL 权限差**；
  ② 从两个 MoveNext 桩往上走**进的是数据而非调用**（`0x14777a93c` / `0x14777a96c`，相距 0x30）——**方法表分发，不是 if**；
  ③ 每个 `GqlAsync` 调用点都显式传了 url，所以"补一个默认端点"会是死代码。
  剩下的唯一路径是读 15 KB 异步体找字段名判断，本轮不做。**R1323–R1326 四轮同一条件未解 → 记 blocker。**
- **转向时撞到真问题**：把 `ApproveOnboardPaymentMutation` 与镜像逐字节一比（`analysis/compare_onboard.py`）：
  ```
  image:   4040 chars
  replica: 4022 chars   ← 结尾是字面量 "[4040 chars total]"
  ```
  **`WarhammerQueries.g.cs` 里那份文档是被人从某个显示输出里粘过来的，粘到了截断标记，文档在中间就断了。**
  这条流一直在往审批端点发一份**畸形 GraphQL 文档**。
- **全树扫同类**（`analysis/find_pasted_truncation.py`，正则 `\\[\\d+\\s*chars? total\\]`）：**只有这一处**。
- **修复**：用镜像 `0x1470CC8CC` 的 4040 字符逐字节写回（脚本生成，非手抄）；复核 `identical: True`；
  产物里 `chars total` 命中 **0**。
- **加了守卫**：`TheOnboardDocumentIsWholeAndCarriesNoTruncationMarker` —— 钉住 4040 长度、结尾形状，
  并**用反射遍历 `WarhammerQueries` 的每个公开常量**，任何一个含 `chars total` 就红。
  **这类粘贴错误不该靠人眼复查。**

### 五要素

- **改了什么**：`WarhammerQueries.g.cs`（文档重建，+240 字符内容）；`WarhammerGraphQlTests.cs`（+1 条守卫）；
  新增 `analysis/{save_paypal_onboard,compare_onboard,find_pasted_truncation,fix_onboard_document,add_onboard_guard}.py`；
  重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter Warhammer` → **15/15**；
  `compare_onboard.py` → `identical: True`（4040 = 4040）；`find_pasted_truncation.py` → `markers found: 0`；
  产物 `chars total` 命中 **0**，尺寸 61,370,368（不变），sha256 `50a245c0…` → `14d1a85e…`；内嵌 `75e4b50eb7a6`。
- **数字变化**：套件 2656 → 见 METRICS 当前值（+1）；产物尺寸不变、哈希变。
- **证据等级**：Observation —— 两份文档长度差、截断标记原文、镜像 4040 字符副本、全树唯一一处、产物零命中。
- **还剩什么**：方言条件（blocker，需抓包）；`OnboardGuestMutation`(3104)、`CurrencyConversion`(10406) 已解码待落；
  AO 三个 checkout 体；Saucony 六步路径。
"""

BLOCK_ENTRY = """
---

## R1326 · PayPal 3DS 方言的选择条件：四轮未解，转为 blocked

- **要回答的问题**：镜像据什么条件在两份 `ResolveThreeDsContingency`/`ThreeDsLookUpMutation` 方言之间选。
- **四轮积累的否定证据**（都可复算）：
  1. **R1323**：两份文档**各自冻结完整**、**各一个引用点**（`sub_14110FDB0` 14458B 发短的，`sub_141113680` 15615B 发长的），
     差异是一整块字段（resolve 108 字符 @2890；look-up 27 字符 @827），**运行时不拼片段**。
  2. **R1324**：resolve 与 look-up **都是方言对**，差的是**同一个字段** `authenticationProvider`；authenticate 只有一份。
  3. **R1325**：两个变体的 MoveNext 桩 `0x14258A4A0`/`0x14258A600` **相距 0x160** → 同一个类的两个异步方法。
  4. **R1326**：六个操作**共用同一端点族** `https://www.paypal.com/graphql?<Operation>`（无 `graphql/partner`）；
     从桩往上走**进数据表**（`0x14777a93c`/`0x14777a96c`，相距 0x30）→ **方法表分发，无 if 可读**。
- **解除条件**：一次带 3DS 挑战的抓包，看 `authenticationProvider` 是否出现在请求文档里。**这是唯一剩下的路径。**
- **复刻件的处置**：`paypal3ds.providerFields` 会话开关（R1325），**默认长那份**（= 改动前行为）。
  **不要**再靠读那两个 15 KB 异步体猜条件。
"""

POINTER = """
---

## 第 1326 轮

- 方言条件**记 blocker**：四轮否定证据（各引用点/整块字段差/MoveNext 桩相距 0x160/共用端点+方法表分发）。**解除条件=抓包。**
- **撞出真 bug**：`WarhammerQueries.ApproveOnboardPaymentMutation` 结尾是字面量 `[4040 chars total]` ——
  从显示输出粘来的截断标记，文档在中间就断了，**这条流一直在发畸形 GraphQL**。已按镜像 4040 字符逐字节重建。
- 全树扫 `[N chars total]` 只有这一处；新增反射守卫遍历 `WarhammerQueries` 全部常量，**粘贴错误不再靠人眼**。
- 已解码待落：`OnboardGuestMutation` 3104、`CurrencyConversion` 10406。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1326 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1326 \u8f6e')
append(BLOCKERS, BLOCK_ENTRY, 'R1326 \u00b7 PayPal 3DS')

text = io.open(DOC, encoding='utf-8').read()
if 'R1326' not in text:
    text += """
## 已解码、尚无归宿（R1326）

| 地址 | 长度 | 名称 | 状态 |
|---|---|---|---|
| `0x1470D611C` | 3104 | `OnboardGuestMutation` | 已解码，`analysis/.paypal_onboard.json`；没有已证实的步骤接它 |
| `0x1470CC8CC` | 4040 | `ApproveOnboardPaymentMutation` | **已修复**：`WarhammerQueries` 里那份曾被截断标记污染 |
| `0x1470D0FB4` | 10406 | `CurrencyConversion` | 已解码，同上 |

`OnboardGuestMutation` 与 `CurrencyConversion` **故意没有落进 `src`**：没有调用点的类型会被 AOT 裁掉（R1310 的教训）。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated with the decoded-but-unhoused set')
