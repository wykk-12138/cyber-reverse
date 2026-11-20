# 类型缺失 17 条的逐条分类（自动生成：`python analysis/type_presence_triage.py`）

> 判据见脚本文件头。**成员覆盖率是下界**：只数类体里的成员名，继承来的、表达式体、
> 以及改了名但等价的成员都会被算成缺。所以「低覆盖」不能证明「不是同一类型」，
> 只能说明「没能证明是同一类型」——这也是 RENAMED 要求满覆盖的原因。

> **判别力规则（R619/R620）**：**同一个阈值适用于所有判定**，不只 RENAMED。
> 成员总数 < 3 的契约分不清两个类（一成员 `{ Count }` 会匹配任何提到 `Count` 的类），
> 所以一律记 `UNKNOWN`，不给更强的判定。否则 `PARTIAL` 桶会混进
> 「18/19 几乎肯定是同一类型」和「1/2 纯噪音」，而混着这两者的桶不成其为分类。
> 这与 R601 邻域判据、R616 抽样判据是同一类教训：看似合理，实际不区分。

| 类型（简单名） | 判定 | 证据 |
|---|---|---|
| `CloudflareSolver` | **RENAMED** | best match `CaptchaProvider` in GlobalSettings.cs — 9/9 (100%) |
| `Settings` | **RENAMED** | `GlobalSettings` declares all 34 member(s) — sole declaration match |
| `Concurrency` | **RENAMED** | `ConcurrencySettings` declares all 3 member(s) — sole declaration match |
| `ImapProvider` | **RENAMED** | `ImapMailProvider` in ImapMailProvider.cs — 4/4 (100%) documented; its doc comment names ImapProvider |
| `ActionConfig` | **RENAMED** | `SmartActionStepConfig` in SmartActions.cs — 2/2 (100%) documented; its doc comment names ActionConfig |
| `LocalizeEnumExtension` | **UNKNOWN (non-discriminative)** | best match `EditValue` in Primitives.cs — 1/1 (100%) |
| `LocalizeFallbackExtension` | **UNKNOWN (non-discriminative)** | best match `EditValue` in Primitives.cs — 1/1 (100%) |
| `LocalizeFormatExtension` | **UNKNOWN (non-discriminative)** | best match `EditValue` in Primitives.cs — 1/2 (50%) |
| `LocalizeSwitchExtension` | **UNKNOWN (non-discriminative)** | best match `TimeSpansExtensions` in TimeSpans.cs — 0/1 (0%) |
| `AccountsCreatorView` | **UNKNOWN (non-discriminative)** | best match `ProxyKeyBinds` in GlobalSettings.cs — 1/2 (50%) |
| `AuthWindow` | **NOT_IN_FUNCTION_SET** | R702: auth/licence is user management, not part of the replica's function set |
| `LicenseControl` | **NOT_IN_FUNCTION_SET** | R702: auth/licence is user management, not part of the replica's function set |
| `SettingsView` | **STRUCTURAL** | 18/19 member names co-occur in `SettingsShell` (only 1 class(es) reach that) |
| `TaskCreatorCartView` | **UNKNOWN (non-discriminating match)** | best match `ProxyKeyBinds` in GlobalSettings.cs — 2/3 (67%) |
| `TaskCreatorMainView` | **RENAMED** | `TaskCreatorView` declares all 4 member(s) — sole declaration match |

判定合计：NOT_IN_FUNCTION_SET=2, RENAMED=6, STRUCTURAL=1, UNKNOWN (non-discriminating match)=1, UNKNOWN (non-discriminative)=5
