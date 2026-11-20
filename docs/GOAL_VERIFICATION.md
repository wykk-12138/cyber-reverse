# 完成判据 a–f 核验清单（R1299，可复算）

> 全部数字取自 `docs/METRICS.md`（生成时间 **2026-11-20 15:24:49 +0800**，`python tools/metrics_report.py`，
> **度量脚本结果：全部 exit 0**、**时效警告：无**）。
> 每条判据给出：**证据（数字）→ 命令 → 结论**。

---

## a) 类型级缺口 → 0；类型缺失 → 0（不可得标 Unknown，范围外引 R702）；名字级三分类结案

| 证据 | 值 |
|---|---|
| `types with scope misses` | **0** |
| `types absent from source` | 15 = `renamed 13, out of scope 2, unimplemented 0, **unclassified 0**` |
| 名字级 `missing` 的分解 | **14 = noise 12 + out of scope 2 + real gap 0** |

- 命令：`python tools/bind_scope.py`；`python tools/bind_diff.py --type-presence`；`python tools/bind_diff.py --buckets`
- 12 条 `noise` 是 **NativeAOT 泛型实例编号**：镜像里 `Cybersole.Models.EditValue\`1,Cybersole.Core.HasMultiple_87…_101`
  与同块的 `Value_100` 证明编号是**全局实例序号**（`EditValue<T>` 被实例化多次，AOT 给每个实例成员加后缀去重），
  不是 12 个不同属性。
- 2 条 `out of scope` 是 `AuthWindow.Logout` 与 `LicenseControl.Authenticate`，由
  `docs/DECISION_LICENSE_OUT_OF_SCOPE.md`（R702）裁决不做。
- **结论：✅ 达标**（无未分类项，无未解释缺口）。

## b) 剩余仅不可得文案，且每条写明原因

| 证据 | 值 |
|---|---|
| `copy: zones with a missing key` | **0（0 个区）** |

- 命令：`python tools/copy_audit_report.py`
- 另：`Stores/Flows` 的 **24 条 `inferred`** 已全部对 324,901 条字符串 dump 查过（R1289/R1290），
  两轮共 **41 行注释**逐条写明「查过 / 0 命中 / 按 R1266 属 unknown」；唯一命中 `/rest/V1` 已升为实证（`146AB72A4`）。
- **结论：✅ 达标**。

## c) 产物级对照报告可复算（原版 `target\Cybersole.exe` ↔ 复刻件 `.publish-aot`）

| 对照面 | 值 | 命令 |
|---|---|---|
| 绑定描述符 | `entries 951 / types 215 / only-in-descriptors 137 / only-in-xaml 0` | `python tools/descriptor_report.py` |
| 数据文件名 | `original-on-disk not in replica 0 / replica-only 2` | `python tools/datafiles_diff.py` |
| 函数数量 `.pdata` | `277,120 ↔ 179,840 = 64.90%` | `python tools/func_count.py` |
| 可执行段体量 | `51,695,104 ↔ 29,511,680 = 57.09%` | `python tools/section_mass.py` |
| 产物新鲜度 | `changed against HEAD 0` ⇒ **`state: current`** | `python tools/artifact_freshness.py` |
| AOT 产物 | **57,491,456 B**（14:15:16 重新发布） | — |

- **结论：✅ 达标**（每一行都有命令，两产物均为本机可复算）。

## d) claim 表每条都有 authority + 命令 + gap_reason

- 表：`docs/PARITY_CLAIMS.md`（22 条 claim）+ `docs/METRIC_CLAIMS.md`（8 项度量各带证据等级与偏差方向）。
- 机械核验（`python analysis/audit_parity_claims.py`）：

```
claims parsed: 22
status counts: {'pass': 10, 'fail': 4, 'unknown': 8}
claims without authority      : 0
non-unknown without a command : 0
unknown without a gap_reason  : 0
CRITERION (d): MET
```

- **4 条 `fail` 的性质**（都带可复算命令，且都在 AGENTS §0「允许内部命名不同、不要求字节级一致」的豁免内）：

| id | 内容 | 值 | 性质 |
|---|---|---|---|
| C2 | 节布局 | 6 节 ↔ 9 节 | 不同框架/编译器必然不同 |
| C3 | 导出面 | 39 ↔ 1 | .NET 10 与 .NET 8 NativeAOT 导出策略不同（原版 39 个 Brotli 导出） |
| C4 | 导入面 | 17 DLL/438 函数 ↔ 18 DLL/409 函数 | 近似相同（差 1 DLL、29 函数） |
| C7b | 成员形状 | 91 处不匹配（core 3） | 已逐条处置于 `docs/SHAPE_GAPS.md` |

- **结论：✅ 达标**（判据 d 的满足条件即「每条有 authority，非 unknown 者都有命令」，脚本判定 `MET`）。

## e) 全量套件绿 + 变异全部 fired + 文档数字来自 METRICS.md

| 证据 | 值 |
|---|---|
| 完整套件 | **2468 通过 / 0 失败 / 0 跳过**（`metrics_report.py` 的 filter）；独立全量 `Speed!=Slow` = **2485 / 0 / 2 / 2487** |
| 变异 | **`total 59 / fired 59 / decorative 0 / skipped 0`** |
| 变异新鲜度 | **`staleness: 0 -- no exercised file's content differs from the run`** |
| 数字同源 | `DocsConsistency｜ParityDoc｜CoreCoverage` **21/21** |

- 命令：`python tools/metrics_report.py`、`python tools/mutation-check.py`
- **结论：✅ 达标**（时效警告区整块消失）。

## f) 核心覆盖可复算：站点流程、支付挑战、风控与 captcha 从二进制取证并对账，核心可执行逻辑逐项落地

| 面 | 值 | 命令 |
|---|---|---|
| 站点流程 | `flows 18 / override steps 369 / **unknown placeholders 0** / provenance exit 0` | `python tools/core_coverage.py` |
| 风控厂商 | `controls ok **True** / named in image 11 / wiring rows 0 / **missing 0**` | `python tools/vendor_coverage.py` |
| captcha | `families 6 / control 17 / **markers absent 0/5**`；四家挑战（hCaptcha / Turnstile / Enterprise / v2-v3）的 loader 字面量已实证并接进 `StoreFlow.DetectAsync`（R1286） | `python tools/captcha_coverage.py` |
| 支付挑战 | `control ok **True** / **stages 9** / **markers absent 0/5**` | `python tools/payment_challenges.py` |

- **结论：✅ 达标**。

---

## 剩余项：全部落在 GOAL 允许的两类外部条件内

### 一、原版有效登录凭据（无法静态获知）

- `FarfetchFlow` 7 条：`connect/app` 是**服务端下发**配置，其 schema 需原版登录才能捕获（R1077 反编译结论，R1294 已按此分类）。
- `Stores/Flows` 23 条 `inferred` 的 **0 命中**：按 R1266（哈希差分已证 NativeAOT 部分串逐字节不可搜）只能读作 unknown，需 live capture。
- `connect/app` 通道的 payload 字段、`BotTask.Running` / `BotTask.Task` 成员类型。

### 二、结构性不可做（需外部引擎，已在 `docs/CAPTCHA_COVERAGE.md` §七 结案）

- `HCaptchaSpoof` / `RecaptchaEnterprise` / `TurnstileSiteKey` 的**执行面**：原版在嵌入式
  **DotNetBrowser 4.3.5.8591 + 外部 Chromium**（`DOTNETBROWSER_CHROMIUM_DIR`）里跑
  `grecaptcha.enterprise.execute()` 与 `turnstile.render()`；复刻件无该引擎，接入等于引入新依赖（商业授权/另行裁决）。
  **识别面已落地并有调用点**。

---

## 结论

**判据 a、b、c、d、e、f 六条全部达标**，每条都附可复算命令与当前数字；
核心队列 ①（站点流程 placeholders 0）、②（支付 stages 9 / markers 0-5 / captcha 0-5）、③（传输层默认路径与镜像同源：SocketsHttpHandler + SslStream + TLS 1.2/1.3 + GREASE）均已结案；
剩余项**无一例外**落在「原版登录凭据」与「结构性需外部引擎」两类外部条件内。

<!-- GOAL_COMPLETE -->
