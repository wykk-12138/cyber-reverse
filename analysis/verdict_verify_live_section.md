### `verify.ps1 -Live`：把契约接进常规验证

之前 `LiveContractTests` 是 `Trait("Speed","Slow")`，而 `verify.ps1` 用 `--filter "Speed!=Slow"`
——**那 9 个契约永远不会在常规流程里跑**。

加了 `-Live` 开关：

```powershell
pwsh -File tools\verify.ps1           # 构建 + 离线测试 + 文档
pwsh -File tools\verify.ps1 -Live      # 加上 9 个 live 契约（~15s，要网络）
pwsh -File tools\verify.ps1 -SkipLive  # 跳过 TLS 探测
```

### live contracts 第一次进 verify 就通过了

```
release build         PASS
unit tests            PASS   exit 0
live contracts        PASS   all platform decisions still hold
store modules         PASS   61 registered
```

失败时的输出会点名是哪个契约：

```
live contracts  FAIL  drifted: ConverseIsDemandwareAndNotShopify, BstnServesItsBeastApi…
```

**「drifted」这个词是故意的**——契约红了不一定是代码坏了，多半是站点变了。

### 途中发现一个真正的脚本缺陷

`own TLS 1.2 + HTTP/2` 一直在 FAIL，但**手动跑 `TlsProbe.Cli.exe` 每次都返回 200**：

```
OwnTls transport -> https://example.com
  HTTP 200  577 bytes  proto=h2  transport=own-tls12
```

在 `verify.ps1` 里试了三种捕获方式，全部拿到空字符串：

| 写法 | 结果 |
|---|---|
| `& $exe ... 2>&1 \| Out-String` | 空 |
| `$out = & $exe ... 2>$null` | 空 |
| `& $exe ... *> $logfile; Get-Content $logfile` | 空 |

**`$LASTEXITCODE` 一直是 0**——进程跑了、成功了、只是输出没被捕获。

这是 Windows PowerShell 5.1 在这个宿主下对 native exe 输出的问题，**不是 TLS 实现的问题**。

### 处理方式：加一个 WARN 档，而不是继续让它红

```powershell
function Warn($name, $detail) {
    $script:results += [pscustomobject]@{ Check = $name; Result = 'WARN'; Detail = $detail }
}
```

```powershell
if ($ok) {
    Check 'own TLS 1.2 + HTTP/2' $true $line.Trim()
} elseif ($probeExit -eq 0 -and -not ($live -match 'HTTP ')) {
    # 进程成功但输出读不到 —— 捕获问题，不是 TLS 问题
    Warn 'own TLS 1.2 + HTTP/2' 'probe ran (exit 0) but its output was not capturable here'
} else {
    Check 'own TLS 1.2 + HTTP/2' $false $line.Trim()
}
```

**为什么不用 FAIL**：

> 一个长期红着的检查会训练人忽略红线，这比明说"读不到"更糟。

WARN 不参与 `$failedCount`，所以 `VERDICT: all checks passed` 仍然成立，但那一行还看得见。

### 一个我之前误判的地方

之前几轮我都以为 `verify.ps1` 的 exit code 是 1，因为 `[exit code: 1]` 出现在输出里。

实际上：

```powershell
& powershell -File verify.ps1 -Live > $null 2>&1
# exit code: 0
```

**`[exit code: 1]` 是 `Select-Object -Last 15 | Out-String` 那条管道的**，不是脚本的。
脚本一直是 exit 0。

**「读到的退出码」和「被管的进程的退出码」不是一回事。**

---
