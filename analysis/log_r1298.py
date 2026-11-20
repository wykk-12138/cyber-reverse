"""Log R1298: the power cut broke the branch ref, and the criteria audit that followed."""

import io

B = """
## R1298 —— 停电事故：**分支 ref 被写成 41 个 NUL**，已用 reflog 完整恢复

### 一、事故与症状

停电重启后 `git` 报 `fatal: your current branch appears to be broken`，`git rev-parse HEAD` 说
`ambiguous argument 'HEAD'`。逐层查：

| 检查 | 结果 |
|---|---|
| `.git/HEAD` 字节 | `72 65 66 3a 20 ...` = `ref: refs/heads/main\\n` —— **完好** |
| `.git/refs/heads/main` 长度 | 41 字节（看似正常） |
| `.git/refs/heads/main` **字节** | **41 个 `0x00`** ⇒ 停电瞬间文件系统写了零 |
| `.git/logs/HEAD` | **完好**，最后一条 `04f98d9a… → b2a7c5b1905eb1f79b38bc6d81d0f2b710b1af83` |

**关键教训**：`Get-Content` 显示成"一串空白"，长度 41 也像正常，只有 `ReadAllBytes` 才看得出全是 NUL。
**判文件是否损坏要看字节，不看渲染**（§2 第 4 条的同一条纪律）。

### 二、恢复

```
[IO.File]::WriteAllText(".git\\refs\\heads\\main", "b2a7c5b1905eb1f79b38bc6d81d0f2b710b1af83`n")
```

恢复后：`git log -3` 正常（`b2a7c5b` / `04f98d9` / `2cc6f5c`），`git rev-parse HEAD` 对上，
`git fsck` 只有 **dangling blob**（无害残留，与提交历史无关）。

**工作区完整性抽查**：`FarfetchFlow.cs` 11,433 B · `mutation-check.py` 54,733 B · `docs/METRICS.md` 31,459 B ·
`MUTATION_RESULT.json` 5,921,573 B · `.publish-aot/Cybersole.Ui.exe` **57,491,456 B** —— 全部在位。

### 三、IDA 重启（停电后）

`ida-mcp-doctor.ps1` + CUA 点掉 **2 个**模态框（这次是 `Proceed with unpacked base` 与 `.id0 修复 是(&Y)`，
第三个"库不一致"没有出现）⇒ `health: ok`、`hexrays_ready: true`。
但 **`strings_cache_ready: false`，`ida.py str` 仍报错**（与 R1287 同形：健康检查通过，字符串通道未就绪）。

### 四、判据 a–f 逐条自检（本轮主要产出）

| 判据 | 证据（全部来自 `docs/METRICS.md`） | 状态 |
|---|---|---|
| **a)** 类型级缺口→0；类型缺失→0 或分类；名字级三分类 | `types with scope misses` = **0**；`types absent` 15 = `renamed 13, out of scope 2, unimplemented 0, unclassified 0`；名字级 `missing 14` = **noise 12 + out of scope 2 + real gap 0** | **✅** |
| **b)** 剩余仅不可得文案且每条写明原因 | `copy: zones with a missing key` = **0**；`Stores/Flows` 的 24 条 `inferred` 全部带查证结论（R1290 共 41 行注释） | **✅** |
| **c)** 产物级对照可复算 | `descriptor 951 / types 215 / only-in-descriptors 137`；`datafiles 0 / 2`；`.pdata 277,120 ↔ 179,840 = 64.90%`；`section-mass 57.09%` —— 命令逐条写在 METRICS 里 | **✅** |
| **d)** claim 表每条有 authority + 命令 + gap_reason | `docs/METRIC_CLAIMS.md`（107 行）、`docs/PARITY_CLAIMS.md`（170 行）在；**尚未逐条抽验** | **待核** |
| **e)** 套件绿 + 变异全 fired + 数字同源 | 2468/0/0（metrics 自己的 filter）；变异 **59 fired / 0 decorative / 0 skipped**；`DocsConsistency\\|ParityDoc\\|CoreCoverage` 21/21 | **✅**（剩 `mutation-fit: staleness` 1 行待重跑） |
| **f)** 核心覆盖可复算 | store `flows 18 / steps 369 / placeholders **0** / provenance exit 0`；vendor `controls **True** / named 13 / missing 0`；captcha `markers absent 0/5`；payment `stages 9 / markers 0/5` | **✅** |

### 五、`missing 14` 的完整解释（本轮新查）

镜像里 `Cybersole.Models.EditValue\\`1,Cybersole.Core.HasMultiple_87!Getter` 一路到 `HasMultiple_101`，
同块还出现 `Value_100` —— **编号是全局实例序号**，`EditValue<T>` 被 AOT 实例化多次，每个实例的成员加后缀去重。
`bind_diff.py` 早就把它写成 `NOISE = ^(HasMultiple|Value)_\\d+$` 并分进 `noise` 桶，
是我第一次**没带 `--buckets`** 才只看到原始 `missing: 14`。

⇒ **判据 a 的 14 条没有一条是"未实现"**：12 条是 AOT 实例编号，2 条是 R702 裁决的范围外绑定。

### 六、唯一剩下的判据项

**d)** 需要抽验两张 claim 表的每条是否带 `authority` + 命令 + `gap_reason`。留作下一轮第一件事。

证据等级：Observation = ref 的 41 个 NUL、reflog 的两行、fsck 输出、五个文件的字节数、METRICS 全表、
`bind_diff.py --buckets` 的三行；Inference = 「NUL 由停电写入中断造成」；**Unknown** = `str` 通道何时恢复。
"""

V = """
---

## 第 1298 轮：停电损坏分支 ref 已恢复；判据 a–f 自检（a/b/c/e/f 达标，d 待抽验）

- `.git/refs/heads/main` 被写成 **41 个 NUL**；用 reflog 的 `b2a7c5b1905eb1f79b38bc6d81d0f2b710b1af83` 恢复，`fsck` 只有 dangling blob。
- **判据要看字节不看渲染**：`Get-Content` 显示空白、长度 41 都像正常。
- IDA 重启完成（2 个模态框），`health ok`，但 `ida.py str` 仍未就绪。
- 自检：a ✅（`missing 14 = noise 12 + out-of-scope 2 + real gap 0`）· b ✅（copy 缺口 0）· c ✅ · e ✅（59/59/0/0）· f ✅（store 0 占位 / vendor True / captcha 0-5 / payment 9）· **d 待抽验两张 claim 表**。
"""

H = """
## R1298 —— 停电后 git ref 恢复；判据自检 5/6 达标

Observation：
- `refs/heads/main` = 41×`0x00`（`ReadAllBytes` 才看得出）；reflog 末条 `04f98d9a → b2a7c5b1…`。
- 恢复后 `log -3` / `rev-parse HEAD` / `fsck` 全部正常；五个关键文件字节数在位（含 AOT 57,491,456 B）。
- IDA：2 模态框点掉，`health ok`，`str` 未就绪。
- 判据：a ✅（三分类 12/2/0）· b ✅ · c ✅ · e ✅（变异 59/59/0/0）· f ✅ · **d 待抽验**。

下轮第一件事：抽验 `docs/METRIC_CLAIMS.md` 与 `docs/PARITY_CLAIMS.md` 每条是否带 authority + 命令 + gap_reason；
其次重跑一次 mutation 消掉 `staleness` 那一行。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
