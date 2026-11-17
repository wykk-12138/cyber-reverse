---
name: antigravity-tool-map
description: >-
  Use when starting or resuming work in D:/projects/cyber-reverse inside Antigravity: maps each job
  (decompile a function, read a string, drive IDA's dialogs, cross-check two binaries) to the exact MCP
  server and tool-name prefix this workspace's plugin provides, and gives the readiness checks that
  separate "IDA is not loaded" from "the MCP entry is broken".
---

# 这个工作区里，哪个工具干哪件事

本插件 `cyber-reverse-toolkit` 注册四个 MCP 服务器。Antigravity 会把插件里的服务器**加前缀**，
所以工具名形如 `cyber-reverse-toolkit_ida_*`。**按服务器找工具，不要按名字猜**。

## 一、任务 → 服务器

| 你要做的事 | 用哪个 | 说明 |
|---|---|---|
| 反编译一个函数 / 看伪代码 | **ida** | 主参照。结论的出处 |
| 查一个字符串在镜像里有没有（**反向结论**必须走这条） | **ida** | `analysis/pe_strings.txt` 是**抽样**，搜不到 ≠ 不存在 |
| 交叉引用 / 调用者 / 被调用者 | **ida** | 不要用符号计数推断"接线还是逻辑"，读伪代码 |
| 列出函数清单 / 段信息 / 命名空间 | **ida** | |
| 确认 IDA 处于什么状态（有没有对话框、库载没载入） | **cua** | 截图 + 无障碍树 |
| 点掉 IDA 的模态框、在 GUI 里定位一个控件 | **cua** | 只做消歧/定位，不做证据 |
| 两个函数的伪代码/CFG 对比 | **rea** | 第二意见，用来裁决分歧，不单独当证据 |
| 二进制级退化路线（IDA 不可用时） | **seep** | radare2 工具 + 知识库检索 |

## 二、IDA 就绪检查（三句话）

1. 调一个 ida 工具；报 `Did you run Edit -> Plugins -> MCP` ⇒ **IDA 没开或库没载入**，不是 MCP 坏了。
2. 端口 `13337`；报 ConnectionRefused ⇒ 端口漂移，重启这个 MCP 服务器即可，**不要改 JSON**。
3. 判据是**再读一次窗口没有对话框** + **工具返回真实数据**，不是"我点了 N 次"。

体检脚本：`powershell -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 [-Path <二进制>]`
，看到 `VERDICT: ready` 才算可用。

## 三、开 IDA 的顺序（别跳步）

打开已有的 `target\Cybersole.exe.i64` → 「加载现有(L)」→（若问）「Proceed with unpacked base」
→（若问）「Repair」/「是(Y)」→「请稍候…」就等 →（若警告）「确定」→ cua 截图确认无对话框。

**永不重建这个库**：它 1375 MB，重新分析要几小时。

## 四、跑度量（改完代码必做）

```powershell
cd D:\projects\cyber-reverse\replica
python tools\metrics_report.py --skip-tests   # 约 2 秒，只要度量
python tools\metrics_report.py                # 五个度量 + 完整套件
```

- 唯一事实源是 `docs/METRICS.md`（生成物）。**不要在任何文档里手写这些数字。**
- IDA 不在时 `vendor_coverage.py` 会印出 `missing=0` 并正常退出 —— **那是假零**，
  先让 IDA 就绪再跑，或只信 `controls ok=True` 的那一次输出。
- 动手写实现之前先跑 `python tools\where_is.py <名字>`：它按 **implementation / analysis / test / doc**
  四组报位置，先读 implementation 组，再决定要不要写新的。
