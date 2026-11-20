"""Log R1297: AOT republished, mutation back to 59/59 green, and two stale reports fixed."""

import io

B = """
## R1297 —— 产物重新发布 + 变异回到 59/59 GREEN + 两处"陈旧"误报修正

### 一、AOT 重新发布（消掉"产物陈旧"）

```
dotnet publish src\\Cybersole.Ui -c Release -r win-x64 -o .publish-aot \\
       -p:PublishAot=true -p:UseSharedCompilation=false
→ publish_exit=0
→ artifact 57,491,456 bytes  14:15:16
```

发布时 `.publish-aot/Cybersole.Ui.exe` 从 **54.8 MB（07:00）** 换成 **57.49 MB（14:15）**。

### 二、变异重跑：`59/59, 0 decorative, 0 skipped, tree=GREEN`

上一轮 `tree=RED` 归因并行会话，这一轮同一命令给出 **GREEN** ⇒ 归因成立，测试树本身没问题。

### 三、两处"陈旧"报告，都是**工具误判**，不是产物问题

跑完变异后 METRICS 又报"17 个源文件比产物新（14,192 行）"。查下来：

| 事实 | 值 |
|---|---|
| 那 17 个文件的 mtime | 14:16–14:19，正是变异运行时段 |
| `of those, changed against HEAD` | **0** |
| `publish artifact state` | **`current`** |

⇒ **变异把每个目标文件改写再还原**，mtime 变了而字节没变。`artifact_freshness.py` 早在 **R1183**
就把这两件事分开了（`newer` vs `changed`），但 `metrics_report.py` 的**警告文案**只看 `newer`。

改：警告改为**只在 `changed != 0` 时**触发（R1297）。这是"修生成器，不修生成物"。

### 四、剩下那一条警告是**准确的**

```
**变异套件那一组数来自上一次运行，而它已经过期**：`1 -- tools/metrics_report.py differs from the run's manifest`
```

因为我在变异跑完之后**又改了 `tools/metrics_report.py`**（就是上面那个修正）。
**被测代码（`src/`、`tests/`）本轮没动**，所以变异结论仍然成立；下一轮开头跑一次变异即可让这行消失。
这里不代填、不删警告。

### 五、验证

| 项 | 结果 |
|---|---|
| `metrics_report.py` | **全部 exit 0** |
| 变异 | **59 fired / 0 decorative / 0 skipped / tree=GREEN**（`ran_at 14:25:51`） |
| AOT 产物 | 57,491,456 B，`state: current` |
| 伪陈旧警告 | 已修（改为按内容判定） |

证据等级：Observation = 发布字节数与时间、变异 JSON 四项、`changed against HEAD: 0`、`state: current`；
Inference = 「17 文件 mtime 来自变异改写」；**Unknown** = 并行会话在 `src/` 的改动意图（本轮未见其提交）。
"""

V = """
---

## 第 1297 轮：AOT 重发布 + 变异 59/59 GREEN + 两处陈旧误报

- 发布：57,491,456 B / 14:15:16；`.publish-aot` 由 54.8 MB 更新。
- 变异：**59 fired / 0 decorative / 0 skipped / tree=GREEN**（上轮 RED 确系并行会话）。
- 「17 文件比产物新」是**误报**：`changed against HEAD: 0`、`state: current`——变异改写后还原，mtime 变、字节不变。
  警告已改为按**内容**判定（R1297）；`artifact_freshness.py` 自 R1183 就分开统计，是 `metrics_report.py` 只读了 mtime 那格。
- 剩一条警告准确（本轮改了 `tools/metrics_report.py` 本身），下轮跑一次变异即消。
- `metrics_report.py` 全部 exit 0。
"""

H = """
## R1297 —— AOT 57,491,456 B；变异 59/59 GREEN；陈旧误报改为按内容判定

Observation：
- `publish_exit=0`，产物 57,491,456 B @14:15:16。
- `MUTATION_RESULT.json`：total=59 fired=59 decorative=0 skipped=0 tree=GREEN ran_at=14:25:51。
- `artifact_freshness.py`：`newer=17`、`lines=14192`、**`changed against HEAD: 0`**、**`state: current`**。
- `metrics_report.py` 全部 exit 0。

下轮：跑一次 `mutation-check.py` 消掉最后那条 manifest 警告（本轮改了 `tools/metrics_report.py`），
随后进入判据 a–f 的逐条自检清单。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
