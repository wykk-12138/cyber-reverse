"""R1357 record: the cart block posts by hash, not by document — plus the recovery from the OOM crash."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1357 轮：`GetCartCookie` 那一族**不发文档，发 GraphQL 哈希** —— 顺带一次 OOM 崩溃的完整恢复

- **名字指向处理器，处理器说清了机制**：`GetCartCookie` 的字符串（`0x146D9D6BC`）头地址形式 → `sub_14088BB80`（47 行伪代码），
  它带的字面量里有两个 **64 位十六进制串**，而同一个函数还命名了三个头：
  ```
  x-graphql-hash        83c4b10c99a6f6c89abf7e84f83d5dc6360f8627eb2b70c7eb4b12590c6f1950
                        b613893783ae3da73f38b5f93a9a59ccbaa7f131a209cac92634a93d06f06866
  x-graphql-query-name
  x-header-id
  ```
  旁边还有 `Getting session`、`StatusInfo` 与整套浏览器头。**所以这一族按哈希投递持久化查询** ——
  这解释了为什么它们的发送方**既无主机也无路径**：路径在别处，查询本身也不在 body 里。
- **两个哈希、三个操作，配对不明** → **只实现机制，不替它们配对**：
  `GraphQlHashQueries.SendAsync` 接受调用方给的哈希（有哈希则头带哈希、body 只留变量；无哈希则退回发文档）。
  **发错哈希比不发更糟**，这条写进了类注释。
- **落码**：`GraphQlHashQueries`（3 份文档 74/490/3520 + 三个头名 + 两个观测哈希 + Envelope + SendAsync），
  接进 `StoreFlow.GetCartAsync`（`graphqlHash.origin` 触发）。
- **一次 OOM 崩溃与恢复（值得记）**：上一轮 `ilc` 以 `0xC0000409` 崩掉、整机内存耗尽重启。
  恢复步骤：① 清掉 `src/Cybersole.Ui/obj/Release/net8.0/win-x64/native`（崩溃留下的**损坏 .obj** 会让链接器报 `LNK1136`）；
  ② 重发；③ IDA 起三个模态框（**加载现有** → **Proceed with unpacked base** → **Repair** → 确定）。
- **产物**：`query GetCart {` 与 `query GetCartCookie {` **UTF-16 与 ascii 各命中 1**；`x-graphql-hash` **ascii 命中 1、utf16 0**；
  尺寸 62,095,168 → **61,917,184**（**变小** —— 因为这一版还顺带重算了别的，尺寸不是单调的，按 §4.5 不作判据）。

### 五要素

- **改了什么**：新增 `Flows/GraphQlHashQueries.cs`、`tests/GraphQlHashQueriesTests.cs`（7 条）；
  `StoreFlow.GetCartAsync` 加分支；新增 4 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`GraphQlHashQueriesTests` → **7/7**；`StoreFlow` 相关 → **21/21**；
  `operation_gap.py` → 覆盖 **43/65**（缺 22）；`orphan_documents.py` → 0；
  产物三串命中（2/2/ascii-1）；mutation **59 fired / 0 / 0 / GREEN**；扫描 56,479 文件 0 命中。
- **数字变化**：覆盖 40 → **43**（GetCartCookie / GetProductInventory / GetCart 三个）；缺 25 → **22**；套件 +7。
- **证据等级**：Observation —— 处理器里两个 64 位哈希与三个头名同处一函数、三份文档的长度、产物命中。
  Unknown —— 两个哈希与三个操作的**配对**（未成立，故不指定）。
- **还剩什么**：22 个 —— `CreditCard`(2867)、`SignInAsGuest` 等五份、`addToCartByChannel`(2271)、
  `updateShipAddress`(140)/`updateMyPaymentWithActions`(401)、Unknown 六份、B 块其余、两方言、
  浏览器侧结账面、`/cartApi/checkout` 归属、`AddressInput`、AO 三个体、Saucony 六步。
"""

POINTER = """
---

## 第 1357 轮

- **`GetCartCookie` 一族发的是 GraphQL 哈希，不是文档**：处理器 `sub_14088BB80` 里有
  `x-graphql-hash` / `x-graphql-query-name` / `x-header-id` 与两个 64 位十六进制值。
  **这解释了它们为什么既无主机也无路径。**
- 两个哈希、三个操作 → **配对不成立，只实现机制**（`GraphQlHashQueries`，哈希由调用方给；无哈希退回发文档）。
- **OOM 崩溃恢复四步**：清 `obj/.../win-x64/native`（损坏 .obj 会 `LNK1136`）→ 重发 →
  IDA 三模态（加载现有 / Proceed with unpacked base / Repair）→ `health ok`。
- 覆盖 40 → **43/65**，缺 25 → **22**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1357 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1357 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'GraphQlHashQueries' not in text:
    text += """
## 按哈希投递的一族（R1357）

`sub_14088BB80`（`GetCartCookie` 名字的引用者）带：

```
x-graphql-hash          83c4b10c99a6f6c89abf7e84f83d5dc6360f8627eb2b70c7eb4b12590c6f1950
                        b613893783ae3da73f38b5f93a9a59ccbaa7f131a209cac92634a93d06f06866
x-graphql-query-name    x-header-id    Getting session    StatusInfo
```

| 操作 | 文档长度 | 地址 |
|---|---|---|
| `GetCartCookie` | 74 | 0x147120B5C |
| `GetProductInventory` | 490 | 0x147120C0C |
| `GetCart` | 3520 | 0x14711EFC4 |

**两个哈希与三个操作的配对未成立** —— 实现里哈希一律由调用方给。见 `Flows/GraphQlHashQueries.cs`。
"""
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')

note = """
## OOM 崩溃后的发布恢复（R1357 实测）

`ilc` 若以 `0xC0000409` 崩掉，会留下**损坏的 `.obj`**，之后每次链接都报 `LNK1136: 无效或损坏的文件`：

```
Remove-Item -Recurse -Force replica\\src\\Cybersole.Ui\\obj\\Release\\net8.0\\win-x64\\native
```

再重发即可。**内存必须留足**（实测 4.4 GB 时崩溃，16 GB 时成功）。
"""

text = io.open(BLOCKERS, encoding='utf-8').read()
if 'OOM 崩溃后的发布恢复' not in text:
    with io.open(BLOCKERS, 'a', encoding='utf-8', newline='') as fh:
        fh.write(note)
    print('BLOCKERS got the OOM recovery note')
