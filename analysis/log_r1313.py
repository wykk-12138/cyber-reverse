"""R1313 round record: two dead ends on the Casio signature, then AO.com."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1313 轮：签名线两次走死，转向 AO.com——这次只做能做的，不凑占位

- **死路一（`UgAFUFFACQAEU1BSBAcB`）**：本以为这个唯一串能把我带到 Casio 的 checkout 函数。
  九处引用全落在 `0x14093A900` 一带，反编译出来是个**浏览器请求头构造器**：
  `accept` / `accept-encoding: gzip, deflate, br, zstd` / `accept-language: en-US,en;q=0.9` /
  `priority` / `referer` / `same-origin` / `cors` / `newrelic` / `?0` / `application/json, text/plain, */*`，
  还带 `https://checkout.ao.com/shoppingbasket.aspx`。也就是说这个 New Relic id 是**通用头表里的一个值**，
  跟 Casio 无关；而且这些头**复刻件早就有了**（`Gateways.cs` 里 `gzip, deflate, br, zstd`、
  `same-origin`、`priority` 全部命中）——**无可补**。
- **死路二（`productCode`，上一轮）**：通往 PayPal 3DS JWT 构造器，同样已有。
- **结论**：`_timestamp`/`_hash` 签名对**这轮仍未解出**，而且我两次选锚点的思路都错在同一处——
  拿"看起来很独特"的串当锚，却没先问它**是不是被所有店铺共用的字段**。记进 BLOCKERS。
- **转向的收获**：同一批引用里露出 `checkout.ao.com` 的**三个 checkout API**
  —— `/v2/app/contact`(0x14705D114)、`/v2/app/delivery`(0x14705D17C)、`/v2/app/payment`(0x14705D1E4)，
  加上 `https://ao.com`、`https://checkout.ao.com`、`/shoppingbasket.aspx`。
  **AO.com 是复刻件目录里没有的第五家店**（`ao.com` 全仓只在 `CardinalThreeDs.cs` 的主机检查里出现过一次）。
- **落码的克制**：`AoFlow` 只重写 `GetHomeAsync` 与 `FindProductAsync`——两条都是页面读取，有据可依；
  三个 `/v2/app/*` 的**请求体在镜像里一个字都没有**（这几个 URL 躺在按字母排序的池子里，
  邻居是别的店而不是它们自己的键），所以**不重写那三步**，让它们落到基类自己的拒绝上。
  `FlowWorkAuditTests` 的占位上限**停在 16 没动**——上一轮就是靠"不重写"绕开了加占位。
- **五处计数随事实移动**：目录 66→67、flow 文件 19→20、PARITY 的 66→67 与 36→37、VERDICT 状态行 66→67。
  脚本里第一次写错了比较（`findall` 对带组模式返回元组，我拿字符串去比），四份文档一个都没改上却报"found=1"——
  已改成按组取值。**这也是"数字对不对"和"改没改成"是两件事的活例子。**

### 五要素

- **改了什么**：新增 `replica/src/Cybersole.Stores/Flows/AoFlow.cs`、
  `replica/tests/Cybersole.Tests/AoFlowTests.cs`（6 条）；`Modules/Registry.cs` 注册；
  五处计数与两处注释；新增 `analysis/fix_r1313_counters.py`；NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter AoFlowTests` → 6/6；连同五处计数守卫 **33/33**；
  产物搜 `AoFlow` **1**、`shoppingbasket.aspx` **1**，尺寸 61,284,864 → **61,293,568**；
  `artifact_freshness.py` → `state: current`；`metrics_report.py` → 全部 exit 0；
  `mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**：目录 66 → **67**；套件 2611 → 见 METRICS 当前值（+6）。
- **证据等级**：Observation —— 六个 AO 地址、三个 API 路径、头构造器的十一个串、`ao.com` 在仓库的唯一出现。
  Unknown —— 三个 `/v2/app/*` 的请求体；`_timestamp`/`_hash` 签名方案。
- **还剩什么**：Casio 签名（锚点思路要换：**从 `AddToCart`/`SetAdyenPayment` 这类 Casio 特有步骤名出发**，
  而不是从看着独特的通用值出发）；AO 三个 checkout 体；Saucony 六步路径。
"""

BLOCK_ENTRY = """
---

## R1313 · Casio `_timestamp`/`_hash` 签名：两次锚点都选错了

- **尝试**：① `productCode`（R1312）→ 通往 **PayPal 3DS JWT 构造器**，与 Casio 无关，且复刻件已有；
  ② `UgAFUFFACQAEU1BSBAcB`（唯一 New Relic id）→ 通往**通用浏览器头构造器**，与 Casio 无关，且复刻件已有。
- **共同错因**：两次都是**拿"看起来很独特"的串当锚**，没有先问一句「这个串是不是所有店铺共用的」。
  New Relic id 唯一，但它是**每个请求都带的头值**；`productCode` 万能，但它是通用字段名。
- **正确方向（下轮）**：从 **Casio 特有的步骤名**出发——`<SetAdyenPayment>d__6`、`<SubmitAdyenOrder>d__7`、
  `<GetAdyenPaymentStatus>d__8` 的状态机类型，或 `casio_can_purchase` 这类**只有 Casio 有**的串。
- **状态**：签名方案**未解**，不当作已知写入任何实现。
"""

POINTER = """
---

## 第 1313 轮

- 签名线两次走死（`productCode` → PayPal JWT；`UgAFUFFACQAEU1BSBAcB` → 通用头构造器），共同错因是
  **拿通用值当锚**。下轮改从 Casio 特有步骤名出发。
- **AO.com 进目录**（第五家原本缺的店，66 → 67）：`AoFlow` 只实现 `GetHome`/`FindProduct`，
  三个 `/v2/app/{contact,delivery,payment}` **请求体未知所以不重写**，占位上限停在 16 没动。
- 产物搜 `AoFlow` 1 次，尺寸 61,293,568。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1313 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1313 \u8f6e')
append(BLOCKERS, BLOCK_ENTRY, 'R1313 \u00b7 Casio')
