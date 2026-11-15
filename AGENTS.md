# 本项目的作战约定（cyber-reverse）

## 0. 任务本体

把 `Cybersole.exe` 5.18.32（**.NET 10 NativeAOT**，无 IL —— 依据 PDB 路径 `bin/Release/net10.0/win-x64/native/`，R431 用 `pe_triage.py` 读出）
在 `replica/` 里做成**功能 1:1** 的复刻件（复刻件本身用 .NET 8 + Avalonia，目标框架不必跟随原版）：
函数数量对等、每个函数功能相等、效率相近；命名可以不同，不要求字节级相同。

验收口径：**反编译优先**（主参照），**GUI 观察只用于消歧、去噪、定位**（辅助），一切结论要能被第三方用可复现命令重算。

---

## 1. 方法论优先级（YG 明令，2026-11-14）

> 「我的规矩不是硬性的……这两个逆向工具的仓库里的方法才是更专业的，
>  **优先按 seep-reverse-lab 的方法论来**，然后把 rea 里你认为有用的工具用上。
>  用不上的功能就关掉。切忌你自己想当然的写一个工具出来，优先用这些公开的仓库，
>  他们经历过反馈迭代，绝对比你一拍脑门写出来的工具专业多了。」

落地成四条硬规则：

1. **方法先抄，不先发明。** 遇到「怎么做」的问题，先读
   `D:\projects\seep-reverse-lab\{MANUAL, Tool/skill, Tool/prompts, AGENTS.md}`；
   找不到再读 `D:\projects\rea\{src, docs/reference}`；两处都没有，才自己设计。
2. **工具先用公开的。** 反编译/对照/追踪类能力，优先
   `seep-reverse-lab` 的 MCP 与 skill、`rea` 的 MCP 工具、`ida_pro_mcp`（直连 13337）。
   **只有在公开仓库确实覆盖不到时**才写脚本；写的时候必须在文件头注明
   「为什么现有的不够用」。
3. **能力用完就关。** 用不上的 MCP 条目、skill、后台服务不常驻 ——
   常驻的每一个进程都是故障面和内存占用。
4. **版本问题不是理由。** 缺 Node、缺依赖、缺 build，由我来装（侧装、不覆盖系统运行时）。

### 已确认的落位

| 资源 | 用途 | 状态 |
|---|---|---|
| `seep-reverse-lab/MANUAL/IDA-PRO.md` | IDA/MCP 三段链、端口、就绪判定 | 已采用 |
| `seep-reverse-lab/MANUAL/POC-VALIDATION.md` | 验证口径（待读） | 待采用 |
| `ida-reverse` skill | 启动 IDA → 轮询 13337 → MCP 工具矩阵 → 失败降级 r2 | 已加载 |
| `analysis/ida.py` | **过渡件**：DSH 代理缺失时直连插件的 MCP 客户端（66 工具）。代理稳定后应退役 | 在用 |
| `rea` MCP（`D:\projects\rea`） | 第二意见：`compare_functions`、`match_native_functions`、`trace_application_feature`、`compare_application_versions` | 建设中 |
| 侧装 Node 24.22.1 | `rea` 要求 Node ≥24.22.1，系统 Node 24.13.1 被拒 | 已装 `D:\tools\node24\node-v24.22.1-win-x64\node.exe` |
| `exe-reverse` skill | 仓库在 `D:\projects\exe-reverse\skills\exe-reverse`（Codeberg `reverse-skill-lab/exe-reverse`）。**R432 起不再注册为 skill**（见下），只按白名单直调两个只读脚本 | 已停用注册，脚本可用 |

`exe-reverse` 的用法边界（R432 收紧）：

- **不再注册为 skill**：junction 已从 `.dsh/skills/` 移到 `.dsh/skills-disabled/`，新会话的技能目录里不会再出现它。
  原因：它的交付判据是"打补丁后仍能运行"，与我们"忠实重实现"方向相反，容易被新 agent 当成方法论主导。
- **仍可用的只有两个只读脚本**（绝对路径直调，不需要加载 skill）：
  ```
  D:\projects\IDA-pro\python311\python.exe D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_triage.py <exe>
  D:\projects\IDA-pro\python311\python.exe D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_diff.py   <exeA> <exeB>
  ```
  R431 实测价值：查出原版是 **.NET 10**（PDB 路径）、39 导出全是 Brotli、TLS callback 存在、5.18.32↔5.18.35 六节全重排。
- 需要恢复注册时（一行）：
  `New-Item -ItemType Junction -Path D:\projects\cyber-reverse\.dsh\skills\exe-reverse -Target D:\projects\exe-reverse\skills\exe-reverse`
- `EXEREV_TOOLS` 仍持久化为 `D:\projects\IDA-pro;C:\Program Files\7-Zip`（`static_disassembly`
  与 `installer_inspect` 靠它解锁）。它要求的方法论与 `seep-reverse-lab` 冲突时，以 `seep-reverse-lab` 为准（见 §1）。

`rea` 里**明确不用**的能力：Android/APK/Electron/JS/EVM/PyInstaller 各工具；
.NET **IL** 三件（`project_managed_application_graph`、`compare_managed_members`）对 NativeAOT 原版无效，
最多用来抽查复刻件自身。

---

## 2. 证据规则（踩过坑，别重犯）

1. **可信**：字符串池 `analysis/pe_strings.txt`、locale 键、`docs/xaml_bindings.json`、原版自己写的 `.cyb` 备份、反编译结果。
2. **不可信**：复刻件写出的 `settings.json` / `tasks.json` / `solvers.json` / `checkoutHistory.json`
   —— 那是我们自己的输出，引用它就是循环论证（R387 踩过）。
3. **永不写入** `%APPDATA%\Cybersole`（原版数据目录，只读）；`%LOCALAPPDATA%\Cybersole` 也只读。
   有守卫 `EverythingTheReplicaWritesStaysUnderItsOwnDataRoot` 看着。
4. **判断文件编码只看字节**（`raw.decode('utf-8')`），这个控制台把 UTF-8 中文渲染成乱码，曾经害我误判"文件乱码"（R404）。
5. **不要在文档里复述坏字符。** 说明"这里有编码问题"时只写位置和成因，**绝不把那串坏字符抄进来**——
   `SourceEncodingTests.NoSourceFileContainsMojibake` 会红，而且红的是文档本身。
   这条已经犯过四次（R439、R477、R484、R487），每次都是"为了举例而抄一遍"。
6. **"没跑成" ≠ "通过"**，也 ≠ "失败"。内存不足导致的崩溃必须单列，不许混进结论（R419/R424/R425）。

---

## 2.5 目标与循环（新会话从这里接手）

新会话的 goal 原文、每轮五步循环、完成判据（a–e）、Unknown 的判定标准，都在 `docs/GOAL.md`。
一句话：**每轮从 `replica/docs/BINDING_BACKLOG.md` 取一条未结案项，取证 → 落实现 → 复算 → 更新数字**，
完成判据必须逐条附证据，不许用"大概完成度"代替。

## 3. 改代码的纪律

**「方法改成绑定属性」的固定连带清单**（R468–R499 踩了七次，七次的错因就这六项）：

```
把 public void X() 改成绑定属性，必须同时做：
  (a) public ICommand X { get; }
  (b) 构造函数里 X = new RelayCommand(XCore)   （bool 返回则 () => XCore()）
  (c) using Cybersole.Core.Models (RelayCommand) 与 using System.Windows.Input (ICommand) —— 两个都要
  (d) 类内 X() 调用        -> XCore()
  (e) 类内 X 方法组引用    -> () => X.Execute(null)
  (f) 测试里 "public void X(" 断言 -> 同时接受 "public ICommand X"
  (g) 改名正则**限定在类体内**，且不能命中 `_other.Member()` —— 别的对象可能有同名方法
  (h) bool 方法包装后返回值没了：先看测试有没有消费它，有就改成断言副作用
      —— **例外**：若该 bool 本身是被测行为、且无副作用可断言（如"没宿主窗口所以什么都没关"），
      就保留 `XxxCore` 为 `public` 供测试调用，**不要削弱断言**
```

`(c)` 最容易漏（两个 using 在同一个文件里缺一个就报 CS0246）；
`(d)(e)` 必须单独扫（脚本只改定义，不改调用点）；
`(f)` 一律改成 `GetMembers()` 或双形式接受，别等红了再改。

- 改前先 `python tools/snapshot.py`（快照到 `tools/.mutation-backup/`），改后一次只跑相关用例。
- **禁止按行号做手术**（R352 删掉过四个类，靠备份救回）；只按整块锚点替换。
- 新加 action 成员 → 必须是 `ICommand` 属性（绑定表里 action 就是属性）。
- 断言行为，不断言注解。
- 守卫红了先判断：是行为变了（改代码）还是只是形状变了（改数字，并写清原因）。
- 数字随事实走：`docs/PARITY.md`、`docs/SESSION_STATE.md`、`replica/docs/BINDING_BACKLOG.md` 的头条数字必须等于度量工具的当前输出。

---

## 4. 度量与验证（当前基线）

**单一事实源：`docs/METRICS.md`** —— 由 `python tools/metrics_report.py` 生成，带时间戳与逐条命令。
**不要在任何文档里硬编码这些数字**（R433 裁决 1：数字漂移从此是生成问题，不是纪律问题）。

```
# 生成（在 replica/ 下）
python tools/metrics_report.py               # 五个度量 + 完整套件
python tools/metrics_report.py --skip-tests  # 只要度量，约 2 秒

# 当前值见 docs/METRICS.md（R433 生成时：名字级 16 / 类型级 4 / 形状 275 / 文案 5 / 套件 1607）
```

内存纪律：`available < 2 GB` 时只用 `-m:1` 跑相关用例；`< 1 GB` 时停止一切构建。

**浏览器依赖用例不进默认全量**（R493）：`VoiceListTests` / `GlobalSurfaceTests` / `KeyOrderDispatchTests` /
`PatchJournalTests` / `PruneWhitelistTests` / `NetworkRecorderLiveTests` 要驱动真 Chrome，端点起不来时
每个耗约 2 分钟。2026-11-14 连着跑几轮全量导致**整机内存耗尽、系统重启**。`metrics_report.py` 已默认排除，
排除理由写在代码里；需要时**一次跑一个类**：

```
dotnet test --filter "FullyQualifiedName~VoiceListTests" -m:1
```

---

## 5. 一句话总结

> **抄公开仓库的方法，用公开仓库的工具，只在它们够不到的地方动手；**
> **每一条结论都要能被重算，每一个数字都要和事实对齐。**
