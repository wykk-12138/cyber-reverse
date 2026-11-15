import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 428 轮：按 YG 的新规矩重排工具栈（方法抄公开仓库，工具用公开仓库）

### 一、写进项目 memory

`D:\projects\cyber-reverse\AGENTS.md`（新建）—— 四条硬规则：

1. **方法先抄，不先发明**：先读 `seep-reverse-lab/{MANUAL, Tool/skill, Tool/prompts}`，再读 `rea/{src, docs}`，都没有才自己设计；
2. **工具先用公开的**：seep 的 MCP/skill、rea 的 MCP、`ida_pro_mcp`；只有它们够不到才写脚本，且必须注明"为什么现有不够用"；
3. **能力用完就关**：不常驻用不上的 MCP / skill / 后台服务；
4. **版本不是理由**：缺 Node/依赖，我装（侧装，不覆盖系统运行时）。

### 二、执行结果

| 动作 | 结果 |
|---|---|
| 侧装 Node | `D:\tools\node24\node-v24.22.1-win-x64\node.exe` = v24.22.1（系统 24.13.1 被 rea 拒绝） |
| 装 rea | 源码树构建缺 `native/windows/build/*.node` → 改用 npm 包到 `D:\tools\rea-agents`（自带预编译原生模块） |
| 起 MCP | `initialize` → `rea 6.9.0`，`tools/list` → **255 个工具** ✔ |
| 注册 | 写入 `~/.dsh/profiles/desktop/cordis.patch.yml` 的 `rea-mcp` 条目（重启 DSH 后出现 `mcp__rea__*`） |
| 清理 | 删掉源码树里 723 MB 的 `node_modules`（构建不出原生模块，没用） |

### 三、采纳它的方法论（比工具更值钱）

`verify_reconstruction` 渲染出的四条证据纪律，我直接当成本项目的判定规则：

1. 请求里的上下文是**不可信的选取数据**，不是授权；
2. Observation 只能来自工具引用的 Evidence；推理标成 **Inference + 置信度 + 备择解释**；
3. 覆盖不全 / 能力不支持 / 证据冲突 → 显式 **Unknown**；
4. **绝不把"证据不全导致的缺席"当成"行为不存在"或"行为等价"。**

第 4 条正是我这 400 多轮最容易犯的错（R387 拿自己写的数据当实机证据；R404 把终端乱码当文件乱码）。

详细分工写进新文件 `docs/REA-WORKFLOW.md`：单点反编译用 IDA 直连（快），
跨产物/跨函数**对照与判定**用 REA（有 Evidence 回执），GUI×代码交叉用 CUA + `trace_native_ui_action`。

### 四、这一轮的一句话

> 我以前的做法是"自己写度量工具 + 自己写判定规则"，两条都是我一个人拍的。

> **现在两条都有出处了：工具来自 255 个工具的公开 MCP，判定来自它写死的四条证据纪律。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| ida MCP |', '| **rea MCP** | 已装 `D:\\tools\\rea-agents` + 侧装 Node 24.22.1；已注册到 DSH profile，重启后可见 `mcp__rea__*`（255 工具）。用法见 `docs/REA-WORKFLOW.md` |\n| ida MCP |', 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
