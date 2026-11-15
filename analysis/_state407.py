import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 407 轮：再次尝试打通反编译通道（失败，但把失败写得可复现）

### 一、两条路都试了

| 路线 | 结果 |
|---|---|
| ida MCP（`mcp__ida__*`） | 仍然 `PROXY MISSING / PORT 13337 REFUSED` —— 代理只能由 DSH 启动 |
| **IDA 无头批处理**（`idat.exe -A -S…`） | **进程立刻退出，脚本从未执行** |

无头尝试的观测：

```
Start-Process idat.exe -A -Lida_log.txt -S<probe.py> target\\Cybersole.exe.i64
exited: True   code: (空)
probe file: MISSING          ← 脚本没跑
stdout / stderr: 空
ida_log.txt: 无
```

探针脚本只有三行（写一个文件、`qexit(0)`），所以不是脚本本身的问题 —— 这台机器上的 `idat.exe` 是**绿色版**，
批处理模式直接退出、不给任何诊断。

### 二、结论与出路

反编译通道要恢复，只有一条路：**用 GUI 的 IDA 打开 `.i64`，并让 DSH 重新启动 `ida_pro_mcp` 代理**
（或重启 DSH）。两条都需要你在方便时操作一次 —— 我不再自动重试，避免把时间耗在同一个死路上。

### 三、这一轮的一句话

> 我把"试过、怎么试的、看到什么、为什么不再试"全写下来了。

> **失败也要写成别人能复现的样子，否则下一轮还会重来一遍。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('''| ida MCP（`PROXY MISSING`） | 用户重启 DSH 或重开 IDA + 载入库 |''',
'''| ida MCP（`PROXY MISSING` / `13337 REFUSED`） | 用 GUI 的 IDA 打开 `target/Cybersole.exe.i64`，并让 DSH 重启 `ida_pro_mcp` 代理（或重启 DSH） |
| IDA 无头批处理 | **不可用**：`idat.exe -A -S<script>` 立刻退出、脚本不执行、日志为空（R407 实测） |''')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE blocked section updated')
