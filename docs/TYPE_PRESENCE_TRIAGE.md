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
| `LocalizeEnumExtension` | **UNKNOWN (缺：类型自身成员集)** | R1110 correction: the `1 members: Value` this row previously leaned on is a **descriptor artifact**. The descriptor reads `Cybersole.Ui.Localization.LocalizeEnumExtension,Cybersole.Value!Getter` (0x14320d3b4, also 0x14320d3fb / 0x14363910b) -- `Cybersole.Value` is the binding **path** on the target, not a member of this type. So its own member set is not present in the descriptors at all. Missing: member evidence from the MethodTable or the type metadata, not the binding table. |
| `LocalizeFallbackExtension` | **UNKNOWN (缺：类型自身成员集)** | R1110 correction: same artifact -- `Cybersole.Ui.Localization.LocalizeFallbackExtension,Cybersole.Value!Getter` (0x14320eae3, also 0x14320eb2e / 0x143639e4b) makes the map report a `Value` member that is really the binding path. Missing: the type's own member set, from MethodTable / metadata. |
| `LocalizeFormatExtension` | **EQUIVALENT** | `docs/B_CLASS_DECISIONS.md` L26 rules it `已有等价物`: the replica formats with a direct `string.Format` call. Image-side identity recovered this round: namespace `Cybersole.Ui.Localization` and the XAML type-name table at `0x1432fd514` (see `0x14320c2d5`). |
| `LocalizeSwitchExtension` | **EQUIVALENT** | `docs/B_CLASS_DECISIONS.md` L25 rules it `已有等价物`: the replica expresses the same intent with an inline ternary. Image-side identity recovered this round: namespace `Cybersole.Ui.Localization`, same name table at `0x1432fd514`. |
| `AccountsCreatorView` | **RENAMED** | `tests/Cybersole.Tests/OriginalViewClassParityTests.cs` L47 pins the mapping `AccountsCreatorView` -> `AccountImportWindow` (machine-checked, not a guess); the replica class carries the original's full name in its doc comment. |
| `AuthWindow` | **OUT_OF_SCOPE** | YG ruling R702: auth/licence is user management, not part of the replica's function set |
| `LicenseControl` | **OUT_OF_SCOPE** | YG ruling R702: auth/licence is user management, not part of the replica's function set |
| `SettingsView` | **STRUCTURAL** | 18/19 member names co-occur in `SettingsShell` (only 1 class(es) reach that) |
| `TaskCreatorCartView` | **RENAMED** | `tests/Cybersole.Tests/OriginalViewClassParityTests.cs` L51 pins `TaskCreatorCartView` -> `TaskCreatorView`; the test's own comment records that the image's three task-creator classes are one class in the replica. |
| `TaskCreatorMainView` | **RENAMED** | `TaskCreatorView` declares all 4 member(s) — sole declaration match |

判定合计：OUT_OF_SCOPE=2, RENAMED=6, STRUCTURAL=1, UNKNOWN (non-discriminating match)=1, UNKNOWN (non-discriminative)=5
