# 内存纪律（R205 事故后）

2026-11-13 13:0x，本机内存被打满，DSH 与 IDA Pro 同时崩溃。原因是我把三件吃内存的事并行堆在了一起：

1. `Cybersole.exe` 常驻（~600 MB，GUI 交叉验证用）
2. IDA Pro 载着 `Cybersole.exe.i64`（**1.4 GB 的数据库，常驻 4–8 GB**）
3. `mutation-check.py` —— 它内部会**连续启动 20+ 次 `dotnet test`**，每次都要装 Avalonia + 起 Chromium

加上我同时挂了两个后台 job（旧的没杀干净又起新的），机器就被压死了。

## 以后固定这么干

| 场景 | 规则 |
|---|---|
| 跑 `mutation-check` | **独占**跑。跑之前 `dotnet build-server shutdown`，跑之后确认无 `testhost` 残留；**绝不**与 IDA 反编译或 GUI 会话并行 |
| 用 Cybersole GUI | 只在需要看界面时启动，看完 `Stop-Process` 关掉；不要让它常驻陪我写代码 |
| 用 IDA MCP | 需要时开，长时间不做反编译就关掉 IDA（1.4 GB 数据库不是背景进程） |
| 后台 job | 起之前先 `job_list`；同一个工具不重复起；拿到结果就 `job_kill`/清理，不叠 |
| 全量测试 | 一次只跑一份；不再"连跑三次"验证稳定性，改成"跑一次 + 失败再跑一次" |
| 观察内存 | 大动作前后各看一次 `FreePhysicalMemory`；低于 8 GB 就先清场再继续 |

## 事故后的自检清单（本次已执行）

```
1. 残留进程：Cybersole / python / dotnet / testhost  → 全无          ✓
2. 变异残留：14 个 tools/.mutation-backup 备份 vs 线上文件逐行 diff → 全 0  ✓
3. 树是否可用：单跑全量 → 1378 通过 / 0 失败                          ✓
4. 内存：31.7 GB 总，17.6 GB 空闲                                    ✓
```

> 第 2 条是这次事故里最要紧的一条：`mutation-check` 是**改源码再还原**的工具，
> 它在半途被杀，唯一要担心的是「某个变异没还原」。逐行 diff 是唯一能证明没问题的办法，
> 不能靠"看起来绿"来推断 —— 留在树里的变异恰好可能让测试仍然是绿的。


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
