"""R1308 round record: the per-class step inventory, and the store it turned up."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
ROADMAP = 'docs/REMAINING_REPLICATION_ROADMAP.md'

ROUND = """
---

## 第 1308 轮：状态机名按类成组——于是长尾里浮出一整个复刻件没有的店

- **上一轮给的是一张扁平名字表**，这轮把地址也用上了：`<名字>d__NN` 在元数据里**按类成组**出现，
  `NN` 是该类内的方法序号，所以相邻一串名字就是**那个类的步骤清单**。`analysis/async_tail.py` 增加
  `--classes-doc`，产物 `docs/ASYNC_CLASSES.md`（按起始地址分组，逐组列出 d__ 序号 / 名字 / 三态）。
- **分组是按邻近度（0x800 字节）切的，不是按类型边界**——所以偶尔会把相邻两个类并进一组。这一点写在
  文档抬头，不能把它当"DLL 边界"用。
- **它立刻兑现了价值**：一组里出现了 `_merchantId` / `_encodedMerchantId` / `_paymentFormToken` /
  `_checkoutCaptchaEnabled` 四个字段名，紧邻的步骤是
  `<FindProduct>d__6` / `<AddToCart>d__7` / `<GetCheckout>d__8` / `<SubmitShipping>d__9` /
  `<SubmitBilling>d__10` / `<SubmitOrder>d__11` / **`<HandleOrderResult>d__12`** / **`<PayerAuthenticate>d__13`**，
  同一条串里还有 `SauconyVariant`。
- **镜像里有一家店，复刻件完全不知道**：`Saucony` / `Saucony CA` / `Saucony EU` / `Saucony UK`
  与 `saucony_us` / `saucony_ca` / `saucony_eu` / `saucony_europe`、`https://www.saucony.com`；
  而 `python tools/where_is.py Saucony` 在仓库里**零命中**，`store_catalog.py` 的 65 条也没有它。
  它的支付面是**自带 merchantId + paymentFormToken + checkoutCaptcha 的托管表单**，
  两个步骤 `HandleOrderResult` / `PayerAuthenticate` 在复刻件源码里都不存在。
- **这一轮没有改 `replica/src`**：把 Saucony 加进目录需要先定它的 `flow type`（那 8 个步骤名不像
  Shopify/Demandware 的任何一套），凭猜写进 `CreateAll()` 就是把 Unknown 伪装成事实。留到下一轮。

### 五要素

- **改了什么**：`analysis/async_tail.py`（新增 `state_machine_sites` / `group_by_blob` / `render_classes`
  与 `--classes-doc`）、新增生成物 `docs/ASYNC_CLASSES.md`（2858 行）。未改 `replica/src` 与 `replica/tests`。
- **验证命令与输出**：`python analysis/async_tail.py --classes-doc` → 写出 2858 行，分组表首行起
  `0x1431E380A/4 步`、`0x1432A493F/26 步` 等；`grep SubmitThreeDSAuthentication docs/ASYNC_CLASSES.md`
  → 该组的 `12 HandleOrderResult absent`、`13 PayerAuthenticate absent`、`29 SubmitAddress absent`、
  `35 SubmitThreeDSAuthentication absent`、`36 FinalizeCheckout absent`；
  `dotnet test --filter "DocsConsistency|ParityDoc|DocumentNumbersAreSourced|SourceEncoding"` → **20/20**。
- **数字变化**：仍是分类而非度量；`docs/METRICS.md` 不需要重生成（树未变、产物 `current`）。
- **证据等级**：Observation —— 四个字段名、8 个步骤名及其 d__ 序号、`Saucony` 四行显示名与四个 store id、
  `https://www.saucony.com`、以及 `where_is Saucony` 零命中与 catalog 65 条里没有它。
  Inference —— 这是一个独立店铺类且带自己的托管支付表单（由字段名与步骤名推定，未反编译其方法体）。
  Unknown —— 该类的方法地址、`flow type`、两个支付步骤的报文。
- **还剩什么**：Saucony 的目录条目与 flow（需先定 flow type）；66 个 absent 支付名里其余部分的定位；
  分组边界若要做准，得用类型元数据而不是字节邻近度。
"""

ROADMAP_ADD = """
  6. **`Saucony` 是一个复刻件完全没有的店**（R1308 从状态机分组里发现）：镜像有
     `Saucony` / `Saucony CA` / `Saucony EU` / `Saucony UK` 与 `saucony_us|ca|eu|europe` 四个 id、
     `https://www.saucony.com`，以及一个带 `_merchantId` / `_encodedMerchantId` / `_paymentFormToken` /
     `_checkoutCaptchaEnabled` 的**托管支付表单**。它的步骤是 d__6..13：
     `FindProduct` / `AddToCart` / `GetCheckout` / `SubmitShipping` / `SubmitBilling` / `SubmitOrder` /
     `HandleOrderResult` / `PayerAuthenticate`。`where_is Saucony` 在仓库零命中，`store_catalog.py` 的 65 条也没有它。
     **下一轮先定它的 `flow type` 再进 `CreateAll()`**，不要凭猜。
"""

POINTER = """
---

## 第 1308 轮

- 状态机名**按类成组**（`NN` 是类内方法序号），所以 `docs/ASYNC_CLASSES.md` 给出的是**每个类的步骤清单**，
  比扁平名字表有用。生成器 `analysis/async_tail.py --classes-doc`。
- 分组是**按 0x800 字节邻近度**切的，会偶尔并组，别当类型边界用。
- 由此发现：**`Saucony` 是复刻件完全没有的一家店**（4 个 id、独立托管支付表单、8 个步骤），
  两个支付步骤 `HandleOrderResult` / `PayerAuthenticate` 源码里根本没有。下轮先定 flow type 再加目录。
- 本轮未改 `replica/src`。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1308 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1308 \u8f6e')

text = io.open(ROADMAP, encoding='utf-8').read()
if 'Saucony' in text:
    print('roadmap already mentions Saucony')
else:
    anchor = '  5. **\u957f\u5c3e\u540d\u5355\u5df2\u843d\u6210\u8868**'
    start = text.index(anchor)
    end = text.index('\n\n', start)
    text = text[:end + 2] + ROADMAP_ADD + text[end + 2:]
    io.open(ROADMAP, 'w', encoding='utf-8', newline='').write(text)
    print('roadmap updated with the Saucony item')
