"""R1323 record: the image sends two variants of the 3DS resolve mutation, and both are now present."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1323 轮：3DS 的 resolve 有两个变体，两份都在镜像里活着——先量、再落

- **先问"复刻件里有没有"，这次问对了**：`PayPalThreeDs.ResolveDocument` 从 R1149 就在。
  用 `analysis/compare_resolve.py` 一比，它**与镜像的 B 变体逐字节相同（10370 字符）** —— 不用改。
- **缺的是另一份**：`0x1470D7974` 的 **10262 字符**变体。两份**各自只有一个代码引用点**：
  - A（10262）← `sub_14110FDB0`（14458 字节），引用点 `0x141112BAF`
  - B（10370）← `sub_141113680`（15615 字节），引用点 `0x141117103`
  **两条路都是活的**，所以"哪份在用"这个问法本身就是错的 —— 答案是用两份。
- **差在哪，量出来了**：`difflib` 只有一个差异区，B 在 **offset 2890** 插入了 **108 字符**的一块字段
  （`authenticationProvider`、`cardBrandProcessed`、`dataOnlyIndicator`、`deviceDataCollectionBin…`）。
  相似度 0.995 —— 是"同一份文档的方言"，不是两份不同文档。
- **落码**：`ResolveDocumentWithoutProviderFields`（10262 逐字节，脚本生成而非手抄）+
  `DocumentFor(operationName, providerFields = true)`。**默认值保持原行为**，既有调用点一个都不用改；
  要短那份就显式传 `false`。测试钉三件事：两份长度、**插入点必须正好在 2890**（否则将来有人"整理"成一份就会红）、
  以及选择器对另外三个操作不受影响。
- **一个工具层的坑**：`get_bytes` 要 22 KB 时返回的形状变了（不再是数组首元素），直接 `res[0]` 抛 `KeyError`。
  改成 8 KiB 分块读就好了。**读大字符串要分块**，这条以前踩过、这次又踩了一次。

### 五要素

- **改了什么**：`PayPalThreeDs.cs`（新增 10262 字符变体 + `DocumentFor` 加变体参数）；
  `PayPalThreeDsTests.cs`（+3 条）；新增 `analysis/{diff_three_ds,compare_resolve,add_resolve_variant,verify_resolve_variant,add_resolve_tests}.py`；重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter PayPalThreeDsTests` → **29/29**；
  `compare_resolve.py` → `replica == B: True`；`verify_resolve_variant.py` → `identical: True`、`contains the provider block: False`；
  产物 `authenticationProvider` 命中 **1**（长那份有、短那份没有，1 就对了）；
  尺寸 61,347,840 → **61,368,320**；内嵌 `6e0c829fb8cd (is HEAD)`。
- **数字变化**：套件 2644 → 见 METRICS 当前值（+3）；产物 +20,480 字节。
- **证据等级**：Observation —— 两份文档的地址、长度、**各自单一引用点**、唯一差异区在 2890、逐字节一致。
  Inference —— 两个函数对应"两种方言"（正常流与带 provider 字段的流），函数名未解。
- **还剩什么**：`ThreeDsLookUpMutation` 877/905 与 `ThreeDsAuthenticateMutation` 837 也该同样量一遍
  （很可能也是方言对）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1323 轮

- **3DS resolve 有两个变体，两份都在镜像里活着**：A 10262（`sub_14110FDB0`）、B 10370（`sub_141113680`），
  各一个引用点。复刻件本来就有 B 且逐字节正确，这轮补上 A。
- 唯一差异：B 在 **offset 2890** 插入 **108 字符**的 provider/device-data 字段块，相似度 0.995 —— 是方言不是两份文档。
- `DocumentFor(operationName, providerFields = true)`：**默认不变**，要短那份显式传 `false`；测试钉住插入点。
- 工具坑：`get_bytes` 读 22 KB 时返回形状变化 → **读大字符串要 8 KiB 分块**。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1323 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1323 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'R1323' not in text:
    text = text.replace(
        '| `0x1470D7974` | 10846 | `ResolveThreeDsContingency` | 3DS 核心，需与 `PayPalThreeDs` 对齐后再落 |',
        '| `0x1470D7974` | **10262** | `ResolveThreeDsContingency`（无 provider 字段的方言） | **R1323 已落地**：`ResolveDocumentWithoutProviderFields` |')
    text = text.replace(
        '| `0x1470DC9BC` | 10958 | `ResolveThreeDsContingency`（第二份） | 与上面差 112 字符，先要判定哪份在用 |',
        '| `0x1470DC9BC` | **10370** | `ResolveThreeDsContingency`（带 provider 字段） | 早已在 `ResolveDocument`（R1149），R1323 确认逐字节一致 |')
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated for both variants')
