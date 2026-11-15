# R433 待决事项与口径校订（给 YG 的一份清单）

> 本轮做了三件事：**复算基线并校订口径** → **判据 c（产物级对照）** → **判据 d（claim 表）**。
> 这份文件只装**问题与待决项**，不含叙述性总结。
> 详细交付物：`docs/PARITY_PRODUCT.md`（判据 c）、`docs/PARITY_CLAIMS.md`（判据 d）。

生成时间：2026-11-14 18:0x（Asia/Shanghai）· 会话轮次：R433

---

## 0. 一句话状态

口径已对齐（实测 4，不是 10，差异来源已证）；判据 c 的**结构层完成、函数层卡在 rea provider 版本契约**；
判据 d 的 claim 表已落地（4 pass / 3 fail-可解释 / 7 unknown）。**三处陈旧数字未改，等你点头。**

---

## 1. 口径校订（已查清，结论如下）

### 1.1 类型级缺口：实测 4，不是 10

```
$ cd D:\projects\cyber-reverse\replica
$ python tools\bind_scope.py
type-scoped check: types present, members missing on THAT type
  Profile                      Card, Username
  ProxyTester                  Name
  MonitorView                  LinkChange, OpenFilter, OpenUrl, Quicktask, View
  SmartActionsView             Export
types with scope misses: 4
```

差的 6 个 = `TaskView.Toggle`、`DataView.ViewLogs`、`CloudflareSolversView.Edit`、
`GoogleAccountsView.Edit`、`ImapView.Configure`、`GeneralSettingsView.ProfileItems`
（`replica/docs/BINDING_BACKLOG.md` 记为 R432 已清零）。

**三重证明这不是口径放宽**：

| # | 证据 |
|---|---|
| 1 | `bind_scope.py` 源码**无排除名单、无阈值**；逻辑仅为“类型存在时，成员名出现在该类型 body（含基类）即算有” |
| 2 | `docs/xaml_bindings.json` mtime = 11-13 17:47（绑定表未动）；`tools/bind_scope.py` mtime = 11-14 08:37（R432 工作时段） |
| 3 | 6 个成员在源码里**都在各自类型 body 内**：`Toggle = new RelayCommand(() => ToggleSelected())`、`ViewLogs = new RelayCommand(...)`、`Edit = new RelayCommand(...)`、`ExecuteConfigure`、`ProfileItems`（`grep` 实见 25 处命中） |

### 1.2 附带发现：8 个类型是**纯靠基类继承**通过的（**待你定口径**）

把“基类继承”关掉做严格版：

```
STRICT (own body only, no base inheritance): 12 types
LOOSE  (with base inheritance): 4 types
types rescued purely by base inheritance: 8
    AycdInboxCreatorView        -> Close
    CaptchaProviderCreatorView  -> Close, Delete
    Checkout                    -> Profile
    CloudflareSolverCreatorView -> Close, Delete
    GoogleAccountEditView       -> Close
    ImapCreatorView             -> Close
    PayPalAccountCreatorView    -> Close
    WebhookCreatorView          -> Close
```

- `with_bases` 是 `bind_scope.py` **从 R343 就有的设计**（注释原文：`members inherited from a base are not missing`）。
- XAML 绑定本来就沿继承链解析，所以 LOOSE 是**正确口径**，这 8 个不算缺口。
- **但**：从来没人把这条写进任何账本。要不要单列一条“已知口径：基类继承计入”，还是维持现状，**需要你一句话**。

---

## 2. 待订正的陈旧数字（我一个都没动）

| 文件 | 现在写的 | 实测 | 依据命令 |
|---|---|---|---|
| `AGENTS.md` §4 | 名字级缺口 17 | **16** | `python tools\bind_diff.py --buckets` |
| `AGENTS.md` §4、`docs/GOAL.md` 判据 a、`docs/HANDOFF.md` 第 2 条 | 类型级缺口 10 | **4** | `python tools\bind_scope.py` |
| `AGENTS.md` §4、`replica/docs/DEVIATIONS.md` §1 | 成员形状 272 | **275** | `python tools\shape_audit.py` |
| `AGENTS.md` §4、`replica/docs/SESSION_STATE.md`、`docs/HANDOFF.md` §5 | 套件 1606 通过 | **1607 / 0 / 2**（25 s） | `dotnet test --filter "Speed!=Slow" -m:1` |
| `replica/docs/SESSION_STATE.md` 标题 | R426 状态 | 实际已到 **R433** | 本轮 |
| `replica/docs/SESSION_STATE.md` 底部 | 残留一整块 R425「机器已无法 dotnet build / 未完成（需要重启机器）」 | 与自己的标题自相矛盾（R426 已“重启后全量跑通”） | 本轮复核 |
| `replica/docs/DEVIATIONS.md` §6 / §7 | 类型级缺口 18 / 套件 1525 | 4 / 1607 | 同上 |
| `docs/HANDOFF.md` §六「下一步任务」第 2 条 | 列了 10 个类型级缺口，其中 **6 个已做完** | 剩 4 个 | `BINDING_BACKLOG.md`（R432）已更新，HANDOFF 没跟 |

> 纪律依据：`AGENTS.md` §3「数字随事实走」+ §4「文档数字必须等于度量工具的当前输出」。
> **改不改、什么时候改，等你定。**

---

## 3. 待决事项（按我建议的顺序）

### Q1. 判据 c 的函数层：走哪条路？

| 选项 | 解锁 | 代价 | 我的看法 |
|---|---|---|---|
| A. 原版跑一次 `inspect_pe_imports`（`max_functions≥438`，输出重定向到文件） | claim C4（导入面） | 几分钟，无新依赖 | **可以直接做** |
| B. 字符串池分类比对（`analysis\pe_strings.txt` ↔ AOT 字符串清单） | C8 | 需写分类器（现有工具确无此能力，须按 §1.2 注明理由） | 可做 |
| C. 装 Ghidra（`GHIDRA_INSTALL_DIR`）给 REA 当 native provider | **C6 / C7 / C9**（函数级） | 数 GB 下载 + 123 MB NativeAOT 分析时间；引入第三套反编译口径 | 唯一能真正“逐函数对照”的路 |
| D. 给 IDA 装 legacy 工具名兼容层 | C6 / C7 / C9 | 会与现有 66 工具矩阵冲突 | **不建议** |
| E. 另做一次 managed 发布，走 REA 的 .NET 工具 | C10 / C11（成员级） | 需新构建配置；managed 不是交付形态，只作对照输入 | 备选 |

**卡点原文**（实测，非推断）：

```
mcp__rea__binary_session →
  ghidra  : unavailable  Set GHIDRA_INSTALL_DIR to an extracted Ghidra 12.x (>=12.1)
  hopper  : unavailable  Hopper integration is not supported on win32
  ida     : unavailable  Set REA_IDA_MCP_CONFIG to an upstream IDA MCP JSON registration
  kuna    : unavailable  Set REA_KUNA_COMMAND …
  rea-dotnet-static : available   （只对有 CLR 元数据的产物有效 → NativeAOT 原版无效）
  rea-artifact-graph: available  （inspect_artifact 不收 path，须先 open_binary，PE 要 native provider）
```

`REA` 的 `ida` attached profile 只认 **legacy 工具名**（`get_metadata`/`list_functions`/`decompile_function`），
本机 `ida_pro_mcp` 是新版目录（`list_funcs`/`decompile`/`server_health`，66 工具，`analysis\ida.py tools` 实测）。

### Q2. 判据 d 的工具缺口要不要报为“判据未满足”？

`verify_reconstruction` 实测拒绝：

```
Error: Claim c1-import-surface requires compare_artifacts Evidence; selected inspect_pe_imports
```

`docs/PARITY_CLAIMS.md` 是**沿用它的 schema、人工判定**的表（文件开头已声明）。
如果验收口径要求“必须由工具产出”，那判据 d 现在算**未满足**；如果接受“同构 claim 表 + 人工判定”，
那判据 d **已满足**（4 pass / 3 fail-可解释 / 7 unknown，unknown 逐条写了缺什么）。**这条要你裁。**

### Q3. MonitorView 五条何时做？

按你原定顺序（c → d → MonitorView → e）。现在 c 的结构层与 d 已交付，MonitorView 是 backlog 里**唯一还有证据可挖**的一条
（其余 3 条已按你指示写成 Unknown 结案，见 `PARITY_CLAIMS.md` §6）。

### Q4. 环境残留要不要清？

| 残留 | 说明 | 处置建议 |
|---|---|---|
| IDA 实例 ①pid 18852，端口 **13337** | 原版 `target\Cybersole.exe.i64`，已就绪（hexrays_ready, 324,901 strings） | **保留**（主参照） |
| IDA 实例 ②pid 9408，端口 **13338**，1.5 GB | 复刻件库 `.publish-aot\Cybersole.Ui.exe.i64`，已加载 PDB 符号 | 做成员对照要用 → 保留；不做则关掉省内存 |
| `.publish-aot\`（51.85 MB exe + 240 MB pdb + 依赖） | 判据 c 的产物 | 保留（复算用） |
| `analysis\replica_aot_funcs.txt`（136,798 行） | 复刻件符号清单 | 保留（新工具的输入） |
| rea MCP 代理进程 | 6.9.0，255 工具 | 保留 |

### Q5. 29 条变异测试（判据 e）

**一次都没跑过**。前置：`available > 6 GB` 且期间不并行。当前 available ≈ 16 GB，
但两个 IDA 实例占约 2.4 GB —— 要跑之前建议先关实例 ②。

---

## 4. 本轮新增/改动的文件

| 文件 | 性质 | 说明 |
|---|---|---|
| `docs/PARITY_PRODUCT.md` | 新建 | 判据 c：双产物结构对照 + 函数/字符串数量 + 差异清单 + 缺什么证据 |
| `docs/PARITY_CLAIMS.md` | 新建 | 判据 d：14 条有限 claim 的逐条判定（4 pass / 3 fail / 7 unknown） |
| `docs/R433_OPEN_QUESTIONS.md` | 新建（本文件） | 待决事项与口径校订清单 |
| `replica/tools/aot_member_coverage.py` | 新建 | 产物符号 × 绑定表交叉；文件头注明“现有工具为什么不够用” |
| `analysis/replica_aot_funcs.txt` | 新建（数据） | 复刻件 AOT 的 136,798 行符号清单（IDA 产出） |
| `replica/.publish-aot/` | 新建（产物） | NativeAOT 发布物 |

**没有改动**：任何源码、任何度量脚本、任何既有文档的数字。`snapshot.py` 未运行（因为没改源码）。

---

## 5. 复现本轮全部数字

```powershell
cd D:\projects\cyber-reverse

# 口径
cd replica
python tools\bind_scope.py
python tools\bind_diff.py --buckets
python tools\shape_audit.py
python tools\copy_audit_report.py
D:\tools\dotnet8\dotnet.exe test tests\Cybersole.Tests\Cybersole.Tests.csproj -c Debug --filter "Speed!=Slow" -m:1

# 判据 c：构建 + PE 层
cd D:\projects\cyber-reverse
D:\tools\dotnet8\dotnet.exe publish replica\src\Cybersole.Ui\Cybersole.Ui.csproj -c Release -r win-x64 `
    -p:PublishAot=true -p:StripSymbols=false -o replica\.publish-aot
$env:PYTHONIOENCODING="utf-8"
D:\projects\IDA-pro\python311\python.exe D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_triage.py `
    replica\.publish-aot\Cybersole.Ui.exe
D:\projects\IDA-pro\python311\python.exe D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_diff.py `
    target\Cybersole.exe replica\.publish-aot\Cybersole.Ui.exe --summary

# 函数/字符串（原版，端口 13337）
python analysis\ida.py py "import idautils; print(len(list(idautils.Functions()))); print(len(list(idautils.Strings())))"

# 成员可见性
cd replica; python tools\aot_member_coverage.py
```

复刻件函数清单的取法（第二实例，端口 13338）：IDA 加载 `.publish-aot\Cybersole.Ui.exe`，
接受 `Load PDB file`（`Load types` + `Load names`），用同一 RPC 协议对 `127.0.0.1:13338/mcp`
发 `py_eval`，把 `idautils.Functions()` 导成 `addr<TAB>size<TAB>name` 落到
`analysis\replica_aot_funcs.txt`。

---

## 6. 需要你回的三句话

1. **陈旧数字**：一次改齐，还是先推 MonitorView？
2. **函数级对照**：走 Ghidra（C），还是本轮接受 Unknown 结案？
3. **判据 d 的验收口径**：人工 claim 表算满足，还是必须工具产出？

（另外两句可选：8 个基类继承类型要不要单列口径；IDA 实例 ② 关不关。）
