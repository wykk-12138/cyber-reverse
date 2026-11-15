# Cybersole — 功能复刻

> 目标：复现 Cybersole 5.18.32 客户端的**功能**，不追求字节级一致。
> 依据：对 `Cybersole.exe`（.NET NativeAOT，320,933 函数）的静态逆向 + 运行时观测。
>
> 逐轮开发记录在 [docs/HISTORY.md](docs/HISTORY.md)。完整结论在 [docs/VERDICT.md](docs/VERDICT.md)。
> **接手从这里开始**：[docs/SESSION_STATE.md](docs/SESSION_STATE.md) —— 现在在哪、怎么验证、还剩什么、别踩哪些坑。
> 从二进制挖出来的原版事实：[docs/ORIGINAL_ENDPOINTS.md](docs/ORIGINAL_ENDPOINTS.md)、[docs/NIKE_PARITY.md](docs/NIKE_PARITY.md)、[docs/ORIGINAL_VIEWS.md](docs/ORIGINAL_VIEWS.md)（87 个原版 XAML 视图）。

---

## 这个复刻做到什么程度

用户给的三条标准，逐条对照：

| 标准 | 现在 | 达成 |
|---|---|---|
| 函数数量对等 | 业务词汇 **168/168**，实现体 **872/872** | ✅ |
| 每个函数功能相等 | **61 个模块** · 平台 **15/15** · 9 个平台误判已修正 | ✅ |
| 效率相近 | 真实网络 p50 **1.01x**、p95 **1.18x**（n=50） | ✅ |

**这三条已经达成。** 剩余项都是「在真实站点上跑通」而不是「复刻得对不对」：

| 剩余 | 原因 |
|---|---|
| `bstn` / `goat` / `scheels` 的加购端点 | JS 路由或反爬，需要交互式抓包 |
| 远程 Store 名单 | 服务器下发，API 路径运行时拼接 |
| `fanatics` / `warhammer` 被拦 | Akamai / 403 |

---

## 哪些站现在能用

61 个模块逐个探测过一次（`docs/VERDICT.md` 第八节有完整表）：

| 状态 | 数量 | 含义 |
|---|---|---|
| **Live** | 44 | 站点正常应答 |
| **Guarded** | 6 | 主机在，拒绝自动化（`goat` `offspring` `pocketgames` `scheels` `yeezysupply` `fanatics`） |
| **Missing** | 2 | `shopify` / `trophyroom`（通用域名、站点已 404） |
| **Dead** | 9 | 域名解析不了（`bodega` `hypecommerce` `livestock` `nakedcph` `offthehook` `premiumgoods` `shophmvs` + 两个占位） |

**50 / 61 有地方可跑。** 具体每个模块用哪个平台、哪个端点，见
[docs/PLATFORM_VERIFICATION.md](docs/PLATFORM_VERIFICATION.md)。

---

## 怎么跑

```powershell
cd replica

# 构建
D:\tools\dotnet8\dotnet.exe build Cybersole.sln -c Release

# 启动 GUI
D:\tools\dotnet8\dotnet.exe run --project src\Cybersole.Ui\Cybersole.Ui.csproj

# 离线测试（539 个，约 7 秒）
D:\tools\dotnet8\dotnet.exe test tests\Cybersole.Tests\Cybersole.Tests.csproj --filter "Speed!=Slow"
```

## 怎么验证

```powershell
# 常规：构建 + 离线测试 + 模块数 + 文档锚点（约 10 秒）
pwsh -File tools\verify.ps1

# 加上 9 个 live 契约（打真实站点，约 25 秒）
pwsh -File tools\verify.ps1 -Live

# 全部 250 个 Speed=Slow 测试（约 3 分钟）
pwsh -File tools\verify.ps1 -Full
```

### 为什么需要 `-Full`

**543 个测试里有 250 个带 `Trait("Speed","Slow")`，默认的 `Speed!=Slow` 筛选从来没跑过它们。**

R93 手工跑了一次，发现两个**从写下来那天就一直在失败**的测试：

- `nike-gs` 漏在风控门白名单外（它继承 `NikeFlow`，行为对但断言错）
- Shopify 主机清单落后四次注册改动（`footpatrol`/`size`/`jbhifi`/`supreme` 该加，`bstn`/`converse` 该删）

**这两个只有跑 `-Full` 才能看见。** 改了 `Registry.cs` 或任何平台判断之后，请跑一次。

### `-Full` 覆盖什么

| 测试 | 做什么 | 耗时 |
|---|---|---|
| `LiveContractTests` | 9 组平台断言（`/cart.js` 是不是 Shopify、Hybris controller 在不在） | 15 s |
| `ShopifyWrappingTests` | 31 个 Shopify 站点逐个探测 `/cart.js` | 90 s |
| `ModuleRobustnessTests` | 61 个模块 × 2 个失败场景 | 60 s |
| `ModuleReachabilityTests` | 61 个域名逐个探测可达性 | 180 s |
| 性能测试 | TLS 双栈 p50/p95 | 60 s |

### 关于 `own TLS` 那行 WARN

```
own TLS 1.2 + HTTP/2   WARN   probe ran (exit 0) but its output was not capturable here
```

这是 Windows PowerShell 5.1 在此脚本上下文里捕获不到 native exe 输出的问题。
**手动跑一直是 200**：

```powershell
tools\TlsProbe.Cli\bin\Release\net8.0\TlsProbe.Cli.exe --own example.com
# HTTP 200  577 bytes  proto=h2  transport=own-tls12  alpn=h2
```

WARN 不参与判定，`VERDICT: all checks passed` 仍然成立。

## 抓包工具

判断一个陌生店铺用什么平台时用它：

```powershell
dotnet run --project tools\NetworkCapture -- <url> [秒数] [--scroll] [--find-add] [--follow=N] [--eval-file=路径]
```

| 参数 | 用途 |
|---|---|
| `--scroll` | 懒加载网格要先滚动才渲染（**没有它经常什么都看不到**） |
| `--find-add` | 列出页面上像加购的控件，拿到选择器 |
| `--follow=N` | 自动下钻 N 层列表页 |
| `--eval-file` | 执行脚本文件（JS 含分号和引号时，命令行传不进去） |
| `--steps="click:x;; wait:800;; click:y"` | 串联动作，`;;` 分隔 |

---

## 目录

```
src/Cybersole.Core        模型、设置、存储、事件
src/Cybersole.Http        NetClient（四种传输：SChannel / BouncyH2 / BouncyHttp11 / OwnTls）
src/Cybersole.Services    认证、许可、时钟、代理、验证码、任务引擎、通知
src/Cybersole.Stores      61 个站点模块 + 15 个平台 flow
src/Cybersole.Ui          Avalonia 界面
tests/Cybersole.Tests     539 个测试
tools/                    verify.ps1 / NetworkCapture / TlsProbe.Cli
docs/                     VERDICT / PLATFORM_VERIFICATION / HISTORY / PARITY / WIRING
```

## 文档在哪

| 想看 | 去 |
|---|---|
| 这个复刻完成到什么程度 | [docs/VERDICT.md](docs/VERDICT.md) |
| 每个店铺确认是什么平台、证据是什么 | [docs/PLATFORM_VERIFICATION.md](docs/PLATFORM_VERIFICATION.md) |
| 逐轮做了什么 | [docs/HISTORY.md](docs/HISTORY.md) |
| 与原版逐项对照 | [docs/PARITY.md](docs/PARITY.md) |
| GUI 有哪些页面、每个字段是什么 | [docs/GUI_BASELINE.md](docs/GUI_BASELINE.md) |

## 不复刻的部分

| 项 | 原因 |
|---|---|
| 厂商授权校验 | 需要真实许可服务器 |
| 遥测上报 | 无服务端 |
| Velopack 自更新 | 无发布渠道 |
| 内嵌 Chromium（DotNetBrowser） | 用 `tools/NetworkCapture` 的 CDP 通道替代，覆盖抓包诊断场景 |
