"""R1325 record: what the dialect choice is not, and a run-time switch for what it is."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1325 轮：方言的**选择条件**仍未解，但已经把"它不是什么"钉死了，并把开关做成运行时可切

- **这轮读的是两个 14–15 KB 异步体的接线**，得到三条否定结论（都是可复算的）：
  1. `sub_14110FDB0`(14458) 与 `sub_141113680`(15615) 的 **MoveNext 桩**是 `0x14258A4A0`(0xc1) 与
     `0x14258A600`(0xcf)，**相距 0x160** —— 同一个类的两个异步方法，不是两条独立流程。
  2. 两份文档**各自冻结完整**（R1323/R1324 已测得各一个引用点），**运行时不拼字段**：
     选择发生在"选方法"，不在"选片段"。
  3. 引用点落在方法描述符表里（`0x14760B5F8` 处能看到 `0x0110FDB0` 这样的 4 字节 RVA），从另一侧得出同一结论。
- **于是这轮不做猜测，做开关**：`ProviderFieldsRequested(c)` 读 `paypal3ds.providerFields`，
  **默认 `true`（=长那份）**，即本类此前一直发的文档；`GqlAsync` 的 `document ?? DocumentFor(...)` 现在带上它。
  这样**一次抓包就能定案，不用改代码**。
- **可达性这次按 §4.5 判，不靠字面量**：
  - 上一轮产物 `61,370,368 / 16791e4d…`，本轮产物 **同尺寸** `61,370,368 / 50a245c0…`；
  - 两轮之间**唯一的源码改动就是本轮这三处**（新方法 + 调用点 + 测试，测试不进产物）；
  - **同尺寸、哈希变** ⇒ 新代码进了产物。这正是 §4.5 说的情形（三个探针都是 +0 尺寸）。
  - 附带一条观察：`paypal3ds.providerFields` 在产物里 **ascii 与 UTF-16LE 都搜不到**，
    而同一批会话键 `casio.cartVersion` 在 UTF-16LE 里**搜得到**（对照）。
    字符串存储依旧是混合的 —— **有对照的缺席仍然不是证据**，这轮的判定走的是哈希，不是搜索。

### 五要素

- **改了什么**：`PayPalThreeDs.cs`（`ProviderFieldsRequested` + `GqlAsync` 接入）；
  `PayPalThreeDsTests.cs`（+8 条：会话取值 Theory 七行、请求体随开关切换一条）；新增 `analysis/add_dialect_flag.py`、`analysis/add_dialect_tests.py`；
  重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter PayPalThreeDsTests` → **38/38**；
  产物 `ProviderFieldsRequested` 命中 1；尺寸 61,370,368（与上轮同）；sha256 `16791e4d…` → `50a245c0…`；内嵌 `6b83b9c4e678`。
- **数字变化**：套件 2648 → 见 METRICS 当前值（+8）；产物尺寸不变（§4.5 的正常情形）。
- **证据等级**：Observation —— 两个 MoveNext 桩的地址与间距、描述符表里的 RVA、同尺寸哈希变化、对照搜索。
  **Unknown（未解）** —— 镜像据什么条件选方言。
- **还剩什么**：方言选择条件（**唯一路径是抓包**，或读懂那两个 15 KB 函数的分叉）；
  `CurrencyConversion`(10996)、`cartApiObjectCreate`(5876) 未落地；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1325 轮

- 方言**选择条件未解**，但本轮钉死三条否定：两个变体是**同一个类的两个异步方法**（MoveNext 桩相距 0x160）、
  两份文档**各自冻结完整**（运行时不拼片段）、引用落在方法描述符表。
- 因此**做开关不做猜测**：`ProviderFieldsRequested(c)` 读 `paypal3ds.providerFields`，默认长那份；`GqlAsync` 已接入。
  **一次抓包即可定案，无需改码。**
- 可达性按 §4.5 走哈希：上轮 `16791e4d…` → 本轮 `50a245c0…`，**同尺寸**，两轮之间只有本轮三处改动 ⇒ 新代码进产物。
  附带：`paypal3ds.providerFields` 两种编码都搜不到，而 `casio.cartVersion` 搜得到 —— **有对照的缺席仍不是证据**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1325 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1325 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'R1325' not in text:
    text += """
## 方言开关（R1325）

两份文档**各自冻结完整**，镜像在"选方法"而不是"选片段"：`sub_14110FDB0`(14458) 发不带
`authenticationProvider` 的那份，`sub_141113680`(15615) 发带的那份。两者的 MoveNext 桩
（`0x14258A4A0` / `0x14258A600`）**相距 0x160**，是同一个类的两个异步方法。

**镜像据什么条件选，仍未解。** 复刻件因此提供运行时可切：
`paypal3ds.providerFields`（缺省 `true` = 带 `authenticationProvider` 的那份），由
`PayPalThreeDs.ProviderFieldsRequested` 读取、`GqlAsync` 使用。一次抓包即可定案。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md got the dialect section')
