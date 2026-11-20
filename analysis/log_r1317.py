"""R1317 round record: three dead ends on Casio, and one silent fall-through made visible."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1317 轮：Casio 连撞三次都是"复刻件已经更通用地做了"——于是去修一个我自己留下的哑路径

- **第三次找签名，又没找到**。这轮把 `casioid` 的两个引用点（`sub_14094AF90` 187 字节查表、
  `sub_140952790` 893 字节、`casio_dob` 的 713 字节）都读了：893 字节那个是**验证码提取器**
  （`>\\s*?(\\d{6})\\s*?`、`Verification code information`、`code`），713 与 187 是查表。
  **仍然没有时间戳/哈希/密钥**。
- **而且验证码这条也不用做**：复刻件的 `AycdInboxClient.VerificationCodeExtractor` 是**带打分的通用提取器**
  （强/弱关键词、`\\d{4,8}`、窗口加权、金额/订单号排除），比镜像那条单一正则在覆盖面上更强。
  再补一条 Casio 专用正则**只会更差**。
- **三次尝试的共同教训（这次是第三条）**：在 Casio 上找东西，我连续三次得出"复刻件已经做了，而且更通用"。
  这不是巧合——**说明这个项目的通用层已经比镜像那家店的专用实现更宽**。
  下轮起改判断顺序：先问「通用层是否已覆盖这家店的特殊写法」，再决定要不要为某家店加专用分支。
- **签名项就此定案为 Unknown，并写清重开条件**：`_timestamp`/`_hash` 是**元数据里的字段名**（无代码引用），
  值由某个签名辅助方法产出，而**它没有 Casio 独有的字面量可锚**。
  重开条件二选一：① 找到 Casio 下单/支付端点的**专用字面量**（如某条只有 Casio 用的路径）；
  ② 一次实机抓包。**在此之前不再重复这三次尝试。**
- **改的东西**：R1312/R1314 我把 GraphQL 分支接进了 `CasioFlow.FindProductAsync`，
  但它要 `casio.sku`，而**这条流程里没有任何地方会设它**（Magento 商品 URL 带的是 `url_key` 不是 sku）。
  也就是说那两条路径**在实跑里永远不触发**——我造了一段不可达的代码，和 R1310 那次裁剪是同一个毛病的另一种形态。
  现在：无 sku 时**明确发一条事件并落 `casio.skuMissing`**，有 sku 时清掉该标记。
  **"分支没跑"和"分支跑了但没结果"从此可区分**，不再都长得像"从页面读到了商品"。

### 五要素

- **改了什么**：`RetailFlows.cs`（`CasioFlow.FindProductAsync` 的 sku 分支显性化）；
  `CasioGraphQLTests.cs`（+2 条：无 sku 时发事件/单请求、有 sku 时清标记）；三份文档记录。
  NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter FullyQualifiedName~Casio` → **33/33**；
  `artifact_freshness.py` → 内嵌 `a519f73b2b76 (is HEAD)`、尺寸 61,295,104、sha256 `3c832881…`；
  `metrics_report.py` → 全部 exit 0；`mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**：套件 2624 → 见 METRICS 当前值（+2）；产物 61,294,592 → 61,295,104。
- **证据等级**：Observation —— 三个函数的字面量、验证码提取器的通用实现、sku 无来源。
  Unknown —— `_timestamp`/`_hash`（附重开条件）。
- **还剩什么**：Casio 签名（按上述条件重开）；AO 三个 checkout 体；Saucony 六步路径。
"""

BLOCK_ENTRY = """
---

## R1317 · Casio `_timestamp`/`_hash`：定案为 Unknown，附重开条件

- **三条已排除的路径**（都可复算）：
  1. 商品读取 `sub_140954410`：十五个字面量全是 GraphQL 响应键值，无时间/哈希/密钥；
  2. `casioid` 的两个引用点 `sub_14094AF90`(187B) / `sub_140952790`(893B，验证码提取器) 与 `casio_dob` 的
     `sub_140948FA0`(713B)：均无签名逻辑；
  3. 两个像密钥的 blob（`VgmotEs-…`、`/0400F0sae66…`）：`.text` 里 0 引用点，无法跟进。
- **结构性原因**：`_timestamp`/`_hash` 是**元数据字段名**，代码里没有它们的字符串；
  产出它们的辅助方法**没有 Casio 独有的字面量**可作单引用锚。
- **重开条件**（满足任一才再查）：
  ① 找到一条**只有 Casio 用**的下单/支付端点字面量（当作锚）；
  ② 一次实机抓包，直接看报文里 `_timestamp`/`_hash` 怎么算。
- **在此之前**：不再重复上面三次尝试，也不把任何"看起来像签名"的 blob 写进实现。
"""

POINTER = """
---

## 第 1317 轮

- Casio 三连空手（且三次都是"复刻件已更通用地做了"：验证码提取器比镜像那条正则更强）。
  **判断顺序改为**：先问通用层是否已覆盖这家店的特殊写法，再决定要不要加专用分支。
- `_timestamp`/`_hash` **定案 Unknown**，附两个重开条件（专用端点字面量 / 实机抓包）。见 BLOCKERS。
- 修了自己留下的哑路径：`CasioFlow.FindProductAsync` 的 GraphQL 分支需要 `casio.sku`，而**没有任何代码设它**
  → 实跑永不触发。现在无 sku 时发事件并落 `casio.skuMissing`，"分支没跑"与"跑了没结果"可区分。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1317 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1317 \u8f6e')
append(BLOCKERS, BLOCK_ENTRY, 'R1317 \u00b7 Casio `_timestamp`')
