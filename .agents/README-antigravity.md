# `.agents/` —— Antigravity 在本仓库的定制层

Antigravity（`%LOCALAPPDATA%\Programs\antigravity`，v44.9.1，语言服务器 2.32.1）会在工作区根找
`.agents/`（也认 `.agent/`、`_agents/`、`_agent/`），并从当前目录一路往上走到仓库根。
这里的东西只对本仓库生效。

## 目录内容

```
.agents/
├── plugins/cyber-reverse-toolkit/       ← 项目级 MCP + 规则 + 项目专属 skill（手写，进 git）
│   ├── plugin.json                      # 清单，必须是这个文件名
│   ├── mcp_config.json                  # ida / cua / rea / seep 四个服务器
│   ├── rules/AGENTS.md                  # IDA 段链就绪判据、别做的事、内存纪律
│   └── skills/antigravity-tool-map/     # 「哪个工具干哪件事」+ 度量/体检命令
├── skills/                              ← 第三方 skill 的**副本**（派生，不进 git）
│   ├── ida-reverse/                     ← D:\projects\Seep-Reverse-Lab\Tool\skill\ida-reverse
│   ├── softseep/
│   ├── client-license-validation-bypass/
│   ├── reverse-engineering/             ← …\Tool\skill\safe-skills\reverse-engineering
│   ├── radare2/
│   └── cua-driver/                      ← C:\Users\wykk\.cua-driver\skills\cua-driver
└── README-antigravity.md                # 本文件
```

`skills/` 是**副本**，由 `tools/sync-antigravity-skills.ps1` 从源刷新（源改了就跑一次；它带 RPC 自检，
末尾打印 `VERDICT: all workspace skills loaded` 才算同步到位）。为什么不是 junction、为什么不是
`skills.json`，见下面「实测记录」。

仓库根的 `AGENTS.md` 会被 Antigravity 当**规则**自动加载（任务本体、方法论优先级、证据规则、
度量口径）。这里只补它没写的部分。

## 格式依据（读的是 Antigravity 自己带的文档，不是猜的）

文档在 `~/.gemini/antigravity/builtin/skills/agy-customizations/docs/`：

| 事实 | 依据 |
|---|---|
| MCP 文件名 `mcp_config.json`，结构 `{"mcpServers": {...}}` | `mcp_servers.md` |
| stdio 用 `command` / `args` / `env` / `cwd`；另有 `url` / `headers` / `disabled` / `variables` | `mcp_servers.md` + `plugin` skill 的允许键清单 |
| 插件 = `plugins/<name>/plugin.json`，可选 `mcp_config.json` / `rules/` / `skills/` / `hooks.json` | `plugins.md` |
| 工作区定制根 = `.agents/`，插件放 `.agents/plugins/` | `plugins.md` + 语言服务器内嵌指令「Workspace Customizations Root: ".agents"」 |
| Skill = `skills/<name>/SKILL.md`，frontmatter 必含 `name` + `description` | `skills.md` |
| 规则文件上限 24,000 字节；全局规则预算 20,000 token | `rules.md` |

## 实测记录（v44.9.1，2026-11-17 23:5x）

语言服务器的本地 RPC 可以直接问「你现在认到哪些插件/技能」，这是唯一不靠猜的判据：

```powershell
# 端口与令牌在 ~/.gemini/antigravity/daemon/hub_<port>.json 里（取最新写入的那个）
$meta = Get-Content "$env:USERPROFILE\.gemini\antigravity\daemon\hub_15390.json" -Raw | ConvertFrom-Json
$base = "http://localhost:$($meta.httpPort)/exa.language_server_pb.LanguageServerService"
$h    = @{ 'x-codeium-csrf-token' = $meta.csrfToken }
$body = '{"workspaceUris":["file:///d:/projects/cyber-reverse"]}'
Invoke-RestMethod "$base/GetAllPlugins" -Method Post -ContentType application/json -Headers $h -Body $body
Invoke-RestMethod "$base/GetAllSkills"  -Method Post -ContentType application/json -Headers $h -Body $body
```

`workspaceUris` 是关键：**不带它，工作区的插件不会被发现**（这就是 Customizations 页面在
"No Project" 状态下显示 `Plugins 0 / MCP Servers 0` 的原因，不是配置没写对）。

| 问什么 | 结果 |
|---|---|
| `GetAllPlugins` + 本仓库 URI | 认出 `cyber-reverse-toolkit`，路径 `file:///d:/projects/cyber-reverse/.agents/plugins/cyber-reverse-toolkit` |
| 它的 MCP 服务器 | 4 个，名字被加了插件前缀：`cyber-reverse-toolkit_ida` / `_cua` / `_rea` / `_seep`，`configPath` 指向本仓库的 `mcp_config.json` |
| 它的规则 | `d:\projects\cyber-reverse\.agents\plugins\cyber-reverse-toolkit\rules\AGENTS.md` |
| `GetAllSkills` | 20 条 = 13 条内置 + `antigravity-tool-map` + 6 条 `.agents/skills/*` |

三条**踩过的坑**（都是实测，不是推断）：

1. **NTFS junction 不认。** 用 junction 把 `.agents/skills/<name>` 指到源目录，`GetAllSkills` 里
   一条都没有；把同名目录换成真实副本，一秒就出现。所以只能用副本。
2. **`.agents/skills.json` 清单不生效。** 按 `json_configs.md` 的格式写过 `entries`
   （`/d:/…`、`D:/…`、`d:/…`、`\\…`、`~/…` 五种绝对路径形式，带/不带 `include_only` 都试过），
   `GetAllSkills` 始终只有内置 + 插件自带的那些。这个功能在这版里没接上。
3. **MCP 只放在插件里。** agent 内嵌指令说 `mcp_config.json` 也能放在任意定制根下，而
   `mcp_servers.md` 只写了「全局 / 插件」。为了不赌、也避免同一服务器注册两遍，这里只走插件路。

## 已证 / 未证

- **已证**：插件被发现、4 个服务器带正确命令行被登记、规则被登记、6 个技能被加载。
- **未证**：这四个服务器在一次真实对话里能不能拉起并返回工具列表 —— 那要开一轮对话才会发生。
  间接证据：其中三条命令行（ida / cua / rea）与本机 DSH 现在正在用的完全相同，而 DSH 侧这三个
  服务器此刻是连着可用的；`seep` 单独验过 `import` 成功并导出了 22 个工具函数。
- 前缀不是猜的：`serverName` 字段实测就是 `cyber-reverse-toolkit_<原名>`。

## 怎么撤销

- 只关某个 MCP：在 `mcp_config.json` 里给该服务器加 `"disabled": true`。
- 关整个插件：Antigravity 设置里禁用 `cyber-reverse-toolkit`（或 Customizations 页面切掉它）。
  **不要手改 `~/.gemini/config/config.json`**（绕过语言服务器的热重载，还会和并发写入打架）。
- 关技能：删 `.agents/skills/<name>` 即可，源仓库不受影响；要恢复就跑一次同步脚本。
