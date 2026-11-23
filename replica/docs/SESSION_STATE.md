# 会话状态（2026-11-23 R1383 静态逆向收口交接态）

本文件只保留**当前工作态索引与环境基线**。历史逐轮叙述归 `docs/VERDICT.md`、`docs/HANDOFF.md`（与 git 历史），实时度量唯一事实源归 **`docs/METRICS.md`**。

## 当前状态（2026-11-23 R1383，最新提交见 `git log --oneline -5`）

**单一事实源：`docs/METRICS.md`**（`python tools/metrics_report.py` 生成，带时间戳与逐条命令）。
本文件**不再硬编码动态度量数值** —— 数字只认 `docs/METRICS.md` 当次生成输出。

| 项 | 看哪里 |
|---|---|
| **最新收口总账（Phase 1/2 + R1383）** | **`docs/PROGRESS_AND_GAP.md`** |
| **完整复现工作路线图与三类边界** | **`docs/REMAINING_REPLICATION_ROADMAP.md`** |
| **新会话交接导航与复制即用提示词** | **`docs/HANDOFF.md`** · **`docs/HANDOFF_PROMPT_antigravity.md`** |
| **全量度量、套件通过数与变异新鲜度** | **`docs/METRICS.md`** |
| **原版 ↔ 复刻件模块级 PDB/IDA 函数普查** | **`docs/MODULE_FUNCTION_CENSUS.md`** |
| **异步状态机尾项 / 字符串分类 / 只读风控审计** | **`docs/ASYNC_TAIL.md`** · **`docs/C8_STRING_CLASSES.md`** · **`docs/VENDOR_WIRING.md` §十三** |
| **产物级对照与「1:1」Claim 表** | `docs/PARITY_PRODUCT.md` · `docs/PARITY_CLAIMS.md` |
| **已接受差异与 UI 形状台账（冻结在 ④）** | `docs/DEVIATIONS.md` · `docs/SHAPE_GAPS.md` · `docs/BINDING_BACKLOG.md` |

- **已闭环状态（R1383）**：Phase 1 + Phase 2（Waves 2A–2D）+ R1382 纠偏 + R1383（Batches 1–3：`StripeGateway`/`CommerceHub`/`Gmo`/`Komoju`、`Checkout.com` 28 家 ACS 处理器、`JDGroup/FINL` vs `Warhammer` CT 消歧、`CasioFlow` 4 条非 PoW 网关、Panini PPCP/Braintree、`JohnLewis`/`Scheels`/`Shopify` 与安全异步尾、`AngleSharp 1.4.0` `HtmlFormDom`、`ZstdSharp.Port 0.8.1` `ContentEncodingCodec` + `NetClient`/`Bouncy*` 传输对齐、`VENDOR_WIRING.md` §十三只读被动审计、`C7c` 回环探针与 `C8` 去噪）均已落地；全量 NativeAOT 产物已重发布（`state: current`），全部指标与非浏览器测试套件绿灯（`CRITERION (d): MET`、变异 `staleness: 0`）。

## 参照物（两个版本，别混）

| 版本 | 路径 | 用途 |
|---|---|---|
| **5.18.32** | `target/Cybersole.exe`（`target/Cybersole.exe.i64` 基于它） | **任务主目标** |
| 5.18.35 | `target-alt/Cybersole-5.18.35.exe` | 版本差分对照输入（REA `compare_application_versions` / `pe_diff.py`） |

## 数据目录（重要）

```
复刻件   %APPDATA%\CybersoleReplica      （CYBERSOLE_DATA_ROOT 可覆盖）
原版     %APPDATA%\Cybersole             （OriginalDataRoot，只读证据，永不写入）
原版安装 %LOCALAPPDATA%\Cybersole        （LocalRoot，只读）
```

守卫：`EverythingTheReplicaWritesStaysUnderItsOwnDataRoot` —— 复刻件一切可写路径必须落在自身 `DataRoot` 下，绝不写入原版目录。

## 证据可信度

| 证据 | 状态 |
|---|---|
| IDA 数据库（`analysis/ida.py str` / Hex-Rays / `names_at.py` / `.pdata`） | ✅ 全量权威（须对冻结字符串算 `chars_va - 12`） |
| 字符串池抽样（`analysis/pe_strings.txt`） | 🟡 正向可用，反向**不可**当全量否定证据 |
| 原版 `.cyb` 备份（紧凑 camelCase）与 `docs/GUI_BASELINE.md` | ✅ 可信实证 |
| `settings.json` / `tasks.json` / `solvers.json` 等复刻件输出 | ❌ 不可作为原版“实机”证据（防止循环论证） |

## 工具（`replica/tools/` 与 `analysis/`）

| 工具 | 作用 |
|---|---|
| `replica/tools/metrics_report.py` | 一键生成 `docs/METRICS.md` 并跑非慢速全量测试 |
| `replica/tools/mutation-check.py` / `mutation_report.py` | 变异测试校验与新鲜度报告 |
| `replica/tools/where_is.py` | 动手前先查 `replica/src/` 现有实现 |
| `replica/tools/snapshot.py` | 修改源码前创建恢复快照 |
| `replica/tools/vendor_coverage.py` / `core_coverage.py` | 风控与站点流程覆盖核对 |
| `replica/tools/bind_diff.py` / `bind_scope.py` / `copy_audit_report.py` / `datafiles_diff.py` | 绑定、文案与数据文件名对照 |
| `analysis/module_function_census.py` | 复刻件 PDB + 原版 IDA 模块级函数普查（生成 `docs/MODULE_FUNCTION_CENSUS.md`） |
| `analysis/disp32_scan_any.py` / `site_to_func.py` / `names_at.py` | NativeAOT 冻结字符串定位与字面量解码链 |

## 下一步推进路线

①–③ 本机可达成静态逆向与运行态重实现已在 R1383 收口。剩余工作划分为四类明确边界（安全跳过禁区 / 外部阻塞需新凭据与抓包 / 优先级 ④ UI 形状冻结 / 结构性非等价噪声），详见 **`docs/REMAINING_REPLICATION_ROADMAP.md`** 与 **`docs/HANDOFF_PROMPT_antigravity.md`**。
