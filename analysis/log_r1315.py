"""R1315 round record: the Casio reader has no signing, and a hash question about the build itself."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1315 轮：Casio 商品读取里没有签名——顺带撞见一个关于产物哈希的问题

- **顺着单引用点继续**：`casio_can_purchase` 的引用点落在 `sub_140954410`（2122 字节）。
  反编译读完，它是 **GraphQL 响应读取器**，十二个字面量全是响应键值：
  `data`(0x146FEA418)、`products`(0x147118348)、`items`(0x1470ABD58)、`name`(0x1470FEDF8)、
  `stock_status`(0x147163D10)、`IN_STOCK`(0x146DB5C90)、`casio_can_purchase`(0x146FC1DB0)、
  `price_range`(0x1471168F0)、`minimum_price`(0x1470C4148)、`final_price`(0x147034CF0)、
  `value`(0x14717CA98)、`image`(0x1470A0DC8)、`url`(0x147178B38)、`"true"`(0x147173DE8)、`"1"`(0x146AC4CC8)。
  **没有时间戳、没有哈希、没有密钥** —— 所以 `_timestamp`/`_hash` 这对不在商品读取路径上，
  它属于**下单/支付**那几步（`SetAdyenPayment` d__6、`SubmitAdyenOrder` d__7）。
- **两个像密钥的 blob 也没有代码引用**：`VgmotEs-…`(0x14348CB1C，43 字符，够 32 字节 base64url)
  与 `/0400F0sae66…`(0x1434B480C，长 base64) 在 `.text` 里**各 0 个引用点**。
  按 §4.5，0 引用不构成"没用"的证明，但**确实没法从这里跟进**。
- **顺带确认 R1312 的读取器是忠实的**：镜像比较 `casio_can_purchase` 与 `"true"` **和** `"1"` 两种拼法，
  我的 `CanBuy` 早就两种都收；价格走 `price_range.minimum_price.final_price.value` 四级路径，也一致。
  这两条现在都有测试钉住——**`"1"` 被"顺手清理"掉是一次行为改变**，注释里写了。
- **测试暴露了我自己的一处语义没写清**：`CanPurchase = ""` 时落到 `stock_status` 判定（`IN_STOCK`→true），
  我原本把它期望成 false。**空串是"店里没答这个属性"，不是"属性说不行"**，已改正并在用例里写明区别。

### 关于产物哈希的一个问题（重要，影响 §4.5 的仪器）

- 本轮只改了**测试**，`src` 一字未动。连发两次产物：**尺寸 61,294,592、sha256 `bcbee69f…`，两次逐字节相同**
  ——所以构建**现在是可复现的**。
- 但 R1314 那轮 `docs/METRICS.md` 记的是 `sha256 dab75acb…`，**尺寸同为 61,294,592**。
  同样的应用源码、同样的尺寸、不同的哈希。
- **不能解释的那个差异，我不编解释**。它意味着：**单凭哈希不同，不足以断定源码变了**——
  而 §4.5 的整套可达性判定正是建立在"改一处→哈希必变"之上。
  在查清之前，哈希差分只能读作"可能变了"，必须配一条独立的确认（类型名在不在、尺寸、行为测试）。
- 另外记一笔：R1314 的散文里我把产物尺寸写成 61,294,080，**比真实值少 512**（`docs/METRICS.md` 里的
  61294592 一直是对的）。散文数字与生成数字不一致时，以生成数字为准。

### 五要素

- **改了什么**：`tests/Cybersole.Tests/CasioGraphQLTests.cs`（+7 条：两种拼法的 Theory 六行、
  四级价格路径一条、空串语义）；`replica/docs/VERDICT.md` 与 `docs/BLOCKERS.md` 记录。
  **未改 `replica/src`**。
- **验证命令与输出**：`dotnet test --filter FullyQualifiedName~Casio` → **31/31**；
  连发两次产物 → 尺寸与 sha256 **完全相同**（61,294,592 / `bcbee69f…`）；
  `artifact_freshness.py` → `state: current`；`metrics_report.py` → 全部 exit 0；
  `mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**：套件 2617 → 见 METRICS 当前值（+7）；产物**未变**（只改测试）。
- **证据等级**：Observation —— 十五个字面量及其地址、两个 blob 的 0 引用、两次产物逐字节相同、
  R1314 记录的哈希与尺寸。Unknown —— `_timestamp`/`_hash` 属于哪一步；R1314 哈希差异的成因。
- **还剩什么**：Casio 签名（在下单/支付步骤上）；R1314 哈希差异待查；AO 三个 checkout 体；Saucony 六步路径。
"""

BLOCK_ENTRY = """
---

## R1315 · 产物哈希：两次相同，但与上一轮记录不同（未解）

- **实测**：本轮只改测试，`src` 未动。连续两次 `dotnet publish`（同一源码、同一参数）
  → 尺寸 **61,294,592**、sha256 **`bcbee69f45c4b84c…`**，两次**逐字节相同**。
- **矛盾点**：R1314 的 `docs/METRICS.md` 记录 `sha256 dab75acb1f4a2649…`，**尺寸同为 61,294,592**。
  同尺寸、不同哈希、源码相同。
- **影响**：§4.5 规定「改一处 → 重发 → 比 sha256」是判可达性的唯一可信仪器。
  如果同样的源码能给出不同哈希，那**哈希变化本身就不再是源码变化的充分证据**。
- **处置（在查清之前）**：哈希差分只读作「可能变了」，必须配一条独立确认
  （类型名是否在产物里、尺寸、以及行为测试）才能下结论。**不要**把单次哈希差异写成「代码被裁/被改」。
- **候选成因（未验证，不作为结论）**：发布目录不同（`.publish-aot` vs 新建目录）、
  或那次 metrics 读到的是另一个构建产物。两种都只要重跑一次就能排除，但本轮不做无据推测。
"""

POINTER = """
---

## 第 1315 轮

- Casio 商品读取器 `sub_140954410` 的十五个字面量全是 GraphQL 键值，**没有时间戳/哈希/密钥**——
  `_timestamp`/`_hash` 属于下单/支付步骤，不在读取路径上。
- 两个像密钥的 blob（`VgmotEs-…`、`/0400F0sae66…`）在 `.text` 里**各 0 引用点**，无法从那里跟进。
- 确认 R1312 读取器忠实：`casio_can_purchase` 接受 `"true"`/`"1"` 两种拼法，价格走四级路径，均已钉测试。
- **产物哈希问题**：两次连发逐字节相同（`bcbee69f…`），但与 R1314 记录的 `dab75acb…` 尺寸相同、哈希不同。
  在查清前，哈希差分只读作「可能变了」，需独立确认。见 BLOCKERS。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1315 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1315 \u8f6e')
append(BLOCKERS, BLOCK_ENTRY, 'R1315 \u00b7 \u4ea7\u7269\u54c8\u5e0c')
