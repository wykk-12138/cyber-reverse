"""R1381 record: the payment tail measured, and the static agenda closed with evidence."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
OPEN = 'docs/OPEN_ITEMS.md'

ROUND = """
---

## 第 1381 轮：把**支付侧长尾**也量了一遍 —— 两条长尾用同一把尺，结论一致

- **不继承结论**：R1367 量的是 30 个**店铺**异步名（29 个只有 `<Name>d__NN`、唯一有独立串的 `AddAddress` 零引用）。
  支付侧 243 个名字**从没这样量过**，直接用"大概一样"就是本项目反复付代价的那种继承。
- **新工具 `analysis/classify_payment_tail.py`**（用 R1378 的 `pe_read_direct`，不依赖 IDA）：
  ```
  支付族异步名：243
    可按名追到处理器：   6      GetPaymentIntent / GetSetupIntent / GetThreeDsJwtQuery
                                PlaceOrder / RefreshToken / SendTokenRequestAsync
    只有元数据：        237      无独立串
  ```
- **结论**：**两条长尾用同一把尺量出同一个答案** —— 按名可追的比例极低（店铺 1/30、支付 6/243），
  因为 NativeAOT 只保留状态机类型名，**方法名本身不是可引用的字符串**。
- **仍然开的**：**按地址逐条反编译**（267 个名字）。**这是 267 个独立工作单元，不是"一轮能做几件"的量**，
  且它不在 handoff 的取件判据里（那是"每轮取一条核心能力待办"，而 65/65 操作与全端点族已结案）。
- **因此把静态议程标记为完成**，并把残余**命名 + 量化**留在文档里，而不是含糊地说"还有一点"。

### 五要素

- **改了什么**：新增 `analysis/classify_payment_tail.py`、数据 `analysis/.payment_tail.json`；
  本文件（VERDICT）与 HANDOFF、OPEN_ITEMS 各一节；**无源码改动**。
- **验证命令与输出**：`python analysis/classify_payment_tail.py` → 243 / 6 可追 / 237 仅元数据，落盘 json。
- **数字变化**：长尾结论从"店铺 30 个已量"扩到"**店铺 30 + 支付 243 都量过**"。
- **证据等级**：Observation —— 243 个名字的分类结果与 6 个可追名字的地址/函数映射。
- **还剩什么**：267 个名字的按地址反编译（**已量化，非模糊待办**）；会话值类输入（euat/metadata id/storefront token）。
"""

POINTER = """
---

## 第 1381 轮（静态议程收口）

- **支付侧长尾量完了**：243 个名字里 **6 个可按名追、237 个只有元数据**（`analysis/classify_payment_tail.py`）。
  店铺侧 30 个在 R1367 量过（1 可追 / 29 元数据）。**两条长尾同一把尺、同一答案。**
- **剩余静态工作已量化**：**267 个名字需按地址逐条反编译** —— 不在 handoff 取件判据内，单独成账。
- 静态议程（65/65 操作、全端点族、C8 仪器、两条长尾的量）到此完成。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1381 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1381 \u8f6e')

text = io.open(OPEN, encoding='utf-8').read()
if 'classify_payment_tail' not in text:
    text += """
---

## 十八、两条长尾都已量化（R1381）

| 族 | 名字数 | 可按名追 | 只有元数据 | 量于 |
|---|---|---|---|---|
| 店铺 | 30 | 1（且零引用） | 29 | R1367 |
| 支付 | 243 | 6 | 237 | R1381 |

**剩余静态工作 = 267 个名字的按地址逐条反编译**，已量化成账，**不在 handoff 取件判据内**。

工具：`python analysis/classify_payment_tail.py`（不依赖 IDA，产出 `analysis/.payment_tail.json`）。
"""
    io.open(OPEN, 'w', encoding='utf-8', newline='').write(text)
    print('OPEN_ITEMS updated: both tails measured')
