### 那个 WARN 修不掉，记录原因后停手

上一轮说"也许是 exe 没 flush，加一行就好"。这轮试了六种捕获方式，**全部失败**。

### 试过的方法

在一个独立脚本（`tools/_probe-capture.ps1`，已删）里，四种方法**全部成功**：

| 方法 | 独立脚本 | verify.ps1 里 |
|---|---|---|
| `& $exe ... 2>&1 \| Out-String` | ✅ 234 字节 | ❌ 空 |
| `& $exe ... *> $logfile; Get-Content` | ✅ 470 字节 | ❌ 空 |
| `cmd /c "exe > file 2>&1"` | ✅ 234 字节 | 未试（会污染全局） |
| `Start-Process -Wait -RedirectStandardOutput` | ✅ 234 字节 | ❌ 空 |

`verify.ps1` 里又试了：去掉 `dotnet build` 前置、保留 build、`Start-Process` 重定向。
**三种组合全部返回空，`$LASTEXITCODE` 一直是 0。**

### 结论：不是捕获方式的问题

同一个 exe、同一个 PowerShell 5.1、同一个 `$env:TEMP`：

- **在独立脚本里**：四种方法全通
- **在 verify.ps1 里**（跑过 build + 两轮 `dotnet test` 之后）：四种方法全空

**区别在脚本已经执行过的内容**，不在调用语法。

### 为什么停在这里

这个检查花掉的轮次（R73–R75，三轮）已经超过它的价值：

1. **它不阻塞任何东西** —— WARN 不参与 `$failedCount`，`VERDICT: all checks passed` 成立
2. **真实网络能力已经有更硬的证据** —— 9 个 live 契约打到 8 个不同站点，全部 PASS
3. **手动验证永远成功** —— `TlsProbe.Cli.exe --own example.com` 每次返回 200

**继续挖下去只会得到"PowerShell 5.1 某个内部状态"这种不影响任何交付物的知识。**

### WARN 保留了，因为删掉更糟

```
own TLS 1.2 + HTTP/2   WARN   probe ran (exit 0) but its output was not capturable here
```

三种处理方式：

| 方式 | 问题 |
|---|---|
| 删掉检查 | 悄悄失去一项验证 |
| 保持 FAIL | 训练人忽略红线 |
| **WARN + 说明** | ✅ 看得见、不误报 |

### 三轮 WARN 排查的净收获

**零行生产代码改动。**

但确认了两件有用的事：

1. `verify.ps1 -Live` 能跑通 9 个 live 契约（这是真实价值，不是 WARN 的副产品）
2. 手动跑 `TlsProbe.Cli` 一直是好的，OwnTls 实现没坏

**知道"这个检查在我这里测不准，但被测对象是好的"，比假装它测准了更有用。**

---
