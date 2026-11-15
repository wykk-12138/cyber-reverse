### `verify.ps1 -Full`：把 250 个从没跑过的测试接进流程

R93 发现的问题不是「两个测试坏了」，是**一个系统性盲区**：

> `verify.ps1` 只跑 `Speed!=Slow`。带 `Speed=Slow` 的测试有 **250 个**，从来没进过门禁。

### 加了第三个开关

```
pwsh -File tools\verify.ps1           # 约 10 秒
pwsh -File tools\verify.ps1 -Live      # 约 25 秒，加 9 个 live 契约
pwsh -File tools\verify.ps1 -Full      # 约 3 分钟，加全部 250 个
```

`-Full` 包含 `-Live`，另外跑：

| 测试 | 做什么 | 耗时 |
|---|---|---|
| `ShopifyWrappingTests` | 31 个 Shopify 站点逐个探 `/cart.js` | 90 s |
| `ModuleRobustnessTests` | 61 个模块 × 2 个失败场景 | 60 s |
| `ModuleReachabilityTests` | 61 个域名逐个探可达性 | 180 s |
| 性能测试 | TLS 双栈 p50/p95 | 60 s |

### 第一次跑的结果

```
release build                     PASS
unit tests                        PASS   exit 0
slow tests (Speed=Slow)           PASS   all live/network tests green
store modules                     PASS   61 registered
own TLS 1.2 + HTTP/2              WARN   (PowerShell 5.1 捕获问题)
VERDICT: all checks passed
```

**250 个全绿**——因为 R93 已经把那两个修了。

### 失败时会点名

```powershell
$failed = ([regex]::Matches($slow, '失败\s+(\w+)') | ForEach-Object { $_.Groups[1].Value }) -join ', '
$slowDetail = if ($slowOk) { 'all live/network tests green' }
              else { 'failed: ' + $failed.Trim(', ', ' ') }
```

红的时候读作 `failed: ShopifyWrappingTests, ModuleRobustnessTests`，不用翻日志。

### README 也更新了

新增一节「为什么需要 `-Full`」，把那两个一直红着的测试作为理由写进去：

> **这两个只有跑 `-Full` 才能看见。改了 `Registry.cs` 或任何平台判断之后，请跑一次。**

### 一个仍然存在的差距

**`-Full` 不会自动跑。** 它需要人记得。

真正的解法是在 CI 里定期跑，但这个仓库没有 CI。**所以现在的状态是「有这个能力，但依赖纪律」。**

**这比「没有这个能力」好，但不是最好。** 已经在 README 和脚本注释里都写明了什么时候该跑。

---
