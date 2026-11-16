# 交接提示词（新会话 / 冷启动专用）

> 这份文件是给**一个完全不记得前面 430 轮的新 agent** 用的。
> 用法：把下面「▣ 第 0 条消息」整段贴进新会话；剩下的章节是它执行时会反复回来查的细节。

---

## ▣ 第 0 条消息（整段复制）

```
工作目录：D:\projects\cyber-reverse。你是接着一个已经跑了 430 轮的任务继续做，不要从头设计。

## 一、先建立上下文（按顺序读，别跳）

1. D:\projects\cyber-reverse\AGENTS.md                     —— 作战约定：方法论优先级、证据规则、改码纪律、度量基线（必读，5 KB）
2. D:\projects\cyber-reverse\docs\REA-WORKFLOW.md          —— rea MCP 怎么用、哪些功能被禁用（必读）
3. D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md —— 当前状态、阻塞项、下一步（必读，80 行，这是"现在"）
4. D:\projects\cyber-reverse\replica\docs\METHOD.md        —— 200 行，15 条踩过的坑与做法（必读）
5. D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md（54 行）与 DEVIATIONS.md（77 行）—— 还缺什么、哪些差异是"已接受"
6. D:\projects\cyber-reverse\replica\docs\COPY_QUEUE.md    —— 19 个区文案缺口总表
7. D:\projects\cyber-reverse\replica\docs\VERDICT.md       —— 1.17 MB 编年史。**不要整读**：
   只读最后 300 行（`Get-Content -Tail 300`）了解最近 5 轮，需要某条历史结论时再按关键词搜。

另外：D:\projects\cyber-reverse\docs\HANDOFF.md（本文件）含环境事实与两版本参照物。

## 二、任务

把 Cybersole.exe **5.18.32**（**.NET 10 NativeAOT**，无 IL）在 replica\ 里做成**功能 1:1** 的复刻件：
函数数量对等、每个函数功能相等、效率相近；命名可以不同，不要求字节级相同。
复刻件：.NET 8 + Avalonia 11.3.2 + xunit（目标框架不必跟随原版），解决方案 replica\Cybersole.sln，dotnet 在 D:\tools\dotnet8\dotnet.exe。

## 三、动手前先把证据链打通（三条链，命令可直接用）

1) IDA（主参照，Hex-Rays）
   - 先体检：powershell -NoProfile -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 -Path "D:\projects\cyber-reverse\target\Cybersole.exe"
   - 期望末行 VERDICT: ready；若 INSTANCE: none，用 GUI 的 IDA 打开 D:\projects\cyber-reverse\target\Cybersole.exe.i64，
     并处理它弹的模态框：①"unpacked version of database… proceed?" → 点 Proceed with unpacked base；
     ②"database is not closed / repair?" → 先整库备份再点 Repair（备份示例：target\db-backup-<时间戳>\）。
   - 库很大（1.4 GB），载入约 60 秒、工作集约 1.9 GB；端口 127.0.0.1:13337 由 ida.exe 自己监听。
   - **库里只有 sub_* 符号**（没有 PDB/符号恢复）。检索路径固定为：字符串 → xrefs → 函数 → 反编译。
   - DSH 的 ida 代理若显示 PROXY: MISSING，用直连客户端顶上：
     python analysis\ida.py health | funcs <substr> | dec <addr> | dis <addr> | xrefs <name-or-addr> | str <regex>
2) rea（第二意见，255 工具）
   - 用侧装 Node 启动（系统 Node 24.13.1 会被拒）：D:\tools\node24\node-v24.22.1-win-x64\node.exe
     D:\tools\rea-agents\node_modules\rea-agents\scripts\rea.mjs mcp
   - 已注册在 ~/.dsh/profiles/desktop/cordis.patch.yml（serverName: rea），DSH 重启后出现 mcp__rea__*。
   - 只用这几件：investigate_feature、compare_application_versions、compare_functions、
     match_native_functions、verify_reconstruction、list_unknowns/record_unknown、correlate_static_and_runtime。
     其余（Android/JS/EVM/Frida/ADB/build-computer…）不用。
3) CUA（GUI，只做消歧和定位，不作主参照）
   - 原版当前停在登录页（无凭据进不了主界面）；主界面的证据来自 docs\GUI_BASELINE.md 的十次实测记录。
   - 复刻件可随时启动看界面：dotnet run --project replica\src\Cybersole.Ui

## 三·补、只读读数器（不用加载 skill）

`exe-reverse` 已**停用 skill 注册**（仓库仍在 `D:\projects\exe-reverse`，junction 在 `.dsh\skills-disabled\`），
原因：它的交付判据是"打补丁后仍能运行"，与"忠实重实现"方向相反，容易被误当方法论主导。
**只保留两个只读脚本，绝对路径直调**：

```
python D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_triage.py <exe>
python D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_diff.py   <exeA> <exeB>
```

已经用它们得到的事实（别再重复试）：
- 原版是 **.NET 10**（PDB 路径 `bin/Release/net10.0/win-x64/native/Cybersole.pdb`，linker 14.44）；
- 39 个导出**全是 Brotli**（`BrotliDecoderDecompress` 等），不是应用符号 → "导出表当符号源"这条路断了；
- **TLS callback 存在**（`0x3105edc`）→ 断点打 `AddressOfEntryPoint` 太晚；
- 5.18.32 ↔ 5.18.35：6 个节全部重排、4.19 MB 字节差异 → 版本 diff 只能在 inventory/资源/字符串层面做。

## 四、红线（违反会静默污染结论）

- 只读：C:\Users\wykk\AppData\Local\Cybersole（原版安装/更新目录）、%APPDATA%\Cybersole（原版数据目录）。
  复刻件只写 %APPDATA%\CybersoleReplica（或 $env:CYBERSOLE_DATA_ROOT）。
- 不能把复刻件自己写出的 settings.json/tasks.json/solvers.json/checkoutHistory.json 当"实机证据"（循环论证）。
- 判断文件编码只看字节（raw.decode('utf-8')）；这个控制台会把 UTF-8 中文显示成乱码，别据此改文件。
- 改代码前先 python tools\snapshot.py；禁止按行号做手术，只按整块锚点替换。
- "没跑成" ≠ "通过" ≠ "失败"：内存不足导致的崩溃必须单列。
- 不要自己发明方法论或工具：先抄 seep-reverse-lab（D:\projects\seep-reverse-lab 的 MANUAL\Tool\skill），
  再抄 rea，都没有才自己写，并在文件头注明"为什么现有不够用"。

## 五、先复算基线，再动手（每个数字都要能重算）

**唯一入口**（R433 裁决 1：数字集中到一处生成，不在文档里硬编码）：

```
cd D:\projects\cyber-reverse\replica
python tools\metrics_report.py               → 生成 docs\METRICS.md（五个度量 + 完整套件，带时间戳与逐条命令）
python tools\metrics_report.py --skip-tests  → 只要五个度量，约 2 秒
```

`docs\METRICS.md` 里包含：名字级缺口（`bind_diff.py --buckets`）、类型级缺口（`bind_scope.py`）、
成员形状（`shape_audit.py`）、文案 19 区（`copy_audit_report.py`，会重写 `docs\COPY_QUEUE.md`）、
缺口分桶（`backlog_report.py`）、完整套件（`dotnet test --filter "Speed!=Slow"`）。
**引用数字时写「见 docs\METRICS.md」，不要复述具体数值。**

内存纪律：available < 2 GB 时加 -m:1 且只跑相关用例；< 1 GB 停止一切构建。

## 六、下一步任务（按顺序，做完一条就更新 docs\SESSION_STATE.md 与 VERDICT.md 的对应数字）

1. 用 rea 的 investigate_feature 拿 TaskView.Toggle 练手，确认 rea↔IDA↔CUA 三条链在你手里真的通。
2. 把类型级缺口逐个结案（**未结案清单以 `replica\docs\BINDING_BACKLOG.md` 为准**，不要照抄本文件的旧列表）：
   R432 已清掉 6 个（`TaskView.Toggle`、`DataView.ViewLogs`、`CloudflareSolversView.Edit`、
   `GoogleAccountsView.Edit`、`ImapView.Configure`、`GeneralSettingsView.ProfileItems`）；
   R433 实测剩 4 个类型（见 `docs\METRICS.md` 的 `bind_scope.py` 段）：
   `Profile.Card/Username`、`ProxyTester.Name`、`MonitorView` 的 5 个绑定、`SmartActionsView.Export`。
3. 用 verify_reconstruction 把"1:1"拆成有限 claim 逐条判 pass/fail/unknown，替掉散文式结论。
4. 两个版本可互照：target\Cybersole.exe 是 5.18.32（任务目标，IDB 基于它），
   target-alt\Cybersole-5.18.35.exe 是原版今天自更新出来的（只读对照物）。
   用 compare_application_versions 看这两个只差三版的文件能反推出什么。

## 七、交付格式

每轮结束：改了什么 → 用哪条命令验证的 → 当前数字变化 → 还剩什么。数字必须来自工具输出，不许手写估计。
```

---

## 环境事实速查（给人类 / agent 查细节用）

### 关键路径

| 用途 | 路径 |
|---|---|
| 目标二进制（任务目标 5.18.32） | `D:\projects\cyber-reverse\target\Cybersole.exe`（123.26 MB，SHA256 前缀 `F2B96D9ABD76559C`） |
| IDA 数据库 | `target\Cybersole.exe.i64`（1.37 GB）+ `.id0/.id1`；备份 `target\db-backup-20261114-1617\` |
| 第二参照（5.18.35，只读） | `target-alt\Cybersole-5.18.35.exe`（123.32 MB，`0D98E405E0620AA9`） |
| 复刻件 | `replica\`（`Cybersole.sln`：Core / Http / Services / Ui / Tests） |
| 证据 | `analysis\`（`pe_strings.txt` 字符串池、`xaml_bindings.json` 绑定表、各类快照） |
| 原版数据（只读） | `%APPDATA%\Cybersole`；复刻件数据 `%APPDATA%\CybersoleReplica` |

### 工具一览（`replica\tools\`）

度量：`bind_diff.py` `bind_scope.py` `bind_shape.py` `shape_audit.py` `copy_audit_report.py`
`locale_text_gap.py` `locale_near_miss.py` `locale_coverage.py` `live_schema_diff.py` `settings_schema_diff.py`
`model_audit.py` `method_audit.py` `backlog_report.py` `count-repo.py`

安全网：`snapshot.py`（改前快照到 `tools\.mutation-backup\`）`mutation-check.py`（条数以 `running N of N` 为准，约 12–15 分钟）
`mutation-audit.py` `mutation-self-test.py`

其它：`wire_candidates.py` `endpoint-ledger.py` `endpoint-provenance.py` `flow_dump.py` `flow_filter.py`
`row_groups.py` `settings_audit.py` `clienthello_probe.py` `tls12_*.py`

### 两条链的常见故障与处置

| 症状 | 原因 | 处置 |
|---|---|---|
| `mcp__ida__*` 报 ConnectionRefused / "Did you run Edit → Plugins → MCP" | IDA 没载库，或端口漂移 | 先 `ida-mcp-doctor.ps1 -Path …`；再看 `PORT 13337` 与 `INSTANCE` |
| doctor 说 `PROXY: MISSING` | DSH 没 spawn `python -m ida_pro_mcp` | 把 `ida` 这条 MCP 关掉再打开，或重启 DSH；期间用 `analysis\ida.py` 直连 |
| IDA 弹 "unpacked version / repair?" | 上一次 IDA 非正常退出 | 备份整库 → Proceed with unpacked base / Repair |
| rea 启动即退出，提示 Node 版本 | 系统 Node 24.13.1 < 要求 24.22.1 | 用 `D:\tools\node24\…\node.exe` |
| 测试挂住 30 分钟无输出 | 可用内存 < 2 GB | 终止、清 `testhost`、改用 `-m:1` + 相关用例；必要时重启机器 |
| 中文文档在终端里显示成乱码 | 控制台渲染 UTF-8 有问题 | 用 `raw.decode('utf-8')` 验证，别改文件 |


---

## R752 交班快照（2026-11-16，重启前）

### 状态

```
完整套件        1730 通过 / 0 失败 / 0 跳过
四项度量        见 docs/METRICS.md（唯一来源，不在此硬编码）
已审候选        29 / 129（analysis/witness_ranking.tsv）
git             工作树干净
```

### 方法上的三条新结论（本轮最有价值的部分）

1. **ranking 有两处口径偏差**：R743 数「函数引用了什么」而非「目录里有什么」；
   R750 只数**带占位符**的，于是 0/1/n 三段里 0 和 1 两档整类不可见。
2. **判别式**：文案条数取决于**参数种类** —— 计数 → 三段（`No X` / `1 X` / `{0} X`）；
   名字或被比较的值 → 两段。**有因果，不是巧合。**
3. **兄弟关系在 catalog 里没有显式表达**，只体现在函数分支里。
   **按命名空间猜兄弟不成立**（`analysis/count_shaped_copy.py` 自己的缺陷，已写进 BLOCKERS §181）。

### 下一轮该做什么（按优先级）

1. **7 条未消费的计数型文案**：用 `analysis/csv_key_functions.py` 的办法，
   把每个键的引用函数扫出来再读。这是**有明确清单**的活。
2. **`analysis/count_shaped_copy.py` 的分组需要按函数修正**，否则它给出的 18 组是噪声。
3. 剩余 100 个候选按 `witness_ranking.tsv` 往下。

### 需要运行时才能解的（攒着，等凭据）

| 项 | 缺什么 |
|---|---|
| profiles 删确认的三层闸门 | 两个 delegate 的目标（R738/R739） |
| `ProfileCsv.Status.Imported` 的 `{1}` | Hex-Rays 对被折叠实参的还原；运行期可绕 |
| `EditValue\`1` 那 12 个成员的类型 | AOT 元数据表（.NET 10 不再携带 `DEHYDRATED_DATA`） |
| Pin/Unpin 标志的方向 | 一个已知状态的样本 |

**这四项都需要原版跑起来 + 登录凭据。静态侧已到边界。**

### Cybersole 需不需要开着

**不需要**。R710 起的所有轮次都是对磁盘上 `target\Cybersole.exe` 的静态反编译 + 改复刻件。
只有上表那四项需要它运行。

### R757 起：**核心优先**（YG 明令）

> 「ui先不急着复刻，先把cybersole核心的各个网站自动下单、解决风控的能力复刻出来」

**取件顺序：站点 flow 覆盖 → 风控对抗 → 请求/指纹层 → 其余（含 UI）。**

核心不是"没有"（复刻件已有约 40 个 flow 类 + 完整 solver 体系 + 305 行 `Registry.cs` 分派表），
**是覆盖范围与风控种类不齐**：缺 forter / funcaptcha(Arkose) / arkoselabs，
缺 walmart / bestbuy / newbalance / finishline 等站的显式引用。
**做法是对表补齐，不是重写。**

### R753 起：活窗口已可用，且它能看到四度量看不到的东西

运行中的是 **5.18.35**（`%LOCALAPPDATA%\Cybersole\current`），**不是对等目标 5.18.32**。
YG 判定「小版本不动前端」，所以 UI 观测可用，但**每条都要标注观测对象是 5.18.35**。

**已经用它找到第一类新差异**：复刻件用字面文字 `(i)` 冒充 `ⓘ` 图标（3 处，活窗口有 4 行带图标）。
**这类渲染差异四度量结构上看不见。**

下一步待办：`(i)` → 真图标（`UiKit.Row` 加 icon 参数 + 3 处调用），需一次构建。
