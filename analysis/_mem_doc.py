import io
p = r'D:\projects\cyber-reverse\replica\docs\MEMORY_DISCIPLINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## 崩溃前兆的两个数（R210 实测，记下来当仪表盘）

每次跑完测试套件都会拉起真实 Chromium。进程退出了，但**页/提交不会立刻归还**。判断要不要重启，看两个数就够了：

| 指标 | 健康 | 危险 | 怎么看 |
|---|---|---|---|
| `Repurposed` 页 | 0 GB | ≥ 2.5 GB | `analysis/memlists.ps1` |
| Commit | ≈ 14 GB | ≥ 30 GB | `analysis/perfinfo.ps1` |

判断依据是"**提交远大于进程之和**"：R210 收尾时

```
Commit 31.71 GB（峰值 36.13）   进程最大者仅 619 MB，进程之和约 3 GB
Repurposed 2.91 GB              Standby 7.45 GB   Zero 3.8 GB
KernelTotal 3.03 GB = nonpaged 1.04 + paged 1.99
```

上一轮崩机前是 `Commit 42 GB / Repurposed 3.4 GB` —— **同一条曲线的两个不同位置**。
`Repurposed` 一旦上 2.5 GB，就该重启，而不是继续堆测试。

### 一回合最多跑一次套件

`mutation-check` 内部会跑 24 次套件，是最大的内存消耗者。规矩：

1. 一轮里**只跑一次** `mutation-check`，跑之前先清 `chrome` 与 `dotnet` 残留；
2. 跑完立刻 `Get-Process chrome | Stop-Process -Force` + `dotnet build-server shutdown`；
3. 看见 `Repurposed ≥ 2.5 GB` 就收工报告，**不要在同一轮里再开第二次重活**。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('memory discipline notes appended')
