# R433 裁决（YG 口径）

> 已核对：`bind_scope.py` = **4**、`bind_diff.py --buckets` = **16**、`shape_audit.py` = **275**、
> 套件 = **1607 通过 / 0 失败 / 2 跳过（25 s）**。你报的四个数**全部正确**。
> 你没有擅改数字、把待决项单列出来 —— 这是对的，继续这么做。

---

## 0. 三条主裁决

### 裁决 1：陈旧数字一次改齐，但**改法要变**（消灭漂移源）

不要再把数字硬编码进各文档。做法：

1. 新建 `replica/tools/metrics_report.py`：单进程依次跑 `bind_diff --buckets`、`bind_scope`、`shape_audit`、
   `copy_audit_report`、`backlog_report`，把结果写进 **`docs/METRICS.md`**（带生成时间与逐条命令）。
   文件头必须写：「为什么现有不够用：五个度量脚本输出格式各不相同，需要一个**单一事实源**，否则每份文档各写一套数字。」
2. 所有**当前状态类**文档（`AGENTS.md §4`、`docs/GOAL.md` 判据 a、`docs/HANDOFF.md`、`docs/COPY_QUEUE.md` 头部、
   `replica/docs/SESSION_STATE.md`、`replica/docs/DEVIATIONS.md`）把具体数字替换为
   **`见 docs/METRICS.md（python tools/metrics_report.py）`**，只在必须给量级的地方保留一行"当前值"并注明生成时间。
3. `replica/docs/VERDICT.md` **不动** —— 那是按轮次的历史记录，改它等于篡改。

> 这样以后任何人问"现在是多少"，答案只有一个来源；数字漂移从此是生成问题，不是纪律问题。

### 裁决 2：函数级对照走 **IDA 两侧**，不装 Ghidra（新增选项 F）

- 你已经有两条现成的链：原版 `13337`、复刻件 `13338`（**带 PDB 符号**）。
- 新建 `analysis/func_compare.py`（文件头写：「rea 的 native provider 全部 unavailable，且 REA_IDA_MCP_CONFIG
  只认 legacy 工具名；本机唯一现成的双实例通道就是 IDA 直连，故不引入 Ghidra 这第三套口径。」），做：
  1. 从 13337 导 `addr<TAB>size<TAB>name`（原版，几乎全 `sub_*`）；
  2. 从 13338 导同样格式（复刻件，带 PDB 名字）；
  3. 输出：两侧函数总数、可命名函数数、**绑定表成员在复刻件侧的命中率**、差集清单（分页）。
- claim **C6 / C7 / C9** 改为：
  - `Observation`：函数数量与符号可见性对照（附上述命令）；
  - `Unknown`：伪代码级逐函数等价 —— 明确写「需要伪代码对照，当前两实例只做清单对照」。
- **Ghidra 留作后手**：只有当某条 claim 必须"伪代码级"证据时才装，装之前先说明它要解决哪一条具体 claim。

### 裁决 3：判据 d 采用**双轨制**，每条 claim 必须带 `authority`

在 `docs/PARITY_CLAIMS.md` 每条 claim 上补三列：

| 列 | 取值 |
|---|---|
| `authority` | `tool-evidence` / `manual-from-command` / `unknown` |
| `command` | 能重算出这条结论的命令（`unknown` 可为空） |
| `gap_reason` | 只有 `unknown` 必填：缺哪一类证据能解 |

判据 d **满足的条件 = 每条 claim 都有 authority +（非 unknown 者）都有命令**。
`verify_reconstruction` 的拒绝原文贴在文件顶部，作为"为什么这张表是人工判定"的证据 —— 这不是放水，是把限制写清楚。

---

## 1. 其余三句

### Q3 MonitorView：**c 的函数层闭环后立刻做**

顺序固定：`裁决 2 落地 → MonitorView 五条 → 变异 29 条 + 全量（e）`。
MonitorView 是 backlog 里唯一还有证据可挖的一条，做完它就只剩 3 条 Unknown 结案项。

### 8 个基类继承：**单列口径，不要沉默**

- `replica/docs/DEVIATIONS.md` 增一节：「**LOOSE 口径（含基类继承）为正确口径** —— XAML 绑定沿继承链解析；
  `bind_scope.py` 自 R343 起如此设计；纯靠基类通过的 8 个类型**不计为缺口**」，并列出那 8 个类型。
- `tools/bind_scope.py` 输出末尾加一行：`note: base-class inheritance is counted (by design since R343)`。
- 这样以后没人会再问第二次。

### Q4/Q5 环境与收口

| 项 | 处置 |
|---|---|
| IDA ① (13337) | 保留（主参照） |
| IDA ② (13338) | 做到"裁决 2"结束即**关闭**（省 1.5 GB）；之后要复算再开 |
| `.publish-aot/` + `analysis/replica_aot_funcs.txt` | 保留（可复算输入） |
| 变异 29 条 | 在 MonitorView 之后、关掉实例②的前提下跑，期间不并行；跑完贴 `fired` 计数 |
| rea MCP | 保留（判据 d 的 Evidence 侧以后可能用得上） |

---

## 2. 一句话总结

> **数字集中到一处生成；函数级对照用现成的两条 IDA 链；claim 表允许人工，但必须标 authority 与命令。**
> 先把这三件做实，再谈 1:1 还剩多少。
