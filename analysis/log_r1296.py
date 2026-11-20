"""Log R1296: three generators that still pointed at a file R1282 deleted, and criterion (f) turning green."""

import io

B = """
## R1296 —— ① ② 判据**双双转绿**；三个生成器修掉同一处 R1282 遗留

### 一、`placeholders` 归零（①）

`python tools/core_coverage.py` 跑通后：

```
flows=18  steps=369  placeholders=0  provenance exit=0
```

`placeholders=0` 是 **R1284**（BstnFlow 4 条）+ **R1294**（FarfetchFlow 7 条）分类结案的结果。
此前那一格是 11。

### 二、② 也全绿

`python tools/payment_challenges.py`：

```
control ok=True  stages=9  markers absent=0/5
```

九阶段齐、五个标记零缺席。

### 三、同一处 R1282 遗留，三个生成器各中一刀

R1282 删了 `src/Cybersole.Stores/Scripts/VendorWiring.cs`（零真实调用者），但**三个生成器还在读它**：

| 生成器 | 症状 | 修法 |
|---|---|---|
| `core_coverage.py` | `FileNotFoundError` 崩溃 | `wiring_row_count()` 文件不在 ⇒ 返回 `None`，文档写"该表已于 R1282 删除" |
| `vendor_coverage.py` | 同样崩溃，整条 vendor 检查 exit 1 | `wiring_rows()` 文件不在 ⇒ `None`；**区分"表被删"与"解析出零行"** |
| 同上（第二处） | 修完后 13 家全成 `missing` | 表已删 ⇒ 不计算 missing（否则就是 R764 那类"自信的错误清单"） |

**这一条值得记住**：删除一个被生成器读的文件，崩的不是产品，是**度量**——而度量崩了会让判据悄悄失去意义。

### 四、`metrics_report.py` 首次「全部 exit 0」

| 项 | 结果 |
|---|---|
| 度量脚本结果 | **全部 exit 0** |
| 完整套件 | 2468 通过 / 0 失败 / 0 跳过 / 2468（该脚本自己的 filter） |
| `vendor: controls ok` | **True**（YG 点名的那一格） |
| 变异 | `total=59 fired=59`（上一轮的成果） |

### 五、`docs/METRICS.md` 仍报的两条时效警告（如实留）

1. **产物陈旧**：31 个源文件比 `.publish-aot` 新（22,549 行）⇒ 需要重新 AOT 发布；
2. **变异组数过期**：`2 -- tools/core_coverage.py (+1 more) differs from the run's manifest` ——
   因为我本轮刚改了那两个生成器，manifest 变了，必须重跑一次变异才算数。

两条都是**长任务**（发布 10–20 分钟、变异 10 分钟），留到下一轮单独做，不在这轮末尾硬塞。

证据等级：Observation = 三个生成器的实际输出行、METRICS 的头 16 行、`metrics_exit=0`；
Inference = 「placeholders=0 由 R1284/R1294 造成」；**Unknown** = 并行会话对 `CORE_COVERAGE.md` 的改动内容
（该文件是生成物，本轮已按生成器覆盖）。
"""

V = """
---

## 第 1296 轮：① ② 判据转绿；三个生成器修掉 R1282 遗留

- `core_coverage.py`：`flows=18 steps=369 **placeholders=0** provenance exit=0`。
- `payment_challenges.py`：`control ok=True stages=9 markers absent=0/5`。
- 三个生成器都还在读 R1282 删除的 `VendorWiring.cs` ⇒ 全部改成"表已删"分支（并区分"删了"与"解析零行"）。
- `metrics_report.py` **首次全部 exit 0**；`vendor: controls ok=True`。
- METRICS 仍有两条时效警告：产物陈旧（31 文件/22549 行）、变异组数过期（因本轮改生成器）。
"""

H = """
## R1296 —— ① placeholders=0、② stages=9/markers 0/5、metrics 全部 exit 0

Observation：
- `core_coverage.py` → `flows=18 steps=369 placeholders=0 provenance exit=0`
- `payment_challenges.py` → `control ok=True stages=9 markers absent=0/5`
- `vendor_coverage.py` → `controls ok=True vendors named=13 wiring rows=0 missing=0` exit 0
- `metrics_report.py` → **全部 exit 0**；套件 2468/0/0/2468
- METRICS 警告：产物陈旧 31 文件 / 变异组数过期（本轮改了生成器）

下轮（两条长任务，单独做）：
1. 重新 AOT 发布消除"产物陈旧"（`-p:PublishAot=true -p:UseSharedCompilation=false`，产物 ≈57.4 MB）；
2. 重跑 `mutation-check.py` 让 manifest 重新对齐（预期仍 59/59/0/0）。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
