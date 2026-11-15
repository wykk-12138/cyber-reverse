# 会话状态（第 402 轮重写；此前 175 个状态块已归档到 `SESSION_STATE.archive.md`）

本文件只保留**当前**状态。历史逐轮叙述在 `docs/VERDICT.md`，被替换掉的旧状态块在
`docs/SESSION_STATE.archive.md`。

## 当前状态（R433）

**单一事实源：`docs/METRICS.md`**（`python tools/metrics_report.py` 生成，带时间戳与逐条命令）。
本文件**不再复述具体数值** —— R433 裁决 1：数字漂移是生成问题，不是纪律问题。

> **R449 起**：`Global.Settings → GlobalSettings` 的成员覆盖到 **34/34**（此前 33/34，差的是
> `SmartActions` 被写成 `Smartactions`）。修法是改名 + `[JsonProperty("smartactions")]` ——
> 这样绑定名对上，落盘名仍是原版的全小写 `smartactions`。

| 项 | 看哪里 |
|---|---|
| **objective 达成到哪一步（先看这个）** | **`docs/DELIVERY_STATUS.md`** |
| 名字级缺口 / 类型级缺口 / 类型缺失 / 成员形状 / 文案 19 区 / 缺口分桶 / 完整套件 | **`docs/METRICS.md`** |
| 产物级对照（双产物结构、函数数量、符号可见性） | `docs/PARITY_PRODUCT.md`（`analysis/func_compare.py`） |
| 「1:1」的有限 claim 与逐条 authority | `docs/PARITY_CLAIMS.md` |
| 已接受差异 / 已知口径 | `docs/DEVIATIONS.md` |
| 未结案的绑定缺口 | `docs/BINDING_BACKLOG.md` |

R434 生成时的量级（仅作参照，**以 METRICS.md 为准**）：类型级缺口 3、类型缺失 51（多数是改名，待分类）、
名字级 16、形状 275、文案 5（全为池中截断）、套件全绿。

R434 的进展：**MonitorView 五条结案**（`View`/`OpenFilter` 真做并有用例；`OpenUrl`/`LinkChange`/`Quicktask`
是显式钩子 + claim 记 Unknown，`MonitorViewBehaviourPins` 守卫代码与账本互指）；
`Models.Input{Type}` 补上；新增第三类度量 `bind_diff.py --type-presence`。

## 参照物（两个版本，别混）

| 版本 | 路径 | 用途 |
|---|---|---|
| **5.18.32** | `target/Cybersole.exe`（IDB 基于它） | **任务目标** |
| 5.18.35 | `target-alt/Cybersole-5.18.35.exe`（原版今天自更新出来的，已存档） | 只作对照输入（REA `compare_application_versions`） |

## 数据目录（重要）

```
复刻件   %APPDATA%\CybersoleReplica      （CYBERSOLE_DATA_ROOT 可覆盖）
原版     %APPDATA%\Cybersole             （OriginalDataRoot，只读证据，永不写入）
原版安装 %LOCALAPPDATA%\Cybersole        （LocalRoot，只读；只有版本面板数包）
```

守卫：`EverythingTheReplicaWritesStaysUnderItsOwnDataRoot` —— 15 条可写路径必须都在 `DataRoot` 下。

R387 之前两者共用一个目录，导致"用实机文件核对模型"变成循环论证。

## 证据可信度

| 证据 | 状态 |
|---|---|
| 字符串池 / locale / 绑定表（`analysis/pe_strings.txt`） | ✅ 始终可信 |
| 原版 `.cyb` 备份（紧凑 camelCase） | ✅ 可信（R388 用格式指纹判定） |
| `settings.json` / `tasks.json` / `solvers.json` 等 | ❌ 曾被复刻件写入，不可作为"实机"证据 |
| GUI 实测记录（`docs/GUI_BASELINE.md`） | ✅ 可信（十个界面） |

## 工具（都在 `replica/tools/`）

| 工具 | 作用 |
|---|---|
| `bind_diff.py` | 名字级绑定缺口 |
| `backlog_report.py` | 重算账本数字 |
| `bind_scope.py` | 类型级绑定缺口 |
| `bind_shape.py` / `shape_audit.py` | 成员形状（属性 vs 方法） |
| `locale_coverage.py` / `locale_text_gap.py` | 界面文案缺口（可归零） |
| `locale_near_miss.py` | "几乎对但不相等"的文案（需人工三分类） |
| `copy_audit_report.py` | 一张总表：19 区的键数 / 缺失 / 近似（写入 `docs/COPY_QUEUE.md`） |
| `live_schema_diff.py` | 落盘 JSON 与模型的字段差 |
| `wire_candidates.py` | 未被构造的 UI 类 ↔ 绑定成员 |
| `snapshot.py` | 改结构前的源码快照 |

## 阻塞项

| 项 | 恢复条件 |
|---|---|
| **exe-reverse** | 已停用 skill 注册（junction 移到 `.dsh/skills-disabled/`），只留两个只读脚本直调：`pe_triage.py`（PE 分诊）、`pe_diff.py`（版本对照）。R431 实测：`pe_triage.py`（PE 分诊）、`pe_diff.py`（版本对照）。R431 实测：原版是 **.NET 10**（PDB 路径）、39 个导出全是 Brotli、TLS callback 存在、5.18.32↔5.18.35 六节全重排 | 已用 |
| **rea MCP** | 已装 `D:\tools\rea-agents` + 侧装 Node 24.22.1；已注册到 DSH profile，重启后可见 `mcp__rea__*`（255 工具）。用法见 `docs/REA-WORKFLOW.md` |
| ida MCP | **IDA 侧已就绪**（R427：已启动 IDA 并载入 `target/Cybersole.exe.i64`，插件在 127.0.0.1:13337 监听，pid 20560）。**缺 DSH 侧的代理**：需要你在 DSH 设置里把 `ida` 这条 MCP 关掉再打开（或重启 DSH），代理才会被 spawn。之后 `mcp__ida__server_health` 应返回 ok |
| IDA 无头批处理 | **不可用**：`idat.exe -A -S<script>` 立刻退出、脚本不执行、日志为空（R407 实测） |
| 主界面 GUI 核对 | 需要登录账号；目前只能核对登录窗口 |

## ~~⚠ 现在机器已无法 dotnet build（R425）~~ — 已过期，R426 机器重启后全量跑通

> 这块是 R425 的现场记录，**保留仅为历史**（R433 复核时发现它与本文件标题自相矛盾）。
> 当前能否构建只看 `docs/METRICS.md` 里的「完整套件」一行：exit 0 且失败 0 即正常。

```
（R425 原始记录）available 1.35 GB / Commit 93.91 of 94.03 GB
dotnet test → MSB4184 System.OutOfMemoryException
```

## 未完成

| 任务 | 状态 |
|---|---|
| 全量套件 | **已跑通** —— 见 `docs/METRICS.md` |
| 变异测试 `python tools/mutation-check.py`（29 条） | **仍未跑**。前置：available > 6 GB 且期间不并行；R433 裁决：放在 MonitorView 之后、关掉 IDA 实例②再跑 |

## 下一步（R433/R434 裁决，顺序固定）

1. ~~裁决 2 落地~~ —— `analysis/func_compare.py` 双链对照（完成，见 `docs/PARITY_PRODUCT.md`）；
2. ~~MonitorView 五条~~ —— **R434 完成**（见 `docs/PARITY_CLAIMS.md` §3.5）；
3. **类型缺失分类** —— 51 条 ABSENT 逐条判"改名"或"未实现"（多数是改名；先补映射表，见 `BINDING_BACKLOG.md`）；
4. **变异全量 + 全量套件（判据 e）** —— 期间不并行，跑完贴 `running N of N` 与 `fired` 计数。

再往后：判据 c 的语义层（伪代码级逐函数等价）仍是 Unknown，见 `docs/PARITY_CLAIMS.md` C7。

---

