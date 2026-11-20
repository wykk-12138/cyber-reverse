"""R1306 round record for VERDICT.md and HANDOFF.md (UTF-8, append-only)."""
import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1306 轮：Unzer 剩下两项各十一行与十句——都解出来了

- **`0x14094a870` 全文十一行**：
  `s.IndexOf("unzer.com", 0, s.Length, OrdinalIgnoreCase) >= 0 || s.IndexOf("heidelpay", 0, s.Length, OrdinalIgnoreCase) >= 0`。
  `sub_141CFAD70` 的第 5 参是 `StringComparison.OrdinalIgnoreCase`，两个针是 `0x147178230`(`unzer.com`) 与
  `0x147046530`(`heidelpay`，Unzer 改名前的集团名)。**这就是「URL 谓词」的全部**，落成 `IsUnzerThreeDsUrl`。
- **`qword_1472c65a0+8` 不是哈希表**：`0x1472c65a0` 处那几格 `0xFEC6xxxx` 看着像哈希，但 `sub_14094AB00`
  暴露了真相——它是那个静态的**懒初始化器**：`sub_143028DA0(&unk_145DDB978, 10)` 分配十元 `string[]`，
  然后往 `v0[2]..v0[11]`（即元素 0..9，越过对象头）逐个塞冻结串，最后 `sub_143028E70(qword_1472C65A0+8, v0)`。
  十个串解出来全是「支付失败」的说法：`declined`、`issue processing your payment`、`was declined`、
  `not authorized`、**`not authorised`**、`refused`、`insufficient`、`invalid card`、`card error`、`payment error`。
  **英美两种拼写都在**，这正是它作为「文本包含任一即终态」集合的指纹。
- 该静态被 10 个函数引用，全在 `0x14094/0x14095` 的 Unzer 邻域——与「多个状态函数共用一张终态表」一致。
- **落码**：`TerminalPhrases`（十条，逐条带地址）、`IsTerminalFailure`（大小写不敏感，标 Inference）、
  `IsUnzerThreeDsUrl`；并接进 `RunUnzerThreeDsAsync` 起点——**页面说 declined 就此结束，不再跟跳**，
  落 `unzer.terminal` 并发一条 `error` 事件。此前这个方法在末尾无条件 `Success(landedUrl)`。
- **测试 19 条**里最能说明问题的两对：`not authorized` / `not authorised` 都在表里；
  同一句话大小写成 `DECLINED` 仍判终态，而 `Payment successful` 不判。

### 五要素

- **改了什么**：`Gateways.cs`（新增三成员 + 在 `RunUnzerThreeDsAsync` 起点接入 + Unzer 文档改写）、
  新增 `tests/Cybersole.Tests/UnzerThreeDsDecisionTests.cs`（19 条）、三处文档口径纠正、
  NativeAOT 重发布、`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter UnzerThreeDsDecisionTests` → **19/19**；
  `dotnet test --filter FullyQualifiedName~Unzer` → **24/24**（既有 Unzer 用例无回归）；
  `artifact_freshness.py` → `state: current`；`metrics_report.py` → 全部 exit 0；
  `mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**（均引 `docs/METRICS.md`）：套件 `2543/0/0` → 见 METRICS 当前值（+19）；
  产物 `61,246,976` → **`61,248,512`** 字节。
- **证据等级**：Observation —— `0x14094a870` 的十一家指令与两个针地址、`sub_14094AB00` 的十次赋值与
  `qword_1472C65A0+8` 的写入、十个终态串及其地址。Inference —— 终态扫描的比较模式（谓词那处是
  `OrdinalIgnoreCase`，数组扫描的调用未解，取同样的大小写不敏感）。Unknown —— 终态表在哪个状态函数里被
  逐条比对（10 个引用者只确认了共用，未逐个反编译）。
- **还剩什么**：ACS 各处理器方法体；Komoju 两个请求体的目标 URL；23 条 live-capture `inferred`；
  33 条店铺长尾 + 77 条支付长尾。**路线图上 4 处「已定位但未穷举的静态 Unknown」至此全部结案**。
"""

POINTER = """
---

## 第 1306 轮

- 路线图那 4 处静态 `Unknown` 的最后两项（Unzer）已结案：`0x14094a870` 是两个 `IndexOf(OrdinalIgnoreCase)`
  （`unzer.com`/`heidelpay`）；`qword_1472c65a0+8` 不是哈希表，是 `sub_14094AB00` 懒建的十元 `string[]` 失败措辞表。
- 已落成 `IsUnzerThreeDsUrl` / `TerminalPhrases` / `IsTerminalFailure`，并在 `RunUnzerThreeDsAsync` 起点接入
  （页面说 declined 就结束，不再跟跳）。
- 见 `replica/docs/VERDICT.md` 第 1306 轮。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1306 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1306 \u8f6e')
