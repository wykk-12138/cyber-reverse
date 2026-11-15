# Cybersole 5.18.28 逆向分析报告

> 目标：`C:\Users\wykk\AppData\Local\Cybersole\current\Cybersole.exe`（129,111,632 B，PE64）
> 运行实例：PID 34996（用户已启动，主窗口 "Cybersole"）
> 工具链：IDA Pro 9.3sp2 + idalib（headless）+ Hex-Rays；静态字符串测绘；进程/模块/网络观测
> 分析时间：2026-11-10 11:13–11:35（Asia/Shanghai）

---

## 0. 结论摘要

| 项目 | 结论 |
|---|---|
| 打包 | Velopack（Squirrel 同源）安装器，`current\` 目录为版本化实体 |
| 主程序形态 | **.NET 8/9 NativeAOT 单文件**（无 CLR 头、仅 17 个系统导入、静态链接 Brotli） |
| UI 框架 | **Avalonia UI 12.1.3** + SkiaSharp + HarfBuzz（非 Electron、非 WPF） |
| 内嵌浏览器 | **DotNetBrowser 4.3.5**（Chromium 内核，独立 profile 在 `%APPDATA%\Cybersole\Chromium\4.3.5`） |
| 网络栈 | 自研 `Cybersole.Http`（内部名 **NetClient**）：HTTP/2 + **TLS 指纹伪造**（JA3/ClientHelloSpec/GREASE/ECH/BoringPaddingStyle） |
| 认证 | OAuth 浏览器登录 → JWT（HS256，iss/aud=`https://cybersole.io/`，role=`Bot`）；令牌落在 `settings.json` |
| 许可 | 本地 `license` 键 + 服务端 `https://cybersole.io/api/apisecuretoken` 换取安全令牌 |
| 反机器人 | HumanPresence（`api.humanpresence.io/v2`）、Cloudflare Turnstile、自建 `cf-solver.cybersole.io`、Uncaptcha、Geetest/HCaptcha/reCAPTCHA |
| 反编译 | IDA 全量分析 **320,933 个函数** 完成；Hex-Rays 批量反编译导入链/网络栈/启动链/Brotli 共 51 个函数（107 KB C 伪代码） |

**一句话**：这是一个 `NativeAOT + Avalonia + 自研抗指纹 HTTP 栈` 的抢购机器人客户端；认证与订阅由服务端 JWT 权威，客户端只做缓存与 UI 呈现。

---

## 1. 样本与进程事实

### 1.1 文件布局（Velopack）

```
Cybersole\
├─ Cybersole.exe                 786 KB   Velopack stub（原生 PE）
├─ Update.exe                   5.5 MB    Velopack 更新器
├─ current\
│   ├─ Cybersole.exe           129.1 MB   ★ 真身，NativeAOT 单文件
│   ├─ libSkiaSharp.dll         11.6 MB
│   ├─ libHarfBuzzSharp.dll      1.8 MB
│   ├─ av_libglesv2.dll          5.4 MB
│   └─ sq.version                 910 B   → 5.18.28-win-x64
└─ packages\
    └─ Cybersole-5.18.28-win-x64-full.nupkg  59.7 MB（含 ExecutionStub/Squirrel）
```

### 1.2 PE 结构（`current\Cybersole.exe`）

| 节 | VA | 大小 | 备注 |
|---|---|---|---|
| `.text` | `0x140001000` | 0x313d400 (51.6 MB) | 320,933 函数 |
| `.rdata` | `0x14313f000` | 0x38ece00 (59.7 MB) | 元数据 + 常量 |
| `.data` | `0x146a2c000` | 0x9bde00 (10.2 MB) | 运行时字符串对象 |
| `.pdata` | `0x147525000` | 0x32b200 | 异常表 |
| `.reloc` | `0x14789d000` | 0x3c0000 | 重定位 |

- 导入表仅 17 个 DLL：`ADVAPI32/bcrypt/CRYPT32/IPHLPAPI/KERNEL32/ncrypt/ole32/OLEAUT32/USER32/WS2_32` + 7 个 UCRT API-set。
- 无 `coreclr.dll` 导入、CLR 数据目录为空 → **NativeAOT**。
- 导出表 39 项：36 个 `Brotli*`（静态链接的 Brotli 编解码器）+ `DotNetRuntimeDebugHeader` + 2 个 `_kBrotli*` 数据符号。
- PE 入口 `0x1430F65C8`：
  ```c
  __int64 start() { sub_1430F6F18(); return __scrt_common_main_seh(); }
  ```
  （`sub_1430F6F18` = CRT `__security_init_cookie`）

### 1.3 运行态观测

- 内存工作集 1.14 GB / 私有 885 MB，句柄 1702，148 个模块。
- 非系统模块：`libSkiaSharp.dll`、`libHarfBuzzSharp.dll`、`av_libGLESv2.dll`、`%APPDATA%\Cybersole\Chromium\4.3.5\WindowsX64\{ipc64.dll, toolkit64.dll}`（DotNetBrowser）。
- 网络：
  - `127.0.0.1:16861`、`127.0.0.1:16875` 监听 + 多条本地回环 ESTABLISHED（DotNetBrowser IPC / 本地调试通道）
  - `198.18.0.1:16900 → 198.18.1.32:443`（fake-IP 代理出口，走用户代理软件）

---

## 2. 技术栈清单（从字符串/元数据/符号提取）

| 组件 | 证据 |
|---|---|
| .NET NativeAOT | `NativeAOT`×3、`System.Private.CoreLib`、`DotNetRuntimeDebugHeader`、无 CLR 头 |
| Avalonia 12.1.3 | `12.1.3.0^12.1.3+…AvaloniaUI/Avalonia`、`Avalonia.Themes.Fluent`、大量 `NamespaceInfo:/Views/*.axaml` |
| AvaloniaEdit 12.0.0 | `AvaloniaEdit.Highlighting`、`SyntaxDefinition`（C#/JS/JSON/Python…） |
| DotNetBrowser.Core | `DotNetBrowser.Core`、`%APPDATA%\Cybersole\Chromium\4.3.5` |
| 自研 HTTP | `Cybersole.Http` / `.Newtonsoft` / `.Analytics` / `.Debug`，GitHub 仓 `Cybersole/NetClient`，版本 `0.10.0` |
| 遥测 | `HttpAnalytics`（批量写 ClickHouse：URL/状态/耗时/字节/协议/代理/标签）、`HttpDebug.Enable()` 实时请求流 |
| 序列化 | Newtonsoft.Json 13.x、Google.Protobuf 3.32、gRPC |
| 加密 | BouncyCastle、BCrypt/NCrypt（DPAPI 风格持久化密钥） |
| JS 引擎 | Jint 4.17（站点脚本/表达式） |
| HTML 解析 | AngleSharp 1.8 |
| 消息 | RabbitMQ.Client、SignalR（`Microsoft.NET.Sdk.Web` 依赖）、MSAL（Azure AD） |
| AOP | Metalama 2026.1（编译期织入） |
| 压缩 | Brotli（导出表） |

---

## 3. 网络与反检测栈（核心价值区）

### 3.1 端点清单

| 用途 | 端点 |
|---|---|
| 主 API | `https://api.cybersole.io` |
| 安全令牌 | `https://cybersole.io/api/apisecuretoken` |
| Web | `https://cybersole.io` |
| 遥测 | `https://telemetry.cybersole.io`、`https://analytics.cybersole.io` |
| 更新 CDN | `https://cdn.cybersole.io/releases/` |
| CF 求解 | `https://cf-solver.cybersole.io` |
| 匹配服务 | `https://match.cybersole.io/`、`https://arno-1863--matcher-standby-web.modal.run/` |
| 行为检测 | `https://api.humanpresence.io/v2` |
| 验证码平台 | `https://api.uncaptcha.io/v1`、`https://api.parallaxsystems.io/gen|holdcaptcha` |
| 邮箱 | `https://inbox-api.aycd.io/api/v1/{tasks/mail/create, tasks/completed, user/verify}` |
| 支付 | Adyen / Stripe / Square / Unzer / PayPal / CommerceHub |

### 3.2 TLS 指纹伪造（关键发现）

元数据中出现完整的"客户端指纹编排"符号族，说明 NetClient 不是普通 `HttpClient`：

```
JA3                       ×2
ClientHelloSpec / ClientHelloOptions / ClientHelloBuilder
TlsClientOptions / TlsClientCache
Tls13RecordProtection / Tls12GcmProtection / Tls12ChaChaProtection / Tls12CbcProtection
AlpnExtension / GreaseEchExtension / KeyShareExtension / RenegotiationInfoExtension
BoringPaddingStyle（方法内 lambda: <Prepare>b__105_3）
X25519Key / EcdhKey / HybridMlKemKey
```

→ 自行实现 ClientHello 构造 + GREASE + ECH + ALPN，按目标站点切换 TLS 指纹（Chrome 148 UA/JS 指纹与之配套：`navigator.appVersion … Chrome/148.0.0.0`）。

### 3.3 HTTP/2 自研实现

`http2Stream / headerBytes / endStream / mustFlush / pingContent / isAck` 等字段名直接暴露 HPACK 帧状态机。

### 3.4 验证码与风控

- 站点级：Cloudflare Turnstile、hCaptcha、reCAPTCHA、Geetest v4、BotDetect、Ynap、Popmart。
- 客户端内置 Solver 窗口（`Views/Captcha/SolverWindow`、`GoogleLogin`、`YoutubeWindow`）+ `Cybersole.CloudflareSolvers.CloudflareSolver` 模型（`ApiKey/Balance/Concurrency/Count/IsFetchingBalance`）。
- 站点适配器数量庞大：Shopify（含 myshopify 域名族）、End、John Lewis、Casio、Pop Mart、Superswipe、Pocketgames、Footsites、Nike、Supreme 等。

---

## 4. 认证与许可模型

### 4.1 登录流

UI 类：`Cybersole.Ui.Views.Auth.AuthWindow` / `LoginControl` / `LicenseControl`，命令：`SignIn / SignUp / UseCode / OpenBrowser / Cancel / Logout / Authenticate / Dashboard / Refresh`。

→ 浏览器 OAuth 完成登录，回跳后客户端拿到 JWT。

### 4.2 JWT（运行时证据）

`%APPDATA%\Cybersole\settings.json`：

```json
"bearer":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.<payload>.1L9TVP7jVDp4X6TT_U5aoVYJ1EIrfar8tYwq0fmERIQ"
"license":"6af28adf9813baada60406dd"
```

JWT claims（解码）：`sub=6ae74a6b1d092c6997d4d1c6`、`name=sethe189rn@gmail.com`、`role=Bot`、`SecurityStamp=…`、`iss/aud=https://cybersole.io/`、`exp=1825816245`(2027-08)。

- 算法 **HS256** → 密钥在服务端，**本地无法伪造**（除非密钥泄露）。
- claims 中的 `role=Bot` 是服务端下发的角色。

### 4.3 许可校验链路

符号族：`LicenseKey / LicenseTo / Last4 / VerifyLicense / FindLicense / ReadLicense / LicenseFile / CheckLicense / LicenseVerifier / InvalidLicenseException / NoLicenseException`，模型 `Cybersole.Models.License`。

- 判定：**服务端权威**（`apisecuretoken` 换票据 + JWT 验签）；客户端保留 `license` 明文键作为标识/缓存，属"可读不可改"性质。
- 结论措辞：本目标不具备"纯本地离线破解"面；能做的只有中继/回放与 UI 侧本地化，不影响服务端计费。

### 4.4 数据文件

`%APPDATA%\Cybersole\`：

| 文件 | 内容 |
|---|---|
| `settings.json` | bearer、license、并发/延迟/键盘快捷键/通知/币种/滚动条主题等 |
| `accounts.json` | `accountGroups / payPal / google / imap / aycdInbox` |
| `tasks.json` | 任务组（`captchaSource=7`、`cloudflareSolver`、`webhooks`） |
| `proxies.json` / `analytics.json` | 代理组 + 流量统计 |
| `solvers.json` | Solver 窗口位置 + `autoBoundingBox/autoTickBox/autoCanvas/questionSharing/autoClick/reCaptchaSegmentation` |
| `Backups\*.cyb` | **明文 JSON**（实测无加密，可直接读写） |
| `BrowserData\` | DotNetBrowser 的 Chromium profile（History/Login Data/Web Data 等） |
| `Logs\` | 运行日志（按分钟切分） |

---

## 5. 反编译证据（Hex-Rays 输出）

### 5.1 导入 IAT 链（网络栈定位法）

NativeAOT 无符号，用 `WS2_32` IAT → thunk → 真实包装函数逐层下钻：

| 导入 | IAT VA | thunk | 真实包装 |
|---|---|---|---|
| `WSASocketW` | `0x14313F9D8` | `0x1430F61FD` | `0x141CCF400`（+2 处） |
| `WSASend` | `0x14313F9E0` | `0x1430F61F7` | `0x141CC2E00` |
| `WSARecv` | `0x14313F9E8` | `0x1430F61F1` | `0x141CC2C70` |
| `WSAIoctl` | `0x14313F9F0` | `0x1430F61EB` | `0x141CA35A0 / 0x141CC28D0 / 0x141CC2A90` |
| `WSAConnect` | `0x14313FA08` | `0x1430F61D9` | `0x141CC25D0` |
| `GetAddrInfoExW` | `0x14313FA10` | `0x1430F61C1` | `0x141CA22B0` → `0x141CA0900`（Dns 实现） |
| `GetAddrInfoW` | `0x14313FA20` | `0x1430F61C7` | `0x141C9FD60` |

真实包装示例（`x1_WSASend_141cc2e00.c`）：

```c
__int64 __fastcall sub_141CC2E00(...)
{
  *(_QWORD *)&v18 = a1;
  sub_141DC71A0(a1, (char *)&v18 + 8);      // SafeHandle → HANDLE
  s = *(_QWORD *)(v18 + 8);
  SetLastError(0);
  v11 = WSASend(s, lpBuffers, dwBufferCount, lpNumberOfBytesSent, dwFlags, lpOverlapped, lpCompletionRoutine);
  sub_14301AEB0(v16);                        // 结束线程状态/异常边界
  LastError = GetLastError();
  *(_DWORD *)(v14 + 424) = LastError;        // ThreadStatic last-error
  return v11;
}
```

→ 确认 socket 层是 .NET `System.Net.Sockets` 的 async/overlapped 实现，业务侧（NetClient）在其上自建 TLS/HTTP2。

### 5.2 启动链

```
0x1430F65C8  start()
 ├─ 0x1430F6F18  __security_init_cookie
 └─ __scrt_common_main_seh  → nativeAOT RhpInitialize → StartupCodeHelpers.InitializeModules → 托管 Main
```

### 5.3 Brotli 静态链接证据

`entry_4_1430e3140.c`（33 KB）为 `BrotliDecoderDecompressStream` 的完整反编译，证明压缩由原生库承担（`Cybersole.Http` 的 `System.IO.Compression.Brotli` 直连）。

### 5.4 字符串锚点（IDA 可复核地址）

| 字符串 | 元数据地址 | 说明 |
|---|---|---|
| `https://api.cybersole.io` | `0x1433B46F1` | 另见运行时 String 对象 `0x147036B8C`（len=0x18，UTF-16） |
| `https://cybersole.io/api/apisecuretoken` | `0x143359A69` | 许可票据端点 |
| `https://api.humanpresence.io/v2` | `0x14330EDD9` | 行为检测 |
| `https://cf-solver.cybersole.io` | `0x14344694F` | CF 求解 |
| `LicenseVerifier` | `0x1431F8277` | 许可校验类名 |
| `TlsClientOptions` | `0x1433BF51C` | TLS 指纹配置 |
| `ClientHelloBuilder` | `0x1433BF13F` | ClientHello 构造器 |

> 注意：这些是 NativeAOT **元数据字符串**（UTF-8 长度前缀表），不被代码 `lea` 直接引用（已用全 `.text` 的 `lea r64,[rip+disp32]` 扫描 + 8/4 字节指针扫描验证 = 0 命中）。运行时由反射层构造 String，故静态 xref 不可达——这是 NativeAOT 反编译的主要障碍，也是下一步解析 `DotNetRuntimeDebugHeader` 的动机。

---

## 6. 产物清单

| 文件 | 说明 |
|---|---|
| `current\Cybersole.exe.i64` | IDA 数据库 1.44 GB（可直接 GUI 打开继续） |
| `analysis\decompiled_all.c` | 51 个函数反编译合集（107 KB） |
| `analysis\strings_dump.json` | 去重字符串 + 类名统计（392 KB） |
| `analysis\strings_full.txt` | 可读字符串报告（167 KB） |
| `analysis\ida_*.log` | 每轮分析/反编译日志 |
| `analysis\ida_*.py` | 可复现的反编译脚本（idalib + Hex-Rays） |

---

## 7. 结论与下一步

### 7.1 已确认

1. 不是 Electron/WPF，是 **NativeAOT + Avalonia**；单文件 129 MB，320,933 函数，反编译链路可用。
2. 网络层自研且刻意做 **TLS/HTTP2 指纹伪装**（JA3/ECH/GREASE/ALPN + Chrome 148 指纹），这是该产品对抗风控的核心资产。
3. 认证与许可是 **服务端 JWT 权威**（HS256），客户端 `settings.json` 仅缓存 bearer/license。
4. 反检测生态完整：HumanPresence 行为评分 + 自建 CF solver + 多验证码平台 + 代理组管理。

### 7.2 未完成（需下一轮）

| 方向 | 办法 |
|---|---|
| 恢复 NativeAOT 符号 | 解析 `DotNetRuntimeDebugHeader` → 类型/方法名 ↔ 代码地址（IDA 脚本或 NativeAOTDumper） |
| NetClient/TLS 实现细节 | 有了符号后反编译 `TlsClientOptions/ClientHelloBuilder` 对应方法，可对比 JA3 指纹表 |
| 协议层 | 结合现有代理（198.18.1.32:443）+ 自建 MITM（Frida/tls 抓包）验证 `apisecuretoken` 请求签名 |
| 行为验证 | 对 `settings.json` 的 bearer 做离线复用测试，确认服务端会话绑定策略 |

### 7.3 关于 seep-reverse-lab

本机会话未挂载 `seep_*` MCP（`~/.dsh` 下无该 MCP 注册，工具列表中也没有 `seep_*` 工具），因此本次用 **IDA Pro 9.3 idalib + Hex-Rays 直连** 完成等价链路：无头分析 → 数据库落盘 → 字符串锚点 → IAT 链下钻 → C 伪代码落盘。`seep` 若需接入，注册 MCP server 后可直接复用本报告的 `.i64` 与脚本。
