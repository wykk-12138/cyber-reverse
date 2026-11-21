"""R1340 addendum: the truncated metrics run and its re-run."""

import io

VERDICT = 'replica/docs/VERDICT.md'

ADDENDUM = """
### 第 1340 轮补充（度量重跑记录）

第一次 `metrics_report.py` 的完整套件只跑到 **486 通过** 就 `exit 1` —— 不是失败，是**跑到一半崩了**。
按 §2.6，「没跑成」既不算通过也不算失败，必须单列。当时机器可用内存 **4.7 GB**，还挂着两个 dotnet 进程（1.4 GB RSS）。

清掉残留 testhost/vstest 后重跑：**2708 通过 / 0 失败 / 0 跳过，全部命令 exit 0**。
**本轮结论以这次干净重跑为准**，第一次截断那次只作为资源压力的记录保留。
"""

text = io.open(VERDICT, encoding='utf-8').read()
if '第 1340 轮补充' not in text:
    io.open(VERDICT, 'a', encoding='utf-8', newline='').write(ADDENDUM)
    print('addendum appended')
else:
    print('already there')
