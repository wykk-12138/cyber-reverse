"""R1314 round record: the Casio GraphQL head is observed, and the search is a GET."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
BLOCKERS = 'docs/BLOCKERS.md'
ROADMAP = 'docs/REMAINING_REPLICATION_ROADMAP.md'

ROUND = """
---

## 第 1314 轮：换锚点立刻见效——Casio 的 GraphQL 头是实证的，而且搜索是 **GET**

- **上一轮记的教训照做了**：不再拿"看起来很独特"的通用值当锚，改用**只有 Casio 有**的串。
  `casio_image_url` 在 `.text` 里**只有一个引用点**（`0x1409546E0`→`sub_140954410`），
  而整份选择集尾部 `0x146A758CC` 也只有一个（`0x14095A121`→`sub_14095A090`）。
  单引用点就是"这是这家店专用"的直接证据。
- **`sub_14095A090` 的 MoveNext 里两次字符串拼接把整件事说完了**：
  ```
  sub_141CF62D0(&off_147197250, *(v1+208), &off_146A758C0)   // 头 + sku + 尾
  sub_141CF62D0(v5, &off_146B28A80, v6)                      // ... 再拼 "?query=" + 上面那串
  ```
  两个字面量解出来：
  - `0x147197250` **28 字符** `{products(filter:{sku:{in:["`
  - `0x146B28A80` **7 字符** `?query=`
- **三件事同时被纠正**：
  1. 上一轮标为 **Inference** 的「文档头」其实是**实证**的，而且**猜对了**——`sku:{in:[` 正是那个 `]` 逼出来的；
  2. 文档**没有 `query{...}` 外壳**，就是大括号本身（GraphQL 简写查询）；
  3. 传输是 **GET + `?query=`**，不是 POST 带 JSON 体——上一轮的做法是错的。
- **落码**：`CasioGraphQL` 增 `ObservedHead` / `QueryParameter` / `SearchUrl` / `EndpointFor`，
  `SearchDocument` 改成 `头 + sku + 尾`，`SearchAsync` 改 **GET**（`c.Http.GetAsync`），
  并把 `document` 参数真正接上（改 GET 后它一度变成无效参数——**无效的参数就是装饰**，接上才算数）。
- **顺手修的一个真错**：`SearchAsync` 对已含 `/graphql` 的 endpoint 又拼了一次 `Path`，
  得到 `/graphql/graphql`。测试用的是 TinyServer 的绝对地址，所以这条只有跑起来才看得见。
- **测试基建第二次 additive 扩展**：`TinyServer` 加 `RequestTargets`（原始 path+query）。
  上一轮加 `RequestHeaders` 是为了断言 bearer，这轮加 target 是为了断言 **GET 的载荷在查询串里**——
  `Requests` 只记 path，GET 没有 body，不记 target 就等于这条行为没有断言点。

### 五要素

- **改了什么**：`Flows/CasioGraphQL.cs`（头/参数常量、GET 化、endpoint 修正、document 接上）；
  `tests/Cybersole.Tests/CasioGraphQLTests.cs`（`TheSearchAsksByGetAndReadsTheAnswer` 改名并改断言）；
  `tests/Cybersole.Tests/Support/TinyServer.cs`（`RequestTargets`，additive）；
  新增 `analysis/fix_r1314_graphql.py`；NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter FullyQualifiedName~Casio` → **24/24**；
  产物搜 `{products(filter:{sku:{in:` **1**、`?query=` **1**、`CasioGraphQL` **1**、`casio_image_url` **1**；
  尺寸 61,293,568 → **61,294,080**；`artifact_freshness.py` → `state: current`；
  `metrics_report.py` → 全部 exit 0；`mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**：套件 2617 → 见 METRICS 当前值（本轮无新增用例，改了既有断言）；产物见上。
- **证据等级**：Observation —— 两个字面量及地址、两次拼接调用、单引用点、GET 化的四串命中。
  Inference —— 拼接顺序即 `头 + sku + 尾`（两次 concat 的实参顺序推出）。Unknown —— `_timestamp`/`_hash` 签名仍未解。
- **还剩什么**：Casio 签名；Casio 其余步骤；AO 三个 checkout 体；Saucony 六步路径。
"""

BLOCK_UPDATE = """
---

## R1314 · 锚点方法论的修正（替代 R1313 那条）

- **R1313 记的错因是「拿通用值当锚」，本轮验证了正解**：用**只有这家店有**的串。
  判据不是"看起来独特"，而是**在 `.text` 里只有一个引用点**：
  `casio_image_url` → 1 处，选择集尾部 → 1 处；而 `productCode` 有 6 处、New Relic id 有 9 处。
- **可直接复用**：`disp32_scan_any.py <obj_va>` 的输出行数就是判据。行数 = 1，锚点是专用的；行数多，
  那是通用值，别用。
- **`_timestamp`/`_hash`**：仍未解，仍未写入任何实现。
"""

POINTER = """
---

## 第 1314 轮

- 换锚点（只认单引用点）立刻见效：`sub_14095A090` 的 MoveNext 两次拼接暴露了 GraphQL 文档头
  `{products(filter:{sku:{in:["`(0x147197250, 28 字符) 与 `?query=`(0x146B28A80)。
- 三处纠正：上一轮的 Inference 变 Observation 且**猜对了**；文档无 `query{}` 外壳；**搜索是 GET 不是 POST**。
- `CasioGraphQL` GET 化 + endpoint 双拼 `/graphql/graphql` 修正 + `document` 参数接上（无效参数即装饰）。
- `TinyServer` 加 `RequestTargets`（additive）：GET 的载荷在查询串里，不记 target 就没有断言点。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1314 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1314 \u8f6e')
append(BLOCKERS, BLOCK_UPDATE, 'R1314 \u00b7 \u951a\u70b9\u65b9\u6cd5\u8bba')
