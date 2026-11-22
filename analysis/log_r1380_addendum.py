"""Record the claims-row slip, then hand the numbers to metrics."""

import io

VERDICT = 'replica/docs/VERDICT.md'

block = """
#### 补记：C8 那一行把 claims 审计弄挂了（R1380）

我把 `PARITY_CLAIMS.md` 的 C8 行改成了 **四格**，而表头是六列 —— `analysis/check_claims.py` 只收 `>= 6` 格的行，
于是它报 **claim rows: 21**，而独立计数是 22，`ClaimsCoverageTests` 立刻红：

```
Assert.Contains() Failure: Sub-string not found
```

**修法**：把该行恢复成**六格**（status / authority / command / gap_reason 各自归位），现在
`claim tables: 5、claim rows: 22`，两个守卫全绿。

**教训**：`PARITY_CLAIMS.md` 的表格是**机器读的**，不是散文 —— 改它等于改一个接口。
这和"锚点必须从源码复制"是同一族：**先看消费者怎么读，再改生产者怎么写。**
"""

text = io.open(VERDICT, encoding='utf-8').read()
if 'claim rows: 21' not in text:
    with io.open(VERDICT, 'a', encoding='utf-8', newline='') as handle:
        handle.write(block)
    print('appended the claims-row slip')
else:
    print('already recorded')
