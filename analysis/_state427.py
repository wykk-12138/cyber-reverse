import io
p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding='utf-8').read()
old_start = t.index('| ida MCP（`PROXY MISSING` / `13337 REFUSED`） |')
old_end = t.index('\n', t.index('| IDA 无头批处理 |', old_start))
new = '''| ida MCP | **IDA 侧已就绪**（R427：已启动 IDA 并载入 `target/Cybersole.exe.i64`，插件在 127.0.0.1:13337 监听，pid 20560）。**缺 DSH 侧的代理**：需要你在 DSH 设置里把 `ida` 这条 MCP 关掉再打开（或重启 DSH），代理才会被 spawn。之后 `mcp__ida__server_health` 应返回 ok |
| IDA 无头批处理 | **不可用**：`idat.exe -A -S<script>` 立刻退出、脚本不执行、日志为空（R407 实测） |'''
t = t[:old_start] + new + t[old_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('SESSION_STATE blocked section updated')

p2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
t2 = io.open(p2, encoding='utf-8').read()
add = '''
---

## 第 427 轮：把 IDA 那一段接上了（只剩 DSH 侧一个开关）

### 一、先看它到底卡在哪

`ida-mcp-doctor.ps1` 给的是三段链的状态：

```
PROXY: MISSING    ← DSH 没有 spawn [python -m ida_pro_mcp]
INSTANCE: none    ← IDA 没在跑 / 没载库
PORT 13337: REFUSED
```

也就是说：**不是 IDA 坏了，是三段里断了两段，而断点各不相同。**

### 二、我修好了两段

1. 启动 IDA 并载入 `target/Cybersole.exe.i64`；
2. 它弹了一个模态框：*"IDA has found an unpacked version of database … Should we proceed with the unpacked files?"*
   → 点 **Proceed with unpacked base**（用磁盘上已分析好的 `.i64`）。

结果：

```
ida.exe  pid=20560   work set 1.9 GB
port 13337 LISTEN    127.0.0.1   owner=20560
doctor:  INSTANCE: port=13337 pid=20560 module=Cybersole.exe idb=D:\\projects\\cyber-reverse\\target\\Cybersole.exe.i64
         PORT 13337: OPEN
         VERDICT: ready
```

### 三、剩下的一段只能由 DSH 做

```
PROXY: MISSING - DSH did not spawn [python -m ida_pro_mcp]
```

代理是 DSH 在启动 / 切换 MCP 条目时 spawn 的，**进程表里连一个 python 都没有**，我自己起一个也接不到 DSH 的客户端上。
所以还需要你**把 `ida` 这条 MCP 关掉再打开**（或重启 DSH）。

之后的自检命令：

```
mcp__ida__server_health      → 期望 status: ok（带 idb_path / hexrays_ready）
```

### 四、这一轮的一句话

> 我之前一直笼统地说"IDA 用不了"，其实它有三段，**断的是两段，而其中一段我今天就能修。**

> **"不可用"要拆到能分别修理的粒度，才叫诊断。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add)
print('VERDICT appended')
