"""R1329 record: an orphan document gets a caller, and a per-class duplicate check replaces the file-wide one."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1329 轮：给一个"没有调用点"的文档接上调用者——顺手把"查重复"改成按类查

- **先查自己留下的孤儿**：`CustomerCartDocument`（61 字符，R1320 落地的）在 `src` 里**只出现在自己的声明处**，
  其余引用全在测试里。**没有调用者的文档 = 复刻件发不出去的文档**，在 AOT 里还可能是会消失的那种（R1310）。
- **`AddressInput` 的形状这轮没找到，也不硬找**：
  - `line1`/`line2`/`line3` 看着像一簇，其实是**冻结字符串池按字母序排**的结果，邻居是 `line-feed`、`lineItem`；
  - 三个键的代码引用点分别是 **18 / 69 / 59** —— 通用 JSON 键，**按单引用点找专用锚的判据用不上**。
  - 结论写清：`AddressInput` 形状仍需抓包，`wh.onboard.billing/shipping` 的门槛保持不变。
- **改道做能做的**：`MagentoCart.ReadCartAsync`（发那份 61 字符查询）+ `CasioFlow.GetCartAsync`。
  这条同时补上 async tail 里 store 家族的购物车读步骤，用的**是镜像自己的查询**而不是编的。
- **"查重复"这件事终于改对了工具**：上一步我按文件查 `GetCartAsync`，结果被 `YeezySupplyFlow` 里那份挡住，
  报了"已存在"——**文件里有九个股类，按文件查答的是错的问题**。于是写了 `analysis/which_class_has.py`：
  **按大括号配对切类体**，报出是哪个类持有这个名字。查清 `CasioFlow` 确实没有，才插进去。
  这是 R1320/R1321/R1322 连撞三次 `CS0111` 之后，第一次用对的检查方式。
- **一个不肯编的判断**：店铺若用 masked id 存车，`customerCart` 就是空的——那要**报失败**，
  不能当成"购物车为空"继续跑。测试两条都钉住。

### 五要素

- **改了什么**：`MagentoCart.cs`（`ReadCartAsync`）；`RetailFlows.cs`（`CasioFlow.GetCartAsync`）；
  `MagentoCartTests.cs`（+2 条）；新增 `analysis/{find_address_keys,which_class_has,add_cart_read,add_cascio_get_cart,add_cart_read_tests}.py`；
  重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter "MagentoCartTests|Casio"` → **53/53**；
  `which_class_has.py GetCartAsync` → 只有 `YeezySupplyFlow`；产物 `customerCart` 命中 **1**；
  尺寸 61,383,680 → **61,390,848**；内嵌 `a708cddd9646`。
- **数字变化**：套件 2674 → 见 METRICS 当前值（+2）；产物 +7,168 字节。
- **证据等级**：Observation —— 孤儿文档（源码级事实，非搜索）、三个键的引用点数、按类切分的结果、产物命中。
  Inference —— 购物车读与购物车变更共用 `/graphql`。
  Unknown —— `AddressInput` 形状（仍需抓包）。
- **还剩什么**：`AddressInput`；方言条件（blocker）；`CurrencyConversion`(10406) 无归宿；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1329 轮

- `CustomerCartDocument`（61 字符）**此前没有调用者**（源码级事实）。已接进 `MagentoCart.ReadCartAsync` +
  `CasioFlow.GetCartAsync`，用的是镜像自己的查询。
- `AddressInput` 形状**没找到**：`line1/line2/line3` 相邻只是字符串池字母序；三个键引用点 18/69/59 是通用 JSON 键。
  **按单引用点找专用锚的判据在这里不适用**，仍需抓包。
- **查重复改用按类大括号配对**（`analysis/which_class_has.py`）：按文件查会被别的流里的同名 override 挡住 ——
  这正是 R1320–R1322 连撞三次 `CS0111` 的根因。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1329 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1329 \u8f6e')
