"""Log R1289: what the eight inferred literals turned out to be."""

import io

B = """
## R1289 —— `StoreFlow`(10) + `MagentoFlow`(6) 的 `inferred` 逐条查证：**1 命中 / 7 零命中**

### 一、查法

脚本 `analysis/check_inferred_literals.py`：从两文件的 `inferred` 行抽出路径/字面量，
逐个在 **324,901 条**的全量字符串 dump 里查（正向判据可靠）。

| 字面量 | 结果 |
|---|---|
| `/rest/V1` | **命中 `146AB72A4`** |
| `/discount/` · `/api/payments/` · `/checkout/complete` · `/account/recover` | 0 命中 |
| `/rest/V1/carts/mine/totals` · `/account/verify` · `/collections/new-releases` | 0 命中 |

### 二、结论要按 R1266 读，不能按直觉读

**`/rest/V1` 命中** ⇒ Magento 的 REST 前缀是镜像字面量，可以升为实证（地址如上）。

**其余 7 条 0 命中 ≠ 镜像里没有**。R1266 已经用哈希差分证明过：NativeAOT 把一部分串存成**逐字节搜不到的形态**
（`Process3DSAsync` 那四个字面量就是活证据）。所以 0 命中的正确读法是 **unknown**，
写进代码的也只能是「查过了、0 命中」，不能写成「镜像里没有」。

### 三、改了 13 处注释（不是台账，是把查证结果写在使用点上）

两个文件里每条 `inferred: no image evidence` 后面追加：

```
; 0 hits in the 324,901-entry dump; R1266: absence carries no information
```

`/rest/V1` 那条追加的是 `present at 146AB72A4`。**原标记短语保持不变**——
`EndpointEvidenceRatchetTests` 按短语绑行，删了它会红（该测试是在防"未背书路径没有说明"，不是防措辞）。
共标注 `StoreFlow` 8 行、`MagentoFlow` 5 行。

### 四、验证

`EndpointEvidenceRatchet|Magento|StoreFlow` **34/34**；全量 **2478 通过 / 0 失败 / 2 跳过 / 2480**。

### 五、这条队列还剩多少

`inferred` 分布（本轮前的计数）：`GoatFlow` 14（已查完，无可核销）· `StoreFlow` 10（本轮）·
`MagentoFlow` 6（本轮）· 其余 9 个文件合计 22。
⇒ **剩下的 22 处按同一脚本再跑一轮即可**，能命中的升为实证，不能的标注 0 命中。
"""

V = """
---

## 第 1289 轮：StoreFlow + MagentoFlow 的 inferred 查证（1 命中 / 7 零命中）

- `/rest/V1` 命中 `146AB72A4`（可升实证）；其余 7 条 0 命中。
- **按 R1266，0 命中读作 unknown，不是"不存在"**——注释里也只写"查过了、0 命中"。
- 13 处注释追加查证结论，原 `inferred: no image evidence` 短语保留（ratchet 按短语绑行）。
- 全量 **2478/0/2/2480**。
"""

H = """
## R1289 —— inferred 查证：StoreFlow/MagentoFlow（1 命中 / 7 零命中）；全量 2478/0/2/2480

Observation：
- `/rest/V1` → `146AB72A4`；`/discount/`、`/api/payments/`、`/checkout/complete`、`/account/recover`、
  `/rest/V1/carts/mine/totals`、`/account/verify`、`/collections/new-releases` → 0 命中。
- 13 处注释已标注（StoreFlow 8 / MagentoFlow 5），原标记短语保留。
- 全量 2478/0/2/2480。

下轮：剩 9 个文件共 22 处 inferred，用同一脚本 `check_inferred_literals.py` 扩到全目录再跑一轮。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
