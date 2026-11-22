"""R1376 addendum: the first mutation run reported RED and the second GREEN; record both and the reason."""

import io

VERDICT = 'replica/docs/VERDICT.md'

block = """
#### 补记：变异首跑 RED、复跑 GREEN（R1376）

首跑 `tree: RED`，trx 里失败的是**两个全树扫描型守卫**：

```
Cybersole.Tests.BindScopeGuardTests.ScopeMissesStayAtZeroAndTheExaminedSetReconciles
Cybersole.Tests.ShapeAuditGuardTests.NullableReturningPublicMethodsAreNotReportedAsMissing
```

单独跑这两个类 → **4/4 通过（9 秒）**；完整变异复跑 → **`restored tree: GREEN`**、零 FAILED。

**成因**：这两个守卫**扫全树文件**，而变异器**正在逐文件改/还原**；并发与负载下它们会读到"瞬时被改过的文件"。
**结论**：不是回归，是**扫描型守卫与变异器的结构性冲突**；**记录两个用例名 + 两次结果**，不掩盖首跑。
（与 R1191 记的"非零退出但零失败 = 跑没跑完"是同一族问题：**标签必须能区分"坏"与"没跑完"**。）
"""

text = io.open(VERDICT, encoding='utf-8').read()
if 'BindScopeGuardTests.ScopeMissesStayAtZeroAndTheExaminedSetReconciles' not in text:
    with io.open(VERDICT, 'a', encoding='utf-8', newline='') as handle:
        handle.write(block)
    print('appended the flake note')
else:
    print('already recorded')
