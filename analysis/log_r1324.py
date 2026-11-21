"""R1324 record: the look-up has the same pair, so the flag stops being resolve-only."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1324 轮：look-up 也是方言对，而且差的是**同一个字段**——上一轮那个"只作用于 resolve"的断言是错的

- **先量后写**（`analysis/measure_three_ds_docs.py`）：
  ```
  lookup_b     0x1470E2CCC   871   vs replica LookUpDocument       IDENTICAL
  authenticate 0x1470E1FAC   813   vs replica AuthenticateDocument  IDENTICAL
  lookup_a     0x1470E261C   844   vs lookup_b 差 27 字符，offset 827
  ```
  这 27 字符就是 **`authenticationProvider`** —— 和 resolve 那一对差的是**同一个字段**。
- **所以这不是两次巧合，是一个方言问题**：镜像里 resolve 与 look-up **各有两份**，
  短的那份都少 `authenticationProvider`；authenticate 只有一份，本来就不含该字段。
- **上一轮我写的断言是错的**：`DocumentFor(LookUpOperation, providerFields: false)` 当时被我钉成"等于长那份"，
  理由是"这个开关只作用于 resolve"。现在有新证据：**开关属于两个操作**。
  **我改的是断言本身，并在注释里写明为什么改**——不是删掉它。
- **落码**：`LookUpDocumentWithoutProviderFields`（844 逐字节，脚本生成）+
  `DocumentFor` 的 `providerFields` 现在对 **resolve 与 look-up 同时生效**；默认仍是长那份，既有调用点不变。
  新增测试钉住 look-up 对的**插入点 827**，并顺带断言 authenticate **不含** `authenticationProvider`。
- **五个常量全部与镜像逐字节一致**（`analysis/verify_three_ds_docs.py` 一次核完）：
  844 / 871 / 813 / 10262 / 10370。

### 五要素

- **改了什么**：`PayPalThreeDs.cs`（新增 844 变体、开关扩到两个操作、`DocumentFor` 补文档注释）；
  `PayPalThreeDsTests.cs`（**改正 1 条**、新增 1 条）；新增 `analysis/{measure_three_ds_docs,add_lookup_variant,verify_three_ds_docs}.py`；
  重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter PayPalThreeDsTests` → **30/30**；
  `verify_three_ds_docs.py` → 五个常量 **IDENTICAL / every constant matches: True**；
  尺寸 61,368,320 → **61,370,368**；内嵌 `685fce352c1c (is HEAD)`。
- **数字变化**：套件 2647 → 见 METRICS 当前值（+1）；产物 +2,048 字节；**3DS 文档常量：2 个 → 5 个**。
- **证据等级**：Observation —— 三份文档长度、lookup 对唯一差异区在 827、五个常量逐字节一致。
  Inference —— 短方言=不带 `authenticationProvider` 的那条代码路径（函数名未解）。
- **还剩什么**：**从"有文档"到"会选"**——哪个函数在什么条件下选哪个方言，这需要读那两个 14–15 KB 的函数；
  `CurrencyConversion`(10996) 与 `cartApiObjectCreate`(5876) 未落地；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1324 轮

- **look-up 也是方言对**：844（`0x1470E261C`）与 871（`0x1470E2CCC`），差 **27 字符 `authenticationProvider`**（offset 827）——
  和 resolve 那一对差的是同一个字段。**一个方言问题，不是两次巧合。**
- authenticate 813 只有一份，本来不含该字段；复刻件里它一直是对的。
- **改正了上一轮的错误断言**：`providerFields` 现在对 resolve 与 look-up **同时**生效，默认仍为长那份。
- 五个 3DS 文档常量全部与镜像逐字节一致（`verify_three_ds_docs.py`）。
- 下一步是**"会选"**：读那两个 14–15 KB 的函数，定出选方言的条件。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1324 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1324 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'R1324' not in text:
    text = text.replace(
        '| `0x1470E261C`/`0x1470E2CCC` | 877/905 | `ThreeDsLookUpMutation` | 同上 |',
        '| `0x1470E261C`/`0x1470E2CCC` | **844/871** | `ThreeDsLookUpMutation` 方言对 | **R1324 已落地**：`LookUpDocumentWithoutProviderFields` / `LookUpDocument` |')
    text = text.replace(
        '| `0x1470E1FAC` | 837 | `ThreeDsAuthenticateMutation` | 同上 |',
        '| `0x1470E1FAC` | **813** | `ThreeDsAuthenticateMutation`（只有一份，不含 provider 字段） | 早已在 `AuthenticateDocument`，R1324 确认逐字节一致 |')
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
