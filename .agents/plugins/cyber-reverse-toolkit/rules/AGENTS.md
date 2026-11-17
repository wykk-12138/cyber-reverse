# 本仓库在 Antigravity 下的工具链约定（cyber-reverse-toolkit 插件提供）

> 仓库根的 `AGENTS.md` 已由 Antigravity 作为规则自动加载（任务本体、方法论优先级、证据规则、
> 度量口径）。**本文件只补它没有覆盖的部分**：MCP 工具怎么算"就绪"、失败怎么归因、别做的事。

## 1. MCP 服务器由谁提供

插件 `cyber-reverse-toolkit` 的 `mcp_config.json` 注册四个服务器，工具名带插件前缀（`<plugin>_<server>_<tool>`）：

| server | 干什么 | 什么时候用 |
|---|---|---|
| **ida** | IDA Pro MCP，反编译 / xref / 函数清单 / 字符串查询 | **主参照**。所有"原版怎么实现的"结论都从这里出 |
| **cua** | 驱动本机 GUI（截图、无障碍树、点框、读窗口） | **只用于消歧、去噪、定位**；以及点掉 IDA 的模态对话框 |
| **rea** | 第二意见（`compare_functions` / `match_native_functions`） | 与 IDA 结论打架时用来裁决，不单独当证据 |
| **seep** | radare2 跨架构 / 知识库检索 | 降级路线；IDA 不可用时的替代入口 |

## 2. IDA MCP 的就绪判据（**唯一判据，不看"点了 N 次"**）

三段链：`客户端 → stdio 代理(MCP server) → IDA 插件 HTTP 127.0.0.1:13337`。
**第三段只在 IDA 已载入数据库之后才存在** —— 空 IDA 停在"快速开始"界面不会起服务。

- 报 `Failed to complete request ... Did you run Edit -> Plugins -> MCP` = **IDA 没开 / 没载入库**，
  不是 MCP 没注册。**不要重装、不要改配置。**
- 端口默认 `13337`，被占用会 `+1` 递增；stdio 代理在**启动那一刻**锁死端口。一旦漂移就是 ConnectionRefused。
- **就绪的判据**：再读一次窗口状态，**没有对话框、且工具调用返回真实数据**。
- 一键体检（含开 IDA + 点模态框 + 等就绪）：
  `powershell -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 [-Path <二进制>]`
  输出 `VERDICT: ready` 才算可用；`HINT:` 开头的那行就是下一步动作。

## 3. 开 IDA 的固定流程（每次打开都要走，别跳）

1. 开 IDA → 打开 **已有** 的 `.i64`：`target\Cybersole.exe.i64`（1375 MB）。
   弹"数据库已存在" → 选 **「加载现有(L)」**。**永远不要让它重建**。
2. 弹"版本/打包不一致" → 「Proceed with unpacked base」；弹 `id0 未正常关闭` → 「Repair」/「是(Y)」。
3. 出现「请稍候…」→ **等**，别连点；出现 inconsistencies 警告 → 「确定」。
4. 用 `cua` 截图确认窗口状态，直到**再读一次没有对话框**，再做第一次工具调用。

## 4. 不许做的事

- **不许覆盖 / 重建那个 1375 MB 的 IDB**（重新分析要几小时，且会丢掉已有命名）。
- **不许把 GUI 观察当主证据**。截图只能用来"确认 IDA 在哪个状态"或"这个控件长什么样"，
  不能用来回答"函数做了什么"。
- **不许把复刻件写出的 JSON 当证据**（`settings.json` / `tasks.json` / `solvers.json` /
  `checkoutHistory.json`）—— 那是我们自己的输出，引用它等于循环论证。
- **永不写入** `%APPDATA%\Cybersole` 和 `%LOCALAPPDATA%\Cybersole`（原版数据目录，只读）。
- **不许在任何文档里硬编码度量数字** —— 唯一事实源是 `docs/METRICS.md`（由
  `python tools/metrics_report.py` 生成）。
- **不许对 NativeAOT 字符串 `chars_va` 直接查 xref 得 0 就判「无引用/不可得」** —— 冻结字符串对象头在 **`chars_va - 12`**，须用 `xrefs_to(chars_va - 12)` 或 `analysis/disp32_scan_any.py` → `site_to_func.py` 定位，再用 `analysis/names_at.py` 还原伪代码里的 `&off_146xxxxxx`。
- **不许往 `replica/src/` 新增静态逆向台账/缺口免责类**（如 `*Gaps`、`*Wiring`、`*Witness`）—— 考据与缺口记录归 `docs/`，`replica/src/` 只写可执行的运行时业务代码。

## 5. 内存纪律（这台机器因为内存耗尽崩过多次）

- `available < 2 GB` ⇒ 构建/测试只加 `-m:1`。
- `available < 1 GB` ⇒ **停止一切构建**。
- IDA 载入 1375 MB 库本身吃内存：先看可用内存，再决定要不要开第二个重工具（rea / seep）。

## 6. 结论口径

- 每条结论要能被第三方用**可复现命令**重算；"我读了代码觉得是" 不算。
- 观察 / 推断 / 未知 三种状态必须分开写，不许用"大概完成度"代替。
- 计数先问"这个来源是全量还是抽样"；零要有对照才能读。
