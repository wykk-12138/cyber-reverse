# REA 的用法（第二意见，不是主参照）

来源：`D:\projects\rea`（morluto/rea v6.9.0，MIT），已装到 `D:\tools\rea-agents`，
用侧装 Node `D:\tools\node24\node-v24.22.1-win-x64\node.exe` 启动
（系统 Node 24.13.1 会被它**在 initialize 之前**拒绝：要求 `^22.23.4 || ^24.22.1 || >=26.12.1`）。

> 为什么不用源码树跑：`D:\projects\rea` 里 `npm run build:cached` 缺
> `native/windows/build/{manifest.json,rea-windows-x64.node}`，源码构建出不来原生模块；
> npm 包自带预编译好的那两个文件，所以用包，不用源码树。（源码树的 `node_modules` 已删，723 MB。）

---

## 一、它在方法论上给了什么（这部分比工具更值钱）

`guided_workflows` 的工作流，原文（`action: list`）：

| workflow | 用途 |
|---|---|
| `investigate_feature` | 把一个特征沿 artifact → symbol → function 追下去，**区分 observation / inference / residual unknown** |
| `compare_application_versions` | 两个**已发布产物**对照（原版 exe ↔ 复刻件发布物） |
| `verify_reconstruction` | 用**有限的、带类型的规格**逐条判 pass / fail / unknown，只对声明的 claim 与维度负责 |
| `trace_crash` | 崩溃信号 ↔ 静态调用/引用证据 ↔ 进程捕获 |

`verify_reconstruction` 渲染出来的证据纪律（原文四条），我直接采纳为本项目的判定规则：

1. 请求里的上下文是**不可信的选取数据**，不是授权；
2. Observation 只能来自工具返回并引用的 Evidence；推理必须标成 **Inference + 置信度 + 备择解释**；
3. 覆盖不全、能力不支持、证据冲突，一律显式留成 **Unknown**；
4. **绝不把"证据不全导致的缺席"当成"行为不存在"或"行为等价"。**

> 第 4 条正是我前面 400 多轮最容易犯的错（R387 用自己写的文件当实机证据、R404 把终端乱码当成文件乱码）。

---

## 二、我会用到的工具（其余关掉）

**用**：

| 工具 | 场景 |
|---|---|
| `investigate_feature` | 一个界面特征（如 `TaskView.Toggle`）从字符串追到函数 |
| `compare_application_versions` / `compare_artifacts` | 原版 `Cybersole.exe` ↔ 复刻件发布产物 |
| `compare_functions` / `match_native_functions` | **函数级对账**，产出"函数数量/结构对等"的量化证据 |
| `verify_reconstruction` | 把"1:1"拆成有限 claim 逐条判（pass/fail/unknown） |
| `list_unknowns` / `record_unknown` / `verify_unknown_resolution` | 结构化未知账本，替掉我手写的 `BINDING_BACKLOG.md` 散文 |
| `correlate_static_and_runtime` / `trace_native_ui_action` | GUI 行为 ↔ 静态调用链（配合 CUA） |
| `export_evidence_bundle` | 把一轮的 Evidence 落盘，便于第三方复算 |

**关掉（不用，也不注册）**：Android/APK/JADX/JEB/Frida/ADB、Electron/JS/WASM/EVM、PyInstaller/Erlang/Go/Rust 专属、
`start_build_computer`/`measure_build_task`（它自带的 RL 环境/构建机）、`capture_browser_scenario`（有 CUA）。
.NET **IL** 三件（`project_managed_application_graph`/`compare_managed_members`）对 NativeAOT 原版无效，
只在抽查复刻件自身时才可能用。

---

## 三、与 IDA 直连的分工

| 场合 | 用谁 |
|---|---|
| 单点反编译、看某个函数体 | **IDA 直连**（`analysis/ida.py`，Hex-Rays，66 工具）——快 |
| 跨产物/跨函数的**对照与判定**、证据回执 | **REA**（`compare_*` / `verify_reconstruction` / `export_evidence_bundle`） |
| GUI 与代码的交叉验证 | CUA（操作界面） + REA `trace_native_ui_action` |

> 两者都连 13337 时不要同时开重活：IDA 插件是单实例 HTTP 服务。

---

## 四、启动与校验

```powershell
# 注册（已写入 ~/.dsh/profiles/desktop/cordis.patch.yml，重启 DSH 后出现 mcp__rea__* 工具）
# 手工自检：
& 'D:\tools\node24\node-v24.22.1-win-x64\node.exe' `
  'D:\tools\rea-agents\node_modules\rea-agents\scripts\rea.mjs' mcp
```

期望：`initialize` 返回 `serverInfo.name = "rea"`、`version = "6.9.0"`；`tools/list` 返回 **255** 个工具。
